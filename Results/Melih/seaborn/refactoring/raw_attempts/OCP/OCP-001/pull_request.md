# Refactor OCP-001 (OCP): Long if/elif/else chain for dispatching plot kinds.

**Status:** `applied_passed`  
**Branch:** `refactor/OCP-001` -> `main`  
**Head commit:** `f8f7cbd97fdc89a534e3b78c3c8911cc50837781`  
**LLM finish:** `FinishReason.STOP` (prompt 7387, completion 4793)  

## Detected issue

- **File**: `seaborn/categorical.py`
- **Entity**: `catplot` (class)
- **Lines (at detection time)**: L1086–L1260
- **Severity**: high
- **Confidence**: detected by 4 scan(s)

**Description.** Long if/elif/else chain for dispatching plot kinds.

**Reasoning.** The `catplot` function uses a long `if/elif/else` chain based on the `kind` string parameter to dispatch to different plotting logic. To introduce a new categorical plot type, this function would require modification to add a new `elif` branch, directly violating the Open/Closed Principle. A more OCP-compliant design would involve a registry or a strategy pattern where new plot kinds can be registered without modifying `catplot`.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `seaborn/categorical.py`

**Summary.** Refactor catplot dispatch logic to use a registry pattern.

**Rationale.** Replaced the long if/elif/else chain in catplot with a registry dictionary mapping 'kind' strings to handler functions, improving extensibility and adhering to the Open/Closed Principle.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `seaborn/categorical.py` (241-line block → 121-line replacement)

**Replaces:**

```python
    if kind == "strip":

        jitter = kwargs.pop("jitter", True)
        plot_kws = kwargs.copy()
        plot_kws.setdefault("zorder", 3)
        plot_kws.setdefault("linewidth", 0)
        if "s" not in plot_kws:
            plot_kws["s"] = plot_kws.pop("size", 5) ** 2

        p.plot_strips(
            jitter=jitter,
            dodge=dodge,
            color=color,
            plot_kws=plot_kws,
        )

    elif kind == "swarm":

        warn_thresh = kwargs.pop("warn_thresh", .05)
        plot_kws = kwargs.copy()
        plot_kws.setdefault("zorder", 3)
        if "s" not in plot_kws:
            plot_kws["s"] = plot_kws.pop("size", 5) ** 2

        if plot_kws.setdefault("linewidth", 0) is None:
            plot_kws["linewidth"] = np.sqrt(plot_kws["s"]) / 10

        p.plot_swarms(
            dodge=dodge,
            color=color,
            warn_thresh=warn_thresh,
            plot_kws=plot_kws,
        )

    elif kind == "box":

        plot_kws = kwargs.copy()
        gap = plot_kws.pop("gap", 0)
        fill = plot_kws.pop("fill", True)
        whis = plot_kws.pop("whis", 1.5)
        linewidth = plot_kws.pop("linewidth", None)
        fliersize = plot_kws.pop("fliersize", 5)
        linecolor = p._complement_color(
            plot_kws.pop("linecolor", "auto"), color, p._hue_map
        )

        p.plot_boxes(
            width=width,
            dodge=dodge,
            gap=gap,
            fill=fill,
            whis=whis,
            color=color,
            linecolor=linecolor,
            linewidth=linewidth,
            fliersize=fliersize,
            plot_kws=plot_kws,
        )

    elif kind == "violin":
... (181 more line(s) truncated)
```

**With:**

