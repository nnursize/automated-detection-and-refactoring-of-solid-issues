# Refactor LSP-009 (LSP): JsonTreeReader violates JsonReader's contract by using an unreadable internal...

**Status:** `applied_unverified`  
**Branch:** `refactor/LSP-009` -> `main`  
**Head commit:** `86f37caa994d81de9153a7c167b204fd8777676d`  
**LLM finish:** `FinishReason.STOP` (prompt 5070, completion 369)  

## Detected issue

- **File**: `gson/src/main/java/com/google/gson/internal/bind/JsonTreeReader.java`
- **Entity**: `JsonTreeReader` (class)
- **Lines (at detection time)**: L41–L223
- **Severity**: high
- **Confidence**: detected by 7 scan(s)

**Description.** JsonTreeReader violates JsonReader's contract by using an unreadable internal Reader and changing close() behavior.

**Reasoning.** The `JsonTreeReader` extends `JsonReader`. Its constructor initializes the superclass with `UNREADABLE_READER`, an anonymous `Reader` implementation that throws `AssertionError` for `read` and `close` methods. This fundamentally breaks the contract of `JsonReader` (and `Closeable`). A client expecting a `JsonReader` to operate on an underlying `Reader` or to properly close resources will encounter an `AssertionError` when calling `close()` on a `JsonTreeReader` instance, instead of the expected `IOException` or a normal close. This makes `JsonTreeReader` not substitutable for `JsonReader` in scenarios where the underlying stream interaction or resource management is expected.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 2
- **Files modified** (1): `gson/src/main/java/com/google/gson/internal/bind/JsonTreeReader.java`

**Summary.** Remove UNREADABLE_READER and use a dummy Reader to satisfy JsonReader constructor

**Rationale.** The UNREADABLE_READER threw AssertionError on close(), which violates the Closeable contract and LSP. By using a standard empty Reader (or a no-op implementation), we ensure that calling close() on a JsonTreeReader behaves as expected (doing nothing) without crashing the application.

## Changes overview

_2 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `gson/src/main/java/com/google/gson/internal/bind/JsonTreeReader.java` (13-line block → 11-line replacement)

**Replaces:**

```java
  private static final Reader UNREADABLE_READER =
      new Reader() {
        @Override
        public int read(char[] buffer, int offset, int count) {
          throw new AssertionError();
        }

        @Override
        public void close() {
          throw new AssertionError();
        }
      };
  private static final Object SENTINEL_CLOSED = new Object();
```

**With:**

```java
  private static final Reader EMPTY_READER =
      new Reader() {
        @Override
        public int read(char[] buffer, int offset, int count) {
          return -1;
        }

        @Override
        public void close() {}
      };
  private static final Object SENTINEL_CLOSED = new Object();
```

### 2. EDIT `gson/src/main/java/com/google/gson/internal/bind/JsonTreeReader.java` (4-line block → 4-line replacement)

**Replaces:**

```java
  public JsonTreeReader(JsonElement element) {
    super(UNREADABLE_READER);
    push(element);
  }
```

**With:**

```java
  public JsonTreeReader(JsonElement element) {
    super(EMPTY_READER);
    push(element);
  }
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `gson/src/main/java/com/google/gson/internal/bind/JsonTreeReader.java` | 353 → 351 | 29 → 29 | 3.28 → 3.28 | 67 → 67 | 0 → 0 |

## Diff

```diff
diff --git a/gson/src/main/java/com/google/gson/internal/bind/JsonTreeReader.java b/gson/src/main/java/com/google/gson/internal/bind/JsonTreeReader.java
index 4ca4878..e5be36e 100644
--- a/gson/src/main/java/com/google/gson/internal/bind/JsonTreeReader.java
+++ b/gson/src/main/java/com/google/gson/internal/bind/JsonTreeReader.java
@@ -37,17 +37,15 @@ import java.util.Map;
  * @author Jesse Wilson
  */
 public final class JsonTreeReader extends JsonReader {
-  private static final Reader UNREADABLE_READER =
+  private static final Reader EMPTY_READER =
       new Reader() {
         @Override
         public int read(char[] buffer, int offset, int count) {
-          throw new AssertionError();
+          return -1;
         }
 
         @Override
-        public void close() {
-          throw new AssertionError();
-        }
+        public void close() {}
       };
   private static final Object SENTINEL_CLOSED = new Object();
 
@@ -74,7 +72,7 @@ public final class JsonTreeReader extends JsonReader {
   private int[] pathIndices = new int[32];
 
   public JsonTreeReader(JsonElement element) {
-    super(UNREADABLE_READER);
+    super(EMPTY_READER);
     push(element);
   }
 

```
