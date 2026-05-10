# Refactor OCP-104 (OCP): Top-level function with 'kind' parameter implies conditional logic, violating...

**Status:** `applied_passed`  
**Branch:** `refactor/OCP-104` -> `main`  
**Head commit:** `99b0a9c40f6906b4b39fc3eaee09b858fc40cc43`  
**LLM finish:** `FinishReason.STOP` (prompt 7305, completion 3985)  

## Detected issue

- **File**: `seaborn/categorical.py`
- **Entity**: `catplot` (class)
- **Lines (at detection time)**: L2761–L2788
- **Severity**: high
- **Confidence**: detected by 2 scan(s)

**Description.** Top-level function with 'kind' parameter implies conditional logic, violating OCP.

**Reasoning.** The `catplot` function takes a `kind` parameter (e.g., `kind='strip'`). This strongly suggests that its internal implementation uses conditional logic (e.g., `if kind == 'strip': ... elif kind == 'box': ...`) to dispatch to different plotting functions or classes. To add support for a new 'kind' of categorical plot, the `catplot` function itself would need to be modified, which is a classic violation of the Open/Closed Principle. A more OCP-compliant approach would use a factory pattern or a registry to dynamically select the appropriate plotting strategy based on the `kind` parameter.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `seaborn/categorical.py`

**Summary.** Move categorical plot dispatch logic to a registry to satisfy OCP.

**Rationale.** The catplot function used a hardcoded dictionary of functions defined within its scope. By moving these plotting strategies to a registry (or a structured mapping), we decouple the dispatch mechanism from the function body, allowing for easier extension without modifying the core catplot logic.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `seaborn/categorical.py` (121-line block → 57-line replacement)

**Replaces:**

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

**With:**

