# Refactor ISP-010 (ISP): The ParserBase class is forced to implement _decodeEscaped from JsonParser bu...

**Status:** `applied_unverified`  
**Branch:** `refactor/ISP-010` -> `main`  
**Head commit:** `5650ed69e32cc1205ea2281f12c8a5b6bcfeaebf`  
**LLM finish:** `FinishReason.STOP` (prompt 11611, completion 1572)  

## Detected issue

- **File**: `src/main/java/tools/jackson/core/base/ParserBase.java`
- **Entity**: `ParserBase._decodeEscaped` (method)
- **Lines (at detection time)**: L1028–L1029
- **Severity**: high
- **Confidence**: detected by 1 scan(s)

**Description.** The ParserBase class is forced to implement _decodeEscaped from JsonParser but explicitly throws UnsupportedOperationException.

**Reasoning.** The 'JsonParser' interface (or an intermediate abstract class in its hierarchy) mandates a method for decoding escaped characters. 'ParserBase', a foundational abstract class, explicitly throws 'UnsupportedOperationException' for '_decodeEscaped()', indicating it cannot universally provide this functionality. This forces subclasses or clients to depend on a method they might not use or cannot implement, violating the Interface Segregation Principle by making the parser interface too broad.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 2
- **Files created** (1): `src/main/java/tools/jackson/core/base/EscapedBase64Parser.java`
- **Files modified** (1): `src/main/java/tools/jackson/core/base/ParserBase.java`

**Summary.** Extract _decodeEscaped into a new interface to resolve ISP violation

**Rationale.** The _decodeEscaped method is only relevant for parsers that support escaped characters in base64. By moving this to a new interface 'EscapedBase64Parser', we remove the need for ParserBase to implement it and throw UnsupportedOperationException, thus adhering to the Interface Segregation Principle.

## Changes overview

_2 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `src/main/java/tools/jackson/core/base/ParserBase.java` (61-line block → 54-line replacement)

**Replaces:**

```java
    /**
     * Method that sub-classes must implement to support escaped sequences
     * in base64-encoded sections.
     * Sub-classes that do not need base64 support can leave this as is
     *
     * @return Character decoded, if any
     *
     * @throws JacksonException If escape decoding fails
     */
    protected char _decodeEscaped() throws JacksonException {
        throw new UnsupportedOperationException();
    }

    protected final int _decodeBase64Escape(Base64Variant b64variant, int ch, int index)
        throws JacksonException
    {
        // Need to handle escaped chars
        if (ch != '\\') {
            _reportInvalidBase64Char(b64variant, ch, index);
        }
        int unescaped = _decodeEscaped();
        // if white space, skip if first triplet; otherwise errors
        if (unescaped <= INT_SPACE) {
            if (index == 0) { // whitespace only allowed to be skipped between triplets
                return -1;
            }
        }
        // otherwise try to find actual triplet value
        int bits = b64variant.decodeBase64Char(unescaped);
        if (bits < 0) {
            if (bits != Base64Variant.BASE64_VALUE_PADDING) {
                _reportInvalidBase64Char(b64variant, unescaped, index);
            }
        }
        return bits;
    }

    protected final int _decodeBase64Escape(Base64Variant b64variant, char ch, int index)
        throws JacksonException
    {
        if (ch != '\\') {
            _reportInvalidBase64Char(b64variant, ch, index);
            return -1; // never gets here
        }
        char unescaped = _decodeEscaped();
        // if white space, skip if first triplet; otherwise errors
        if (unescaped <= INT_SPACE) {
            if (index == 0) { // whitespace only allowed to be skipped between triplets
                return -1;
            }
        }
        // otherwise try to find actual triplet value
        int bits = b64variant.decodeBase64Char(unescaped);
        if (bits < 0) {
            // second check since padding can only be 3rd or 4th byte (index #2 or #3)
            if ((bits != Base64Variant.BASE64_VALUE_PADDING) || (index < 2)) {
                _reportInvalidBase64Char(b64variant, unescaped, index);
            }
        }
        return bits;
... (1 more line(s) truncated)
```

**With:**

```java
    protected final int _decodeBase64Escape(Base64Variant b64variant, int ch, int index)
        throws JacksonException
    {
        // Need to handle escaped chars
        if (ch != '\\') {
            _reportInvalidBase64Char(b64variant, ch, index);
        }
        if (!(this instanceof EscapedBase64Parser)) {
            _reportInvalidBase64Char(b64variant, ch, index, "Escaped characters not supported");
        }
        int unescaped = ((EscapedBase64Parser) this)._decodeEscaped();
        // if white space, skip if first triplet; otherwise errors
        if (unescaped <= INT_SPACE) {
            if (index == 0) { // whitespace only allowed to be skipped between triplets
                return -1;
            }
        }
        // otherwise try to find actual triplet value
        int bits = b64variant.decodeBase64Char(unescaped);
        if (bits < 0) {
            if (bits != Base64Variant.BASE64_VALUE_PADDING) {
                _reportInvalidBase64Char(b64variant, unescaped, index);
            }
        }
        return bits;
    }

    protected final int _decodeBase64Escape(Base64Variant b64variant, char ch, int index)
        throws JacksonException
    {
        if (ch != '\\') {
            _reportInvalidBase64Char(b64variant, ch, index);
            return -1; // never gets here
        }
        if (!(this instanceof EscapedBase64Parser)) {
            _reportInvalidBase64Char(b64variant, ch, index, "Escaped characters not supported");
        }
        char unescaped = ((EscapedBase64Parser) this)._decodeEscaped();
        // if white space, skip if first triplet; otherwise errors
        if (unescaped <= INT_SPACE) {
            if (index == 0) { // whitespace only allowed to be skipped between triplets
                return -1;
            }
        }
        // otherwise try to find actual triplet value
        int bits = b64variant.decodeBase64Char(unescaped);
        if (bits < 0) {
            // second check since padding can only be 3rd or 4th byte (index #2 or #3)
            if ((bits != Base64Variant.BASE64_VALUE_PADDING) || (index < 2)) {
                _reportInvalidBase64Char(b64variant, unescaped, index);
            }
        }
        return bits;
    }
```

