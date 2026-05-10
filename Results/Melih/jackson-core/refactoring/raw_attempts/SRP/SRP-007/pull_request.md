# Refactor SRP-007 (SRP): The class combines output writer management, JSON structural generation, JSON...

**Status:** `applied_unverified`  
**Branch:** `refactor/SRP-007` -> `main`  
**Head commit:** `62813d7cd06cc5fe317df068b918ab746e871c58`  
**LLM finish:** `FinishReason.STOP` (prompt 20443, completion 8878)  

## Detected issue

- **File**: `src/main/java/tools/jackson/core/json/WriterBasedJsonGenerator.java`
- **Entity**: `WriterBasedJsonGenerator` (class)
- **Lines (at detection time)**: L14–L883
- **Severity**: high
- **Confidence**: detected by 6 scan(s)

**Description.** The class combines output writer management, JSON structural generation, JSON name writing, string/text escaping, raw content writing, Base64 encoding, numeric formatting, boolean/null writing, and detailed character escape sequence generation.

**Reasoning.** This class is another significant SRP violator, similar to `UTF8JsonGenerator`. It manages the `Writer` and internal character buffers (`_flushBuffer()`, `writeRawLong()`), handles JSON structure (`writeStartObject()`), property names (`_writeName()`), and various value types. It includes complex logic for string escaping (`_writeString2()`, `_writeStringASCII()`, `_writeStringCustom()`), Base64 encoding (`_writeBinary()`), numeric formatting (`writeNumber()`), and generating character escape sequences (`_prependOrWriteCharacterEscape()`). A change in any of these distinct responsibilities would require modifying this single, large class.

## Fix logic

- **Model**: `gemini-2.5-flash` (temperature 0.2)
- **Patch blocks**: 5
- **Files created** (2): `src/main/java/tools/jackson/core/json/CharOutputTarget.java`, `src/main/java/tools/jackson/core/json/WriterBasedBase64Encoder.java`
- **Files modified** (1): `src/main/java/tools/jackson/core/json/WriterBasedJsonGenerator.java`

**Summary.** Extracts Base64 encoding logic into a dedicated helper class, `WriterBasedBase64Encoder`.

**Rationale.** The `WriterBasedJsonGenerator` class previously handled Base64 encoding directly, which is a distinct responsibility from general JSON generation and character output management. This refactoring extracts all Base64 encoding and related input stream reading logic into a new `WriterBasedBase64Encoder` class. A new `CharOutputTarget` interface is introduced to allow the encoder to interact with the generator's character buffer and writer without tightly coupling to the generator's internal state. This improves the Single Responsibility Principle by separating the concern of Base64 encoding from the core JSON generation process.

## Changes overview

_5 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `src/main/java/tools/jackson/core/json/WriterBasedJsonGenerator.java` (92-line block → 105-line replacement)

**Replaces:**

```java
public class WriterBasedJsonGenerator
    extends JsonGeneratorBase
{
    protected final static int SHORT_WRITE = 32;

    protected final static char[] HEX_CHARS_UPPER = CharTypes.copyHexChars(true);
    protected final static char[] HEX_CHARS_LOWER = CharTypes.copyHexChars(false);

    private char[] getHexChars() {
        return _cfgWriteHexUppercase ? HEX_CHARS_UPPER : HEX_CHARS_LOWER;
    }

    /*
    /**********************************************************************
    /* Configuration
    /**********************************************************************
     */

    protected final Writer _writer;

    /**
     * Character used for quoting JSON Object property names
     * and String values.
     */
    protected final char _quoteChar;

    /*
    /**********************************************************************
    /* Output buffering
    /**********************************************************************
     */

    /**
     * Intermediate buffer in which contents are buffered before
     * being written using {@link #_writer}.
     */
    protected char[] _outputBuffer;

    /**
     * Pointer to the first buffered character to output
     */
    protected int _outputHead;

    /**
     * Pointer to the position right beyond the last character to output
     * (end marker; may point to position right beyond the end of the buffer)
     */
    protected int _outputTail;

    /**
     * End marker of the output buffer; one past the last valid position
     * within the buffer.
     */
    protected int _outputEnd;

    /**
     * Short (14 char) temporary buffer allocated if needed, for constructing
     * escape sequences
     */
    protected char[] _entityBuffer;
... (32 more line(s) truncated)
```

**With:**

```java
public class WriterBasedJsonGenerator
    extends JsonGeneratorBase
    implements CharOutputTarget // Implements the new interface
{
    protected final static int SHORT_WRITE = 32;

    protected final static char[] HEX_CHARS_UPPER = CharTypes.copyHexChars(true);
    protected final static char[] HEX_CHARS_LOWER = CharTypes.copyHexChars(false);

    private char[] getHexChars() {
        return _cfgWriteHexUppercase ? HEX_CHARS_UPPER : HEX_CHARS_LOWER;
    }

    /*
    /**********************************************************************
    /* Configuration
    /**********************************************************************
     */

    protected final Writer _writer;

    /**
     * Character used for quoting JSON Object property names
     * and String values.
     */
    protected final char _quoteChar;

    /*
    /**********************************************************************
    /* Output buffering
    /**********************************************************************
     */

    /**
     * Intermediate buffer in which contents are buffered before
     * being written using {@link #_writer}.
     */
    protected char[] _outputBuffer;

    /**
     * Pointer to the first buffered character to output
     */
    protected int _outputHead;

    /**
     * Pointer to the position right beyond the last character to output
     * (end marker; may point to position right beyond the end of the buffer)
     */
    protected int _outputTail;

    /**
     * End marker of the output buffer; one past the last valid position
     * within the buffer.
     */
    protected int _outputEnd;

    /**
     * Short (14 char) temporary buffer allocated if needed, for constructing
     * escape sequences
     */
... (45 more line(s) truncated)
```

