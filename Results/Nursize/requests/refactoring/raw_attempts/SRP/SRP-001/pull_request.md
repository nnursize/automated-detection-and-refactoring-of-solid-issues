# Refactor SRP-001 (SRP): Combines multiple strategies for determining content length and issues warnings.

**Status:** `llm_error`  
**Branch:** `refactor/SRP-001` -> `main`  
**Head commit:** `fbbb51ee88d79384e571ee7f04ba1b13f1b954a9`  

## Detected issue

- **File**: `src/requests/utils.py`
- **Entity**: `super_len` (method)
- **Lines (at detection time)**: L98–L160
- **Severity**: high
- **Confidence**: detected by 3 scan(s)

**Description.** Combines multiple strategies for determining content length and issues warnings.

**Reasoning.** This function has several reasons to change: 1) Changes in how length is determined for different object types (e.g., `__len__`, `len` attribute, `fileno`, `tell`/`seek`). 2) Changes in `urllib3` string handling. 3) Changes in warning policies (e.g., `FileModeWarning`). 4) Changes in error handling for `tell()` on special file descriptors. These are distinct concerns that could evolve independently.

## LLM / runtime error

```
unhandled error: FatalLLMError: Server unavailable (503) — skipping to preserve quota: 503 UNAVAILABLE. {'error': {'code': 503, 'message': 'This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.', 'status': 'UNAVAILABLE'}}
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/requests/utils.py` | 769 → - | 43 → - | 4.55 → - | 18 → - | 25.21 → - |

## Diff

*(no diff — patch was not applied)*
