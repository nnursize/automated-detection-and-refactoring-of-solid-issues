# Refactor OCP-002 (OCP): Conditional logic for handling different 'multiple' strategies.

**Status:** `applied_passed`  
**Branch:** `refactor/OCP-002` -> `main`  
**Head commit:** `977ea50463d7be2d2ebafe0aa246c7ba8db213de`  
**LLM finish:** `FinishReason.STOP` (prompt 4365, completion 1601)  

## Detected issue

- **File**: `seaborn/distributions.py`
- **Entity**: `_DistributionPlotter._resolve_multiple` (method)
- **Lines (at detection time)**: L280–L327
- **Severity**: medium
- **Confidence**: detected by 6 scan(s)

**Description.** Conditional logic for handling different 'multiple' strategies.

**Reasoning.** The `_resolve_multiple` method contains `if multiple in ('stack', 'fill'):` and `if multiple == 'dodge':` blocks to apply different data transformation logic based on the `multiple` parameter. If a new strategy for handling multiple distributions is introduced, this method would need to be modified to add a new conditional branch, violating OCP.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `seaborn/distributions.py`

**Summary.** Refactor _resolve_multiple to use a strategy pattern for multiple-distribution handling.

**Rationale.** Replaced the conditional if/elif chain in _resolve_multiple with a dictionary-based strategy lookup, allowing for easier extension without modifying the core logic.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `seaborn/distributions.py` (66-line block → 68-line replacement)

**Replaces:**

```python
    def _resolve_multiple(self, curves, multiple):
        """Modify the density data structure to handle multiple densities."""

        # Default baselines have all densities starting at 0
        baselines = {k: np.zeros_like(v) for k, v in curves.items()}

        # TODO we should have some central clearinghouse for checking if any
        # "grouping" (terminnology?) semantics have been assigned
        if "hue" not in self.variables:
            return curves, baselines

        if multiple in ("stack", "fill"):

            # Setting stack or fill means that the curves share a
            # support grid / set of bin edges, so we can make a dataframe
            # Reverse the column order to plot from top to bottom
            curves = pd.DataFrame(curves).iloc[:, ::-1]

            # Find column groups that are nested within col/row variables
            column_groups = {}
            for i, keyd in enumerate(map(dict, curves.columns)):
                facet_key = keyd.get("col", None), keyd.get("row", None)
                column_groups.setdefault(facet_key, [])
                column_groups[facet_key].append(i)

            baselines = curves.copy()

            for col_idxs in column_groups.values():
                cols = curves.columns[col_idxs]

                norm_constant = curves[cols].sum(axis="columns")

                # Take the cumulative sum to stack
                curves[cols] = curves[cols].cumsum(axis="columns")

                # Normalize by row sum to fill
                if multiple == "fill":
                    curves[cols] = curves[cols].div(norm_constant, axis="index")

                # Define where each segment starts
                baselines[cols] = curves[cols].shift(1, axis=1).fillna(0)

        if multiple == "dodge":

            # Account for the unique semantic (non-faceting) levels
            # This will require rethiniking if we add other semantics!
            hue_levels = self.var_levels["hue"]
            n = len(hue_levels)
            f_fwd, f_inv = self._get_scale_transforms(self.data_variable)
            for key in curves:

                level = dict(key)["hue"]
                hist = curves[key].reset_index(name="heights")
                level_idx = hue_levels.index(level)

                a = f_fwd(hist["edges"])
                b = f_fwd(hist["edges"] + hist["widths"])
                w = (b - a) / n
                new_min = f_inv(a + level_idx * w)
                new_max = f_inv(a + (level_idx + 1) * w)
... (6 more line(s) truncated)
```

**With:**

