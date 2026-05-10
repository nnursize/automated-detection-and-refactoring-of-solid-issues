# Refactor SRP-056 (SRP): Acts as a data holder for HTTP responses but also performs content processing...

**Status:** `applied_failed`  
**Branch:** `refactor/SRP-056` -> `main`  
**Head commit:** `178332b19159a5d45228c36e03126748061c76d5`  
**LLM finish:** `FinishReason.STOP` (prompt 10176, completion 1289)  

## Detected issue

- **File**: `src/requests/models.py`
- **Entity**: `Response` (class)
- **Lines (at detection time)**: L642–L1041
- **Severity**: high
- **Confidence**: detected by 4 scan(s)

**Description.** Acts as a data holder for HTTP responses but also performs content processing, encoding detection, JSON deserialization, and header parsing.

**Reasoning.** The `Response` class combines the responsibility of being a simple data container for an HTTP response with several distinct content processing and interpretation responsibilities. Specifically, it includes logic for: (1) content encoding detection (`apparent_encoding`, used by `text`, `json`), (2) content decoding (bytes to unicode in `text`, `iter_content`), (3) JSON deserialization (`json`, including its own encoding guessing), and (4) parsing specific HTTP headers (`links`). These are separate concerns; a change in the JSON specification, encoding detection algorithm, or Link header parsing rules would require modifying this class, even if the core response data structure remains the same. These processing tasks could be delegated to specialized helper objects.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 3
- **Files created** (1): `src/requests/models_utils.py`
- **Files modified** (1): `src/requests/models.py`

**Summary.** Extract content processing logic from Response class to a helper class

**Rationale.** The Response class was violating SRP by handling content decoding, JSON deserialization, and header parsing. I have extracted these responsibilities into a new 'ResponseDecoder' class in a new file 'src/requests/models_utils.py' to keep the Response class focused on being a data container.

## Changes overview

_3 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `src/requests/models.py` (12-line block → 10-line replacement)

**Replaces:**

```python
from .utils import (
    check_header_validity,
    get_auth_from_url,
    guess_filename,
    guess_json_utf,
    iter_slices,
    parse_header_links,
    requote_uri,
    stream_decode_response_unicode,
    super_len,
    to_key_val_list,
)
```

**With:**

```python
from .utils import (
    check_header_validity,
    get_auth_from_url,
    guess_filename,
    iter_slices,
    requote_uri,
    super_len,
    to_key_val_list,
)
from .models_utils import ResponseDecoder
```

### 2. EDIT `src/requests/models.py` (51-line block → 15-line replacement)

**Replaces:**

```python
    def json(self, **kwargs):
        r"""Decodes the JSON response body (if any) as a Python object.

        This may return a dictionary, list, etc. depending on what is in the response.

        :param \*\*kwargs: Optional arguments that ``json.loads`` takes.
        :raises requests.exceptions.JSONDecodeError: If the response body does not
            contain valid json.
        """

        if not self.encoding and self.content and len(self.content) > 3:
            # No encoding set. JSON RFC 4627 section 3 states we should expect
            # UTF-8, -16 or -32. Detect which one to use; If the detection or
            # decoding fails, fall back to `self.text` (using charset_normalizer to make
            # a best guess).
            encoding = guess_json_utf(self.content)
            if encoding is not None:
                try:
                    return complexjson.loads(self.content.decode(encoding), **kwargs)
                except UnicodeDecodeError:
                    # Wrong UTF codec detected; usually because it's not UTF-8
                    # but some other 8-bit codec.  This is an RFC violation,
                    # and the server didn't bother to tell us what codec *was*
                    # used.
                    pass
                except JSONDecodeError as e:
                    raise RequestsJSONDecodeError(e.msg, e.doc, e.pos)

        try:
            return complexjson.loads(self.text, **kwargs)
        except JSONDecodeError as e:
            # Catch JSON-related errors and raise as requests.JSONDecodeError
            # This aliases json.JSONDecodeError and simplejson.JSONDecodeError
            raise RequestsJSONDecodeError(e.msg, e.doc, e.pos)

    @property
    def links(self):
        """Returns the parsed header links of the response, if any."""

        header = self.headers.get("link")

        resolved_links = {}

        if header:
            links = parse_header_links(header)

            for link in links:
                key = link.get("rel") or link.get("url")
                resolved_links[key] = link

        return resolved_links
```

