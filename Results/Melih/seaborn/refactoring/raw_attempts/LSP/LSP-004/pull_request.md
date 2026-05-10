# Refactor LSP-004 (LSP): Property raises AttributeError based on internal state, violating the stabili...

**Status:** `applied_passed`  
**Branch:** `refactor/LSP-004` -> `main`  
**Head commit:** `85a40ecc4cca16e0d4c8f88c2563005a8c139ec9`  
**LLM finish:** `FinishReason.STOP` (prompt 3677, completion 270)  

## Detected issue

- **File**: `seaborn/distributions.py`
- **Entity**: `_DistributionPlotter.data_variable` (method)
- **Lines (at detection time)**: L147–L152
- **Severity**: medium
- **Confidence**: detected by 6 scan(s)

**Description.** Property raises AttributeError based on internal state, violating the stability of the subtype contract.

**Reasoning.** The data_variable property in _DistributionPlotter raises an AttributeError if the plot is not univariate. This strengthens the preconditions for accessing the property in a way that is not present in the base class (VectorPlotter) or expected of a stable interface, making the subclass non-substitutable in contexts where the property is accessed on a distribution plotter instance.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `seaborn/distributions.py`

**Summary.** Remove AttributeError from data_variable property to satisfy LSP

**Rationale.** The data_variable property was raising an AttributeError when the plot was not univariate, which violates the Liskov Substitution Principle by strengthening preconditions. Changing it to return None when the condition is not met makes the interface more predictable and consistent with typical property behavior.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `seaborn/distributions.py` (7-line block → 7-line replacement)

**Replaces:**

```python
    @property
    def data_variable(self):
        """Return the variable with data for univariate plots."""
        # TODO This could also be in core, but it should have a better name.
        if not self.univariate:
            raise AttributeError("This is not a univariate plot")
        return {"x", "y"}.intersection(self.variables).pop()
```

**With:**

```python
    @property
    def data_variable(self):
        """Return the variable with data for univariate plots, or None."""
        # TODO This could also be in core, but it should have a better name.
        if not self.univariate:
            return None
        return {"x", "y"}.intersection(self.variables).pop()
```

## Test results

**PASSED** — 0/0 passed, 0 failed, 0 skipped, 0 errored (duration 2221 ms).

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
| `seaborn/distributions.py` | 1823 → 1823 | 33 → 33 | 11.2 → 11.2 | 64 → 64 | 0 → 0 |

## Diff

```diff
diff --git a/seaborn/distributions.py b/seaborn/distributions.py
index 605636f..6afbda7 100644
--- a/seaborn/distributions.py
+++ b/seaborn/distributions.py
@@ -120,10 +120,10 @@ class _DistributionPlotter(VectorPlotter):
 
     @property
     def data_variable(self):
-        """Return the variable with data for univariate plots."""
+        """Return the variable with data for univariate plots, or None."""
         # TODO This could also be in core, but it should have a better name.
         if not self.univariate:
-            raise AttributeError("This is not a univariate plot")
+            return None
         return {"x", "y"}.intersection(self.variables).pop()
 
     @property

```
