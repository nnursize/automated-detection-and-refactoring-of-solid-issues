# Refactor SRP-013 (SRP): Orchestrates the entire redirect handling process, including history, URL nor...

**Status:** `applied_failed`  
**Branch:** `refactor/SRP-013` -> `main`  
**Head commit:** `178332b19159a5d45228c36e03126748061c76d5`  
**LLM finish:** `FinishReason.STOP` (prompt 8906, completion 1601)  

## Detected issue

- **File**: `src/requests/sessions.py`
- **Entity**: `SessionRedirectMixin.resolve_redirects` (method)
- **Lines (at detection time)**: L103–L222
- **Severity**: high
- **Confidence**: detected by 4 scan(s)

**Description.** Orchestrates the entire redirect handling process, including history, URL normalization, request modification, cookie management, auth/proxy rebuilding, and sending new requests.

**Reasoning.** This is a 'god method' for redirect handling. Its responsibilities are numerous and distinct: 1) Managing redirect history. 2) Consuming and closing previous responses. 3) Enforcing redirect limits. 4) Normalizing redirect URLs (scheme, fragment, relative paths). 5) Modifying the request method (`rebuild_method`). 6) Purging headers. 7) Extracting and merging cookies. 8) Rebuilding authentication (`rebuild_auth`). 9) Rebuilding proxy configuration (`rebuild_proxies`). 10) Rewinding the request body. 11) Sending the new request. Each of these steps is a significant responsibility that could change independently.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 2
- **Files modified** (1): `src/requests/sessions.py`

**Summary.** Decompose SessionRedirectMixin.resolve_redirects into smaller, focused helper methods.

**Rationale.** The resolve_redirects method was a 'god method' handling too many distinct responsibilities. By extracting the URL normalization, request preparation, and cookie/header management into dedicated helper methods, the code becomes more modular, readable, and maintainable while preserving existing behavior.

## Changes overview

_2 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `src/requests/sessions.py` (45-line block → 7-line replacement)

**Replaces:**

```python
            # Handle redirection without scheme (see: RFC 1808 Section 4)
            if url.startswith("//"):
                parsed_rurl = urlparse(resp.url)
                url = ":".join([to_native_string(parsed_rurl.scheme), url])

            # Normalize url case and attach previous fragment if needed (RFC 7231 7.1.2)
            parsed = urlparse(url)
            if parsed.fragment == "" and previous_fragment:
                parsed = parsed._replace(fragment=previous_fragment)
            elif parsed.fragment:
                previous_fragment = parsed.fragment
            url = parsed.geturl()

            # Facilitate relative 'location' headers, as allowed by RFC 7231.
            # (e.g. '/path/to/resource' instead of 'http://domain.tld/path/to/resource')
            # Compliant with RFC3986, we percent encode the url.
            if not parsed.netloc:
                url = urljoin(resp.url, requote_uri(url))
            else:
                url = requote_uri(url)

            prepared_request.url = to_native_string(url)

            self.rebuild_method(prepared_request, resp)

            # https://github.com/psf/requests/issues/1084
            if resp.status_code not in (
                codes.temporary_redirect,
                codes.permanent_redirect,
            ):
                # https://github.com/psf/requests/issues/3490
                purged_headers = ("Content-Length", "Content-Type", "Transfer-Encoding")
                for header in purged_headers:
                    prepared_request.headers.pop(header, None)
                prepared_request.body = None

            headers = prepared_request.headers
            headers.pop("Cookie", None)

            # Extract any cookies sent on the response to the cookiejar
            # in the new request. Because we've mutated our copied prepared
            # request, use the old one that we haven't yet touched.
            extract_cookies_to_jar(prepared_request._cookies, req, resp.raw)
            merge_cookies(prepared_request._cookies, self.cookies)
            prepared_request.prepare_cookies(prepared_request._cookies)
```

**With:**

```python
            url = self.prepare_redirect_url(resp, url, previous_fragment)
            previous_fragment = urlparse(url).fragment
            prepared_request.url = to_native_string(url)

            self.rebuild_method(prepared_request, resp)
            self.prepare_redirect_headers(prepared_request, resp)
            self.prepare_redirect_cookies(prepared_request, req, resp)
```

### 2. EDIT `src/requests/sessions.py` (21-line block → 53-line replacement)

**Replaces:**

```python
    def rebuild_method(self, prepared_request, response):
        """When being redirected we may want to change the method of the request
        based on certain specs or browser behavior.
        """
        method = prepared_request.method

        # https://tools.ietf.org/html/rfc7231#section-6.4.4
        if response.status_code == codes.see_other and method != "HEAD":
            method = "GET"

        # Do what the browsers do, despite standards...
        # First, turn 302s into GETs.
        if response.status_code == codes.found and method != "HEAD":
            method = "GET"

        # Second, if a POST is responded to with a 301, turn it into a GET.
        # This bizarre behaviour is explained in Issue 1704.
        if response.status_code == codes.moved and method == "POST":
            method = "GET"

        prepared_request.method = method
```