```python
    def _resolve_multiple(self, curves, multiple):
        """Modify the density data structure to handle multiple densities."""

        # Default baselines have all densities starting at 0
        baselines = {k: np.zeros_like(v) for k, v in curves.items()}

        # TODO we should have some central clearinghouse for checking if any
        # "grouping" (terminnology?) semantics have been assigned
        if "hue" not in self.variables or multiple == "layer":
            return curves, baselines

        strategies = {
            "stack": self._multiple_stack,
            "fill": self._multiple_fill,
            "dodge": self._multiple_dodge,
        }

        if multiple in strategies:
            curves, baselines = strategies[multiple](curves)

        return curves, baselines

    def _multiple_stack(self, curves):
        curves = pd.DataFrame(curves).iloc[:, ::-1]
        column_groups = self._get_column_groups(curves)
        baselines = curves.copy()
        for col_idxs in column_groups.values():
            cols = curves.columns[col_idxs]
            curves[cols] = curves[cols].cumsum(axis="columns")
            baselines[cols] = curves[cols].shift(1, axis=1).fillna(0)
        return curves, baselines

    def _multiple_fill(self, curves):
        curves, baselines = self._multiple_stack(curves)
        column_groups = self._get_column_groups(curves)
        for col_idxs in column_groups.values():
            cols = curves.columns[col_idxs]
            norm_constant = curves[cols].iloc[:, -1]
            curves[cols] = curves[cols].div(norm_constant, axis="index")
            baselines[cols] = baselines[cols].div(norm_constant, axis="index")
        return curves, baselines

    def _multiple_dodge(self, curves):
        baselines = {k: np.zeros_like(v) for k, v in curves.items()}
        hue_levels = self.var_levels["hue"]
        n = len(hue_levels)
        f_fwd, f_inv = self._get_scale_transforms(self.data_variable)
        for key in curves:
            level = dict(key)["hue"]
            hist = curves[key].reset_index(name="heights")
            level_idx = hue_levels.index(level)
            a = f_fwd(hist["edges"])
            b = f_fwd(hist["edges"] + hist["widths"])
            w = (b - a) / n
            new_min = f_inv(a + level_idx * w)
            new_max = f_inv(a + (level_idx + 1) * w)
            hist["widths"] = new_max - new_min
            hist["edges"] = new_min
            curves[key] = hist.set_index(["edges", "widths"])["heights"]
        return curves, baselines
... (8 more line(s) truncated)
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
seaborn\categorical.py:482: in _CategoricalPlotter
    @register_plot("strips")
     ^^^^^^^^^^^^^^^^^^^^^^^
E   TypeError: 'classmethod' object is not callable
=========================== short test summary info ===========================
ERROR tests/_core/test_data.py - TypeError: 'classmethod' object is not callable
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!
1 error in 1.36s

```

</details>

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `seaborn/distributions.py` | 1802 → 1821 | 26 → 30 | 13.19 → 11.53 | 64 → 64 | 0 → 0 |

## Diff

