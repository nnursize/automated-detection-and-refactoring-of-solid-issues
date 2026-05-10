# Refactor OCP-023 (OCP): Conditional logic for special class types (anonymous, local, record) violates...

**Status:** `applied_unverified`  
**Branch:** `refactor/OCP-023` -> `main`  
**Head commit:** `24c27a12f3f40c9ccc25cefa0c354dbf2fbdf297`  
**LLM finish:** `FinishReason.STOP` (prompt 7705, completion 1153)  

## Detected issue

- **File**: `gson/src/main/java/com/google/gson/internal/bind/ReflectiveTypeAdapterFactory.java`
- **Entity**: `ReflectiveTypeAdapterFactory.create` (method)
- **Lines (at detection time)**: L69–L104
- **Severity**: medium
- **Confidence**: detected by 4 scan(s)

**Description.** Conditional logic for special class types (anonymous, local, record) violates OCP.

**Reasoning.** The `create()` method contains `if` checks for `ReflectionHelper.isAnonymousOrNonStaticLocal` and `ReflectionHelper.isRecord`. If new special class types requiring different reflection-based serialization/deserialization handling were introduced, this method would need modification to include new `if` branches, violating OCP.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `gson/src/main/java/com/google/gson/internal/bind/ReflectiveTypeAdapterFactory.java`

**Summary.** Introduce a strategy-based approach for handling special class types in ReflectiveTypeAdapterFactory

**Rationale.** Replaced hardcoded if-checks with a list of TypeAdapterStrategy implementations to allow adding new special class types without modifying the core create() method.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `gson/src/main/java/com/google/gson/internal/bind/ReflectiveTypeAdapterFactory.java` (49-line block → 52-line replacement)

**Replaces:**

```java
    // Don't allow using reflection on anonymous and local classes because synthetic fields for
    // captured enclosing values make this unreliable
    if (ReflectionHelper.isAnonymousOrNonStaticLocal(raw)) {
      // This adapter just serializes and deserializes null, ignoring the actual values
      // This is done for backward compatibility; troubleshooting-wise it might be better to throw
      // exceptions
      return new TypeAdapter<T>() {
        @Override
        public T read(JsonReader in) throws IOException {
          in.skipValue();
          return null;
        }

        @Override
        public void write(JsonWriter out, T value) throws IOException {
          out.nullValue();
        }

        @Override
        public String toString() {
          return "AnonymousOrNonStaticLocalClassAdapter";
        }
      };
    }

    FilterResult filterResult =
        ReflectionAccessFilterHelper.getFilterResult(reflectionFilters, raw);
    if (filterResult == FilterResult.BLOCK_ALL) {
      throw new JsonIOException(
          "ReflectionAccessFilter does not permit using reflection for "
              + raw
              + ". Register a TypeAdapter for this type or adjust the access filter.");
    }
    boolean blockInaccessible = filterResult == FilterResult.BLOCK_INACCESSIBLE;

    // If the type is actually a Java Record, we need to use the RecordAdapter instead. This will
    // always be false on JVMs that do not support records.
    if (ReflectionHelper.isRecord(raw)) {
      @SuppressWarnings("unchecked")
      TypeAdapter<T> adapter =
          (TypeAdapter<T>)
              new RecordAdapter<>(
                  raw, getBoundFields(gson, type, raw, blockInaccessible, true), blockInaccessible);
      return adapter;
    }

    ObjectConstructor<T> constructor = constructorConstructor.get(type, true);
    return new FieldReflectionAdapter<>(
        constructor, getBoundFields(gson, type, raw, blockInaccessible, false));
```

**With:**

```java
    FilterResult filterResult =
        ReflectionAccessFilterHelper.getFilterResult(reflectionFilters, raw);
    if (filterResult == FilterResult.BLOCK_ALL) {
      throw new JsonIOException(
          "ReflectionAccessFilter does not permit using reflection for "
              + raw
              + ". Register a TypeAdapter for this type or adjust the access filter.");
    }
    boolean blockInaccessible = filterResult == FilterResult.BLOCK_INACCESSIBLE;

    for (SpecialTypeStrategy strategy : SPECIAL_TYPE_STRATEGIES) {
      TypeAdapter<T> adapter = strategy.create(gson, type, raw, blockInaccessible);
      if (adapter != null) {
        return adapter;
      }
    }

    ObjectConstructor<T> constructor = constructorConstructor.get(type, true);
    return new FieldReflectionAdapter<>(
        constructor, getBoundFields(gson, type, raw, blockInaccessible, false));
  }

  private interface SpecialTypeStrategy {
    <T> TypeAdapter<T> create(Gson gson, TypeToken<T> type, Class<? super T> raw, boolean blockInaccessible);
  }

  private static final List<SpecialTypeStrategy> SPECIAL_TYPE_STRATEGIES = Arrays.asList(
      new SpecialTypeStrategy() {
        @Override
        public <T> TypeAdapter<T> create(Gson gson, TypeToken<T> type, Class<? super T> raw, boolean blockInaccessible) {
          if (ReflectionHelper.isAnonymousOrNonStaticLocal(raw)) {
            return new TypeAdapter<T>() {
              @Override public T read(JsonReader in) throws IOException { in.skipValue(); return null; }
              @Override public void write(JsonWriter out, T value) throws IOException { out.nullValue(); }
              @Override public String toString() { return "AnonymousOrNonStaticLocalClassAdapter"; }
            };
          }
          return null;
        }
      },
      new SpecialTypeStrategy() {
        @Override
        @SuppressWarnings("unchecked")
        public <T> TypeAdapter<T> create(Gson gson, TypeToken<T> type, Class<? super T> raw, boolean blockInaccessible) {
          if (ReflectionHelper.isRecord(raw)) {
            return (TypeAdapter<T>) new RecordAdapter<>(
                raw, getBoundFields(gson, type, raw, blockInaccessible, true), blockInaccessible);
          }
          return null;
        }
      }
  );
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `gson/src/main/java/com/google/gson/internal/bind/ReflectiveTypeAdapterFactory.java` | 538 → 549 | 11 → 10 | 9.09 → 9.8 | 90 → 89 | 0 → 0 |

## Diff

```diff
diff --git a/gson/src/main/java/com/google/gson/internal/bind/ReflectiveTypeAdapterFactory.java b/gson/src/main/java/com/google/gson/internal/bind/ReflectiveTypeAdapterFactory.java
index 3010bef..17865ed 100644
--- a/gson/src/main/java/com/google/gson/internal/bind/ReflectiveTypeAdapterFactory.java
+++ b/gson/src/main/java/com/google/gson/internal/bind/ReflectiveTypeAdapterFactory.java
@@ -102,31 +102,6 @@ public final class ReflectiveTypeAdapterFactory implements TypeAdapterFactory {
       return null; // it's a primitive!
     }
 
