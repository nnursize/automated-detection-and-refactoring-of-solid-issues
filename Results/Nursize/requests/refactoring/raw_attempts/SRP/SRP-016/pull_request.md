# Refactor SRP-016 (SRP): Merges cookies, applies environment authentication, and merges headers, param...

**Status:** `patch_failed`  
**Branch:** `refactor/SRP-016` -> `main`  
**Head commit:** `178332b19159a5d45228c36e03126748061c76d5`  
**LLM finish:** `FinishReason.STOP` (prompt 8844, completion 863)  

## Detected issue

- **File**: `src/requests/sessions.py`
- **Entity**: `Session.prepare_request` (method)
- **Lines (at detection time)**: L339–L376
- **Severity**: medium
- **Confidence**: detected by 5 scan(s)

**Description.** Merges cookies, applies environment authentication, and merges headers, params, and hooks from session and request.

**Reasoning.** This method is responsible for preparing a `Request` into a `PreparedRequest` by applying session-level settings. It combines several distinct merging strategies: 1) Merging request cookies with session cookies. 2) Conditionally applying environment-based authentication (`get_netrc_auth`). 3) Merging headers, parameters, and hooks using `merge_setting` and `merge_hooks`. Each of these merging operations for different types of request components is a separate concern.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `src/requests/sessions.py`

**Summary.** Refactor Session.prepare_request to delegate merging logic to helper methods.

**Rationale.** The prepare_request method was handling multiple concerns (cookie merging, auth resolution, and general setting merging). By extracting these into private helper methods, we adhere to the Single Responsibility Principle and improve readability.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `src/requests/sessions.py` (42-line block → 38-line replacement)

**Replaces:**

```python
    def prepare_request(self, request):
        """Constructs a :class:`PreparedRequest <PreparedRequest>` for
        transmission and returns it. The :class:`PreparedRequest` has settings
        merged from the :class:`Request <Request>` instance and those of the
        `Session`.

        :param request: :class:`Request` instance to prepare with this
            session's settings.
        :rtype: requests.PreparedRequest
        """
        cookies = request.cookies or {}

        # Bootstrap CookieJar.
        if not isinstance(cookies, cookielib.CookieJar):
            cookies = cookiejar_from_dict(cookies)

        # Merge with session cookies
        merged_cookies = merge_cookies(
            merge_cookies(RequestsCookieJar(), self.cookies), cookies
        )

        # Set environment's basic authentication if not explicitly set.
        auth = request.auth
        if self.trust_env and not auth and not self.auth:
            auth = get_netrc_auth(request.url)

        p = PreparedRequest()
        p.prepare(
            method=request.method.upper(),
            url=request.url,
            files=request.files,
            data=request.data,
            json=request.json,
            headers=merge_setting(
                request.headers, self.headers, dict_class=CaseInsensitiveDict
            ),
            params=merge_setting(request.params, self.params),
            auth=merge_setting(auth, self.auth),
            cookies=merged_cookies,
            hooks=merge_hooks(request.hooks, self.hooks),
        )
        return p
```

**With:**

```python
    def prepare_request(self, request):
        """Constructs a :class:`PreparedRequest <PreparedRequest>` for
        transmission and returns it. The :class:`PreparedRequest` has settings
        merged from the :class:`Request <Request>` instance and those of the
        :class:`Session`.

        :param request: :class:`Request` instance to prepare with this
            session's settings.
        :rtype: requests.PreparedRequest
        """
        p = PreparedRequest()
        p.prepare(
            method=request.method.upper(),
            url=request.url,
            files=request.files,
            data=request.data,
            json=request.json,
            headers=merge_setting(
                request.headers, self.headers, dict_class=CaseInsensitiveDict
            ),
            params=merge_setting(request.params, self.params),
            auth=self._get_auth(request),
            cookies=self._get_cookies(request),
            hooks=merge_hooks(request.hooks, self.hooks),
        )
        return p

    def _get_cookies(self, request):
        cookies = request.cookies or {}
        if not isinstance(cookies, cookielib.CookieJar):
            cookies = cookiejar_from_dict(cookies)
        return merge_cookies(merge_cookies(RequestsCookieJar(), self.cookies), cookies)

    def _get_auth(self, request):
        auth = request.auth
        if self.trust_env and not auth and not self.auth:
            auth = get_netrc_auth(request.url)
        return merge_setting(auth, self.auth)
```

## Apply error

```
search_text not found in src/requests/sessions.py (block 0)
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/requests/sessions.py` | 566 → - | 28 → - | 4.07 → - | 15 → - | 38.09 → - |

## Diff

*(no diff — patch was not applied)*
