# Refactor SRP-004 (SRP): The class combines input stream management from `Reader`, JSON token traversa...

**Status:** `applied_unverified`  
**Branch:** `refactor/SRP-004` -> `main`  
**Head commit:** `01568689a84bd8fcda551772e84352f0e477029f`  
**LLM finish:** `FinishReason.STOP` (prompt 8744, completion 5433)  

## Detected issue

- **File**: `src/main/java/tools/jackson/core/json/ReaderBasedJsonParser.java`
- **Entity**: `ReaderBasedJsonParser` (class)
- **Lines (at detection time)**: L17–L1500
- **Severity**: high
- **Confidence**: detected by 5 scan(s)

**Description.** The class combines input stream management from `Reader`, JSON token traversal, various JSON value parsing (strings, numbers, booleans, null), JSON name parsing and canonicalization, Base64 decoding, character escaping, whitespace/comment skipping, and error reporting.

**Reasoning.** Similar to its `UTF8StreamJsonParser` counterpart, this class is a 'God class'. Although it uses a `Reader` and thus doesn't handle UTF-8 byte-level decoding, it still bundles many responsibilities: I/O buffering (`_loadMore()`), JSON structure parsing (`nextToken()`), value parsing (`_parseUnsignedNumber()`, `_finishString()`), name canonicalization (`_parseName()`), Base64 decoding (`_decodeBase64()`), character escaping (`_decodeEscaped()`), and comprehensive error reporting (`_reportInvalidToken()`). A change in any of these distinct areas would necessitate modifications to this single class.

## Fix logic

- **Model**: `gemini-2.5-flash` (temperature 0.2)
- **Patch blocks**: 8
- **Files created** (2): `src/main/java/tools/jackson/core/json/Base64CharInput.java`, `src/main/java/tools/jackson/core/json/ReaderBasedBase64StreamDecoder.java`
- **Files modified** (1): `src/main/java/tools/jackson/core/json/ReaderBasedJsonParser.java`

**Summary.** Extract stream-based Base64 decoding logic into a dedicated helper class.

**Rationale.** The `ReaderBasedJsonParser` class was responsible for both JSON parsing and stream-based Base64 decoding, violating the Single Responsibility Principle. This refactoring extracts the stream-based Base64 decoding logic from the `_readBinary` method into a new class, `ReaderBasedBase64StreamDecoder`. This new decoder class interacts with the parser through a `Base64CharInput` interface, which `ReaderBasedJsonParser` now implements. This clearly separates the concern of Base64 data processing from the core JSON parsing and input buffer management, making `ReaderBasedJsonParser` more focused on its primary responsibility.

## Changes overview

_8 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `src/main/java/tools/jackson/core/json/ReaderBasedJsonParser.java` (13-line block → 16-line replacement)

**Replaces:**

```java
package tools.jackson.core.json;

import java.io.*;

import tools.jackson.core.*;
import tools.jackson.core.exc.JacksonIOException;
import tools.jackson.core.exc.StreamReadException;
import tools.jackson.core.io.CharTypes;
import tools.jackson.core.io.IOContext;
import tools.jackson.core.sym.CharsToNameCanonicalizer;
import tools.jackson.core.util.*;

import static tools.jackson.core.JsonTokenId.*;
```

**With:**

```java
package tools.jackson.core.json;

import java.io.*;

import tools.jackson.core.*;
import tools.jackson.core.exc.JacksonIOException;
import tools.jackson.core.exc.StreamReadException;
import tools.jackson.core.io.CharTypes;
import tools.jackson.core.io.IOContext;
import tools.jackson.core.sym.CharsToNameCanonicalizer;
import tools.jackson.core.util.*;

import static tools.jackson.core.JsonTokenId.*;

import tools.jackson.core.json.Base64CharInput;
import tools.jackson.core.json.ReaderBasedBase64StreamDecoder;
```

### 2. EDIT `src/main/java/tools/jackson/core/json/ReaderBasedJsonParser.java` (9-line block → 15-line replacement)

**Replaces:**

