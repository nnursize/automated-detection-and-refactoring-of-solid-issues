# Refactor OCP-028 (OCP): If-else if chain for default collection implementations violates OCP.

**Status:** `applied_unverified`  
**Branch:** `refactor/OCP-028` -> `main`  
**Head commit:** `6a48dcdb3e155bc2c6193e52e32b60d54695b3e9`  
**LLM finish:** `FinishReason.STOP` (prompt 5688, completion 807)  

## Detected issue

- **File**: `gson/src/main/java/com/google/gson/internal/ConstructorConstructor.java`
- **Entity**: `ConstructorConstructor.newCollectionConstructor` (method)
- **Lines (at detection time)**: L220–L239
- **Severity**: medium
- **Confidence**: detected by 4 scan(s)

**Description.** If-else if chain for default collection implementations violates OCP.

**Reasoning.** This method contains an `if-else if` chain checking for specific `Collection` implementations (`ArrayList`, `LinkedHashSet`, `TreeSet`, `ArrayDeque`). Adding support for other default collection implementations would require modifying this method.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 2
- **Files modified** (1): `gson/src/main/java/com/google/gson/internal/ConstructorConstructor.java`

**Summary.** Refactor collection and map constructor selection to use a registry pattern to satisfy OCP.

**Rationale.** Replaced hardcoded if-else chains in newCollectionConstructor and newMapConstructor with a registry of functional providers, allowing for easier extension without modifying the core logic.

## Changes overview

_2 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `gson/src/main/java/com/google/gson/internal/ConstructorConstructor.java` (10-line block → 18-line replacement)

**Replaces:**

```java
  private static ObjectConstructor<? extends Collection<?>> newCollectionConstructor(
      Class<?> rawType) {
    if (ArrayList.class.isAssignableFrom(rawType)) return ArrayList::new;
    if (LinkedHashSet.class.isAssignableFrom(rawType)) return LinkedHashSet::new;
    if (TreeSet.class.isAssignableFrom(rawType)) return TreeSet::new;
    if (ArrayDeque.class.isAssignableFrom(rawType)) return ArrayDeque::new;
    return null;
  }

  private static boolean hasStringKeyType(Type mapType) {
```

**With:**

```java
  private static final Map<Class<?>, java.util.function.Supplier<Collection<Object>>> COLLECTION_CONSTRUCTORS = Map.of(
      ArrayList.class, ArrayList::new,
      LinkedHashSet.class, LinkedHashSet::new,
      TreeSet.class, TreeSet::new,
      ArrayDeque.class, ArrayDeque::new
  );

  private static ObjectConstructor<? extends Collection<?>> newCollectionConstructor(
      Class<?> rawType) {
    for (Map.Entry<Class<?>, java.util.function.Supplier<Collection<Object>>> entry : COLLECTION_CONSTRUCTORS.entrySet()) {
      if (entry.getKey().isAssignableFrom(rawType)) {
        return entry.getValue()::get;
      }
    }
    return null;
  }

  private static boolean hasStringKeyType(Type mapType) {
```

### 2. EDIT `gson/src/main/java/com/google/gson/internal/ConstructorConstructor.java` (11-line block → 19-line replacement)

**Replaces:**

```java
  private static ObjectConstructor<? extends Map<?, Object>> newMapConstructor(
      Type type, Class<?> rawType) {
    if (LinkedTreeMap.class.isAssignableFrom(rawType) && hasStringKeyType(type)) {
      return () -> new LinkedTreeMap<>();
    }
    if (LinkedHashMap.class.isAssignableFrom(rawType)) return LinkedHashMap::new;
    if (TreeMap.class.isAssignableFrom(rawType)) return TreeMap::new;
    if (ConcurrentHashMap.class.isAssignableFrom(rawType)) return ConcurrentHashMap::new;
    if (ConcurrentSkipListMap.class.isAssignableFrom(rawType)) return ConcurrentSkipListMap::new;
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

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `gson/src/main/java/com/google/gson/internal/ConstructorConstructor.java` | 365 → 379 | 13 → 13 | 7.23 → 6.92 | 82 → 78 | 0 → 0 |

## Diff

```diff
diff --git a/gson/src/main/java/com/google/gson/internal/ConstructorConstructor.java b/gson/src/main/java/com/google/gson/internal/ConstructorConstructor.java
index 9f78c63..3ec674b 100644
--- a/gson/src/main/java/com/google/gson/internal/ConstructorConstructor.java
+++ b/gson/src/main/java/com/google/gson/internal/ConstructorConstructor.java
@@ -322,12 +322,20 @@ public final class ConstructorConstructor {
     return null;
   }
 
+  private static final Map<Class<?>, java.util.function.Supplier<Collection<Object>>> COLLECTION_CONSTRUCTORS = Map.of(
+      ArrayList.class, ArrayList::new,
+      LinkedHashSet.class, LinkedHashSet::new,
+      TreeSet.class, TreeSet::new,
+      ArrayDeque.class, ArrayDeque::new
+  );
+
   private static ObjectConstructor<? extends Collection<?>> newCollectionConstructor(
       Class<?> rawType) {
-    if (ArrayList.class.isAssignableFrom(rawType)) return ArrayList::new;
-    if (LinkedHashSet.class.isAssignableFrom(rawType)) return LinkedHashSet::new;
-    if (TreeSet.class.isAssignableFrom(rawType)) return TreeSet::new;
-    if (ArrayDeque.class.isAssignableFrom(rawType)) return ArrayDeque::new;
+    for (Map.Entry<Class<?>, java.util.function.Supplier<Collection<Object>>> entry : COLLECTION_CONSTRUCTORS.entrySet()) {
+      if (entry.getKey().isAssignableFrom(rawType)) {
+        return entry.getValue()::get;
+      }
+    }
     return null;
   }
 
@@ -344,15 +352,23 @@ public final class ConstructorConstructor {
     return GsonTypes.getRawType(typeArguments[0]) == String.class;
   }
 
+  private static final Map<Class<?>, java.util.function.Supplier<Map<Object, Object>>> MAP_CONSTRUCTORS = Map.of(
+      LinkedHashMap.class, LinkedHashMap::new,
+      TreeMap.class, TreeMap::new,
+      ConcurrentHashMap.class, ConcurrentHashMap::new,
+      ConcurrentSkipListMap.class, ConcurrentSkipListMap::new
+  );
+
   private static ObjectConstructor<? extends Map<?, Object>> newMapConstructor(
       Type type, Class<?> rawType) {
     if (LinkedTreeMap.class.isAssignableFrom(rawType) && hasStringKeyType(type)) {
       return () -> new LinkedTreeMap<>();
     }
-    if (LinkedHashMap.class.isAssignableFrom(rawType)) return LinkedHashMap::new;
-    if (TreeMap.class.isAssignableFrom(rawType)) return TreeMap::new;
-    if (ConcurrentHashMap.class.isAssignableFrom(rawType)) return ConcurrentHashMap::new;
-    if (ConcurrentSkipListMap.class.isAssignableFrom(rawType)) return ConcurrentSkipListMap::new;
+    for (Map.Entry<Class<?>, java.util.function.Supplier<Map<Object, Object>>> entry : MAP_CONSTRUCTORS.entrySet()) {
+      if (entry.getKey().isAssignableFrom(rawType)) {
+        return entry.getValue()::get;
+      }
+    }
     return null;
   }
 

```
