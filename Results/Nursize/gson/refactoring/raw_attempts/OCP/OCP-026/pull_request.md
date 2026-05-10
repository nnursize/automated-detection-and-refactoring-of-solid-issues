# Refactor OCP-026 (OCP): If-else if chain for special collection types violates OCP.

**Status:** `applied_unverified`  
**Branch:** `refactor/OCP-026` -> `main`  
**Head commit:** `0f6a3458af64df3bd4d8d26f47054b228d5ab896`  
**LLM finish:** `FinishReason.STOP` (prompt 5559, completion 1029)  

## Detected issue

- **File**: `gson/src/main/java/com/google/gson/internal/ConstructorConstructor.java`
- **Entity**: `ConstructorConstructor.newSpecialCollectionConstructor` (method)
- **Lines (at detection time)**: L112–L147
- **Severity**: medium
- **Confidence**: detected by 6 scan(s)

**Description.** If-else if chain for special collection types violates OCP.

**Reasoning.** This method contains an `if-else if` chain specifically checking for `EnumSet.class` and `EnumMap.class`. If support for other special collection types (e.g., new JDK collection types) were needed, this method would require modification.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `gson/src/main/java/com/google/gson/internal/ConstructorConstructor.java`

**Summary.** Refactor special collection constructor creation to use a registry pattern to satisfy OCP.

**Rationale.** Replaced the hardcoded if-else chain with a registry of 'SpecialCollectionCreator' strategies. This allows adding new special collection types without modifying the core logic of ConstructorConstructor.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `gson/src/main/java/com/google/gson/internal/ConstructorConstructor.java` (43-line block → 53-line replacement)

**Replaces:**

```java
  /**
   * Creates constructors for special JDK collection types which do not have a public no-args
   * constructor.
   */
  private static <T> ObjectConstructor<T> newSpecialCollectionConstructor(
      Type type, Class<? super T> rawType) {
    if (EnumSet.class.isAssignableFrom(rawType)) {
      return () -> {
        if (type instanceof ParameterizedType) {
          Type elementType = ((ParameterizedType) type).getActualTypeArguments()[0];
          if (elementType instanceof Class) {
            @SuppressWarnings({"unchecked", "rawtypes"})
            T set = (T) EnumSet.noneOf((Class) elementType);
            return set;
          } else {
            throw new JsonIOException("Invalid EnumSet type: " + type);
          }
        } else {
          throw new JsonIOException("Invalid EnumSet type: " + type);
        }
      };
    }
    // Only support creation of EnumMap, but not of custom subtypes; for them type parameters
    // and constructor parameter might have completely different meaning
    else if (rawType == EnumMap.class) {
      return () -> {
        if (type instanceof ParameterizedType) {
          Type elementType = ((ParameterizedType) type).getActualTypeArguments()[0];
          if (elementType instanceof Class) {
            @SuppressWarnings({"unchecked", "rawtypes"})
            T map = (T) new EnumMap((Class) elementType);
            return map;
          } else {
            throw new JsonIOException("Invalid EnumMap type: " + type);
          }
        } else {
          throw new JsonIOException("Invalid EnumMap type: " + type);
        }
      };
    }

    return null;
  }
```

**With:**

```java
  private interface SpecialCollectionCreator {
    <T> ObjectConstructor<T> create(Type type, Class<? super T> rawType);
  }

  private static final List<SpecialCollectionCreator> SPECIAL_COLLECTION_CREATORS = List.of(
      new SpecialCollectionCreator() {
        @Override public <T> ObjectConstructor<T> create(Type type, Class<? super T> rawType) {
          if (!EnumSet.class.isAssignableFrom(rawType)) return null;
          return () -> {
            if (type instanceof ParameterizedType) {
              Type elementType = ((ParameterizedType) type).getActualTypeArguments()[0];
              if (elementType instanceof Class) {
                @SuppressWarnings({"unchecked", "rawtypes"})
                T set = (T) EnumSet.noneOf((Class) elementType);
                return set;
              }
              throw new JsonIOException("Invalid EnumSet type: " + type);
            }
            throw new JsonIOException("Invalid EnumSet type: " + type);
          };
        }
      },
      new SpecialCollectionCreator() {
        @Override public <T> ObjectConstructor<T> create(Type type, Class<? super T> rawType) {
          if (rawType != EnumMap.class) return null;
          return () -> {
            if (type instanceof ParameterizedType) {
              Type elementType = ((ParameterizedType) type).getActualTypeArguments()[0];
              if (elementType instanceof Class) {
                @SuppressWarnings({"unchecked", "rawtypes"})
                T map = (T) new EnumMap((Class) elementType);
                return map;
              }
              throw new JsonIOException("Invalid EnumMap type: " + type);
            }
            throw new JsonIOException("Invalid EnumMap type: " + type);
          };
        }
      }
  );

  /**
   * Creates constructors for special JDK collection types which do not have a public no-args
   * constructor.
   */
  private static <T> ObjectConstructor<T> newSpecialCollectionConstructor(
      Type type, Class<? super T> rawType) {
    for (SpecialCollectionCreator creator : SPECIAL_COLLECTION_CREATORS) {
      ObjectConstructor<T> constructor = creator.create(type, rawType);
      if (constructor != null) return constructor;
    }
    return null;
  }
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `gson/src/main/java/com/google/gson/internal/ConstructorConstructor.java` | 354 → 365 | 13 → 13 | 7.15 → 7.23 | 81 → 82 | 0 → 0 |

## Diff

```diff
diff --git a/gson/src/main/java/com/google/gson/internal/ConstructorConstructor.java b/gson/src/main/java/com/google/gson/internal/ConstructorConstructor.java
index 163b26b..9f78c63 100644
--- a/gson/src/main/java/com/google/gson/internal/ConstructorConstructor.java
+++ b/gson/src/main/java/com/google/gson/internal/ConstructorConstructor.java
@@ -170,47 +170,57 @@ public final class ConstructorConstructor {
     return newUnsafeAllocator(rawType);
   }
 
