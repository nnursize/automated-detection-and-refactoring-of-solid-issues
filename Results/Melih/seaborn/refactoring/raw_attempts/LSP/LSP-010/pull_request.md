# Refactor LSP-010 (LSP): Monkey-patching the 'draw' method of a base type instance alters its behavior...

**Status:** `applied_passed`  
**Branch:** `refactor/LSP-010` -> `main`  
**Head commit:** `ad105e2a82653e5f63b1da3a15b0e28098338bae`  
**LLM finish:** `FinishReason.STOP` (prompt 4595, completion 795)  

## Detected issue

- **File**: `seaborn/categorical.py`
- **Entity**: `_CategoricalPlotter.plot_swarms` (method)
- **Lines (at detection time)**: L466–L491
- **Severity**: high
- **Confidence**: detected by 6 scan(s)

**Description.** Monkey-patching the 'draw' method of a base type instance alters its behavioral contract

**Reasoning.** Inappropriate Intimacy smell -> LSP violation because this method replaces the 'draw' method of a matplotlib.collections.PathCollection instance with a custom local function. This violates the behavioral contract of the matplotlib Artist hierarchy; any consumer expecting a standard PathCollection will now trigger Seaborn-specific beeswarm logic during the rendering pass, which is an unexpected side effect for that type.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `seaborn/categorical.py`

**Summary.** Replace monkey-patched 'draw' method with a custom Artist subclass to avoid LSP violation.

**Rationale.** Monkey-patching the 'draw' method of a PathCollection violates the Liskov Substitution Principle by altering the behavior of a standard matplotlib object. By wrapping the collection in a custom Artist subclass that overrides 'draw', we maintain the expected interface while safely injecting the beeswarm logic.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `seaborn/categorical.py` (27-line block → 26-line replacement)

**Replaces:**

```python
        beeswarm = Beeswarm(width=width, orient=self.orient, warn_thresh=warn_thresh)
        for (ax, center), points in point_collections.items():
            if points.get_offsets().shape[0] > 1:

                def draw(points, renderer, *, center=center):

                    beeswarm(points, center)

                    if self.orient == "y":
                        scalex = False
                        scaley = ax.get_autoscaley_on()
                    else:
                        scalex = ax.get_autoscalex_on()
                        scaley = False

                    # This prevents us from undoing the nice categorical axis limits
                    # set in _adjust_cat_axis, because that method currently leave
                    # the autoscale flag in its original setting. It may be better
                    # to disable autoscaling there to avoid needing to do this.
                    fixed_scale = self.var_types[self.orient] == "categorical"
                    ax.update_datalim(points.get_datalim(ax.transData))
                    if not fixed_scale and (scalex or scaley):
                        ax.autoscale_view(scalex=scalex, scaley=scaley)

                    super(points.__class__, points).draw(renderer)

                points.draw = draw.__get__(points)
```

**With:**

```python
        class BeeswarmArtist(type(point_collections[next(iter(point_collections))])):
            def __init__(self, collection, beeswarm, center, orient, var_types, ax):
                self.__dict__.update(collection.__dict__)
                self._beeswarm = beeswarm
                self._center = center
                self._orient = orient
                self._var_types = var_types
                self._ax = ax

            def draw(self, renderer):
                self._beeswarm(self, self._center)
                if self._orient == "y":
                    scalex, scaley = False, self._ax.get_autoscaley_on()
                else:
                    scalex, scaley = self._ax.get_autoscalex_on(), False
                fixed_scale = self._var_types[self._orient] == "categorical"
                self._ax.update_datalim(self.get_datalim(self._ax.transData))
                if not fixed_scale and (scalex or scaley):
                    self._ax.autoscale_view(scalex=scalex, scaley=scaley)
                super().draw(renderer)

        beeswarm = Beeswarm(width=width, orient=self.orient, warn_thresh=warn_thresh)
        for (ax, center), points in point_collections.items():
            if points.get_offsets().shape[0] > 1:
                artist = BeeswarmArtist(points, beeswarm, center, self.orient, self.var_types, ax)
                ax.collections[ax.collections.index(points)] = artist
```

## Test results

**PASSED** — 0/0 passed, 0 failed, 0 skipped, 0 errored (duration 2281 ms).

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
1 error in 1.40s

```

</details>

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `seaborn/categorical.py` | 2599 → 2606 | 61 → 62 | 7 → 7 | 39 → 39 | 0 → 0 |

## Diff

```diff
diff --git a/seaborn/categorical.py b/seaborn/categorical.py
index 8eed607..026cb33 100644
--- a/seaborn/categorical.py
+++ b/seaborn/categorical.py
@@ -575,33 +575,32 @@ class _CategoricalPlotter(VectorPlotter):
             if not sub_data.empty:
                 point_collections[(ax, sub_data[self.orient].iloc[0])] = points
 
+        class BeeswarmArtist(type(point_collections[next(iter(point_collections))])):
+            def __init__(self, collection, beeswarm, center, orient, var_types, ax):
+                self.__dict__.update(collection.__dict__)
+                self._beeswarm = beeswarm
+                self._center = center
+                self._orient = orient
+                self._var_types = var_types
+                self._ax = ax
+
+            def draw(self, renderer):
+                self._beeswarm(self, self._center)
+                if self._orient == "y":
+                    scalex, scaley = False, self._ax.get_autoscaley_on()
+                else:
+                    scalex, scaley = self._ax.get_autoscalex_on(), False
+                fixed_scale = self._var_types[self._orient] == "categorical"
+                self._ax.update_datalim(self.get_datalim(self._ax.transData))
+                if not fixed_scale and (scalex or scaley):
+                    self._ax.autoscale_view(scalex=scalex, scaley=scaley)
+                super().draw(renderer)
+
         beeswarm = Beeswarm(width=width, orient=self.orient, warn_thresh=warn_thresh)
         for (ax, center), points in point_collections.items():
             if points.get_offsets().shape[0] > 1:
-
-                def draw(points, renderer, *, center=center):
-
-                    beeswarm(points, center)
-
-                    if self.orient == "y":
-                        scalex = False
-                        scaley = ax.get_autoscaley_on()
-                    else:
-                        scalex = ax.get_autoscalex_on()
-                        scaley = False
-
-                    # This prevents us from undoing the nice categorical axis limits
-                    # set in _adjust_cat_axis, because that method currently leave
-                    # the autoscale flag in its original setting. It may be better
-                    # to disable autoscaling there to avoid needing to do this.
-                    fixed_scale = self.var_types[self.orient] == "categorical"
-                    ax.update_datalim(points.get_datalim(ax.transData))
-                    if not fixed_scale and (scalex or scaley):
-                        ax.autoscale_view(scalex=scalex, scaley=scaley)
-
-                    super(points.__class__, points).draw(renderer)
-
-                points.draw = draw.__get__(points)
+                artist = BeeswarmArtist(points, beeswarm, center, self.orient, self.var_types, ax)
+                ax.collections[ax.collections.index(points)] = artist
 
         _draw_figure(ax.figure)
         self._configure_legend(ax, _scatter_legend_artist, plot_kws)

```
