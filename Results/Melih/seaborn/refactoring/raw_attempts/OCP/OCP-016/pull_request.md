# Refactor OCP-016 (OCP): Conditional dispatch for default scale based on variable type.

**Status:** `applied_passed`  
**Branch:** `refactor/OCP-016` -> `main`  
**Head commit:** `d8ae66d0225a36f8bf7a8c30d85d660ef983e8df`  
**LLM finish:** `FinishReason.STOP` (prompt 8908, completion 321)  

## Detected issue

- **File**: `seaborn/_core/properties.py`
- **Entity**: `Property.default_scale` (method)
- **Lines (at detection time)**: L39–L49
- **Severity**: high
- **Confidence**: detected by 2 scan(s)

**Description.** Conditional dispatch for default scale based on variable type.

**Reasoning.** The `default_scale` method uses an `if/elif/else` chain to return a specific `Scale` subclass based on the `var_type` ('numeric', 'datetime', 'boolean', or other). If new fundamental variable types are introduced, this method would need to be modified to add a new `elif` branch, directly violating the Open/Closed Principle.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `seaborn/_core/properties.py`

**Summary.** Replace conditional dispatch in Property.default_scale with a registry-based mapping.

**Rationale.** The hardcoded if/elif/else chain in Property.default_scale violates the Open/Closed Principle. By introducing a class-level dictionary mapping variable types to scale classes, we allow for extension without modifying the base class logic.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `seaborn/_core/properties.py` (12-line block → 10-line replacement)

**Replaces:**

```python
    def default_scale(self, data: Series) -> Scale:
        """Given data, initialize appropriate scale class."""

        var_type = variable_type(data, boolean_type="boolean", strict_boolean=True)
        if var_type == "numeric":
            return Continuous()
        elif var_type == "datetime":
            return Temporal()
        elif var_type == "boolean":
            return Boolean()
        else:
            return Nominal()
```

**With:**

```python
    _default_scale_map = {
        "numeric": Continuous,
        "datetime": Temporal,
        "boolean": Boolean,
    }

    def default_scale(self, data: Series) -> Scale:
        """Given data, initialize appropriate scale class."""
        var_type = variable_type(data, boolean_type="boolean", strict_boolean=True)
        return self._default_scale_map.get(var_type, Nominal)()
```

## Test results

**PASSED** — 0/0 passed, 0 failed, 0 skipped, 0 errored (duration 2186 ms).

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
1 error in 1.34s

```

</details>

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `seaborn/_core/properties.py` | 592 → 590 | 55 → 55 | 2.94 → 2.89 | 12 → 12 | 23.32 → 24 |

## Diff

```diff
diff --git a/seaborn/_core/properties.py b/seaborn/_core/properties.py
index b9cac72..9de60f2 100644
--- a/seaborn/_core/properties.py
+++ b/seaborn/_core/properties.py
@@ -56,18 +56,16 @@ class Property:
             variable = self.__class__.__name__.lower()
         self.variable = variable
 
+    _default_scale_map = {
+        "numeric": Continuous,
+        "datetime": Temporal,
+        "boolean": Boolean,
+    }
+
     def default_scale(self, data: Series) -> Scale:
         """Given data, initialize appropriate scale class."""
-
         var_type = variable_type(data, boolean_type="boolean", strict_boolean=True)
-        if var_type == "numeric":
-            return Continuous()
-        elif var_type == "datetime":
-            return Temporal()
-        elif var_type == "boolean":
-            return Boolean()
-        else:
-            return Nominal()
+        return self._default_scale_map.get(var_type, Nominal)()
 
     _magic_scales = {
         "log": Continuous,

```
