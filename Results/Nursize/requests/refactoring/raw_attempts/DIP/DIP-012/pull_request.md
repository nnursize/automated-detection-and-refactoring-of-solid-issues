# Refactor DIP-012 (DIP): Factory function directly instantiates RequestsCookieJar.

**Status:** `applied_passed`  
**Branch:** `refactor/DIP-012` -> `main`  
**Head commit:** `234d6a661d2a0df2a426b39622a2ae205c2d6868`  
**LLM finish:** `FinishReason.STOP` (prompt 6056, completion 431)  

## Detected issue

- **File**: `src/requests/cookies.py`
- **Entity**: `cookiejar_from_dict` (class)
- **Lines (at detection time)**: L308–L308
- **Severity**: low
- **Confidence**: detected by 2 scan(s)

**Description.** Factory function directly instantiates RequestsCookieJar.

**Reasoning.** The `cookiejar_from_dict` function is explicitly a factory whose purpose is to create a `RequestsCookieJar` object. Factory functions are designed to encapsulate the creation of concrete objects. Therefore, its direct instantiation of `RequestsCookieJar` is not a violation of DIP, as it fulfills its role as a creator of a specific concrete type.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `src/requests/cookies.py`

**Summary.** Refactor cookiejar_from_dict to accept a factory function for dependency inversion.

**Rationale.** The direct instantiation of RequestsCookieJar inside cookiejar_from_dict couples the factory to a concrete implementation. By allowing an optional factory function (defaulting to RequestsCookieJar), we adhere to the Dependency Inversion Principle, allowing for easier testing and substitution of cookie jar implementations.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `src/requests/cookies.py` (13-line block → 14-line replacement)

**Replaces:**

```python
def cookiejar_from_dict(cookie_dict, cookiejar=None, overwrite=True):
    """Returns a CookieJar from a key/value dictionary.

    :param cookie_dict: Dict of key/values to insert into CookieJar.
    :param cookiejar: (optional) A cookiejar to add the cookies to.
    :param overwrite: (optional) If False, will not replace cookies
        already in the jar with new ones.
    :rtype: CookieJar
    """
    if cookiejar is None:
        cookiejar = RequestsCookieJar()

    if cookie_dict is not None:
```

**With:**

```python
def cookiejar_from_dict(cookie_dict, cookiejar=None, overwrite=True, jar_factory=RequestsCookieJar):
    """Returns a CookieJar from a key/value dictionary.

    :param cookie_dict: Dict of key/values to insert into CookieJar.
    :param cookiejar: (optional) A cookiejar to add the cookies to.
    :param overwrite: (optional) If False, will not replace cookies
        already in the jar with new ones.
    :param jar_factory: (optional) A factory function to create a new CookieJar.
    :rtype: CookieJar
    """
    if cookiejar is None:
        cookiejar = jar_factory()

    if cookie_dict is not None:
```

## Test results

**PASSED** — 606/610 passed, 0 failed, 3 skipped, 0 errored (duration 165730 ms).

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
606 passed, 3 skipped, 1 deselected, 1 xfailed, 17 warnings in 164.86s (0:02:44)

[stderr]
127.0.0.1 - - [04/May/2026 15:09:06] "GET /cookies HTTP/1.1" 200 30

```

</details>

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/requests/cookies.py` | 436 → 437 | 48 → 48 | 2.42 → 2.42 | 9 → 9 | 39.73 → 39.74 |

## Diff

```diff
diff --git a/src/requests/cookies.py b/src/requests/cookies.py
index 2a787ba..123635c 100644
--- a/src/requests/cookies.py
+++ b/src/requests/cookies.py
@@ -514,17 +514,18 @@ def morsel_to_cookie(morsel):
     )
 
 
-def cookiejar_from_dict(cookie_dict, cookiejar=None, overwrite=True):
+def cookiejar_from_dict(cookie_dict, cookiejar=None, overwrite=True, jar_factory=RequestsCookieJar):
     """Returns a CookieJar from a key/value dictionary.
 
     :param cookie_dict: Dict of key/values to insert into CookieJar.
     :param cookiejar: (optional) A cookiejar to add the cookies to.
     :param overwrite: (optional) If False, will not replace cookies
         already in the jar with new ones.
+    :param jar_factory: (optional) A factory function to create a new CookieJar.
     :rtype: CookieJar
     """
     if cookiejar is None:
-        cookiejar = RequestsCookieJar()
+        cookiejar = jar_factory()
 
     if cookie_dict is not None:
         names_from_jar = [cookie.name for cookie in cookiejar]

```
