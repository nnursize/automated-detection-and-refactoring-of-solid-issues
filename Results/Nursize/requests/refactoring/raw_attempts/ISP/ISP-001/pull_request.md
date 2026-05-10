# Refactor ISP-001 (ISP): The MockRequest class is forced to implement add_header but explicitly raises...

**Status:** `patch_failed`  
**Branch:** `refactor/ISP-001` -> `main`  
**Head commit:** `2de64a995585a0d6c740cb951d8eee572aa200f6`  
**LLM finish:** `FinishReason.STOP` (prompt 6105, completion 189)  

## Detected issue

- **File**: `src/requests/cookies.py`
- **Entity**: `MockRequest.add_header` (method)
- **Lines (at detection time)**: L49–L51
- **Severity**: high
- **Confidence**: detected by 2 scan(s)

**Description.** The MockRequest class is forced to implement add_header but explicitly raises NotImplementedError.

**Reasoning.** The `MockRequest` class is designed to mimic the interface of `urllib2.Request` for `http.cookiejar.CookieJar`. However, `MockRequest`'s internal design for handling headers (collecting new headers via `add_unredirected_header`) means it does not legitimately use or need the `add_header` method. By raising `NotImplementedError`, `MockRequest` signals that it is forced to depend on a method from a broader interface (`urllib2.Request`'s expected interface) that is irrelevant to its specific responsibilities, thus violating the Interface Segregation Principle.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `src/requests/cookies.py`

**Summary.** Remove unused add_header method from MockRequest

**Rationale.** The MockRequest class was implementing add_header only to raise NotImplementedError, which violates the Interface Segregation Principle. Since the class manages headers via add_unredirected_header and does not require add_header, removing it cleans up the interface.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `src/requests/cookies.py` (4-line block → 4-line replacement)

**Replaces:**

```python
    def add_unredirected_header(self, name, value):
        self._new_headers[name] = value

    def get_new_headers(self):
```

**With:**

```python
    def add_unredirected_header(self, name, value):
        self._new_headers[name] = value

    def get_new_headers(self):
```

## Apply error

```
patch applied but produced no net source changes; the LLM replacement was likely identical to the matched text
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/requests/cookies.py` | 436 → - | 48 → - | 2.42 → - | 9 → - | 39.73 → - |

## Diff

*(no diff — patch was not applied)*
