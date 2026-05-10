# Refactor SRP-007 (SRP): Combines URL parsing, scheme/host validation, IDNA encoding, parameter encodi...

**Status:** `applied_passed`  
**Branch:** `refactor/SRP-007` -> `main`  
**Head commit:** `86adf5b7fc0237d018b9f36b810b5e074c620668`  
**LLM finish:** `FinishReason.STOP` (prompt 10131, completion 1270)  

## Detected issue

- **File**: `src/requests/models.py`
- **Entity**: `PreparedRequest.prepare_url` (method)
- **Lines (at detection time)**: L251–L307
- **Severity**: medium
- **Confidence**: detected by 4 scan(s)

**Description.** Combines URL parsing, scheme/host validation, IDNA encoding, parameter encoding, and URI requoting.

**Reasoning.** This method is responsible for preparing the request URL. It mixes several concerns: 1) Parsing the URL into components. 2) Validating the scheme and host. 3) Applying IDNA encoding to the hostname. 4) Encoding URL parameters (delegating to `_encode_params`). 5) Reconstructing and requoting the final URI. Changes in URL validation rules, IDNA encoding standards, parameter encoding logic, or URI quoting behavior would all necessitate changes to this single method.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `src/requests/models.py`

**Summary.** Extract URL preparation logic into a dedicated helper method to improve SRP compliance.

**Rationale.** The `prepare_url` method was doing too much (parsing, validation, IDNA encoding, parameter encoding, and reconstruction). By extracting the URL reconstruction and validation logic into a private helper `_prepare_url_components`, we separate the high-level orchestration from the low-level URL manipulation details.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `src/requests/models.py` (73-line block → 60-line replacement)

**Replaces:**

```python
    def prepare_url(self, url, params):
        """Prepares the given HTTP URL."""
        #: Accept objects that have string representations.
        #: We're unable to blindly call unicode/str functions
        #: as this will include the bytestring indicator (b'')
        #: on python 3.x.
        #: https://github.com/psf/requests/pull/2238
        if isinstance(url, bytes):
            url = url.decode("utf8")
        else:
            url = str(url)

        # Remove leading whitespaces from url
        url = url.lstrip()

        # Don't do any URL preparation for non-HTTP schemes like `mailto`,
        # `data` etc to work around exceptions from `url_parse`, which
        # handles RFC 3986 only.
        if ":" in url and not url.lower().startswith("http"):
            self.url = url
            return

        # Support for unicode domain names and paths.
        try:
            scheme, auth, host, port, path, query, fragment = parse_url(url)
        except LocationParseError as e:
            raise InvalidURL(*e.args)

        if not scheme:
            raise MissingSchema(
                f"Invalid URL {url!r}: No scheme supplied. "
                f"Perhaps you meant https://{url}?"
            )

        if not host:
            raise InvalidURL(f"Invalid URL {url!r}: No host supplied")

        # In general, we want to try IDNA encoding the hostname if the string contains
        # non-ASCII characters. This allows users to automatically get the correct IDNA
        # behaviour. For strings containing only ASCII characters, we need to also verify
        # it doesn't start with a wildcard (*), before allowing the unencoded hostname.
        if not unicode_is_ascii(host):
            try:
                host = self._get_idna_encoded_host(host)
            except UnicodeError:
                raise InvalidURL("URL has an invalid label.")
        elif host.startswith(("*", ".")):
            raise InvalidURL("URL has an invalid label.")

        # Carefully reconstruct the network location
        netloc = auth or ""
        if netloc:
            netloc += "@"
        netloc += host
        if port:
            netloc += f":{port}"

        # Bare domains aren't valid URLs.
        if not path:
            path = "/"
... (13 more line(s) truncated)
```

**With:**

```python
    def _prepare_url_components(self, url, params):
        """Parses, validates, and encodes URL components."""
        try:
            scheme, auth, host, port, path, query, fragment = parse_url(url)
        except LocationParseError as e:
            raise InvalidURL(*e.args)

        if not scheme:
            raise MissingSchema(
                f"Invalid URL {url!r}: No scheme supplied. "
                f"Perhaps you meant https://{url}?"
            )

        if not host:
            raise InvalidURL(f"Invalid URL {url!r}: No host supplied")

        if not unicode_is_ascii(host):
            try:
                host = self._get_idna_encoded_host(host)
            except UnicodeError:
                raise InvalidURL("URL has an invalid label.")
        elif host.startswith(("*", ".")):
            raise InvalidURL("URL has an invalid label.")

        netloc = auth or ""
        if netloc:
            netloc += "@"
        netloc += host
        if port:
            netloc += f":{port}"

        if not path:
            path = "/"

        if isinstance(params, (str, bytes)):
            params = to_native_string(params)

        enc_params = self._encode_params(params)
        if enc_params:
            if query:
                query = f"{query}&{enc_params}"
            else:
                query = enc_params

        return urlunparse([scheme, netloc, path, None, query, fragment])

    def prepare_url(self, url, params):
        """Prepares the given HTTP URL."""
        if isinstance(url, bytes):
            url = url.decode("utf8")
        else:
            url = str(url)

        url = url.lstrip()

        if ":" in url and not url.lower().startswith("http"):
            self.url = url
            return

        self.url = requote_uri(self._prepare_url_components(url, params))
```

