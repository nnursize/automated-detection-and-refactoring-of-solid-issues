# Refactor DIP-029 (DIP): High-level redirect handling logic directly depends on numerous concrete util...

**Status:** `applied_failed`  
**Branch:** `refactor/DIP-029` -> `main`  
**Head commit:** `2438f1af4c906d0cb8147a99e660d67493be677b`  
**LLM finish:** `FinishReason.STOP` (prompt 9090, completion 2395)  

## Detected issue

- **File**: `src/requests/sessions.py`
- **Entity**: `SessionRedirectMixin.resolve_redirects` (method)
- **Lines (at detection time)**: L62–L136
- **Severity**: high
- **Confidence**: detected by 1 scan(s)

**Description.** High-level redirect handling logic directly depends on numerous concrete utility functions and the session's send method.

**Reasoning.** The `resolve_redirects` method, which encapsulates complex redirect logic, directly calls several concrete utility functions like `urlparse`, `urljoin`, `requote_uri`, `extract_cookies_to_jar`, `merge_cookies`, `rewind_body`, and crucially, `self.send`. This tight coupling to specific implementations of URL manipulation, cookie management, request body handling, and the concrete request sending mechanism makes the redirect logic rigid and hard to modify or test in isolation.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 4
- **Files modified** (1): `src/requests/sessions.py`

**Summary.** Refactor SessionRedirectMixin to use an abstract send method to decouple redirect logic from Session implementation.

**Rationale.** The SessionRedirectMixin was tightly coupled to the Session class's 'send' method. By defining an abstract 'send' method interface within the mixin (or assuming it exists on the host class), we improve the separation of concerns. While the mixin still relies on utility functions, the primary violation of coupling to the concrete 'Session.send' implementation is mitigated by treating 'send' as an interface method provided by the host class.

## Changes overview

_4 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `src/requests/sessions.py` (17-line block → 24-line replacement)

**Replaces:**

```python
    def resolve_redirects(
        self,
        resp,
        req,
        stream=False,
        timeout=None,
        verify=True,
        cert=None,
        proxies=None,
        yield_requests=False,
        **adapter_kwargs,
    ):
        """Receives a Response. Returns a generator of Responses or Requests."""

        hist = []  # keep track of history

        url = self.get_redirect_target(resp)
```

**With:**

```python
    def send_redirect(self, request, **kwargs):
        """
        Abstract method to send a request.
        This should be implemented by the class using this mixin.
        """
        raise NotImplementedError("Subclasses must implement send_redirect")

    def resolve_redirects(
        self,
        resp,
        req,
        stream=False,
        timeout=None,
        verify=True,
        cert=None,
        proxies=None,
        yield_requests=False,
        **adapter_kwargs,
    ):
        """Receives a Response. Returns a generator of Responses or Requests."""

        hist = []  # keep track of history

        url = self.get_redirect_target(resp)
```

### 2. EDIT `src/requests/sessions.py` (15-line block → 15-line replacement)

**Replaces:**

```python
            if yield_requests:
                yield req
            else:
                resp = self.send(
                    req,
                    stream=stream,
                    timeout=timeout,
                    verify=verify,
                    cert=cert,
                    proxies=proxies,
                    allow_redirects=False,
                    **adapter_kwargs,
                )

                extract_cookies_to_jar(self.cookies, prepared_request, resp.raw)
```

**With:**

```python
            if yield_requests:
                yield req
            else:
                resp = self.send_redirect(
                    req,
                    stream=stream,
                    timeout=timeout,
                    verify=verify,
                    cert=cert,
                    proxies=proxies,
                    allow_redirects=False,
                    **adapter_kwargs,
                )

                extract_cookies_to_jar(self.cookies, prepared_request, resp.raw)
```

### 3. EDIT `src/requests/sessions.py` (24-line block → 24-line replacement)

**Replaces:**

```python
        # Resolve redirects if allowed.
        if allow_redirects:
            # Redirect resolving generator.
            gen = self.resolve_redirects(r, request, **kwargs)
            history = [resp for resp in gen]
        else:
            history = []

        # Shuffle things around if there's history.
        if history:
            # Insert the first (original) request at the start
            history.insert(0, r)
            # Get the last request made
            r = history.pop()
            r.history = history

        # If redirects aren't being followed, store the response on the Request for Response.next().
        if not allow_redirects:
            try:
                r._next = next(
                    self.resolve_redirects(r, request, yield_requests=True, **kwargs)
                )
            except StopIteration:
                pass
```