```python
    def _plot_strip(p, dodge, color, kwargs):
        jitter = kwargs.pop("jitter", True)
        plot_kws = kwargs.copy()
        plot_kws.setdefault("zorder", 3)
        plot_kws.setdefault("linewidth", 0)
        if "s" not in plot_kws:
            plot_kws["s"] = plot_kws.pop("size", 5) ** 2
        p.plot_strips(jitter=jitter, dodge=dodge, color=color, plot_kws=plot_kws)

    def _plot_swarm(p, dodge, color, kwargs):
        warn_thresh = kwargs.pop("warn_thresh", .05)
        plot_kws = kwargs.copy()
        plot_kws.setdefault("zorder", 3)
        if "s" not in plot_kws:
            plot_kws["s"] = plot_kws.pop("size", 5) ** 2
        if plot_kws.setdefault("linewidth", 0) is None:
            plot_kws["linewidth"] = np.sqrt(plot_kws["s"]) / 10
        p.plot_swarms(dodge=dodge, color=color, warn_thresh=warn_thresh, plot_kws=plot_kws)

    def _plot_box(p, dodge, color, kwargs):
        plot_kws = kwargs.copy()
        gap = plot_kws.pop("gap", 0)
        fill = plot_kws.pop("fill", True)
        whis = plot_kws.pop("whis", 1.5)
        linewidth = plot_kws.pop("linewidth", None)
        fliersize = plot_kws.pop("fliersize", 5)
        linecolor = p._complement_color(plot_kws.pop("linecolor", "auto"), color, p._hue_map)
        p.plot_boxes(width=width, dodge=dodge, gap=gap, fill=fill, whis=whis, color=color,
                     linecolor=linecolor, linewidth=linewidth, fliersize=fliersize, plot_kws=plot_kws)

    def _plot_violin(p, dodge, color, kwargs):
        plot_kws = kwargs.copy()
        gap = plot_kws.pop("gap", 0)
        fill = plot_kws.pop("fill", True)
        split = plot_kws.pop("split", False)
        inner = plot_kws.pop("inner", "box")
        density_norm = plot_kws.pop("density_norm", "area")
        common_norm = plot_kws.pop("common_norm", False)
        scale = plot_kws.pop("scale", deprecated)
        scale_hue = plot_kws.pop("scale_hue", deprecated)
        density_norm, common_norm = p._violin_scale_backcompat(scale, scale_hue, density_norm, common_norm)
        bw_method = p._violin_bw_backcompat(plot_kws.pop("bw", deprecated), plot_kws.pop("bw_method", "scott"))
        kde_kws = dict(cut=plot_kws.pop("cut", 2), gridsize=plot_kws.pop("gridsize", 100),
                       bw_adjust=plot_kws.pop("bw_adjust", 1), bw_method=bw_method)
        inner_kws = plot_kws.pop("inner_kws", {}).copy()
        linewidth = plot_kws.pop("linewidth", None)
        linecolor = p._complement_color(plot_kws.pop("linecolor", "auto"), color, p._hue_map)
        p.plot_violins(width=width, dodge=dodge, gap=gap, split=split, color=color, fill=fill,
                       linecolor=linecolor, linewidth=linewidth, inner=inner, density_norm=density_norm,
                       common_norm=common_norm, kde_kws=kde_kws, inner_kws=inner_kws, plot_kws=plot_kws)

    def _plot_boxen(p, dodge, color, kwargs):
        plot_kws = kwargs.copy()
        gap = plot_kws.pop("gap", 0)
        fill = plot_kws.pop("fill", True)
        linecolor = plot_kws.pop("linecolor", "auto")
        linewidth = plot_kws.pop("linewidth", None)
        k_depth = plot_kws.pop("k_depth", "tukey")
        width_method = plot_kws.pop("width_method", "exponential")
        outlier_prop = plot_kws.pop("outlier_prop", 0.007)
... (61 more line(s) truncated)
```

## Test results

**PASSED** — 0/0 passed, 0 failed, 0 skipped, 0 errored (duration 2249 ms).

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
| `seaborn/categorical.py` | 2736 → 2645 | 57 → 65 | 7.46 → 7.23 | 53 → 53 | 0 → 0 |

## Diff

