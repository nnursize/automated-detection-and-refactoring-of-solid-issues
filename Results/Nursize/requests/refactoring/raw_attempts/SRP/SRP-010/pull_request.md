# Refactor SRP-010 (SRP): Iterates over raw response data, handles streaming, decodes unicode, and catc...

**Status:** `applied_passed`  
**Branch:** `refactor/SRP-010` -> `main`  
**Head commit:** `fee6776a86057ca49096021ed1cbe5150b2812d8`  
**LLM finish:** `FinishReason.STOP` (prompt 9962, completion 1188)  

## Detected issue

- **File**: `src/requests/models.py`
- **Entity**: `Response.iter_content` (method)
- **Lines (at detection time)**: L507–L554
- **Severity**: medium
- **Confidence**: detected by 4 scan(s)

**Description.** Iterates over raw response data, handles streaming, decodes unicode, and catches/re-raises various urllib3 exceptions.

**Reasoning.** This method combines several responsibilities: 1) Iterating over the raw response stream (from `self.raw.stream` or a file-like object). 2) Managing the `_content_consumed` state and raising `StreamConsumedError`. 3) Validating `chunk_size`. 4) Conditionally decoding unicode (delegating to `stream_decode_response_unicode`). 5) Catching and re-raising a wide array of `urllib3` exceptions as `requests` exceptions. The core iteration logic, error handling, and conditional decoding are distinct concerns.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `src/requests/models.py`

**Summary.** Extract raw stream iteration logic from Response.iter_content into a private helper method.

**Rationale.** The iter_content method was violating SRP by handling both the high-level state management/validation and the low-level raw stream iteration/exception mapping. Extracting the iteration logic into _iter_raw_stream clarifies the responsibilities and makes the code more maintainable.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `src/requests/models.py` (57-line block → 58-line replacement)

**Replaces:**

```python
    def iter_content(self, chunk_size=1, decode_unicode=False):
        """Iterates over the response data.  When stream=True is set on the
        request, this avoids reading the content at once into memory for
        large responses.  The chunk size is the number of bytes it should
        read into memory.  This is not necessarily the length of each item
        returned as decoding can take place.

        chunk_size must be of type int or None. A value of None will
        function differently depending on the value of `stream`.
        stream=True will read data as it arrives in whatever size the
        chunks are received. If stream=False, data is returned as
        a single chunk.

        If decode_unicode is True, content will be decoded using the best
        available encoding based on the response.
        """

        def generate():
            # Special case for urllib3.
            if hasattr(self.raw, "stream"):
                try:
                    yield from self.raw.stream(chunk_size, decode_content=True)
                except ProtocolError as e:
                    raise ChunkedEncodingError(e)
                except DecodeError as e:
                    raise ContentDecodingError(e)
                except ReadTimeoutError as e:
                    raise ConnectionError(e)
                except SSLError as e:
                    raise RequestsSSLError(e)
            else:
                # Standard file-like object.
                while True:
                    chunk = self.raw.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk

            self._content_consumed = True

        if self._content_consumed and isinstance(self._content, bool):
            raise StreamConsumedError()
        elif chunk_size is not None and not isinstance(chunk_size, int):
            raise TypeError(
                f"chunk_size must be an int, it is instead a {type(chunk_size)}."
            )
        # simulate reading small chunks of the content
        reused_chunks = iter_slices(self._content, chunk_size)

        stream_chunks = generate()

        chunks = reused_chunks if self._content_consumed else stream_chunks

        if decode_unicode:
            chunks = stream_decode_response_unicode(chunks, self)

        return chunks
```

**With:**

```python
    def _iter_raw_stream(self, chunk_size):
        """Iterates over the raw response stream."""
        # Special case for urllib3.
        if hasattr(self.raw, "stream"):
            try:
                yield from self.raw.stream(chunk_size, decode_content=True)
            except ProtocolError as e:
                raise ChunkedEncodingError(e)
            except DecodeError as e:
                raise ContentDecodingError(e)
            except ReadTimeoutError as e:
                raise ConnectionError(e)
            except SSLError as e:
                raise RequestsSSLError(e)
        else:
            # Standard file-like object.
            while True:
                chunk = self.raw.read(chunk_size)
                if not chunk:
                    break
                yield chunk

        self._content_consumed = True

    def iter_content(self, chunk_size=1, decode_unicode=False):
        """Iterates over the response data.  When stream=True is set on the
        request, this avoids reading the content at once into memory for
        large responses.  The chunk size is the number of bytes it should
        read into memory.  This is not necessarily the length of each item
        returned as decoding can take place.

        chunk_size must be of type int or None. A value of None will
        function differently depending on the value of `stream`.
        stream=True will read data as it arrives in whatever size the
        chunks are received. If stream=False, data is returned as
        a single chunk.

        If decode_unicode is True, content will be decoded using the best
        available encoding based on the response.
        """

        if self._content_consumed and isinstance(self._content, bool):
            raise StreamConsumedError()
        elif chunk_size is not None and not isinstance(chunk_size, int):
            raise TypeError(
                f"chunk_size must be an int, it is instead a {type(chunk_size)}."
            )
        # simulate reading small chunks of the content
        reused_chunks = iter_slices(self._content, chunk_size)

        stream_chunks = self._iter_raw_stream(chunk_size)

        chunks = reused_chunks if self._content_consumed else stream_chunks

        if decode_unicode:
            chunks = stream_decode_response_unicode(chunks, self)

        return chunks
```