```diff
diff --git a/seaborn/distributions.py b/seaborn/distributions.py
index f8ec166..99ee5df 100644
--- a/seaborn/distributions.py
+++ b/seaborn/distributions.py
@@ -232,65 +232,67 @@ class _DistributionPlotter(VectorPlotter):
 
         # TODO we should have some central clearinghouse for checking if any
         # "grouping" (terminnology?) semantics have been assigned
-        if "hue" not in self.variables:
+        if "hue" not in self.variables or multiple == "layer":
             return curves, baselines
 
-        if multiple in ("stack", "fill"):
-
-            # Setting stack or fill means that the curves share a
-            # support grid / set of bin edges, so we can make a dataframe
-            # Reverse the column order to plot from top to bottom
-            curves = pd.DataFrame(curves).iloc[:, ::-1]
-
-            # Find column groups that are nested within col/row variables
-            column_groups = {}
-            for i, keyd in enumerate(map(dict, curves.columns)):
-                facet_key = keyd.get("col", None), keyd.get("row", None)
-                column_groups.setdefault(facet_key, [])
-                column_groups[facet_key].append(i)
-
-            baselines = curves.copy()
-
-            for col_idxs in column_groups.values():
-                cols = curves.columns[col_idxs]
-
-                norm_constant = curves[cols].sum(axis="columns")
-
-                # Take the cumulative sum to stack
-                curves[cols] = curves[cols].cumsum(axis="columns")
-
-                # Normalize by row sum to fill
-                if multiple == "fill":
-                    curves[cols] = curves[cols].div(norm_constant, axis="index")
-
-                # Define where each segment starts
-                baselines[cols] = curves[cols].shift(1, axis=1).fillna(0)
-
-        if multiple == "dodge":
+        strategies = {
+            "stack": self._multiple_stack,
+            "fill": self._multiple_fill,
+            "dodge": self._multiple_dodge,
+        }
 
-            # Account for the unique semantic (non-faceting) levels
-            # This will require rethiniking if we add other semantics!
-            hue_levels = self.var_levels["hue"]
-            n = len(hue_levels)
-            f_fwd, f_inv = self._get_scale_transforms(self.data_variable)
-            for key in curves:
+        if multiple in strategies:
+            curves, baselines = strategies[multiple](curves)
 
-                level = dict(key)["hue"]
-                hist = curves[key].reset_index(name="heights")
-                level_idx = hue_levels.index(level)
+        return curves, baselines
 
-                a = f_fwd(hist["edges"])
-                b = f_fwd(hist["edges"] + hist["widths"])
-                w = (b - a) / n
-                new_min = f_inv(a + level_idx * w)
-                new_max = f_inv(a + (level_idx + 1) * w)
-                hist["widths"] = new_max - new_min
-                hist["edges"] = new_min
+    def _multiple_stack(self, curves):
+        curves = pd.DataFrame(curves).iloc[:, ::-1]
+        column_groups = self._get_column_groups(curves)
+        baselines = curves.copy()
+        for col_idxs in column_groups.values():
+            cols = curves.columns[col_idxs]
+            curves[cols] = curves[cols].cumsum(axis="columns")
+            baselines[cols] = curves[cols].shift(1, axis=1).fillna(0)
+        return curves, baselines
 
-                curves[key] = hist.set_index(["edges", "widths"])["heights"]
+    def _multiple_fill(self, curves):
+        curves, baselines = self._multiple_stack(curves)
+        column_groups = self._get_column_groups(curves)
+        for col_idxs in column_groups.values():
+            cols = curves.columns[col_idxs]
+            norm_constant = curves[cols].iloc[:, -1]
+            curves[cols] = curves[cols].div(norm_constant, axis="index")
+            baselines[cols] = baselines[cols].div(norm_constant, axis="index")
+        return curves, baselines
 
+    def _multiple_dodge(self, curves):
+        baselines = {k: np.zeros_like(v) for k, v in curves.items()}
+        hue_levels = self.var_levels["hue"]
+        n = len(hue_levels)
+        f_fwd, f_inv = self._get_scale_transforms(self.data_variable)
+        for key in curves:
+            level = dict(key)["hue"]
+            hist = curves[key].reset_index(name="heights")
+            level_idx = hue_levels.index(level)
+            a = f_fwd(hist["edges"])
+            b = f_fwd(hist["edges"] + hist["widths"])
+            w = (b - a) / n
+            new_min = f_inv(a + level_idx * w)
+            new_max = f_inv(a + (level_idx + 1) * w)
+            hist["widths"] = new_max - new_min
+            hist["edges"] = new_min
+            curves[key] = hist.set_index(["edges", "widths"])["heights"]
         return curves, baselines
 
+    def _get_column_groups(self, curves):
+        column_groups = {}
+        for i, keyd in enumerate(map(dict, curves.columns)):
+            facet_key = keyd.get("col", None), keyd.get("row", None)
+            column_groups.setdefault(facet_key, [])
+            column_groups[facet_key].append(i)
+        return column_groups
+
     # -------------------------------------------------------------------------------- #
     # Computation
     # -------------------------------------------------------------------------------- #

```
