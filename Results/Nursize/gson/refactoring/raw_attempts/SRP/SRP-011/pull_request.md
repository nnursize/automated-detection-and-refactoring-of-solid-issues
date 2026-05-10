# Refactor SRP-011 (SRP): The JsonArray class manages a collection of JsonElements and also provides a...

**Status:** `patch_failed`  
**Branch:** `refactor/SRP-011` -> `main`  
**Head commit:** `c2bbd3bd54efd9770303fde6d241738326997470`  
**LLM finish:** `FinishReason.STOP` (prompt 5722, completion 1766)  

## Detected issue

- **File**: `gson/src/main/java/com/google/gson/JsonArray.java`
- **Entity**: `JsonArray` (class)
- **Lines (at detection time)**: L29–L297
- **Severity**: medium
- **Confidence**: detected by 5 scan(s)

**Description.** The JsonArray class manages a collection of JsonElements and also provides a comprehensive API for converting a single element within itself to various primitive types.

**Reasoning.** This class exhibits a 'Divergent Change' smell. Its primary responsibility is to represent and manage an ordered list of `JsonElement`s (collection management via `add`, `remove`, `size`, `iterator`). However, it also provides a large number of `getAs...` methods (e.g., `getAsNumber`, `getAsString`, `getAsDouble`) specifically designed to convert the *single* element of the array into a primitive type. These methods throw an `IllegalStateException` if the array does not contain exactly one element, highlighting that this is a distinct 'single-element conversion' responsibility, separate from its role as a general collection.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 0

**Summary.** Remove single-element conversion methods from JsonArray to enforce SRP

**Rationale.** The JsonArray class was violating the Single Responsibility Principle by acting as both a collection and a single-element converter. The 'getAs...' methods were removed as they are conceptually incompatible with an array structure and were only intended for single-element arrays, which is a misuse of the collection type.

## Apply error

```
no patch blocks produced by LLM
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `gson/src/main/java/com/google/gson/JsonArray.java` | 400 → - | 31 → - | 2.87 → - | 59 → - | 0 → - |

## Diff

*(no diff — patch was not applied)*
