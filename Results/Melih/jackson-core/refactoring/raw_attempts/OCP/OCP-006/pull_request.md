# Refactor OCP-006 (OCP): Switch statement on character input requires modification to handle new value...

**Status:** `patch_failed`  
**Branch:** `refactor/OCP-006` -> `main`  
**Head commit:** `68ce7e9ad175b8602bc625a892c37584b60ad05f`  
**LLM finish:** `FinishReason.STOP` (prompt 3719, completion 3418)  

## Detected issue

- **File**: `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java`
- **Entity**: `UTF8StreamJsonParser._nextTokenNotInObject` (class)
- **Lines (at detection time)**: L690–L732
- **Severity**: high
- **Confidence**: detected by 3 scan(s)

**Description.** Switch statement on character input requires modification to handle new value types

**Reasoning.** The _nextTokenNotInObject method uses a switch statement to dispatch parsing based on the first character of a value. Adding new value types would require modifying this switch block, violating the Open/Closed Principle.

## Fix logic

- **Model**: `gemini-2.5-flash` (temperature 0.2)
- **Patch blocks**: 12
- **Files created** (10): `src/main/java/tools/jackson/core/json/ArrayStartValueHandler.java`, `src/main/java/tools/jackson/core/json/FalseValueHandler.java`, `src/main/java/tools/jackson/core/json/NullValueHandler.java`, `src/main/java/tools/jackson/core/json/ObjectStartValueHandler.java`, `src/main/java/tools/jackson/core/json/PeriodFloatValueHandler.java`, `src/main/java/tools/jackson/core/json/PlusSignNumberValueHandler.java`, `src/main/java/tools/jackson/core/json/SignedNumberValueHandler.java`, `src/main/java/tools/jackson/core/json/TrueValueHandler.java`, `src/main/java/tools/jackson/core/json/UnsignedNumberValueHandler.java`, `src/main/java/tools/jackson/core/json/ValueTokenHandler.java`
- **Files modified** (1): `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java`

**Summary.** Refactor _nextTokenNotInObject to use a strategy pattern for value parsing.

**Rationale.** The original `_nextTokenNotInObject` method used a switch statement to dispatch parsing logic based on the first character of a value. This violates the Open/Closed Principle because adding new value types would require modifying this switch statement. This refactoring introduces a `ValueTokenHandler` interface and several concrete implementations, each responsible for parsing a specific type of value. The `_nextTokenNotInObject` method now iterates through a list of these handlers, delegating the parsing to the first handler that can process the input character. To add a new value type, a new `ValueTokenHandler` implementation can be created and added to the static list, without modifying the `_nextTokenNotInObject` method itself, thus adhering to OCP.

## Changes overview

_12 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java` (9-line block → 12-line replacement)

**Replaces:**

```java
import tools.jackson.core.json.JsonReadFeature;
import tools.jackson.core.json.JsonWriteContext;
import tools.jackson.core.json.ReaderBasedBase64StreamDecoder;
import tools.jackson.core.json.UTF8Base64Decoder;
import tools.jackson.core.json.UTF8DataInputBase64Decoder;
import tools.jackson.core.json.UTF8DataInputJsonParser;
import tools.jackson.core.json.UTF8JsonGenerator;
import tools.jackson.core.json.WriterBasedBase64Encoder;
import tools.jackson.core.json.WriterBasedJsonGenerator;
```

**With:**

```java
import java.util.ArrayList;
import java.util.List;

import tools.jackson.core.json.JsonReadFeature;
import tools.jackson.core.json.JsonWriteContext;
import tools.jackson.core.json.ReaderBasedBase64StreamDecoder;
import tools.jackson.core.json.UTF8Base64Decoder;
import tools.jackson.core.json.UTF8DataInputBase64Decoder;
import tools.jackson.core.json.UTF8DataInputJsonParser;
import tools.jackson.core.json.UTF8JsonGenerator;
import tools.jackson.core.json.WriterBasedBase64Encoder;
import tools.jackson.core.json.WriterBasedJsonGenerator;
```

### 2. EDIT `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java` (45-line block → 29-line replacement)

**Replaces:**

```java
    private final JsonToken _nextTokenNotInObject(int i) throws JacksonException
    {
        if (i == INT_QUOTE) {
            _tokenIncomplete = true;
            return _updateToken(JsonToken.VALUE_STRING);
        }
        switch (i) {
        case '[':
            createChildArrayContext(_tokenInputRow, _tokenInputCol);
            return _updateToken(JsonToken.START_ARRAY);
        case '{':
            createChildObjectContext(_tokenInputRow, _tokenInputCol);
            return _updateToken(JsonToken.START_OBJECT);
        case 't':
            _matchTrue();
            return _updateToken(JsonToken.VALUE_TRUE);
        case 'f':
            _matchFalse();
            return _updateToken(JsonToken.VALUE_FALSE);
        case 'n':
            _matchNull();
            return _updateToken(JsonToken.VALUE_NULL);
        case '-':
            return _updateToken(_parseSignedNumber(true));
        case '+':
            if (!isEnabled(JsonReadFeature.ALLOW_LEADING_PLUS_SIGN_FOR_NUMBERS)) {
                return _updateToken(_handleUnexpectedValue(i));
            }
            return _updateToken(_parseSignedNumber(false));
        case '.': // [core#611]:
            return _updateToken(_parseFloatThatStartsWithPeriod(false, false));
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
            return _updateToken(_parseUnsignedNumber(i));
        }
        return _updateToken(_handleUnexpectedValue(i));
    }
