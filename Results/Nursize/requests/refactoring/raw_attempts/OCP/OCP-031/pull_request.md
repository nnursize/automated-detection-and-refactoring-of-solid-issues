# Refactor OCP-031 (OCP): Chain of isinstance checks for exception mapping

**Status:** `applied_passed`  
**Branch:** `refactor/OCP-031` -> `main`  
**Head commit:** `72a89cf498ed13d5ada86739ea1ec7a4c42408fe`  
**LLM finish:** `FinishReason.STOP` (prompt 7974, completion 718)  

## Detected issue

- **File**: `src/requests/adapters.py`
- **Entity**: `HTTPAdapter.send` (class)
- **Lines (at detection time)**: L670–L696
- **Severity**: medium
- **Confidence**: detected by 3 scan(s)

**Description.** Chain of isinstance checks for exception mapping

**Reasoning.** The exception handling block in the 'send' method uses a long chain of 'isinstance' checks to map internal urllib3 exceptions to Requests-specific exceptions. Adding support for new exception types from the underlying library or changing the mapping logic requires modifying the 'send' method directly.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `src/requests/adapters.py`

**Summary.** Refactor exception handling in HTTPAdapter to use a mapping dictionary instead of if/elif chains.

**Rationale.** Replaced the procedural if/elif chain in _handle_exception with a declarative dictionary mapping. This allows for easier extension of exception handling without modifying the logic flow, adhering to the Open/Closed Principle.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `src/requests/adapters.py` (37-line block → 28-line replacement)

**Replaces:**

```python
    def _handle_exception(self, request, e):
        """Handles exceptions thrown by urllib3 during a request."""
        if isinstance(e, (ProtocolError, OSError, ClosedPoolError)):
            raise ConnectionError(e, request=request)

        if isinstance(e, MaxRetryError):
            if isinstance(e.reason, ConnectTimeoutError):
                # TODO: Remove this in 3.0.0: see #2811
                if not isinstance(e.reason, NewConnectionError):
                    raise ConnectTimeout(e, request=request)

            if isinstance(e.reason, ResponseError):
                raise RetryError(e, request=request)

            if isinstance(e.reason, _ProxyError):
                raise ProxyError(e, request=request)

            if isinstance(e.reason, _SSLError):
                # This branch is for urllib3 v1.22 and later.
                raise SSLError(e, request=request)

            raise ConnectionError(e, request=request)

        if isinstance(e, _ProxyError):
            raise ProxyError(e)

        if isinstance(e, _SSLError):
            # This branch is for urllib3 versions earlier than v1.22
            raise SSLError(e, request=request)

        if isinstance(e, ReadTimeoutError):
            raise ReadTimeout(e, request=request)

        if isinstance(e, _InvalidHeader):
            raise InvalidHeader(e, request=request)

        raise e
```

**With:**

```python
    def _handle_exception(self, request, e):
        """Handles exceptions thrown by urllib3 during a request."""
        if isinstance(e, MaxRetryError):
            if isinstance(e.reason, ConnectTimeoutError) and not isinstance(
                e.reason, NewConnectionError
            ):
                raise ConnectTimeout(e, request=request)
            if isinstance(e.reason, ResponseError):
                raise RetryError(e, request=request)
            if isinstance(e.reason, _ProxyError):
                raise ProxyError(e, request=request)
            if isinstance(e.reason, _SSLError):
                raise SSLError(e, request=request)
            raise ConnectionError(e, request=request)

        exception_mapping = {
            (ProtocolError, OSError, ClosedPoolError): ConnectionError,
            _ProxyError: ProxyError,
            _SSLError: SSLError,
            ReadTimeoutError: ReadTimeout,
            _InvalidHeader: InvalidHeader,
        }

        for exc_types, target_exc in exception_mapping.items():
            if isinstance(e, exc_types):
                raise target_exc(e, request=request)

        raise e
```

## Test results

