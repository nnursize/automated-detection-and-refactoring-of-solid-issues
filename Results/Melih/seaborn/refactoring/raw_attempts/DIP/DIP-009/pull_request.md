# Refactor DIP-009 (DIP): 'FacetGrid' directly interacts with Matplotlib's global state and concrete fi...

**Status:** `applied_passed`  
**Branch:** `refactor/DIP-009` -> `main`  
**Head commit:** `71477eccde99ba3d425044329639b974f09a7568`  
**LLM finish:** `FinishReason.STOP` (prompt 5324, completion 494)  

## Detected issue

- **File**: `seaborn/axisgrid.py`
- **Entity**: `FacetGrid.__init__` (class)
- **Lines (at detection time)**: L301–L301
- **Severity**: medium
- **Confidence**: detected by 3 scan(s)

**Description.** 'FacetGrid' directly interacts with Matplotlib's global state and concrete figure/subplot creation functions.

**Reasoning.** The `FacetGrid` class directly calls `plt.figure` and `fig.subplots` for figure and subplot creation. While Matplotlib itself is a dependency, `FacetGrid` could abstract the creation of its figure and axes, e.g., by receiving a figure factory or an axes manager through its constructor. This direct coupling to Matplotlib's concrete API and global state reduces flexibility and makes it harder to swap out the underlying plotting backend or mock during testing.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 2
- **Files modified** (1): `seaborn/axisgrid.py`

**Summary.** Inject figure creation into FacetGrid to decouple from matplotlib.pyplot

**Rationale.** By allowing an optional 'figure' argument, FacetGrid can now be initialized with an existing figure or a custom factory, reducing direct dependency on the global matplotlib.pyplot state.

## Changes overview

_2 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `seaborn/axisgrid.py` (11-line block → 11-line replacement)

**Replaces:**

```python
    def __init__(
        self, data, *,
        row=None, col=None, hue=None, col_wrap=None,
        sharex=True, sharey=True, height=3, aspect=1, palette=None,
        row_order=None, col_order=None, hue_order=None, hue_kws=None,
        dropna=False, legend_out=True, despine=True,
        margin_titles=False, xlim=None, ylim=None, subplot_kws=None,
        gridspec_kws=None,
    ):

        super().__init__()
```

**With:**

```python
    def __init__(
        self, data, *,
        row=None, col=None, hue=None, col_wrap=None,
        sharex=True, sharey=True, height=3, aspect=1, palette=None,
        row_order=None, col_order=None, hue_order=None, hue_kws=None,
        dropna=False, legend_out=True, despine=True,
        margin_titles=False, xlim=None, ylim=None, subplot_kws=None,
        gridspec_kws=None, figure=None,
    ):

        super().__init__()
```

### 2. EDIT `seaborn/axisgrid.py` (6-line block → 9-line replacement)

**Replaces:**

```python
        # --- Initialize the subplot grid

        with _disable_autolayout():
            fig = plt.figure(figsize=figsize)

        if col_wrap is None:
```

**With:**

```python
        # --- Initialize the subplot grid

        if figure is None:
            with _disable_autolayout():
                fig = plt.figure(figsize=figsize)
        else:
            fig = figure

        if col_wrap is None:
```

## Test results

**PASSED** — 0/0 passed, 0 failed, 0 skipped, 0 errored (duration 2223 ms).

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
1 error in 1.35s

```

</details>

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `seaborn/axisgrid.py` | 1827 → 1830 | 59 → 59 | 6.13 → 6.14 | 34 → 35 | 0 → 0 |

## Diff

```diff
diff --git a/seaborn/axisgrid.py b/seaborn/axisgrid.py
index 17d333b..4958ed0 100644
--- a/seaborn/axisgrid.py
+++ b/seaborn/axisgrid.py
@@ -375,7 +375,7 @@ class FacetGrid(Grid):
         row_order=None, col_order=None, hue_order=None, hue_kws=None,
         dropna=False, legend_out=True, despine=True,
         margin_titles=False, xlim=None, ylim=None, subplot_kws=None,
-        gridspec_kws=None,
+        gridspec_kws=None, figure=None,
     ):
 
         super().__init__()
@@ -449,8 +449,11 @@ class FacetGrid(Grid):
 
         # --- Initialize the subplot grid
 
-        with _disable_autolayout():
-            fig = plt.figure(figsize=figsize)
+        if figure is None:
+            with _disable_autolayout():
+                fig = plt.figure(figsize=figsize)
+        else:
+            fig = figure
 
         if col_wrap is None:
 

```
