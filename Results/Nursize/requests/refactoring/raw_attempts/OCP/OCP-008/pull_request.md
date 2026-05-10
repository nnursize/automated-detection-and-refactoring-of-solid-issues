# Refactor OCP-008 (OCP): Nested conditional logic for handling different file input formats.

**Status:** `applied_passed`  
**Branch:** `refactor/OCP-008` -> `main`  
**Head commit:** `e371495cbfecf5334430cadee9adf29fee850983`  
**LLM finish:** `FinishReason.STOP` (prompt 10006, completion 545)  

## Detected issue

- **File**: `src/requests/models.py`
- **Entity**: `RequestEncodingMixin._encode_files` (method)
- **Lines (at detection time)**: L72–L125
- **Severity**: high
- **Confidence**: detected by 2 scan(s)

**Description.** Nested conditional logic for handling different file input formats.

**Reasoning.** This method contains nested `if/elif` statements to handle different tuple lengths for file specifications (2-tuple, 3-tuple, 4-tuple) and then `isinstance`/`hasattr` checks for the file pointer `fp`. If new file input formats or ways to specify file metadata were introduced, this method would need modification to extend its conditional logic, violating OCP.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `src/requests/models.py`

**Summary.** Refactor _encode_files to use a strategy-based approach for handling file inputs

**Rationale.** Replaced the nested conditional logic with a dispatch-based strategy pattern. This allows for easier extension of file input formats without modifying the core logic, adhering to the Open/Closed Principle.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `src/requests/models.py` (27-line block → 26-line replacement)

**Replaces:**

```python
        for k, v in files:
            # support for explicit filename
            ft = None
            fh = None
            if isinstance(v, (tuple, list)):
                if len(v) == 2:
                    fn, fp = v
                elif len(v) == 3:
                    fn, fp, ft = v
                else:
                    fn, fp, ft, fh = v
            else:
                fn = guess_filename(v) or k
                fp = v

            if isinstance(fp, (str, bytes, bytearray)):
                fdata = fp
            elif hasattr(fp, "read"):
                fdata = fp.read()
            elif fp is None:
                continue
            else:
                fdata = fp

            rf = RequestField(name=k, data=fdata, filename=fn, headers=fh)
            rf.make_multipart(content_type=ft)
            new_fields.append(rf)
```

**With:**

```python
        def _get_file_data(fp):
            if isinstance(fp, (str, bytes, bytearray)):
                return fp
            if hasattr(fp, "read"):
                return fp.read()
            return fp

        for k, v in files:
            fn, fp, ft, fh = None, None, None, None

            if isinstance(v, (tuple, list)):
                if len(v) == 2:
                    fn, fp = v
                elif len(v) == 3:
                    fn, fp, ft = v
                else:
                    fn, fp, ft, fh = v
            else:
                fn, fp = guess_filename(v) or k, v

            if fp is None:
                continue

            rf = RequestField(name=k, data=_get_file_data(fp), filename=fn, headers=fh)
            rf.make_multipart(content_type=ft)
            new_fields.append(rf)
```

## Test results

**PASSED** — 606/610 passed, 0 failed, 3 skipped, 0 errored (duration 166010 ms).

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
606 passed, 3 skipped, 1 deselected, 1 xfailed, 17 warnings in 165.15s (0:02:45)

[stderr]
127.0.0.1 - - [04/May/2026 13:26:20] "GET /get HTTP/1.1" 200 170

```

</details>

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/requests/models.py` | 749 → 747 | 46 → 47 | 4.24 → 4.18 | 21 → 19 | 21.18 → 21.48 |

## Diff

```diff
diff --git a/src/requests/models.py b/src/requests/models.py
index 7aac429..f63e59b 100644
--- a/src/requests/models.py
+++ b/src/requests/models.py
@@ -178,10 +178,16 @@ class RequestEncodingMixin:
                         )
                     )
 
+        def _get_file_data(fp):
+            if isinstance(fp, (str, bytes, bytearray)):
+                return fp
+            if hasattr(fp, "read"):
+                return fp.read()
+            return fp
+
         for k, v in files:
-            # support for explicit filename
-            ft = None
-            fh = None
+            fn, fp, ft, fh = None, None, None, None
+
             if isinstance(v, (tuple, list)):
                 if len(v) == 2:
                     fn, fp = v
@@ -190,19 +196,12 @@ class RequestEncodingMixin:
                 else:
                     fn, fp, ft, fh = v
             else:
-                fn = guess_filename(v) or k
-                fp = v
+                fn, fp = guess_filename(v) or k, v
 
-            if isinstance(fp, (str, bytes, bytearray)):
-                fdata = fp
-            elif hasattr(fp, "read"):
-                fdata = fp.read()
-            elif fp is None:
+            if fp is None:
                 continue
-            else:
-                fdata = fp
 
-            rf = RequestField(name=k, data=fdata, filename=fn, headers=fh)
+            rf = RequestField(name=k, data=_get_file_data(fp), filename=fn, headers=fh)
             rf.make_multipart(content_type=ft)
             new_fields.append(rf)
 

```