**PASSED** — 606/610 passed, 0 failed, 3 skipped, 0 errored (duration 165502 ms).

Command: `C:\Users\User\Desktop\SDP-Codex\S1-T7-Okeyish\refactor_workspaces\requests\.venv\Scripts\python.exe -m pytest --tb=short -q --no-header -p no:cacheprovider -x --json-report --json-report-file=C:\Users\User\Desktop\SDP-Codex\S1-T7-Okeyish\refactor_workspaces\requests\.pytest_report.json --deselect=tests/test_requests.py::TestPreparingURLs::test_different_connection_pool_for_tls_settings_verify_bundle_unexpired_cert`

<details><summary>Output tail</summary>

```
........................................................................ [ 11%]
........................................................................ [ 23%]
......sattempting to ignore so the rest of the tests can run
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
  C:\Users\User\Desktop\SDP-Codex\S1-T7-Okeyish\refactor_workspaces\requests\src\requests\utils.py:478: DeprecationWarning: In requests 3.0, get_encodings_from_content will be removed. For more information, please see the discussion on issue #2266. (This warning should only appear once.)
    warnings.warn(

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
606 passed, 3 skipped, 1 deselected, 1 xfailed, 17 warnings in 164.67s (0:02:44)

[stderr]
127.0.0.1 - - [04/May/2026 13:15:25] "GET /redirect-to?url=http%3A%2F%2F%3A1 HTTP/1.1" 302 0

```

</details>

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/requests/adapters.py` | 587 → 588 | 24 → 24 | 3.42 → 3.29 | 14 → 14 | 46.92 → 47.37 |

## Diff

```diff
diff --git a/src/requests/adapters.py b/src/requests/adapters.py
index e72309e..d049183 100644
--- a/src/requests/adapters.py
+++ b/src/requests/adapters.py
@@ -608,39 +608,30 @@ class HTTPAdapter(BaseAdapter):
 
     def _handle_exception(self, request, e):
         """Handles exceptions thrown by urllib3 during a request."""
-        if isinstance(e, (ProtocolError, OSError, ClosedPoolError)):
-            raise ConnectionError(e, request=request)
-
         if isinstance(e, MaxRetryError):
-            if isinstance(e.reason, ConnectTimeoutError):
-                # TODO: Remove this in 3.0.0: see #2811
-                if not isinstance(e.reason, NewConnectionError):
-                    raise ConnectTimeout(e, request=request)
-
+            if isinstance(e.reason, ConnectTimeoutError) and not isinstance(
+                e.reason, NewConnectionError
+            ):
+                raise ConnectTimeout(e, request=request)
             if isinstance(e.reason, ResponseError):
                 raise RetryError(e, request=request)
-
             if isinstance(e.reason, _ProxyError):
                 raise ProxyError(e, request=request)
-
             if isinstance(e.reason, _SSLError):
-                # This branch is for urllib3 v1.22 and later.
                 raise SSLError(e, request=request)
-
             raise ConnectionError(e, request=request)
 
-        if isinstance(e, _ProxyError):
-            raise ProxyError(e)
-
-        if isinstance(e, _SSLError):
-            # This branch is for urllib3 versions earlier than v1.22
-            raise SSLError(e, request=request)
-
-        if isinstance(e, ReadTimeoutError):
-            raise ReadTimeout(e, request=request)
+        exception_mapping = {
+            (ProtocolError, OSError, ClosedPoolError): ConnectionError,
+            _ProxyError: ProxyError,
+            _SSLError: SSLError,
+            ReadTimeoutError: ReadTimeout,
+            _InvalidHeader: InvalidHeader,
+        }
 
-        if isinstance(e, _InvalidHeader):
-            raise InvalidHeader(e, request=request)
+        for exc_types, target_exc in exception_mapping.items():
+            if isinstance(e, exc_types):
+                raise target_exc(e, request=request)
 
         raise e
 

```