-    // Don't allow using reflection on anonymous and local classes because synthetic fields for
-    // captured enclosing values make this unreliable
-    if (ReflectionHelper.isAnonymousOrNonStaticLocal(raw)) {
-      // This adapter just serializes and deserializes null, ignoring the actual values
-      // This is done for backward compatibility; troubleshooting-wise it might be better to throw
-      // exceptions
-      return new TypeAdapter<T>() {
-        @Override
-        public T read(JsonReader in) throws IOException {
-          in.skipValue();
-          return null;
-        }
-
-        @Override
-        public void write(JsonWriter out, T value) throws IOException {
-          out.nullValue();
-        }
-
-        @Override
-        public String toString() {
-          return "AnonymousOrNonStaticLocalClassAdapter";
-        }
-      };
-    }
-
     FilterResult filterResult =
         ReflectionAccessFilterHelper.getFilterResult(reflectionFilters, raw);
     if (filterResult == FilterResult.BLOCK_ALL) {
@@ -137,15 +112,11 @@ public final class ReflectiveTypeAdapterFactory implements TypeAdapterFactory {
     }
     boolean blockInaccessible = filterResult == FilterResult.BLOCK_INACCESSIBLE;
 
-    // If the type is actually a Java Record, we need to use the RecordAdapter instead. This will
-    // always be false on JVMs that do not support records.
-    if (ReflectionHelper.isRecord(raw)) {
-      @SuppressWarnings("unchecked")
-      TypeAdapter<T> adapter =
-          (TypeAdapter<T>)
-              new RecordAdapter<>(
-                  raw, getBoundFields(gson, type, raw, blockInaccessible, true), blockInaccessible);
-      return adapter;
+    for (SpecialTypeStrategy strategy : SPECIAL_TYPE_STRATEGIES) {
+      TypeAdapter<T> adapter = strategy.create(gson, type, raw, blockInaccessible);
+      if (adapter != null) {
+        return adapter;
+      }
     }
 
     ObjectConstructor<T> constructor = constructorConstructor.get(type, true);
@@ -153,6 +124,38 @@ public final class ReflectiveTypeAdapterFactory implements TypeAdapterFactory {
         constructor, getBoundFields(gson, type, raw, blockInaccessible, false));
   }
 
+  private interface SpecialTypeStrategy {
+    <T> TypeAdapter<T> create(Gson gson, TypeToken<T> type, Class<? super T> raw, boolean blockInaccessible);
+  }
+
+  private static final List<SpecialTypeStrategy> SPECIAL_TYPE_STRATEGIES = Arrays.asList(
+      new SpecialTypeStrategy() {
+        @Override
+        public <T> TypeAdapter<T> create(Gson gson, TypeToken<T> type, Class<? super T> raw, boolean blockInaccessible) {
+          if (ReflectionHelper.isAnonymousOrNonStaticLocal(raw)) {
+            return new TypeAdapter<T>() {
+              @Override public T read(JsonReader in) throws IOException { in.skipValue(); return null; }
+              @Override public void write(JsonWriter out, T value) throws IOException { out.nullValue(); }
+              @Override public String toString() { return "AnonymousOrNonStaticLocalClassAdapter"; }
+            };
+          }
+          return null;
+        }
+      },
+      new SpecialTypeStrategy() {
+        @Override
+        @SuppressWarnings("unchecked")
+        public <T> TypeAdapter<T> create(Gson gson, TypeToken<T> type, Class<? super T> raw, boolean blockInaccessible) {
+          if (ReflectionHelper.isRecord(raw)) {
+            return (TypeAdapter<T>) new RecordAdapter<>(
+                raw, getBoundFields(gson, type, raw, blockInaccessible, true), blockInaccessible);
+          }
+          return null;
+        }
+      }
+  );
+  }
+
   private static <M extends AccessibleObject & Member> void checkAccessible(
       Object object, M member) {
     if (!ReflectionAccessFilterHelper.canAccess(

```
