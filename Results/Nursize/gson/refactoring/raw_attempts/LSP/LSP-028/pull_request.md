# Refactor LSP-028 (LSP): Returns a TypeAdapter that ignores content for anonymous/local classes, chang...

**Status:** `applied_unverified`  
**Branch:** `refactor/LSP-028` -> `main`  
**Head commit:** `ff4cb3ebe63508f4e8b76b6323080527463247f8`  
**LLM finish:** `FinishReason.STOP` (prompt 7842, completion 722)  

## Detected issue

- **File**: `gson/src/main/java/com/google/gson/internal/bind/ReflectiveTypeAdapterFactory.java`
- **Entity**: `ReflectiveTypeAdapterFactory.create` (method)
- **Lines (at detection time)**: L98–L117
- **Severity**: medium
- **Confidence**: detected by 4 scan(s)

**Description.** Returns a TypeAdapter that ignores content for anonymous/local classes, changing reflective behavior.

**Reasoning.** For anonymous or non-static local classes, the `create` method returns a `TypeAdapter` that serializes to JSON `null` and deserializes by skipping the value and returning Java `null`. This deviates from the expected reflective serialization/deserialization behavior of a `ReflectiveTypeAdapterFactory`, which is to process the object's fields. This makes the generated adapter not fully substitutable for a truly reflective adapter for all class types.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `gson/src/main/java/com/google/gson/internal/bind/ReflectiveTypeAdapterFactory.java`

**Summary.** Remove special handling for anonymous/local classes in ReflectiveTypeAdapterFactory

**Rationale.** The special handling that returned a null-adapter for anonymous/local classes violated the Liskov Substitution Principle by failing to provide the expected reflective behavior. Removing this special case allows the factory to attempt reflective serialization/deserialization, which is the correct behavior for a reflective adapter factory.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `gson/src/main/java/com/google/gson/internal/bind/ReflectiveTypeAdapterFactory.java` (42-line block → 9-line replacement)

**Replaces:**

```java
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

**With:**

```java
    if (ReflectionHelper.isRecord(raw)) {
      return (TypeAdapter<T>) new RecordAdapter<>(
          raw, getBoundFields(gson, type, raw, blockInaccessible, true), blockInaccessible);
    }

    ObjectConstructor<T> constructor = constructorConstructor.get(type, true);
    return new FieldReflectionAdapter<>(
        constructor, getBoundFields(gson, type, raw, blockInaccessible, false));
  }
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `gson/src/main/java/com/google/gson/internal/bind/ReflectiveTypeAdapterFactory.java` | 549 → 518 | 10 → 8 | 9.8 → 11.62 | 89 → 86 | 0 → 0 |

## Diff

```diff
diff --git a/gson/src/main/java/com/google/gson/internal/bind/ReflectiveTypeAdapterFactory.java b/gson/src/main/java/com/google/gson/internal/bind/ReflectiveTypeAdapterFactory.java
index 17865ed..bb26de5 100644
--- a/gson/src/main/java/com/google/gson/internal/bind/ReflectiveTypeAdapterFactory.java
+++ b/gson/src/main/java/com/google/gson/internal/bind/ReflectiveTypeAdapterFactory.java
@@ -112,48 +112,15 @@ public final class ReflectiveTypeAdapterFactory implements TypeAdapterFactory {
     }
     boolean blockInaccessible = filterResult == FilterResult.BLOCK_INACCESSIBLE;
 
-    for (SpecialTypeStrategy strategy : SPECIAL_TYPE_STRATEGIES) {
-      TypeAdapter<T> adapter = strategy.create(gson, type, raw, blockInaccessible);
-      if (adapter != null) {
-        return adapter;
-      }
+    if (ReflectionHelper.isRecord(raw)) {
+      return (TypeAdapter<T>) new RecordAdapter<>(
+          raw, getBoundFields(gson, type, raw, blockInaccessible, true), blockInaccessible);
     }
 
     ObjectConstructor<T> constructor = constructorConstructor.get(type, true);
     return new FieldReflectionAdapter<>(
         constructor, getBoundFields(gson, type, raw, blockInaccessible, false));
   }
-
-  private interface SpecialTypeStrategy {
-    <T> TypeAdapter<T> create(Gson gson, TypeToken<T> type, Class<? super T> raw, boolean blockInaccessible);
-  }
-
-  private static final List<SpecialTypeStrategy> SPECIAL_TYPE_STRATEGIES = Arrays.asList(
-      new SpecialTypeStrategy() {
-        @Override
-        public <T> TypeAdapter<T> create(Gson gson, TypeToken<T> type, Class<? super T> raw, boolean blockInaccessible) {
-          if (ReflectionHelper.isAnonymousOrNonStaticLocal(raw)) {
-            return new TypeAdapter<T>() {
-              @Override public T read(JsonReader in) throws IOException { in.skipValue(); return null; }
-              @Override public void write(JsonWriter out, T value) throws IOException { out.nullValue(); }
-              @Override public String toString() { return "AnonymousOrNonStaticLocalClassAdapter"; }
-            };
-          }
-          return null;
-        }
-      },
-      new SpecialTypeStrategy() {
-        @Override
-        @SuppressWarnings("unchecked")
-        public <T> TypeAdapter<T> create(Gson gson, TypeToken<T> type, Class<? super T> raw, boolean blockInaccessible) {
-          if (ReflectionHelper.isRecord(raw)) {
-            return (TypeAdapter<T>) new RecordAdapter<>(
-                raw, getBoundFields(gson, type, raw, blockInaccessible, true), blockInaccessible);
-          }
-          return null;
-        }
-      }
-  );
   }
 
   private static <M extends AccessibleObject & Member> void checkAccessible(

```
