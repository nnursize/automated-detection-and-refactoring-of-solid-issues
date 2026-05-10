# Refactor SRP-024 (SRP): Orchestrates sending a PreparedRequest, including connection retrieval, TLS v...

**Status:** `applied_passed`  
**Branch:** `refactor/SRP-024` -> `main`  
**Head commit:** `d73b93322ad291bb743e2710fbbc2684175c5be5`  
**LLM finish:** `FinishReason.STOP` (prompt 7925, completion 1216)  

## Detected issue

- **File**: `src/requests/adapters.py`
- **Entity**: `HTTPAdapter.send` (method)
- **Lines (at detection time)**: L380–L458
- **Severity**: high
- **Confidence**: detected by 2 scan(s)

**Description.** Orchestrates sending a PreparedRequest, including connection retrieval, TLS verification, URL formatting, header modification, timeout conversion, exception handling, and response building.

**Reasoning.** This is a 'god method' that encapsulates the entire process of sending a `PreparedRequest` via `urllib3`. Its responsibilities include: 1) Retrieving the `urllib3` connection (`get_connection_with_tls_context`). 2) Performing TLS certificate verification (`cert_verify`). 3) Determining the request URL format (`request_url`). 4) Adding connection-specific headers (`add_headers`). 5) Handling chunked encoding. 6) Converting Requests' timeout format to `urllib3.TimeoutSauce`. 7) Executing the `conn.urlopen` call. 8) Catching and re-raising a wide array of `urllib3` exceptions as `requests` exceptions. 9) Building the `requests.Response` object (`build_response`). Each of these is a significant, distinct responsibility.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 2
- **Files modified** (1): `src/requests/adapters.py`

**Summary.** Extract exception handling from HTTPAdapter.send into a dedicated helper method.

**Rationale.** The HTTPAdapter.send method is a 'god method' that handles too many concerns. Extracting the complex exception-handling logic into a private helper method (_handle_exception) reduces the cognitive load and size of the primary send method, adhering better to the Single Responsibility Principle.

## Changes overview

_2 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `src/requests/adapters.py` (37-line block → 2-line replacement)

**Replaces:**

```python
        except (ProtocolError, OSError) as err:
            raise ConnectionError(err, request=request)

        except MaxRetryError as e:
            if isinstance(e.reason, ConnectTimeoutError):
                # TODO: Remove this in 3.0.0: see #2811
                if not isinstance(e.reason, NewConnectionError):
                    raise ConnectTimeout(e, request=request)

            if isinstance(e.reason, ResponseError):
                raise RetryError(e, request=request)

            if isinstance(e.reason, _ProxyError):
                raise ProxyError(e, request=request)

            if isinstance(e.reason, _SSLError):
                # This branch is for urllib3 v1.22 and later.
                raise SSLError(e, request=request)

            raise ConnectionError(e, request=request)

        except ClosedPoolError as e:
            raise ConnectionError(e, request=request)

        except _ProxyError as e:
            raise ProxyError(e)

        except (_SSLError, _HTTPError) as e:
            if isinstance(e, _SSLError):
                # This branch is for urllib3 versions earlier than v1.22
                raise SSLError(e, request=request)
            elif isinstance(e, ReadTimeoutError):
                raise ReadTimeout(e, request=request)
            elif isinstance(e, _InvalidHeader):
                raise InvalidHeader(e, request=request)
            else:
                raise
```

**With:**

```python
        except (ProtocolError, OSError, MaxRetryError, ClosedPoolError, _ProxyError, _SSLError, _HTTPError) as e:
            self._handle_exception(request, e)
```

### 2. EDIT `src/requests/adapters.py` (20-line block → 58-line replacement)

**Replaces:**

```python
    def proxy_headers(self, proxy):
        """Returns a dictionary of the headers to add to any request sent
        through a proxy. This works with urllib3 magic to ensure that they are
        correctly sent to the proxy, rather than in a tunnelled request if
        CONNECT is being used.

        This should not be called from user code, and is only exposed for use
        when subclassing the
        :class:`HTTPAdapter <requests.adapters.HTTPAdapter>`.

        :param proxy: The url of the proxy being used for this request.
        :rtype: dict
        """
        headers = {}
        username, password = get_auth_from_url(proxy)

        if username:
            headers["Proxy-Authorization"] = _basic_auth_str(username, password)

        return headers
```

**With:**