```

**With:**

```java
    private static final List<ValueTokenHandler> VALUE_TOKEN_HANDLERS;

    static {
        VALUE_TOKEN_HANDLERS = new ArrayList<>();
        VALUE_TOKEN_HANDLERS.add(new ArrayStartValueHandler());
        VALUE_TOKEN_HANDLERS.add(new ObjectStartValueHandler());
        VALUE_TOKEN_HANDLERS.add(new TrueValueHandler());
        VALUE_TOKEN_HANDLERS.add(new FalseValueHandler());
        VALUE_TOKEN_HANDLERS.add(new NullValueHandler());
        VALUE_TOKEN_HANDLERS.add(new SignedNumberValueHandler());
        VALUE_TOKEN_HANDLERS.add(new PlusSignNumberValueHandler());
        VALUE_TOKEN_HANDLERS.add(new PeriodFloatValueHandler());
        VALUE_TOKEN_HANDLERS.add(new UnsignedNumberValueHandler());
    }

    private final JsonToken _nextTokenNotInObject(int i) throws JacksonException
    {
        if (i == INT_QUOTE) {
            _tokenIncomplete = true;
            return _updateToken(JsonToken.VALUE_STRING);
        }

        for (ValueTokenHandler handler : VALUE_TOKEN_HANDLERS) {
            if (handler.canHandle(i)) {
                return _updateToken(handler.handle(this, i));
            }
        }
        return _updateToken(_handleUnexpectedValue(i));
    }
```

### 3. CREATE `src/main/java/tools/jackson/core/json/ValueTokenHandler.java` (26 line(s))

```java
package tools.jackson.core.json;

import tools.jackson.core.JacksonException;
import tools.jackson.core.JsonToken;

/**
 * Interface for handling the parsing of a JSON value based on its first character.
 * Implementations encapsulate the logic for a specific type of value.
 */
interface ValueTokenHandler {
    /**
     * Checks if this handler can process the given character as the start of a value.
     * @param firstChar The first character of the potential value.
     * @return True if this handler can process the character, false otherwise.
     */
    boolean canHandle(int firstChar);

    /**
     * Parses the value starting with the given character and returns the corresponding JsonToken.
     * @param parser The parser instance to use for parsing operations.
     * @param firstChar The first character of the value.
     * @return The JsonToken representing the parsed value.
     * @throws JacksonException If an error occurs during parsing.
     */
    JsonToken handle(UTF8StreamJsonParser parser, int firstChar) throws JacksonException;
}
```

### 4. CREATE `src/main/java/tools/jackson/core/json/ArrayStartValueHandler.java` (18 line(s))

```java
package tools.jackson.core.json;

import tools.jackson.core.JacksonException;
import tools.jackson.core.JsonToken;
import static tools.jackson.core.json.JsonParserBase.INT_LBRACKET;

class ArrayStartValueHandler implements ValueTokenHandler {
    @Override
    public boolean canHandle(int firstChar) {
        return firstChar == INT_LBRACKET;
    }

    @Override
    public JsonToken handle(UTF8StreamJsonParser parser, int firstChar) throws JacksonException {
        parser.createChildArrayContext(parser._tokenInputRow, parser._tokenInputCol);
        return JsonToken.START_ARRAY;
    }
}
```

### 5. CREATE `src/main/java/tools/jackson/core/json/ObjectStartValueHandler.java` (18 line(s))

```java
package tools.jackson.core.json;

import tools.jackson.core.JacksonException;
import tools.jackson.core.JsonToken;
import static tools.jackson.core.json.JsonParserBase.INT_LCURLY;

class ObjectStartValueHandler implements ValueTokenHandler {
    @Override
    public boolean canHandle(int firstChar) {
        return firstChar == INT_LCURLY;
    }

    @Override
    public JsonToken handle(UTF8StreamJsonParser parser, int firstChar) throws JacksonException {
        parser.createChildObjectContext(parser._tokenInputRow, parser._tokenInputCol);
        return JsonToken.START_OBJECT;
    }
}
```

### 6. CREATE `src/main/java/tools/jackson/core/json/TrueValueHandler.java` (18 line(s))

```java
package tools.jackson.core.json;

