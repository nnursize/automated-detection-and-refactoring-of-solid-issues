# Refactor OCP-017 (OCP): Adding new categorical plot types requires modifying this class by adding new...

**Status:** `applied_passed`  
**Branch:** `refactor/OCP-017` -> `main`  
**Head commit:** `da52b6909eeb2ec1e3b66752c15792b16978b3f8`  
**LLM finish:** `FinishReason.STOP` (prompt 17427, completion 1412)  

## Detected issue

- **File**: `seaborn/categorical.py`
- **Entity**: `_CategoricalPlotter` (class)
- **Lines (at detection time)**: L169–L741
- **Severity**: medium
- **Confidence**: detected by 7 scan(s)

**Description.** Adding new categorical plot types requires modifying this class by adding new plot_X methods.

**Reasoning.** The _CategoricalPlotter class contains distinct methods for each specific plot type (e.g., plot_strips, plot_swarms, plot_boxes). To introduce a new categorical plot, a new method (e.g., plot_newplot) would need to be added to this class. This means the class is open for modification when new behaviors (plot types) are introduced, violating OCP. A more OCP-compliant design might involve a registry or factory pattern where new plot types are registered externally without modifying the base plotter.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 8
- **Files modified** (1): `seaborn/categorical.py`

**Summary.** Refactor _CategoricalPlotter to use a registry for plot types to improve OCP compliance.

**Rationale.** By introducing a registry mechanism, we decouple the plotter class from specific plot implementations, allowing new plot types to be added without modifying the base class.

## Changes overview

_8 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `seaborn/categorical.py` (7-line block → 24-line replacement)

**Replaces:**

```python
    # Note that the plotting methods here aim (in most cases) to produce the
    # exact same artists as the original (pre 0.12) version of the code, so
    # there is some weirdness that might not otherwise be clean or make sense in
    # this context, such as adding empty artists for combinations of variables
    # with no observations

    def plot_strips(
```

**With:**

```python
    # Note that the plotting methods here aim (in most cases) to produce the
    # exact same artists as the original (pre 0.12) version of the code, so
    # there is some weirdness that might not otherwise be clean or make sense in
    # this context, such as adding empty artists for combinations of variables
    # with no observations

    _plot_methods = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._plot_methods = {}

    @classmethod
    def register_plot(cls, name):
        def decorator(func):
            cls._plot_methods[name] = func
            return func
        return decorator

    def plot(self, name, *args, **kwargs):
        return self._plot_methods[name](self, *args, **kwargs)

    @register_plot("strips")
    def plot_strips(
```

### 2. EDIT `seaborn/categorical.py` (7-line block → 7-line replacement)

**Replaces:**

```python
    def plot_strips(
        self,
        jitter,
        dodge,
        color,
        plot_kws,
    ):
```

**With:**

```python
    def plot_strips(
        self,
        jitter,
        dodge,
        color,
        plot_kws,
    ):
```

### 3. EDIT `seaborn/categorical.py` (7-line block → 8-line replacement)

**Replaces:**

```python
    def plot_swarms(
        self,
        dodge,
        color,
        warn_thresh,
        plot_kws,
    ):
```

**With:**

```python
    @register_plot("swarms")
    def plot_swarms(
        self,
        dodge,
        color,
        warn_thresh,
        plot_kws,
    ):
```

### 4. EDIT `seaborn/categorical.py` (13-line block → 14-line replacement)

**Replaces:**

```python
    def plot_boxes(
        self,
        width,
        dodge,
        gap,
        fill,
        whis,
        color,
        linecolor,
        linewidth,
        fliersize,
        plot_kws,  # TODO rename user_kws?
    ):
```

**With:**

```python
    @register_plot("boxes")
    def plot_boxes(
        self,
        width,
        dodge,
        gap,
        fill,
        whis,
        color,
        linecolor,
        linewidth,
        fliersize,
        plot_kws,  # TODO rename user_kws?
    ):
```

### 5. EDIT `seaborn/categorical.py` (19-line block → 20-line replacement)

**Replaces:**

```python
    def plot_boxens(
        self,
        width,
        dodge,
        gap,
        fill,
        color,
        linecolor,
        linewidth,
        width_method,
        k_depth,
        outlier_prop,
        trust_alpha,
        showfliers,
        box_kws,
        flier_kws,
        line_kws,
        plot_kws,
    ):
```

**With:**

```python
    @register_plot("boxens")
    def plot_boxens(
        self,
        width,
        dodge,
        gap,
        fill,
        color,
        linecolor,
        linewidth,
        width_method,
        k_depth,
        outlier_prop,
        trust_alpha,
        showfliers,
        box_kws,
        flier_kws,
        line_kws,
        plot_kws,
    ):
```

### 6. EDIT `seaborn/categorical.py` (17-line block → 18-line replacement)

