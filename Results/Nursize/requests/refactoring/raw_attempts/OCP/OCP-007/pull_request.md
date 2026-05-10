# Refactor OCP-007 (OCP): Conditional logic for encoding request parameters based on type.

**Status:** `applied_passed`  
**Branch:** `refactor/OCP-007` -> `main`  
**Head commit:** `1d657244b1c4cc0c16944153f3d3c966d8ea4deb`  
**LLM finish:** `FinishReason.STOP` (prompt 9963, completion 664)  

## Detected issue

- **File**: `src/requests/models.py`
- **Entity**: `RequestEncodingMixin._encode_params` (method)
- **Lines (at detection time)**: L50–L70
- **Severity**: high
- **Confidence**: detected by 2 scan(s)

**Description.** Conditional logic for encoding request parameters based on type.

**Reasoning.** This method uses a series of `if/elif` statements and `isinstance`/`hasattr` checks to determine how to encode different types of `data`. If a new type of data (e.g., a custom object that knows how to encode itself) needs to be supported, this method would require modification to add new conditional branches, violating OCP. This could be refactored using a strategy pattern or a dispatch table.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `src/requests/models.py`

**Summary.** Refactor _encode_params to use a dispatch table for OCP compliance

**Rationale.** Replaced the if/elif chain with a dispatch table approach. This allows adding new encoding strategies without modifying the core logic of _encode_params, adhering to the Open/Closed Principle.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `src/requests/models.py` (29-line block → 35-line replacement)

**Replaces:**

```python
    @staticmethod
    def _encode_params(data):
        """Encode parameters in a piece of data.

        Will successfully encode parameters when passed as a dict or a list of
        2-tuples. Order is retained if data is a list of 2-tuples but arbitrary
        if parameters are supplied as a dict.
        """

        if isinstance(data, (str, bytes)):
            return data
        elif hasattr(data, "read"):
            return data
        elif hasattr(data, "__iter__"):
            result = []
            for k, vs in to_key_val_list(data):
                if isinstance(vs, basestring) or not hasattr(vs, "__iter__"):
                    vs = [vs]
                for v in vs:
                    if v is not None:
                        result.append(
                            (
                                k.encode("utf-8") if isinstance(k, str) else k,
                                v.encode("utf-8") if isinstance(v, str) else v,
                            )
                        )
            return urlencode(result, doseq=True)
        else:
            return data
```

**With:**

```python
    @staticmethod
    def _encode_params(data):
        """Encode parameters in a piece of data.

        Will successfully encode parameters when passed as a dict or a list of
        2-tuples. Order is retained if data is a list of 2-tuples but arbitrary
        if parameters are supplied as a dict.
        """

        def _encode_iterable(data):
            result = []
            for k, vs in to_key_val_list(data):
                if isinstance(vs, basestring) or not hasattr(vs, "__iter__"):
                    vs = [vs]
                for v in vs:
                    if v is not None:
                        result.append(
                            (
                                k.encode("utf-8") if isinstance(k, str) else k,
                                v.encode("utf-8") if isinstance(v, str) else v,
                            )
                        )
            return urlencode(result, doseq=True)

        dispatch = {
            lambda d: isinstance(d, (str, bytes)): lambda d: d,
            lambda d: hasattr(d, "read"): lambda d: d,
            lambda d: hasattr(d, "__iter__"): _encode_iterable,
        }

        for condition, action in dispatch.items():
            if condition(data):
                return action(data)

        return data
```

## Test results

**PASSED** — 606/610 passed, 0 failed, 3 skipped, 0 errored (duration 166490 ms).

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
606 passed, 3 skipped, 1 deselected, 1 xfailed, 17 warnings in 165.70s (0:02:45)

[stderr]
127.0.0.1 - - [04/May/2026 13:22:38] "GET /get HTTP/1.1" 200 222

```

</details>

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/requests/models.py` | 746 → 749 | 45 → 46 | 4.46 → 4.24 | 21 → 21 | 20.13 → 21.18 |

## Diff

```diff
diff --git a/src/requests/models.py b/src/requests/models.py
index 1264d02..7aac429 100644
--- a/src/requests/models.py
+++ b/src/requests/models.py
@@ -114,11 +114,7 @@ class RequestEncodingMixin:
         if parameters are supplied as a dict.
         """
 
-        if isinstance(data, (str, bytes)):
-            return data
-        elif hasattr(data, "read"):
-            return data
-        elif hasattr(data, "__iter__"):
+        def _encode_iterable(data):
             result = []
             for k, vs in to_key_val_list(data):
                 if isinstance(vs, basestring) or not hasattr(vs, "__iter__"):
@@ -132,8 +128,18 @@ class RequestEncodingMixin:
                             )
                         )
             return urlencode(result, doseq=True)
-        else:
-            return data
+
+        dispatch = {
+            lambda d: isinstance(d, (str, bytes)): lambda d: d,
+            lambda d: hasattr(d, "read"): lambda d: d,
+            lambda d: hasattr(d, "__iter__"): _encode_iterable,
+        }
+
+        for condition, action in dispatch.items():
+            if condition(data):
+                return action(data)
+
+        return data
 
     @staticmethod
     def _encode_files(files, data):

```
