# Refactor DIP-003 (DIP): High-level Request object directly instantiates a concrete PreparedRequest.

**Status:** `applied_passed`  
**Branch:** `refactor/DIP-003` -> `main`  
**Head commit:** `f3b44f9283ed3f26a9bfb8c8a3acf3b8f9095e77`  
**LLM finish:** `FinishReason.STOP` (prompt 10195, completion 235)  

## Detected issue

- **File**: `src/requests/models.py`
- **Entity**: `Request.prepare` (method)
- **Lines (at detection time)**: L130–L130
- **Severity**: high
- **Confidence**: detected by 8 scan(s)

**Description.** High-level Request object directly instantiates a concrete PreparedRequest.

**Reasoning.** The `Request` class, representing a user's high-level HTTP request, directly instantiates `PreparedRequest` within its `prepare` method. This creates a tight coupling between the abstract concept of a `Request` and the concrete implementation of how it is prepared for transmission. DIP suggests that `Request` should depend on an abstraction for request preparation (e.g., an `IRequestPreparer` interface) rather than a concrete `PreparedRequest` class, allowing for more flexible and testable preparation strategies.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `src/requests/models.py`

**Summary.** Inject PreparedRequest class into Request.prepare to decouple instantiation

**Rationale.** By allowing the PreparedRequest class to be passed as an argument (with a default value), we invert the dependency, allowing for easier testing and substitution of the preparation logic without hard-coding the concrete class inside the Request object.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `src/requests/models.py` (5-line block → 8-line replacement)

**Replaces:**

```python
    def prepare(self):
        """Constructs a :class:`PreparedRequest <PreparedRequest>` for transmission and returns it."""
        p = PreparedRequest()
        p.prepare(
            method=self.method,
```

**With:**

```python
    def prepare(self, prepared_request_class=None):
        """Constructs a :class:`PreparedRequest <PreparedRequest>` for transmission and returns it."""
        if prepared_request_class is None:
            prepared_request_class = PreparedRequest

        p = prepared_request_class()
        p.prepare(
            method=self.method,
```

## Test results

**PASSED** — 606/610 passed, 0 failed, 3 skipped, 0 errored (duration 165662 ms).

Command: `C:\Users\User\Desktop\SDP-Codex\S1-T7-Okeyish\refactor_workspaces\requests\.venv\Scripts\python.exe -m pytest --tb=short -q --no-header -p no:cacheprovider -x --json-report --json-report-file=C:\Users\User\Desktop\SDP-Codex\S1-T7-Okeyish\refactor_workspaces\requests\.pytest_report.json --deselect=tests/test_requests.py::TestPreparingURLs::test_different_connection_pool_for_tls_settings_verify_bundle_unexpired_cert`

<details><summary>Output tail</summary>

```
........................................................................ [ 11%]
........................................................................ [ 23%]
......spytest-httpbin server hit an exception serving request: [WinError 10054] An existing connection was forcibly closed by the remote host
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
606 passed, 3 skipped, 1 deselected, 1 xfailed, 17 warnings in 164.84s (0:02:44)

```

</details>

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/requests/models.py` | 763 → 765 | 51 → 51 | 3.86 → 3.88 | 19 → 19 | 20.36 → 20.13 |

## Diff

```diff
diff --git a/src/requests/models.py b/src/requests/models.py
index 5d97b63..9d14d8c 100644
--- a/src/requests/models.py
+++ b/src/requests/models.py
@@ -301,9 +301,12 @@ class Request(RegisterOnlyHooksMixin):
     def __repr__(self):
         return f"<Request [{self.method}]>"
 
-    def prepare(self):
+    def prepare(self, prepared_request_class=None):
         """Constructs a :class:`PreparedRequest <PreparedRequest>` for transmission and returns it."""
-        p = PreparedRequest()
+        if prepared_request_class is None:
+            prepared_request_class = PreparedRequest
+
+        p = prepared_request_class()
         p.prepare(
             method=self.method,
             url=self.url,

```