**Replaces:**

```python
    def plot_violins(
        self,
        width,
        dodge,
        gap,
        split,
        color,
        fill,
        linecolor,
        linewidth,
        inner,
        density_norm,
        common_norm,
        kde_kws,
        inner_kws,
        plot_kws,
    ):
```

**With:**

```python
    @register_plot("violins")
    def plot_violins(
        self,
        width,
        dodge,
        gap,
        split,
        color,
        fill,
        linecolor,
        linewidth,
        inner,
        density_norm,
        common_norm,
        kde_kws,
        inner_kws,
        plot_kws,
    ):
```

### 7. EDIT `seaborn/categorical.py` (11-line block → 12-line replacement)

**Replaces:**

```python
    def plot_points(
        self,
        aggregator,
        markers,
        linestyles,
        dodge,
        color,
        capsize,
        err_kws,
        plot_kws,
    ):
```

**With:**

```python
    @register_plot("points")
    def plot_points(
        self,
        aggregator,
        markers,
        linestyles,
        dodge,
        color,
        capsize,
        err_kws,
        plot_kws,
    ):
```

### 8. EDIT `seaborn/categorical.py` (12-line block → 13-line replacement)

**Replaces:**

```python
    def plot_bars(
        self,
        aggregator,
        dodge,
        gap,
        width,
        fill,
        color,
        capsize,
        err_kws,
        plot_kws,
    ):
```

**With:**

```python
    @register_plot("bars")
    def plot_bars(
        self,
        aggregator,
        dodge,
        gap,
        width,
        fill,
        color,
        capsize,
        err_kws,
        plot_kws,
    ):
```

## Test results

**PASSED** — 0/0 passed, 0 failed, 0 skipped, 0 errored (duration 2296 ms).

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
1 error in 1.41s

```

</details>

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `seaborn/categorical.py` | 2717 → 2736 | 53 → 57 | 7.85 → 7.46 | 53 → 53 | 0 → 0 |

## Diff

```diff
diff --git a/seaborn/categorical.py b/seaborn/categorical.py
index 017f0b8..dcbddc2 100644
--- a/seaborn/categorical.py
+++ b/seaborn/categorical.py
@@ -463,6 +463,23 @@ class _CategoricalPlotter(VectorPlotter):
     # this context, such as adding empty artists for combinations of variables
     # with no observations
 
+    _plot_methods = {}
+
+    def __init_subclass__(cls, **kwargs):
+        super().__init_subclass__(**kwargs)
+        cls._plot_methods = {}
+
+    @classmethod
+    def register_plot(cls, name):
+        def decorator(func):
+            cls._plot_methods[name] = func
+            return func
+        return decorator
+
+    def plot(self, name, *args, **kwargs):
+        return self._plot_methods[name](self, *args, **kwargs)
+
+    @register_plot("strips")
     def plot_strips(
         self,
         jitter,
@@ -514,6 +531,7 @@ class _CategoricalPlotter(VectorPlotter):
 
         self._configure_legend(ax, _scatter_legend_artist, common_kws=plot_kws)
 
+    @register_plot("swarms")
     def plot_swarms(
         self,
         dodge,
@@ -588,6 +606,7 @@ class _CategoricalPlotter(VectorPlotter):
         _draw_figure(ax.figure)
         self._configure_legend(ax, _scatter_legend_artist, plot_kws)
 
+    @register_plot("boxes")
     def plot_boxes(
         self,
         width,
@@ -752,6 +771,7 @@ class _CategoricalPlotter(VectorPlotter):
         legend_artist = _get_patch_legend_artist(fill)
         self._configure_legend(ax, legend_artist, boxprops)
 
+    @register_plot("boxens")
     def plot_boxens(
         self,
         width,
@@ -893,6 +913,7 @@ class _CategoricalPlotter(VectorPlotter):
         common_kws = {**box_kws, "linewidth": linewidth, "edgecolor": linecolor}
         self._configure_legend(ax, legend_artist, common_kws)
 
+    @register_plot("violins")
     def plot_violins(
         self,
         width,
@@ -1169,6 +1190,7 @@ class _CategoricalPlotter(VectorPlotter):
         common_kws = {**plot_kws, "linewidth": linewidth, "edgecolor": linecolor}
         self._configure_legend(ax, legend_artist, common_kws)
 
+    @register_plot("points")
     def plot_points(
         self,
         aggregator,
@@ -1249,6 +1271,7 @@ class _CategoricalPlotter(VectorPlotter):
         semantic_kws = {"hue": {"marker": markers, "linestyle": linestyles}}
         self._configure_legend(ax, legend_artist, sub_kws, semantic_kws)
 
+    @register_plot("bars")
     def plot_bars(
         self,
         aggregator,

```
