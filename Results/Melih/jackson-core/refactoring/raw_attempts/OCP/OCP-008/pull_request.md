# Refactor OCP-008 (OCP): Switch statement on character input requires modification to handle new value...

**Status:** `patch_failed`  
**Branch:** `refactor/OCP-008` -> `main`  
**Head commit:** `830edb6aac4f165c94a5fdc01dc77dc6a23643ba`  
**LLM finish:** `FinishReason.STOP` (prompt 3646, completion 553)  

## Detected issue

- **File**: `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java`
- **Entity**: `UTF8StreamJsonParser.nextNameMatch` (class)
- **Lines (at detection time)**: L932–L1003
- **Severity**: high
- **Confidence**: detected by 3 scan(s)

**Description.** Switch statement on character input requires modification to handle new value types

**Reasoning.** The nextNameMatch method uses a switch statement to dispatch parsing based on the first character of a value. Adding new value types would require modifying this switch block, violating the Open/Closed Principle.

## Fix logic

- **Model**: `gemini-2.5-flash` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java`

**Summary.** Centralize value parsing logic in `nextNameMatch` by delegating to `_parseValueToken`.

**Rationale.** The `nextNameMatch` method contained a `switch` statement for parsing different value types based on the initial character. This duplicated logic already present in `_parseValueToken` and violated the Open/Closed Principle, as adding new value types would require modifying this `switch` block. By delegating to the existing `_parseValueToken` method, we centralize the value parsing logic, making `nextNameMatch` closed for modification while `_parseValueToken` remains open for extension (or is itself refactored to be so). This change maintains existing behavior and public API.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java` (42-line block → 3-line replacement)

**Replaces:**

```java
        JsonToken t;
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
        }
        _nextToken = t;
        return match;
```

**With:**

```java
        JsonToken t = _parseValueToken(i);
        _nextToken = t;
        return match;
```

## Apply error

```
search_text not found in src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java (block 0)
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java` | 3534 → - | 112 → - | 9.81 → - | 988 → - | 0 → - |

## Diff

*(no diff — patch was not applied)*
