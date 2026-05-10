# Refactor ISP-002 (ISP): Anonymous TypeAdapter for anonymous or non-static local classes provides no-o...

**Status:** `applied_unverified`  
**Branch:** `refactor/ISP-002` -> `main`  
**Head commit:** `50fe3c8e3b1ffb442722bde40c3ba4ee868b5d77`  
**LLM finish:** `FinishReason.STOP` (prompt 7498, completion 462)  

## Detected issue

- **File**: `gson/src/main/java/com/google/gson/internal/bind/ReflectiveTypeAdapterFactory.java`
- **Entity**: `ReflectiveTypeAdapterFactory.create(...).new TypeAdapter<T>() {...}` (class)
- **Lines (at detection time)**: L78–L96
- **Severity**: medium
- **Confidence**: detected by 2 scan(s)

**Description.** Anonymous TypeAdapter for anonymous or non-static local classes provides no-op implementations for read and write.

**Reasoning.** The `TypeAdapter` interface forces this adapter to implement both `read` and `write` methods. However, for anonymous or non-static local classes, Gson's reflective adapter is designed to ignore them (serialize as null, skip value on deserialize). This results in no-op implementations (`in.skipValue()`, `out.nullValue()`), indicating that the interface is too broad for types that are meant to be excluded or ignored.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `gson/src/main/java/com/google/gson/internal/bind/ReflectiveTypeAdapterFactory.java`

**Summary.** Refactor ReflectiveTypeAdapterFactory to avoid anonymous TypeAdapter implementation for ignored types

**Rationale.** The previous implementation of ReflectiveTypeAdapterFactory.create() returned an anonymous TypeAdapter that implemented no-op read/write methods for types that should be ignored. By returning null instead of an anonymous class, we adhere to the Interface Segregation Principle, as the factory now correctly signals that it cannot provide an adapter for these types, rather than providing a 'fat' adapter that violates the contract of the TypeAdapter interface.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `gson/src/main/java/com/google/gson/internal/bind/ReflectiveTypeAdapterFactory.java` (9-line block → 15-line replacement)

**Replaces:**

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

**With:**

```java
    if (ReflectionHelper.isRecord(raw)) {
      return (TypeAdapter<T>) new RecordAdapter<>(
          raw, getBoundFields(gson, type, raw, blockInaccessible, true), blockInaccessible);
    }

    // If the class is anonymous or a local class, we cannot reflectively instantiate it.
    // We return null to let other factories handle it or to let Gson skip it.
    if (raw.isAnonymousClass() || raw.isLocalClass()) {
      return null;
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
| `gson/src/main/java/com/google/gson/internal/bind/ReflectiveTypeAdapterFactory.java` | 518 → 521 | 8 → 8 | 11.62 → 11.88 | 86 → 88 | 0 → 0 |

## Diff

```diff
diff --git a/gson/src/main/java/com/google/gson/internal/bind/ReflectiveTypeAdapterFactory.java b/gson/src/main/java/com/google/gson/internal/bind/ReflectiveTypeAdapterFactory.java
index bb26de5..5979b7b 100644
--- a/gson/src/main/java/com/google/gson/internal/bind/ReflectiveTypeAdapterFactory.java
+++ b/gson/src/main/java/com/google/gson/internal/bind/ReflectiveTypeAdapterFactory.java
@@ -117,6 +117,12 @@ public final class ReflectiveTypeAdapterFactory implements TypeAdapterFactory {
           raw, getBoundFields(gson, type, raw, blockInaccessible, true), blockInaccessible);
     }
 
+    // If the class is anonymous or a local class, we cannot reflectively instantiate it.
+    // We return null to let other factories handle it or to let Gson skip it.
+    if (raw.isAnonymousClass() || raw.isLocalClass()) {
+      return null;
+    }
+
     ObjectConstructor<T> constructor = constructorConstructor.get(type, true);
     return new FieldReflectionAdapter<>(
         constructor, getBoundFields(gson, type, raw, blockInaccessible, false));

```