```java
public class ReaderBasedJsonParser
    extends JsonParserBase
{
    private final static int FEAT_MASK_TRAILING_COMMA = JsonReadFeature.ALLOW_TRAILING_COMMA.getMask();
    private final static int FEAT_MASK_ALLOW_MISSING = JsonReadFeature.ALLOW_MISSING_VALUES.getMask();

    // Latin1 encoding is not supported, but we do use 8-bit subset for
    // pre-processing task, to simplify first pass, keep it fast.
    protected final static int[] _icLatin1 = CharTypes.getInputCodeLatin1();
```

**With:**

```java
public class ReaderBasedJsonParser
    extends JsonParserBase
    implements Base64CharInput
{
    private final static int FEAT_MASK_TRAILING_COMMA = JsonReadFeature.ALLOW_TRAILING_COMMA.getMask();
    private final static int FEAT_MASK_ALLOW_MISSING = JsonReadFeature.ALLOW_MISSING_VALUES.getMask();

    // Latin1 encoding is not supported, but we do use 8-bit subset for
    // pre-processing task, to simplify first pass, keep it fast.
    protected final static int[] _icLatin1 = CharTypes.getInputCodeLatin1();

    /**
     * Helper object for stream-based Base64 decoding.
     */
    protected ReaderBasedBase64StreamDecoder _base64StreamDecoder;
```

### 3. EDIT `src/main/java/tools/jackson/core/json/ReaderBasedJsonParser.java` (14-line block → 15-line replacement)

**Replaces:**

```java
            boolean bufferRecyclable)
    {
        super(readCtxt, ctxt, stdFeatures, formatFeatures);
        _reader = r;
        _inputBuffer = inputBuffer;
        _inputPtr = start;
        _inputEnd = end;
        _currInputRowStart = start;
        // If we have offset, need to omit that from byte offset, so:
        _currInputProcessed = -start;
        _symbols = st;
        _hashSeed = st.hashSeed();
        _bufferRecyclable = bufferRecyclable;
    }
```

**With:**

```java
            boolean bufferRecyclable)
    {
        super(readCtxt, ctxt, stdFeatures, formatFeatures);
        _reader = r;
        _inputBuffer = inputBuffer;
        _inputPtr = start;
        _inputEnd = end;
        _currInputRowStart = start;
        // If we have offset, need to omit that from byte offset, so:
        _currInputProcessed = -start;
        _symbols = st;
        _hashSeed = st.hashSeed();
        _bufferRecyclable = bufferRecyclable;
        _base64StreamDecoder = new ReaderBasedBase64StreamDecoder(this);
    }
```

### 4. EDIT `src/main/java/tools/jackson/core/json/ReaderBasedJsonParser.java` (12-line block → 13-line replacement)

**Replaces:**

```java
            int stdFeatures, int formatFeatures, Reader r,
            CharsToNameCanonicalizer st)
    {
        super(readCtxt, ctxt, stdFeatures, formatFeatures);
        _reader = r;
        _inputBuffer = ctxt.allocTokenBuffer();
        _inputPtr = 0;
        _inputEnd = 0;
        _symbols = st;
        _hashSeed = st.hashSeed();
        _bufferRecyclable = true;
    }
```

**With:**

```java
            int stdFeatures, int formatFeatures, Reader r,
            CharsToNameCanonicalizer st)
    {
        super(readCtxt, ctxt, stdFeatures, formatFeatures);
        _reader = r;
        _inputBuffer = ctxt.allocTokenBuffer();
        _inputPtr = 0;
        _inputEnd = 0;
        _symbols = st;
        _hashSeed = st.hashSeed();
        _bufferRecyclable = true;
        _base64StreamDecoder = new ReaderBasedBase64StreamDecoder(this);
    }
```

### 5. EDIT `src/main/java/tools/jackson/core/json/ReaderBasedJsonParser.java` (143-line block → 7-line replacement)

**Replaces:**

