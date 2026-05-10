# Refactor LSP-006 (LSP): Subclass override violates the behavioral contract of the parent method by ig...

**Status:** `applied_passed`  
**Branch:** `refactor/LSP-006` -> `main`  
**Head commit:** `909d86c6fd5c4bbb2f761a668a97158802822856`  
**LLM finish:** `FinishReason.STOP` (prompt 8794, completion 630)  

## Detected issue

- **File**: `seaborn/_core/properties.py`
- **Entity**: `Color.infer_scale` (method)
- **Lines (at detection time)**: L487–L515
- **Severity**: high
- **Confidence**: detected by 1 scan(s)

**Description.** Subclass override violates the behavioral contract of the parent method by ignoring transformation logic.

**Reasoning.** Similar to IntervalProperty, the 'Color' subclass overrides 'infer_scale' and fails to respect the base class contract for processing transformation strings. While the base class 'Property' is designed to handle 'log', 'pow', etc., 'Color.infer_scale' redirects string arguments to nominal palette lookups or other color-specific logic, breaking the substitutability of the Property interface for numeric-based color mappings.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `seaborn/_core/properties.py`

**Summary.** Update Color.infer_scale to respect base class magic scale arguments

**Rationale.** The Color subclass was overriding infer_scale and ignoring the base class's logic for 'magic' scale arguments (like 'log', 'pow', etc.). By incorporating the base class's magic scale check into Color.infer_scale, we restore the expected behavior for numeric-based color mappings while maintaining color-specific palette logic.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `seaborn/_core/properties.py` (27-line block → 30-line replacement)

**Replaces:**

```python
    def infer_scale(self, arg: Any, data: Series) -> Scale:
        var_type = variable_type(data, boolean_type="boolean", strict_boolean=True)

        if var_type == "boolean":
            return Boolean(arg)

        if isinstance(arg, (dict, list)):
            return Nominal(arg)

        if isinstance(arg, tuple):
            return Nominal(arg) if var_type == "categorical" else Continuous(arg)

        if callable(arg):
            return Continuous(arg)

        if isinstance(arg, str):
            if arg in QUAL_PALETTES:
                return Nominal(arg)
            if var_type == "numeric":
                return Continuous(arg)
            return Nominal(arg)

        msg = " ".join([
            f"A single scale argument for {self.variable} variables must be",
            f"a string, dict, tuple, list, or callable, not {type(arg)}."
        ])
        raise TypeError(msg)
```

**With:**

```python
    def infer_scale(self, arg: Any, data: Series) -> Scale:
        var_type = variable_type(data, boolean_type="boolean", strict_boolean=True)

        if var_type == "boolean":
            return Boolean(arg)

        if isinstance(arg, (dict, list)):
            return Nominal(arg)

        if isinstance(arg, tuple):
            return Nominal(arg) if var_type == "categorical" else Continuous(arg)

        if callable(arg):
            return Continuous(arg)

        if isinstance(arg, str):
            for key, cls in self._magic_scales.items():
                if arg.startswith(key):
                    return cls(trans=arg)
            if arg in QUAL_PALETTES:
                return Nominal(arg)
            if var_type == "numeric":
                return Continuous(arg)
            return Nominal(arg)

        msg = " ".join([
            f"A single scale argument for {self.variable} variables must be",
            f"a string, dict, tuple, list, or callable, not {type(arg)}."
        ])
        raise TypeError(msg)
```

## Test results

**PASSED** — 0/0 passed, 0 failed, 0 skipped, 0 errored (duration 2220 ms).

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
seaborn\categorical.py:460: in _CategoricalPlotter
    @register_plot("strips")
     ^^^^^^^^^^^^^^^^^^^^^^^
E   TypeError: 'classmethod' object is not callable
=========================== short test summary info ===========================
ERROR tests/_core/test_data.py - TypeError: 'classmethod' object is not callable
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!
1 error in 1.35s

```

</details>

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `seaborn/_core/properties.py` | 587 → 590 | 55 → 55 | 2.89 → 2.94 | 12 → 12 | 23.43 → 23.05 |

## Diff

```diff
diff --git a/seaborn/_core/properties.py b/seaborn/_core/properties.py
index 8bbddde..86bb33b 100644
--- a/seaborn/_core/properties.py
+++ b/seaborn/_core/properties.py
@@ -598,6 +598,9 @@ class Color(Property):
             return Continuous(arg)
 
         if isinstance(arg, str):
+            for key, cls in self._magic_scales.items():
+                if arg.startswith(key):
+                    return cls(trans=arg)
             if arg in QUAL_PALETTES:
                 return Nominal(arg)
             if var_type == "numeric":

```
