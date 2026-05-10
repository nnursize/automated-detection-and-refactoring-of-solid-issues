# Refactor OCP-022 (OCP): Function uses multiple hasattr checks to handle different object types

**Status:** `applied_passed`  
**Branch:** `refactor/OCP-022` -> `main`  
**Head commit:** `380714d4acc73557af3763195c3cf77746a61428`  
**LLM finish:** `FinishReason.STOP` (prompt 10519, completion 1289)  

## Detected issue

- **File**: `src/requests/utils.py`
- **Entity**: `super_len` (class)
- **Lines (at detection time)**: L135–L207
- **Severity**: medium
- **Confidence**: detected by 5 scan(s)

**Description.** Function uses multiple hasattr checks to handle different object types

**Reasoning.** The function calculates object length by checking for various attributes (__len__, len, fileno, tell, seek). Supporting a new type of stream or custom object with a unique way to determine length would require adding more conditional branches to this utility.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `src/requests/utils.py`

**Summary.** Refactor super_len to use a registry-based strategy pattern for OCP compliance.

**Rationale.** Replaced the hardcoded if/elif chain with a registry of length-calculating strategies. This allows adding support for new types by registering a new handler without modifying the core logic of super_len.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `src/requests/utils.py` (69-line block → 65-line replacement)

**Replaces:**

```python
def super_len(o):
    total_length = None
    current_position = 0

    if not is_urllib3_1 and isinstance(o, str):
        # urllib3 2.x+ treats all strings as utf-8 instead
        # of latin-1 (iso-8859-1) like http.client.
        o = o.encode("utf-8")

    if hasattr(o, "__len__"):
        total_length = len(o)

    elif hasattr(o, "len"):
        total_length = o.len

    elif hasattr(o, "fileno"):
        try:
            fileno = o.fileno()
        except (io.UnsupportedOperation, AttributeError):
            # AttributeError is a surprising exception, seeing as how we've just checked
            # that `hasattr(o, 'fileno')`.  It happens for objects obtained via
            # `Tarfile.extractfile()`, per issue 5229.
            pass
        else:
            total_length = os.fstat(fileno).st_size

            # Having used fstat to determine the file length, we need to
            # confirm that this file was opened up in binary mode.
            if "b" not in o.mode:
                warnings.warn(
                    (
                        "Requests has determined the content-length for this "
                        "request using the binary size of the file: however, the "
                        "file has been opened in text mode (i.e. without the 'b' "
                        "flag in the mode). This may lead to an incorrect "
                        "content-length. In Requests 3.0, support will be removed "
                        "for files in text mode."
                    ),
                    FileModeWarning,
                )

    if hasattr(o, "tell"):
        try:
            current_position = o.tell()
        except OSError:
            # This can happen in some weird situations, such as when the file
            # is actually a special file descriptor like stdin. In this
            # instance, we don't know what the length is, so set it to zero and
            # let requests chunk it instead.
            if total_length is not None:
                current_position = total_length
        else:
            if hasattr(o, "seek") and total_length is None:
                # StringIO and BytesIO have seek but no usable fileno
                try:
                    # seek to end of file
                    o.seek(0, 2)
                    total_length = o.tell()

                    # seek back to current position to support
... (9 more line(s) truncated)
```

**With:**

```python
def _len_len(o):
    return len(o)


def _len_attr(o):
    return o.len


def _len_file(o):
    try:
        fileno = o.fileno()
    except (io.UnsupportedOperation, AttributeError):
        return None
    total_length = os.fstat(fileno).st_size
    if "b" not in o.mode:
        warnings.warn(
            (
                "Requests has determined the content-length for this "
                "request using the binary size of the file: however, the "
                "file has been opened in text mode (i.e. without the 'b' "
                "flag in the mode). This may lead to an incorrect "
                "content-length. In Requests 3.0, support will be removed "
                "for files in text mode."
            ),
            FileModeWarning,
        )
    return total_length


_LENGTH_STRATEGIES = [
    (lambda o: hasattr(o, "__len__"), _len_len),
    (lambda o: hasattr(o, "len"), _len_attr),
    (lambda o: hasattr(o, "fileno"), _len_file),
]


def super_len(o):
    total_length = None
    current_position = 0

    if not is_urllib3_1 and isinstance(o, str):
        o = o.encode("utf-8")

    for predicate, strategy in _LENGTH_STRATEGIES:
        if predicate(o):
            total_length = strategy(o)
            if total_length is not None:
                break

    if hasattr(o, "tell"):
        try:
            current_position = o.tell()
        except OSError:
            if total_length is not None:
                current_position = total_length
        else:
            if hasattr(o, "seek") and total_length is None:
                try:
                    o.seek(0, 2)
                    total_length = o.tell()
... (5 more line(s) truncated)
```

