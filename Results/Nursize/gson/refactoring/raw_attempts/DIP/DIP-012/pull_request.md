# Refactor DIP-012 (DIP): Base abstraction depends on a concrete subclass implementation detail.

**Status:** `patch_failed`  
**Branch:** `refactor/DIP-012` -> `main`  
**Head commit:** `29fb26dc6739abacd329814707753280ac11a2e7`  
**LLM finish:** `FinishReason.STOP` (prompt 5096, completion 254)  

## Detected issue

- **File**: `gson/src/main/java/com/google/gson/TypeAdapter.java`
- **Entity**: `TypeAdapter.fromJsonTree` (method)
- **Lines (at detection time)**: L183–L190
- **Severity**: medium
- **Confidence**: detected by 4 scan(s)

**Description.** Base abstraction depends on a concrete subclass implementation detail.

**Reasoning.** The abstract class 'TypeAdapter' directly instantiates 'JsonTreeReader', which is a concrete implementation of 'JsonReader' located in an internal package ('internal.bind'). Abstractions should not depend on details; here, the base class is coupled to a specific implementation of the reading logic, making it difficult to change the tree-reading implementation without modifying the base abstraction.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 0

## Apply error

```
no patch blocks produced by LLM
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `gson/src/main/java/com/google/gson/TypeAdapter.java` | 286 → - | 10 → - | 4.2 → - | 33 → - | 0 → - |

## Diff

*(no diff — patch was not applied)*
