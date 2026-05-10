# Refactor ISP-009 (ISP): The Request class inherits 'deregister_hook' from RequestHooksMixin but does...

**Status:** `applied_passed`  
**Branch:** `refactor/ISP-009` -> `main`  
**Head commit:** `1e9f9ab4990d9ca195910d699fed2f0ced15160e`  
**LLM finish:** `FinishReason.STOP` (prompt 10054, completion 504)  

## Detected issue

- **File**: `src/requests/models.py`
- **Entity**: `Request` (class)
- **Lines (at detection time)**: L232–L312
- **Severity**: medium
- **Confidence**: detected by 1 scan(s)

**Description.** The Request class inherits 'deregister_hook' from RequestHooksMixin but does not appear to use this functionality itself.

**Reasoning.** The Request class inherits from RequestHooksMixin, which provides both 'register_hook' and 'deregister_hook' methods. While Request utilizes 'register_hook' during its initialization, there is no apparent use case or call to 'deregister_hook' within the Request class's own responsibilities. This means Request is forced to depend on a method it does not use, indicating a potential 'fat interface' in the mixin from Request's perspective. Although the mixin is small, it still represents a dependency on unused functionality.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `src/requests/models.py`

**Summary.** Split RequestHooksMixin into RegisterOnlyHooksMixin and RequestHooksMixin to enforce ISP.

**Rationale.** The Request class only needs to register hooks during initialization, not deregister them. By splitting the mixin, Request no longer depends on the unused deregister_hook method, adhering to the Interface Segregation Principle.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `src/requests/models.py` (25-line block → 27-line replacement)

**Replaces:**

```python
class RequestHooksMixin:
    def register_hook(self, event, hook):
        """Properly register a hook."""

        if event not in self.hooks:
            raise ValueError(f'Unsupported event specified, with event name "{event}"')

        if isinstance(hook, Callable):
            self.hooks[event].append(hook)
        elif hasattr(hook, "__iter__"):
            self.hooks[event].extend(h for h in hook if isinstance(h, Callable))

    def deregister_hook(self, event, hook):
        """Deregister a previously registered hook.
        Returns True if the hook existed, False if not.
        """

        try:
            self.hooks[event].remove(hook)
            return True
        except ValueError:
            return False


class Request(RequestHooksMixin):
```

**With:**

```python
class RegisterOnlyHooksMixin:
    def register_hook(self, event, hook):
        """Properly register a hook."""

        if event not in self.hooks:
            raise ValueError(f'Unsupported event specified, with event name "{event}"')

        if isinstance(hook, Callable):
            self.hooks[event].append(hook)
        elif hasattr(hook, "__iter__"):
            self.hooks[event].extend(h for h in hook if isinstance(h, Callable))


class RequestHooksMixin(RegisterOnlyHooksMixin):
    def deregister_hook(self, event, hook):
        """Deregister a previously registered hook.
        Returns True if the hook existed, False if not.
        """

        try:
            self.hooks[event].remove(hook)
            return True
        except ValueError:
            return False


class Request(RegisterOnlyHooksMixin):
```

## Test results

**PASSED** — 606/610 passed, 0 failed, 3 skipped, 0 errored (duration 165324 ms).

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
606 passed, 3 skipped, 1 deselected, 1 xfailed, 17 warnings in 164.44s (0:02:44)

[stderr]
127.0.0.1 - - [04/May/2026 14:34:58] "GET /get HTTP/1.1" 200 170
127.0.0.1 - - [04/May/2026 14:35:22] "GET /get?test=foo&test=baz HTTP/1.1" 200 260

```

</details>

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/requests/models.py` | 747 → 748 | 47 → 47 | 4.18 → 4.2 | 19 → 19 | 21.48 → 21.45 |

## Diff

```diff
diff --git a/src/requests/models.py b/src/requests/models.py
index f63e59b..50a372b 100644
--- a/src/requests/models.py
+++ b/src/requests/models.py
@@ -210,7 +210,7 @@ class RequestEncodingMixin:
         return body, content_type
 
 
-class RequestHooksMixin:
+class RegisterOnlyHooksMixin:
     def register_hook(self, event, hook):
         """Properly register a hook."""
 
@@ -222,6 +222,8 @@ class RequestHooksMixin:
         elif hasattr(hook, "__iter__"):
             self.hooks[event].extend(h for h in hook if isinstance(h, Callable))
 
+
+class RequestHooksMixin(RegisterOnlyHooksMixin):
     def deregister_hook(self, event, hook):
         """Deregister a previously registered hook.
         Returns True if the hook existed, False if not.
@@ -234,7 +236,7 @@ class RequestHooksMixin:
             return False
 
 
-class Request(RequestHooksMixin):
+class Request(RegisterOnlyHooksMixin):
     """A user-created :class:`Request <Request>` object.
 
     Used to prepare a :class:`PreparedRequest <PreparedRequest>`, which is sent to the server.

```