## Test results

**PASSED** — 606/610 passed, 0 failed, 3 skipped, 0 errored (duration 165983 ms).

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
  C:\Users\User\Desktop\SDP-Codex\S1-T7-Okeyish\refactor_workspaces\requests\src\requests\utils.py:478: DeprecationWarning: In requests 3.0, get_encodings_from_content will be removed. For more information, please see the discussion on issue #2266. (This warning should only appear once.)
    warnings.warn(

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
606 passed, 3 skipped, 1 deselected, 1 xfailed, 17 warnings in 165.22s (0:02:45)

[stderr]
127.0.0.1 - - [04/May/2026 12:58:30] "GET /get HTTP/1.1" 200 257

```

</details>

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/requests/utils.py` | 769 → 777 | 43 → 46 | 4.55 → 4.29 | 18 → 17 | 25.21 → 25.03 |

## Diff

```diff
diff --git a/src/requests/utils.py b/src/requests/utils.py
index 4d3039b..3938a2c 100644
--- a/src/requests/utils.py
+++ b/src/requests/utils.py
@@ -131,75 +131,71 @@ def dict_to_sequence(d):
     return d
 
 
+def _len_len(o):
+    return len(o)
+
+
+def _len_attr(o):
+    return o.len
+
+
+def _len_file(o):
+    try:
+        fileno = o.fileno()
+    except (io.UnsupportedOperation, AttributeError):
+        return None
+    total_length = os.fstat(fileno).st_size
+    if "b" not in o.mode:
+        warnings.warn(
+            (
+                "Requests has determined the content-length for this "
+                "request using the binary size of the file: however, the "
+                "file has been opened in text mode (i.e. without the 'b' "
+                "flag in the mode). This may lead to an incorrect "
+                "content-length. In Requests 3.0, support will be removed "
+                "for files in text mode."
+            ),
+            FileModeWarning,
+        )
+    return total_length
+
+
+_LENGTH_STRATEGIES = [
+    (lambda o: hasattr(o, "__len__"), _len_len),
+    (lambda o: hasattr(o, "len"), _len_attr),
+    (lambda o: hasattr(o, "fileno"), _len_file),
+]
+
+
 def super_len(o):
     total_length = None
     current_position = 0
 
     if not is_urllib3_1 and isinstance(o, str):
-        # urllib3 2.x+ treats all strings as utf-8 instead
-        # of latin-1 (iso-8859-1) like http.client.
         o = o.encode("utf-8")
 
-    if hasattr(o, "__len__"):
-        total_length = len(o)
-
-    elif hasattr(o, "len"):
-        total_length = o.len
-
-    elif hasattr(o, "fileno"):
-        try:
-            fileno = o.fileno()
-        except (io.UnsupportedOperation, AttributeError):
-            # AttributeError is a surprising exception, seeing as how we've just checked
-            # that `hasattr(o, 'fileno')`.  It happens for objects obtained via
-            # `Tarfile.extractfile()`, per issue 5229.
-            pass
-        else:
-            total_length = os.fstat(fileno).st_size
-
-            # Having used fstat to determine the file length, we need to
-            # confirm that this file was opened up in binary mode.
-            if "b" not in o.mode:
-                warnings.warn(
-                    (
-                        "Requests has determined the content-length for this "
-                        "request using the binary size of the file: however, the "
-                        "file has been opened in text mode (i.e. without the 'b' "
-                        "flag in the mode). This may lead to an incorrect "
-                        "content-length. In Requests 3.0, support will be removed "
-                        "for files in text mode."
-                    ),
-                    FileModeWarning,
-                )
+    for predicate, strategy in _LENGTH_STRATEGIES:
+        if predicate(o):
+            total_length = strategy(o)
+            if total_length is not None:
+                break
 
     if hasattr(o, "tell"):
         try:
             current_position = o.tell()
         except OSError:
-            # This can happen in some weird situations, such as when the file
-            # is actually a special file descriptor like stdin. In this
-            # instance, we don't know what the length is, so set it to zero and
-            # let requests chunk it instead.
             if total_length is not None:
                 current_position = total_length
         else:
             if hasattr(o, "seek") and total_length is None:
-                # StringIO and BytesIO have seek but no usable fileno
                 try:
-                    # seek to end of file
                     o.seek(0, 2)
                     total_length = o.tell()
-
-                    # seek back to current position to support
-                    # partially read file-like objects
                     o.seek(current_position or 0)
                 except OSError:
                     total_length = 0
 
-    if total_length is None:
-        total_length = 0
-
-    return max(0, total_length - current_position)
+    return max(0, (total_length or 0) - current_position)
 
 
 def get_netrc_auth(url, raise_errors=False):

```