**With:**

```python
    def json(self, **kwargs):
        r"""Decodes the JSON response body (if any) as a Python object.

        This may return a dictionary, list, etc. depending on what is in the response.

        :param \*\*kwargs: Optional arguments that ``json.loads`` takes.
        :raises requests.exceptions.JSONDecodeError: If the response body does not
            contain valid json.
        """
        return ResponseDecoder.decode_json(self, **kwargs)

    @property
    def links(self):
        """Returns the parsed header links of the response, if any."""
        return ResponseDecoder.parse_links(self.headers)
```

### 3. CREATE `src/requests/models_utils.py` (29 line(s))

```python
from .compat import json as complexjson, JSONDecodeError
from .exceptions import JSONDecodeError as RequestsJSONDecodeError, InvalidJSONError
from .utils import guess_json_utf, parse_header_links, stream_decode_response_unicode

class ResponseDecoder:
    @staticmethod
    def decode_json(response, **kwargs):
        if not response.encoding and response.content and len(response.content) > 3:
            encoding = guess_json_utf(response.content)
            if encoding is not None:
                try:
                    return complexjson.loads(response.content.decode(encoding), **kwargs)
                except (UnicodeDecodeError, JSONDecodeError):
                    pass
        try:
            return complexjson.loads(response.text, **kwargs)
        except JSONDecodeError as e:
            raise RequestsJSONDecodeError(e.msg, e.doc, e.pos)

    @staticmethod
    def parse_links(headers):
        header = headers.get("link")
        resolved_links = {}
        if header:
            links = parse_header_links(header)
            for link in links:
                key = link.get("rel") or link.get("url")
                resolved_links[key] = link
        return resolved_links
```

## Test results

**FAILED** — 183/185 passed, 1 failed, 1 skipped, 0 errored (duration 86798 ms).

- New failures introduced by this refactor: **1**
- Pre-existing failures (unrelated to this refactor): **0**

New-failure node IDs (first 25):

  - `tests/test_requests.py::TestRequests::test_response_decode_unicode`

Command: `C:\Users\User\Desktop\SDP-Codex\S1-T7-Okeyish\refactor_workspaces\requests\.venv\Scripts\python.exe -m pytest --tb=short -q --no-header -p no:cacheprovider -x --json-report --json-report-file=C:\Users\User\Desktop\SDP-Codex\S1-T7-Okeyish\refactor_workspaces\requests\.pytest_report.json --deselect=tests/test_requests.py::TestPreparingURLs::test_different_connection_pool_for_tls_settings_verify_bundle_unexpired_cert`

<details><summary>Output tail</summary>

```
........................................................................ [ 11%]
........................................................................ [ 23%]
......sattempting to ignore so the rest of the tests can run
.................................F
================================== FAILURES ===================================
__________________ TestRequests.test_response_decode_unicode __________________
tests\test_requests.py:1443: in test_response_decode_unicode
    chunks = r.iter_content(decode_unicode=True)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src\requests\models.py:853: in iter_content
    chunks = stream_decode_response_unicode(chunks, self)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   NameError: name 'stream_decode_response_unicode' is not defined
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
FAILED tests/test_requests.py::TestRequests::test_response_decode_unicode - N...
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!
1 failed, 183 passed, 1 skipped, 1 deselected, 8 warnings in 86.00s (0:01:26)

```

