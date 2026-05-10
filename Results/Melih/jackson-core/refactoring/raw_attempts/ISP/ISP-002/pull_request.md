# Refactor ISP-002 (ISP): UTF8StreamJsonParser implements the fat JsonParser interface, forcing it to i...

**Status:** `patch_failed`  
**Branch:** `refactor/ISP-002` -> `main`  
**Head commit:** `c0312adeb68851e7c649cb513bc9afa5dc665f48`  
**LLM finish:** `FinishReason.STOP` (prompt 40555, completion 1514)  

## Detected issue

- **File**: `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java`
- **Entity**: `UTF8StreamJsonParser` (class)
- **Lines (at detection time)**: L21–L1780
- **Severity**: medium
- **Confidence**: detected by 4 scan(s)

**Description.** UTF8StreamJsonParser implements the fat JsonParser interface, forcing it to implement many methods that may not be relevant for a stream-based parser.

**Reasoning.** The JsonParser interface is a large, monolithic interface containing methods for all possible parsing behaviors (e.g., binary, textual, numeric, and traversal). A stream-based parser like UTF8StreamJsonParser is forced to implement the entire contract, even though some functionality (like arbitrary binary access) might be secondary or require complex state management not naturally supported by the primary stream-reading model.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 3
- **Files created** (1): `src/main/java/tools/jackson/core/BinaryValueParser.java`
- **Files modified** (2): `src/main/java/tools/jackson/core/JsonParser.java`, `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java`

**Summary.** Extract binary data access methods into a separate interface to improve ISP compliance.

**Rationale.** The JsonParser interface is monolithic. By extracting binary-specific methods into a new BinaryValueParser interface, we allow implementations to opt-in to binary support, reducing the burden on stream-based parsers that may not require full binary access capabilities.

## Changes overview

_3 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `src/main/java/tools/jackson/core/JsonParser.java` (3-line block → 3-line replacement)

**Replaces:**

```java
public abstract class JsonParser
    implements AutoCloseable, Versioned
{
```

**With:**

```java
public abstract class JsonParser
    implements AutoCloseable, Versioned, tools.jackson.core.BinaryValueParser
{
```

### 2. EDIT `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java` (52-line block → 52-line replacement)

**Replaces:**

```java
    @Override
    public byte[] getBinaryValue(Base64Variant b64variant) throws JacksonException
    {
        if (_currToken != JsonToken.VALUE_STRING &&
                (_currToken != JsonToken.VALUE_EMBEDDED_OBJECT || _binaryValue == null)) {
            return _reportError("Current token ("+_currToken+") not VALUE_STRING or VALUE_EMBEDDED_OBJECT, cannot access as binary");
        }
        // To ensure that we won't see inconsistent data, better clear up state...
        if (_tokenIncomplete) {
            try {
                _binaryValue = _base64Decoder.decodeBase64(b64variant);
            } catch (IllegalArgumentException iae) {
                throw _constructReadException("Failed to decode VALUE_STRING as base64 ("+b64variant+"): "+iae.getMessage());
            }
            // let's clear incomplete only now; allows for accessing other textual content in error cases
            _tokenIncomplete = false;
        } else { // may actually require conversion...
            if (_binaryValue == null) {
                @SuppressWarnings("resource")
                ByteArrayBuilder builder = _getByteArrayBuilder();
                // This calls JsonParser.decodeBase64, which is a default method, not a method of this class.
                // So no change needed here.
                decodeBase64(getString(), builder, b64variant);
                _binaryValue = builder.toByteArray();
            }
        }
        return _binaryValue;
    }

    @Override
    public int readBinaryValue(Base64Variant b64variant, OutputStream out) throws JacksonException
    {
        // if we have already read the token, just use whatever we may have
        if (!_tokenIncomplete || _currToken != JsonToken.VALUE_STRING) {
            byte[] b = getBinaryValue(b64variant);
            try {
                out.write(b);
            } catch (IOException e) {
                throw _wrapIOFailure(e);
            }
            return b.length;
        }
        // otherwise do "real" incremental parsing...
        byte[] buf = _ioContext.allocBase64Buffer();
        try {
            return _base64Decoder.readBinary(b64variant, out, buf);
        } catch (IOException e) {
            throw _wrapIOFailure(e);
        } finally {
            _ioContext.releaseBase64Buffer(buf);
        }
    }
```

**With:**

```java
    @Override
    public byte[] getBinaryValue(Base64Variant b64variant) throws JacksonException
    {
        if (_currToken != JsonToken.VALUE_STRING &&
                (_currToken != JsonToken.VALUE_EMBEDDED_OBJECT || _binaryValue == null)) {
            return _reportError("Current token ("+_currToken+") not VALUE_STRING or VALUE_EMBEDDED_OBJECT, cannot access as binary");
        }
        // To ensure that we won't see inconsistent data, better clear up state...
        if (_tokenIncomplete) {
            try {
                _binaryValue = _base64Decoder.decodeBase64(b64variant);
            } catch (IllegalArgumentException iae) {
                throw _constructReadException("Failed to decode VALUE_STRING as base64 ("+b64variant+"): "+iae.getMessage());
            }
            // let's clear incomplete only now; allows for accessing other textual content in error cases
            _tokenIncomplete = false;
        } else { // may actually require conversion...
            if (_binaryValue == null) {
                @SuppressWarnings("resource")
                ByteArrayBuilder builder = _getByteArrayBuilder();
                // This calls JsonParser.decodeBase64, which is a default method, not a method of this class.
                // So no change needed here.
                decodeBase64(getString(), builder, b64variant);
                _binaryValue = builder.toByteArray();
            }
        }
        return _binaryValue;
    }

    @Override
    public int readBinaryValue(Base64Variant b64variant, OutputStream out) throws JacksonException
    {
        // if we have already read the token, just use whatever we may have
        if (!_tokenIncomplete || _currToken != JsonToken.VALUE_STRING) {
            byte[] b = getBinaryValue(b64variant);
            try {
                out.write(b);
            } catch (IOException e) {
                throw _wrapIOFailure(e);
            }
            return b.length;
        }
        // otherwise do "real" incremental parsing...
        byte[] buf = _ioContext.allocBase64Buffer();
        try {
            return _base64Decoder.readBinary(b64variant, out, buf);
        } catch (IOException e) {
            throw _wrapIOFailure(e);
        } finally {
            _ioContext.releaseBase64Buffer(buf);
        }
    }
```

### 3. CREATE `src/main/java/tools/jackson/core/BinaryValueParser.java` (11 line(s))

```java
package tools.jackson.core;

import java.io.OutputStream;

/**
 * Interface for parsers that support binary data access.
 */
public interface BinaryValueParser {
    byte[] getBinaryValue(Base64Variant b64variant) throws JacksonException;
    int readBinaryValue(Base64Variant b64variant, OutputStream out) throws JacksonException;
}
```

## Apply error

```
search_text not found in src/main/java/tools/jackson/core/JsonParser.java (block 0)
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java` | 3558 → - | 114 → - | 9.62 → - | 984 → - | 0 → - |

## Diff

*(no diff — patch was not applied)*
