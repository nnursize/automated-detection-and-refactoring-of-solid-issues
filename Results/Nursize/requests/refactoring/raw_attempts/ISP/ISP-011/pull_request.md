# Refactor ISP-011 (ISP): The Response class presents a broad API combining multiple concerns like cont...

**Status:** `applied_passed`  
**Branch:** `refactor/ISP-011` -> `main`  
**Head commit:** `b69752944cb8fd517f087ba0a9729e95aafbea76`  
**LLM finish:** `FinishReason.STOP` (prompt 10076, completion 333)  

## Detected issue

- **File**: `src/requests/models.py`
- **Entity**: `Response` (class)
- **Lines (at detection time)**: L642–L1041
- **Severity**: medium
- **Confidence**: detected by 1 scan(s)

**Description.** The Response class presents a broad API combining multiple concerns like content access, status checking, and resource management.

**Reasoning.** The Response class includes methods for various client needs (e.g., `iter_content` for streaming, `json` for JSON parsing, `ok` for status, `close` for resource management). Clients interacting with a Response object are forced to depend on the entire broad interface, even if they only require a subset of its functionalities (e.g., only checking status or only streaming content). This suggests the API could be segregated into more role-specific interfaces (e.g., IResponseStatus, IResponseContent, IResponseResource) to allow clients to depend only on what they use.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `src/requests/models.py`

**Summary.** Segregate Response interface into smaller, role-specific protocols

**Rationale.** The Response class is a 'fat' interface. By introducing Protocols (IResponseStatus, IResponseContent, IResponseResource), we allow clients to depend on specific capabilities (e.g., just checking status or just accessing content) rather than the entire Response object, adhering to the Interface Segregation Principle.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `src/requests/models.py` (6-line block → 25-line replacement)

**Replaces:**

```python
class Response:
    """The :class:`Response <Response>` object, which contains a
    server's response to an HTTP request.
    """

    __attrs__ = [
```

**With:**

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class IResponseStatus(Protocol):
    status_code: int
    ok: bool
    def raise_for_status(self) -> None: ...

@runtime_checkable
class IResponseContent(Protocol):
    content: bytes
    text: str
    def json(self, **kwargs): ...
    def iter_content(self, chunk_size=1, decode_unicode=False): ...

@runtime_checkable
class IResponseResource(Protocol):
    def close(self) -> None: ...

