# Refactor LSP-010 (LSP): HTTPProxyAuth inherits from HTTPBasicAuth but modifies a different header, br...

**Status:** `patch_failed`  
**Branch:** `refactor/LSP-010` -> `main`  
**Head commit:** `d7c31619d0f4344c4f802c51dcde02ae3f039a75`  
**LLM finish:** `FinishReason.STOP` (prompt 4068, completion 181)  

## Detected issue

- **File**: `src/requests/auth.py`
- **Entity**: `HTTPProxyAuth` (class)
- **Lines (at detection time)**: L93–L98
- **Severity**: medium
- **Confidence**: detected by 2 scan(s)

**Description.** HTTPProxyAuth inherits from HTTPBasicAuth but modifies a different header, breaking behavioral substitution.

**Reasoning.** HTTPProxyAuth inherits from HTTPBasicAuth but overrides the '__call__' method to modify the 'Proxy-Authorization' header instead of the 'Authorization' header. This violates LSP because HTTPProxyAuth is not a valid behavioral substitute for HTTPBasicAuth; any calling code expecting the parent's contract (applying Basic credentials to the 'Authorization' header) will find that the expected header is missing when an HTTPProxyAuth instance is used.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `src/requests/auth.py`

**Summary.** Remove inheritance from HTTPBasicAuth for HTTPProxyAuth to fix LSP violation

**Rationale.** HTTPProxyAuth was inheriting from HTTPBasicAuth despite having different behavioral requirements (modifying 'Proxy-Authorization' instead of 'Authorization'). By changing the base class to AuthBase, we maintain the interface contract while removing the incorrect inheritance relationship.

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