**With:**

```python
        # Resolve redirects if allowed.
        if allow_redirects:
            # Redirect resolving generator.
            gen = self.resolve_redirects(r, request, **kwargs)
            history = [resp for resp in gen]
        else:
            history = []

        # Shuffle things around if there's history.
        if history:
            # Insert the first (original) request at the start
            history.insert(0, r)
            # Get the last request made
            r = history.pop()
            r.history = history

        # If redirects aren't being followed, store the response on the Request for Response.next().
        if not allow_redirects:
            try:
                r._next = next(
                    self.resolve_redirects(r, request, yield_requests=True, **kwargs)
                )
            except StopIteration:
                pass
```

### 4. EDIT `src/requests/sessions.py` (76-line block → 80-line replacement)

**Replaces:**

```python
    def send(self, request, **kwargs):
        """Send a given PreparedRequest.

        :rtype: requests.Response
        """
        # Set defaults that the hooks can utilize to ensure they always have
        # the correct parameters to reproduce the previous request.
        kwargs.setdefault("stream", self.stream)
        kwargs.setdefault("verify", self.verify)
        kwargs.setdefault("cert", self.cert)
        if "proxies" not in kwargs:
            kwargs["proxies"] = resolve_proxies(request, self.proxies, self.trust_env)

        # It's possible that users might accidentally send a Request object.
        # Guard against that specific failure case.
        if isinstance(request, Request):
            raise ValueError("You can only send PreparedRequests.")

        # Set up variables needed for resolve_redirects and dispatching of hooks
        allow_redirects = kwargs.pop("allow_redirects", True)
        stream = kwargs.get("stream")
        hooks = request.hooks

        # Get the appropriate adapter to use
        adapter = self.get_adapter(url=request.url)

        # Start time (approximately) of the request
        start = preferred_clock()

        # Send the request
        r = adapter.send(request, **kwargs)

        # Total elapsed time of the request (approximately)
        elapsed = preferred_clock() - start
        r.elapsed = timedelta(seconds=elapsed)

        # Response manipulation hooks
        r = dispatch_hook("response", hooks, r, **kwargs)

        # Persist cookies
        if r.history:
            # If the hooks create history then we want those cookies too
            for resp in r.history:
                extract_cookies_to_jar(self.cookies, resp.request, resp.raw)

        extract_cookies_to_jar(self.cookies, request, r.raw)

        # Resolve redirects if allowed.
        if allow_redirects:
            # Redirect resolving generator.
            gen = self.resolve_redirects(r, request, **kwargs)
            history = [resp for resp in gen]
        else:
            history = []

        # Shuffle things around if there's history.
        if history:
            # Insert the first (original) request at the start
            history.insert(0, r)
            # Get the last request made
... (16 more line(s) truncated)
```

**With:**

```python
    def send_redirect(self, request, **kwargs):
        """Proxy to self.send for redirect handling."""
        return self.send(request, **kwargs)

    def send(self, request, **kwargs):
        """Send a given PreparedRequest.

        :rtype: requests.Response
        """
        # Set defaults that the hooks can utilize to ensure they always have
        # the correct parameters to reproduce the previous request.
        kwargs.setdefault("stream", self.stream)
        kwargs.setdefault("verify", self.verify)
        kwargs.setdefault("cert", self.cert)
        if "proxies" not in kwargs:
            kwargs["proxies"] = resolve_proxies(request, self.proxies, self.trust_env)

        # It's possible that users might accidentally send a Request object.
        # Guard against that specific failure case.
        if isinstance(request, Request):
            raise ValueError("You can only send PreparedRequests.")

        # Set up variables needed for resolve_redirects and dispatching of hooks
        allow_redirects = kwargs.pop("allow_redirects", True)
        stream = kwargs.get("stream")
        hooks = request.hooks

        # Get the appropriate adapter to use
        adapter = self.get_adapter(url=request.url)

        # Start time (approximately) of the request
        start = preferred_clock()

        # Send the request
        r = adapter.send(request, **kwargs)

        # Total elapsed time of the request (approximately)
        elapsed = preferred_clock() - start
        r.elapsed = timedelta(seconds=elapsed)

        # Response manipulation hooks
        r = dispatch_hook("response", hooks, r, **kwargs)

        # Persist cookies
        if r.history:
            # If the hooks create history then we want those cookies too
            for resp in r.history:
                extract_cookies_to_jar(self.cookies, resp.request, resp.raw)

        extract_cookies_to_jar(self.cookies, request, r.raw)

        # Resolve redirects if allowed.
        if allow_redirects:
            # Redirect resolving generator.
            gen = self.resolve_redirects(r, request, **kwargs)
            history = [resp for resp in gen]
        else:
            history = []

        # Shuffle things around if there's history.
... (20 more line(s) truncated)
```

