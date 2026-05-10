# Refactor ISP-036 (ISP): The TypeAdapter for java.lang.Class forces clients to implement read and writ...

**Status:** `applied_unverified`  
**Branch:** `refactor/ISP-036` -> `main`  
**Head commit:** `74e65007e469622caed11b2a3e3e9a92119d7150`  
**LLM finish:** `FinishReason.STOP` (prompt 9731, completion 520)  

## Detected issue

- **File**: `gson/src/main/java/com/google/gson/internal/bind/TypeAdapters.java`
- **Entity**: `TypeAdapters.CLASS` (class)
- **Lines (at detection time)**: L60–L77
- **Severity**: high
- **Confidence**: detected by 3 scan(s)

**Description.** The TypeAdapter for java.lang.Class forces clients to implement read and write methods which are explicitly unsupported.

**Reasoning.** The anonymous TypeAdapter implementation for java.lang.Class throws UnsupportedOperationException for both its 'read' and 'write' methods. This indicates that the TypeAdapter interface is too broad for this specific client, forcing it to depend on and 'implement' methods it does not use or support, which is a direct violation of the Interface Segregation Principle. A more segregated interface might offer separate 'JsonReader' and 'JsonWriter' interfaces, or a 'SerializableTypeAdapter' and 'DeserializableTypeAdapter'.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `gson/src/main/java/com/google/gson/internal/bind/TypeAdapters.java`

**Summary.** Replace UnsupportedOperationException with a dedicated UnsupportedTypeAdapter

**Rationale.** The TypeAdapter interface is too broad for types that are explicitly unsupported. By introducing a specific UnsupportedTypeAdapter, we avoid forcing the implementation of read/write methods that are never meant to be called, adhering to the Interface Segregation Principle.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `gson/src/main/java/com/google/gson/internal/bind/TypeAdapters.java` (21-line block → 25-line replacement)

**Replaces:**

```java
  @SuppressWarnings("rawtypes")
  public static final TypeAdapter<Class> CLASS =
      new TypeAdapter<Class>() {
        @Override
        public void write(JsonWriter out, Class value) throws IOException {
          throw new UnsupportedOperationException(
              "Attempted to serialize java.lang.Class: "
                  + value.getName()
                  + ". Forgot to register a type adapter?"
                  + "\nSee "
                  + TroubleshootingGuide.createUrl("java-lang-class-unsupported"));
        }

        @Override
        public Class read(JsonReader in) throws IOException {
          throw new UnsupportedOperationException(
              "Attempted to deserialize a java.lang.Class. Forgot to register a type adapter?"
                  + "\nSee "
                  + TroubleshootingGuide.createUrl("java-lang-class-unsupported"));
        }
      }.nullSafe();
```

**With:**

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

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `gson/src/main/java/com/google/gson/internal/bind/TypeAdapters.java` | 836 → 837 | 72 → 72 | 2.01 → 2.01 | 74 → 74 | 0 → 0 |

## Diff

```diff
diff --git a/gson/src/main/java/com/google/gson/internal/bind/TypeAdapters.java b/gson/src/main/java/com/google/gson/internal/bind/TypeAdapters.java
index f6f7db9..ef6016e 100644
--- a/gson/src/main/java/com/google/gson/internal/bind/TypeAdapters.java
+++ b/gson/src/main/java/com/google/gson/internal/bind/TypeAdapters.java
@@ -62,27 +62,31 @@ public final class TypeAdapters {
     throw new UnsupportedOperationException();
   }
 
+  private static class UnsupportedTypeAdapter<T> extends TypeAdapter<T> {
+    private final String message;
+
+    UnsupportedTypeAdapter(String message) {
+      this.message = message;
+    }
+
+    @Override
+    public void write(JsonWriter out, T value) throws IOException {
+      throw new UnsupportedOperationException(message);
+    }
+
+    @Override
+    public T read(JsonReader in) throws IOException {
+      throw new UnsupportedOperationException(message);
+    }
+  }
+
   @SuppressWarnings("rawtypes")
   public static final TypeAdapter<Class> CLASS =
-      new TypeAdapter<Class>() {
-        @Override
-        public void write(JsonWriter out, Class value) throws IOException {
-          throw new UnsupportedOperationException(
-              "Attempted to serialize java.lang.Class: "
-                  + value.getName()
-                  + ". Forgot to register a type adapter?"
+      new UnsupportedTypeAdapter<Class>(
+              "Attempted to serialize/deserialize java.lang.Class. Forgot to register a type adapter?"
                   + "\nSee "
-                  + TroubleshootingGuide.createUrl("java-lang-class-unsupported"));
-        }
-
-        @Override
-        public Class read(JsonReader in) throws IOException {
-          throw new UnsupportedOperationException(
-              "Attempted to deserialize a java.lang.Class. Forgot to register a type adapter?"
-                  + "\nSee "
-                  + TroubleshootingGuide.createUrl("java-lang-class-unsupported"));
-        }
-      }.nullSafe();
+                  + TroubleshootingGuide.createUrl("java-lang-class-unsupported"))
+          .nullSafe();
 
   public static final TypeAdapterFactory CLASS_FACTORY = newFactory(Class.class, CLASS);
 

```