class Response:
    """The :class:`Response <Response>` object, which contains a
    server's response to an HTTP request.
    """

    __attrs__ = [
```

## Test results

**PASSED** — 606/610 passed, 0 failed, 3 skipped, 0 errored (duration 165056 ms).

Command: `C:\Users\User\Desktop\SDP-Codex\S1-T7-Okeyish\refactor_workspaces\requests\.venv\Scripts\python.exe -m pytest --tb=short -q --no-header -p no:cacheprovider -x --json-report --json-report-file=C:\Users\User\Desktop\SDP-Codex\S1-T7-Okeyish\refactor_workspaces\requests\.pytest_report.json --deselect=tests/test_requests.py::TestPreparingURLs::test_different_connection_pool_for_tls_settings_verify_bundle_unexpired_cert`

<details><summary>Output tail</summary>

```
........................................................................ [ 11%]
........................................................................ [ 23%]
......spytest-httpbin server hit an exception serving request: [SSL: TLSV1_ALERT_UNKNOWN_CA] tlsv1 alert unknown ca (_ssl.c:1006)
attempting to ignore so the rest of the tests can run
................................................................. [ 35%]
...............................................x........................ [ 47%]
........................................................................ [ 59%]
...........................s......s..................................... [ 70%]
........................................................................ [ 82%]
........................................................................ [ 94%]
..................................                                       [100%]
============================== warnings summary ===============================
tests/test_requests.py::TestRequests::test_set_basicauth[42-42]
tests/test_requests.py::TestRequests::test_set_basicauth[42-42]
  C:\Users\User\Desktop\SDP-Codex\S1-T7-Okeyish\refactor_workspaces\requests\src\requests\auth.py:36: DeprecationWarning: Non-string usernames will no longer be supported in Requests 3.0.0. Please convert the object you've passed in (42) to a string or bytes object in the near future to avoid problems.
    warnings.warn(

tests/test_requests.py::TestRequests::test_set_basicauth[42-42]
tests/test_requests.py::TestRequests::test_set_basicauth[42-42]
  C:\Users\User\Desktop\SDP-Codex\S1-T7-Okeyish\refactor_workspaces\requests\src\requests\auth.py:46: DeprecationWarning: Non-string passwords will no longer be supported in Requests 3.0.0. Please convert the object you've passed in (<class 'int'>) to a string or bytes object in the near future to avoid problems.
    warnings.warn(

tests/test_requests.py::TestRequests::test_set_basicauth[None-None]
tests/test_requests.py::TestRequests::test_set_basicauth[None-None]
  C:\Users\User\Desktop\SDP-Codex\S1-T7-Okeyish\refactor_workspaces\requests\src\requests\auth.py:36: DeprecationWarning: Non-string usernames will no longer be supported in Requests 3.0.0. Please convert the object you've passed in (None) to a string or bytes object in the near future to avoid problems.
    warnings.warn(

tests/test_requests.py::TestRequests::test_set_basicauth[None-None]
tests/test_requests.py::TestRequests::test_set_basicauth[None-None]
  C:\Users\User\Desktop\SDP-Codex\S1-T7-Okeyish\refactor_workspaces\requests\src\requests\auth.py:46: DeprecationWarning: Non-string passwords will no longer be supported in Requests 3.0.0. Please convert the object you've passed in (<class 'NoneType'>) to a string or bytes object in the near future to avoid problems.
    warnings.warn(

tests/test_requests.py::TestPreparingURLs::test_different_connection_pool_for_tls_settings_verify_True
tests/test_requests.py::TestPreparingURLs::test_different_connection_pool_for_tls_settings_verify_bundle_expired_cert
tests/test_requests.py::TestPreparingURLs::test_different_connection_pool_for_mtls_settings
  C:\Users\User\Desktop\SDP-Codex\S1-T7-Okeyish\refactor_workspaces\requests\.venv\Lib\site-packages\urllib3\connectionpool.py:1097: InsecureRequestWarning: Unverified HTTPS request is being made to host 'localhost'. Adding certificate verification is strongly advised. See: https://urllib3.readthedocs.io/en/latest/advanced-usage.html#tls-warnings
    warnings.warn(

tests/test_utils.py::TestContentEncodingDetection::test_none
tests/test_utils.py::TestContentEncodingDetection::test_pragmas[<meta charset="UTF-8">]
tests/test_utils.py::TestContentEncodingDetection::test_pragmas[<meta http-equiv="Content-type" content="text/html;charset=UTF-8">]
tests/test_utils.py::TestContentEncodingDetection::test_pragmas[<meta http-equiv="Content-type" content="text/html;charset=UTF-8" />]
tests/test_utils.py::TestContentEncodingDetection::test_pragmas[<?xml version="1.0" encoding="UTF-8"?>]
tests/test_utils.py::TestContentEncodingDetection::test_precedence
  C:\Users\User\Desktop\SDP-Codex\S1-T7-Okeyish\refactor_workspaces\requests\src\requests\utils.py:477: DeprecationWarning: In requests 3.0, get_encodings_from_content will be removed. For more information, please see the discussion on issue #2266. (This warning should only appear once.)
    warnings.warn(

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
606 passed, 3 skipped, 1 deselected, 1 xfailed, 17 warnings in 164.12s (0:02:44)

```

</details>

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/requests/models.py` | 748 → 763 | 47 → 51 | 4.2 → 3.86 | 19 → 19 | 21.45 → 20.36 |

## Diff

```diff
diff --git a/src/requests/models.py b/src/requests/models.py
index 50a372b..5d97b63 100644
--- a/src/requests/models.py
+++ b/src/requests/models.py
@@ -633,6 +633,25 @@ class PreparedRequest(RequestEncodingMixin, RequestHooksMixin):
             self.register_hook(event, hooks[event])
 
 
+from typing import Protocol, runtime_checkable
+
+@runtime_checkable
+class IResponseStatus(Protocol):
+    status_code: int
+    ok: bool
+    def raise_for_status(self) -> None: ...
+
+@runtime_checkable
+class IResponseContent(Protocol):
+    content: bytes
+    text: str
+    def json(self, **kwargs): ...
+    def iter_content(self, chunk_size=1, decode_unicode=False): ...
+
+@runtime_checkable
+class IResponseResource(Protocol):
+    def close(self) -> None: ...
+
 class Response:
     """The :class:`Response <Response>` object, which contains a
     server's response to an HTTP request.

```
