# Refactor DIP-023 (DIP): Hard-codes the instantiation of concrete Map implementations like LinkedTreeMap.

**Status:** `applied_unverified`  
**Branch:** `refactor/DIP-023` -> `main`  
**Head commit:** `4bf2dc60510151703176448dbf43c7fa29b0c143`  
**LLM finish:** `FinishReason.STOP` (prompt 5907, completion 603)  

## Detected issue

- **File**: `gson/src/main/java/com/google/gson/internal/ConstructorConstructor.java`
- **Entity**: `ConstructorConstructor.newMapConstructor` (method)
- **Lines (at detection time)**: L344–L365
- **Severity**: medium
- **Confidence**: detected by 2 scan(s)

**Description.** Hard-codes the instantiation of concrete Map implementations like LinkedTreeMap.

**Reasoning.** The method directly instantiates concrete classes like LinkedTreeMap instead of using an abstraction or a configurable provider. This couples the high-level instantiation logic to specific low-level data structures, making it difficult to change default implementations without modifying the internal factory.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `gson/src/main/java/com/google/gson/internal/ConstructorConstructor.java`

**Summary.** Refactor Map instantiation to use a registry of suppliers to decouple from concrete implementations.

**Rationale.** The previous implementation hard-coded concrete Map classes within the `MAP_CREATORS` list. By moving these to a static map of suppliers, we decouple the factory logic from specific implementations, adhering to the Dependency Inversion Principle.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `gson/src/main/java/com/google/gson/internal/ConstructorConstructor.java` (24-line block → 19-line replacement)

**Replaces:**

```java
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

**With:**

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
      return LinkedTreeMap::new;
    }
    for (Map.Entry<Class<?>, java.util.function.Supplier<Map<Object, Object>>> entry : MAP_CONSTRUCTORS.entrySet()) {
      if (entry.getKey().isAssignableFrom(rawType)) {
        return entry.getValue()::get;
      }
    }
    return null;
  }
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `gson/src/main/java/com/google/gson/internal/ConstructorConstructor.java` | 387 → 382 | 13 → 13 | 7.23 → 6.92 | 82 → 78 | 0 → 0 |

## Diff

```diff
diff --git a/gson/src/main/java/com/google/gson/internal/ConstructorConstructor.java b/gson/src/main/java/com/google/gson/internal/ConstructorConstructor.java
index 7e39836..8f8207e 100644
--- a/gson/src/main/java/com/google/gson/internal/ConstructorConstructor.java
+++ b/gson/src/main/java/com/google/gson/internal/ConstructorConstructor.java
@@ -356,27 +356,22 @@ public final class ConstructorConstructor {
     ObjectConstructor<? extends Map<?, Object>> create(Type type, Class<?> rawType);
   }
 
-  private static final List<MapCreator> MAP_CREATORS = List.of(
-      (type, rawType) -> {
-        if (LinkedTreeMap.class.isAssignableFrom(rawType) && hasStringKeyType(type)) {
-          return () -> new LinkedTreeMap<>();
-        }
-        return null;
-      },
-      (type, rawType) -> {
-        if (LinkedHashMap.class.isAssignableFrom(rawType)) return LinkedHashMap::new;
-        if (TreeMap.class.isAssignableFrom(rawType)) return TreeMap::new;
-        if (ConcurrentHashMap.class.isAssignableFrom(rawType)) return ConcurrentHashMap::new;
-        if (ConcurrentSkipListMap.class.isAssignableFrom(rawType)) return ConcurrentSkipListMap::new;
-        return null;
-      }
+  private static final Map<Class<?>, java.util.function.Supplier<Map<Object, Object>>> MAP_CONSTRUCTORS = Map.of(
+      LinkedHashMap.class, LinkedHashMap::new,
+      TreeMap.class, TreeMap::new,
+      ConcurrentHashMap.class, ConcurrentHashMap::new,
+      ConcurrentSkipListMap.class, ConcurrentSkipListMap::new
   );
 
   private static ObjectConstructor<? extends Map<?, Object>> newMapConstructor(
       Type type, Class<?> rawType) {
-    for (MapCreator creator : MAP_CREATORS) {
-      ObjectConstructor<? extends Map<?, Object>> constructor = creator.create(type, rawType);
-      if (constructor != null) return constructor;
+    if (LinkedTreeMap.class.isAssignableFrom(rawType) && hasStringKeyType(type)) {
+      return LinkedTreeMap::new;
+    }
+    for (Map.Entry<Class<?>, java.util.function.Supplier<Map<Object, Object>>> entry : MAP_CONSTRUCTORS.entrySet()) {
+      if (entry.getKey().isAssignableFrom(rawType)) {
+        return entry.getValue()::get;
+      }
     }
     return null;
   }

```