+  private interface SpecialCollectionCreator {
+    <T> ObjectConstructor<T> create(Type type, Class<? super T> rawType);
+  }
+
+  private static final List<SpecialCollectionCreator> SPECIAL_COLLECTION_CREATORS = List.of(
+      new SpecialCollectionCreator() {
+        @Override public <T> ObjectConstructor<T> create(Type type, Class<? super T> rawType) {
+          if (!EnumSet.class.isAssignableFrom(rawType)) return null;
+          return () -> {
+            if (type instanceof ParameterizedType) {
+              Type elementType = ((ParameterizedType) type).getActualTypeArguments()[0];
+              if (elementType instanceof Class) {
+                @SuppressWarnings({"unchecked", "rawtypes"})
+                T set = (T) EnumSet.noneOf((Class) elementType);
+                return set;
+              }
+              throw new JsonIOException("Invalid EnumSet type: " + type);
+            }
+            throw new JsonIOException("Invalid EnumSet type: " + type);
+          };
+        }
+      },
+      new SpecialCollectionCreator() {
+        @Override public <T> ObjectConstructor<T> create(Type type, Class<? super T> rawType) {
+          if (rawType != EnumMap.class) return null;
+          return () -> {
+            if (type instanceof ParameterizedType) {
+              Type elementType = ((ParameterizedType) type).getActualTypeArguments()[0];
+              if (elementType instanceof Class) {
+                @SuppressWarnings({"unchecked", "rawtypes"})
+                T map = (T) new EnumMap((Class) elementType);
+                return map;
+              }
+              throw new JsonIOException("Invalid EnumMap type: " + type);
+            }
+            throw new JsonIOException("Invalid EnumMap type: " + type);
+          };
+        }
+      }
+  );
+
   /**
    * Creates constructors for special JDK collection types which do not have a public no-args
    * constructor.
    */
   private static <T> ObjectConstructor<T> newSpecialCollectionConstructor(
       Type type, Class<? super T> rawType) {
-    if (EnumSet.class.isAssignableFrom(rawType)) {
-      return () -> {
-        if (type instanceof ParameterizedType) {
-          Type elementType = ((ParameterizedType) type).getActualTypeArguments()[0];
-          if (elementType instanceof Class) {
-            @SuppressWarnings({"unchecked", "rawtypes"})
-            T set = (T) EnumSet.noneOf((Class) elementType);
-            return set;
-          } else {
-            throw new JsonIOException("Invalid EnumSet type: " + type);
-          }
-        } else {
-          throw new JsonIOException("Invalid EnumSet type: " + type);
-        }
-      };
+    for (SpecialCollectionCreator creator : SPECIAL_COLLECTION_CREATORS) {
+      ObjectConstructor<T> constructor = creator.create(type, rawType);
+      if (constructor != null) return constructor;
     }
-    // Only support creation of EnumMap, but not of custom subtypes; for them type parameters
-    // and constructor parameter might have completely different meaning
-    else if (rawType == EnumMap.class) {
-      return () -> {
-        if (type instanceof ParameterizedType) {
-          Type elementType = ((ParameterizedType) type).getActualTypeArguments()[0];
-          if (elementType instanceof Class) {
-            @SuppressWarnings({"unchecked", "rawtypes"})
-            T map = (T) new EnumMap((Class) elementType);
-            return map;
-          } else {
-            throw new JsonIOException("Invalid EnumMap type: " + type);
-          }
-        } else {
-          throw new JsonIOException("Invalid EnumMap type: " + type);
-        }
-      };
-    }
-
     return null;
   }
 

```
