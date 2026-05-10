# Refactor LSP-008 (LSP): Subclass modifies a different header than its parent class, breaking expected...

**Status:** `applied_passed`  
**Branch:** `refactor/LSP-008` -> `main`  
**Head commit:** `e96a1330471edbe1f13403a3614cb92ebe18f56a`  
**LLM finish:** `FinishReason.STOP` (prompt 3974, completion 355)  

## Detected issue

- **File**: `src/requests/auth.py`
- **Entity**: `HTTPProxyAuth.__call__` (method)
- **Lines (at detection time)**: L101–L103
- **Severity**: medium
- **Confidence**: detected by 4 scan(s)

**Description.** Subclass modifies a different header than its parent class, breaking expected side effects

**Reasoning.** HTTPProxyAuth inherits from HTTPBasicAuth. While HTTPBasicAuth is expected to set the 'Authorization' header, HTTPProxyAuth overrides the __call__ method to set the 'Proxy-Authorization' header instead. Because it inherits from HTTPBasicAuth rather than AuthBase directly, it fails to fulfill the specific contract of its parent class (setting the standard Auth header), making it non-substitutable in contexts expecting Basic Authentication behavior.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `src/requests/auth.py`

**Summary.** Refactor HTTPProxyAuth to inherit from AuthBase instead of HTTPBasicAuth to resolve LSP violation.

**Rationale.** HTTPProxyAuth was inheriting from HTTPBasicAuth but overriding its behavior to set a different header ('Proxy-Authorization' vs 'Authorization'). This violates the Liskov Substitution Principle as it breaks the contract of the parent class. By inheriting directly from AuthBase, we maintain the same interface while correctly separating the concerns.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `src/requests/auth.py` (6-line block → 21-line replacement)

**Replaces:**

```python
class HTTPProxyAuth(HTTPBasicAuth):
    """Attaches HTTP Proxy Authentication to a given Request object."""

    def __call__(self, r):
        r.headers["Proxy-Authorization"] = _basic_auth_str(self.username, self.password)
        return r
```

**With:**

```python
class HTTPProxyAuth(AuthBase):
    """Attaches HTTP Proxy Authentication to a given Request object."""

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __eq__(self, other):
        return all(
            [
                self.username == getattr(other, "username", None),
                self.password == getattr(other, "password", None),
            ]
        )

    def __ne__(self, other):
        return not self == other

    def __call__(self, r):
        r.headers["Proxy-Authorization"] = _basic_auth_str(self.username, self.password)
        return r
```

## Test results

**PASSED** — 606/610 passed, 0 failed, 3 skipped, 0 errored (duration 165203 ms).

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
606 passed, 3 skipped, 1 deselected, 1 xfailed, 17 warnings in 164.37s (0:02:44)

```

</details>

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/requests/auth.py` | 208 → 220 | 16 → 19 | 2.63 → 2.41 | 14 → 14 | 50.08 → 48.46 |

## Diff

```diff
diff --git a/src/requests/auth.py b/src/requests/auth.py
index 3aa7f83..4b277b9 100644
--- a/src/requests/auth.py
+++ b/src/requests/auth.py
@@ -96,9 +96,24 @@ class HTTPBasicAuth(AuthBase):
         return r
 
 
-class HTTPProxyAuth(HTTPBasicAuth):
+class HTTPProxyAuth(AuthBase):
     """Attaches HTTP Proxy Authentication to a given Request object."""
 
+    def __init__(self, username, password):
+        self.username = username
+        self.password = password
+
+    def __eq__(self, other):
+        return all(
+            [
+                self.username == getattr(other, "username", None),
+                self.password == getattr(other, "password", None),
+            ]
+        )
+
+    def __ne__(self, other):
+        return not self == other
+
     def __call__(self, r):
         r.headers["Proxy-Authorization"] = _basic_auth_str(self.username, self.password)
         return r

```
