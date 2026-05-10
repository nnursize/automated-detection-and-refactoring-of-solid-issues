# Refactor OCP-020 (OCP): Hardcoded if/elif chain for hashing algorithms

**Status:** `applied_passed`  
**Branch:** `refactor/OCP-020` -> `main`  
**Head commit:** `48be9e2d422554b69de8db2cdf97896fee28f89a`  
**LLM finish:** `FinishReason.STOP` (prompt 4002, completion 461)  

## Detected issue

- **File**: `src/requests/auth.py`
- **Entity**: `HTTPDigestAuth.build_digest_header` (method)
- **Lines (at detection time)**: L154–L182
- **Severity**: high
- **Confidence**: detected by 2 scan(s)

**Description.** Hardcoded if/elif chain for hashing algorithms

**Reasoning.** The method uses a hardcoded conditional chain to select hashing algorithms (MD5, SHA, SHA-256, SHA-512). Adding support for a new algorithm like SHA-3 would require modifying this existing class rather than extending it through a strategy pattern or registry.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `src/requests/auth.py`

**Summary.** Replace hardcoded hashing algorithm chain with a registry-based lookup

**Rationale.** Replaced the if/elif chain in build_digest_header with a dictionary-based registry of hashlib functions. This allows adding new algorithms without modifying the core logic, adhering to the Open/Closed Principle.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `src/requests/auth.py` (22-line block → 14-line replacement)

**Replaces:**

```python
        def get_hash_function(algorithm):
            if algorithm is None:
                algorithm = "MD5"
            else:
                algorithm = algorithm.upper()

            def hash_utf8(x):
                if isinstance(x, str):
                    x = x.encode("utf-8")
                if algorithm == "MD5" or algorithm == "MD5-SESS":
                    return hashlib.md5(x).hexdigest()
                elif algorithm == "SHA":
                    return hashlib.sha1(x).hexdigest()
                elif algorithm == "SHA-256":
                    return hashlib.sha256(x).hexdigest()
                elif algorithm == "SHA-512":
                    return hashlib.sha512(x).hexdigest()
                return None

            return hash_utf8, algorithm

        hash_utf8, _algorithm = get_hash_function(algorithm)
```

**With:**

```python
        _algorithm = (algorithm or "MD5").upper()
        _algorithms = {
            "MD5": hashlib.md5,
            "MD5-SESS": hashlib.md5,
            "SHA": hashlib.sha1,
            "SHA-256": hashlib.sha256,
            "SHA-512": hashlib.sha512,
        }

        def hash_utf8(x):
            if isinstance(x, str):
                x = x.encode("utf-8")
            func = _algorithms.get(_algorithm)
            return func(x).hexdigest() if func else None
```

## Test results

**PASSED** — 606/610 passed, 0 failed, 3 skipped, 0 errored (duration 165651 ms).

Command: `C:\Users\User\Desktop\SDP-Codex\S1-T7-Okeyish\refactor_workspaces\requests\.venv\Scripts\python.exe -m pytest --tb=short -q --no-header -p no:cacheprovider -x --json-report --json-report-file=C:\Users\User\Desktop\SDP-Codex\S1-T7-Okeyish\refactor_workspaces\requests\.pytest_report.json --deselect=tests/test_requests.py::TestPreparingURLs::test_different_connection_pool_for_tls_settings_verify_bundle_unexpired_cert`

<details><summary>Output tail</summary>

```
........................................................................ [ 11%]
........................................................................ [ 23%]
......s.attempting to ignore so the rest of the tests can run
................................................................ [ 35%]
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
606 passed, 3 skipped, 1 deselected, 1 xfailed, 17 warnings in 164.84s (0:02:44)

[stderr]
127.0.0.1 - - [04/May/2026 13:18:18] "GET /get HTTP/1.1" 200 222

```

</details>

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/requests/auth.py` | 214 → 208 | 17 → 16 | 2.58 → 2.63 | 13 → 14 | 48.8 → 50.08 |

## Diff

```diff
diff --git a/src/requests/auth.py b/src/requests/auth.py
index 2664e45..3aa7f83 100644
--- a/src/requests/auth.py
+++ b/src/requests/auth.py
@@ -135,28 +135,20 @@ class HTTPDigestAuth(AuthBase):
         opaque = self._thread_local.chal.get("opaque")
         hash_utf8 = None
 
-        def get_hash_function(algorithm):
-            if algorithm is None:
-                algorithm = "MD5"
-            else:
-                algorithm = algorithm.upper()
-
-            def hash_utf8(x):
-                if isinstance(x, str):
-                    x = x.encode("utf-8")
-                if algorithm == "MD5" or algorithm == "MD5-SESS":
-                    return hashlib.md5(x).hexdigest()
-                elif algorithm == "SHA":
-                    return hashlib.sha1(x).hexdigest()
-                elif algorithm == "SHA-256":
-                    return hashlib.sha256(x).hexdigest()
-                elif algorithm == "SHA-512":
-                    return hashlib.sha512(x).hexdigest()
-                return None
-
-            return hash_utf8, algorithm
-
-        hash_utf8, _algorithm = get_hash_function(algorithm)
+        _algorithm = (algorithm or "MD5").upper()
+        _algorithms = {
+            "MD5": hashlib.md5,
+            "MD5-SESS": hashlib.md5,
+            "SHA": hashlib.sha1,
+            "SHA-256": hashlib.sha256,
+            "SHA-512": hashlib.sha512,
+        }
+
+        def hash_utf8(x):
+            if isinstance(x, str):
+                x = x.encode("utf-8")
+            func = _algorithms.get(_algorithm)
+            return func(x).hexdigest() if func else None
         KD = lambda s, d: hash_utf8(f"{s}:{d}")  # noqa:E731
 
         if hash_utf8 is None:

```