### 2. EDIT `src/main/java/tools/jackson/core/json/WriterBasedJsonGenerator.java` (66-line block → 112-line replacement)

**Replaces:**

```java
    /*
    /**********************************************************************
    /* Output method implementations, base64-encoded binary
    /**********************************************************************
     */

    @Override
    public JsonGenerator writeBinary(Base64Variant b64variant, byte[] data, int offset, int len)
        throws JacksonException
    {
        _checkRangeBoundsForByteArray(data, offset, len);

        _verifyValueWrite(WRITE_BINARY);
        // Starting quotes
        if (_outputTail >= _outputEnd) {
            _flushBuffer();
        }
        _outputBuffer[_outputTail++] = _quoteChar;
        _writeBinary(b64variant, data, offset, offset+len);
        // and closing quotes
        if (_outputTail >= _outputEnd) {
            _flushBuffer();
        }
        _outputBuffer[_outputTail++] = _quoteChar;
        return this;
    }

    @Override
    public int writeBinary(Base64Variant b64variant,
            InputStream data, int dataLength)
        throws JacksonException
    {
        _verifyValueWrite(WRITE_BINARY);
        // Starting quotes
        if (_outputTail >= _outputEnd) {
            _flushBuffer();
        }
        _outputBuffer[_outputTail++] = _quoteChar;
        byte[] encodingBuffer = _ioContext.allocBase64Buffer();
        int bytes;
        try {
            if (dataLength < 0) { // length unknown
                bytes = _writeBinary(b64variant, data, encodingBuffer);
            } else {
                int missing = _writeBinary(b64variant, data, encodingBuffer, dataLength);
                if (missing > 0) {
                    _reportError("Too few bytes available: missing "+missing+" bytes (out of "+dataLength+")");
                }
                bytes = dataLength;
            }
        } finally {
            _ioContext.releaseBase64Buffer(encodingBuffer);
        }
        // and closing quotes
        if (_outputTail >= _outputEnd) {
            _flushBuffer();
        }
        _outputBuffer[_outputTail++] = _quoteChar;
        return bytes;
    }
... (6 more line(s) truncated)
```

**With:**

```java
    /*
    /**********************************************************************
    /* Output method implementations, base64-encoded binary
    /**********************************************************************
     */

    @Override
    public JsonGenerator writeBinary(Base64Variant b64variant, byte[] data, int offset, int len)
        throws JacksonException
    {
        _checkRangeBoundsForByteArray(data, offset, len);

        _verifyValueWrite(WRITE_BINARY);
        // Starting quotes
        if (_outputTail >= _outputEnd) {
            _flushBuffer();
        }
        _outputBuffer[_outputTail++] = _quoteChar;
        _base64Encoder.writeBinary(b64variant, data, offset, offset+len); // Delegate to helper
        // and closing quotes
        if (_outputTail >= _outputEnd) {
            _flushBuffer();
        }
        _outputBuffer[_outputTail++] = _quoteChar;
        return this;
    }

    @Override
    public int writeBinary(Base64Variant b64variant,
            InputStream data, int dataLength)
        throws JacksonException
    {
        _verifyValueWrite(WRITE_BINARY);
        // Starting quotes
        if (_outputTail >= _outputEnd) {
            _flushBuffer();
        }
        _outputBuffer[_outputTail++] = _quoteChar;
        byte[] encodingBuffer = _ioContext.allocBase64Buffer();
        int bytes;
        try {
            if (dataLength < 0) { // length unknown
                bytes = _base64Encoder.writeBinary(b64variant, data, encodingBuffer); // Delegate to helper
            } else {
                int missing = _base64Encoder.writeBinary(b64variant, data, encodingBuffer, dataLength); // Delegate to helper
                if (missing > 0) {
                    _reportError("Too few bytes available: missing "+missing+" bytes (out of "+dataLength+")");
                }
                bytes = dataLength;
            }
        } finally {
            _ioContext.releaseBase64Buffer(encodingBuffer);
        }
        // and closing quotes
        if (_outputTail >= _outputEnd) {
            _flushBuffer();
        }
        _outputBuffer[_outputTail++] = _quoteChar;
        return bytes;
    }
... (52 more line(s) truncated)
```

### 3. EDIT `src/main/java/tools/jackson/core/json/WriterBasedJsonGenerator.java` (196-line block → 5-line replacement)

**Replaces:**

