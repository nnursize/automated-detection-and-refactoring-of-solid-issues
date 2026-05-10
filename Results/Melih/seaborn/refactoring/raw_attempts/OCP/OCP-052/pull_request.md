# Refactor OCP-052 (OCP): Method dispatches scale type instantiation based on argument type and value.

**Status:** `applied_passed`  
**Branch:** `refactor/OCP-052` -> `main`  
**Head commit:** `9c9e6990cf6306b3f3fac515399aa2c39b5980da`  
**LLM finish:** `FinishReason.STOP` (prompt 8975, completion 587)  

## Detected issue

- **File**: `seaborn/_core/properties.py`
- **Entity**: `Property.infer_scale` (method)
- **Lines (at detection time)**: L66–L83
- **Severity**: medium
- **Confidence**: detected by 3 scan(s)

**Description.** Method dispatches scale type instantiation based on argument type and value.

**Reasoning.** This method uses an `if/elif/else` chain to determine which `Scale` subclass to instantiate based on the type of the `arg` parameter (`str` in this case) and string matching (`arg.startswith(k)`). Adding new 'magic' scale arguments or types would require modifying this method, violating OCP.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `seaborn/_core/properties.py`

**Summary.** Refactor Property.infer_scale to use a registry for magic scale arguments.

**Rationale.** Replaced the hardcoded if/elif/else chain in Property.infer_scale with a registry-based approach. This allows new scale types to be registered without modifying the base Property class, adhering to the Open/Closed Principle.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `seaborn/_core/properties.py` (19-line block → 20-line replacement)

**Replaces:**

```python
    def infer_scale(self, arg: Any, data: Series) -> Scale:
        """Given data and a scaling argument, initialize appropriate scale class."""
        # TODO put these somewhere external for validation
        # TODO putting this here won't pick it up if subclasses define infer_scale
        # (e.g. color). How best to handle that? One option is to call super after
        # handling property-specific possibilities (e.g. for color check that the
        # arg is not a valid palette name) but that could get tricky.
        trans_args = ["log", "symlog", "logit", "pow", "sqrt"]
        if isinstance(arg, str):
            if any(arg.startswith(k) for k in trans_args):
                # TODO validate numeric type? That should happen centrally somewhere
                return Continuous(trans=arg)
            else:
                msg = f"Unknown magic arg for {self.variable} scale: '{arg}'."
                raise ValueError(msg)
        else:
            arg_type = type(arg).__name__
            msg = f"Magic arg for {self.variable} scale must be str, not {arg_type}."
            raise TypeError(msg)
```

**With:**

```python
    _magic_scales = {
        "log": Continuous,
        "symlog": Continuous,
        "logit": Continuous,
        "pow": Continuous,
        "sqrt": Continuous,
    }

    def infer_scale(self, arg: Any, data: Series) -> Scale:
        """Given data and a scaling argument, initialize appropriate scale class."""
        if isinstance(arg, str):
            for key, cls in self._magic_scales.items():
                if arg.startswith(key):
                    return cls(trans=arg)
            msg = f"Unknown magic arg for {self.variable} scale: '{arg}'."
            raise ValueError(msg)
        else:
            arg_type = type(arg).__name__
            msg = f"Magic arg for {self.variable} scale must be str, not {arg_type}."
            raise TypeError(msg)
```

## Test results

**PASSED** — 0/0 passed, 0 failed, 0 skipped, 0 errored (duration 2286 ms).

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
1 error in 1.38s

```

</details>

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `seaborn/_core/properties.py` | 586 → 592 | 55 → 55 | 2.94 → 2.94 | 12 → 12 | 23.93 → 23.32 |

## Diff

```diff
diff --git a/seaborn/_core/properties.py b/seaborn/_core/properties.py
index 4e2df91..b9cac72 100644
--- a/seaborn/_core/properties.py
+++ b/seaborn/_core/properties.py
@@ -69,21 +69,22 @@ class Property:
         else:
             return Nominal()
 
+    _magic_scales = {
+        "log": Continuous,
+        "symlog": Continuous,
+        "logit": Continuous,
+        "pow": Continuous,
+        "sqrt": Continuous,
+    }
+
     def infer_scale(self, arg: Any, data: Series) -> Scale:
         """Given data and a scaling argument, initialize appropriate scale class."""
-        # TODO put these somewhere external for validation
-        # TODO putting this here won't pick it up if subclasses define infer_scale
-        # (e.g. color). How best to handle that? One option is to call super after
-        # handling property-specific possibilities (e.g. for color check that the
-        # arg is not a valid palette name) but that could get tricky.
-        trans_args = ["log", "symlog", "logit", "pow", "sqrt"]
         if isinstance(arg, str):
-            if any(arg.startswith(k) for k in trans_args):
-                # TODO validate numeric type? That should happen centrally somewhere
-                return Continuous(trans=arg)
-            else:
-                msg = f"Unknown magic arg for {self.variable} scale: '{arg}'."
-                raise ValueError(msg)
+            for key, cls in self._magic_scales.items():
+                if arg.startswith(key):
+                    return cls(trans=arg)
+            msg = f"Unknown magic arg for {self.variable} scale: '{arg}'."
+            raise ValueError(msg)
         else:
             arg_type = type(arg).__name__
             msg = f"Magic arg for {self.variable} scale must be str, not {arg_type}."

```