## Test results

**FAILED** — 309/312 passed, 1 failed, 1 skipped, 0 errored (duration 116780 ms).

- New failures introduced by this refactor: **1**
- Pre-existing failures (unrelated to this refactor): **0**

New-failure node IDs (first 25):

  - `tests/test_requests.py::test_requests_are_updated_each_time`

Command: `C:\Users\User\Desktop\SDP-Codex\S1-T7-Okeyish\refactor_workspaces\requests\.venv\Scripts\python.exe -m pytest --tb=short -q --no-header -p no:cacheprovider -x --json-report --json-report-file=C:\Users\User\Desktop\SDP-Codex\S1-T7-Okeyish\refactor_workspaces\requests\.pytest_report.json --deselect=tests/test_requests.py::TestPreparingURLs::test_different_connection_pool_for_tls_settings_verify_bundle_unexpired_cert`

<details><summary>Output tail</summary>

```
........................................................................ [ 11%]
........................................................................ [ 23%]
......spytest-httpbin server hit an exception serving request: [WinError 10054] An existing connection was forcibly closed by the remote host
attempting to ignore so the rest of the tests can run
................................................................. [ 35%]
...............................................x........................ [ 47%]
.......................F
================================== FAILURES ===================================
_____________________ test_requests_are_updated_each_time _____________________
tests\test_requests.py:2609: in test_requests_are_updated_each_time
    for response in redirect_generator:
src\requests\sessions.py:304: in resolve_redirects
    resp = self.send_redirect(
src\requests\sessions.py:196: in send_redirect
    raise NotImplementedError("Subclasses must implement send_redirect")
E   NotImplementedError: Subclasses must implement send_redirect
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
FAILED tests/test_requests.py::test_requests_are_updated_each_time - NotImple...
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!
1 failed, 309 passed, 1 skipped, 1 deselected, 1 xfailed, 8 warnings in 115.92s (0:01:55)

[stderr]
127.0.0.1 - - [04/May/2026 15:18:07] "GET /get HTTP/1.1" 200 170

```

</details>

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/requests/sessions.py` | 591 → - | 31 → - | 3.91 → - | 15 → - | 36.83 → - |

## Diff

```diff
diff --git a/src/requests/sessions.py b/src/requests/sessions.py
index 2dc6d7a..a72f932 100644
--- a/src/requests/sessions.py
+++ b/src/requests/sessions.py
@@ -188,6 +188,13 @@ class SessionRedirectMixin:
         # Standard case: root URI must match
         return changed_port or changed_scheme
 
+    def send_redirect(self, request, **kwargs):
+        """
+        Abstract method to send a request.
+        This should be implemented by the class using this mixin.
+        """
+        raise NotImplementedError("Subclasses must implement send_redirect")
+
     def resolve_redirects(
         self,
         resp,
@@ -294,7 +301,7 @@ class SessionRedirectMixin:
             if yield_requests:
                 yield req
             else:
-                resp = self.send(
+                resp = self.send_redirect(
                     req,
                     stream=stream,
                     timeout=timeout,
@@ -699,6 +706,10 @@ class Session(SessionRedirectMixin, SessionAdapterMixin):
 
         return self.request("DELETE", url, **kwargs)
 
+    def send_redirect(self, request, **kwargs):
+        """Proxy to self.send for redirect handling."""
+        return self.send(request, **kwargs)
+
     def send(self, request, **kwargs):
         """Send a given PreparedRequest.
 

```