```java
    protected int _readBinary(Base64Variant b64variant, OutputStream out, byte[] buffer) throws JacksonException
    {
        int outputPtr = 0;
        final int outputEnd = buffer.length - 3;
        int outputCount = 0;

        while (true) {
            // first, we'll skip preceding white space, if any
            char ch;
            do {
                if (_inputPtr >= _inputEnd) {
                    _loadMoreGuaranteed();
                }
                ch = _inputBuffer[_inputPtr++];
            } while (ch <= INT_SPACE);
            int bits = b64variant.decodeBase64Char(ch);
            if (bits < 0) { // reached the end, fair and square?
                if (ch == '"') {
                    break;
                }
                bits = _decodeBase64Escape(b64variant, ch, 0);
                if (bits < 0) { // white space to skip
                    continue;
                }
            }

            // enough room? If not, flush
            if (outputPtr > outputEnd) {
                outputCount += outputPtr;
                try {
                    out.write(buffer, 0, outputPtr);
                } catch (IOException e) {
                    throw _wrapIOFailure(e);
                }
                outputPtr = 0;
            }

            int decodedData = bits;

            // then second base64 char; can't get padding yet, nor ws

            if (_inputPtr >= _inputEnd) {
                _loadMoreGuaranteed();
            }
            ch = _inputBuffer[_inputPtr++];
            bits = b64variant.decodeBase64Char(ch);
            if (bits < 0) {
                bits = _decodeBase64Escape(b64variant, ch, 1);
            }
            decodedData = (decodedData << 6) | bits;

            // third base64 char; can be padding, but not ws
            if (_inputPtr >= _inputEnd) {
                _loadMoreGuaranteed();
            }
            ch = _inputBuffer[_inputPtr++];
            bits = b64variant.decodeBase64Char(ch);

            // First branch: can get padding (-> 1 byte)
            if (bits < 0) {
... (83 more line(s) truncated)
```

**With:**

```java
    @Override
    protected int _readBinary(Base64Variant b64variant, OutputStream out, byte[] buffer) throws JacksonException
    {
        // Delegate to the new helper class
        _tokenIncomplete = false; // The decoder will handle the completion
        return _base64StreamDecoder.decode(b64variant, out, buffer);
    }
```

### 6. EDIT `src/main/java/tools/jackson/core/json/ReaderBasedJsonParser.java` (5-line block → 54-line replacement)

**Replaces:**

```java
    /*
    /**********************************************************************
    /* Public API, traversal
    /**********************************************************************
     */
```

**With:**

```java
    /*
    /**********************************************************************
    /* Public API, traversal
    /**********************************************************************
     */

    /*
    /**********************************************************************
    /* Base64CharInput implementation
    /**********************************************************************
     */

    @Override
    public char getNextChar() throws JacksonException {
        if (_inputPtr >= _inputEnd) {
            _loadMoreGuaranteed();
        }
        return _inputBuffer[_inputPtr++];
    }

    @Override
    public void pushBackChar() {
        --_inputPtr;
    }

    @Override
    public void reportInvalidBase64Char(Base64Variant b64variant, int ch, int bpt, String msg) throws JacksonException {
        _reportInvalidBase64Char(b64variant, ch, bpt, msg);
    }

    @Override
    public int decodeBase64Escape(Base64Variant b64variant, char ch, int bpt) throws JacksonException {
        return _decodeBase64Escape(b64variant, ch, bpt);
    }

    @Override
    public void handleBase64MissingPadding(Base64Variant b64variant) throws JacksonException {
        _handleBase64MissingPadding(b64variant);
    }

    @Override
    public JacksonException wrapIOFailure(IOException e) {
        return _wrapIOFailure(e);
    }

    @Override
    public IOContext getIOContext() {
        return _ioContext;
    }

    @Override
    public int getSpaceChar() {
        return INT_SPACE;
    }
```

### 7. CREATE `src/main/java/tools/jackson/core/json/Base64CharInput.java` (55 line(s))

```java
package tools.jackson.core.json;

import java.io.IOException;

import tools.jackson.core.Base64Variant;
import tools.jackson.core.JacksonException;
import tools.jackson.core.io.IOContext;

/**
 * Interface for providing character input and error reporting for stream-based Base64 decoding.
 * This allows decoupling the Base64 decoding logic from the specific JsonParser implementation.
 */
public interface Base64CharInput {
    /**
     * Get the next character from the input stream.
     * Implementations should handle buffer loading and EOF.
     */
    char getNextChar() throws JacksonException;

    /**
     * Push back the last character read, effectively decrementing the input pointer.
     * This is used when a character is read but not consumed by the Base64 logic (e.g., closing quote).
     */
    void pushBackChar();

    /**
     * Report an invalid Base64 character.
     */
    void reportInvalidBase64Char(Base64Variant b64variant, int ch, int bpt, String msg) throws JacksonException;

    /**
     * Decode an escaped character within a Base64 string.
     */
    int decodeBase64Escape(Base64Variant b64variant, char ch, int bpt) throws JacksonException;

    /**
     * Handle cases where Base64 padding is missing.
     */
    void handleBase64MissingPadding(Base64Variant b64variant) throws JacksonException;

    /**
     * Wrap an IOException into a JacksonException.
     */
    JacksonException wrapIOFailure(IOException e);

    /**
     * Get the IOContext for buffer allocation/release.
     */
    IOContext getIOContext();

    /**
     * Constant for space character, used for skipping whitespace.
     */
    int getSpaceChar();
}
```

