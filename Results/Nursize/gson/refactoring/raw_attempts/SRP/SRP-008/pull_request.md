# Refactor SRP-008 (SRP): The JsonWriter class is responsible for writing JSON tokens, managing JSON fo...

**Status:** `applied_unverified`  
**Branch:** `refactor/SRP-008` -> `main`  
**Head commit:** `2f6c73f5bb622d5770715968852e9f1357b89017`  
**LLM finish:** `FinishReason.STOP` (prompt 8950, completion 1682)  

## Detected issue

- **File**: `gson/src/main/java/com/google/gson/stream/JsonWriter.java`
- **Entity**: `JsonWriter` (class)
- **Lines (at detection time)**: L40–L508
- **Severity**: high
- **Confidence**: detected by 4 scan(s)

**Description.** The JsonWriter class is responsible for writing JSON tokens, managing JSON formatting (indentation, newlines, spaces), and handling HTML escaping.

**Reasoning.** This class exhibits a 'God Class' smell. It combines the core responsibility of writing syntactically correct JSON tokens to a character stream with distinct concerns such as: (1) applying formatting styles (indentation, newlines, spaces after separators, managed by `formattedColon`, `formattedComma`, `usesEmptyNewlineAndIndent` and `newline` method), and (2) performing HTML character escaping (`htmlSafe` flag and `string` method's logic). Changes to formatting rules or HTML escaping logic are separate reasons to change from ensuring valid JSON token output.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 2
- **Files created** (1): `gson/src/main/java/com/google/gson/stream/JsonWriterHelper.java`
- **Files modified** (1): `gson/src/main/java/com/google/gson/stream/JsonWriter.java`

**Summary.** Extract JSON formatting and string escaping logic into a helper class to improve SRP

**Rationale.** JsonWriter was handling both structural JSON writing and low-level concerns like string escaping and formatting. By moving these to a dedicated JsonWriterHelper, we separate the concerns of 'how to write JSON' from 'how to format/escape data'.

## Changes overview

_2 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `gson/src/main/java/com/google/gson/stream/JsonWriter.java` (22-line block → 53-line replacement)

**Replaces:**

```java
  private static final String[] REPLACEMENT_CHARS;
  private static final String[] HTML_SAFE_REPLACEMENT_CHARS;

  static {
    REPLACEMENT_CHARS = new String[128];
    for (int i = 0; i <= 0x1f; i++) {
      REPLACEMENT_CHARS[i] = String.format("\\u%04x", i);
    }
    REPLACEMENT_CHARS['"'] = "\\\"";
    REPLACEMENT_CHARS['\\'] = "\\\\";
    REPLACEMENT_CHARS['\t'] = "\\t";
    REPLACEMENT_CHARS['\b'] = "\\b";
    REPLACEMENT_CHARS['\n'] = "\\n";
    REPLACEMENT_CHARS['\r'] = "\\r";
    REPLACEMENT_CHARS['\f'] = "\\f";
    HTML_SAFE_REPLACEMENT_CHARS = REPLACEMENT_CHARS.clone();
    HTML_SAFE_REPLACEMENT_CHARS['<'] = "\\u003c";
    HTML_SAFE_REPLACEMENT_CHARS['>'] = "\\u003e";
    HTML_SAFE_REPLACEMENT_CHARS['&'] = "\\u0026";
    HTML_SAFE_REPLACEMENT_CHARS['='] = "\\u003d";
    HTML_SAFE_REPLACEMENT_CHARS['\''] = "\\u0027";
  }
```

**With:**

```java
>>>>>>> REPLACE

<<<<<<< SEARCH gson/src/main/java/com/google/gson/stream/JsonWriter.java
  private void string(String value) throws IOException {
    String[] replacements = htmlSafe ? HTML_SAFE_REPLACEMENT_CHARS : REPLACEMENT_CHARS;
    out.write('\"');
    int last = 0;
    int length = value.length();
    for (int i = 0; i < length; i++) {
      char c = value.charAt(i);
      String replacement;
      if (c < 128) {
        replacement = replacements[c];
        if (replacement == null) {
          continue;
        }
      } else if (c == '\u2028') {
        replacement = "\\u2028";
      } else if (c == '\u2029') {
        replacement = "\\u2029";
      } else {
        continue;
      }
      if (last < i) {
        out.write(value, last, i - last);
      }
      out.write(replacement);
      last = i + 1;
    }
    if (last < length) {
      out.write(value, last, length - last);
    }
    out.write('\"');
  }

  private void newline() throws IOException {
    if (usesEmptyNewlineAndIndent) {
      return;
    }

    out.write(formattingStyle.getNewline());
    for (int i = 1, size = stackSize; i < size; i++) {
      out.write(formattingStyle.getIndent());
    }
  }
=======
  private void string(String value) throws IOException {
    JsonWriterHelper.writeString(out, value, htmlSafe);
  }

  private void newline() throws IOException {
    JsonWriterHelper.writeNewline(out, formattingStyle, stackSize);
  }
```

### 2. CREATE `gson/src/main/java/com/google/gson/stream/JsonWriterHelper.java` (64 line(s))

```java
package com.google.gson.stream;

import com.google.gson.FormattingStyle;
import java.io.IOException;
import java.io.Writer;

class JsonWriterHelper {
  private static final String[] REPLACEMENT_CHARS;
  private static final String[] HTML_SAFE_REPLACEMENT_CHARS;

  static {
    REPLACEMENT_CHARS = new String[128];
    for (int i = 0; i <= 0x1f; i++) {
      REPLACEMENT_CHARS[i] = String.format("\\u%04x", i);
    }
    REPLACEMENT_CHARS['"'] = "\\\"";
    REPLACEMENT_CHARS['\\'] = "\\\\";
    REPLACEMENT_CHARS['\t'] = "\\t";
    REPLACEMENT_CHARS['\b'] = "\\b";
    REPLACEMENT_CHARS['\n'] = "\\n";
    REPLACEMENT_CHARS['\r'] = "\\r";
    REPLACEMENT_CHARS['\f'] = "\\f";
    HTML_SAFE_REPLACEMENT_CHARS = REPLACEMENT_CHARS.clone();
    HTML_SAFE_REPLACEMENT_CHARS['<'] = "\\u003c";
    HTML_SAFE_REPLACEMENT_CHARS['>'] = "\\u003e";
    HTML_SAFE_REPLACEMENT_CHARS['&'] = "\\u0026";
    HTML_SAFE_REPLACEMENT_CHARS['='] = "\\u003d";
    HTML_SAFE_REPLACEMENT_CHARS['\''] = "\\u0027";
  }

  static void writeString(Writer out, String value, boolean htmlSafe) throws IOException {
    String[] replacements = htmlSafe ? HTML_SAFE_REPLACEMENT_CHARS : REPLACEMENT_CHARS;
    out.write('\"');
    int last = 0;
    int length = value.length();
    for (int i = 0; i < length; i++) {
      char c = value.charAt(i);
      String replacement;
      if (c < 128) {
        replacement = replacements[c];
        if (replacement == null) continue;
      } else if (c == '\u2028') {
        replacement = "\\u2028";
      } else if (c == '\u2029') {
        replacement = "\\u2029";
      } else {
        continue;
      }
      if (last < i) out.write(value, last, i - last);
      out.write(replacement);
      last = i + 1;
    }
    if (last < length) out.write(value, last, length - last);
    out.write('\"');
  }

  static void writeNewline(Writer out, FormattingStyle style, int stackSize) throws IOException {
    if (style.getNewline().isEmpty() && style.getIndent().isEmpty()) return;
    out.write(style.getNewline());
    for (int i = 1; i < stackSize; i++) {
... (4 more line(s) truncated)
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `gson/src/main/java/com/google/gson/stream/JsonWriter.java` | 759 → 787 | 38 → 42 | 3.5 → 3.45 | 96 → 104 | 0 → 0 |
| `gson/src/main/java/com/google/gson/stream/JsonWriterHelper.java` | - → 59 | - → 2 | - → 6.5 | - → 12 | - → 0 |

## Diff

```diff
diff --git a/gson/src/main/java/com/google/gson/stream/JsonWriter.java b/gson/src/main/java/com/google/gson/stream/JsonWriter.java
index f08a698..2bbc53c 100644
--- a/gson/src/main/java/com/google/gson/stream/JsonWriter.java
+++ b/gson/src/main/java/com/google/gson/stream/JsonWriter.java
@@ -175,27 +175,58 @@ public class JsonWriter implements Closeable, Flushable {
    * newline characters. This prevents eval() from failing with a syntax
    * error. http://code.google.com/p/google-gson/issues/detail?id=341
    */
-  private static final String[] REPLACEMENT_CHARS;
-  private static final String[] HTML_SAFE_REPLACEMENT_CHARS;
+>>>>>>> REPLACE
 
-  static {
-    REPLACEMENT_CHARS = new String[128];
-    for (int i = 0; i <= 0x1f; i++) {
-      REPLACEMENT_CHARS[i] = String.format("\\u%04x", i);
+<<<<<<< SEARCH gson/src/main/java/com/google/gson/stream/JsonWriter.java
+  private void string(String value) throws IOException {
+    String[] replacements = htmlSafe ? HTML_SAFE_REPLACEMENT_CHARS : REPLACEMENT_CHARS;
+    out.write('\"');
+    int last = 0;
+    int length = value.length();
+    for (int i = 0; i < length; i++) {
+      char c = value.charAt(i);
+      String replacement;
+      if (c < 128) {
+        replacement = replacements[c];
+        if (replacement == null) {
+          continue;
+        }
+      } else if (c == '\u2028') {
+        replacement = "\\u2028";
+      } else if (c == '\u2029') {
+        replacement = "\\u2029";
+      } else {
+        continue;
+      }
+      if (last < i) {
+        out.write(value, last, i - last);
+      }
+      out.write(replacement);
+      last = i + 1;
+    }
+    if (last < length) {
+      out.write(value, last, length - last);
+    }
+    out.write('\"');
+  }
+
+  private void newline() throws IOException {
+    if (usesEmptyNewlineAndIndent) {
+      return;
+    }
+
+    out.write(formattingStyle.getNewline());
+    for (int i = 1, size = stackSize; i < size; i++) {
+      out.write(formattingStyle.getIndent());
     }
-    REPLACEMENT_CHARS['"'] = "\\\"";
-    REPLACEMENT_CHARS['\\'] = "\\\\";
-    REPLACEMENT_CHARS['\t'] = "\\t";
-    REPLACEMENT_CHARS['\b'] = "\\b";
-    REPLACEMENT_CHARS['\n'] = "\\n";
-    REPLACEMENT_CHARS['\r'] = "\\r";
-    REPLACEMENT_CHARS['\f'] = "\\f";
-    HTML_SAFE_REPLACEMENT_CHARS = REPLACEMENT_CHARS.clone();
-    HTML_SAFE_REPLACEMENT_CHARS['<'] = "\\u003c";
-    HTML_SAFE_REPLACEMENT_CHARS['>'] = "\\u003e";
-    HTML_SAFE_REPLACEMENT_CHARS['&'] = "\\u0026";
-    HTML_SAFE_REPLACEMENT_CHARS['='] = "\\u003d";
-    HTML_SAFE_REPLACEMENT_CHARS['\''] = "\\u0027";
+  }
+=======
+  private void string(String value) throws IOException {
+    JsonWriterHelper.writeString(out, value, htmlSafe);
+  }
+
+  private void newline() throws IOException {
+    JsonWriterHelper.writeNewline(out, formattingStyle, stackSize);
   }
 
   /** The JSON output destination */
diff --git a/gson/src/main/java/com/google/gson/stream/JsonWriterHelper.java b/gson/src/main/java/com/google/gson/stream/JsonWriterHelper.java
new file mode 100644
index 0000000..0000000
--- /dev/null
+++ b/gson/src/main/java/com/google/gson/stream/JsonWriterHelper.java
@@ -0,0 +1,64 @@
+package com.google.gson.stream;
+
+import com.google.gson.FormattingStyle;
+import java.io.IOException;
+import java.io.Writer;
+
+class JsonWriterHelper {
+  private static final String[] REPLACEMENT_CHARS;
+  private static final String[] HTML_SAFE_REPLACEMENT_CHARS;
+
+  static {
+    REPLACEMENT_CHARS = new String[128];
+    for (int i = 0; i <= 0x1f; i++) {
+      REPLACEMENT_CHARS[i] = String.format("\\u%04x", i);
+    }
+    REPLACEMENT_CHARS['"'] = "\\\"";
+    REPLACEMENT_CHARS['\\'] = "\\\\";
+    REPLACEMENT_CHARS['\t'] = "\\t";
+    REPLACEMENT_CHARS['\b'] = "\\b";
+    REPLACEMENT_CHARS['\n'] = "\\n";
+    REPLACEMENT_CHARS['\r'] = "\\r";
+    REPLACEMENT_CHARS['\f'] = "\\f";
+    HTML_SAFE_REPLACEMENT_CHARS = REPLACEMENT_CHARS.clone();
+    HTML_SAFE_REPLACEMENT_CHARS['<'] = "\\u003c";
+    HTML_SAFE_REPLACEMENT_CHARS['>'] = "\\u003e";
+    HTML_SAFE_REPLACEMENT_CHARS['&'] = "\\u0026";
+    HTML_SAFE_REPLACEMENT_CHARS['='] = "\\u003d";
+    HTML_SAFE_REPLACEMENT_CHARS['\''] = "\\u0027";
+  }
+
+  static void writeString(Writer out, String value, boolean htmlSafe) throws IOException {
+    String[] replacements = htmlSafe ? HTML_SAFE_REPLACEMENT_CHARS : REPLACEMENT_CHARS;
+    out.write('\"');
+    int last = 0;
+    int length = value.length();
+    for (int i = 0; i < length; i++) {
+      char c = value.charAt(i);
+      String replacement;
+      if (c < 128) {
+        replacement = replacements[c];
+        if (replacement == null) continue;
+      } else if (c == '\u2028') {
+        replacement = "\\u2028";
+      } else if (c == '\u2029') {
+        replacement = "\\u2029";
+      } else {
+        continue;
+      }
+      if (last < i) out.write(value, last, i - last);
+      out.write(replacement);
+      last = i + 1;
+    }
+    if (last < length) out.write(value, last, length - last);
+    out.write('\"');
+  }
+
+  static void writeNewline(Writer out, FormattingStyle style, int stackSize) throws IOException {
+    if (style.getNewline().isEmpty() && style.getIndent().isEmpty()) return;
+    out.write(style.getNewline());
+    for (int i = 1; i < stackSize; i++) {
+      out.write(style.getIndent());
+    }
+  }
+}
\ No newline at end of file

```
