# Refactor OCP-033 (OCP): Switch statement on character code for token parsing requires modification fo...

**Status:** `patch_failed`  
**Branch:** `refactor/OCP-033` -> `main`  
**Head commit:** `68ce7e9ad175b8602bc625a892c37584b60ad05f`  
**LLM finish:** `FinishReason.STOP` (prompt 3609, completion 1042)  

## Detected issue

- **File**: `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java`
- **Entity**: `UTF8StreamJsonParser.nextToken` (method)
- **Lines (at detection time)**: L479–L546
- **Severity**: high
- **Confidence**: detected by 4 scan(s)

**Description.** Switch statement on character code for token parsing requires modification for new tokens.

**Reasoning.** The switch-case logic based on the character `i` to identify the next token is a hard-coded parser logic that must be modified to support any new JSON token or value type.

## Fix logic

- **Model**: `gemini-2.5-flash` (temperature 0.2)
- **Patch blocks**: 2
- **Files modified** (1): `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java`

**Summary.** Extract token parsing switch statement into a protected method to allow extension.

**Rationale.** The original `nextToken` method contained a `switch` statement that directly handled various character codes to determine the next JSON token. This violated the Open/Closed Principle because adding support for new token types would require modifying this `switch` statement. By extracting this logic into a new `protected` method, `_parseValueToken`, the `nextToken` method is now closed for modification. Subclasses can override `_parseValueToken` to introduce or alter token parsing behavior without changing the core `nextToken` logic, thus adhering to OCP. All existing behavior is preserved as the extracted logic is identical.

## Changes overview

_2 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java` (50-line block → 1-line replacement)

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
            case '[':
                t = JsonToken.START_ARRAY;
                break;
            case '{':
                t = JsonToken.START_OBJECT;
                break;

            default:
                t = _handleUnexpectedValue(i);
            }
```

**With:**

```java
            JsonToken t = _parseValueToken(i);
```

### 2. EDIT `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java` (3-line block → 54-line replacement)

**Replaces:**

```java
        _nextToken = t;
        return _currToken;
    }
```

**With:**

```java
        _nextToken = t;
        return _currToken;
    }

    /**
     * Helper method called by {@link #nextToken()} to parse a value token
     * based on the first character encountered.
     * This method is protected to allow subclasses to override and extend
     * token parsing behavior.
     *
     * @param i The first character of the token.
     * @return The {@link JsonToken} representing the parsed value.
     * @throws JacksonException If an unexpected character is encountered or parsing fails.
     */
    protected JsonToken _parseValueToken(int i) throws JacksonException
    {
        switch (i) {
        case '-':
            return _parseSignedNumber(true);
        case '+':
            if (isEnabled(JsonReadFeature.ALLOW_LEADING_PLUS_SIGN_FOR_NUMBERS)) {
                return _parseSignedNumber(false);
            }
            return _handleUnexpectedValue(i);
        case '.': // [core#611]:
            return _parseFloatThatStartsWithPeriod(false, false);
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
            return _parseUnsignedNumber(i);
        case 'f':
            _matchFalse();
            return JsonToken.VALUE_FALSE;
        case 'n':
            _matchNull();
            return JsonToken.VALUE_NULL;
        case 't':
            _matchTrue();
            return JsonToken.VALUE_TRUE;
        case '[':
            return JsonToken.START_ARRAY;
        case '{':
            return JsonToken.START_OBJECT;
        default:
            return _handleUnexpectedValue(i);
        }
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
