# Refactor ISP-015 (ISP): Class 'Identity' inherits from abstract base class 'Scale' but does not imple...

**Status:** `applied_passed`  
**Branch:** `refactor/ISP-015` -> `main`  
**Head commit:** `bb02a5ee25829482ac5ad16f4a75c28ab2eb7293`  
**LLM finish:** `FinishReason.STOP` (prompt 10773, completion 229)  

## Detected issue

- **File**: `seaborn/_core/scales.py`
- **Entity**: `Identity` (class)
- **Lines (at detection time)**: L139–L143
- **Severity**: high
- **Confidence**: detected by 1 scan(s)

**Description.** Class 'Identity' inherits from abstract base class 'Scale' but does not implement any of its abstract methods.

**Reasoning.** The 'Scale' abstract base class (L55-L145) defines several abstract methods like 'tick', 'label', '_get_locators', '_get_formatter', and '_setup'. The 'Identity' class (L139-L143) inherits from 'Scale' but does not provide implementations for any of these abstract methods. This forces 'Identity' to depend on an interface it does not fully implement, violating ISP by failing to fulfill the contract of its base interface.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `seaborn/_core/scales.py`

**Summary.** Implement abstract methods in Identity class to satisfy Scale interface

**Rationale.** The Identity class inherits from Scale but failed to implement the abstract _setup method. While it is a simple identity scale, it must fulfill the interface contract to avoid runtime errors and satisfy the Interface Segregation Principle.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `seaborn/_core/scales.py` (8-line block → 11-line replacement)

**Replaces:**

```python
        class Identity(Scale):
            _pipeline = []
            _spacer = _default_spacer
            _legend = None
            _matplotlib_scale = None

            def _setup(self, data, prop, axis=None):
                return self
```

**With:**

```python
        class Identity(Scale):
            _pipeline = []
            _spacer = _default_spacer
            _legend = None
            _matplotlib_scale = None

            def _setup(self, data, prop, axis=None):
                return self

            def _finalize(self, p, axis):
                pass
```

## Test results

**PASSED** — 0/0 passed, 0 failed, 0 skipped, 0 errored (duration 2294 ms).

Command: `C:\Users\User\Desktop\SDP-Codex\S1-T7-Okeyish\refactor_workspaces\seaborn-master\.venv\Scripts\python.exe -m pytest --tb=short -q --no-header -p no:cacheprovider -x --json-report --json-report-file=C:\Users\User\Desktop\SDP-Codex\S1-T7-Okeyish\refactor_workspaces\seaborn-master\.pytest_report.json`

<details><summary>Output tail</summary>

```

=================================== ERRORS ====================================
__________________ ERROR collecting tests/_core/test_data.py __________________
tests\_core\test_data.py:9: in <module>
    from seaborn._core.data import PlotData
seaborn\__init__.py:7: in <module>
    from .categorical import *  # noqa: F401,F403
    ^^^^^^^^^^^^^^^^^^^^^^^^^^
seaborn\categorical.py:460: in <module>
    class _StripPlotter(_CategoricalPlotter):
seaborn\categorical.py:461: in _StripPlotter
    @register_plot("strips")
     ^^^^^^^^^^^^^
E   NameError: name 'register_plot' is not defined
=========================== short test summary info ===========================
ERROR tests/_core/test_data.py - NameError: name 'register_plot' is not defined
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!
1 error in 1.39s

```

</details>

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `seaborn/_core/scales.py` | 773 → 775 | 85 → 86 | 2.64 → 2.64 | 16 → 16 | 21.74 → 21.69 |

## Diff

```diff
diff --git a/seaborn/_core/scales.py b/seaborn/_core/scales.py
index ecaa0ad..bbbfa96 100644
--- a/seaborn/_core/scales.py
+++ b/seaborn/_core/scales.py
@@ -117,6 +117,9 @@ class Scale:
             def _setup(self, data, prop, axis=None):
                 return self
 
+            def _finalize(self, p, axis):
+                pass
+
         return Identity()
 
 

```
