# Refactor ISP-004 (ISP): The `HTTPAdapter.add_headers` method is implemented as a no-op, indicating it...

**Status:** `applied_failed`  
**Branch:** `refactor/ISP-004` -> `main`  
**Head commit:** `2de64a995585a0d6c740cb951d8eee572aa200f6`  
**LLM finish:** `FinishReason.STOP` (prompt 8042, completion 573)  

## Detected issue

- **File**: `src/requests/adapters.py`
- **Entity**: `HTTPAdapter.add_headers` (method)
- **Lines (at detection time)**: L346–L360
- **Severity**: medium
- **Confidence**: detected by 2 scan(s)

**Description.** The `HTTPAdapter.add_headers` method is implemented as a no-op, indicating it's not essential for the base adapter's core functionality.

**Reasoning.** The `HTTPAdapter` class's `send` method calls `self.add_headers()`. However, the default implementation of `add_headers` is an empty `pass` statement, with a comment explicitly stating it 'does nothing by default' and is 'left for overriding by users that subclass.' This means `HTTPAdapter` is forced to provide an implementation for a method that is not part of its core responsibility in its base form. This violates ISP because the `HTTPAdapter` (as a client of its own internal interface) is forced to depend on and implement a method it does not use meaningfully, pushing the responsibility of a potentially unused method onto the base class. A more segregated design would introduce this method via a specific mixin or a different pattern only for adapters that genuinely need to add headers.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 2
- **Files modified** (1): `src/requests/adapters.py`

**Summary.** Extract add_headers into a HeaderAdapter mixin to satisfy ISP

**Rationale.** The add_headers method was a no-op in the base HTTPAdapter, violating the Interface Segregation Principle. By moving it to a mixin, only subclasses that actually require header manipulation need to inherit from it, removing the forced dependency from the base class.

## Changes overview

_2 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `src/requests/adapters.py` (13-line block → 10-line replacement)

**Replaces:**

```python
    def add_headers(self, request, **kwargs):
        """Add any headers needed by the connection. As of v2.0 this does
        nothing by default, but is left for overriding by users that subclass
        the :class:`HTTPAdapter <requests.adapters.HTTPAdapter>`.

        This should not be called from user code, and is only exposed for use
        when subclassing the
        :class:`HTTPAdapter <requests.adapters.HTTPAdapter>`.

        :param request: The :class:`PreparedRequest <PreparedRequest>` to add headers to.
        :param kwargs: The keyword arguments from the call to send().
        """
        pass
```

**With:**

```python
class HeaderAdapter:
    """Mixin for adapters that need to add headers to requests."""

    def add_headers(self, request, **kwargs):
        """Add any headers needed by the connection.

        :param request: The :class:`PreparedRequest <PreparedRequest>` to add headers to.
        :param kwargs: The keyword arguments from the call to send().
        """
        pass
```

### 2. EDIT `src/requests/adapters.py` (12-line block → 14-line replacement)

**Replaces:**

```python
        self.cert_verify(conn, request.url, verify, cert)
        url = self.request_url(request, proxies)
        self.add_headers(
            request,
            stream=stream,
            timeout=timeout,
            verify=verify,
            cert=cert,
            proxies=proxies,
        )

        chunked = not (request.body is None or "Content-Length" in request.headers)
```

**With:**

```python
        self.cert_verify(conn, request.url, verify, cert)
        url = self.request_url(request, proxies)

        if hasattr(self, "add_headers"):
            self.add_headers(
                request,
                stream=stream,
                timeout=timeout,
                verify=verify,
                cert=cert,
                proxies=proxies,
            )

        chunked = not (request.body is None or "Content-Length" in request.headers)
```

## Test results

**FAILED** — 7/8 passed, 1 failed, 0 skipped, 0 errored (duration 1063 ms).

- New failures introduced by this refactor: **1**
- Pre-existing failures (unrelated to this refactor): **0**

New-failure node IDs (first 25):

  - `tests/test_lowlevel.py::test_chunked_upload`

Command: `C:\Users\User\Desktop\SDP-Codex\S1-T7-Okeyish\refactor_workspaces\requests\.venv\Scripts\python.exe -m pytest --tb=short -q --no-header -p no:cacheprovider -x --json-report --json-report-file=C:\Users\User\Desktop\SDP-Codex\S1-T7-Okeyish\refactor_workspaces\requests\.pytest_report.json --deselect=tests/test_requests.py::TestPreparingURLs::test_different_connection_pool_for_tls_settings_verify_bundle_unexpired_cert`

<details><summary>Output tail</summary>

```
.......F
================================== FAILURES ===================================
_____________________________ test_chunked_upload _____________________________
tests\test_lowlevel.py:32: in test_chunked_upload
    r = requests.post(url, data=data, stream=True)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src\requests\api.py:115: in post
    return request("post", url, data=data, json=json, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src\requests\api.py:59: in request
    return session.request(method=method, url=url, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src\requests\sessions.py:587: in request
    resp = self.send(prep, **send_kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src\requests\sessions.py:701: in send
    r = adapter.send(request, **kwargs)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src\requests\adapters.py:138: in send
    raise NotImplementedError
E   NotImplementedError
=========================== short test summary info ===========================
FAILED tests/test_lowlevel.py::test_chunked_upload - NotImplementedError
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!
1 failed, 7 passed, 1 deselected in 0.25s

```

</details>

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/requests/adapters.py` | 588 → - | 24 → - | 3.29 → - | 14 → - | 47.37 → - |

## Diff

```diff
diff --git a/src/requests/adapters.py b/src/requests/adapters.py
index d049183..2f45e3c 100644
--- a/src/requests/adapters.py
+++ b/src/requests/adapters.py
@@ -571,14 +571,11 @@ class HTTPAdapter(BaseAdapter):
 
         return url
 
-    def add_headers(self, request, **kwargs):
-        """Add any headers needed by the connection. As of v2.0 this does
-        nothing by default, but is left for overriding by users that subclass
-        the :class:`HTTPAdapter <requests.adapters.HTTPAdapter>`.
+class HeaderAdapter:
+    """Mixin for adapters that need to add headers to requests."""
 
-        This should not be called from user code, and is only exposed for use
-        when subclassing the
-        :class:`HTTPAdapter <requests.adapters.HTTPAdapter>`.
+    def add_headers(self, request, **kwargs):
+        """Add any headers needed by the connection.
 
         :param request: The :class:`PreparedRequest <PreparedRequest>` to add headers to.
         :param kwargs: The keyword arguments from the call to send().
@@ -663,14 +660,16 @@ class HTTPAdapter(BaseAdapter):
 
         self.cert_verify(conn, request.url, verify, cert)
         url = self.request_url(request, proxies)
-        self.add_headers(
-            request,
-            stream=stream,
-            timeout=timeout,
-            verify=verify,
-            cert=cert,
-            proxies=proxies,
-        )
+
+        if hasattr(self, "add_headers"):
+            self.add_headers(
+                request,
+                stream=stream,
+                timeout=timeout,
+                verify=verify,
+                cert=cert,
+                proxies=proxies,
+            )
 
         chunked = not (request.body is None or "Content-Length" in request.headers)
 

```
