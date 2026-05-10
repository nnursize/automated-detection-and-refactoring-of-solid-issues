# Refactor ISP-001 (ISP): TypeAdapter for Class throws UnsupportedOperationException for both read and...

**Status:** `applied_unverified`  
**Branch:** `refactor/ISP-001` -> `main`  
**Head commit:** `9bf7aae60ed62cb559252a1e0bb2b0b2c9dc554d`  
**LLM finish:** `FinishReason.STOP` (prompt 9698, completion 523)  

## Detected issue

- **File**: `gson/src/main/java/com/google/gson/internal/bind/TypeAdapters.java`
- **Entity**: `TypeAdapters.CLASS` (class)
- **Lines (at detection time)**: L33–L47
- **Severity**: medium
- **Confidence**: detected by 3 scan(s)

**Description.** TypeAdapter for Class throws UnsupportedOperationException for both read and write methods.

**Reasoning.** The `TypeAdapter` interface forces implementers to provide both `read` and `write` methods. For `java.lang.Class`, Gson explicitly does not support default serialization or deserialization, leading to `UnsupportedOperationException` for both methods. This indicates that the `TypeAdapter` interface is not segregated enough for types that might only be serializable, only deserializable, or neither.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `gson/src/main/java/com/google/gson/internal/bind/TypeAdapters.java`

**Summary.** Replace UnsupportedTypeAdapter with a more descriptive error-throwing adapter

**Rationale.** The TypeAdapter interface is a contract that requires both read and write methods. While the current implementation throws UnsupportedOperationException, it is a standard practice in Gson to use a dedicated adapter that provides a clear, actionable error message when a type is explicitly unsupported, rather than relying on a generic internal class that might be misinterpreted as a partial implementation.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `gson/src/main/java/com/google/gson/internal/bind/TypeAdapters.java` (25-line block → 19-line replacement)

**Replaces:**

```java
  private static class UnsupportedTypeAdapter<T> extends TypeAdapter<T> {
    private final String message;

    UnsupportedTypeAdapter(String message) {
      this.message = message;
    }

    @Override
    public void write(JsonWriter out, T value) throws IOException {
      throw new UnsupportedOperationException(message);
    }

    @Override
    public T read(JsonReader in) throws IOException {
      throw new UnsupportedOperationException(message);
    }
  }

  @SuppressWarnings("rawtypes")
  public static final TypeAdapter<Class> CLASS =
      new UnsupportedTypeAdapter<Class>(
              "Attempted to serialize/deserialize java.lang.Class. Forgot to register a type adapter?"
                  + "\nSee "
                  + TroubleshootingGuide.createUrl("java-lang-class-unsupported"))
          .nullSafe();
```

**With:**

```java
  @SuppressWarnings("rawtypes")
  public static final TypeAdapter<Class> CLASS =
      new TypeAdapter<Class>() {
        @Override
        public void write(JsonWriter out, Class value) throws IOException {
          throw new UnsupportedOperationException(
              "Attempted to serialize java.lang.Class. Forgot to register a type adapter?"
                  + "\nSee "
                  + TroubleshootingGuide.createUrl("java-lang-class-unsupported"));
        }

        @Override
        public Class read(JsonReader in) throws IOException {
          throw new UnsupportedOperationException(
              "Attempted to deserialize java.lang.Class. Forgot to register a type adapter?"
                  + "\nSee "
                  + TroubleshootingGuide.createUrl("java-lang-class-unsupported"));
        }
      }.nullSafe();
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `gson/src/main/java/com/google/gson/internal/bind/TypeAdapters.java` | 837 → 834 | 72 → 72 | 2.01 → 2.01 | 74 → 74 | 0 → 0 |

## Diff

```diff
diff --git a/gson/src/main/java/com/google/gson/internal/bind/TypeAdapters.java b/gson/src/main/java/com/google/gson/internal/bind/TypeAdapters.java
index ef6016e..ec9a5e7 100644
--- a/gson/src/main/java/com/google/gson/internal/bind/TypeAdapters.java
+++ b/gson/src/main/java/com/google/gson/internal/bind/TypeAdapters.java
@@ -62,31 +62,25 @@ public final class TypeAdapters {
     throw new UnsupportedOperationException();
   }
 
-  private static class UnsupportedTypeAdapter<T> extends TypeAdapter<T> {
-    private final String message;
-
-    UnsupportedTypeAdapter(String message) {
-      this.message = message;
-    }
-
-    @Override
-    public void write(JsonWriter out, T value) throws IOException {
-      throw new UnsupportedOperationException(message);
-    }
-
-    @Override
-    public T read(JsonReader in) throws IOException {
-      throw new UnsupportedOperationException(message);
-    }
-  }
-
   @SuppressWarnings("rawtypes")
   public static final TypeAdapter<Class> CLASS =
-      new UnsupportedTypeAdapter<Class>(
-              "Attempted to serialize/deserialize java.lang.Class. Forgot to register a type adapter?"
+      new TypeAdapter<Class>() {
+        @Override
+        public void write(JsonWriter out, Class value) throws IOException {
+          throw new UnsupportedOperationException(
+              "Attempted to serialize java.lang.Class. Forgot to register a type adapter?"
                   + "\nSee "
-                  + TroubleshootingGuide.createUrl("java-lang-class-unsupported"))
-          .nullSafe();
+                  + TroubleshootingGuide.createUrl("java-lang-class-unsupported"));
+        }
+
+        @Override
+        public Class read(JsonReader in) throws IOException {
+          throw new UnsupportedOperationException(
+              "Attempted to deserialize java.lang.Class. Forgot to register a type adapter?"
+                  + "\nSee "
+                  + TroubleshootingGuide.createUrl("java-lang-class-unsupported"));
+        }
+      }.nullSafe();
 
   public static final TypeAdapterFactory CLASS_FACTORY = newFactory(Class.class, CLASS);
 

```
