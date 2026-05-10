# Refactor OCP-005 (OCP): Switch statement on character input requires modification to handle new value...

**Status:** `patch_failed`  
**Branch:** `refactor/OCP-005` -> `main`  
**Head commit:** `68ce7e9ad175b8602bc625a892c37584b60ad05f`  
**LLM finish:** `FinishReason.STOP` (prompt 3609, completion 1394)  

## Detected issue

- **File**: `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java`
- **Entity**: `UTF8StreamJsonParser.nextToken` (class)
- **Lines (at detection time)**: L625–L687
- **Severity**: high
- **Confidence**: detected by 5 scan(s)

**Description.** Switch statement on character input requires modification to handle new value types

**Reasoning.** The nextToken method uses a switch statement to dispatch parsing based on the first character of a value. Adding new value types or syntax would require modifying this switch block, violating the Open/Closed Principle.

## Fix logic

- **Model**: `gemini-2.5-flash` (temperature 0.2)
- **Patch blocks**: 4
- **Files modified** (1): `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java`

**Summary.** Replaced switch statement in nextToken with a strategy map for OCP compliance.

**Rationale.** The original `nextToken` method used a switch statement to dispatch parsing logic based on the first character of a value. This violates the Open/Closed Principle because adding new value types or syntax would require modifying this existing switch block. The refactoring introduces a `ValueTokenHandler` functional interface and a `_valueTokenHandlers` map. Each entry in the map associates a starting character with a lambda expression (handler) that encapsulates the parsing logic for that value type. Digit handling is optimized with a direct check before map lookup. This design allows for extending the parser's capabilities (e.g., adding new literal types) by simply adding new entries to the map during initialization, without modifying the core `nextToken` method, thus adhering to OCP.

## Changes overview

_4 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java` (1-line block → 3-line replacement)

**Replaces:**

```java
import java.util.Arrays;
```

**With:**

```java
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;
```

### 2. EDIT `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java` (7-line block → 13-line replacement)

**Replaces:**

```java
    /**
     * Flag that indicates that the current token is a String or Number
     * that has not yet been fully parsed.
     *
     * @since 2.10
     */
    protected boolean _tokenIncomplete;
```

**With:**

```java
    /**
     * Flag that indicates that the current token is a String or Number
     * that has not yet been fully parsed.
     *
     * @since 2.10
     */
    protected boolean _tokenIncomplete;

    private final Map<Integer, ValueTokenHandler> _valueTokenHandlers;

    private interface ValueTokenHandler {
        JsonToken handle(int firstChar) throws JacksonException;
    }
```

### 3. EDIT `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java` (4-line block → 20-line replacement)

**Replaces:**

```java
    _base64Decoder = UTF8Base64Decoder.instance;
    // 07-Nov-2023, tatu: New for [core#1074]
    _tokenIncomplete = false;
}
```

**With:**

```java
    _base64Decoder = UTF8Base64Decoder.instance;
    // 07-Nov-2023, tatu: New for [core#1074]
    _tokenIncomplete = false;

    _valueTokenHandlers = new HashMap<>();
    _valueTokenHandlers.put((int) '-', (firstChar) -> _parseSignedNumber(true));
    _valueTokenHandlers.put((int) '+', (firstChar) -> {
        if (isEnabled(JsonReadFeature.ALLOW_LEADING_PLUS_SIGN_FOR_NUMBERS)) {
            return _parseSignedNumber(false);
        } else {
            return _handleUnexpectedValue(firstChar);
        }
    });
    _valueTokenHandlers.put((int) '.', (firstChar) -> _parseFloatThatStartsWithPeriod(false, false));
    _valueTokenHandlers.put((int) 'f', (firstChar) -> { _matchFalse(); return JsonToken.VALUE_FALSE; });
    _valueTokenHandlers.put((int) 'n', (firstChar) -> { _matchNull(); return JsonToken.VALUE_NULL; });
    _valueTokenHandlers.put((int) 't', (firstChar) -> { _matchTrue(); return JsonToken.VALUE_TRUE; });
    _valueTokenHandlers.put((int) '[', (firstChar) -> JsonToken.START_ARRAY);
    _valueTokenHandlers.put((int) '{', (firstChar) -> JsonToken.START_OBJECT);
}
```

### 4. EDIT `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java` (50-line block → 13-line replacement)

**Replaces:**

```java
        switch (i) {
        case '-':
            t = _parseSignedNumber(true);
            break;
        case '+':
            if (isEnabled(JsonReadFeature.ALLOW_LEADING_PLUS_SIGN_FOR_NUMBERS)) {
                t = _parseSignedNumber(false);
            } else {
                t = _handleUnexpectedValue(i);
            }
            break;
        case '.': // [core#611]:
            t = _parseFloatThatStartsWithPeriod(false, false);
            break;
        case '0':
        case '1':
        case '2':
        case '3':
        case '4':
        case '5':
        case '6':
        case '7':
        case '8':
        case '9':
            t = _parseUnsignedNumber(i);
            break;
        case 'f':
            _matchFalse();
             t = JsonToken.VALUE_FALSE;
            break;
        case 'n':
            _matchNull();
            t = JsonToken.VALUE_NULL;
            break;
        case 't':
            _matchTrue();
            t = JsonToken.VALUE_TRUE;
            break;
        case '[':
            t = JsonToken.START_ARRAY;
            break;
        case '{':
            t = JsonToken.START_OBJECT;
            break;

        default:
            t = _handleUnexpectedValue(i);
        }
        _nextToken = t;
        return _currToken;
```

**With:**

```java
        // Handle digits separately for efficiency and to avoid map population for 0-9
        if (i >= '0' && i <= '9') {
            t = _parseUnsignedNumber(i);
        } else {
            ValueTokenHandler handler = _valueTokenHandlers.get(i);
            if (handler != null) {
                t = handler.handle(i);
            } else {
                t = _handleUnexpectedValue(i);
            }
        }
        _nextToken = t;
        return _currToken;
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
