# Refactor DIP-015 (DIP): High-level API function directly instantiates a concrete Session.

**Status:** `applied_passed`  
**Branch:** `refactor/DIP-015` -> `main`  
**Head commit:** `605d581ad1c9a45c9376d841286040efdce291c6`  
**LLM finish:** `FinishReason.STOP` (prompt 3121, completion 357)  

## Detected issue

- **File**: `src/requests/api.py`
- **Entity**: `request` (class)
- **Lines (at detection time)**: L21–L22
- **Severity**: high
- **Confidence**: detected by 2 scan(s)

**Description.** High-level API function directly instantiates a concrete Session.

**Reasoning.** The `request` function, which is the primary public entry point for making HTTP requests, directly creates an instance of `requests.sessions.Session`. This couples the highest-level policy (how requests are made via the public API) to a concrete implementation (`Session` class). According to DIP, high-level modules should not depend on low-level modules; both should depend on abstractions. Here, the public API depends on a concrete session implementation, making it difficult to substitute alternative session management without modifying the core API.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 2
- **Files modified** (1): `src/requests/api.py`

**Summary.** Decouple request() from concrete Session class by using a module-level session factory.

**Rationale.** The request function was hardcoded to use sessions.Session. By defining a module-level variable for the session factory, we allow the implementation to be swapped or configured without modifying the high-level API function, adhering to the Dependency Inversion Principle.

## Changes overview

_2 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `src/requests/api.py` (4-line block → 7-line replacement)

**Replaces:**

```python
from . import sessions


def request(method, url, **kwargs):
```

**With:**

```python
from . import sessions

# Default session factory
session_factory = sessions.Session


def request(method, url, **kwargs):
```

### 2. EDIT `src/requests/api.py` (7-line block → 7-line replacement)

**Replaces:**

```python
    session_factory = kwargs.pop("session_factory", sessions.Session)

    # By using the 'with' statement we are sure the session is closed, thus we
    # avoid leaving sockets open which can trigger a ResourceWarning in some
    # cases, and look like a memory leak in others.
    with session_factory() as session:
        return session.request(method=method, url=url, **kwargs)
```

**With:**

```python
    factory = kwargs.pop("session_factory", session_factory)

    # By using the 'with' statement we are sure the session is closed, thus we
    # avoid leaving sockets open which can trigger a ResourceWarning in some
    # cases, and look like a memory leak in others.
    with factory() as session:
        return session.request(method=method, url=url, **kwargs)
```

## Test results

**PASSED** — 606/610 passed, 0 failed, 3 skipped, 0 errored (duration 165301 ms).

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
606 passed, 3 skipped, 1 deselected, 1 xfailed, 17 warnings in 164.45s (0:02:44)

```

</details>

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/requests/api.py` | 119 → 120 | 8 → 8 | 1 → 1 | 1 → 1 | 100 → 100 |

## Diff

```diff
diff --git a/src/requests/api.py b/src/requests/api.py
index de8f75d..55d060f 100644
--- a/src/requests/api.py
+++ b/src/requests/api.py
@@ -10,6 +10,9 @@ This module implements the Requests API.
 
 from . import sessions
 
+# Default session factory
+session_factory = sessions.Session
+
 
 def request(method, url, **kwargs):
     """Constructs and sends a :class:`Request <Request>`.
@@ -53,12 +56,12 @@ def request(method, url, **kwargs):
       <Response [200]>
     """
 
-    session_factory = kwargs.pop("session_factory", sessions.Session)
+    factory = kwargs.pop("session_factory", session_factory)
 
     # By using the 'with' statement we are sure the session is closed, thus we
     # avoid leaving sockets open which can trigger a ResourceWarning in some
     # cases, and look like a memory leak in others.
-    with session_factory() as session:
+    with factory() as session:
         return session.request(method=method, url=url, **kwargs)
 
 

```