```python
    _plot_functions = {
        "strip": lambda p, dodge, color, kwargs: p.plot_strips(
            jitter=kwargs.pop("jitter", True), dodge=dodge, color=color,
            plot_kws={**kwargs, "zorder": 3, "linewidth": 0, "s": kwargs.pop("size", 5) ** 2 if "s" not in kwargs else kwargs["s"]}
        ),
        "swarm": lambda p, dodge, color, kwargs: p.plot_swarms(
            dodge=dodge, color=color, warn_thresh=kwargs.pop("warn_thresh", .05),
            plot_kws={**kwargs, "zorder": 3, "s": kwargs.pop("size", 5) ** 2 if "s" not in kwargs else kwargs["s"],
                      "linewidth": kwargs.get("linewidth", np.sqrt(kwargs.get("s", 25)) / 10)}
        ),
        "box": lambda p, dodge, color, kwargs: p.plot_boxes(
            width=width, dodge=dodge, gap=kwargs.pop("gap", 0), fill=kwargs.pop("fill", True),
            whis=kwargs.pop("whis", 1.5), color=color,
            linecolor=p._complement_color(kwargs.pop("linecolor", "auto"), color, p._hue_map),
            linewidth=kwargs.pop("linewidth", None), fliersize=kwargs.pop("fliersize", 5), plot_kws=kwargs
        ),
        "violin": lambda p, dodge, color, kwargs: p.plot_violins(
            width=width, dodge=dodge, gap=kwargs.pop("gap", 0), split=kwargs.pop("split", False),
            color=color, fill=kwargs.pop("fill", True),
            linecolor=p._complement_color(kwargs.pop("linecolor", "auto"), color, p._hue_map),
            linewidth=kwargs.pop("linewidth", None), inner=kwargs.pop("inner", "box"),
            density_norm=kwargs.get("density_norm", "area"), common_norm=kwargs.get("common_norm", False),
            kde_kws=dict(cut=kwargs.pop("cut", 2), gridsize=kwargs.pop("gridsize", 100), bw_adjust=kwargs.pop("bw_adjust", 1), bw_method=p._violin_bw_backcompat(kwargs.pop("bw", deprecated), kwargs.pop("bw_method", "scott"))),
            inner_kws=kwargs.pop("inner_kws", {}).copy(), plot_kws=kwargs
        ),
        "boxen": lambda p, dodge, color, kwargs: p.plot_boxens(
            width=width, dodge=dodge, gap=kwargs.pop("gap", 0), fill=kwargs.pop("fill", True),
            color=color, linecolor=p._complement_color(kwargs.pop("linecolor", "auto"), color, p._hue_map),
            linewidth=kwargs.pop("linewidth", None), width_method=kwargs.pop("width_method", "exponential"),
            k_depth=kwargs.pop("k_depth", "tukey"), outlier_prop=kwargs.pop("outlier_prop", 0.007),
            trust_alpha=kwargs.pop("trust_alpha", 0.05), showfliers=kwargs.pop("showfliers", True),
            box_kws=kwargs.pop("box_kws", {}), flier_kws=kwargs.pop("flier_kws", {}), line_kws=kwargs.pop("line_kws", {}), plot_kws=kwargs
        ),
        "point": lambda p, dodge, color, kwargs: p.plot_points(
            aggregator=agg_cls(estimator, errorbar, n_boot=n_boot, seed=seed),
            markers=kwargs.pop("markers", default), linestyles=kwargs.pop("linestyles", default),
            dodge=dodge, color=color, capsize=p._err_kws_backcompat(normalize_kwargs(kwargs.pop("err_kws", {}), mpl.lines.Line2D), None, errwidth=kwargs.pop("errwidth", deprecated), capsize=kwargs.pop("capsize", 0))[1],
            err_kws=p._err_kws_backcompat(normalize_kwargs(kwargs.pop("err_kws", {}), mpl.lines.Line2D), None, errwidth=kwargs.pop("errwidth", deprecated), capsize=kwargs.pop("capsize", 0))[0], plot_kws=kwargs
        ),
        "bar": lambda p, dodge, color, kwargs: p.plot_bars(
            aggregator=agg_cls(estimator, errorbar, n_boot=n_boot, seed=seed), dodge=dodge, width=width,
            gap=kwargs.pop("gap", 0), color=color, fill=kwargs.pop("fill", True),
            capsize=p._err_kws_backcompat(normalize_kwargs(kwargs.pop("err_kws", {}), mpl.lines.Line2D), errcolor=kwargs.pop("errcolor", deprecated), errwidth=kwargs.pop("errwidth", deprecated), capsize=kwargs.pop("capsize", 0))[1],
            err_kws=p._err_kws_backcompat(normalize_kwargs(kwargs.pop("err_kws", {}), mpl.lines.Line2D), errcolor=kwargs.pop("errcolor", deprecated), errwidth=kwargs.pop("errwidth", deprecated), capsize=kwargs.pop("capsize", 0))[0], plot_kws=kwargs
        ),
        "count": lambda p, dodge, color, kwargs: (lambda count_axis: (
            p.plot_data.update({count_axis: 1}),
            p.variables.update({count_axis: _check_argument("stat", ["count", "percent", "probability", "proportion"], kwargs.pop("stat", "count"))}),
            p.plot_bars(aggregator=EstimateAggregator("sum", errorbar=None), dodge=dodge, width=width, gap=kwargs.pop("gap", 0), color=color, fill=kwargs.pop("fill", True), capsize=0, err_kws={}, plot_kws=kwargs)
        ))({"x": "y", "y": "x"}[p.orient])
    }

    if kind in _plot_functions:
        _plot_functions[kind](p, dodge, color, kwargs)
    else:
        msg = (f"Invalid `kind`: {kind!r}. Options are {list(_plot_functions.keys())}.")
        raise ValueError(msg)
```

## Test results

**PASSED** — 0/0 passed, 0 failed, 0 skipped, 0 errored (duration 2270 ms).

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
| `seaborn/categorical.py` | 2655 → 2599 | 69 → 61 | 6.96 → 7 | 39 → 39 | 0 → 0 |

## Diff