## Test results

**PASSED** — 606/610 passed, 0 failed, 3 skipped, 0 errored (duration 165962 ms).

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
  C:\Users\User\Desktop\SDP-Codex\S1-T7-Okeyish\refactor_workspaces\requests\src\requests\utils.py:482: DeprecationWarning: In requests 3.0, get_encodings_from_content will be removed. For more information, please see the discussion on issue #2266. (This warning should only appear once.)
    warnings.warn(

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
606 passed, 3 skipped, 1 deselected, 1 xfailed, 17 warnings in 165.19s (0:02:45)

[stderr]
127.0.0.1 - - [04/May/2026 12:35:46] "GET /digest-auth/auth/user/pass/SHA-512 HTTP/1.1" 200 37
127.0.0.1 - - [04/May/2026 12:36:17] "GET /get HTTP/1.1" 200 222
127.0.0.1 - - [04/May/2026 12:36:17] "GET /redirect-to?url=http%3A%2F%2F%3A1 HTTP/1.1" 302 0

```

</details>

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/requests/models.py` | 743 → 745 | 44 → 45 | 4.46 → 4.39 | 21 → 21 | 21.73 → 21.22 |

## Diff

```diff
diff --git a/src/requests/models.py b/src/requests/models.py
index 2d043f5..6c69679 100644
--- a/src/requests/models.py
+++ b/src/requests/models.py
@@ -408,29 +408,8 @@ class PreparedRequest(RequestEncodingMixin, RequestHooksMixin):
             raise UnicodeError
         return host
 
-    def prepare_url(self, url, params):
-        """Prepares the given HTTP URL."""
-        #: Accept objects that have string representations.
-        #: We're unable to blindly call unicode/str functions
-        #: as this will include the bytestring indicator (b'')
-        #: on python 3.x.
-        #: https://github.com/psf/requests/pull/2238
-        if isinstance(url, bytes):
-            url = url.decode("utf8")
-        else:
-            url = str(url)
-
-        # Remove leading whitespaces from url
-        url = url.lstrip()
-
-        # Don't do any URL preparation for non-HTTP schemes like `mailto`,
-        # `data` etc to work around exceptions from `url_parse`, which
-        # handles RFC 3986 only.
-        if ":" in url and not url.lower().startswith("http"):
-            self.url = url
-            return
-
-        # Support for unicode domain names and paths.
+    def _prepare_url_components(self, url, params):
+        """Parses, validates, and encodes URL components."""
         try:
             scheme, auth, host, port, path, query, fragment = parse_url(url)
         except LocationParseError as e:
@@ -445,10 +424,6 @@ class PreparedRequest(RequestEncodingMixin, RequestHooksMixin):
         if not host:
             raise InvalidURL(f"Invalid URL {url!r}: No host supplied")
 
-        # In general, we want to try IDNA encoding the hostname if the string contains
-        # non-ASCII characters. This allows users to automatically get the correct IDNA
-        # behaviour. For strings containing only ASCII characters, we need to also verify
-        # it doesn't start with a wildcard (*), before allowing the unencoded hostname.
         if not unicode_is_ascii(host):
             try:
                 host = self._get_idna_encoded_host(host)
@@ -457,7 +432,6 @@ class PreparedRequest(RequestEncodingMixin, RequestHooksMixin):
         elif host.startswith(("*", ".")):
             raise InvalidURL("URL has an invalid label.")
 
-        # Carefully reconstruct the network location
         netloc = auth or ""
         if netloc:
             netloc += "@"
@@ -465,7 +439,6 @@ class PreparedRequest(RequestEncodingMixin, RequestHooksMixin):
         if port:
             netloc += f":{port}"
 
-        # Bare domains aren't valid URLs.
         if not path:
             path = "/"
 
@@ -479,8 +452,22 @@ class PreparedRequest(RequestEncodingMixin, RequestHooksMixin):
             else:
                 query = enc_params
 
-        url = requote_uri(urlunparse([scheme, netloc, path, None, query, fragment]))
-        self.url = url
+        return urlunparse([scheme, netloc, path, None, query, fragment])
+
+    def prepare_url(self, url, params):
+        """Prepares the given HTTP URL."""
+        if isinstance(url, bytes):
+            url = url.decode("utf8")
+        else:
+            url = str(url)
+
+        url = url.lstrip()
+
+        if ":" in url and not url.lower().startswith("http"):
+            self.url = url
+            return
+
+        self.url = requote_uri(self._prepare_url_components(url, params))
 
     def prepare_headers(self, headers):
         """Prepares the given HTTP headers."""

```
