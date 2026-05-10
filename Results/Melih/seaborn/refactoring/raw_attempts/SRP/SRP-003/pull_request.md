# Refactor SRP-003 (SRP): This figure-level function acts as a 'god function' by dispatching to various...

**Status:** `applied_failed`  
**Branch:** `refactor/SRP-003` -> `main`  
**Head commit:** `11e83875a77e0bb4e9692f7d424a486dbeb007fc`  
**LLM finish:** `FinishReason.STOP` (prompt 7397, completion 5459)  

## Detected issue

- **File**: `seaborn/categorical.py`
- **Entity**: `catplot` (class)
- **Lines (at detection time)**: L1056–L1289
- **Severity**: high
- **Confidence**: detected by 2 scan(s)

**Description.** This figure-level function acts as a 'god function' by dispatching to various plot kinds, handling faceting, managing parameters, and configuring legends.

**Reasoning.** `catplot` orchestrates the creation of an entire figure, including: input validation, handling deprecations, selecting the appropriate plotter class based on `kind`, adapting data for `FacetGrid`, initializing `FacetGrid`, applying semantic mappings, dispatching to specific `plot_X` methods, and managing the legend. Any change to a plot kind's parameters, faceting logic, or legend behavior would require modifying this function, making it highly susceptible to change for many reasons.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 2
- **Files modified** (1): `seaborn/categorical.py`

**Summary.** Refactor catplot to delegate kind-specific plotting logic to a private helper method.

**Rationale.** The catplot function was a 'god function' handling both faceting orchestration and the implementation details of every plot kind. By moving the kind-specific dispatch logic into a dedicated _plot_kind method, we improve readability and adhere to the Single Responsibility Principle by separating the orchestration of the FacetGrid from the specific plotting implementation.

## Changes overview

_2 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `seaborn/categorical.py` (260-line block → 4-line replacement)

**Replaces:**

```python
    if kind in ["strip", "swarm"]:
        kwargs = normalize_kwargs(kwargs, mpl.collections.PathCollection)
        kwargs["edgecolor"] = p._complement_color(
            kwargs.pop("edgecolor", default), color, p._hue_map
        )

    width = kwargs.pop("width", 0.8)
    dodge = kwargs.pop("dodge", False if kind in undodged_kinds else "auto")
    if dodge == "auto":
        dodge = p._dodge_needed()

    if "weight" in p.plot_data:
        if kind not in ["bar", "point"]:
            msg = f"The `weights` parameter has no effect with kind={kind!r}."
            warnings.warn(msg, stacklevel=2)
        agg_cls = WeightedAggregator
    else:
        agg_cls = EstimateAggregator

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
... (200 more line(s) truncated)
```

**With:**

```python
    _plot_kind(
        p, kind, kwargs, color, dodge, width,
        estimator, errorbar, n_boot, seed,
    )
```

### 2. EDIT `seaborn/categorical.py` (4-line block → 264-line replacement)

**Replaces:**

```python
    for ax in g.axes.flat:
        p._adjust_cat_axis(ax, axis=p.orient)

    g.set_axis_labels(p.variables.get("x"), p.variables.get("y"))
```

**With:**

```python
    for ax in g.axes.flat:
        p._adjust_cat_axis(ax, axis=p.orient)

    g.set_axis_labels(p.variables.get("x"), p.variables.get("y"))


def _plot_kind(
    p, kind, kwargs, color, dodge, width,
    estimator, errorbar, n_boot, seed,
):
    """Dispatch to the appropriate plotter method."""
    undodged_kinds = ["strip", "swarm", "point"]

    if kind in ["strip", "swarm"]:
        kwargs = normalize_kwargs(kwargs, mpl.collections.PathCollection)
        kwargs["edgecolor"] = p._complement_color(
            kwargs.pop("edgecolor", default), color, p._hue_map
        )

    if "weight" in p.plot_data:
        if kind not in ["bar", "point"]:
            msg = f"The `weights` parameter has no effect with kind={kind!r}."
            warnings.warn(msg, stacklevel=2)
        agg_cls = WeightedAggregator
    else:
        agg_cls = EstimateAggregator

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
... (204 more line(s) truncated)
```

## Test results

**FAILED** — 1036/1044 passed, 1 failed, 1 skipped, 0 errored (duration 77259 ms).

- New failures introduced by this refactor: **1**
- Pre-existing failures (unrelated to this refactor): **0**