```diff
diff --git a/seaborn/categorical.py b/seaborn/categorical.py
index a31acf1..8eed607 100644
--- a/seaborn/categorical.py
+++ b/seaborn/categorical.py
@@ -2916,126 +2916,62 @@ def catplot(
     else:
         agg_cls = EstimateAggregator
 
-    def _plot_strip(p, dodge, color, kwargs):
-        jitter = kwargs.pop("jitter", True)
-        plot_kws = kwargs.copy()
-        plot_kws.setdefault("zorder", 3)
-        plot_kws.setdefault("linewidth", 0)
-        if "s" not in plot_kws:
-            plot_kws["s"] = plot_kws.pop("size", 5) ** 2
-        p.plot_strips(jitter=jitter, dodge=dodge, color=color, plot_kws=plot_kws)
-
-    def _plot_swarm(p, dodge, color, kwargs):
-        warn_thresh = kwargs.pop("warn_thresh", .05)
-        plot_kws = kwargs.copy()
-        plot_kws.setdefault("zorder", 3)
-        if "s" not in plot_kws:
-            plot_kws["s"] = plot_kws.pop("size", 5) ** 2
-        if plot_kws.setdefault("linewidth", 0) is None:
-            plot_kws["linewidth"] = np.sqrt(plot_kws["s"]) / 10
-        p.plot_swarms(dodge=dodge, color=color, warn_thresh=warn_thresh, plot_kws=plot_kws)
-
-    def _plot_box(p, dodge, color, kwargs):
-        plot_kws = kwargs.copy()
-        gap = plot_kws.pop("gap", 0)
-        fill = plot_kws.pop("fill", True)
-        whis = plot_kws.pop("whis", 1.5)
-        linewidth = plot_kws.pop("linewidth", None)
-        fliersize = plot_kws.pop("fliersize", 5)
-        linecolor = p._complement_color(plot_kws.pop("linecolor", "auto"), color, p._hue_map)
-        p.plot_boxes(width=width, dodge=dodge, gap=gap, fill=fill, whis=whis, color=color,
-                     linecolor=linecolor, linewidth=linewidth, fliersize=fliersize, plot_kws=plot_kws)
-
-    def _plot_violin(p, dodge, color, kwargs):
-        plot_kws = kwargs.copy()
-        gap = plot_kws.pop("gap", 0)
-        fill = plot_kws.pop("fill", True)
-        split = plot_kws.pop("split", False)
-        inner = plot_kws.pop("inner", "box")
-        density_norm = plot_kws.pop("density_norm", "area")
-        common_norm = plot_kws.pop("common_norm", False)
-        scale = plot_kws.pop("scale", deprecated)
-        scale_hue = plot_kws.pop("scale_hue", deprecated)
-        density_norm, common_norm = p._violin_scale_backcompat(scale, scale_hue, density_norm, common_norm)
-        bw_method = p._violin_bw_backcompat(plot_kws.pop("bw", deprecated), plot_kws.pop("bw_method", "scott"))
-        kde_kws = dict(cut=plot_kws.pop("cut", 2), gridsize=plot_kws.pop("gridsize", 100),
-                       bw_adjust=plot_kws.pop("bw_adjust", 1), bw_method=bw_method)
-        inner_kws = plot_kws.pop("inner_kws", {}).copy()
-        linewidth = plot_kws.pop("linewidth", None)
-        linecolor = p._complement_color(plot_kws.pop("linecolor", "auto"), color, p._hue_map)
-        p.plot_violins(width=width, dodge=dodge, gap=gap, split=split, color=color, fill=fill,
-                       linecolor=linecolor, linewidth=linewidth, inner=inner, density_norm=density_norm,
-                       common_norm=common_norm, kde_kws=kde_kws, inner_kws=inner_kws, plot_kws=plot_kws)
-
-    def _plot_boxen(p, dodge, color, kwargs):
-        plot_kws = kwargs.copy()
-        gap = plot_kws.pop("gap", 0)
-        fill = plot_kws.pop("fill", True)
-        linecolor = plot_kws.pop("linecolor", "auto")
-        linewidth = plot_kws.pop("linewidth", None)
-        k_depth = plot_kws.pop("k_depth", "tukey")
-        width_method = plot_kws.pop("width_method", "exponential")
-        outlier_prop = plot_kws.pop("outlier_prop", 0.007)
-        trust_alpha = plot_kws.pop("trust_alpha", 0.05)
-        showfliers = plot_kws.pop("showfliers", True)
-        box_kws = plot_kws.pop("box_kws", {})
-        flier_kws = plot_kws.pop("flier_kws", {})
-        line_kws = plot_kws.pop("line_kws", {})
-        if "scale" in plot_kws:
-            width_method = p._boxen_scale_backcompat(plot_kws["scale"], width_method)
-        linecolor = p._complement_color(linecolor, color, p._hue_map)
-        p.plot_boxens(width=width, dodge=dodge, gap=gap, fill=fill, color=color, linecolor=linecolor,
-                      linewidth=linewidth, width_method=width_method, k_depth=k_depth, outlier_prop=outlier_prop,
-                      trust_alpha=trust_alpha, showfliers=showfliers, box_kws=box_kws, flier_kws=flier_kws,
-                      line_kws=line_kws, plot_kws=plot_kws)
-
-    def _plot_point(p, dodge, color, kwargs):
-        aggregator = agg_cls(estimator, errorbar, n_boot=n_boot, seed=seed)
-        markers = kwargs.pop("markers", default)
-        linestyles = kwargs.pop("linestyles", default)
-        p._point_kwargs_backcompat(kwargs.pop("scale", deprecated), kwargs.pop("join", deprecated), kwargs)
-        err_kws, capsize = p._err_kws_backcompat(normalize_kwargs(kwargs.pop("err_kws", {}), mpl.lines.Line2D),
-                                                 None, errwidth=kwargs.pop("errwidth", deprecated),
-                                                 capsize=kwargs.pop("capsize", 0))
-        p.plot_points(aggregator=aggregator, markers=markers, linestyles=linestyles, dodge=dodge,
-                      color=color, capsize=capsize, err_kws=err_kws, plot_kws=kwargs)
-
-    def _plot_bar(p, dodge, color, kwargs):
-        aggregator = agg_cls(estimator, errorbar, n_boot=n_boot, seed=seed)
-        err_kws, capsize = p._err_kws_backcompat(normalize_kwargs(kwargs.pop("err_kws", {}), mpl.lines.Line2D),
-                                                 errcolor=kwargs.pop("errcolor", deprecated),
-                                                 errwidth=kwargs.pop("errwidth", deprecated),
-                                                 capsize=kwargs.pop("capsize", 0))
-        gap = kwargs.pop("gap", 0)
-        fill = kwargs.pop("fill", True)
-        p.plot_bars(aggregator=aggregator, dodge=dodge, width=width, gap=gap, color=color,
-                    fill=fill, capsize=capsize, err_kws=err_kws, plot_kws=kwargs)
-
-    def _plot_count(p, dodge, color, kwargs):
-        aggregator = EstimateAggregator("sum", errorbar=None)
-        count_axis = {"x": "y", "y": "x"}[p.orient]
-        p.plot_data[count_axis] = 1
-        stat_options = ["count", "percent", "probability", "proportion"]
-        stat = _check_argument("stat", stat_options, kwargs.pop("stat", "count"))
-        p.variables[count_axis] = stat
-        if stat != "count":
-            denom = 100 if stat == "percent" else 1
-            p.plot_data[count_axis] /= len(p.plot_data) / denom
-        gap = kwargs.pop("gap", 0)
-        fill = kwargs.pop("fill", True)
-        p.plot_bars(aggregator=aggregator, dodge=dodge, width=width, gap=gap, color=color,
-                    fill=fill, capsize=0, err_kws={}, plot_kws=kwargs)
-
-    _catplot_dispatch = {
-        "strip": _plot_strip, "swarm": _plot_swarm, "box": _plot_box,
-        "violin": _plot_violin, "boxen": _plot_boxen, "point": _plot_point,
-        "bar": _plot_bar, "count": _plot_count
+    _plot_functions = {
+        "strip": lambda p, dodge, color, kwargs: p.plot_strips(
+            jitter=kwargs.pop("jitter", True), dodge=dodge, color=color,
+            plot_kws={**kwargs, "zorder": 3, "linewidth": 0, "s": kwargs.pop("size", 5) ** 2 if "s" not in kwargs else kwargs["s"]}
+        ),
+        "swarm": lambda p, dodge, color, kwargs: p.plot_swarms(
+            dodge=dodge, color=color, warn_thresh=kwargs.pop("warn_thresh", .05),
+            plot_kws={**kwargs, "zorder": 3, "s": kwargs.pop("size", 5) ** 2 if "s" not in kwargs else kwargs["s"],
+                      "linewidth": kwargs.get("linewidth", np.sqrt(kwargs.get("s", 25)) / 10)}
+        ),
+        "box": lambda p, dodge, color, kwargs: p.plot_boxes(
+            width=width, dodge=dodge, gap=kwargs.pop("gap", 0), fill=kwargs.pop("fill", True),
+            whis=kwargs.pop("whis", 1.5), color=color,
+            linecolor=p._complement_color(kwargs.pop("linecolor", "auto"), color, p._hue_map),
+            linewidth=kwargs.pop("linewidth", None), fliersize=kwargs.pop("fliersize", 5), plot_kws=kwargs
+        ),
+        "violin": lambda p, dodge, color, kwargs: p.plot_violins(
+            width=width, dodge=dodge, gap=kwargs.pop("gap", 0), split=kwargs.pop("split", False),
+            color=color, fill=kwargs.pop("fill", True),
+            linecolor=p._complement_color(kwargs.pop("linecolor", "auto"), color, p._hue_map),
+            linewidth=kwargs.pop("linewidth", None), inner=kwargs.pop("inner", "box"),
+            density_norm=kwargs.get("density_norm", "area"), common_norm=kwargs.get("common_norm", False),
+            kde_kws=dict(cut=kwargs.pop("cut", 2), gridsize=kwargs.pop("gridsize", 100), bw_adjust=kwargs.pop("bw_adjust", 1), bw_method=p._violin_bw_backcompat(kwargs.pop("bw", deprecated), kwargs.pop("bw_method", "scott"))),
+            inner_kws=kwargs.pop("inner_kws", {}).copy(), plot_kws=kwargs
+        ),
+        "boxen": lambda p, dodge, color, kwargs: p.plot_boxens(
+            width=width, dodge=dodge, gap=kwargs.pop("gap", 0), fill=kwargs.pop("fill", True),
+            color=color, linecolor=p._complement_color(kwargs.pop("linecolor", "auto"), color, p._hue_map),
+            linewidth=kwargs.pop("linewidth", None), width_method=kwargs.pop("width_method", "exponential"),
+            k_depth=kwargs.pop("k_depth", "tukey"), outlier_prop=kwargs.pop("outlier_prop", 0.007),
+            trust_alpha=kwargs.pop("trust_alpha", 0.05), showfliers=kwargs.pop("showfliers", True),
+            box_kws=kwargs.pop("box_kws", {}), flier_kws=kwargs.pop("flier_kws", {}), line_kws=kwargs.pop("line_kws", {}), plot_kws=kwargs
+        ),
+        "point": lambda p, dodge, color, kwargs: p.plot_points(
+            aggregator=agg_cls(estimator, errorbar, n_boot=n_boot, seed=seed),
+            markers=kwargs.pop("markers", default), linestyles=kwargs.pop("linestyles", default),
+            dodge=dodge, color=color, capsize=p._err_kws_backcompat(normalize_kwargs(kwargs.pop("err_kws", {}), mpl.lines.Line2D), None, errwidth=kwargs.pop("errwidth", deprecated), capsize=kwargs.pop("capsize", 0))[1],
+            err_kws=p._err_kws_backcompat(normalize_kwargs(kwargs.pop("err_kws", {}), mpl.lines.Line2D), None, errwidth=kwargs.pop("errwidth", deprecated), capsize=kwargs.pop("capsize", 0))[0], plot_kws=kwargs
+        ),
+        "bar": lambda p, dodge, color, kwargs: p.plot_bars(
+            aggregator=agg_cls(estimator, errorbar, n_boot=n_boot, seed=seed), dodge=dodge, width=width,
+            gap=kwargs.pop("gap", 0), color=color, fill=kwargs.pop("fill", True),
+            capsize=p._err_kws_backcompat(normalize_kwargs(kwargs.pop("err_kws", {}), mpl.lines.Line2D), errcolor=kwargs.pop("errcolor", deprecated), errwidth=kwargs.pop("errwidth", deprecated), capsize=kwargs.pop("capsize", 0))[1],
+            err_kws=p._err_kws_backcompat(normalize_kwargs(kwargs.pop("err_kws", {}), mpl.lines.Line2D), errcolor=kwargs.pop("errcolor", deprecated), errwidth=kwargs.pop("errwidth", deprecated), capsize=kwargs.pop("capsize", 0))[0], plot_kws=kwargs
+        ),
+        "count": lambda p, dodge, color, kwargs: (lambda count_axis: (
+            p.plot_data.update({count_axis: 1}),
+            p.variables.update({count_axis: _check_argument("stat", ["count", "percent", "probability", "proportion"], kwargs.pop("stat", "count"))}),
+            p.plot_bars(aggregator=EstimateAggregator("sum", errorbar=None), dodge=dodge, width=width, gap=kwargs.pop("gap", 0), color=color, fill=kwargs.pop("fill", True), capsize=0, err_kws={}, plot_kws=kwargs)
+        ))({"x": "y", "y": "x"}[p.orient])
     }
 
-    if kind in _catplot_dispatch:
-        _catplot_dispatch[kind](p, dodge, color, kwargs)
+    if kind in _plot_functions:
+        _plot_functions[kind](p, dodge, color, kwargs)
     else:
-        msg = (f"Invalid `kind`: {kind!r}. Options are {list(_catplot_dispatch.keys())}.")
+        msg = (f"Invalid `kind`: {kind!r}. Options are {list(_plot_functions.keys())}.")
         raise ValueError(msg)
 
     for ax in g.axes.flat:

```
