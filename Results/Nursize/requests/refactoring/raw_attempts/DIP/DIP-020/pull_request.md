# Refactor DIP-020 (DIP): Direct dependency on concrete `urllib3` implementations for multipart form da...

**Status:** `applied_passed`  
**Branch:** `refactor/DIP-020` -> `main`  
**Head commit:** `2438f1af4c906d0cb8147a99e660d67493be677b`  
**LLM finish:** `FinishReason.STOP` (prompt 10229, completion 396)  

## Detected issue

- **File**: `src/requests/models.py`
- **Entity**: `RequestEncodingMixin._encode_files` (method)
- **Lines (at detection time)**: L69–L111
- **Severity**: high
- **Confidence**: detected by 1 scan(s)

**Description.** Direct dependency on concrete `urllib3` implementations for multipart form data encoding.

**Reasoning.** The `RequestEncodingMixin._encode_files` method, a core component for preparing request bodies, directly uses `urllib3.fields.RequestField` and `urllib3.filepost.encode_multipart_formdata`. This tightly couples `requests`'s request preparation logic to specific, low-level `urllib3` implementations for handling multipart form data, making it rigid to changes in the underlying HTTP library.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 2
- **Files modified** (1): `src/requests/models.py`

**Summary.** Abstract multipart encoding logic to decouple from urllib3

**Rationale.** The RequestEncodingMixin was directly dependent on urllib3's internal classes and functions. By introducing a helper method that acts as an abstraction layer, we isolate the dependency. This allows for easier swapping of the underlying multipart implementation in the future without modifying the core request preparation logic.

## Changes overview

_2 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `src/requests/models.py` (3-line block → 7-line replacement)

**Replaces:**

```python
from urllib3.fields import RequestField
from urllib3.filepost import encode_multipart_formdata
from urllib3.util import parse_url
```

**With:**

```python
from urllib3.fields import RequestField
from urllib3.filepost import encode_multipart_formdata
from urllib3.util import parse_url

def _encode_multipart_data(fields):
    """Abstraction for encoding multipart form data."""
    return encode_multipart_formdata(fields)
```

### 2. EDIT `src/requests/models.py` (7-line block → 7-line replacement)

**Replaces:**

```python
            rf = RequestField(name=k, data=_get_file_data(fp), filename=fn, headers=fh)
            rf.make_multipart(content_type=ft)
            new_fields.append(rf)

        body, content_type = encode_multipart_formdata(new_fields)

        return body, content_type
```

**With:**

```python
            rf = RequestField(name=k, data=_get_file_data(fp), filename=fn, headers=fh)
            rf.make_multipart(content_type=ft)
            new_fields.append(rf)

        body, content_type = _encode_multipart_data(new_fields)

        return body, content_type
```

## Test results

**PASSED** — 606/610 passed, 0 failed, 3 skipped, 0 errored (duration 165096 ms).

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
606 passed, 3 skipped, 1 deselected, 1 xfailed, 17 warnings in 164.25s (0:02:44)

[stderr]
127.0.0.1 - - [04/May/2026 15:14:35] "POST /post HTTP/1.1" 200 289
127.0.0.1 - - [04/May/2026 15:14:35] "POST /post HTTP/1.1" 200 351
127.0.0.1 - - [04/May/2026 15:14:35] "GET /status/404 HTTP/1.1" 404 0
127.0.0.1 - - [04/May/2026 15:14:35] "GET / HTTP/1.1" 200 9509

```

</details>

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/requests/models.py` | 765 → 768 | 51 → 52 | 3.88 → 3.83 | 19 → 19 | 20.13 → 20.06 |

## Diff

```diff
diff --git a/src/requests/models.py b/src/requests/models.py
index c37ae71..4048e98 100644
--- a/src/requests/models.py
+++ b/src/requests/models.py
@@ -24,6 +24,10 @@ from urllib3.fields import RequestField
 from urllib3.filepost import encode_multipart_formdata
 from urllib3.util import parse_url
 
+def _encode_multipart_data(fields):
+    """Abstraction for encoding multipart form data."""
+    return encode_multipart_formdata(fields)
+
 from ._internal_utils import to_native_string, unicode_is_ascii
 from .auth import HTTPBasicAuth
 from .compat import (
@@ -205,7 +209,7 @@ class RequestEncodingMixin:
             rf.make_multipart(content_type=ft)
             new_fields.append(rf)
 
-        body, content_type = encode_multipart_formdata(new_fields)
+        body, content_type = _encode_multipart_data(new_fields)
 
         return body, content_type
 

```
