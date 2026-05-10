# Refactor LSP-009 (LSP): LookupDict inherits from dict but breaks the contract of __getitem__ and uses...

**Status:** `applied_failed`  
**Branch:** `refactor/LSP-009` -> `main`  
**Head commit:** `d7c31619d0f4344c4f802c51dcde02ae3f039a75`  
**LLM finish:** `FinishReason.STOP` (prompt 2095, completion 391)  

## Detected issue

- **File**: `src/requests/structures.py`
- **Entity**: `LookupDict` (class)
- **Lines (at detection time)**: L73–L88
- **Severity**: high
- **Confidence**: detected by 2 scan(s)

**Description.** LookupDict inherits from dict but breaks the contract of __getitem__ and uses a different storage mechanism.

**Reasoning.** LookupDict inherits from the built-in 'dict' but overrides '__getitem__' to return None instead of raising a KeyError when a key is missing. Furthermore, it retrieves values from the instance's '__dict__' instead of the dictionary's actual internal storage. This breaks the fundamental contract of the dict type, as code expecting a dictionary and using standard error handling (try-except KeyError) will fail to detect missing keys, potentially leading to TypeErrors or incorrect logic downstream.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `src/requests/structures.py`

**Summary.** Refactor LookupDict to inherit from collections.abc.Mapping instead of dict to avoid LSP violation.

**Rationale.** LookupDict does not behave like a standard dict (it returns None for missing keys instead of raising KeyError). By inheriting from Mapping instead of dict, it correctly signals that it is a read-only mapping-like object without implying the full contract of a mutable dictionary, thus resolving the LSP violation.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `src/requests/structures.py` (17-line block → 21-line replacement)

**Replaces:**

```python
class LookupDict(dict):
    """Dictionary lookup object."""

    def __init__(self, name=None):
        self.name = name
        super().__init__()

    def __repr__(self):
        return f"<lookup '{self.name}'>"

    def __getitem__(self, key):
        # We allow fall-through here, so values default to None

        return self.__dict__.get(key, None)

    def get(self, key, default=None):
        return self.__dict__.get(key, default)
```

**With:**

```python
class LookupDict(Mapping):
    """Dictionary lookup object."""

    def __init__(self, name=None):
        self.name = name
        self._items = {}

    def __getitem__(self, key):
        return self._items.get(key)

    def __iter__(self):
        return iter(self._items)

    def __len__(self):
        return len(self._items)

    def __repr__(self):
        return f"<lookup '{self.name}'>"

    def get(self, key, default=None):
        return self._items.get(key, default)
```

## Test results

**FAILED** — 352/355 passed, 1 failed, 1 skipped, 0 errored (duration 117093 ms).

- New failures introduced by this refactor: **1**
- Pre-existing failures (unrelated to this refactor): **0**

New-failure node IDs (first 25):

  - `tests/test_requests.py::TestPreparingURLs::test_status_code_425`

Command: `C:\Users\User\Desktop\SDP-Codex\S1-T7-Okeyish\refactor_workspaces\requests\.venv\Scripts\python.exe -m pytest --tb=short -q --no-header -p no:cacheprovider -x --json-report --json-report-file=C:\Users\User\Desktop\SDP-Codex\S1-T7-Okeyish\refactor_workspaces\requests\.pytest_report.json --deselect=tests/test_requests.py::TestPreparingURLs::test_different_connection_pool_for_tls_settings_verify_bundle_unexpired_cert`

<details><summary>Output tail</summary>

```
........................................................................ [ 11%]
........................................................................ [ 23%]
......sattempting to ignore so the rest of the tests can run
................................................................. [ 35%]
...............................................x........................ [ 47%]
..................................................................F
================================== FAILURES ===================================
___________________ TestPreparingURLs.test_status_code_425 ____________________
tests\test_requests.py:2866: in test_status_code_425
    assert r1 == 425
E   assert None == 425
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

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ===========================
FAILED tests/test_requests.py::TestPreparingURLs::test_status_code_425 - asse...
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!
1 failed, 352 passed, 1 skipped, 1 deselected, 1 xfailed, 8 warnings in 116.27s (0:01:56)

[stderr]
127.0.0.1 - - [04/May/2026 13:58:49] "GET /get HTTP/1.1" 200 170
127.0.0.1 - - [04/May/2026 13:59:14] "GET / HTTP/1.1" 200 9509
127.0.0.1 - - [04/May/2026 13:59:14] "GET /html HTTP/1.1" 200 3741

```

</details>

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/requests/structures.py` | 67 → - | 14 → - | 1.38 → - | 2 → - | 81.77 → - |

## Diff

```diff
diff --git a/src/requests/structures.py b/src/requests/structures.py
index 188e13e..1621a61 100644
--- a/src/requests/structures.py
+++ b/src/requests/structures.py
@@ -80,20 +80,24 @@ class CaseInsensitiveDict(MutableMapping):
         return str(dict(self.items()))
 
 
-class LookupDict(dict):
+class LookupDict(Mapping):
     """Dictionary lookup object."""
 
     def __init__(self, name=None):
         self.name = name
-        super().__init__()
-
-    def __repr__(self):
-        return f"<lookup '{self.name}'>"
+        self._items = {}
 
     def __getitem__(self, key):
-        # We allow fall-through here, so values default to None
+        return self._items.get(key)
+
+    def __iter__(self):
+        return iter(self._items)
 
-        return self.__dict__.get(key, None)
+    def __len__(self):
+        return len(self._items)
+
+    def __repr__(self):
+        return f"<lookup '{self.name}'>"
 
     def get(self, key, default=None):
-        return self.__dict__.get(key, default)
+        return self._items.get(key, default)

```
