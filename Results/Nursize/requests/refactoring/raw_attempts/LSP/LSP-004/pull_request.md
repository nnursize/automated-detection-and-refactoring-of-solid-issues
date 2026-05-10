# Refactor LSP-004 (LSP): Subclass method raises a specialized exception not present in the base class...

**Status:** `applied_failed`  
**Branch:** `refactor/LSP-004` -> `main`  
**Head commit:** `e96a1330471edbe1f13403a3614cb92ebe18f56a`  
**LLM finish:** `FinishReason.STOP` (prompt 6085, completion 321)  

## Detected issue

- **File**: `src/requests/cookies.py`
- **Entity**: `RequestsCookieJar.__getitem__` (class)
- **Lines (at detection time)**: L396–L402
- **Severity**: medium
- **Confidence**: detected by 4 scan(s)

**Description.** Subclass method raises a specialized exception not present in the base class contract.

**Reasoning.** RequestsCookieJar inherits from cookielib.CookieJar and MutableMapping. Its __getitem__ implementation raises CookieConflictError if multiple cookies match a name. A standard Mapping or dict contract expects either the value or a KeyError. Introducing a new exception type for a standard access operation breaks the substitution contract for callers expecting standard mapping behavior.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `src/requests/cookies.py`

**Summary.** Update __getitem__ to raise KeyError instead of CookieConflictError to adhere to Mapping contract

**Rationale.** The Liskov Substitution Principle requires that subclasses of Mapping must raise KeyError when a key is missing or ambiguous in a way that violates the expected interface. By catching CookieConflictError and re-raising it as a KeyError, we maintain compatibility with callers expecting standard dictionary behavior while preserving the existing logic.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `src/requests/cookies.py` (8-line block → 11-line replacement)

**Replaces:**

```python
    def __getitem__(self, name):
        """Dict-like __getitem__() for compatibility with client code. Throws
        exception if there are more than one cookie with name. In that case,
        use the more explicit get() method instead.

        .. warning:: operation is O(n), not O(1).
        """
        return self._find_no_duplicates(name)
```

**With:**

```python
    def __getitem__(self, name):
        """Dict-like __getitem__() for compatibility with client code. Throws
        exception if there are more than one cookie with name. In that case,
        use the more explicit get() method instead.

        .. warning:: operation is O(n), not O(1).
        """
        try:
            return self._find_no_duplicates(name)
        except CookieConflictError as e:
            raise KeyError(str(e))
```

## Test results

**FAILED** — 177/179 passed, 1 failed, 1 skipped, 0 errored (duration 86218 ms).

- New failures introduced by this refactor: **1**
- Pre-existing failures (unrelated to this refactor): **0**

New-failure node IDs (first 25):

  - `tests/test_requests.py::TestRequests::test_cookie_duplicate_names_different_domains`

Command: `C:\Users\User\Desktop\SDP-Codex\S1-T7-Okeyish\refactor_workspaces\requests\.venv\Scripts\python.exe -m pytest --tb=short -q --no-header -p no:cacheprovider -x --json-report --json-report-file=C:\Users\User\Desktop\SDP-Codex\S1-T7-Okeyish\refactor_workspaces\requests\.pytest_report.json --deselect=tests/test_requests.py::TestPreparingURLs::test_different_connection_pool_for_tls_settings_verify_bundle_unexpired_cert`

<details><summary>Output tail</summary>

```
........................................................................ [ 11%]
........................................................................ [ 23%]
......sattempting to ignore so the rest of the tests can run
...........................F
================================== FAILURES ===================================
_________ TestRequests.test_cookie_duplicate_names_different_domains __________
tests\test_requests.py:1378: in test_cookie_duplicate_names_different_domains
    assert key in jar
E   AssertionError: assert 'some_cookie' in <RequestsCookieJar[Cookie(version=0, name='some_cookie', value='some_value', port=None, port_specified=False, domain='...ue, secure=False, expires=None, discard=True, comment=None, comment_url=None, rest={'HttpOnly': None}, rfc2109=False)]>
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

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ===========================
FAILED tests/test_requests.py::TestRequests::test_cookie_duplicate_names_different_domains
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!
1 failed, 177 passed, 1 skipped, 1 deselected, 8 warnings in 85.41s (0:01:25)

```

</details>

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/requests/cookies.py` | 439 → - | 49 → - | 2.38 → - | 9 → - | 39.76 → - |

## Diff

```diff
diff --git a/src/requests/cookies.py b/src/requests/cookies.py
index f69d0cd..59a1913 100644
--- a/src/requests/cookies.py
+++ b/src/requests/cookies.py
@@ -331,7 +331,10 @@ class RequestsCookieJar(cookielib.CookieJar, MutableMapping):
 
         .. warning:: operation is O(n), not O(1).
         """
-        return self._find_no_duplicates(name)
+        try:
+            return self._find_no_duplicates(name)
+        except CookieConflictError as e:
+            raise KeyError(str(e))
 
     def __setitem__(self, name, value):
         """Dict-like __setitem__ for compatibility with client code. Throws

```
