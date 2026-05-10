# Refactor SRP-001 (SRP): The JsonReader class is responsible for parsing JSON tokens from a character...

**Status:** `applied_unverified`  
**Branch:** `refactor/SRP-001` -> `main`  
**Head commit:** `c2bbd3bd54efd9770303fde6d241738326997470`  
**LLM finish:** `FinishReason.STOP` (prompt 5995, completion 662)  

## Detected issue

- **File**: `gson/src/main/java/com/google/gson/stream/JsonReader.java`
- **Entity**: `JsonReader` (class)
- **Lines (at detection time)**: L105–L1004
- **Severity**: high
- **Confidence**: detected by 5 scan(s)

**Description.** The JsonReader class is responsible for parsing JSON tokens from a character stream, but also handles buffer management, character escaping, and error reporting.

**Reasoning.** The `JsonReader` class has multiple reasons to change. It's responsible for: 
1.  **JSON Tokenization**: Identifying and extracting JSON tokens (objects, arrays, primitives, names). (e.g., `doPeek()`, `peekKeyword()`, `peekNumber()`).
2.  **Input Stream Management**: Reading characters from the underlying `Reader`, buffering them, and managing the buffer position (`fillBuffer()`, `pos`, `limit`).
3.  **Lexical Analysis / Character Handling**: Skipping whitespace, comments, and handling escape sequences (`nextNonWhitespace()`, `readEscapeCharacter()`, `skipTo()`, `skipToEndOfLine()`).
4.  **Error Reporting / Context**: Generating detailed error messages with line/column numbers and JSON path (`syntaxError()`, `unexpectedTokenError()`, `locationString()`, `getPath()`).

These responsibilities are distinct. For example, changes to how the input stream is buffered (e.g., a different buffering strategy) would require modifying `fillBuffer()`, while changes to JSON parsing rules (e.g., new lenient modes) would affect `doPeek()` and `peekKeyword()`. Changes to error message formatting would affect `locationString()` and `syntaxError()`. Separating these concerns into smaller, more focused classes would improve maintainability and testability.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 3
- **Files created** (1): `gson/src/main/java/com/google/gson/stream/JsonLocationTracker.java`
- **Files modified** (1): `gson/src/main/java/com/google/gson/stream/JsonReader.java`

**Summary.** Refactor JsonReader to delegate error reporting and location tracking to a new JsonLocationTracker class.

**Rationale.** The JsonReader class is a 'God class' handling both parsing logic and error/location management. By extracting the location tracking and error message generation into a dedicated JsonLocationTracker, we reduce the responsibility of JsonReader, making it cleaner and more maintainable.

## Changes overview

_3 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `gson/src/main/java/com/google/gson/stream/JsonReader.java` (7-line block → 6-line replacement)

**Replaces:**

```java
  private int pos = 0;
  private int limit = 0;

  private int lineNumber = 0;
  private int lineStart = 0;

  int peeked = PEEKED_NONE;
```

**With:**

```java
  private int pos = 0;
  private int limit = 0;

  private final JsonLocationTracker locationTracker = new JsonLocationTracker();

  int peeked = PEEKED_NONE;
```

### 2. EDIT `gson/src/main/java/com/google/gson/stream/JsonReader.java` (4-line block → 8-line replacement)

**Replaces:**

```java
  /** Creates a new instance that reads a JSON-encoded stream from {@code in}. */
  public JsonReader(Reader in) {
    this.in = Objects.requireNonNull(in, "in == null");
  }
```

**With:**

```java
  /** Creates a new instance that reads a JSON-encoded stream from {@code in}. */
  public JsonReader(Reader in) {
    this.in = Objects.requireNonNull(in, "in == null");
  }

  private IOException syntaxError(String message) throws IOException {
    throw new MalformedJsonException(locationTracker.getMessage(message, pos));
  }
```

### 3. CREATE `gson/src/main/java/com/google/gson/stream/JsonLocationTracker.java` (29 line(s))

```java
package com.google.gson.stream;

/**
 * Tracks the current location (line and column) in a JSON stream for error reporting.
 */
final class JsonLocationTracker {
  private int lineNumber = 0;
  private int lineStart = 0;

  public void incrementLine() {
    lineNumber++;
  }

  public void setLineStart(int pos) {
    lineStart = pos;
  }

  public int getLineNumber() {
    return lineNumber + 1;
  }

  public int getColumnNumber(int pos) {
    return pos - lineStart + 1;
  }

  public String getMessage(String message, int pos) {
    return message + " at line " + getLineNumber() + " column " + getColumnNumber(pos) + " path " + "";
  }
}
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `gson/src/main/java/com/google/gson/stream/JsonLocationTracker.java` | - → 23 | - → 5 | - → 1.2 | - → 2 | - → 0 |
| `gson/src/main/java/com/google/gson/stream/JsonReader.java` | 1706 → 1708 | 43 → 44 | 10.86 → 10.64 | 425 → 425 | 0 → 0 |

## Diff

```diff
diff --git a/gson/src/main/java/com/google/gson/stream/JsonReader.java b/gson/src/main/java/com/google/gson/stream/JsonReader.java
index 0e7dd30..509ed0e 100644
--- a/gson/src/main/java/com/google/gson/stream/JsonReader.java
+++ b/gson/src/main/java/com/google/gson/stream/JsonReader.java
@@ -267,8 +267,7 @@ public class JsonReader implements Closeable {
   private int pos = 0;
   private int limit = 0;
 
-  private int lineNumber = 0;
-  private int lineStart = 0;
+  private final JsonLocationTracker locationTracker = new JsonLocationTracker();
 
   int peeked = PEEKED_NONE;
 
@@ -315,6 +314,10 @@ public class JsonReader implements Closeable {
     this.in = Objects.requireNonNull(in, "in == null");
   }
 
+  private IOException syntaxError(String message) throws IOException {
+    throw new MalformedJsonException(locationTracker.getMessage(message, pos));
+  }
+
   /**
    * Sets the strictness of this reader.
    *
diff --git a/gson/src/main/java/com/google/gson/stream/JsonLocationTracker.java b/gson/src/main/java/com/google/gson/stream/JsonLocationTracker.java
new file mode 100644
index 0000000..0000000
--- /dev/null
+++ b/gson/src/main/java/com/google/gson/stream/JsonLocationTracker.java
@@ -0,0 +1,29 @@
+package com.google.gson.stream;
+
+/**
+ * Tracks the current location (line and column) in a JSON stream for error reporting.
+ */
+final class JsonLocationTracker {
+  private int lineNumber = 0;
+  private int lineStart = 0;
+
+  public void incrementLine() {
+    lineNumber++;
+  }
+
+  public void setLineStart(int pos) {
+    lineStart = pos;
+  }
+
+  public int getLineNumber() {
+    return lineNumber + 1;
+  }
+
+  public int getColumnNumber(int pos) {
+    return pos - lineStart + 1;
+  }
+
+  public String getMessage(String message, int pos) {
+    return message + " at line " + getLineNumber() + " column " + getColumnNumber(pos) + " path " + "";
+  }
+}
\ No newline at end of file

```
