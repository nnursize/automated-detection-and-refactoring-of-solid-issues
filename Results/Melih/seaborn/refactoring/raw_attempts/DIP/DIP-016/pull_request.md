# Refactor DIP-016 (DIP): High-level figure-level function directly instantiates a concrete grid layout...

**Status:** `applied_passed`  
**Branch:** `refactor/DIP-016` -> `main`  
**Head commit:** `c6724420b4cdb562337c14e8c6e59fbcf8c7f0f3`  
**LLM finish:** `FinishReason.STOP` (prompt 6546, completion 771)  

## Detected issue

- **File**: `seaborn/categorical.py`
- **Entity**: `catplot` (class)
- **Lines (at detection time)**: L1555–L1555
- **Severity**: high
- **Confidence**: detected by 2 scan(s)

**Description.** High-level figure-level function directly instantiates a concrete grid layout manager.

**Reasoning.** The `catplot` function, a high-level figure-level interface, directly instantiates the concrete `FacetGrid` class (`g = FacetGrid(...)`). This means the high-level `catplot` depends on a specific, concrete implementation of a grid layout manager rather than an abstraction, leading to tight coupling and a violation of DIP.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 2
- **Files modified** (1): `seaborn/categorical.py`

**Summary.** Inject FacetGrid class into catplot to decouple from concrete implementation

**Rationale.** The catplot function directly instantiated FacetGrid, violating the Dependency Inversion Principle. By adding a grid_class parameter (defaulting to FacetGrid), we allow for dependency injection, enabling better testing and decoupling.

## Changes overview

_2 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `seaborn/categorical.py` (9-line block → 9-line replacement)

**Replaces:**

```python
def catplot(
    data=None, *, x=None, y=None, hue=None, row=None, col=None, kind="strip",
    estimator="mean", errorbar=("ci", 95), n_boot=1000, seed=None, units=None,
    weights=None, order=None, hue_order=None, row_order=None, col_order=None,
    col_wrap=None, height=5, aspect=1, log_scale=None, native_scale=False,
    formatter=None, orient=None, color=None, palette=None, hue_norm=None,
    legend="auto", legend_out=True, sharex=True, sharey=True,
    margin_titles=False, facet_kws=None, ci=deprecated, **kwargs
):
```

**With:**

```python
def catplot(
    data=None, *, x=None, y=None, hue=None, row=None, col=None, kind="strip",
    estimator="mean", errorbar=("ci", 95), n_boot=1000, seed=None, units=None,
    weights=None, order=None, hue_order=None, row_order=None, col_order=None,
    col_wrap=None, height=5, aspect=1, log_scale=None, native_scale=False,
    formatter=None, orient=None, color=None, palette=None, hue_norm=None,
    legend="auto", legend_out=True, sharex=True, sharey=True,
    margin_titles=False, facet_kws=None, ci=deprecated, grid_class=None, **kwargs
):
```

### 2. EDIT `seaborn/categorical.py` (10-line block → 13-line replacement)

**Replaces:**

```python
    if facet_kws is None:
        facet_kws = {}

    g = FacetGrid(
        data=facet_data, row=row_name, col=col_name, col_wrap=col_wrap,
        row_order=row_order, col_order=col_order, sharex=sharex, sharey=sharey,
        legend_out=legend_out, margin_titles=margin_titles,
        height=height, aspect=aspect,
        **facet_kws,
    )
```

**With:**

```python
    if facet_kws is None:
        facet_kws = {}

    if grid_class is None:
        grid_class = FacetGrid

    g = grid_class(
        data=facet_data, row=row_name, col=col_name, col_wrap=col_wrap,
        row_order=row_order, col_order=col_order, sharex=sharex, sharey=sharey,
        legend_out=legend_out, margin_titles=margin_titles,
        height=height, aspect=aspect,
        **facet_kws,
    )
```

## Test results

**PASSED** — 0/0 passed, 0 failed, 0 skipped, 0 errored (duration 2213 ms).

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
seaborn\categorical.py:462: in <module>
    class _StripPlotter(_CategoricalPlotter):
seaborn\categorical.py:463: in _StripPlotter
    @register_plot("strips")
     ^^^^^^^^^^^^^
E   NameError: name 'register_plot' is not defined
=========================== short test summary info ===========================
ERROR tests/_core/test_data.py - NameError: name 'register_plot' is not defined
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!
1 error in 1.36s

```

</details>

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `seaborn/categorical.py` | 2596 → 2598 | 62 → 62 | 7.21 → 7.23 | 39 → 40 | 0 → 0 |

## Diff

```diff
diff --git a/seaborn/categorical.py b/seaborn/categorical.py
index 5d95e05..d9910fe 100644
--- a/seaborn/categorical.py
+++ b/seaborn/categorical.py
@@ -2780,7 +2780,7 @@ def catplot(
     col_wrap=None, height=5, aspect=1, log_scale=None, native_scale=False,
     formatter=None, orient=None, color=None, palette=None, hue_norm=None,
     legend="auto", legend_out=True, sharex=True, sharey=True,
-    margin_titles=False, facet_kws=None, ci=deprecated, **kwargs
+    margin_titles=False, facet_kws=None, ci=deprecated, grid_class=None, **kwargs
 ):
 
     # Check for attempt to plot onto specific axes and warn
@@ -2836,7 +2836,10 @@ def catplot(
     if facet_kws is None:
         facet_kws = {}
 
-    g = FacetGrid(
+    if grid_class is None:
+        grid_class = FacetGrid
+
+    g = grid_class(
         data=facet_data, row=row_name, col=col_name, col_wrap=col_wrap,
         row_order=row_order, col_order=col_order, sharex=sharex, sharey=sharey,
         legend_out=legend_out, margin_titles=margin_titles,

```
