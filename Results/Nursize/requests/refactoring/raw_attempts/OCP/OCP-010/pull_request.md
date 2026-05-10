# Refactor OCP-010 (OCP): Complex conditional logic for preparing request body based on input type.

**Status:** `applied_failed`  
**Branch:** `refactor/OCP-010` -> `main`  
**Head commit:** `e371495cbfecf5334430cadee9adf29fee850983`  
**LLM finish:** `FinishReason.STOP` (prompt 10053, completion 1176)  

## Detected issue

- **File**: `src/requests/models.py`
- **Entity**: `PreparedRequest.prepare_body` (method)
- **Lines (at detection time)**: L275–L319
- **Severity**: high
- **Confidence**: detected by 2 scan(s)

**Description.** Complex conditional logic for preparing request body based on input type.

**Reasoning.** This method uses a complex `if/elif/else` structure to handle different ways of providing a request body (JSON, streamed data, multipart files, form-encoded data). It relies on the presence of `json`, `files`, and `is_stream` flags, along with `isinstance` and `hasattr` checks. Adding a new type of request body (e.g., a custom object that handles its own serialization) would require modifying this method, violating OCP. This is a strong candidate for a strategy pattern or a body preparer registry.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `src/requests/models.py`

**Summary.** Refactor prepare_body to use a strategy-like dispatch pattern

**Rationale.** The complex if/elif/else structure in prepare_body is replaced with a dispatch mechanism that separates the logic for different body types (JSON, stream, multipart, form-encoded). This makes the method cleaner and easier to extend without modifying the core logic.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `src/requests/models.py` (77-line block → 45-line replacement)

**Replaces:**

```python
    def prepare_body(self, data, files, json=None):
        """Prepares the given HTTP body data."""

        # Check if file, fo, generator, iterator.
        # If not, run through normal process.

        # Nottin' on you.
        body = None
        content_type = None

        if not data and json is not None:
            # urllib3 requires a bytes-like body. Python 2's json.dumps
            # provides this natively, but Python 3 gives a Unicode string.
            content_type = "application/json"

            try:
                body = complexjson.dumps(json, allow_nan=False)
            except ValueError as ve:
                raise InvalidJSONError(ve, request=self)

            if not isinstance(body, bytes):
                body = body.encode("utf-8")

        is_stream = all(
            [
                hasattr(data, "__iter__"),
                not isinstance(data, (basestring, list, tuple, Mapping)),
            ]
        )

        if is_stream:
            try:
                length = super_len(data)
            except (TypeError, AttributeError, UnsupportedOperation):
                length = None

            body = data

            if getattr(body, "tell", None) is not None:
                # Record the current file position before reading.
                # This will allow us to rewind a file in the event
                # of a redirect.
                try:
                    self._body_position = body.tell()
                except OSError:
                    # This differentiates from None, allowing us to catch
                    # a failed `tell()` later when trying to rewind the body
                    self._body_position = object()

            if files:
                raise NotImplementedError(
                    "Streamed bodies and files are mutually exclusive."
                )

            if length:
                self.headers["Content-Length"] = builtin_str(length)
            else:
                self.headers["Transfer-Encoding"] = "chunked"
        else:
            # Multi-part file uploads.
... (17 more line(s) truncated)
```

**With:**

```python
    def prepare_body(self, data, files, json=None):
        """Prepares the given HTTP body data."""
        body = None
        content_type = None

        if not data and json is not None:
            content_type = "application/json"
            try:
                body = complexjson.dumps(json, allow_nan=False)
            except ValueError as ve:
                raise InvalidJSONError(ve, request=self)
            if not isinstance(body, bytes):
                body = body.encode("utf-8")
        elif files:
            (body, content_type) = self._encode_files(files, data)
        elif data:
            is_stream = all([
                hasattr(data, "__iter__"),
                not isinstance(data, (basestring, list, tuple, Mapping)),
            ])
            if is_stream:
                try:
                    length = super_len(data)
                except (TypeError, AttributeError, UnsupportedOperation):
                    length = None
                body = data
                if getattr(body, "tell", None) is not None:
                    try:
                        self._body_position = body.tell()
                    except OSError:
                        self._body_position = object()
                if length:
                    self.headers["Content-Length"] = builtin_str(length)
                else:
                    self.headers["Transfer-Encoding"] = "chunked"
            else:
                body = self._encode_params(data)
                if not isinstance(data, basestring) and not hasattr(data, "read"):
                    content_type = "application/x-www-form-urlencoded"

        self.body = body
        if body is not None:
            self.prepare_content_length(body)
            if content_type and ("content-type" not in self.headers):
                self.headers["Content-Type"] = content_type
```

## Test results

**FAILED** — 41/42 passed, 1 failed, 0 skipped, 0 errored (duration 62191 ms).

- New failures introduced by this refactor: **1**
- Pre-existing failures (unrelated to this refactor): **0**