**With:**

```python
    def prepare_redirect_url(self, resp, url, previous_fragment):
        """Normalize and prepare the redirect URL."""
        if url.startswith("//"):
            parsed_rurl = urlparse(resp.url)
            url = ":".join([to_native_string(parsed_rurl.scheme), url])

        parsed = urlparse(url)
        if parsed.fragment == "" and previous_fragment:
            parsed = parsed._replace(fragment=previous_fragment)
        url = parsed.geturl()

        if not parsed.netloc:
            url = urljoin(resp.url, requote_uri(url))
        else:
            url = requote_uri(url)
        return url

    def prepare_redirect_headers(self, prepared_request, resp):
        """Purge headers and reset body for redirect."""
        if resp.status_code not in (codes.temporary_redirect, codes.permanent_redirect):
            purged_headers = ("Content-Length", "Content-Type", "Transfer-Encoding")
            for header in purged_headers:
                prepared_request.headers.pop(header, None)
            prepared_request.body = None
        prepared_request.headers.pop("Cookie", None)

    def prepare_redirect_cookies(self, prepared_request, req, resp):
        """Extract and merge cookies for the redirected request."""
        extract_cookies_to_jar(prepared_request._cookies, req, resp.raw)
        merge_cookies(prepared_request._cookies, self.cookies)
        prepared_request.prepare_cookies(prepared_request._cookies)

    def rebuild_method(self, prepared_request, response):
        """When being redirected we may want to change the method of the request
        based on certain specs or browser behavior.
        """
        method = prepared_request.method

        # https://tools.ietf.org/html/rfc7231#section-6.4.4
        if response.status_code == codes.see_other and method != "HEAD":
            method = "GET"

        # Do what the browsers do, despite standards...
        # First, turn 302s into GETs.
        if response.status_code == codes.found and method != "HEAD":
            method = "GET"

        # Second, if a POST is responded to with a 301, turn it into a GET.
        # This bizarre behaviour is explained in Issue 1704.
        if response.status_code == codes.moved and method == "POST":
            method = "GET"

        prepared_request.method = method
```

## Test results

**FAILED** — 64/65 passed, 1 failed, 0 skipped, 0 errored (duration 62396 ms).

- New failures introduced by this refactor: **1**
- Pre-existing failures (unrelated to this refactor): **0**

New-failure node IDs (first 25):

  - `tests/test_requests.py::TestRequests::test_HTTP_307_ALLOW_REDIRECT_POST_WITH_SEEKABLE`

Command: `C:\Users\User\Desktop\SDP-Codex\S1-T7-Okeyish\refactor_workspaces\requests\.venv\Scripts\python.exe -m pytest --tb=short -q --no-header -p no:cacheprovider -x --json-report --json-report-file=C:\Users\User\Desktop\SDP-Codex\S1-T7-Okeyish\refactor_workspaces\requests\.pytest_report.json --deselect=tests/test_requests.py::TestPreparingURLs::test_different_connection_pool_for_tls_settings_verify_bundle_unexpired_cert`

<details><summary>Output tail</summary>

```
................................................................F
================================== FAILURES ===================================
________ TestRequests.test_HTTP_307_ALLOW_REDIRECT_POST_WITH_SEEKABLE _________
tests\test_requests.py:233: in test_HTTP_307_ALLOW_REDIRECT_POST_WITH_SEEKABLE
    r = requests.post(
src\requests\api.py:115: in post
    return request("post", url, data=data, json=json, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src\requests\api.py:59: in request
    return session.request(method=method, url=url, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src\requests\sessions.py:584: in request
    resp = self.send(prep, **send_kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src\requests\sessions.py:719: in send
    history = [resp for resp in gen]
              ^^^^^^^^^^^^^^^^^^^^^^
src\requests\sessions.py:719: in <listcomp>
    history = [resp for resp in gen]
              ^^^^^^^^^^^^^^^^^^^^^^
src\requests\sessions.py:215: in resolve_redirects
    "Content-Length" in headers or "Transfer-Encoding" in headers
                        ^^^^^^^
E   NameError: name 'headers' is not defined
---------------------------- Captured stderr call -----------------------------
127.0.0.1 - - [04/May/2026 12:33:10] "POST /redirect-to?url=post&status_code=307 HTTP/1.1" 307 0
=========================== short test summary info ===========================
FAILED tests/test_requests.py::TestRequests::test_HTTP_307_ALLOW_REDIRECT_POST_WITH_SEEKABLE
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!
1 failed, 64 passed, 1 deselected in 61.62s (0:01:01)

```

