# Refactor OCP-105 (OCP): Logic branches on `inner` and `density_norm` strings, requiring modification...

**Status:** `applied_passed`  
**Branch:** `refactor/OCP-105` -> `main`  
**Head commit:** `68bedf7105c28dcd5093ca34c2ee9bcde96329ed`  
**LLM finish:** `FinishReason.STOP` (prompt 7157, completion 2809)  

## Detected issue

- **File**: `seaborn/categorical.py`
- **Entity**: `_CategoricalPlotter.plot_violins` (method)
- **Lines (at detection time)**: L821–L1190
- **Severity**: high
- **Confidence**: detected by 2 scan(s)

**Description.** Logic branches on `inner` and `density_norm` strings, requiring modification for new types.

**Reasoning.** This method contains multiple `if/elif` chains: one for `inner` (`if inner is None`, `elif inner.startswith('point')`, etc.) and another for `density_norm` (`if density_norm == 'area'`, `elif density_norm == 'count'`, etc.). Introducing new 'inner' plot types or 'density_norm' methods would necessitate modifying these existing conditional blocks, which violates OCP. These behaviors should be implemented polymorphically.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `seaborn/categorical.py`

**Summary.** Refactor inner violin plot logic into a strategy-based dispatcher to improve OCP compliance.

**Rationale.** The long if/elif chain for 'inner' plot types in plot_violins was replaced with a dictionary-based strategy pattern. This allows adding new inner plot types without modifying the core plotting loop, adhering to the Open/Closed Principle.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `seaborn/categorical.py` (97-line block → 109-line replacement)

**Replaces:**

```python
            # --- Plot the inner components
            if inner is None:
                continue

            elif inner.startswith("point"):
                pos = np.array([pos_dict[self.orient]] * len(obs))
                if split:
                    pos += (-1 if right_side else 1) * pos_dict["width"] / 2
                x, y = (pos, obs) if self.orient == "x" else (obs, pos)
                kws = {
                    "color": linecolor,
                    "edgecolor": linecolor,
                    "s": (linewidth * 2) ** 2,
                    "zorder": violin["kwargs"].get("zorder", 2) + 1,
                    **inner_kws,
                }
                ax.scatter(invx(x), invy(y), **kws)

            elif inner.startswith("stick"):
                pos0 = np.interp(obs, data[value_var], data[self.orient] - offsets[0])
                pos1 = np.interp(obs, data[value_var], data[self.orient] + offsets[1])
                pos_pts = np.stack([inv_pos(pos0), inv_pos(pos1)])
                val_pts = np.stack([inv_val(obs), inv_val(obs)])
                segments = np.stack([pos_pts, val_pts]).transpose(2, 1, 0)
                if self.orient == "y":
                    segments = segments[:, :, ::-1]
                kws = {
                    "color": linecolor,
                    "linewidth": linewidth / 2,
                    **inner_kws,
                }
                lines = mpl.collections.LineCollection(segments, **kws)
                ax.add_collection(lines, autolim=False)

            elif inner.startswith("quart"):
                stats = np.percentile(obs, [25, 50, 75])
                pos0 = np.interp(stats, data[value_var], data[self.orient] - offsets[0])
                pos1 = np.interp(stats, data[value_var], data[self.orient] + offsets[1])
                pos_pts = np.stack([inv_pos(pos0), inv_pos(pos1)])
                val_pts = np.stack([inv_val(stats), inv_val(stats)])
                segments = np.stack([pos_pts, val_pts]).transpose(2, 0, 1)
                if self.orient == "y":
                    segments = segments[:, ::-1, :]
                dashes = [(1.25, .75), (2.5, 1), (1.25, .75)]
                for i, segment in enumerate(segments):
                    kws = {
                        "color": linecolor,
                        "linewidth": linewidth,
                        "dashes": dashes[i],
                        **inner_kws,
                    }
                    ax.plot(*segment, **kws)

            elif inner.startswith("box"):
                stats = mpl.cbook.boxplot_stats(obs)[0]
                pos = np.array(pos_dict[self.orient])
                if split:
                    pos += (-1 if right_side else 1) * pos_dict["width"] / 2
                pos = [pos, pos], [pos, pos], [pos]
                val = (
... (37 more line(s) truncated)
```

**With:**

