# Refactor LSP-059 (LSP): Subtype introduces a new precondition by throwing IllegalArgumentException fo...

**Status:** `llm_error`  
**Branch:** `refactor/LSP-059` -> `main`  
**Head commit:** `4b7c6490166c1b426d2880f4209bea8815b0e088`  

## Detected issue

- **File**: `gson/src/main/java/com/google/gson/internal/bind/TypeAdapters.java`
- **Entity**: `TypeAdapters.DoubleAdapter.write` (method)
- **Lines (at detection time)**: L497–L509
- **Severity**: medium
- **Confidence**: detected by 3 scan(s)

**Description.** Subtype introduces a new precondition by throwing IllegalArgumentException for NaN/Infinity values.

**Reasoning.** The TypeAdapter<Number>.write method does not explicitly state a precondition that floating-point numbers must be finite. By throwing an IllegalArgumentException for NaN or Infinity values when 'strict' is true, DoubleAdapter introduces a new precondition that might not be expected by clients using TypeAdapter<Number> polymorphically. While IllegalArgumentException is a RuntimeException and thus doesn't break the method signature, it alters the expected behavior.

## LLM / runtime error

```
unhandled error: FatalLLMError: Server unavailable (503) — skipping to preserve quota: 503 UNAVAILABLE. {'error': {'code': 503, 'message': 'This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.', 'status': 'UNAVAILABLE'}}
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `gson/src/main/java/com/google/gson/internal/bind/TypeAdapters.java` | 836 → - | 72 → - | 2.01 → - | 74 → - | 0 → - |

## Diff

*(no diff — patch was not applied)*