```java
    protected final void _writeBinary(Base64Variant b64variant, byte[] input, int inputPtr, final int inputEnd)
        throws JacksonException
    {
        // Encoding is by chunks of 3 input, 4 output chars, so:
        int safeInputEnd = inputEnd - 3;
        // Let's also reserve room for possible (and quoted) lf char each round
        int safeOutputEnd = _outputEnd - 6;
        int chunksBeforeLF = b64variant.getMaxLineLength() >> 2;

        // Ok, first we loop through all full triplets of data:
        while (inputPtr <= safeInputEnd) {
            if (_outputTail > safeOutputEnd) { // need to flush
                _flushBuffer();
            }
            // First, mash 3 bytes into lsb of 32-bit int
            int b24 = (input[inputPtr++]) << 8;
            b24 |= (input[inputPtr++]) & 0xFF;
            b24 = (b24 << 8) | ((input[inputPtr++]) & 0xFF);
            _outputTail = b64variant.encodeBase64Chunk(b24, _outputBuffer, _outputTail);
            if (--chunksBeforeLF <= 0) {
                // note: must quote in JSON value
                _outputBuffer[_outputTail++] = '\\';
                _outputBuffer[_outputTail++] = 'n';
                chunksBeforeLF = b64variant.getMaxLineLength() >> 2;
            }
        }

        // And then we may have 1 or 2 leftover bytes to encode
        int inputLeft = inputEnd - inputPtr; // 0, 1 or 2
        if (inputLeft > 0) { // yes, but do we have room for output?
            if (_outputTail > safeOutputEnd) { // don't really need 6 bytes but...
                _flushBuffer();
            }
            int b24 = (input[inputPtr++]) << 16;
            if (inputLeft == 2) {
                b24 |= ((input[inputPtr++]) & 0xFF) << 8;
            }
            _outputTail = b64variant.encodeBase64Partial(b24, inputLeft, _outputBuffer, _outputTail);
        }
    }

    // write-method called when length is definitely known
    protected final int _writeBinary(Base64Variant b64variant,
            InputStream data, byte[] readBuffer, int bytesLeft)
        throws JacksonException
    {
        int inputPtr = 0;
        int inputEnd = 0;
        int lastFullOffset = -3;

        // Let's also reserve room for possible (and quoted) lf char each round
        int safeOutputEnd = _outputEnd - 6;
        int chunksBeforeLF = b64variant.getMaxLineLength() >> 2;

        while (bytesLeft > 2) { // main loop for full triplets
            if (inputPtr > lastFullOffset) {
                inputEnd = _readMore(data, readBuffer, inputPtr, inputEnd, bytesLeft);
                inputPtr = 0;
                if (inputEnd < 3) { // required to try to read to have at least 3 bytes
                    break;
... (136 more line(s) truncated)
```

**With:**

```java
    /*
    /**********************************************************************
    /* Internal methods, low-level writing, other
    /**********************************************************************
     */
```

### 4. CREATE `src/main/java/tools/jackson/core/json/CharOutputTarget.java` (66 line(s))

```java
package tools.jackson.core.json;

import java.io.IOException;
import java.io.Writer;

import tools.jackson.core.JacksonException;
import tools.jackson.core.io.IOContext;

/**
 * Interface for components that need to write characters to a buffer
 * managed by a {@link WriterBasedJsonGenerator} and trigger flushing.
 * This allows for delegating specific writing responsibilities while
 * keeping buffer management centralized.
 */
public interface CharOutputTarget {
    /**
     * Returns the internal character buffer used for output.
     * @return The output buffer.
     */
    char[] getOutputBuffer();

    /**
     * Returns the current tail pointer of the output buffer.
     * @return The output tail.
     */
    int getOutputTail();

    /**
     * Returns the end marker of the output buffer.
     * @return The output end.
     */
    int getOutputEnd();

    /**
     * Sets the new tail pointer of the output buffer.
     * @param newTail The new output tail value.
     */
    void setOutputTail(int newTail);

    /**
     * Flushes the internal output buffer to the underlying writer.
     * This method corresponds to {@link WriterBasedJsonGenerator#_flushBuffer()}.
     * @throws JacksonException if an I/O error occurs.
     */
    void flushOutputBuffer() throws JacksonException;

    /**
     * Wraps an {@link IOException} into a {@link JacksonException}.
     * This method corresponds to {@link WriterBasedJsonGenerator#_wrapIOFailure(IOException)}.
     * @param e The IOException to wrap.
     * @return The wrapped JacksonException.
     */
    JacksonException wrapIOException(IOException e);

    /**
     * Returns the underlying {@link Writer} used for output.
     * @return The underlying writer.
     */
    Writer getUnderlyingWriter();

... (6 more line(s) truncated)
```

### 5. CREATE `src/main/java/tools/jackson/core/json/WriterBasedBase64Encoder.java` (280 line(s))

```java
package tools.jackson.core.json;

import java.io.IOException;
import java.io.InputStream;

import tools.jackson.core.Base64Variant;
import tools.jackson.core.JacksonException;
import tools.jackson.core.io.IOContext;

/**
 * Helper class for {@link WriterBasedJsonGenerator} to handle Base64 encoding
 * and writing to the underlying character buffer/writer.
 */
public class WriterBasedBase64Encoder {

    protected final CharOutputTarget _outputTarget;
    protected final Writer _writer;
    protected final char[] _outputBuffer;
    protected final int _outputEnd;
    protected final IOContext _ioContext;

    public WriterBasedBase64Encoder(CharOutputTarget outputTarget) {
        _outputTarget = outputTarget;
        _writer = outputTarget.getUnderlyingWriter();
        _outputBuffer = outputTarget.getOutputBuffer();
        _outputEnd = outputTarget.getOutputEnd();
        _ioContext = outputTarget.getIOContext();
    }

    /**
     * Encodes and writes a byte array as Base64.
     *
     * @param b64variant Base64 variant to use for encoding.
     * @param input Input byte array.
     * @param inputPtr Start offset in the input array.
     * @param inputEnd End offset in the input array (exclusive).
     * @throws JacksonException if an I/O error occurs.
     */
    public void writeBinary(Base64Variant b64variant, byte[] input, int inputPtr, final int inputEnd)
        throws JacksonException
    {
        // Encoding is by chunks of 3 input, 4 output chars, so:
        int safeInputEnd = inputEnd - 3;
        // Let's also reserve room for possible (and quoted) lf char each round
        int safeOutputEnd = _outputEnd - 6;
        int chunksBeforeLF = b64variant.getMaxLineLength() >> 2;

        int currentOutputTail = _outputTarget.getOutputTail();

        // Ok, first we loop through all full triplets of data:
        while (inputPtr <= safeInputEnd) {
            if (currentOutputTail > safeOutputEnd) { // need to flush
                _outputTarget.setOutputTail(currentOutputTail);
                _outputTarget.flushOutputBuffer();
                currentOutputTail = _outputTarget.getOutputTail(); // Re-read after flush
            }
            // First, mash 3 bytes into lsb of 32-bit int
            int b24 = (input[inputPtr++]) << 8;
            b24 |= (input[inputPtr++]) & 0xFF;
            b24 = (b24 << 8) | ((input[inputPtr++]) & 0xFF);
... (220 more line(s) truncated)
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/main/java/tools/jackson/core/json/CharOutputTarget.java` | - → 56 | - → 0 | - → 7 | - → 7 | - → 0 |
| `src/main/java/tools/jackson/core/json/WriterBasedBase64Encoder.java` | - → 245 | - → 4 | - → 14 | - → 53 | - → 0 |
| `src/main/java/tools/jackson/core/json/WriterBasedJsonGenerator.java` | 1934 → 1820 | 76 → 80 | 5.76 → 5.03 | 363 → 323 | 0 → 0 |