New-failure node IDs (first 25):

  - `tests/test_categorical.py::TestCategoricalPlotterNew::test_axis_labels[catplot-kwargs0]`

Command: `C:\Users\User\Desktop\SDP-Codex\S1-T7-Okeyish\refactor_workspaces\seaborn-master\.venv\Scripts\python.exe -m pytest --tb=short -q --no-header -p no:cacheprovider -x --json-report --json-report-file=C:\Users\User\Desktop\SDP-Codex\S1-T7-Okeyish\refactor_workspaces\seaborn-master\.pytest_report.json`

<details><summary>Output tail</summary>

```
....................................s................................... [  3%]
.................................x............x...x................x.x.. [  6%]
........................................................................ [  9%]
........................................................................ [ 12%]
........................................................................ [ 15%]
........................................................................ [ 18%]
.....................................................................x.. [ 21%]
........................................................................ [ 24%]
........................................................................ [ 27%]
........................................................................ [ 30%]
........................................................................ [ 33%]
........................................................................ [ 36%]
........................................................................ [ 39%]
........................................................................ [ 42%]
...................................F
================================== FAILURES ===================================
_________ TestCategoricalPlotterNew.test_axis_labels[catplot-kwargs0] _________
tests\test_categorical.py:70: in test_axis_labels
    func(data=long_df, **kwargs)
seaborn\categorical.py:2866: in catplot
    p, kind, kwargs, color, dodge, width,
                            ^^^^^
E   NameError: name 'dodge' is not defined
=========================== short test summary info ===========================
FAILED tests/test_categorical.py::TestCategoricalPlotterNew::test_axis_labels[catplot-kwargs0]
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!
1 failed, 1036 passed, 1 skipped, 6 xfailed in 75.27s (0:01:15)

```

</details>

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `seaborn/categorical.py` | 2717 → - | 53 → - | 7.85 → - | 53 → - | 0 → - |

## Diff

```diff
diff --git a/seaborn/categorical.py b/seaborn/categorical.py
index 017f0b8..79d59e8 100644
--- a/seaborn/categorical.py
+++ b/seaborn/categorical.py
@@ -2862,17 +2862,30 @@ def catplot(
         if saturation < 1:
             color = desaturate(color, saturation)
 
+    _plot_kind(
+        p, kind, kwargs, color, dodge, width,
+        estimator, errorbar, n_boot, seed,
+    )
+
+    for ax in g.axes.flat:
+        p._adjust_cat_axis(ax, axis=p.orient)
+
+    g.set_axis_labels(p.variables.get("x"), p.variables.get("y"))
+
+
+def _plot_kind(
+    p, kind, kwargs, color, dodge, width,
+    estimator, errorbar, n_boot, seed,
+):
+    """Dispatch to the appropriate plotter method."""
+    undodged_kinds = ["strip", "swarm", "point"]
+
     if kind in ["strip", "swarm"]:
         kwargs = normalize_kwargs(kwargs, mpl.collections.PathCollection)
         kwargs["edgecolor"] = p._complement_color(
             kwargs.pop("edgecolor", default), color, p._hue_map
         )
 
-    width = kwargs.pop("width", 0.8)
-    dodge = kwargs.pop("dodge", False if kind in undodged_kinds else "auto")
-    if dodge == "auto":
-        dodge = p._dodge_needed()
-
     if "weight" in p.plot_data:
         if kind not in ["bar", "point"]:
             msg = f"The `weights` parameter has no effect with kind={kind!r}."
@@ -3035,10 +3048,6 @@ def catplot(
         markers = kwargs.pop("markers", default)
         linestyles = kwargs.pop("linestyles", default)
 
-        # Deprecations to remove in v0.15.0.
-        # TODO Uncomment when removing deprecation backcompat
-        # capsize = kwargs.pop("capsize", 0)
-        # err_kws = normalize_kwargs(kwargs.pop("err_kws", {}), mpl.lines.Line2D)
         p._point_kwargs_backcompat(
             kwargs.pop("scale", deprecated),
             kwargs.pop("join", deprecated),
@@ -3122,11 +3131,6 @@ def catplot(
             "'box', 'boxen', 'violin', 'bar', 'count', and 'point'."
         )
         raise ValueError(msg)
-
-    for ax in g.axes.flat:
-        p._adjust_cat_axis(ax, axis=p.orient)
-
-    g.set_axis_labels(p.variables.get("x"), p.variables.get("y"))
     g.set_titles()
     g.tight_layout()
 

```