New-failure node IDs (first 25):

  - `tests/test_requests.py::TestRequests::test_no_body_content_length[POST]`

Command: `C:\Users\User\Desktop\SDP-Codex\S1-T7-Okeyish\refactor_workspaces\requests\.venv\Scripts\python.exe -m pytest --tb=short -q --no-header -p no:cacheprovider -x --json-report --json-report-file=C:\Users\User\Desktop\SDP-Codex\S1-T7-Okeyish\refactor_workspaces\requests\.pytest_report.json --deselect=tests/test_requests.py::TestPreparingURLs::test_different_connection_pool_for_tls_settings_verify_bundle_unexpired_cert`

<details><summary>Output tail</summary>

```
.........................................F
================================== FAILURES ===================================
_______________ TestRequests.test_no_body_content_length[POST] ________________
tests\test_requests.py:132: in test_no_body_content_length
    assert req.headers["Content-Length"] == "0"
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src\requests\structures.py:52: in __getitem__
    return self._store[key.lower()][1]
           ^^^^^^^^^^^^^^^^^^^^^^^^
E   KeyError: 'content-length'
=========================== short test summary info ===========================
FAILED tests/test_requests.py::TestRequests::test_no_body_content_length[POST]
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!
1 failed, 41 passed, 1 deselected in 61.42s (0:01:01)

```

</details>

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/requests/models.py` | 747 → - | 47 → - | 4.18 → - | 19 → - | 21.48 → - |

## Diff

```diff
diff --git a/src/requests/models.py b/src/requests/models.py
index f63e59b..2666f87 100644
--- a/src/requests/models.py
+++ b/src/requests/models.py
@@ -487,82 +487,50 @@ class PreparedRequest(RequestEncodingMixin, RequestHooksMixin):
 
     def prepare_body(self, data, files, json=None):
         """Prepares the given HTTP body data."""
-
-        # Check if file, fo, generator, iterator.
-        # If not, run through normal process.
-
-        # Nottin' on you.
         body = None
         content_type = None
 
         if not data and json is not None:
-            # urllib3 requires a bytes-like body. Python 2's json.dumps
-            # provides this natively, but Python 3 gives a Unicode string.
             content_type = "application/json"
-
             try:
                 body = complexjson.dumps(json, allow_nan=False)
             except ValueError as ve:
                 raise InvalidJSONError(ve, request=self)
-
             if not isinstance(body, bytes):
                 body = body.encode("utf-8")
-
-        is_stream = all(
-            [
+        elif files:
+            (body, content_type) = self._encode_files(files, data)
+        elif data:
+            is_stream = all([
                 hasattr(data, "__iter__"),
                 not isinstance(data, (basestring, list, tuple, Mapping)),
-            ]
-        )
-
-        if is_stream:
-            try:
-                length = super_len(data)
-            except (TypeError, AttributeError, UnsupportedOperation):
-                length = None
-
-            body = data
-
-            if getattr(body, "tell", None) is not None:
-                # Record the current file position before reading.
-                # This will allow us to rewind a file in the event
-                # of a redirect.
+            ])
+            if is_stream:
                 try:
-                    self._body_position = body.tell()
-                except OSError:
-                    # This differentiates from None, allowing us to catch
-                    # a failed `tell()` later when trying to rewind the body
-                    self._body_position = object()
-
-            if files:
-                raise NotImplementedError(
-                    "Streamed bodies and files are mutually exclusive."
-                )
-
-            if length:
-                self.headers["Content-Length"] = builtin_str(length)
-            else:
-                self.headers["Transfer-Encoding"] = "chunked"
-        else:
-            # Multi-part file uploads.
-            if files:
-                (body, content_type) = self._encode_files(files, data)
+                    length = super_len(data)
+                except (TypeError, AttributeError, UnsupportedOperation):
+                    length = None
+                body = data
+                if getattr(body, "tell", None) is not None:
+                    try:
+                        self._body_position = body.tell()
+                    except OSError:
+                        self._body_position = object()
+                if length:
+                    self.headers["Content-Length"] = builtin_str(length)
+                else:
+                    self.headers["Transfer-Encoding"] = "chunked"
             else:
-                if data:
-                    body = self._encode_params(data)
-                    if isinstance(data, basestring) or hasattr(data, "read"):
-                        content_type = None
-                    else:
-                        content_type = "application/x-www-form-urlencoded"
+                body = self._encode_params(data)
+                if not isinstance(data, basestring) and not hasattr(data, "read"):
+                    content_type = "application/x-www-form-urlencoded"
 
+        self.body = body
+        if body is not None:
             self.prepare_content_length(body)
-
-            # Add content-type if it wasn't explicitly provided.
             if content_type and ("content-type" not in self.headers):
                 self.headers["Content-Type"] = content_type
 
-        self.body = body
-
     def prepare_content_length(self, body):
         """Prepare Content-Length header based on request method and body"""
         if body is not None:

```