```python
            # --- Plot the inner components
            if inner is None:
                continue

            def _plot_point(ax, obs, pos_dict, right_side, split, linecolor, linewidth, inner_kws):
                pos = np.array([pos_dict[self.orient]] * len(obs))
                if split:
                    pos += (-1 if right_side else 1) * pos_dict["width"] / 2
                x, y = (pos, obs) if self.orient == "x" else (obs, pos)
                kws = {
                    "color": linecolor,
                    "edgecolor": linecolor,
                    "s": (linewidth * 2) ** 2,
                    "zorder": violin["kwargs"].get("zorder", 2) + 1,
                    **inner_kws,
                }
                ax.scatter(invx(x), invy(y), **kws)

            def _plot_stick(ax, obs, data, offsets, linecolor, linewidth, inner_kws):
                pos0 = np.interp(obs, data[value_var], data[self.orient] - offsets[0])
                pos1 = np.interp(obs, data[value_var], data[self.orient] + offsets[1])
                pos_pts = np.stack([inv_pos(pos0), inv_pos(pos1)])
                val_pts = np.stack([inv_val(obs), inv_val(obs)])
                segments = np.stack([pos_pts, val_pts]).transpose(2, 1, 0)
                if self.orient == "y":
                    segments = segments[:, :, ::-1]
                kws = {
                    "color": linecolor,
                    "linewidth": linewidth / 2,
                    **inner_kws,
                }
                lines = mpl.collections.LineCollection(segments, **kws)
                ax.add_collection(lines, autolim=False)

            def _plot_quart(ax, obs, data, offsets, linecolor, linewidth, inner_kws):
                stats = np.percentile(obs, [25, 50, 75])
                pos0 = np.interp(stats, data[value_var], data[self.orient] - offsets[0])
                pos1 = np.interp(stats, data[value_var], data[self.orient] + offsets[1])
                pos_pts = np.stack([inv_pos(pos0), inv_pos(pos1)])
                val_pts = np.stack([inv_val(stats), inv_val(stats)])
                segments = np.stack([pos_pts, val_pts]).transpose(2, 0, 1)
                if self.orient == "y":
                    segments = segments[:, ::-1, :]
                dashes = [(1.25, .75), (2.5, 1), (1.25, .75)]
                for i, segment in enumerate(segments):
                    kws = {
                        "color": linecolor,
                        "linewidth": linewidth,
                        "dashes": dashes[i],
                        **inner_kws,
                    }
                    ax.plot(*segment, **kws)

            def _plot_box(ax, obs, pos_dict, right_side, split, linecolor, linewidth, inner_kws):
                stats = mpl.cbook.boxplot_stats(obs)[0]
                pos = np.array(pos_dict[self.orient])
                if split:
                    pos += (-1 if right_side else 1) * pos_dict["width"] / 2
                pos = [pos, pos], [pos, pos], [pos]
                val = (
... (49 more line(s) truncated)
```

## Test results

**PASSED** — 0/0 passed, 0 failed, 0 skipped, 0 errored (duration 2219 ms).

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
| `seaborn/categorical.py` | 2645 → 2655 | 65 → 69 | 7.23 → 6.96 | 53 → 39 | 0 → 0 |

## Diff

```diff
diff --git a/seaborn/categorical.py b/seaborn/categorical.py
index 3fa5a07..a31acf1 100644
--- a/seaborn/categorical.py
+++ b/seaborn/categorical.py
@@ -1092,7 +1092,7 @@ class _CategoricalPlotter(VectorPlotter):
             if inner is None:
                 continue
 
-            elif inner.startswith("point"):
+            def _plot_point(ax, obs, pos_dict, right_side, split, linecolor, linewidth, inner_kws):
                 pos = np.array([pos_dict[self.orient]] * len(obs))
                 if split:
                     pos += (-1 if right_side else 1) * pos_dict["width"] / 2
@@ -1106,7 +1106,7 @@ class _CategoricalPlotter(VectorPlotter):
                 }
                 ax.scatter(invx(x), invy(y), **kws)
 
-            elif inner.startswith("stick"):
+            def _plot_stick(ax, obs, data, offsets, linecolor, linewidth, inner_kws):
                 pos0 = np.interp(obs, data[value_var], data[self.orient] - offsets[0])
                 pos1 = np.interp(obs, data[value_var], data[self.orient] + offsets[1])
                 pos_pts = np.stack([inv_pos(pos0), inv_pos(pos1)])
@@ -1122,7 +1122,7 @@ class _CategoricalPlotter(VectorPlotter):
                 lines = mpl.collections.LineCollection(segments, **kws)
                 ax.add_collection(lines, autolim=False)
 
-            elif inner.startswith("quart"):
+            def _plot_quart(ax, obs, data, offsets, linecolor, linewidth, inner_kws):
                 stats = np.percentile(obs, [25, 50, 75])
                 pos0 = np.interp(stats, data[value_var], data[self.orient] - offsets[0])
                 pos1 = np.interp(stats, data[value_var], data[self.orient] + offsets[1])
@@ -1141,7 +1141,7 @@ class _CategoricalPlotter(VectorPlotter):
                     }
                     ax.plot(*segment, **kws)
 
-            elif inner.startswith("box"):
+            def _plot_box(ax, obs, pos_dict, right_side, split, linecolor, linewidth, inner_kws):
                 stats = mpl.cbook.boxplot_stats(obs)[0]
                 pos = np.array(pos_dict[self.orient])
                 if split:
@@ -1182,10 +1182,22 @@ class _CategoricalPlotter(VectorPlotter):
                     **inner_kws,
                     "markeredgecolor": "w",
                     "markerfacecolor": "w",
-                    "color": linecolor,  # simplify tests
+                    "color": linecolor,
                 }
                 ax.plot(invx(x2), invy(y2), **dot_kws)
 
+            strategies = {
+                "point": lambda: _plot_point(ax, obs, pos_dict, right_side, split, linecolor, linewidth, inner_kws),
+                "stick": lambda: _plot_stick(ax, obs, data, offsets, linecolor, linewidth, inner_kws),
+                "quart": lambda: _plot_quart(ax, obs, data, offsets, linecolor, linewidth, inner_kws),
+                "box": lambda: _plot_box(ax, obs, pos_dict, right_side, split, linecolor, linewidth, inner_kws),
+            }
+
+            for key, func in strategies.items():
+                if inner.startswith(key):
+                    func()
+                    break
+
         legend_artist = _get_patch_legend_artist(fill)
         common_kws = {**plot_kws, "linewidth": linewidth, "edgecolor": linecolor}
         self._configure_legend(ax, legend_artist, common_kws)

```
