# Refactor ISP-006 (ISP): MockRequest implements 'add_header' method from the urllib2.Request interface...

**Status:** `applied_passed`  
**Branch:** `refactor/ISP-006` -> `main`  
**Head commit:** `5f58fef93a8fcbe83fabe9dea284cf8fccce1e3d`  
**LLM finish:** `FinishReason.STOP` (prompt 6143, completion 218)  

## Detected issue

- **File**: `src/requests/cookies.py`
- **Entity**: `MockRequest.add_header` (method)
- **Lines (at detection time)**: L74–L76
- **Severity**: medium
- **Confidence**: detected by 1 scan(s)

**Description.** MockRequest implements 'add_header' method from the urllib2.Request interface but raises NotImplementedError.

**Reasoning.** The `MockRequest` class is designed to mimic the `urllib2.Request` interface expected by `http.cookiejar.CookieJar`. This interface includes an `add_header` method. However, `MockRequest` explicitly raises `NotImplementedError` for this method, indicating it cannot legitimately fulfill this part of the interface. This forces clients (like `http.cookiejar`) to depend on an interface that `MockRequest` does not fully implement, directly violating the Interface Segregation Principle.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `src/requests/cookies.py`

**Summary.** Remove the NotImplementedError-raising add_header method from MockRequest.

**Rationale.** The MockRequest class is a helper for cookie management. The add_header method is part of the urllib2.Request interface but is not used by the cookiejar logic in this context. Removing it prevents the violation of the Interface Segregation Principle where a class is forced to implement an interface method it cannot support.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `src/requests/cookies.py` (8-line block → 1-line replacement)

**Replaces:**

```python
    def add_header(self, name, value):
        """
        cookiejar has no legitimate use for this method;
        use add_unredirected_header instead.
        """
        raise NotImplementedError("Use add_unredirected_header instead.")

    def add_unredirected_header(self, name, value):
```

**With:**

```python
    def add_unredirected_header(self, name, value):
```

## Test results

**PASSED** — 606/610 passed, 0 failed, 3 skipped, 0 errored (duration 165425 ms).

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
  C:\Users\User\Desktop\SDP-Codex\S1-T7-Okeyish\refactor_workspaces\requests\src\requests\utils.py:477: DeprecationWarning: In requests 3.0, get_encodings_from_content will be removed. For more information, please see the discussion on issue #2266. (This warning should only appear once.)
    warnings.warn(

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
606 passed, 3 skipped, 1 deselected, 1 xfailed, 17 warnings in 164.56s (0:02:44)

[stderr]
127.0.0.1 - - [04/May/2026 14:30:33] "GET /headers HTTP/1.1" 200 195

```

</details>

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/requests/cookies.py` | 442 → 436 | 49 → 48 | 2.4 → 2.42 | 9 → 9 | 39.52 → 39.73 |

## Diff

```diff
diff --git a/src/requests/cookies.py b/src/requests/cookies.py
index 32018d5..2a787ba 100644
--- a/src/requests/cookies.py
+++ b/src/requests/cookies.py
@@ -75,13 +75,6 @@ class MockRequest:
     def get_header(self, name, default=None):
         return self._r.headers.get(name, self._new_headers.get(name, default))
 
-    def add_header(self, name, value):
-        """
-        cookiejar has no legitimate use for this method;
-        use add_unredirected_header instead.
-        """
-        raise NotImplementedError("Use add_unredirected_header instead.")
-
     def add_unredirected_header(self, name, value):
         self._new_headers[name] = value
 

```
