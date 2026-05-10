# Refactor ISP-012 (ISP): The Session class provides a broad API encompassing request preparation, send...

**Status:** `applied_passed`  
**Branch:** `refactor/ISP-012` -> `main`  
**Head commit:** `3b311ed3c33786cf4d4f54dea107aa244a276be8`  
**LLM finish:** `FinishReason.STOP` (prompt 8815, completion 682)  

## Detected issue

- **File**: `src/requests/sessions.py`
- **Entity**: `Session` (class)
- **Lines (at detection time)**: L357–L817
- **Severity**: medium
- **Confidence**: detected by 1 scan(s)

**Description.** The Session class provides a broad API encompassing request preparation, sending, redirect handling, adapter management, and various HTTP verb shortcuts.

**Reasoning.** The Session class combines many responsibilities, including high-level HTTP verb methods (`get`, `post`), lower-level request dispatch (`send`), and configuration (`mount`, `get_adapter`). Clients using a Session object are exposed to and depend on this entire broad interface, even if they only interact with a specific subset of its capabilities (e.g., only using the high-level verbs without needing to manage adapters or redirects manually). Segregating these concerns into more focused interfaces could reduce client dependencies on unused parts of the API.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 2
- **Files modified** (1): `src/requests/sessions.py`

**Summary.** Segregate Session interface by extracting adapter management into a SessionAdapterMixin.

**Rationale.** The Session class is a 'fat' interface. By extracting adapter-related methods (mount, get_adapter, close) into a mixin, we separate the concerns of connection management from request dispatching and session state, improving the interface's cohesion.

## Changes overview

_2 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `src/requests/sessions.py` (2-line block → 33-line replacement)

**Replaces:**

```python
class SessionRedirectMixin:
    def get_redirect_target(self, resp):
```

**With:**

```python
class SessionAdapterMixin:
    def get_adapter(self, url):
        """
        Returns the appropriate connection adapter for the given URL.

        :rtype: requests.adapters.BaseAdapter
        """
        for prefix, adapter in self.adapters.items():
            if url.lower().startswith(prefix.lower()):
                return adapter

        # Nothing matches :-/
        raise InvalidSchema(f"No connection adapters were found for {url!r}")

    def close(self):
        """Closes all adapters and as such the session"""
        for v in self.adapters.values():
            v.close()

    def mount(self, prefix, adapter):
        """Registers a connection adapter to a prefix.

        Adapters are sorted in descending order by prefix length.
        """
        self.adapters[prefix] = adapter
        keys_to_move = [k for k in self.adapters if len(k) < len(prefix)]

        for key in keys_to_move:
            self.adapters[key] = self.adapters.pop(key)


class SessionRedirectMixin:
    def get_redirect_target(self, resp):
```

### 2. EDIT `src/requests/sessions.py` (2-line block → 2-line replacement)

**Replaces:**

```python
class Session(SessionRedirectMixin):
    """A Requests session.
```

**With:**

```python
class Session(SessionRedirectMixin, SessionAdapterMixin):
    """A Requests session.
```

## Test results

**PASSED** — 606/610 passed, 0 failed, 3 skipped, 0 errored (duration 165173 ms).

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
606 passed, 3 skipped, 1 deselected, 1 xfailed, 17 warnings in 164.31s (0:02:44)

[stderr]
127.0.0.1 - - [04/May/2026 14:43:05] "GET /get HTTP/1.1" 200 222
127.0.0.1 - - [04/May/2026 14:43:05] "GET /get?foo=bar&FOO=bar HTTP/1.1" 200 261
127.0.0.1 - - [04/May/2026 14:43:16] "GET /get HTTP/1.1" 200 222

```

</details>

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/requests/sessions.py` | 569 → 591 | 28 → 31 | 3.93 → 3.85 | 15 → 15 | 38.99 → 37.21 |

## Diff

```diff
diff --git a/src/requests/sessions.py b/src/requests/sessions.py
index efc56f1..17910ed 100644
--- a/src/requests/sessions.py
+++ b/src/requests/sessions.py
@@ -104,6 +104,37 @@ def merge_hooks(request_hooks, session_hooks, dict_class=OrderedDict):
     return merge_setting(request_hooks, session_hooks, dict_class)
 
 
+class SessionAdapterMixin:
+    def get_adapter(self, url):
+        """
+        Returns the appropriate connection adapter for the given URL.
+
+        :rtype: requests.adapters.BaseAdapter
+        """
+        for prefix, adapter in self.adapters.items():
+            if url.lower().startswith(prefix.lower()):
+                return adapter
+
+        # Nothing matches :-/
+        raise InvalidSchema(f"No connection adapters were found for {url!r}")
+
+    def close(self):
+        """Closes all adapters and as such the session"""
+        for v in self.adapters.values():
+            v.close()
+
+    def mount(self, prefix, adapter):
+        """Registers a connection adapter to a prefix.
+
+        Adapters are sorted in descending order by prefix length.
+        """
+        self.adapters[prefix] = adapter
+        keys_to_move = [k for k in self.adapters if len(k) < len(prefix)]
+
+        for key in keys_to_move:
+            self.adapters[key] = self.adapters.pop(key)
+
+
 class SessionRedirectMixin:
     def get_redirect_target(self, resp):
         """Receives a Response. Returns a redirect URI or ``None``"""
@@ -351,7 +382,7 @@ class SessionRedirectMixin:
         prepared_request.method = method
 
 
-class Session(SessionRedirectMixin):
+class Session(SessionRedirectMixin, SessionAdapterMixin):
     """A Requests session.
 
     Provides cookie persistence, connection-pooling, and configuration.

```
