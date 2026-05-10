# Refactor SRP-020 (SRP): Manages and returns urllib3 ProxyManager instances, differentiating between S...

**Status:** `applied_passed`  
**Branch:** `refactor/SRP-020` -> `main`  
**Head commit:** `535951bd5755d8c54b5cf8b44cdc032ba0abc348`  
**LLM finish:** `FinishReason.STOP` (prompt 7814, completion 862)  

## Detected issue

- **File**: `src/requests/adapters.py`
- **Entity**: `HTTPAdapter.proxy_manager_for` (method)
- **Lines (at detection time)**: L125–L156
- **Severity**: medium
- **Confidence**: detected by 3 scan(s)

**Description.** Manages and returns urllib3 ProxyManager instances, differentiating between SOCKS and HTTP proxies, and extracting auth from SOCKS proxy URLs.

**Reasoning.** This method is responsible for providing the correct `urllib3` `ProxyManager` for a given proxy URL. It combines: 1) Caching `ProxyManager` instances. 2) Detecting if the proxy is SOCKS-based. 3) Extracting authentication credentials from SOCKS proxy URLs. 4) Instantiating either `SOCKSProxyManager` or `proxy_from_url` based on the proxy type. These are distinct concerns related to proxy management and configuration.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `src/requests/adapters.py`

**Summary.** Extract proxy manager creation logic into a dedicated helper method to improve SRP.

**Rationale.** The `proxy_manager_for` method was handling both caching and the complex instantiation logic for different proxy types (SOCKS vs HTTP). By extracting the instantiation logic into `_create_proxy_manager`, we separate the concern of managing the cache from the concern of configuring and creating the specific proxy manager instance.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `src/requests/adapters.py` (37-line block → 39-line replacement)

**Replaces:**

```python
    def proxy_manager_for(self, proxy, **proxy_kwargs):
        """Return urllib3 ProxyManager for the given proxy.

        This method should not be called from user code, and is only
        exposed for use when subclassing the
        :class:`HTTPAdapter <requests.adapters.HTTPAdapter>`.

        :param proxy: The proxy to return a urllib3 ProxyManager for.
        :param proxy_kwargs: Extra keyword arguments used to configure the Proxy Manager.
        :returns: ProxyManager
        :rtype: urllib3.ProxyManager
        """
        if proxy in self.proxy_manager:
            manager = self.proxy_manager[proxy]
        elif proxy.lower().startswith("socks"):
            username, password = get_auth_from_url(proxy)
            manager = self.proxy_manager[proxy] = SOCKSProxyManager(
                proxy,
                username=username,
                password=password,
                num_pools=self._pool_connections,
                maxsize=self._pool_maxsize,
                block=self._pool_block,
                **proxy_kwargs,
            )
        else:
            proxy_headers = self.proxy_headers(proxy)
            manager = self.proxy_manager[proxy] = proxy_from_url(
                proxy,
                proxy_headers=proxy_headers,
                num_pools=self._pool_connections,
                maxsize=self._pool_maxsize,
                block=self._pool_block,
                **proxy_kwargs,
            )

        return manager
```

**With:**

```python
    def _create_proxy_manager(self, proxy, **proxy_kwargs):
        """Creates a urllib3 ProxyManager for the given proxy."""
        if proxy.lower().startswith("socks"):
            username, password = get_auth_from_url(proxy)
            return SOCKSProxyManager(
                proxy,
                username=username,
                password=password,
                num_pools=self._pool_connections,
                maxsize=self._pool_maxsize,
                block=self._pool_block,
                **proxy_kwargs,
            )

        proxy_headers = self.proxy_headers(proxy)
        return proxy_from_url(
            proxy,
            proxy_headers=proxy_headers,
            num_pools=self._pool_connections,
            maxsize=self._pool_maxsize,
            block=self._pool_block,
            **proxy_kwargs,
        )

    def proxy_manager_for(self, proxy, **proxy_kwargs):
        """Return urllib3 ProxyManager for the given proxy.

        This method should not be called from user code, and is only
        exposed for use when subclassing the
        :class:`HTTPAdapter <requests.adapters.HTTPAdapter>`.

        :param proxy: The proxy to return a urllib3 ProxyManager for.
        :param proxy_kwargs: Extra keyword arguments used to configure the Proxy Manager.
        :returns: ProxyManager
        :rtype: urllib3.ProxyManager
        """
        if proxy not in self.proxy_manager:
            self.proxy_manager[proxy] = self._create_proxy_manager(proxy, **proxy_kwargs)
        return self.proxy_manager[proxy]
```

