# Refactor DIP-008 (DIP): Response directly calls a factory function for a concrete CookieJar implement...

**Status:** `applied_passed`  
**Branch:** `refactor/DIP-008` -> `main`  
**Head commit:** `50680975f2e17f7195f470273598150ace470740`  
**LLM finish:** `FinishReason.STOP` (prompt 10230, completion 816)  

## Detected issue

- **File**: `src/requests/models.py`
- **Entity**: `Response.__init__` (class)
- **Lines (at detection time)**: L506–L506
- **Severity**: low
- **Confidence**: detected by 3 scan(s)

**Description.** Response directly calls a factory function for a concrete CookieJar implementation.

**Reasoning.** The `Response` class directly initializes its `cookies` attribute by calling `cookiejar_from_dict({})`. This factory function returns a `RequestsCookieJar` (a concrete implementation). While it's a direct dependency on a concrete factory and type, the `Response` object fundamentally needs a cookie jar, and `RequestsCookieJar` is a core data structure within Requests. The use of a factory function already provides a level of indirection, making this a less severe violation than direct `new` calls for complex services.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `src/requests/models.py`

**Summary.** Inject cookie jar factory into Response constructor to satisfy DIP

**Rationale.** The Response class was tightly coupled to the concrete cookiejar_from_dict factory. By adding a default argument to the constructor, we allow for dependency injection while maintaining backward compatibility with the existing API.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `src/requests/models.py` (37-line block → 37-line replacement)

**Replaces:**

```python
    def __init__(self):
        self._content = False
        self._content_consumed = False
        self._next = None

        #: Integer Code of responded HTTP Status, e.g. 404 or 200.
        self.status_code = None

        #: Case-insensitive Dictionary of Response Headers.
        #: For example, ``headers['content-encoding']`` will return the
        #: value of a ``'Content-Encoding'`` response header.
        self.headers = CaseInsensitiveDict()

        #: File-like object representation of response (for advanced usage).
        #: Use of ``raw`` requires that ``stream=True`` be set on the request.
        #: This requirement does not apply for use internally to Requests.
        self.raw = None

        #: Final URL location of Response.
        self.url = None

        #: Encoding to decode with when accessing r.text.
        self.encoding = None

        #: A list of :class:`Response <Response>` objects from
        #: the history of the Request. Any redirect responses will end
        #: up here. The list is sorted from the oldest to the most recent request.
        self.history = []

        #: Textual reason of responded HTTP Status, e.g. "Not Found" or "OK".
        self.reason = None

        #: A CookieJar of Cookies the server sent back.
        self.cookies = cookiejar_from_dict({})

        #: The amount of time elapsed between sending the request
        #: and the arrival of the response (as a timedelta).
```

**With:**

```python
    def __init__(self, cookie_jar_factory=cookiejar_from_dict):
        self._content = False
        self._content_consumed = False
        self._next = None

        #: Integer Code of responded HTTP Status, e.g. 404 or 200.
        self.status_code = None

        #: Case-insensitive Dictionary of Response Headers.
        #: For example, ``headers['content-encoding']`` will return the
        #: value of a ``'Content-Encoding'`` response header.
        self.headers = CaseInsensitiveDict()

        #: File-like object representation of response (for advanced usage).
        #: Use of ``raw`` requires that ``stream=True`` be set on the request.
        #: This requirement does not apply for use internally to Requests.
        self.raw = None

        #: Final URL location of Response.
        self.url = None

        #: Encoding to decode with when accessing r.text.
        self.encoding = None

        #: A list of :class:`Response <Response>` objects from
        #: the history of the Request. Any redirect responses will end
        #: up here. The list is sorted from the oldest to the most recent request.
        self.history = []

        #: Textual reason of responded HTTP Status, e.g. "Not Found" or "OK".
        self.reason = None

        #: A CookieJar of Cookies the server sent back.
        self.cookies = cookie_jar_factory({})

        #: The amount of time elapsed between sending the request
        #: and the arrival of the response (as a timedelta).
```

## Test results

**PASSED** — 606/610 passed, 0 failed, 3 skipped, 0 errored (duration 165316 ms).

Command: `C:\Users\User\Desktop\SDP-Codex\S1-T7-Okeyish\refactor_workspaces\requests\.venv\Scripts\python.exe -m pytest --tb=short -q --no-header -p no:cacheprovider -x --json-report --json-report-file=C:\Users\User\Desktop\SDP-Codex\S1-T7-Okeyish\refactor_workspaces\requests\.pytest_report.json --deselect=tests/test_requests.py::TestPreparingURLs::test_different_connection_pool_for_tls_settings_verify_bundle_unexpired_cert`

<details><summary>Output tail</summary>

```
........................................................................ [ 11%]
........................................................................ [ 23%]
......spytest-httpbin server hit an exception serving request: [WinError 10054] An existing connection was forcibly closed by the remote host
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
  C:\Users\User\Desktop\SDP-Codex\S1-T7-Okeyish\refactor_workspaces\requests\src\requests\utils.py:477: DeprecationWarning: In requests 3.0, get_encodings_from_content will be removed. For more information, please see the discussion on issue #2266. (This warning should only appear once.)
    warnings.warn(

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
606 passed, 3 skipped, 1 deselected, 1 xfailed, 17 warnings in 164.41s (0:02:44)

[stderr]
127.0.0.1 - - [04/May/2026 15:00:47] "GET / HTTP/1.1" 200 9509
127.0.0.1 - - [04/May/2026 15:00:47] "GET /get HTTP/1.1" 200 235
127.0.0.1 - - [04/May/2026 15:00:48] "GET /get HTTP/1.1" 200 222

```

</details>

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/requests/models.py` | 765 → 765 | 51 → 51 | 3.88 → 3.88 | 19 → 19 | 20.13 → 20.13 |

## Diff

```diff
diff --git a/src/requests/models.py b/src/requests/models.py
index 9d14d8c..c37ae71 100644
--- a/src/requests/models.py
+++ b/src/requests/models.py
@@ -673,7 +673,7 @@ class Response:
         "request",
     ]
 
-    def __init__(self):
+    def __init__(self, cookie_jar_factory=cookiejar_from_dict):
         self._content = False
         self._content_consumed = False
         self._next = None
@@ -706,7 +706,7 @@ class Response:
         self.reason = None
 
         #: A CookieJar of Cookies the server sent back.
-        self.cookies = cookiejar_from_dict({})
+        self.cookies = cookie_jar_factory({})
 
         #: The amount of time elapsed between sending the request
         #: and the arrival of the response (as a timedelta).

```
