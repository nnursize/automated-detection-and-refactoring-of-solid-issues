# Refactor OCP-029 (OCP): If-else if chain for default map implementations violates OCP.

**Status:** `applied_unverified`  
**Branch:** `refactor/OCP-029` -> `main`  
**Head commit:** `d0fa5aa077f21ff09e9f7beb4c987f40aa4249cb`  
**LLM finish:** `FinishReason.STOP` (prompt 5830, completion 617)  

## Detected issue

- **File**: `gson/src/main/java/com/google/gson/internal/ConstructorConstructor.java`
- **Entity**: `ConstructorConstructor.newMapConstructor` (method)
- **Lines (at detection time)**: L249–L274
- **Severity**: medium
- **Confidence**: detected by 4 scan(s)

**Description.** If-else if chain for default map implementations violates OCP.

**Reasoning.** This method contains an `if-else if` chain checking for specific `Map` implementations (`LinkedTreeMap`, `LinkedHashMap`, `TreeMap`, `ConcurrentHashMap`, `ConcurrentSkipListMap`). Adding support for other default map implementations would require modifying this method.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `gson/src/main/java/com/google/gson/internal/ConstructorConstructor.java`

**Summary.** Refactor map constructor logic to use a registry pattern for OCP compliance

**Rationale.** Replaced the hardcoded logic in newMapConstructor with a registry of MapCreators, allowing new map types to be added without modifying the core logic.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `gson/src/main/java/com/google/gson/internal/ConstructorConstructor.java` (19-line block → 28-line replacement)

**Replaces:**

```java
  private static final Map<Class<?>, java.util.function.Supplier<Map<Object, Object>>> MAP_CONSTRUCTORS = Map.of(
      LinkedHashMap.class, LinkedHashMap::new,
      TreeMap.class, TreeMap::new,
      ConcurrentHashMap.class, ConcurrentHashMap::new,
      ConcurrentSkipListMap.class, ConcurrentSkipListMap::new
  );

  private static ObjectConstructor<? extends Map<?, Object>> newMapConstructor(
      Type type, Class<?> rawType) {
    if (LinkedTreeMap.class.isAssignableFrom(rawType) && hasStringKeyType(type)) {
      return () -> new LinkedTreeMap<>();
    }
    for (Map.Entry<Class<?>, java.util.function.Supplier<Map<Object, Object>>> entry : MAP_CONSTRUCTORS.entrySet()) {
      if (entry.getKey().isAssignableFrom(rawType)) {
        return entry.getValue()::get;
      }
    }
    return null;
  }
```

**With:**

```java
  private interface MapCreator {
    ObjectConstructor<? extends Map<?, Object>> create(Type type, Class<?> rawType);
  }

  private static final List<MapCreator> MAP_CREATORS = List.of(
      (type, rawType) -> {
        if (LinkedTreeMap.class.isAssignableFrom(rawType) && hasStringKeyType(type)) {
          return () -> new LinkedTreeMap<>();
        }
        return null;
      },
      (type, rawType) -> {
        if (LinkedHashMap.class.isAssignableFrom(rawType)) return LinkedHashMap::new;
        if (TreeMap.class.isAssignableFrom(rawType)) return TreeMap::new;
        if (ConcurrentHashMap.class.isAssignableFrom(rawType)) return ConcurrentHashMap::new;
        if (ConcurrentSkipListMap.class.isAssignableFrom(rawType)) return ConcurrentSkipListMap::new;
        return null;
      }
  );

  private static ObjectConstructor<? extends Map<?, Object>> newMapConstructor(
      Type type, Class<?> rawType) {
    for (MapCreator creator : MAP_CREATORS) {
      ObjectConstructor<? extends Map<?, Object>> constructor = creator.create(type, rawType);
      if (constructor != null) return constructor;
    }
    return null;
  }
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `gson/src/main/java/com/google/gson/internal/ConstructorConstructor.java` | 379 → 387 | 13 → 13 | 6.92 → 7.23 | 78 → 82 | 0 → 0 |

## Diff

```diff
diff --git a/gson/src/main/java/com/google/gson/internal/ConstructorConstructor.java b/gson/src/main/java/com/google/gson/internal/ConstructorConstructor.java
index 3ec674b..3ad6523 100644
--- a/gson/src/main/java/com/google/gson/internal/ConstructorConstructor.java
+++ b/gson/src/main/java/com/google/gson/internal/ConstructorConstructor.java
@@ -352,22 +352,31 @@ public final class ConstructorConstructor {
     return GsonTypes.getRawType(typeArguments[0]) == String.class;
   }
 
-  private static final Map<Class<?>, java.util.function.Supplier<Map<Object, Object>>> MAP_CONSTRUCTORS = Map.of(
-      LinkedHashMap.class, LinkedHashMap::new,
-      TreeMap.class, TreeMap::new,
-      ConcurrentHashMap.class, ConcurrentHashMap::new,
-      ConcurrentSkipListMap.class, ConcurrentSkipListMap::new
+  private interface MapCreator {
+    ObjectConstructor<? extends Map<?, Object>> create(Type type, Class<?> rawType);
+  }
+
+  private static final List<MapCreator> MAP_CREATORS = List.of(
+      (type, rawType) -> {
+        if (LinkedTreeMap.class.isAssignableFrom(rawType) && hasStringKeyType(type)) {
+          return () -> new LinkedTreeMap<>();
+        }
+        return null;
+      },
+      (type, rawType) -> {
+        if (LinkedHashMap.class.isAssignableFrom(rawType)) return LinkedHashMap::new;
+        if (TreeMap.class.isAssignableFrom(rawType)) return TreeMap::new;
+        if (ConcurrentHashMap.class.isAssignableFrom(rawType)) return ConcurrentHashMap::new;
+        if (ConcurrentSkipListMap.class.isAssignableFrom(rawType)) return ConcurrentSkipListMap::new;
+        return null;
+      }
   );
 
   private static ObjectConstructor<? extends Map<?, Object>> newMapConstructor(
       Type type, Class<?> rawType) {
-    if (LinkedTreeMap.class.isAssignableFrom(rawType) && hasStringKeyType(type)) {
-      return () -> new LinkedTreeMap<>();
-    }
-    for (Map.Entry<Class<?>, java.util.function.Supplier<Map<Object, Object>>> entry : MAP_CONSTRUCTORS.entrySet()) {
-      if (entry.getKey().isAssignableFrom(rawType)) {
-        return entry.getValue()::get;
-      }
+    for (MapCreator creator : MAP_CREATORS) {
+      ObjectConstructor<? extends Map<?, Object>> constructor = creator.create(type, rawType);
+      if (constructor != null) return constructor;
     }
     return null;
   }

```