## Test results

**PASSED** — 606/610 passed, 0 failed, 3 skipped, 0 errored (duration 165953 ms).

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
606 passed, 3 skipped, 1 deselected, 1 xfailed, 17 warnings in 165.17s (0:02:45)

[stderr]
127.0.0.1 - - [04/May/2026 12:47:56] "GET /cookies HTTP/1.1" 200 26
127.0.0.1 - - [04/May/2026 12:48:51] "GET /redirect-to?url=http%3A%2F%2F%3A1 HTTP/1.1" 302 0

```

</details>

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/requests/adapters.py` | 574 → 575 | 20 → 21 | 3.73 → 3.61 | 19 → 19 | 47.52 → 47.34 |

## Diff

```diff
diff --git a/src/requests/adapters.py b/src/requests/adapters.py
index 130154f..8aad06f 100644
--- a/src/requests/adapters.py
+++ b/src/requests/adapters.py
@@ -241,6 +241,30 @@ class HTTPAdapter(BaseAdapter):
             **pool_kwargs,
         )
 
+    def _create_proxy_manager(self, proxy, **proxy_kwargs):
+        """Creates a urllib3 ProxyManager for the given proxy."""
+        if proxy.lower().startswith("socks"):
+            username, password = get_auth_from_url(proxy)
+            return SOCKSProxyManager(
+                proxy,
+                username=username,
+                password=password,
+                num_pools=self._pool_connections,
+                maxsize=self._pool_maxsize,
+                block=self._pool_block,
+                **proxy_kwargs,
+            )
+
+        proxy_headers = self.proxy_headers(proxy)
+        return proxy_from_url(
+            proxy,
+            proxy_headers=proxy_headers,
+            num_pools=self._pool_connections,
+            maxsize=self._pool_maxsize,
+            block=self._pool_block,
+            **proxy_kwargs,
+        )
+
     def proxy_manager_for(self, proxy, **proxy_kwargs):
         """Return urllib3 ProxyManager for the given proxy.
 
@@ -253,31 +277,9 @@ class HTTPAdapter(BaseAdapter):
         :returns: ProxyManager
         :rtype: urllib3.ProxyManager
         """
-        if proxy in self.proxy_manager:
-            manager = self.proxy_manager[proxy]
-        elif proxy.lower().startswith("socks"):
-            username, password = get_auth_from_url(proxy)
-            manager = self.proxy_manager[proxy] = SOCKSProxyManager(
-                proxy,
-                username=username,
-                password=password,
-                num_pools=self._pool_connections,
-                maxsize=self._pool_maxsize,
-                block=self._pool_block,
-                **proxy_kwargs,
-            )
-        else:
-            proxy_headers = self.proxy_headers(proxy)
-            manager = self.proxy_manager[proxy] = proxy_from_url(
-                proxy,
-                proxy_headers=proxy_headers,
-                num_pools=self._pool_connections,
-                maxsize=self._pool_maxsize,
-                block=self._pool_block,
-                **proxy_kwargs,
-            )
-
-        return manager
+        if proxy not in self.proxy_manager:
+            self.proxy_manager[proxy] = self._create_proxy_manager(proxy, **proxy_kwargs)
+        return self.proxy_manager[proxy]
 
     def cert_verify(self, conn, url, verify, cert):
         """Verify a SSL certificate. This method should not be called from user

```