</details>

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/requests/sessions.py` | 566 → - | 28 → - | 4.07 → - | 15 → - | 38.09 → - |

## Diff

```diff
diff --git a/src/requests/sessions.py b/src/requests/sessions.py
index 7d34b29..02f7ec1 100644
--- a/src/requests/sessions.py
+++ b/src/requests/sessions.py
@@ -196,51 +196,13 @@ class SessionRedirectMixin:
             # Release the connection back into the pool.
             resp.close()
 
-            # Handle redirection without scheme (see: RFC 1808 Section 4)
-            if url.startswith("//"):
-                parsed_rurl = urlparse(resp.url)
-                url = ":".join([to_native_string(parsed_rurl.scheme), url])
-
-            # Normalize url case and attach previous fragment if needed (RFC 7231 7.1.2)
-            parsed = urlparse(url)
-            if parsed.fragment == "" and previous_fragment:
-                parsed = parsed._replace(fragment=previous_fragment)
-            elif parsed.fragment:
-                previous_fragment = parsed.fragment
-            url = parsed.geturl()
-
-            # Facilitate relative 'location' headers, as allowed by RFC 7231.
-            # (e.g. '/path/to/resource' instead of 'http://domain.tld/path/to/resource')
-            # Compliant with RFC3986, we percent encode the url.
-            if not parsed.netloc:
-                url = urljoin(resp.url, requote_uri(url))
-            else:
-                url = requote_uri(url)
-
+            url = self.prepare_redirect_url(resp, url, previous_fragment)
+            previous_fragment = urlparse(url).fragment
             prepared_request.url = to_native_string(url)
 
             self.rebuild_method(prepared_request, resp)
-
-            # https://github.com/psf/requests/issues/1084
-            if resp.status_code not in (
-                codes.temporary_redirect,
-                codes.permanent_redirect,
-            ):
-                # https://github.com/psf/requests/issues/3490
-                purged_headers = ("Content-Length", "Content-Type", "Transfer-Encoding")
-                for header in purged_headers:
-                    prepared_request.headers.pop(header, None)
-                prepared_request.body = None
-
-            headers = prepared_request.headers
-            headers.pop("Cookie", None)
-
-            # Extract any cookies sent on the response to the cookiejar
-            # in the new request. Because we've mutated our copied prepared
-            # request, use the old one that we haven't yet touched.
-            extract_cookies_to_jar(prepared_request._cookies, req, resp.raw)
-            merge_cookies(prepared_request._cookies, self.cookies)
-            prepared_request.prepare_cookies(prepared_request._cookies)
+            self.prepare_redirect_headers(prepared_request, resp)
+            self.prepare_redirect_cookies(prepared_request, req, resp)
 
             # Rebuild auth and proxy information.
             proxies = self.rebuild_proxies(prepared_request, proxies)
@@ -331,6 +293,38 @@ class SessionRedirectMixin:
 
         return new_proxies
 
+    def prepare_redirect_url(self, resp, url, previous_fragment):
+        """Normalize and prepare the redirect URL."""
+        if url.startswith("//"):
+            parsed_rurl = urlparse(resp.url)
+            url = ":".join([to_native_string(parsed_rurl.scheme), url])
+
+        parsed = urlparse(url)
+        if parsed.fragment == "" and previous_fragment:
+            parsed = parsed._replace(fragment=previous_fragment)
+        url = parsed.geturl()
+
+        if not parsed.netloc:
+            url = urljoin(resp.url, requote_uri(url))
+        else:
+            url = requote_uri(url)
+        return url
+
+    def prepare_redirect_headers(self, prepared_request, resp):
+        """Purge headers and reset body for redirect."""
+        if resp.status_code not in (codes.temporary_redirect, codes.permanent_redirect):
+            purged_headers = ("Content-Length", "Content-Type", "Transfer-Encoding")
+            for header in purged_headers:
+                prepared_request.headers.pop(header, None)
+            prepared_request.body = None
+        prepared_request.headers.pop("Cookie", None)
+
+    def prepare_redirect_cookies(self, prepared_request, req, resp):
+        """Extract and merge cookies for the redirected request."""
+        extract_cookies_to_jar(prepared_request._cookies, req, resp.raw)
+        merge_cookies(prepared_request._cookies, self.cookies)
+        prepared_request.prepare_cookies(prepared_request._cookies)
+
     def rebuild_method(self, prepared_request, response):
         """When being redirected we may want to change the method of the request
         based on certain specs or browser behavior.

```