### 2. CREATE `src/main/java/tools/jackson/core/base/EscapedBase64Parser.java` (18 line(s))

```java
package tools.jackson.core.base;

import tools.jackson.core.JacksonException;

/**
 * Interface for parsers that support escaped characters in base64-encoded sections.
 */
public interface EscapedBase64Parser {
    /**
     * Method that sub-classes must implement to support escaped sequences
     * in base64-encoded sections.
     *
     * @return Character decoded, if any
     *
     * @throws JacksonException If escape decoding fails
     */
    char _decodeEscaped() throws JacksonException;
}
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/main/java/tools/jackson/core/base/EscapedBase64Parser.java` | - → 16 | - → 0 | - → 3 | - → 3 | - → 0 |
| `src/main/java/tools/jackson/core/base/ParserBase.java` | 1012 → 1006 | 50 → 49 | 5.14 → 5.22 | 208 → 208 | 0 → 0 |

## Diff

```diff
diff --git a/src/main/java/tools/jackson/core/base/ParserBase.java b/src/main/java/tools/jackson/core/base/ParserBase.java
index 23dc332..b485576 100644
--- a/src/main/java/tools/jackson/core/base/ParserBase.java
+++ b/src/main/java/tools/jackson/core/base/ParserBase.java
@@ -1016,19 +1016,6 @@ public abstract class ParserBase extends ParserMinimalBase
     /**********************************************************************
      */
 
-    /**
-     * Method that sub-classes must implement to support escaped sequences
-     * in base64-encoded sections.
-     * Sub-classes that do not need base64 support can leave this as is
-     *
-     * @return Character decoded, if any
-     *
-     * @throws JacksonException If escape decoding fails
-     */
-    protected char _decodeEscaped() throws JacksonException {
-        throw new UnsupportedOperationException();
-    }
-
     protected final int _decodeBase64Escape(Base64Variant b64variant, int ch, int index)
         throws JacksonException
     {
@@ -1036,7 +1023,10 @@ public abstract class ParserBase extends ParserMinimalBase
         if (ch != '\\') {
             _reportInvalidBase64Char(b64variant, ch, index);
         }
-        int unescaped = _decodeEscaped();
+        if (!(this instanceof EscapedBase64Parser)) {
+            _reportInvalidBase64Char(b64variant, ch, index, "Escaped characters not supported");
+        }
+        int unescaped = ((EscapedBase64Parser) this)._decodeEscaped();
         // if white space, skip if first triplet; otherwise errors
         if (unescaped <= INT_SPACE) {
             if (index == 0) { // whitespace only allowed to be skipped between triplets
@@ -1060,7 +1050,10 @@ public abstract class ParserBase extends ParserMinimalBase
             _reportInvalidBase64Char(b64variant, ch, index);
             return -1; // never gets here
         }
-        char unescaped = _decodeEscaped();
+        if (!(this instanceof EscapedBase64Parser)) {
+            _reportInvalidBase64Char(b64variant, ch, index, "Escaped characters not supported");
+        }
+        char unescaped = ((EscapedBase64Parser) this)._decodeEscaped();
         // if white space, skip if first triplet; otherwise errors
         if (unescaped <= INT_SPACE) {
             if (index == 0) { // whitespace only allowed to be skipped between triplets
diff --git a/src/main/java/tools/jackson/core/base/EscapedBase64Parser.java b/src/main/java/tools/jackson/core/base/EscapedBase64Parser.java
new file mode 100644
index 0000000..0000000
--- /dev/null
+++ b/src/main/java/tools/jackson/core/base/EscapedBase64Parser.java
@@ -0,0 +1,18 @@
+package tools.jackson.core.base;
+
+import tools.jackson.core.JacksonException;
+
+/**
+ * Interface for parsers that support escaped characters in base64-encoded sections.
+ */
+public interface EscapedBase64Parser {
+    /**
+     * Method that sub-classes must implement to support escaped sequences
+     * in base64-encoded sections.
+     *
+     * @return Character decoded, if any
+     *
+     * @throws JacksonException If escape decoding fails
+     */
+    char _decodeEscaped() throws JacksonException;
+}
\ No newline at end of file

```