### 8. CREATE `src/main/java/tools/jackson/core/json/ReaderBasedBase64StreamDecoder.java` (148 line(s))

```java
package tools.jackson.core.json;

import java.io.IOException;
import java.io.OutputStream;

import tools.jackson.core.Base64Variant;
import tools.jackson.core.JacksonException;
import tools.jackson.core.io.IOContext;

/**
 * Helper class for {@link ReaderBasedJsonParser} to handle stream-based
 * Base64 decoding.
 */
public class ReaderBasedBase64StreamDecoder {
    private final Base64CharInput _input;

    public ReaderBasedBase64StreamDecoder(Base64CharInput input) {
        _input = input;
    }

    public int decode(Base64Variant b64variant, OutputStream out, byte[] buffer) throws JacksonException {
        int outputPtr = 0;
        final int outputEnd = buffer.length - 3;
        int outputCount = 0;
        final int INT_SPACE = _input.getSpaceChar();

        while (true) {
            // first, we'll skip preceding white space, if any
            char ch;
            do {
                ch = _input.getNextChar();
            } while (ch <= INT_SPACE);

            int bits = b64variant.decodeBase64Char(ch);
            if (bits < 0) { // reached the end, fair and square?
                if (ch == '"') {
                    break;
                }
                bits = _input.decodeBase64Escape(b64variant, ch, 0);
                if (bits < 0) { // white space to skip
                    continue;
                }
            }

            // enough room? If not, flush
            if (outputPtr > outputEnd) {
                outputCount += outputPtr;
                try {
                    out.write(buffer, 0, outputPtr);
                } catch (IOException e) {
                    throw _input.wrapIOFailure(e);
                }
                outputPtr = 0;
            }

            int decodedData = bits;

            // then second base64 char; can't get padding yet, nor ws
            ch = _input.getNextChar();
            bits = b64variant.decodeBase64Char(ch);
... (88 more line(s) truncated)
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/main/java/tools/jackson/core/json/Base64CharInput.java` | - → 45 | - → 0 | - → 7 | - → 7 | - → 0 |
| `src/main/java/tools/jackson/core/json/ReaderBasedBase64StreamDecoder.java` | - → 124 | - → 1 | - → 27 | - → 27 | - → 0 |
| `src/main/java/tools/jackson/core/json/ReaderBasedJsonParser.java` | 2673 → 2604 | 77 → 85 | 11.21 → 9.92 | 787 → 759 | 0 → 0 |

## Diff

