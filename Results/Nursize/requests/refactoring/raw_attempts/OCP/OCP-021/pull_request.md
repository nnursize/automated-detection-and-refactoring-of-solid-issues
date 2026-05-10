# Refactor OCP-021 (OCP): Hardcoded redirection logic based on specific HTTP status codes

**Status:** `applied_passed`  
**Branch:** `refactor/OCP-021` -> `main`  
**Head commit:** `c10fd2c771f7ad0c8cf96898e899625e8f8b66f3`  
**LLM finish:** `FinishReason.STOP` (prompt 8804, completion 597)  

## Detected issue

- **File**: `src/requests/sessions.py`
- **Entity**: `SessionRedirectMixin.rebuild_method` (method)
- **Lines (at detection time)**: L315–L334
- **Severity**: medium
- **Confidence**: detected by 4 scan(s)

**Description.** Hardcoded redirection logic based on specific HTTP status codes

**Reasoning.** This method explicitly checks for status codes (301, 302, 303) to determine when to switch HTTP methods. Adding new redirection behaviors for different status codes requires manual modification of this method instead of using a polymorphic approach.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `src/requests/sessions.py`

**Summary.** Refactor SessionRedirectMixin.rebuild_method to use a registry for redirect method changes

**Rationale.** Replaced hardcoded if/elif chains with a dictionary-based lookup table (REDIRECT_METHOD_MAP) to allow for easier extension of redirection behaviors without modifying the core logic, adhering to the Open/Closed Principle.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `src/requests/sessions.py` (21-line block → 22-line replacement)

**Replaces:**

```python
    def rebuild_method(self, prepared_request, response):
        """When being redirected we may want to change the method of the request
        based on certain specs or browser behavior.
        """
        method = prepared_request.method

        # https://tools.ietf.org/html/rfc7231#section-6.4.4
        if response.status_code == codes.see_other and method != "HEAD":
            method = "GET"

        # Do what the browsers do, despite standards...
        # First, turn 302s into GETs.
        if response.status_code == codes.found and method != "HEAD":
            method = "GET"

        # Second, if a POST is responded to with a 301, turn it into a GET.
        # This bizarre behaviour is explained in Issue 1704.
        if response.status_code == codes.moved and method == "POST":
            method = "GET"

        prepared_request.method = method
```

**With:**

```python
    def rebuild_method(self, prepared_request, response):
        """When being redirected we may want to change the method of the request
        based on certain specs or browser behavior.
        """
        method = prepared_request.method

        # Map of status codes to a set of methods that should be changed to GET
        # or a specific method to change to.
        # https://tools.ietf.org/html/rfc7231#section-6.4.4
        # Issue 1704: 301 POST -> GET
        REDIRECT_METHOD_MAP = {
            codes.see_other: ("GET", lambda m: m != "HEAD"),
            codes.found: ("GET", lambda m: m != "HEAD"),
            codes.moved: ("GET", lambda m: m == "POST"),
        }

        if response.status_code in REDIRECT_METHOD_MAP:
            new_method, condition = REDIRECT_METHOD_MAP[response.status_code]
            if condition(method):
                method = new_method

        prepared_request.method = method
```

## Test results

**PASSED** — 606/610 passed, 0 failed, 3 skipped, 0 errored (duration 165975 ms).

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
606 passed, 3 skipped, 1 deselected, 1 xfailed, 17 warnings in 165.16s (0:02:45)

```

</details>

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/requests/sessions.py` | 566 → 569 | 28 → 28 | 4.07 → 3.93 | 15 → 15 | 38.09 → 38.95 |

## Diff

```diff
diff --git a/src/requests/sessions.py b/src/requests/sessions.py
index 7d34b29..32e8f47 100644
--- a/src/requests/sessions.py
+++ b/src/requests/sessions.py
@@ -337,19 +337,20 @@ class SessionRedirectMixin:
         """
         method = prepared_request.method
 
+        # Map of status codes to a set of methods that should be changed to GET
+        # or a specific method to change to.
         # https://tools.ietf.org/html/rfc7231#section-6.4.4
-        if response.status_code == codes.see_other and method != "HEAD":
-            method = "GET"
-
-        # Do what the browsers do, despite standards...
-        # First, turn 302s into GETs.
-        if response.status_code == codes.found and method != "HEAD":
-            method = "GET"
-
-        # Second, if a POST is responded to with a 301, turn it into a GET.
-        # This bizarre behaviour is explained in Issue 1704.
-        if response.status_code == codes.moved and method == "POST":
-            method = "GET"
+        # Issue 1704: 301 POST -> GET
+        REDIRECT_METHOD_MAP = {
+            codes.see_other: ("GET", lambda m: m != "HEAD"),
+            codes.found: ("GET", lambda m: m != "HEAD"),
+            codes.moved: ("GET", lambda m: m == "POST"),
+        }
+
+        if response.status_code in REDIRECT_METHOD_MAP:
+            new_method, condition = REDIRECT_METHOD_MAP[response.status_code]
+            if condition(method):
+                method = new_method
 
         prepared_request.method = method
 

```