```diff
diff --git a/seaborn/categorical.py b/seaborn/categorical.py
index dcbddc2..ac13759 100644
--- a/seaborn/categorical.py
+++ b/seaborn/categorical.py
@@ -2904,67 +2904,37 @@ def catplot(
     else:
         agg_cls = EstimateAggregator
 
-    if kind == "strip":
-
+    def _plot_strip(p, dodge, color, kwargs):
         jitter = kwargs.pop("jitter", True)
         plot_kws = kwargs.copy()
         plot_kws.setdefault("zorder", 3)
         plot_kws.setdefault("linewidth", 0)
         if "s" not in plot_kws:
             plot_kws["s"] = plot_kws.pop("size", 5) ** 2
+        p.plot_strips(jitter=jitter, dodge=dodge, color=color, plot_kws=plot_kws)
 
-        p.plot_strips(
-            jitter=jitter,
-            dodge=dodge,
-            color=color,
-            plot_kws=plot_kws,
-        )
-
-    elif kind == "swarm":
-
+    def _plot_swarm(p, dodge, color, kwargs):
         warn_thresh = kwargs.pop("warn_thresh", .05)
         plot_kws = kwargs.copy()
         plot_kws.setdefault("zorder", 3)
         if "s" not in plot_kws:
             plot_kws["s"] = plot_kws.pop("size", 5) ** 2
-
         if plot_kws.setdefault("linewidth", 0) is None:
             plot_kws["linewidth"] = np.sqrt(plot_kws["s"]) / 10
+        p.plot_swarms(dodge=dodge, color=color, warn_thresh=warn_thresh, plot_kws=plot_kws)
 
-        p.plot_swarms(
-            dodge=dodge,
-            color=color,
-            warn_thresh=warn_thresh,
-            plot_kws=plot_kws,
-        )
-
-    elif kind == "box":
-
+    def _plot_box(p, dodge, color, kwargs):
         plot_kws = kwargs.copy()
         gap = plot_kws.pop("gap", 0)
         fill = plot_kws.pop("fill", True)
         whis = plot_kws.pop("whis", 1.5)
         linewidth = plot_kws.pop("linewidth", None)
         fliersize = plot_kws.pop("fliersize", 5)
-        linecolor = p._complement_color(
-            plot_kws.pop("linecolor", "auto"), color, p._hue_map
-        )
-
-        p.plot_boxes(
-            width=width,
-            dodge=dodge,
-            gap=gap,
-            fill=fill,
-            whis=whis,
-            color=color,
-            linecolor=linecolor,
-            linewidth=linewidth,
-            fliersize=fliersize,
-            plot_kws=plot_kws,
-        )
-
-    elif kind == "violin":
+        linecolor = p._complement_color(plot_kws.pop("linecolor", "auto"), color, p._hue_map)
+        p.plot_boxes(width=width, dodge=dodge, gap=gap, fill=fill, whis=whis, color=color,
+                     linecolor=linecolor, linewidth=linewidth, fliersize=fliersize, plot_kws=plot_kws)
 
+    def _plot_violin(p, dodge, color, kwargs):
         plot_kws = kwargs.copy()
         gap = plot_kws.pop("gap", 0)
         fill = plot_kws.pop("fill", True)
@@ -2972,47 +2942,20 @@ def catplot(
         inner = plot_kws.pop("inner", "box")
         density_norm = plot_kws.pop("density_norm", "area")
         common_norm = plot_kws.pop("common_norm", False)
-
         scale = plot_kws.pop("scale", deprecated)
         scale_hue = plot_kws.pop("scale_hue", deprecated)
-        density_norm, common_norm = p._violin_scale_backcompat(
-            scale, scale_hue, density_norm, common_norm,
-        )
-
-        bw_method = p._violin_bw_backcompat(
-            plot_kws.pop("bw", deprecated), plot_kws.pop("bw_method", "scott")
-        )
-        kde_kws = dict(
-            cut=plot_kws.pop("cut", 2),
-            gridsize=plot_kws.pop("gridsize", 100),
-            bw_adjust=plot_kws.pop("bw_adjust", 1),
-            bw_method=bw_method,
-        )
-
+        density_norm, common_norm = p._violin_scale_backcompat(scale, scale_hue, density_norm, common_norm)
+        bw_method = p._violin_bw_backcompat(plot_kws.pop("bw", deprecated), plot_kws.pop("bw_method", "scott"))
+        kde_kws = dict(cut=plot_kws.pop("cut", 2), gridsize=plot_kws.pop("gridsize", 100),
+                       bw_adjust=plot_kws.pop("bw_adjust", 1), bw_method=bw_method)
         inner_kws = plot_kws.pop("inner_kws", {}).copy()
         linewidth = plot_kws.pop("linewidth", None)
-        linecolor = plot_kws.pop("linecolor", "auto")
-        linecolor = p._complement_color(linecolor, color, p._hue_map)
-
-        p.plot_violins(
-            width=width,
-            dodge=dodge,
-            gap=gap,
-            split=split,
-            color=color,
-            fill=fill,
-            linecolor=linecolor,
-            linewidth=linewidth,
-            inner=inner,
-            density_norm=density_norm,
-            common_norm=common_norm,
-            kde_kws=kde_kws,
-            inner_kws=inner_kws,
-            plot_kws=plot_kws,
-        )
-
-    elif kind == "boxen":
+        linecolor = p._complement_color(plot_kws.pop("linecolor", "auto"), color, p._hue_map)
+        p.plot_violins(width=width, dodge=dodge, gap=gap, split=split, color=color, fill=fill,
+                       linecolor=linecolor, linewidth=linewidth, inner=inner, density_norm=density_norm,
+                       common_norm=common_norm, kde_kws=kde_kws, inner_kws=inner_kws, plot_kws=plot_kws)
 
+    def _plot_boxen(p, dodge, color, kwargs):
         plot_kws = kwargs.copy()
         gap = plot_kws.pop("gap", 0)
         fill = plot_kws.pop("fill", True)
@@ -3027,123 +2970,60 @@ def catplot(
         flier_kws = plot_kws.pop("flier_kws", {})
         line_kws = plot_kws.pop("line_kws", {})
         if "scale" in plot_kws:
-            width_method = p._boxen_scale_backcompat(
-                plot_kws["scale"], width_method
-            )
+            width_method = p._boxen_scale_backcompat(plot_kws["scale"], width_method)
         linecolor = p._complement_color(linecolor, color, p._hue_map)
+        p.plot_boxens(width=width, dodge=dodge, gap=gap, fill=fill, color=color, linecolor=linecolor,
+                      linewidth=linewidth, width_method=width_method, k_depth=k_depth, outlier_prop=outlier_prop,
+                      trust_alpha=trust_alpha, showfliers=showfliers, box_kws=box_kws, flier_kws=flier_kws,
+                      line_kws=line_kws, plot_kws=plot_kws)
 
-        p.plot_boxens(
-            width=width,
-            dodge=dodge,
-            gap=gap,
-            fill=fill,
-            color=color,
-            linecolor=linecolor,
-            linewidth=linewidth,
-            width_method=width_method,
-            k_depth=k_depth,
-            outlier_prop=outlier_prop,
-            trust_alpha=trust_alpha,
-            showfliers=showfliers,
-            box_kws=box_kws,
-            flier_kws=flier_kws,
-            line_kws=line_kws,
-            plot_kws=plot_kws,
-        )
-
-    elif kind == "point":
-
+    def _plot_point(p, dodge, color, kwargs):
         aggregator = agg_cls(estimator, errorbar, n_boot=n_boot, seed=seed)
-
         markers = kwargs.pop("markers", default)
         linestyles = kwargs.pop("linestyles", default)
-
-        # Deprecations to remove in v0.15.0.
-        # TODO Uncomment when removing deprecation backcompat
-        # capsize = kwargs.pop("capsize", 0)
-        # err_kws = normalize_kwargs(kwargs.pop("err_kws", {}), mpl.lines.Line2D)
-        p._point_kwargs_backcompat(
-            kwargs.pop("scale", deprecated),
-            kwargs.pop("join", deprecated),
-            kwargs
-        )
-        err_kws, capsize = p._err_kws_backcompat(
-            normalize_kwargs(kwargs.pop("err_kws", {}), mpl.lines.Line2D),
-            None,
-            errwidth=kwargs.pop("errwidth", deprecated),
-            capsize=kwargs.pop("capsize", 0),
-        )
-
-        p.plot_points(
-            aggregator=aggregator,
-            markers=markers,
-            linestyles=linestyles,
-            dodge=dodge,
-            color=color,
-            capsize=capsize,
-            err_kws=err_kws,
-            plot_kws=kwargs,
-        )
-
-    elif kind == "bar":
-
+        p._point_kwargs_backcompat(kwargs.pop("scale", deprecated), kwargs.pop("join", deprecated), kwargs)
+        err_kws, capsize = p._err_kws_backcompat(normalize_kwargs(kwargs.pop("err_kws", {}), mpl.lines.Line2D),
+                                                 None, errwidth=kwargs.pop("errwidth", deprecated),
+                                                 capsize=kwargs.pop("capsize", 0))
+        p.plot_points(aggregator=aggregator, markers=markers, linestyles=linestyles, dodge=dodge,
+                      color=color, capsize=capsize, err_kws=err_kws, plot_kws=kwargs)
+
+    def _plot_bar(p, dodge, color, kwargs):
         aggregator = agg_cls(estimator, errorbar, n_boot=n_boot, seed=seed)
-
-        err_kws, capsize = p._err_kws_backcompat(
-            normalize_kwargs(kwargs.pop("err_kws", {}), mpl.lines.Line2D),
-            errcolor=kwargs.pop("errcolor", deprecated),
-            errwidth=kwargs.pop("errwidth", deprecated),
-            capsize=kwargs.pop("capsize", 0),
-        )
+        err_kws, capsize = p._err_kws_backcompat(normalize_kwargs(kwargs.pop("err_kws", {}), mpl.lines.Line2D),
+                                                 errcolor=kwargs.pop("errcolor", deprecated),
+                                                 errwidth=kwargs.pop("errwidth", deprecated),
+                                                 capsize=kwargs.pop("capsize", 0))
         gap = kwargs.pop("gap", 0)
         fill = kwargs.pop("fill", True)
+        p.plot_bars(aggregator=aggregator, dodge=dodge, width=width, gap=gap, color=color,
+                    fill=fill, capsize=capsize, err_kws=err_kws, plot_kws=kwargs)
 
-        p.plot_bars(
-            aggregator=aggregator,
-            dodge=dodge,
-            width=width,
-            gap=gap,
-            color=color,
-            fill=fill,
-            capsize=capsize,
-            err_kws=err_kws,
-            plot_kws=kwargs,
-        )
-
-    elif kind == "count":
-
+    def _plot_count(p, dodge, color, kwargs):
         aggregator = EstimateAggregator("sum", errorbar=None)
-
         count_axis = {"x": "y", "y": "x"}[p.orient]
         p.plot_data[count_axis] = 1
-
         stat_options = ["count", "percent", "probability", "proportion"]
         stat = _check_argument("stat", stat_options, kwargs.pop("stat", "count"))
         p.variables[count_axis] = stat
         if stat != "count":
             denom = 100 if stat == "percent" else 1
             p.plot_data[count_axis] /= len(p.plot_data) / denom
-
         gap = kwargs.pop("gap", 0)
         fill = kwargs.pop("fill", True)
+        p.plot_bars(aggregator=aggregator, dodge=dodge, width=width, gap=gap, color=color,
+                    fill=fill, capsize=0, err_kws={}, plot_kws=kwargs)
 
-        p.plot_bars(
-            aggregator=aggregator,
-            dodge=dodge,
-            width=width,
-            gap=gap,
-            color=color,
-            fill=fill,
-            capsize=0,
-            err_kws={},
-            plot_kws=kwargs,
-        )
+    dispatch = {
+        "strip": _plot_strip, "swarm": _plot_swarm, "box": _plot_box,
+        "violin": _plot_violin, "boxen": _plot_boxen, "point": _plot_point,
+        "bar": _plot_bar, "count": _plot_count
+    }
 
+    if kind in dispatch:
+        dispatch[kind](p, dodge, color, kwargs)
     else:
-        msg = (
-            f"Invalid `kind`: {kind!r}. Options are 'strip', 'swarm', "
-            "'box', 'boxen', 'violin', 'bar', 'count', and 'point'."
-        )
+        msg = (f"Invalid `kind`: {kind!r}. Options are {list(dispatch.keys())}.")
         raise ValueError(msg)
 
     for ax in g.axes.flat:

```
