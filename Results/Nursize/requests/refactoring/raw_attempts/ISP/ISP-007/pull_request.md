# Refactor ISP-007 (ISP): The `add_headers` method in `HTTPAdapter` has an empty `pass` implementation,...

**Status:** `llm_error`  
**Branch:** `refactor/ISP-007` -> `main`  
**Head commit:** `2de64a995585a0d6c740cb951d8eee572aa200f6`  

## Detected issue

- **File**: `src/requests/adapters.py`
- **Entity**: `HTTPAdapter.add_headers` (class)
- **Lines (at detection time)**: L579–L591
- **Severity**: medium
- **Confidence**: detected by 2 scan(s)

**Description.** The `add_headers` method in `HTTPAdapter` has an empty `pass` implementation, indicating it's not universally needed by subclasses.

**Reasoning.** The Interface Segregation Principle states that clients should not be forced to depend on interfaces they do not use. By providing a `pass` implementation for `add_headers`, `HTTPAdapter` implies this method is part of its interface for subclasses, but it's not universally needed. Subclasses that do not need to add custom headers are still forced to inherit this method, even if they do nothing with it. This method could be extracted into a more specific mixin or interface for adapters that *do* need to add custom headers.

## LLM / runtime error

```
unhandled error: FatalLLMError: Server unavailable (503) — skipping to preserve quota: 503 UNAVAILABLE. {'error': {'code': 503, 'message': 'This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.', 'status': 'UNAVAILABLE'}}
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/requests/adapters.py` | 588 → - | 24 → - | 3.29 → - | 14 → - | 47.37 → - |

## Diff

*(no diff — patch was not applied)*
