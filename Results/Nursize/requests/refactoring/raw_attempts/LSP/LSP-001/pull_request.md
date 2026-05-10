# Refactor LSP-001 (LSP): Subclass method returns None instead of raising KeyError for missing keys.

**Status:** `llm_error`  
**Branch:** `refactor/LSP-001` -> `main`  
**Head commit:** `d7c31619d0f4344c4f802c51dcde02ae3f039a75`  

## Detected issue

- **File**: `src/requests/structures.py`
- **Entity**: `LookupDict.__getitem__` (class)
- **Lines (at detection time)**: L101–L104
- **Severity**: high
- **Confidence**: detected by 2 scan(s)

**Description.** Subclass method returns None instead of raising KeyError for missing keys.

**Reasoning.** LookupDict inherits from the built-in dict. The contract for dict.__getitem__ is to raise a KeyError when a key is not found. LookupDict overrides this to return None, which breaks the expectations of any code using it as a standard dictionary substitute, potentially leading to AttributeError or silent failures elsewhere.

## LLM / runtime error

```
unhandled error: FatalLLMError: Server unavailable (503) — skipping to preserve quota: 503 UNAVAILABLE. {'error': {'code': 503, 'message': 'This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.', 'status': 'UNAVAILABLE'}}
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/requests/structures.py` | 67 → - | 14 → - | 1.38 → - | 2 → - | 81.77 → - |

## Diff

*(no diff — patch was not applied)*
