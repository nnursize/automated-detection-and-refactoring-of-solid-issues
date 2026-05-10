# Refactor ISP-010 (ISP): `RequestsCookieJar` implements `MutableMapping` but its `__setitem__` and `__...

**Status:** `llm_error`  
**Branch:** `refactor/ISP-010` -> `main`  
**Head commit:** `5f58fef93a8fcbe83fabe9dea284cf8fccce1e3d`  

## Detected issue

- **File**: `src/requests/cookies.py`
- **Entity**: `RequestsCookieJar` (class)
- **Lines (at detection time)**: L176–L437
- **Severity**: medium
- **Confidence**: detected by 1 scan(s)

**Description.** `RequestsCookieJar` implements `MutableMapping` but its `__setitem__` and `__delitem__` methods provide an incomplete or overly broad contract for cookie management.

**Reasoning.** `RequestsCookieJar` inherits from `collections.abc.MutableMapping`, requiring it to implement methods like `__setitem__(self, key, value)` and `__delitem__(self, key)`. The `__setitem__` method only allows setting a cookie's `name` and `value`, ignoring other critical cookie attributes like `domain`, `path`, and `expires`. Clients needing to set full cookie attributes are forced to use the more specific `set_cookie` or `set` methods. Similarly, `__delitem__` removes *all* cookies matching the given name, regardless of domain or path, which can be an overly broad operation compared to typical dictionary item deletion and might not be the desired behavior for clients needing to remove a specific cookie instance. This forces clients to depend on an interface (`MutableMapping`) that either provides an incomplete contract (`__setitem__`) or an overly broad operation (`__delitem__`) for cookie management, thus violating ISP by forcing clients to depend on methods they might not fully use or that don't precisely match their needs for granular cookie control.

## LLM / runtime error

```
unhandled error: FatalLLMError: Server unavailable (503) — skipping to preserve quota: 503 UNAVAILABLE. {'error': {'code': 503, 'message': 'This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.', 'status': 'UNAVAILABLE'}}
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/requests/cookies.py` | 436 → - | 48 → - | 2.42 → - | 9 → - | 39.73 → - |

## Diff

*(no diff — patch was not applied)*