## Diff

```diff
diff --git a/src/main/java/tools/jackson/core/json/WriterBasedJsonGenerator.java b/src/main/java/tools/jackson/core/json/WriterBasedJsonGenerator.java
index d942948..2a08017 100644
--- a/src/main/java/tools/jackson/core/json/WriterBasedJsonGenerator.java
+++ b/src/main/java/tools/jackson/core/json/WriterBasedJsonGenerator.java
@@ -16,6 +16,7 @@ import tools.jackson.core.io.NumberOutput;
  */
 public class WriterBasedJsonGenerator
     extends JsonGeneratorBase
+    implements CharOutputTarget // Implements the new interface
 {
     protected final static int SHORT_WRITE = 32;
 
@@ -87,6 +88,17 @@ public class WriterBasedJsonGenerator
      */
     protected char[] _copyBuffer;
 
+    /*
+    /**********************************************************************
+    /* Helper objects
+    /**********************************************************************
+     */
+
+    /**
+     * Helper object for Base64 encoding and writing.
+     */
+    protected WriterBasedBase64Encoder _base64Encoder;
+
     /*
     /**********************************************************************
     /* Life-cycle
@@ -105,6 +117,7 @@ public class WriterBasedJsonGenerator
         _outputEnd = _outputBuffer.length;
         _quoteChar = quoteChar;
         setCharacterEscapes(charEsc);
+        _base64Encoder = new WriterBasedBase64Encoder(this); // Initialize the helper
     }
 
     @Override
@@ -718,7 +731,7 @@ public class WriterBasedJsonGenerator
             _flushBuffer();
         }
         _outputBuffer[_outputTail++] = _quoteChar;
-        _writeBinary(b64variant, data, offset, offset+len);
+        _base64Encoder.writeBinary(b64variant, data, offset, offset+len); // Delegate to helper
         // and closing quotes
         if (_outputTail >= _outputEnd) {
             _flushBuffer();
@@ -742,9 +755,9 @@ public class WriterBasedJsonGenerator
         int bytes;
         try {
             if (dataLength < 0) { // length unknown
-                bytes = _writeBinary(b64variant, data, encodingBuffer);
+                bytes = _base64Encoder.writeBinary(b64variant, data, encodingBuffer); // Delegate to helper
             } else {
-                int missing = _writeBinary(b64variant, data, encodingBuffer, dataLength);
+                int missing = _base64Encoder.writeBinary(b64variant, data, encodingBuffer, dataLength); // Delegate to helper
                 if (missing > 0) {
                     _reportError("Too few bytes available: missing "+missing+" bytes (out of "+dataLength+")");
                 }
@@ -761,6 +774,52 @@ public class WriterBasedJsonGenerator
         return bytes;
     }
 
+    /*
+    /**********************************************************************
+    /* CharOutputTarget implementation
+    /**********************************************************************
+     */
+
+    @Override
+    public char[] getOutputBuffer() {
+        return _outputBuffer;
+    }
+
+    @Override
+    public int getOutputTail() {
+        return _outputTail;
+    }
+
+    @Override
+    public int getOutputEnd() {
+        return _outputEnd;
+    }
+
+    @Override
+    public void setOutputTail(int newTail) {
+        _outputTail = newTail;
+    }
+
+    @Override
+    public void flushOutputBuffer() throws JacksonException {
+        _flushBuffer();
+    }
+
+    @Override
+    public JacksonException wrapIOException(IOException e) {
+        return _wrapIOFailure(e);
+    }
+
+    @Override
+    public Writer getUnderlyingWriter() {
+        return _writer;
+    }
+
+    @Override
+    public IOContext getIOContext() {
+        return _ioContext;
+    }
+
     /*
     /**********************************************************************
     /* Output method implementations, primitive
@@ -1673,197 +1732,6 @@ public class WriterBasedJsonGenerator
     /**********************************************************************
      */
 
-    protected final void _writeBinary(Base64Variant b64variant, byte[] input, int inputPtr, final int inputEnd)
-        throws JacksonException
-    {
-        // Encoding is by chunks of 3 input, 4 output chars, so:
-        int safeInputEnd = inputEnd - 3;
-        // Let's also reserve room for possible (and quoted) lf char each round
-        int safeOutputEnd = _outputEnd - 6;
-        int chunksBeforeLF = b64variant.getMaxLineLength() >> 2;
-
-        // Ok, first we loop through all full triplets of data:
-        while (inputPtr <= safeInputEnd) {
-            if (_outputTail > safeOutputEnd) { // need to flush
-                _flushBuffer();
-            }
-            // First, mash 3 bytes into lsb of 32-bit int
-            int b24 = (input[inputPtr++]) << 8;
-            b24 |= (input[inputPtr++]) & 0xFF;
-            b24 = (b24 << 8) | ((input[inputPtr++]) & 0xFF);
-            _outputTail = b64variant.encodeBase64Chunk(b24, _outputBuffer, _outputTail);
-            if (--chunksBeforeLF <= 0) {
-                // note: must quote in JSON value
-                _outputBuffer[_outputTail++] = '\\';
-                _outputBuffer[_outputTail++] = 'n';
-                chunksBeforeLF = b64variant.getMaxLineLength() >> 2;
-            }
-        }
-
-        // And then we may have 1 or 2 leftover bytes to encode
-        int inputLeft = inputEnd - inputPtr; // 0, 1 or 2
-        if (inputLeft > 0) { // yes, but do we have room for output?
-            if (_outputTail > safeOutputEnd) { // don't really need 6 bytes but...
-                _flushBuffer();
-            }
-            int b24 = (input[inputPtr++]) << 16;
-            if (inputLeft == 2) {
-                b24 |= ((input[inputPtr++]) & 0xFF) << 8;
-            }
-            _outputTail = b64variant.encodeBase64Partial(b24, inputLeft, _outputBuffer, _outputTail);
-        }
-    }
-
-    // write-method called when length is definitely known
-    protected final int _writeBinary(Base64Variant b64variant,
-            InputStream data, byte[] readBuffer, int bytesLeft)
-        throws JacksonException
-    {
-        int inputPtr = 0;
-        int inputEnd = 0;
-        int lastFullOffset = -3;
-
-        // Let's also reserve room for possible (and quoted) lf char each round
-        int safeOutputEnd = _outputEnd - 6;
-        int chunksBeforeLF = b64variant.getMaxLineLength() >> 2;
-
-        while (bytesLeft > 2) { // main loop for full triplets
-            if (inputPtr > lastFullOffset) {
-                inputEnd = _readMore(data, readBuffer, inputPtr, inputEnd, bytesLeft);
-                inputPtr = 0;
-                if (inputEnd < 3) { // required to try to read to have at least 3 bytes
-                    break;
-                }
-                lastFullOffset = inputEnd-3;
-            }
-            if (_outputTail > safeOutputEnd) { // need to flush
-                _flushBuffer();
-            }
-            int b24 = (readBuffer[inputPtr++]) << 8;
-            b24 |= (readBuffer[inputPtr++]) & 0xFF;
-            b24 = (b24 << 8) | ((readBuffer[inputPtr++]) & 0xFF);
-            bytesLeft -= 3;
-            _outputTail = b64variant.encodeBase64Chunk(b24, _outputBuffer, _outputTail);
-            if (--chunksBeforeLF <= 0) {
-                _outputBuffer[_outputTail++] = '\\';
-                _outputBuffer[_outputTail++] = 'n';
-                chunksBeforeLF = b64variant.getMaxLineLength() >> 2;
-            }
-        }
-
-        // And then we may have 1 or 2 leftover bytes to encode
-        if (bytesLeft > 0) {
-            inputEnd = _readMore(data, readBuffer, inputPtr, inputEnd, bytesLeft);
-            inputPtr = 0;
-            if (inputEnd > 0) { // yes, but do we have room for output?
-                if (_outputTail > safeOutputEnd) { // don't really need 6 bytes but...
-                    _flushBuffer();
-                }
-                int b24 = (readBuffer[inputPtr++]) << 16;
-                int amount;
-                if (inputPtr < inputEnd) {
-                    b24 |= ((readBuffer[inputPtr]) & 0xFF) << 8;
-                    amount = 2;
-                } else {
-                    amount = 1;
-                }
-                _outputTail = b64variant.encodeBase64Partial(b24, amount, _outputBuffer, _outputTail);
-                bytesLeft -= amount;
-            }
-        }
-        return bytesLeft;
-    }
-
-    // write method when length is unknown
-    protected final int _writeBinary(Base64Variant b64variant,
-            InputStream data, byte[] readBuffer)
-        throws JacksonException
-    {
-        int inputPtr = 0;
-        int inputEnd = 0;
-        int lastFullOffset = -3;
-        int bytesDone = 0;
-
-        // Let's also reserve room for possible (and quoted) LF char each round
-        int safeOutputEnd = _outputEnd - 6;
-        int chunksBeforeLF = b64variant.getMaxLineLength() >> 2;
-
-        // Ok, first we loop through all full triplets of data:
-        while (true) {
-            if (inputPtr > lastFullOffset) { // need to load more
-                inputEnd = _readMore(data, readBuffer, inputPtr, inputEnd, readBuffer.length);
-                inputPtr = 0;
-                if (inputEnd < 3) { // required to try to read to have at least 3 bytes
-                    break;
-                }
-                lastFullOffset = inputEnd-3;
-            }
-            if (_outputTail > safeOutputEnd) { // need to flush
-                _flushBuffer();
-            }
-            // First, mash 3 bytes into lsb of 32-bit int
-            int b24 = (readBuffer[inputPtr++]) << 8;
-            b24 |= (readBuffer[inputPtr++]) & 0xFF;
-            b24 = (b24 << 8) | ((readBuffer[inputPtr++]) & 0xFF);
-            bytesDone += 3;
-            _outputTail = b64variant.encodeBase64Chunk(b24, _outputBuffer, _outputTail);
-            if (--chunksBeforeLF <= 0) {
-                _outputBuffer[_outputTail++] = '\\';
-                _outputBuffer[_outputTail++] = 'n';
-                chunksBeforeLF = b64variant.getMaxLineLength() >> 2;
-            }
-        }
-
-        // And then we may have 1 or 2 leftover bytes to encode
-        if (inputPtr < inputEnd) { // yes, but do we have room for output?
-            if (_outputTail > safeOutputEnd) { // don't really need 6 bytes but...
-                _flushBuffer();
-            }
-            int b24 = (readBuffer[inputPtr++]) << 16;
-            int amount = 1;
-            if (inputPtr < inputEnd) {
-                b24 |= ((readBuffer[inputPtr]) & 0xFF) << 8;
-                amount = 2;
-            }
-            bytesDone += amount;
-            _outputTail = b64variant.encodeBase64Partial(b24, amount, _outputBuffer, _outputTail);
-        }
-        return bytesDone;
-    }
-
-    private int _readMore(InputStream in,
-            byte[] readBuffer, int inputPtr, int inputEnd,
-            int maxRead) throws JacksonException
-    {
-        // anything to shift to front?
-        int i = 0;
-        while (inputPtr < inputEnd) {
-            readBuffer[i++]  = readBuffer[inputPtr++];
-        }
-        inputPtr = 0;
-        inputEnd = i;
-        maxRead = Math.min(maxRead, readBuffer.length);
-
-        do {
-            int length = maxRead - inputEnd;
-            if (length == 0) {
-                break;
-            }
-            int count;
-
-            try {
-                count = in.read(readBuffer, inputEnd, length);
-            } catch (IOException e) {
-                throw _wrapIOFailure(e);
-            }
-            if (count < 0) {
-                return inputEnd;
-            }
-            inputEnd += count;
-        } while (inputEnd < 3);
-        return inputEnd;
-    }
-
     /*
     /**********************************************************************
     /* Internal methods, low-level writing, other
diff --git a/src/main/java/tools/jackson/core/json/CharOutputTarget.java b/src/main/java/tools/jackson/core/json/CharOutputTarget.java
new file mode 100644
index 0000000..0000000
--- /dev/null
+++ b/src/main/java/tools/jackson/core/json/CharOutputTarget.java
@@ -0,0 +1,66 @@
+package tools.jackson.core.json;
+
+import java.io.IOException;
+import java.io.Writer;
+
+import tools.jackson.core.JacksonException;
+import tools.jackson.core.io.IOContext;
+
+/**
+ * Interface for components that need to write characters to a buffer
+ * managed by a {@link WriterBasedJsonGenerator} and trigger flushing.
+ * This allows for delegating specific writing responsibilities while
+ * keeping buffer management centralized.
+ */
+public interface CharOutputTarget {
+    /**
+     * Returns the internal character buffer used for output.
+     * @return The output buffer.
+     */
+    char[] getOutputBuffer();
+
+    /**
+     * Returns the current tail pointer of the output buffer.
+     * @return The output tail.
+     */
+    int getOutputTail();
+
+    /**
+     * Returns the end marker of the output buffer.
+     * @return The output end.
+     */
+    int getOutputEnd();
+
+    /**
+     * Sets the new tail pointer of the output buffer.
+     * @param newTail The new output tail value.
+     */
+    void setOutputTail(int newTail);
+
+    /**
+     * Flushes the internal output buffer to the underlying writer.
+     * This method corresponds to {@link WriterBasedJsonGenerator#_flushBuffer()}.
+     * @throws JacksonException if an I/O error occurs.
+     */
+    void flushOutputBuffer() throws JacksonException;
+
+    /**
+     * Wraps an {@link IOException} into a {@link JacksonException}.
+     * This method corresponds to {@link WriterBasedJsonGenerator#_wrapIOFailure(IOException)}.
+     * @param e The IOException to wrap.
+     * @return The wrapped JacksonException.
+     */
+    JacksonException wrapIOException(IOException e);
+
+    /**
+     * Returns the underlying {@link Writer} used for output.
+     * @return The underlying writer.
+     */
+    Writer getUnderlyingWriter();
+
+    /**
+     * Returns the {@link IOContext} associated with this generator.
+     * @return The IOContext.
+     */
+    IOContext getIOContext();
+}
\ No newline at end of file
diff --git a/src/main/java/tools/jackson/core/json/WriterBasedBase64Encoder.java b/src/main/java/tools/jackson/core/json/WriterBasedBase64Encoder.java
new file mode 100644
index 0000000..0000000
--- /dev/null
+++ b/src/main/java/tools/jackson/core/json/WriterBasedBase64Encoder.java
@@ -0,0 +1,280 @@
+package tools.jackson.core.json;
+
+import java.io.IOException;
+import java.io.InputStream;
+
+import tools.jackson.core.Base64Variant;
+import tools.jackson.core.JacksonException;
+import tools.jackson.core.io.IOContext;
+
+/**
+ * Helper class for {@link WriterBasedJsonGenerator} to handle Base64 encoding
+ * and writing to the underlying character buffer/writer.
+ */
+public class WriterBasedBase64Encoder {
+
+    protected final CharOutputTarget _outputTarget;
+    protected final Writer _writer;
+    protected final char[] _outputBuffer;
+    protected final int _outputEnd;
+    protected final IOContext _ioContext;
+
+    public WriterBasedBase64Encoder(CharOutputTarget outputTarget) {
+        _outputTarget = outputTarget;
+        _writer = outputTarget.getUnderlyingWriter();
+        _outputBuffer = outputTarget.getOutputBuffer();
+        _outputEnd = outputTarget.getOutputEnd();
+        _ioContext = outputTarget.getIOContext();
+    }
+
+    /**
+     * Encodes and writes a byte array as Base64.
+     *
+     * @param b64variant Base64 variant to use for encoding.
+     * @param input Input byte array.
+     * @param inputPtr Start offset in the input array.
+     * @param inputEnd End offset in the input array (exclusive).
+     * @throws JacksonException if an I/O error occurs.
+     */
+    public void writeBinary(Base64Variant b64variant, byte[] input, int inputPtr, final int inputEnd)
+        throws JacksonException
+    {
+        // Encoding is by chunks of 3 input, 4 output chars, so:
+        int safeInputEnd = inputEnd - 3;
+        // Let's also reserve room for possible (and quoted) lf char each round
+        int safeOutputEnd = _outputEnd - 6;
+        int chunksBeforeLF = b64variant.getMaxLineLength() >> 2;
+
+        int currentOutputTail = _outputTarget.getOutputTail();
+
+        // Ok, first we loop through all full triplets of data:
+        while (inputPtr <= safeInputEnd) {
+            if (currentOutputTail > safeOutputEnd) { // need to flush
+                _outputTarget.setOutputTail(currentOutputTail);
+                _outputTarget.flushOutputBuffer();
+                currentOutputTail = _outputTarget.getOutputTail(); // Re-read after flush
+            }
+            // First, mash 3 bytes into lsb of 32-bit int
+            int b24 = (input[inputPtr++]) << 8;
+            b24 |= (input[inputPtr++]) & 0xFF;
+            b24 = (b24 << 8) | ((input[inputPtr++]) & 0xFF);
+            currentOutputTail = b64variant.encodeBase64Chunk(b24, _outputBuffer, currentOutputTail);
+            if (--chunksBeforeLF <= 0) {
+                // note: must quote in JSON value
+                _outputBuffer[currentOutputTail++] = '\\';
+                _outputBuffer[currentOutputTail++] = 'n';
+                chunksBeforeLF = b64variant.getMaxLineLength() >> 2;
+            }
+        }
+
+        // And then we may have 1 or 2 leftover bytes to encode
+        int inputLeft = inputEnd - inputPtr; // 0, 1 or 2
+        if (inputLeft > 0) { // yes, but do we have room for output?
+            if (currentOutputTail > safeOutputEnd) { // don't really need 6 bytes but...
+                _outputTarget.setOutputTail(currentOutputTail);
+                _outputTarget.flushOutputBuffer();
+                currentOutputTail = _outputTarget.getOutputTail(); // Re-read after flush
+            }
+            int b24 = (input[inputPtr++]) << 16;
+            if (inputLeft == 2) {
+                b24 |= ((input[inputPtr++]) & 0xFF) << 8;
+            }
+            currentOutputTail = b64variant.encodeBase64Partial(b24, inputLeft, _outputBuffer, currentOutputTail);
+        }
+        _outputTarget.setOutputTail(currentOutputTail);
+    }
+
+    /**
+     * Encodes and writes binary data from an {@link InputStream} as Base64,
+     * when the total length is known.
+     *
+     * @param b64variant Base64 variant to use for encoding.
+     * @param data Input stream to read bytes from.
+     * @param readBuffer Buffer to use for reading from the input stream.
+     * @param bytesLeft Total number of bytes to read and encode.
+     * @return The number of bytes remaining (should be 0 if successful).
+     * @throws JacksonException if an I/O error occurs.
+     */
+    public int writeBinary(Base64Variant b64variant,
+            InputStream data, byte[] readBuffer, int bytesLeft)
+        throws JacksonException
+    {
+        int inputPtr = 0;
+        int inputEnd = 0;
+        int lastFullOffset = -3;
+
+        // Let's also reserve room for possible (and quoted) lf char each round
+        int safeOutputEnd = _outputEnd - 6;
+        int chunksBeforeLF = b64variant.getMaxLineLength() >> 2;
+
+        int currentOutputTail = _outputTarget.getOutputTail();
+
+        while (bytesLeft > 2) { // main loop for full triplets
+            if (inputPtr > lastFullOffset) {
+                inputEnd = _readMore(data, readBuffer, inputPtr, inputEnd, bytesLeft);
+                inputPtr = 0;
+                if (inputEnd < 3) { // required to try to read to have at least 3 bytes
+                    break;
+                }
+                lastFullOffset = inputEnd-3;
+            }
+            if (currentOutputTail > safeOutputEnd) { // need to flush
+                _outputTarget.setOutputTail(currentOutputTail);
+                _outputTarget.flushOutputBuffer();
+                currentOutputTail = _outputTarget.getOutputTail(); // Re-read after flush
+            }
+            int b24 = (readBuffer[inputPtr++]) << 8;
+            b24 |= (readBuffer[inputPtr++]) & 0xFF;
+            b24 = (b24 << 8) | ((readBuffer[inputPtr++]) & 0xFF);
+            bytesLeft -= 3;
+            currentOutputTail = b64variant.encodeBase64Chunk(b24, _outputBuffer, currentOutputTail);
+            if (--chunksBeforeLF <= 0) {
+                _outputBuffer[currentOutputTail++] = '\\';
+                _outputBuffer[currentOutputTail++] = 'n';
+                chunksBeforeLF = b64variant.getMaxLineLength() >> 2;
+            }
+        }
+
+        // And then we may have 1 or 2 leftover bytes to encode
+        if (bytesLeft > 0) {
+            inputEnd = _readMore(data, readBuffer, inputPtr, inputEnd, bytesLeft);
+            inputPtr = 0;
+            if (inputEnd > 0) { // yes, but do we have room for output?
+                if (currentOutputTail > safeOutputEnd) { // don't really need 6 bytes but...
+                    _outputTarget.setOutputTail(currentOutputTail);
+                    _outputTarget.flushOutputBuffer();
+                    currentOutputTail = _outputTarget.getOutputTail(); // Re-read after flush
+                }
+                int b24 = (readBuffer[inputPtr++]) << 16;
+                int amount;
+                if (inputPtr < inputEnd) {
+                    b24 |= ((readBuffer[inputPtr]) & 0xFF) << 8;
+                    amount = 2;
+                } else {
+                    amount = 1;
+                }
+                currentOutputTail = b64variant.encodeBase64Partial(b24, amount, _outputBuffer, currentOutputTail);
+                bytesLeft -= amount;
+            }
+        }
+        _outputTarget.setOutputTail(currentOutputTail);
+        return bytesLeft;
+    }
+
+    /**
+     * Encodes and writes binary data from an {@link InputStream} as Base64,
+     * when the total length is unknown.
+     *
+     * @param b64variant Base64 variant to use for encoding.
+     * @param data Input stream to read bytes from.
+     * @param readBuffer Buffer to use for reading from the input stream.
+     * @return The total number of bytes read and encoded.
+     * @throws JacksonException if an I/O error occurs.
+     */
+    public int writeBinary(Base64Variant b64variant,
+            InputStream data, byte[] readBuffer)
+        throws JacksonException
+    {
+        int inputPtr = 0;
+        int inputEnd = 0;
+        int lastFullOffset = -3;
+        int bytesDone = 0;
+
+        // Let's also reserve room for possible (and quoted) LF char each round
+        int safeOutputEnd = _outputEnd - 6;
+        int chunksBeforeLF = b64variant.getMaxLineLength() >> 2;
+
+        int currentOutputTail = _outputTarget.getOutputTail();
+
+        // Ok, first we loop through all full triplets of data:
+        while (true) {
+            if (inputPtr > lastFullOffset) { // need to load more
+                inputEnd = _readMore(data, readBuffer, inputPtr, inputEnd, readBuffer.length);
+                inputPtr = 0;
+                if (inputEnd < 3) { // required to try to read to have at least 3 bytes
+                    break;
+                }
+                lastFullOffset = inputEnd-3;
+            }
+            if (currentOutputTail > safeOutputEnd) { // need to flush
+                _outputTarget.setOutputTail(currentOutputTail);
+                _outputTarget.flushOutputBuffer();
+                currentOutputTail = _outputTarget.getOutputTail(); // Re-read after flush
+            }
+            // First, mash 3 bytes into lsb of 32-bit int
+            int b24 = (readBuffer[inputPtr++]) << 8;
+            b24 |= (readBuffer[inputPtr++]) & 0xFF;
+            b24 = (b24 << 8) | ((readBuffer[inputPtr++]) & 0xFF);
+            bytesDone += 3;
+            currentOutputTail = b64variant.encodeBase64Chunk(b24, _outputBuffer, currentOutputTail);
+            if (--chunksBeforeLF <= 0) {
+                _outputBuffer[currentOutputTail++] = '\\';
+                _outputBuffer[currentOutputTail++] = 'n';
+                chunksBeforeLF = b64variant.getMaxLineLength() >> 2;
+            }
+        }
+
+        // And then we may have 1 or 2 leftover bytes to encode
+        if (inputPtr < inputEnd) { // yes, but do we have room for output?
+            if (currentOutputTail > safeOutputEnd) { // don't really need 6 bytes but...
+                _outputTarget.setOutputTail(currentOutputTail);
+                _outputTarget.flushOutputBuffer();
+                currentOutputTail = _outputTarget.getOutputTail(); // Re-read after flush
+            }
+            int b24 = (readBuffer[inputPtr++]) << 16;
+            int amount = 1;
+            if (inputPtr < inputEnd) {
+                b24 |= ((readBuffer[inputPtr]) & 0xFF) << 8;
+                amount = 2;
+            }
+            bytesDone += amount;
+            currentOutputTail = b64variant.encodeBase64Partial(b24, amount, _outputBuffer, currentOutputTail);
+        }
+        _outputTarget.setOutputTail(currentOutputTail);
+        return bytesDone;
+    }
+
+    /**
+     * Helper method to read more bytes from an {@link InputStream} into a buffer.
+     *
+     * @param in The input stream.
+     * @param readBuffer The buffer to read into.
+     * @param inputPtr Current read pointer in the buffer.
+     * @param inputEnd Current end of valid data in the buffer.
+     * @param maxRead Maximum number of bytes to attempt to read.
+     * @return The new end of valid data in the buffer.
+     * @throws JacksonException if an I/O error occurs.
+     */
+    private int _readMore(InputStream in,
+            byte[] readBuffer, int inputPtr, int inputEnd,
+            int maxRead) throws JacksonException
+    {
+        // anything to shift to front?
+        int i = 0;
+        while (inputPtr < inputEnd) {
+            readBuffer[i++]  = readBuffer[inputPtr++];
+        }
+        inputPtr = 0;
+        inputEnd = i;
+        maxRead = Math.min(maxRead, readBuffer.length);
+
+        do {
+            int length = maxRead - inputEnd;
+            if (length == 0) {
+                break;
+            }
+            int count;
+
+            try {
+                count = in.read(readBuffer, inputEnd, length);
+            } catch (IOException e) {
+                throw _outputTarget.wrapIOException(e);
+            }
+            if (count < 0) {
+                return inputEnd;
+            }
+            inputEnd += count;
+        } while (inputEnd < 3);
+        return inputEnd;
+    }
+}
\ No newline at end of file

```
