# Refactor OCP-002 (OCP): Switch statement on token ID requires modification to handle new token types

**Status:** `patch_failed`  
**Branch:** `refactor/OCP-002` -> `main`  
**Head commit:** `68ce7e9ad175b8602bc625a892c37584b60ad05f`  
**LLM finish:** `FinishReason.STOP` (prompt 3560, completion 873)  

## Detected issue

- **File**: `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java`
- **Entity**: `UTF8StreamJsonParser.getStringCharacters` (class)
- **Lines (at detection time)**: L357–L376
- **Severity**: medium
- **Confidence**: detected by 5 scan(s)

**Description.** Switch statement on token ID requires modification to handle new token types

**Reasoning.** The getStringCharacters method uses a switch statement based on token IDs. Adding new token types would require modifying this switch block, violating the Open/Closed Principle.

## Fix logic

- **Model**: `gemini-2.5-flash` (temperature 0.2)
- **Patch blocks**: 3
- **Files modified** (1): `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java`

**Summary.** Replaced switch statement in getStringCharacters with a static lookup map to adhere to OCP.

**Rationale.** The original `getStringCharacters` method used a switch statement on `JsonToken.id()`, which violates the Open/Closed Principle because adding new token types would require modifying this method. By introducing a static `Map` of `Function`s, the method itself becomes closed for modification. New token-specific character retrieval logic can be added by extending the `CHARACTER_PROVIDERS` map in its static initializer block, thus adhering to OCP. This approach keeps the logic localized within the parser where it has access to necessary internal state (`_tokenIncomplete`, `_finishString`, `_textBuffer`, `currentNameInBuffer`).

## Changes overview

_3 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java` (1-line block → 5-line replacement)

**Replaces:**

```java
import tools.jackson.core.util.TextBuffer;
```

**With:**

```java
import tools.jackson.core.util.TextBuffer;

import java.util.HashMap;
import java.util.Map;
import java.util.function.Function;
```

### 2. EDIT `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java` (7-line block → 23-line replacement)

**Replaces:**

```java
public class UTF8StreamJsonParser extends JsonParserBase
{
    /*
    /**********************************************************
    /* Configuration
    /**********************************************************
     */
```

**With:**

```java
public class UTF8StreamJsonParser extends JsonParserBase
{
    private static final Map<Integer, Function<UTF8StreamJsonParser, char[]>> CHARACTER_PROVIDERS;

    static {
        CHARACTER_PROVIDERS = new HashMap<>();
        CHARACTER_PROVIDERS.put(JsonToken.ID_PROPERTY_NAME, parser -> parser.currentNameInBuffer());
        CHARACTER_PROVIDERS.put(JsonToken.ID_STRING, parser -> {
            if (parser._tokenIncomplete) {
                parser._tokenIncomplete = false;
                parser._finishString();
            }
            return parser._textBuffer.getTextBuffer();
        });
        CHARACTER_PROVIDERS.put(JsonToken.ID_NUMBER_INT, parser -> parser._textBuffer.getTextBuffer());
        CHARACTER_PROVIDERS.put(JsonToken.ID_NUMBER_FLOAT, parser -> parser._textBuffer.getTextBuffer());
    }

    /*
    /**********************************************************
    /* Configuration
    /**********************************************************
     */
```

### 3. EDIT `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java` (24-line block → 12-line replacement)

**Replaces:**

```java
    @Override
    public char[] getStringCharacters() throws JacksonException
    {
        if (_currToken != null) { // null only before/after document
            switch (_currToken.id()) {

            case ID_PROPERTY_NAME:
                return currentNameInBuffer();
            case ID_STRING:
                if (_tokenIncomplete) {
                    _tokenIncomplete = false;
                    _finishString(); // only strings can be incomplete
                }
                // fall through
            case ID_NUMBER_INT:
            case ID_NUMBER_FLOAT:
                return _textBuffer.getTextBuffer();

            default:
                return _currToken.asCharArray();
            }
        }
        return null;
    }
```

**With:**

```java
    @Override
    public char[] getStringCharacters() throws JacksonException
    {
        if (_currToken == null) { // null only before/after document
            return null;
        }
        Function<UTF8StreamJsonParser, char[]> provider = CHARACTER_PROVIDERS.get(_currToken.id());
        if (provider != null) {
            return provider.apply(this);
        }
        return _currToken.asCharArray();
    }
```

## Apply error

```
search_text not found in src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java (block 0)
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java` | 3541 → - | 111 → - | 9.88 → - | 987 → - | 0 → - |

## Diff

*(no diff — patch was not applied)*