import tools.jackson.core.JacksonException;
import tools.jackson.core.JsonToken;
import static tools.jackson.core.json.JsonParserBase.INT_t;

class TrueValueHandler implements ValueTokenHandler {
    @Override
    public boolean canHandle(int firstChar) {
        return firstChar == INT_t;
    }

    @Override
    public JsonToken handle(UTF8StreamJsonParser parser, int firstChar) throws JacksonException {
        parser._matchTrue();
        return JsonToken.VALUE_TRUE;
    }
}
```

### 7. CREATE `src/main/java/tools/jackson/core/json/FalseValueHandler.java` (18 line(s))

```java
package tools.jackson.core.json;

import tools.jackson.core.JacksonException;
import tools.jackson.core.JsonToken;
import static tools.jackson.core.json.JsonParserBase.INT_f;

class FalseValueHandler implements ValueTokenHandler {
    @Override
    public boolean canHandle(int firstChar) {
        return firstChar == INT_f;
    }

    @Override
    public JsonToken handle(UTF8StreamJsonParser parser, int firstChar) throws JacksonException {
        parser._matchFalse();
        return JsonToken.VALUE_FALSE;
    }
}
```

### 8. CREATE `src/main/java/tools/jackson/core/json/NullValueHandler.java` (18 line(s))

```java
package tools.jackson.core.json;

import tools.jackson.core.JacksonException;
import tools.jackson.core.JsonToken;
import static tools.jackson.core.json.JsonParserBase.INT_n;

class NullValueHandler implements ValueTokenHandler {
    @Override
    public boolean canHandle(int firstChar) {
        return firstChar == INT_n;
    }

    @Override
    public JsonToken handle(UTF8StreamJsonParser parser, int firstChar) throws JacksonException {
        parser._matchNull();
        return JsonToken.VALUE_NULL;
    }
}
```

### 9. CREATE `src/main/java/tools/jackson/core/json/SignedNumberValueHandler.java` (17 line(s))

```java
package tools.jackson.core.json;

import tools.jackson.core.JacksonException;
import tools.jackson.core.JsonToken;
import static tools.jackson.core.json.JsonParserBase.INT_MINUS;

class SignedNumberValueHandler implements ValueTokenHandler {
    @Override
    public boolean canHandle(int firstChar) {
        return firstChar == INT_MINUS;
    }

    @Override
    public JsonToken handle(UTF8StreamJsonParser parser, int firstChar) throws JacksonException {
        return parser._parseSignedNumber(true);
    }
}
```

### 10. CREATE `src/main/java/tools/jackson/core/json/PlusSignNumberValueHandler.java` (20 line(s))

```java
package tools.jackson.core.json;

import tools.jackson.core.JacksonException;
import tools.jackson.core.JsonToken;
import static tools.jackson.core.json.JsonParserBase.INT_PLUS;

class PlusSignNumberValueHandler implements ValueTokenHandler {
    @Override
    public boolean canHandle(int firstChar) {
        return firstChar == INT_PLUS;
    }

    @Override
    public JsonToken handle(UTF8StreamJsonParser parser, int firstChar) throws JacksonException {
        if (!parser.isEnabled(JsonReadFeature.ALLOW_LEADING_PLUS_SIGN_FOR_NUMBERS)) {
            return parser._handleUnexpectedValue(firstChar);
        }
        return parser._parseSignedNumber(false);
    }
}
```

### 11. CREATE `src/main/java/tools/jackson/core/json/PeriodFloatValueHandler.java` (17 line(s))

```java
package tools.jackson.core.json;

import tools.jackson.core.JacksonException;
import tools.jackson.core.JsonToken;
import static tools.jackson.core.json.JsonParserBase.INT_PERIOD;

class PeriodFloatValueHandler implements ValueTokenHandler {
    @Override
    public boolean canHandle(int firstChar) {
        return firstChar == INT_PERIOD;
    }

    @Override
    public JsonToken handle(UTF8StreamJsonParser parser, int firstChar) throws JacksonException {
        return parser._parseFloatThatStartsWithPeriod(false, false);
    }
}
```

### 12. CREATE `src/main/java/tools/jackson/core/json/UnsignedNumberValueHandler.java` (18 line(s))

```java
package tools.jackson.core.json;

import tools.jackson.core.JacksonException;
import tools.jackson.core.JsonToken;
import static tools.jackson.core.json.JsonParserBase.INT_0;
import static tools.jackson.core.json.JsonParserBase.INT_9;

class UnsignedNumberValueHandler implements ValueTokenHandler {
    @Override
    public boolean canHandle(int firstChar) {
        return firstChar >= INT_0 && firstChar <= INT_9;
    }

    @Override
    public JsonToken handle(UTF8StreamJsonParser parser, int firstChar) throws JacksonException {
        return parser._parseUnsignedNumber(firstChar);
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
