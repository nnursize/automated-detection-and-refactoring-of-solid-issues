# Refactor LSP-015 (LSP): Subclass overrides behavior in a way that breaks the base class contract.

**Status:** `patch_failed`  
**Branch:** `refactor/LSP-015` -> `main`  
**Head commit:** `d7c31619d0f4344c4f802c51dcde02ae3f039a75`  
**LLM finish:** `FinishReason.STOP` (prompt 4065, completion 191)  

## Detected issue

- **File**: `src/requests/auth.py`
- **Entity**: `HTTPProxyAuth.__call__` (method)
- **Lines (at detection time)**: L107–L109
- **Severity**: medium
- **Confidence**: detected by 2 scan(s)

**Description.** Subclass overrides behavior in a way that breaks the base class contract.

**Reasoning.** Refused Bequest smell -> LSP violation because HTTPProxyAuth inherits from HTTPBasicAuth but changes the side effect of the __call__ method. While HTTPBasicAuth is contracted to set the 'Authorization' header, HTTPProxyAuth sets the 'Proxy-Authorization' header instead. A component expecting an HTTPBasicAuth object to authorize a request will find the 'Authorization' header missing if passed an HTTPProxyAuth instance.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `src/requests/auth.py`

**Summary.** Remove inheritance of HTTPProxyAuth from HTTPBasicAuth to resolve LSP violation.

**Rationale.** HTTPProxyAuth was inheriting from HTTPBasicAuth despite having a different behavioral contract (setting 'Proxy-Authorization' instead of 'Authorization'). By having it inherit directly from AuthBase, we maintain the interface while removing the incorrect implication that it is a drop-in replacement for HTTPBasicAuth.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `src/requests/auth.py` (4-line block → 4-line replacement)

**Replaces:**

```python
class HTTPProxyAuth(AuthBase):
    """Attaches HTTP Proxy Authentication to a given Request object."""

    def __init__(self, username, password):
```

**With:**

```python
class HTTPProxyAuth(AuthBase):
    """Attaches HTTP Proxy Authentication to a given Request object."""

    def __init__(self, username, password):
```

## Apply error

```
patch applied but produced no net source changes; the LLM replacement was likely identical to the matched text
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/requests/auth.py` | 220 → - | 19 → - | 2.41 → - | 14 → - | 48.46 → - |

## Diff

*(no diff — patch was not applied)*
