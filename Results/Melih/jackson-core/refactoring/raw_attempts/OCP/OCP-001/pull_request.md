# Refactor OCP-001 (OCP): Switch statement on token ID requires modification to handle new token types

**Status:** `patch_failed`  
**Branch:** `refactor/OCP-001` -> `main`  
**Head commit:** `68ce7e9ad175b8602bc625a892c37584b60ad05f`  
**LLM finish:** `FinishReason.STOP` (prompt 3489, completion 523)  

## Detected issue

- **File**: `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java`
- **Entity**: `UTF8StreamJsonParser._getText2` (class)
- **Lines (at detection time)**: L339–L354
- **Severity**: medium
- **Confidence**: detected by 6 scan(s)

**Description.** Switch statement on token ID requires modification to handle new token types

**Reasoning.** The _getText2 method uses a switch statement based on token IDs. Adding new token types would require modifying this switch block, violating the Open/Closed Principle.

## Fix logic

- **Model**: `gemini-2.5-flash` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java`

**Summary.** Replaced switch statement on JsonToken ID with if/else if structure to improve OCP adherence.

**Rationale.** The original `_getText2` method used a switch statement on `JsonToken.id()`, which would require modification if new token types were introduced, violating the Open/Closed Principle. The refactored code replaces this with an `if/else if` structure that leverages `JsonToken` enum instances directly and its `isNumeric()` method. This makes the method more robust to future additions of token types, as new numeric tokens will be handled by `isNumeric()` and other non-data tokens will fall through to `t.asCharArray()`, without requiring changes to this method.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java` (21-line block → 16-line replacement)

**Replaces:**

```java
    protected final String _getText2(JsonToken t) throws JacksonException
    {
        if (t == null) {
            return null;
        }
        switch (t.id()) {
        case ID_PROPERTY_NAME:
            return _streamReadContext.currentName();

        case ID_STRING:
            // fall through
        case ID_NUMBER_INT:
        case ID_NUMBER_FLOAT:
            // For these, text buffer has the value
            return _textBuffer.contentsAsString();

        default:
            // For others, we have char[] form
            return t.asCharArray();
        }
    }
```

**With:**

```java
    protected final String _getText2(JsonToken t) throws JacksonException
    {
        if (t == null) {
            return null;
        }
        if (t == JsonToken.PROPERTY_NAME) {
            return _streamReadContext.currentName();
        }
        // For VALUE_NUMBER_INT, VALUE_NUMBER_FLOAT, text buffer has the value
        if (t.isNumeric()) {
            return _textBuffer.contentsAsString();
        }
        // For others (START_OBJECT, END_OBJECT, VALUE_TRUE, VALUE_FALSE, VALUE_NULL, etc.),
        // we have char[] form
        return t.asCharArray();
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