```python
    def proxy_headers(self, proxy):
        """Returns a dictionary of the headers to add to any request sent
        through a proxy. This works with urllib3 magic to ensure that they are
        correctly sent to the proxy, rather than in a tunnelled request if
        CONNECT is being used.

        This should not be called from user code, and is only exposed for use
        when subclassing the
        :class:`HTTPAdapter <requests.adapters.HTTPAdapter>`.

        :param proxy: The url of the proxy being used for this request.
        :rtype: dict
        """
        headers = {}
        username, password = get_auth_from_url(proxy)

        if username:
            headers["Proxy-Authorization"] = _basic_auth_str(username, password)

        return headers

    def _handle_exception(self, request, e):
        """Handles exceptions thrown by urllib3 during a request."""
        if isinstance(e, (ProtocolError, OSError, ClosedPoolError)):
            raise ConnectionError(e, request=request)

        if isinstance(e, MaxRetryError):
            if isinstance(e.reason, ConnectTimeoutError):
                # TODO: Remove this in 3.0.0: see #2811
                if not isinstance(e.reason, NewConnectionError):
                    raise ConnectTimeout(e, request=request)

            if isinstance(e.reason, ResponseError):
                raise RetryError(e, request=request)

            if isinstance(e.reason, _ProxyError):
                raise ProxyError(e, request=request)

            if isinstance(e.reason, _SSLError):
                # This branch is for urllib3 v1.22 and later.
                raise SSLError(e, request=request)

            raise ConnectionError(e, request=request)

        if isinstance(e, _ProxyError):
            raise ProxyError(e)

        if isinstance(e, _SSLError):
            # This branch is for urllib3 versions earlier than v1.22
            raise SSLError(e, request=request)

        if isinstance(e, ReadTimeoutError):
            raise ReadTimeout(e, request=request)

        if isinstance(e, _InvalidHeader):
            raise InvalidHeader(e, request=request)

        raise e
```

## Test results

**PASSED** — 606/610 passed, 0 failed, 3 skipped, 0 errored (duration 165958 ms).

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
606 passed, 3 skipped, 1 deselected, 1 xfailed, 17 warnings in 165.17s (0:02:45)

```

</details>

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/requests/adapters.py` | 575 → 575 | 21 → 22 | 3.61 → 3.42 | 19 → 14 | 47.34 → 47.34 |

## Diff

```diff
diff --git a/src/requests/adapters.py b/src/requests/adapters.py
index 8aad06f..2cca2b1 100644
--- a/src/requests/adapters.py
+++ b/src/requests/adapters.py
@@ -591,6 +591,44 @@ class HTTPAdapter(BaseAdapter):
 
         return headers
 
+    def _handle_exception(self, request, e):
+        """Handles exceptions thrown by urllib3 during a request."""
+        if isinstance(e, (ProtocolError, OSError, ClosedPoolError)):
+            raise ConnectionError(e, request=request)
+
+        if isinstance(e, MaxRetryError):
+            if isinstance(e.reason, ConnectTimeoutError):
+                # TODO: Remove this in 3.0.0: see #2811
+                if not isinstance(e.reason, NewConnectionError):
+                    raise ConnectTimeout(e, request=request)
+
+            if isinstance(e.reason, ResponseError):
+                raise RetryError(e, request=request)
+
+            if isinstance(e.reason, _ProxyError):
+                raise ProxyError(e, request=request)
+
+            if isinstance(e.reason, _SSLError):
+                # This branch is for urllib3 v1.22 and later.
+                raise SSLError(e, request=request)
+
+            raise ConnectionError(e, request=request)
+
+        if isinstance(e, _ProxyError):
+            raise ProxyError(e)
+
+        if isinstance(e, _SSLError):
+            # This branch is for urllib3 versions earlier than v1.22
+            raise SSLError(e, request=request)
+
+        if isinstance(e, ReadTimeoutError):
+            raise ReadTimeout(e, request=request)
+
+        if isinstance(e, _InvalidHeader):
+            raise InvalidHeader(e, request=request)
+
+        raise e
+
     def send(
         self, request, stream=False, timeout=None, verify=True, cert=None, proxies=None
     ):
@@ -659,42 +697,7 @@ class HTTPAdapter(BaseAdapter):
                 chunked=chunked,
             )
 
-        except (ProtocolError, OSError) as err:
-            raise ConnectionError(err, request=request)
-
-        except MaxRetryError as e:
-            if isinstance(e.reason, ConnectTimeoutError):
-                # TODO: Remove this in 3.0.0: see #2811
-                if not isinstance(e.reason, NewConnectionError):
-                    raise ConnectTimeout(e, request=request)
-
-            if isinstance(e.reason, ResponseError):
-                raise RetryError(e, request=request)
-
-            if isinstance(e.reason, _ProxyError):
-                raise ProxyError(e, request=request)
-
-            if isinstance(e.reason, _SSLError):
-                # This branch is for urllib3 v1.22 and later.
-                raise SSLError(e, request=request)
-
-            raise ConnectionError(e, request=request)
-
-        except ClosedPoolError as e:
-            raise ConnectionError(e, request=request)
-
-        except _ProxyError as e:
-            raise ProxyError(e)
-
-        except (_SSLError, _HTTPError) as e:
-            if isinstance(e, _SSLError):
-                # This branch is for urllib3 versions earlier than v1.22
-                raise SSLError(e, request=request)
-            elif isinstance(e, ReadTimeoutError):
-                raise ReadTimeout(e, request=request)
-            elif isinstance(e, _InvalidHeader):
-                raise InvalidHeader(e, request=request)
-            else:
-                raise
+        except (ProtocolError, OSError, MaxRetryError, ClosedPoolError, _ProxyError, _SSLError, _HTTPError) as e:
+            self._handle_exception(request, e)
 
         return self.build_response(request, resp)

```
