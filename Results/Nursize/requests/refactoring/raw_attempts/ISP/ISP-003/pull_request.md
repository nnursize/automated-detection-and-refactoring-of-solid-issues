# Refactor ISP-003 (ISP): The MockRequest class is forced to implement a method (add_header) from an in...

**Status:** `applied_passed`  
**Branch:** `refactor/ISP-003` -> `main`  
**Head commit:** `2de64a995585a0d6c740cb951d8eee572aa200f6`  
**LLM finish:** `FinishReason.STOP` (prompt 6173, completion 195)  

## Detected issue

- **File**: `src/requests/cookies.py`
- **Entity**: `MockRequest.add_header` (method)
- **Lines (at detection time)**: L62–L64
- **Severity**: high
- **Confidence**: detected by 3 scan(s)

**Description.** The MockRequest class is forced to implement a method (add_header) from an interface it mimics (urllib2.Request) but does not use, explicitly raising NotImplementedError.

**Reasoning.** The MockRequest class is designed to mimic the urllib2.Request interface for compatibility with http.cookiejar.CookieJar. However, the add_header method is explicitly not implemented and raises NotImplementedError, with a comment stating 'cookiejar has no legitimate use for this method; add it back if you find one.' This indicates that the client (CookieJar) expects an interface (urllib2.Request) that is 'fat' for MockRequest's specific purpose. MockRequest only needs add_unredirected_header for its interaction with CookieJar, but is forced to provide add_header, thereby violating the Interface Segregation Principle.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `src/requests/cookies.py`

**Summary.** Remove unused add_header method from MockRequest to adhere to ISP

**Rationale.** The MockRequest class is used by http.cookiejar.CookieJar, which only requires the add_unredirected_header method. The add_header method was previously implemented but not used, violating the Interface Segregation Principle. Removing it cleans up the interface.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `src/requests/cookies.py` (7-line block → 1-line replacement)

**Replaces:**

```python
    def add_header(self, key, val):
        """
        This method is required by the urllib2.Request interface.
        """
        self._new_headers[key] = val

    def add_unredirected_header(self, name, value):
```

**With:**

```python
    def add_unredirected_header(self, name, value):
```

## Test results

**PASSED** — 606/610 passed, 0 failed, 3 skipped, 0 errored (duration 165611 ms).

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
606 passed, 3 skipped, 1 deselected, 1 xfailed, 17 warnings in 164.78s (0:02:44)

[stderr]
127.0.0.1 - - [04/May/2026 14:11:16] "GET /get HTTP/1.1" 200 170
127.0.0.1 - - [04/May/2026 14:11:16] "GET /cookies HTTP/1.1" 200 26

```

</details>

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/requests/cookies.py` | 441 → 436 | 49 → 48 | 2.4 → 2.42 | 9 → 9 | 39.51 → 39.73 |

## Diff

```diff
diff --git a/src/requests/cookies.py b/src/requests/cookies.py
index 4f2fc7c..2a787ba 100644
--- a/src/requests/cookies.py
+++ b/src/requests/cookies.py
@@ -75,12 +75,6 @@ class MockRequest:
     def get_header(self, name, default=None):
         return self._r.headers.get(name, self._new_headers.get(name, default))
 
-    def add_header(self, key, val):
-        """
-        This method is required by the urllib2.Request interface.
-        """
-        self._new_headers[key] = val
-
     def add_unredirected_header(self, name, value):
         self._new_headers[name] = value
 

```
