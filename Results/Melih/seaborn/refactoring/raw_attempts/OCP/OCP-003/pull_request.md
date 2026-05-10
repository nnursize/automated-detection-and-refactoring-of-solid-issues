# Refactor OCP-003 (OCP): Long if/elif/else chain for dispatching plot kinds.

**Status:** `applied_passed`  
**Branch:** `refactor/OCP-003` -> `main`  
**Head commit:** `3e666832ed27fe2d24707683ab73edea351767eb`  
**LLM finish:** `FinishReason.STOP` (prompt 5332, completion 1541)  

## Detected issue

- **File**: `seaborn/distributions.py`
- **Entity**: `displot` (class)
- **Lines (at detection time)**: L1111–L1200
- **Severity**: high
- **Confidence**: detected by 2 scan(s)

**Description.** Long if/elif/else chain for dispatching plot kinds.

**Reasoning.** The `displot` function uses a long `if/elif/else` chain based on the `kind` string parameter to dispatch to different plotting logic (hist, kde, ecdf). To introduce a new distribution plot type, this function would require modification to add a new `elif` branch, directly violating the Open/Closed Principle. A more OCP-compliant design would involve a registry or a strategy pattern where new plot kinds can be registered without modifying `displot`.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `seaborn/distributions.py`

**Summary.** Refactor displot to use a dispatch dictionary for plot kinds.

**Rationale.** Replaced the if/elif/else chain with a registry dictionary mapping 'kind' strings to handler functions. This allows adding new plot types by updating the registry rather than modifying the core logic of displot, adhering to the Open/Closed Principle.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `seaborn/distributions.py` (79-line block → 54-line replacement)

**Replaces:**

```python
    # --- Draw the plots

    if kind == "hist":

        hist_kws = kwargs.copy()

        # Extract the parameters that will go directly to Histogram
        estimate_defaults = {}
        _assign_default_kwargs(estimate_defaults, Histogram.__init__, histplot)

        estimate_kws = {}
        for key, default_val in estimate_defaults.items():
            estimate_kws[key] = hist_kws.pop(key, default_val)

        # Handle derivative defaults
        if estimate_kws["discrete"] is None:
            estimate_kws["discrete"] = p._default_discrete()

        hist_kws["estimate_kws"] = estimate_kws

        hist_kws.setdefault("color", color)

        if p.univariate:

            _assign_default_kwargs(hist_kws, p.plot_univariate_histogram, histplot)
            p.plot_univariate_histogram(**hist_kws)

        else:

            _assign_default_kwargs(hist_kws, p.plot_bivariate_histogram, histplot)
            p.plot_bivariate_histogram(**hist_kws)

    elif kind == "kde":

        kde_kws = kwargs.copy()

        # Extract the parameters that will go directly to KDE
        estimate_defaults = {}
        _assign_default_kwargs(estimate_defaults, KDE.__init__, kdeplot)

        estimate_kws = {}
        for key, default_val in estimate_defaults.items():
            estimate_kws[key] = kde_kws.pop(key, default_val)

        kde_kws["estimate_kws"] = estimate_kws
        kde_kws["color"] = color

        if p.univariate:

            _assign_default_kwargs(kde_kws, p.plot_univariate_density, kdeplot)
            p.plot_univariate_density(**kde_kws)

        else:

            _assign_default_kwargs(kde_kws, p.plot_bivariate_density, kdeplot)
            p.plot_bivariate_density(**kde_kws)

    elif kind == "ecdf":

        ecdf_kws = kwargs.copy()
... (19 more line(s) truncated)
```

**With:**

```python
    # --- Draw the plots

    def _plot_hist(p, color, **kwargs):
        hist_kws = kwargs.copy()
        estimate_defaults = {}
        _assign_default_kwargs(estimate_defaults, Histogram.__init__, histplot)
        estimate_kws = {k: hist_kws.pop(k, v) for k, v in estimate_defaults.items()}
        if estimate_kws["discrete"] is None:
            estimate_kws["discrete"] = p._default_discrete()
        hist_kws["estimate_kws"] = estimate_kws
        hist_kws.setdefault("color", color)
        if p.univariate:
            _assign_default_kwargs(hist_kws, p.plot_univariate_histogram, histplot)
            p.plot_univariate_histogram(**hist_kws)
        else:
            _assign_default_kwargs(hist_kws, p.plot_bivariate_histogram, histplot)
            p.plot_bivariate_histogram(**hist_kws)

    def _plot_kde(p, color, **kwargs):
        kde_kws = kwargs.copy()
        estimate_defaults = {}
        _assign_default_kwargs(estimate_defaults, KDE.__init__, kdeplot)
        estimate_kws = {k: kde_kws.pop(k, v) for k, v in estimate_defaults.items()}
        kde_kws["estimate_kws"] = estimate_kws
        kde_kws["color"] = color
        if p.univariate:
            _assign_default_kwargs(kde_kws, p.plot_univariate_density, kdeplot)
            p.plot_univariate_density(**kde_kws)
        else:
            _assign_default_kwargs(kde_kws, p.plot_bivariate_density, kdeplot)
            p.plot_bivariate_density(**kde_kws)

    def _plot_ecdf(p, color, **kwargs):
        ecdf_kws = kwargs.copy()
        estimate_kws = {}
        estimate_defaults = {}
        _assign_default_kwargs(estimate_defaults, ECDF.__init__, ecdfplot)
        for k, v in estimate_defaults.items():
            estimate_kws[k] = ecdf_kws.pop(k, v)
        ecdf_kws["estimate_kws"] = estimate_kws
        ecdf_kws["color"] = color
        if p.univariate:
            _assign_default_kwargs(ecdf_kws, p.plot_univariate_ecdf, ecdfplot)
            p.plot_univariate_ecdf(**ecdf_kws)
        else:
            raise NotImplementedError("Bivariate ECDF plots are not implemented")

    plot_dispatch = {
        "hist": _plot_hist,
        "kde": _plot_kde,
        "ecdf": _plot_ecdf,
    }

    plot_dispatch[kind](p, color, **kwargs)
```

