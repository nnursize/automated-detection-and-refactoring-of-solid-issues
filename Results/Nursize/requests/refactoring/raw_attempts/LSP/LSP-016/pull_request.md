# Refactor LSP-016 (LSP): Subclass nullifies a parent class method by raising NotImplementedError.

**Status:** `applied_passed`  
**Branch:** `refactor/LSP-016` -> `main`  
**Head commit:** `a4079fe260460e0c9d15b7b101b057459323e8f7`  
**LLM finish:** `FinishReason.STOP` (prompt 6081, completion 231)  

## Detected issue

- **File**: `src/requests/cookies.py`
- **Entity**: `MockRequest.add_header` (method)
- **Lines (at detection time)**: L77–L81
- **Severity**: medium
- **Confidence**: detected by 3 scan(s)

**Description.** Subclass nullifies a parent class method by raising NotImplementedError.

**Reasoning.** Refused Bequest smell -> LSP violation because MockRequest explicitly mimics the urllib2.Request interface but raises NotImplementedError for the add_header method. This violates the substitution principle where a subtype (the mock) should be able to stand in for the base type (the real request) without throwing unexpected errors for standard interface methods.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `src/requests/cookies.py`

**Summary.** Implement add_header in MockRequest to satisfy the urllib2.Request interface.

**Rationale.** The MockRequest class was raising NotImplementedError for add_header, which violates the Liskov Substitution Principle by breaking the expected interface contract. Implementing it to use add_unredirected_header ensures the mock behaves as expected by callers of the interface.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `src/requests/cookies.py` (5-line block → 5-line replacement)

**Replaces:**

```python
    def add_header(self, key, val):
        """cookiejar has no legitimate use for this method; add it back if you find one."""
        raise NotImplementedError(
            "Cookie headers should be added with add_unredirected_header()"
        )
```

**With:**

```python
    def add_header(self, key, val):
        """
        This method is required by the urllib2.Request interface.
        """
        self.add_unredirected_header(key, val)
```

## Test results

**PASSED** — 606/610 passed, 0 failed, 3 skipped, 0 errored (duration 165601 ms).

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
606 passed, 3 skipped, 1 deselected, 1 xfailed, 17 warnings in 164.80s (0:02:44)

```

</details>

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/requests/cookies.py` | 439 → 439 | 49 → 49 | 2.38 → 2.38 | 9 → 9 | 39.76 → 39.8 |

## Diff

```diff
diff --git a/src/requests/cookies.py b/src/requests/cookies.py
index f69d0cd..90ed5ba 100644
--- a/src/requests/cookies.py
+++ b/src/requests/cookies.py
@@ -76,10 +76,10 @@ class MockRequest:
         return self._r.headers.get(name, self._new_headers.get(name, default))
 
     def add_header(self, key, val):
-        """cookiejar has no legitimate use for this method; add it back if you find one."""
-        raise NotImplementedError(
-            "Cookie headers should be added with add_unredirected_header()"
-        )
+        """
+        This method is required by the urllib2.Request interface.
+        """
+        self.add_unredirected_header(key, val)
 
     def add_unredirected_header(self, name, value):
         self._new_headers[name] = value

```
