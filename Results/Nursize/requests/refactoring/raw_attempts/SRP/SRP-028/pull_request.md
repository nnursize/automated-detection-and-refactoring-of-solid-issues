# Refactor SRP-028 (SRP): Implements the full HTTP Digest Authentication header construction logic, inc...

**Status:** `applied_passed`  
**Branch:** `refactor/SRP-028` -> `main`  
**Head commit:** `fbbb51ee88d79384e571ee7f04ba1b13f1b954a9`  
**LLM finish:** `FinishReason.STOP` (prompt 4233, completion 724)  

## Detected issue

- **File**: `src/requests/auth.py`
- **Entity**: `HTTPDigestAuth.build_digest_header` (method)
- **Lines (at detection time)**: L78–L160
- **Severity**: high
- **Confidence**: detected by 3 scan(s)

**Description.** Implements the full HTTP Digest Authentication header construction logic, including hash function selection, nonce/cnonce/qop calculations, and header formatting.

**Reasoning.** This is a 'god method' that encapsulates the entire RFC 2617 Digest Authentication header construction. Its responsibilities include: 1) Extracting various parameters (realm, nonce, qop, algorithm, opaque) from `self._thread_local.chal`. 2) Dynamically selecting the appropriate hash function (MD5, SHA, SHA-256, SHA-512). 3) Performing complex cryptographic calculations for `HA1`, `HA2`, `respdig` involving nonce, cnonce, and qop. 4) Formatting the final `Digest` header string with all its components. Any change in the Digest Auth specification, supported algorithms, or calculation methods would require extensive modification to this single function.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `src/requests/auth.py`

**Summary.** Extract Digest Auth header construction logic into a helper function to improve SRP.

**Rationale.** The build_digest_header method was doing too much: algorithm selection, cryptographic calculations, and string formatting. By extracting the algorithm selection and hashing logic into a helper function, we separate the concerns of 'how to hash' from 'how to build the header'.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `src/requests/auth.py` (39-line block → 23-line replacement)

**Replaces:**

```python
        if algorithm is None:
            _algorithm = "MD5"
        else:
            _algorithm = algorithm.upper()
        # lambdas assume digest modules are imported at the top level
        if _algorithm == "MD5" or _algorithm == "MD5-SESS":

            def md5_utf8(x):
                if isinstance(x, str):
                    x = x.encode("utf-8")
                return hashlib.md5(x).hexdigest()

            hash_utf8 = md5_utf8
        elif _algorithm == "SHA":

            def sha_utf8(x):
                if isinstance(x, str):
                    x = x.encode("utf-8")
                return hashlib.sha1(x).hexdigest()

            hash_utf8 = sha_utf8
        elif _algorithm == "SHA-256":

            def sha256_utf8(x):
                if isinstance(x, str):
                    x = x.encode("utf-8")
                return hashlib.sha256(x).hexdigest()

            hash_utf8 = sha256_utf8
        elif _algorithm == "SHA-512":

            def sha512_utf8(x):
                if isinstance(x, str):
                    x = x.encode("utf-8")
                return hashlib.sha512(x).hexdigest()

            hash_utf8 = sha512_utf8

        KD = lambda s, d: hash_utf8(f"{s}:{d}")  # noqa:E731
```

**With:**

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
        KD = lambda s, d: hash_utf8(f"{s}:{d}")  # noqa:E731
```

## Test results

**PASSED** — 606/610 passed, 0 failed, 3 skipped, 0 errored (duration 165954 ms).

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
  C:\Users\User\Desktop\SDP-Codex\S1-T7-Okeyish\refactor_workspaces\requests\src\requests\utils.py:482: DeprecationWarning: In requests 3.0, get_encodings_from_content will be removed. For more information, please see the discussion on issue #2266. (This warning should only appear once.)
    warnings.warn(

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
606 passed, 3 skipped, 1 deselected, 1 xfailed, 17 warnings in 165.21s (0:02:45)

[stderr]
127.0.0.1 - - [04/May/2026 12:43:57] "GET /get HTTP/1.1" 200 222

```

</details>

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/requests/auth.py` | 223 → 214 | 19 → 17 | 2.95 → 2.58 | 19 → 13 | 47.4 → 48.8 |

## Diff

```diff
diff --git a/src/requests/auth.py b/src/requests/auth.py
index c39b645..2664e45 100644
--- a/src/requests/auth.py
+++ b/src/requests/auth.py
@@ -135,44 +135,28 @@ class HTTPDigestAuth(AuthBase):
         opaque = self._thread_local.chal.get("opaque")
         hash_utf8 = None
 
-        if algorithm is None:
-            _algorithm = "MD5"
-        else:
-            _algorithm = algorithm.upper()
-        # lambdas assume digest modules are imported at the top level
-        if _algorithm == "MD5" or _algorithm == "MD5-SESS":
-
-            def md5_utf8(x):
-                if isinstance(x, str):
-                    x = x.encode("utf-8")
-                return hashlib.md5(x).hexdigest()
+        def get_hash_function(algorithm):
+            if algorithm is None:
+                algorithm = "MD5"
+            else:
+                algorithm = algorithm.upper()
 
-            hash_utf8 = md5_utf8
-        elif _algorithm == "SHA":
-
-            def sha_utf8(x):
+            def hash_utf8(x):
                 if isinstance(x, str):
                     x = x.encode("utf-8")
-                return hashlib.sha1(x).hexdigest()
-
-            hash_utf8 = sha_utf8
-        elif _algorithm == "SHA-256":
-
-            def sha256_utf8(x):
-                if isinstance(x, str):
-                    x = x.encode("utf-8")
-                return hashlib.sha256(x).hexdigest()
-
-            hash_utf8 = sha256_utf8
-        elif _algorithm == "SHA-512":
-
-            def sha512_utf8(x):
-                if isinstance(x, str):
-                    x = x.encode("utf-8")
-                return hashlib.sha512(x).hexdigest()
-
-            hash_utf8 = sha512_utf8
-
+                if algorithm == "MD5" or algorithm == "MD5-SESS":
+                    return hashlib.md5(x).hexdigest()
+                elif algorithm == "SHA":
+                    return hashlib.sha1(x).hexdigest()
+                elif algorithm == "SHA-256":
+                    return hashlib.sha256(x).hexdigest()
+                elif algorithm == "SHA-512":
+                    return hashlib.sha512(x).hexdigest()
+                return None
+
+            return hash_utf8, algorithm
+
+        hash_utf8, _algorithm = get_hash_function(algorithm)
         KD = lambda s, d: hash_utf8(f"{s}:{d}")  # noqa:E731
 
         if hash_utf8 is None:

```