## Test results

**PASSED** — 0/0 passed, 0 failed, 0 skipped, 0 errored (duration 2226 ms).

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
| `seaborn/distributions.py` | 1821 → 1823 | 30 → 33 | 11.53 → 11.2 | 64 → 64 | 0 → 0 |

## Diff

```diff
diff --git a/seaborn/distributions.py b/seaborn/distributions.py
index 99ee5df..605636f 100644
--- a/seaborn/distributions.py
+++ b/seaborn/distributions.py
@@ -2169,84 +2169,59 @@ def displot(
 
     # --- Draw the plots
 
-    if kind == "hist":
-
+    def _plot_hist(p, color, **kwargs):
         hist_kws = kwargs.copy()
-
-        # Extract the parameters that will go directly to Histogram
         estimate_defaults = {}
         _assign_default_kwargs(estimate_defaults, Histogram.__init__, histplot)
-
-        estimate_kws = {}
-        for key, default_val in estimate_defaults.items():
-            estimate_kws[key] = hist_kws.pop(key, default_val)
-
-        # Handle derivative defaults
+        estimate_kws = {k: hist_kws.pop(k, v) for k, v in estimate_defaults.items()}
         if estimate_kws["discrete"] is None:
             estimate_kws["discrete"] = p._default_discrete()
-
         hist_kws["estimate_kws"] = estimate_kws
-
         hist_kws.setdefault("color", color)
-
         if p.univariate:
-
             _assign_default_kwargs(hist_kws, p.plot_univariate_histogram, histplot)
             p.plot_univariate_histogram(**hist_kws)
-
         else:
-
             _assign_default_kwargs(hist_kws, p.plot_bivariate_histogram, histplot)
             p.plot_bivariate_histogram(**hist_kws)
 
-    elif kind == "kde":
-
+    def _plot_kde(p, color, **kwargs):
         kde_kws = kwargs.copy()
-
-        # Extract the parameters that will go directly to KDE
         estimate_defaults = {}
         _assign_default_kwargs(estimate_defaults, KDE.__init__, kdeplot)
-
-        estimate_kws = {}
-        for key, default_val in estimate_defaults.items():
-            estimate_kws[key] = kde_kws.pop(key, default_val)
-
+        estimate_kws = {k: kde_kws.pop(k, v) for k, v in estimate_defaults.items()}
         kde_kws["estimate_kws"] = estimate_kws
         kde_kws["color"] = color
-
         if p.univariate:
-
             _assign_default_kwargs(kde_kws, p.plot_univariate_density, kdeplot)
             p.plot_univariate_density(**kde_kws)
-
         else:
-
             _assign_default_kwargs(kde_kws, p.plot_bivariate_density, kdeplot)
             p.plot_bivariate_density(**kde_kws)
 
-    elif kind == "ecdf":
-
+    def _plot_ecdf(p, color, **kwargs):
         ecdf_kws = kwargs.copy()
-
-        # Extract the parameters that will go directly to the estimator
         estimate_kws = {}
         estimate_defaults = {}
         _assign_default_kwargs(estimate_defaults, ECDF.__init__, ecdfplot)
-        for key, default_val in estimate_defaults.items():
-            estimate_kws[key] = ecdf_kws.pop(key, default_val)
-
+        for k, v in estimate_defaults.items():
+            estimate_kws[k] = ecdf_kws.pop(k, v)
         ecdf_kws["estimate_kws"] = estimate_kws
         ecdf_kws["color"] = color
-
         if p.univariate:
-
             _assign_default_kwargs(ecdf_kws, p.plot_univariate_ecdf, ecdfplot)
             p.plot_univariate_ecdf(**ecdf_kws)
-
         else:
-
             raise NotImplementedError("Bivariate ECDF plots are not implemented")
 
+    plot_dispatch = {
+        "hist": _plot_hist,
+        "kde": _plot_kde,
+        "ecdf": _plot_ecdf,
+    }
+
+    plot_dispatch[kind](p, color, **kwargs)
+
     # All plot kinds can include a rug
     if rug:
         # TODO with expand_margins=True, each facet expands margins... annoying!

```