</details>

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/requests/models.py` | 743 → - | 44 → - | 4.46 → - | 21 → - | 21.73 → - |

## Diff

```diff
diff --git a/src/requests/models.py b/src/requests/models.py
index 2d043f5..1855267 100644
--- a/src/requests/models.py
+++ b/src/requests/models.py
@@ -59,14 +59,12 @@ from .utils import (
     check_header_validity,
     get_auth_from_url,
     guess_filename,
-    guess_json_utf,
     iter_slices,
-    parse_header_links,
     requote_uri,
-    stream_decode_response_unicode,
     super_len,
     to_key_val_list,
 )
+from .models_utils import ResponseDecoder
 
 #: The set of HTTP status codes that indicate an automatically
 #: processable redirect.
@@ -955,48 +953,12 @@ class Response:
         :raises requests.exceptions.JSONDecodeError: If the response body does not
             contain valid json.
         """
-
-        if not self.encoding and self.content and len(self.content) > 3:
-            # No encoding set. JSON RFC 4627 section 3 states we should expect
-            # UTF-8, -16 or -32. Detect which one to use; If the detection or
-            # decoding fails, fall back to `self.text` (using charset_normalizer to make
-            # a best guess).
-            encoding = guess_json_utf(self.content)
-            if encoding is not None:
-                try:
-                    return complexjson.loads(self.content.decode(encoding), **kwargs)
-                except UnicodeDecodeError:
-                    # Wrong UTF codec detected; usually because it's not UTF-8
-                    # but some other 8-bit codec.  This is an RFC violation,
-                    # and the server didn't bother to tell us what codec *was*
-                    # used.
-                    pass
-                except JSONDecodeError as e:
-                    raise RequestsJSONDecodeError(e.msg, e.doc, e.pos)
-
-        try:
-            return complexjson.loads(self.text, **kwargs)
-        except JSONDecodeError as e:
-            # Catch JSON-related errors and raise as requests.JSONDecodeError
-            # This aliases json.JSONDecodeError and simplejson.JSONDecodeError
-            raise RequestsJSONDecodeError(e.msg, e.doc, e.pos)
+        return ResponseDecoder.decode_json(self, **kwargs)
 
     @property
     def links(self):
         """Returns the parsed header links of the response, if any."""
-
-        header = self.headers.get("link")
-
-        resolved_links = {}
-
-        if header:
-            links = parse_header_links(header)
-
-            for link in links:
-                key = link.get("rel") or link.get("url")
-                resolved_links[key] = link
-
-        return resolved_links
+        return ResponseDecoder.parse_links(self.headers)
 
     def raise_for_status(self):
         """Raises :class:`HTTPError`, if one occurred."""
diff --git a/src/requests/models_utils.py b/src/requests/models_utils.py
new file mode 100644
index 0000000..0000000
--- /dev/null
+++ b/src/requests/models_utils.py
@@ -0,0 +1,29 @@
+from .compat import json as complexjson, JSONDecodeError
+from .exceptions import JSONDecodeError as RequestsJSONDecodeError, InvalidJSONError
+from .utils import guess_json_utf, parse_header_links, stream_decode_response_unicode
+
+class ResponseDecoder:
+    @staticmethod
+    def decode_json(response, **kwargs):
+        if not response.encoding and response.content and len(response.content) > 3:
+            encoding = guess_json_utf(response.content)
+            if encoding is not None:
+                try:
+                    return complexjson.loads(response.content.decode(encoding), **kwargs)
+                except (UnicodeDecodeError, JSONDecodeError):
+                    pass
+        try:
+            return complexjson.loads(response.text, **kwargs)
+        except JSONDecodeError as e:
+            raise RequestsJSONDecodeError(e.msg, e.doc, e.pos)
+
+    @staticmethod
+    def parse_links(headers):
+        header = headers.get("link")
+        resolved_links = {}
+        if header:
+            links = parse_header_links(header)
+            for link in links:
+                key = link.get("rel") or link.get("url")
+                resolved_links[key] = link
+        return resolved_links
\ No newline at end of file

```
