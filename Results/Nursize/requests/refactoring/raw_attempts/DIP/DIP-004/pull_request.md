# Refactor DIP-004 (DIP): Low-level HTTPAdapter directly instantiates a high-level Response object.

**Status:** `patch_failed`  
**Branch:** `refactor/DIP-004` -> `main`  
**Head commit:** `d97e7e9c79ed8bfa8dd1b666962c1c28fe28d2ad`  
**LLM finish:** `FinishReason.STOP` (prompt 7981, completion 820)  

## Detected issue

- **File**: `src/requests/adapters.py`
- **Entity**: `HTTPAdapter.build_response` (method)
- **Lines (at detection time)**: L298–L298
- **Severity**: medium
- **Confidence**: detected by 12 scan(s)

**Description.** Low-level HTTPAdapter directly instantiates a high-level Response object.

**Reasoning.** The `HTTPAdapter` is a low-level component responsible for interacting with the underlying `urllib3` library. However, its `build_response` method directly instantiates the high-level `Response` object. This couples the low-level adapter to the concrete details of the high-level response representation. Ideally, the adapter should return an abstraction of a response, or a higher-level module should provide a factory for creating `Response` objects, allowing the adapter to remain independent of the specific `Response` implementation.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 2
- **Files modified** (1): `src/requests/adapters.py`

**Summary.** Inject Response class into HTTPAdapter to decouple from concrete implementation

**Rationale.** The HTTPAdapter directly instantiated the Response class, creating a hard dependency. By adding a response_cls attribute (defaulting to the existing Response class), we allow for dependency injection and inversion of control, adhering to the Dependency Inversion Principle.

## Changes overview

_2 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `src/requests/adapters.py` (21-line block → 23-line replacement)

**Replaces:**

```python
    def __init__(
        self,
        pool_connections=DEFAULT_POOLSIZE,
        pool_maxsize=DEFAULT_POOLSIZE,
        max_retries=DEFAULT_RETRIES,
        pool_block=DEFAULT_POOLBLOCK,
    ):
        if max_retries == DEFAULT_RETRIES:
            self.max_retries = Retry(0, read=False)
        else:
            self.max_retries = Retry.from_int(max_retries)
        self.config = {}
        self.proxy_manager = {}

        super().__init__()

        self._pool_connections = pool_connections
        self._pool_maxsize = pool_maxsize
        self._pool_block = pool_block

        self.init_poolmanager(pool_connections, maxsize=pool_maxsize, block=pool_block)
```

**With:**

```python
    def __init__(
        self,
        pool_connections=DEFAULT_POOLSIZE,
        pool_maxsize=DEFAULT_POOLSIZE,
        max_retries=DEFAULT_RETRIES,
        pool_block=DEFAULT_POOLBLOCK,
        response_cls=Response,
    ):
        if max_retries == DEFAULT_RETRIES:
            self.max_retries = Retry(0, read=False)
        else:
            self.max_retries = Retry.from_int(max_retries)
        self.config = {}
        self.proxy_manager = {}
        self.response_cls = response_cls

        super().__init__()

        self._pool_connections = pool_connections
        self._pool_maxsize = pool_maxsize
        self._pool_block = pool_block

        self.init_poolmanager(pool_connections, pool_maxsize, block=pool_block)
```

### 2. EDIT `src/requests/adapters.py` (13-line block → 13-line replacement)

**Replaces:**

```python
    def build_response(self, req, resp):
        """Builds a :class:`Response <requests.Response>` object from a urllib3
        response. This should not be called from user code, and is only exposed
        for use when subclassing the
        :class:`HTTPAdapter <requests.adapters.HTTPAdapter>`

        :param req: The :class:`PreparedRequest <PreparedRequest>` used to generate the response.
        :param resp: The urllib3 response object.
        :rtype: requests.Response
        """
        response = Response()

        # Fallback to None if there's no status_code, for whatever reason.
```

**With:**

```python
    def build_response(self, req, resp):
        """Builds a :class:`Response <requests.Response>` object from a urllib3
        response. This should not be called from user code, and is only exposed
        for use when subclassing the
        :class:`HTTPAdapter <requests.adapters.HTTPAdapter>`

        :param req: The :class:`PreparedRequest <PreparedRequest>` used to generate the response.
        :param resp: The urllib3 response object.
        :rtype: requests.Response
        """
        response = self.response_cls()

        # Fallback to None if there's no status_code, for whatever reason.
```

## Apply error

```
search_text not found in src/requests/adapters.py (block 0)
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/requests/adapters.py` | 588 → - | 24 → - | 3.29 → - | 14 → - | 47.37 → - |

## Diff

*(no diff — patch was not applied)*
