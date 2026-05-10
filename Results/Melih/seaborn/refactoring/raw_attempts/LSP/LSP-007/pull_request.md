# Refactor LSP-007 (LSP): Subtype 'Identity' nullifies a required callable attribute '_spacer' used by...

**Status:** `applied_passed`  
**Branch:** `refactor/LSP-007` -> `main`  
**Head commit:** `2572ce6e2a3f26be566723d77229e1e3fba2293d`  
**LLM finish:** `FinishReason.STOP` (prompt 10418, completion 216)  

## Detected issue

- **File**: `seaborn/_core/scales.py`
- **Entity**: `Scale._identity` (class)
- **Lines (at detection time)**: L122–L130
- **Severity**: high
- **Confidence**: detected by 3 scan(s)

**Description.** Subtype 'Identity' nullifies a required callable attribute '_spacer' used by the base class.

**Reasoning.** The 'Identity' class (returned by the Scale._identity factory method) explicitly sets '_spacer = None'. However, the base class 'Scale' provides a concrete method '_spacing' (line 92) that executes 'self._spacer(x)'. Substituting an 'Identity' instance where a 'Scale' is expected and invoking the '_spacing' method will result in a TypeError. A subclass must not nullify or break the internal contract of a base class method that it inherits.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `seaborn/_core/scales.py`

**Summary.** Fix LSP violation by providing a valid _spacer for the Identity scale

**Rationale.** The Identity scale nullified the '_spacer' attribute, which caused a TypeError when the base class '_spacing' method was called. By providing a default spacer that returns 1 (consistent with other scales), we satisfy the base class contract while maintaining the intended identity behavior.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `seaborn/_core/scales.py` (10-line block → 10-line replacement)

**Replaces:**

```python
    @staticmethod
    def _identity():

        class Identity(Scale):
            _pipeline = []
            _spacer = None
            _legend = None
            _matplotlib_scale = None

        return Identity()
```

**With:**

```python
    @staticmethod
    def _identity():

        class Identity(Scale):
            _pipeline = []
            _spacer = _default_spacer
            _legend = None
            _matplotlib_scale = None

        return Identity()
```

## Test results

**PASSED** — 0/0 passed, 0 failed, 0 skipped, 0 errored (duration 2223 ms).

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
seaborn\categorical.py:49: in <module>
    class _CategoricalPlotter(VectorPlotter):
seaborn\categorical.py:482: in _CategoricalPlotter
    @register_plot("strips")
     ^^^^^^^^^^^^^^^^^^^^^^^
E   TypeError: 'classmethod' object is not callable
=========================== short test summary info ===========================
ERROR tests/_core/test_data.py - TypeError: 'classmethod' object is not callable
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!
1 error in 1.37s

```

</details>

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `seaborn/_core/scales.py` | 747 → 747 | 77 → 77 | 2.79 → 2.79 | 16 → 16 | 23.47 → 23.47 |

## Diff

```diff
diff --git a/seaborn/_core/scales.py b/seaborn/_core/scales.py
index fdfd6cb..e0d2051 100644
--- a/seaborn/_core/scales.py
+++ b/seaborn/_core/scales.py
@@ -138,7 +138,7 @@ class Scale:
 
         class Identity(Scale):
             _pipeline = []
-            _spacer = None
+            _spacer = _default_spacer
             _legend = None
             _matplotlib_scale = None
 

```