```diff
diff --git a/src/main/java/tools/jackson/core/json/ReaderBasedJsonParser.java b/src/main/java/tools/jackson/core/json/ReaderBasedJsonParser.java
index cfb5c68..9b40c94 100644
--- a/src/main/java/tools/jackson/core/json/ReaderBasedJsonParser.java
+++ b/src/main/java/tools/jackson/core/json/ReaderBasedJsonParser.java
@@ -12,6 +12,9 @@ import tools.jackson.core.util.*;
 
 import static tools.jackson.core.JsonTokenId.*;
 
+import tools.jackson.core.json.Base64CharInput;
+import tools.jackson.core.json.ReaderBasedBase64StreamDecoder;
+
 /**
  * This is a concrete implementation of {@link JsonParser}, which is
  * based on a {@link java.io.Reader} to handle low-level character
@@ -19,6 +22,7 @@ import static tools.jackson.core.JsonTokenId.*;
  */
 public class ReaderBasedJsonParser
     extends JsonParserBase
+    implements Base64CharInput
 {
     private final static int FEAT_MASK_TRAILING_COMMA = JsonReadFeature.ALLOW_TRAILING_COMMA.getMask();
     private final static int FEAT_MASK_ALLOW_MISSING = JsonReadFeature.ALLOW_MISSING_VALUES.getMask();
@@ -27,6 +31,11 @@ public class ReaderBasedJsonParser
     // pre-processing task, to simplify first pass, keep it fast.
     protected final static int[] _icLatin1 = CharTypes.getInputCodeLatin1();
 
+    /**
+     * Helper object for stream-based Base64 decoding.
+     */
+    protected ReaderBasedBase64StreamDecoder _base64StreamDecoder;
+
     /*
     /**********************************************************************
     /* Input configuration
@@ -130,6 +139,7 @@ public class ReaderBasedJsonParser
         _symbols = st;
         _hashSeed = st.hashSeed();
         _bufferRecyclable = bufferRecyclable;
+        _base64StreamDecoder = new ReaderBasedBase64StreamDecoder(this);
     }
 
     /**
@@ -155,6 +165,7 @@ public class ReaderBasedJsonParser
         _symbols = st;
         _hashSeed = st.hashSeed();
         _bufferRecyclable = true;
+        _base64StreamDecoder = new ReaderBasedBase64StreamDecoder(this);
     }
 
     /*
@@ -511,155 +522,68 @@ public class ReaderBasedJsonParser
         }
     }
 
+    @Override
     protected int _readBinary(Base64Variant b64variant, OutputStream out, byte[] buffer) throws JacksonException
     {
-        int outputPtr = 0;
-        final int outputEnd = buffer.length - 3;
-        int outputCount = 0;
+        // Delegate to the new helper class
+        _tokenIncomplete = false; // The decoder will handle the completion
+        return _base64StreamDecoder.decode(b64variant, out, buffer);
+    }
 
-        while (true) {
-            // first, we'll skip preceding white space, if any
-            char ch;
-            do {
-                if (_inputPtr >= _inputEnd) {
-                    _loadMoreGuaranteed();
-                }
-                ch = _inputBuffer[_inputPtr++];
-            } while (ch <= INT_SPACE);
-            int bits = b64variant.decodeBase64Char(ch);
-            if (bits < 0) { // reached the end, fair and square?
-                if (ch == '"') {
-                    break;
-                }
-                bits = _decodeBase64Escape(b64variant, ch, 0);
-                if (bits < 0) { // white space to skip
-                    continue;
-                }
-            }
+    /*
+    /**********************************************************************
+    /* Public API, traversal
+    /**********************************************************************
+     */
 
-            // enough room? If not, flush
-            if (outputPtr > outputEnd) {
-                outputCount += outputPtr;
-                try {
-                    out.write(buffer, 0, outputPtr);
-                } catch (IOException e) {
-                    throw _wrapIOFailure(e);
-                }
-                outputPtr = 0;
-            }
+    /*
+    /**********************************************************************
+    /* Base64CharInput implementation
+    /**********************************************************************
+     */
 
-            int decodedData = bits;
+    @Override
+    public char getNextChar() throws JacksonException {
+        if (_inputPtr >= _inputEnd) {
+            _loadMoreGuaranteed();
+        }
+        return _inputBuffer[_inputPtr++];
+    }
 
-            // then second base64 char; can't get padding yet, nor ws
+    @Override
+    public void pushBackChar() {
+        --_inputPtr;
+    }
 
-            if (_inputPtr >= _inputEnd) {
-                _loadMoreGuaranteed();
-            }
-            ch = _inputBuffer[_inputPtr++];
-            bits = b64variant.decodeBase64Char(ch);
-            if (bits < 0) {
-                bits = _decodeBase64Escape(b64variant, ch, 1);
-            }
-            decodedData = (decodedData << 6) | bits;
+    @Override
+    public void reportInvalidBase64Char(Base64Variant b64variant, int ch, int bpt, String msg) throws JacksonException {
+        _reportInvalidBase64Char(b64variant, ch, bpt, msg);
+    }
 
-            // third base64 char; can be padding, but not ws
-            if (_inputPtr >= _inputEnd) {
-                _loadMoreGuaranteed();
-            }
-            ch = _inputBuffer[_inputPtr++];
-            bits = b64variant.decodeBase64Char(ch);
+    @Override
+    public int decodeBase64Escape(Base64Variant b64variant, char ch, int bpt) throws JacksonException {
+        return _decodeBase64Escape(b64variant, ch, bpt);
+    }
 
-            // First branch: can get padding (-> 1 byte)
-            if (bits < 0) {
-                if (bits != Base64Variant.BASE64_VALUE_PADDING) {
-                    // could also just be missing padding
-                    if (ch == '"') {
-                        decodedData >>= 4;
-                        buffer[outputPtr++] = (byte) decodedData;
-                        if (b64variant.requiresPaddingOnRead()) {
-                            --_inputPtr; // to keep parser state bit more consistent
-                            _handleBase64MissingPadding(b64variant);
-                        }
-                        break;
-                    }
-                    bits = _decodeBase64Escape(b64variant, ch, 2);
-                }
-                if (bits == Base64Variant.BASE64_VALUE_PADDING) {
-                    // Ok, must get padding
-                    if (_inputPtr >= _inputEnd) {
-                        _loadMoreGuaranteed();
-                    }
-                    ch = _inputBuffer[_inputPtr++];
-                    if (!b64variant.usesPaddingChar(ch)) {
-                        if (_decodeBase64Escape(b64variant, ch, 3) != Base64Variant.BASE64_VALUE_PADDING) {
-                            _reportInvalidBase64Char(b64variant, ch, 3, "expected padding character '"+b64variant.getPaddingChar()+"'");
-                        }
-                    }
-                    // Got 12 bits, only need 8, need to shift
-                    decodedData >>= 4;
-                    buffer[outputPtr++] = (byte) decodedData;
-                    continue;
-                }
-            }
-            // Nope, 2 or 3 bytes
-            decodedData = (decodedData << 6) | bits;
-            // fourth and last base64 char; can be padding, but not ws
-            if (_inputPtr >= _inputEnd) {
-                _loadMoreGuaranteed();
-            }
-            ch = _inputBuffer[_inputPtr++];
-            bits = b64variant.decodeBase64Char(ch);
-            if (bits < 0) {
-                if (bits != Base64Variant.BASE64_VALUE_PADDING) {
-                    // as per could also just be missing padding
-                    if (ch == '"') {
-                        decodedData >>= 2;
-                        buffer[outputPtr++] = (byte) (decodedData >> 8);
-                        buffer[outputPtr++] = (byte) decodedData;
-                        if (b64variant.requiresPaddingOnRead()) {
-                            --_inputPtr; // to keep parser state bit more consistent
-                            _handleBase64MissingPadding(b64variant);
-                        }
-                        break;
-                    }
-                    bits = _decodeBase64Escape(b64variant, ch, 3);
-                }
-                if (bits == Base64Variant.BASE64_VALUE_PADDING) {
-                    /* With padding we only get 2 bytes; but we have
-                     * to shift it a bit so it is identical to triplet
-                     * case with partial output.
-                     * 3 chars gives 3x6 == 18 bits, of which 2 are
-                     * dummies, need to discard:
-                     */
-                    decodedData >>= 2;
-                    buffer[outputPtr++] = (byte) (decodedData >> 8);
-                    buffer[outputPtr++] = (byte) decodedData;
-                    continue;
-                }
-            }
-            // otherwise, our triplet is now complete
-            decodedData = (decodedData << 6) | bits;
-            buffer[outputPtr++] = (byte) (decodedData >> 16);
-            buffer[outputPtr++] = (byte) (decodedData >> 8);
-            buffer[outputPtr++] = (byte) decodedData;
-        }
-        _tokenIncomplete = false;
-        if (outputPtr > 0) {
-            outputCount += outputPtr;
-            try {
-                out.write(buffer, 0, outputPtr);
-            } catch (IOException e) {
-                throw _wrapIOFailure(e);
-            }
-        }
-        return outputCount;
+    @Override
+    public void handleBase64MissingPadding(Base64Variant b64variant) throws JacksonException {
+        _handleBase64MissingPadding(b64variant);
     }
 
-    /*
-    /**********************************************************************
-    /* Public API, traversal
-    /**********************************************************************
-     */
+    @Override
+    public JacksonException wrapIOFailure(IOException e) {
+        return _wrapIOFailure(e);
+    }
+
+    @Override
+    public IOContext getIOContext() {
+        return _ioContext;
+    }
+
+    @Override
+    public int getSpaceChar() {
+        return INT_SPACE;
+    }
 
     /**
      * @return Next token from the stream, if any found, or null
diff --git a/src/main/java/tools/jackson/core/json/Base64CharInput.java b/src/main/java/tools/jackson/core/json/Base64CharInput.java
new file mode 100644
index 0000000..0000000
--- /dev/null
+++ b/src/main/java/tools/jackson/core/json/Base64CharInput.java
@@ -0,0 +1,55 @@
+package tools.jackson.core.json;
+
+import java.io.IOException;
+
+import tools.jackson.core.Base64Variant;
+import tools.jackson.core.JacksonException;
+import tools.jackson.core.io.IOContext;
+
+/**
+ * Interface for providing character input and error reporting for stream-based Base64 decoding.
+ * This allows decoupling the Base64 decoding logic from the specific JsonParser implementation.
+ */
+public interface Base64CharInput {
+    /**
+     * Get the next character from the input stream.
+     * Implementations should handle buffer loading and EOF.
+     */
+    char getNextChar() throws JacksonException;
+
+    /**
+     * Push back the last character read, effectively decrementing the input pointer.
+     * This is used when a character is read but not consumed by the Base64 logic (e.g., closing quote).
+     */
+    void pushBackChar();
+
+    /**
+     * Report an invalid Base64 character.
+     */
+    void reportInvalidBase64Char(Base64Variant b64variant, int ch, int bpt, String msg) throws JacksonException;
+
+    /**
+     * Decode an escaped character within a Base64 string.
+     */
+    int decodeBase64Escape(Base64Variant b64variant, char ch, int bpt) throws JacksonException;
+
+    /**
+     * Handle cases where Base64 padding is missing.
+     */
+    void handleBase64MissingPadding(Base64Variant b64variant) throws JacksonException;
+
+    /**
+     * Wrap an IOException into a JacksonException.
+     */
+    JacksonException wrapIOFailure(IOException e);
+
+    /**
+     * Get the IOContext for buffer allocation/release.
+     */
+    IOContext getIOContext();
+
+    /**
+     * Constant for space character, used for skipping whitespace.
+     */
+    int getSpaceChar();
+}
\ No newline at end of file
diff --git a/src/main/java/tools/jackson/core/json/ReaderBasedBase64StreamDecoder.java b/src/main/java/tools/jackson/core/json/ReaderBasedBase64StreamDecoder.java
new file mode 100644
index 0000000..0000000
--- /dev/null
+++ b/src/main/java/tools/jackson/core/json/ReaderBasedBase64StreamDecoder.java
@@ -0,0 +1,148 @@
+package tools.jackson.core.json;
+
+import java.io.IOException;
+import java.io.OutputStream;
+
+import tools.jackson.core.Base64Variant;
+import tools.jackson.core.JacksonException;
+import tools.jackson.core.io.IOContext;
+
+/**
+ * Helper class for {@link ReaderBasedJsonParser} to handle stream-based
+ * Base64 decoding.
+ */
+public class ReaderBasedBase64StreamDecoder {
+    private final Base64CharInput _input;
+
+    public ReaderBasedBase64StreamDecoder(Base64CharInput input) {
+        _input = input;
+    }
+
+    public int decode(Base64Variant b64variant, OutputStream out, byte[] buffer) throws JacksonException {
+        int outputPtr = 0;
+        final int outputEnd = buffer.length - 3;
+        int outputCount = 0;
+        final int INT_SPACE = _input.getSpaceChar();
+
+        while (true) {
+            // first, we'll skip preceding white space, if any
+            char ch;
+            do {
+                ch = _input.getNextChar();
+            } while (ch <= INT_SPACE);
+
+            int bits = b64variant.decodeBase64Char(ch);
+            if (bits < 0) { // reached the end, fair and square?
+                if (ch == '"') {
+                    break;
+                }
+                bits = _input.decodeBase64Escape(b64variant, ch, 0);
+                if (bits < 0) { // white space to skip
+                    continue;
+                }
+            }
+
+            // enough room? If not, flush
+            if (outputPtr > outputEnd) {
+                outputCount += outputPtr;
+                try {
+                    out.write(buffer, 0, outputPtr);
+                } catch (IOException e) {
+                    throw _input.wrapIOFailure(e);
+                }
+                outputPtr = 0;
+            }
+
+            int decodedData = bits;
+
+            // then second base64 char; can't get padding yet, nor ws
+            ch = _input.getNextChar();
+            bits = b64variant.decodeBase64Char(ch);
+            if (bits < 0) {
+                bits = _input.decodeBase64Escape(b64variant, ch, 1);
+            }
+            decodedData = (decodedData << 6) | bits;
+
+            // third base64 char; can be padding, but not ws
+            ch = _input.getNextChar();
+            bits = b64variant.decodeBase64Char(ch);
+
+            // First branch: can get padding (-> 1 byte)
+            if (bits < 0) {
+                if (bits != Base64Variant.BASE64_VALUE_PADDING) {
+                    // could also just be missing padding
+                    if (ch == '"') {
+                        decodedData >>= 4;
+                        buffer[outputPtr++] = (byte) decodedData;
+                        if (b64variant.requiresPaddingOnRead()) {
+                            _input.pushBackChar();
+                            _input.handleBase64MissingPadding(b64variant);
+                        }
+                        break;
+                    }
+                    bits = _input.decodeBase64Escape(b64variant, ch, 2);
+                }
+                if (bits == Base64Variant.BASE64_VALUE_PADDING) {
+                    // Ok, must get padding
+                    ch = _input.getNextChar();
+                    if (!b64variant.usesPaddingChar(ch)) {
+                        if (_input.decodeBase64Escape(b64variant, ch, 3) != Base64Variant.BASE64_VALUE_PADDING) {
+                            _input.reportInvalidBase64Char(b64variant, ch, 3, "expected padding character '"+b64variant.getPaddingChar()+"'");
+                        }
+                    }
+                    // Got 12 bits, only need 8, need to shift
+                    decodedData >>= 4;
+                    buffer[outputPtr++] = (byte) decodedData;
+                    continue;
+                }
+            }
+            // Nope, 2 or 3 bytes
+            decodedData = (decodedData << 6) | bits;
+            // fourth and last base64 char; can be padding, but not ws
+            ch = _input.getNextChar();
+            bits = b64variant.decodeBase64Char(ch);
+            if (bits < 0) {
+                if (bits != Base64Variant.BASE64_VALUE_PADDING) {
+                    // as per could also just be missing padding
+                    if (ch == '"') {
+                        decodedData >>= 2;
+                        buffer[outputPtr++] = (byte) (decodedData >> 8);
+                        buffer[outputPtr++] = (byte) decodedData;
+                        if (b64variant.requiresPaddingOnRead()) {
+                            _input.pushBackChar();
+                            _input.handleBase64MissingPadding(b64variant);
+                        }
+                        break;
+                    }
+                    bits = _input.decodeBase64Escape(b64variant, ch, 3);
+                }
+                if (bits == Base64Variant.BASE64_VALUE_PADDING) {
+                    /* With padding we only get 2 bytes; but we have
+                     * to shift it a bit so it is identical to triplet
+                     * case with partial output.
+                     * 3 chars gives 3x6 == 18 bits, of which 2 are
+                     * dummies, need to discard:
+                     */
+                    decodedData >>= 2;
+                    buffer[outputPtr++] = (byte) (decodedData >> 8);
+                    buffer[outputPtr++] = (byte) decodedData;
+                    continue;
+                }
+            }
+            // otherwise, our triplet is now complete
+            decodedData = (decodedData << 6) | bits;
+            buffer[outputPtr++] = (byte) (decodedData >> 16);
+            buffer[outputPtr++] = (byte) (decodedData >> 8);
+            buffer[outputPtr++] = (byte) decodedData;
+        }
+        if (outputPtr > 0) {
+            outputCount += outputPtr;
+            try {
+                out.write(buffer, 0, outputPtr);
+            } catch (IOException e) {
+                throw _input.wrapIOFailure(e);
+            }
+        }
+        return outputCount;
+    }
+}
\ No newline at end of file

```