## Test results

**PASSED** — 606/610 passed, 0 failed, 3 skipped, 0 errored (duration 165971 ms).

Command: `C:\Users\User\Desktop\SDP-Codex\S1-T7-Okeyish\refactor_workspaces\requests\.venv\Scripts\python.exe -m pytest --tb=short -q --no-header -p no:cacheprovider -x --json-report --json-report-file=C:\Users\User\Desktop\SDP-Codex\S1-T7-Okeyish\refactor_workspaces\requests\.pytest_report.json --deselect=tests/test_requests.py::TestPreparingURLs::test_different_connection_pool_for_tls_settings_verify_bundle_unexpired_cert`

<details><summary>Output tail</summary>

```
........................................................................ [ 11%]
........................................................................ [ 23%]
......spytest-httpbin server hit an exception serving request: [SSL: TLSV1_ALERT_UNKNOWN_CA] tlsv1 alert unknown ca (_ssl.c:1006)
attempting to ignore so the rest of the tests can run
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
127.0.0.1 - - [04/May/2026 12:39:37] "GET /html HTTP/1.1" 200 3741

```

</details>

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/requests/models.py` | 745 → 746 | 45 → 45 | 4.39 → 4.46 | 21 → 21 | 21.22 → 20.13 |

## Diff

```diff
diff --git a/src/requests/models.py b/src/requests/models.py
index 6c69679..1264d02 100644
--- a/src/requests/models.py
+++ b/src/requests/models.py
@@ -785,6 +785,30 @@ class Response:
             # to a standard Python utf-8 str.
             return "utf-8"
 
+    def _iter_raw_stream(self, chunk_size):
+        """Iterates over the raw response stream."""
+        # Special case for urllib3.
+        if hasattr(self.raw, "stream"):
+            try:
+                yield from self.raw.stream(chunk_size, decode_content=True)
+            except ProtocolError as e:
+                raise ChunkedEncodingError(e)
+            except DecodeError as e:
+                raise ContentDecodingError(e)
+            except ReadTimeoutError as e:
+                raise ConnectionError(e)
+            except SSLError as e:
+                raise RequestsSSLError(e)
+        else:
+            # Standard file-like object.
+            while True:
+                chunk = self.raw.read(chunk_size)
+                if not chunk:
+                    break
+                yield chunk
+
+        self._content_consumed = True
+
     def iter_content(self, chunk_size=1, decode_unicode=False):
         """Iterates over the response data.  When stream=True is set on the
         request, this avoids reading the content at once into memory for
@@ -802,29 +826,6 @@ class Response:
         available encoding based on the response.
         """
 
-        def generate():
-            # Special case for urllib3.
-            if hasattr(self.raw, "stream"):
-                try:
-                    yield from self.raw.stream(chunk_size, decode_content=True)
-                except ProtocolError as e:
-                    raise ChunkedEncodingError(e)
-                except DecodeError as e:
-                    raise ContentDecodingError(e)
-                except ReadTimeoutError as e:
-                    raise ConnectionError(e)
-                except SSLError as e:
-                    raise RequestsSSLError(e)
-            else:
-                # Standard file-like object.
-                while True:
-                    chunk = self.raw.read(chunk_size)
-                    if not chunk:
-                        break
-                    yield chunk
-
-            self._content_consumed = True
-
         if self._content_consumed and isinstance(self._content, bool):
             raise StreamConsumedError()
         elif chunk_size is not None and not isinstance(chunk_size, int):
@@ -834,7 +835,7 @@ class Response:
         # simulate reading small chunks of the content
         reused_chunks = iter_slices(self._content, chunk_size)
 
-        stream_chunks = generate()
+        stream_chunks = self._iter_raw_stream(chunk_size)
 
         chunks = reused_chunks if self._content_consumed else stream_chunks
 

```
