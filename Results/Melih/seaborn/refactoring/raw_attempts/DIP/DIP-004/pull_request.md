# Refactor DIP-004 (DIP): Direct instantiation of VectorPlotter dependency.

**Status:** `applied_passed`  
**Branch:** `refactor/DIP-004` -> `main`  
**Head commit:** `85ae1ed39fa7c3f78b09a940a44af15c9fadecb9`  
**LLM finish:** `FinishReason.STOP` (prompt 4557, completion 444)  

## Detected issue

- **File**: `seaborn/axisgrid.py`
- **Entity**: `JointGrid.__init__` (method)
- **Lines (at detection time)**: L1030–L1030
- **Severity**: medium
- **Confidence**: detected by 2 scan(s)

**Description.** Direct instantiation of VectorPlotter dependency.

**Reasoning.** JointGrid, a high-level layout manager, directly instantiates VectorPlotter to handle variable assignment. This prevents the use of alternative data processing strategies and couples the grid layout logic to a specific data-handling implementation.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 2
- **Files modified** (1): `seaborn/axisgrid.py`

**Summary.** Inject VectorPlotter dependency into JointGrid constructor

**Rationale.** By allowing the VectorPlotter class to be passed as an optional argument (defaulting to the existing implementation), we decouple JointGrid from the concrete VectorPlotter class, adhering to the Dependency Inversion Principle.

## Changes overview

_2 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `seaborn/axisgrid.py` (9-line block → 10-line replacement)

**Replaces:**

```python
    def __init__(
        self, data=None, *,
        x=None, y=None, hue=None,
        height=6, ratio=5, space=.2,
        palette=None, hue_order=None, hue_norm=None,
        dropna=False, xlim=None, ylim=None, marginal_ticks=False,
    ):

        # Set up the subplot grid
```

**With:**

```python
    def __init__(
        self, data=None, *,
        x=None, y=None, hue=None,
        height=6, ratio=5, space=.2,
        palette=None, hue_order=None, hue_norm=None,
        dropna=False, xlim=None, ylim=None, marginal_ticks=False,
        plotter_class=None,
    ):

        # Set up the subplot grid
```

### 2. EDIT `seaborn/axisgrid.py` (3-line block → 5-line replacement)

**Replaces:**

```python
        # Process the input variables
        p = VectorPlotter(data=data, variables=dict(x=x, y=y, hue=hue))
        plot_data = p.plot_data.loc[:, p.plot_data.notna().any()]
```

**With:**

```python
        # Process the input variables
        if plotter_class is None:
            plotter_class = VectorPlotter
        p = plotter_class(data=data, variables=dict(x=x, y=y, hue=hue))
        plot_data = p.plot_data.loc[:, p.plot_data.notna().any()]
```

## Test results

**PASSED** — 0/0 passed, 0 failed, 0 skipped, 0 errored (duration 2263 ms).

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
1 error in 1.40s

```

</details>

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `seaborn/axisgrid.py` | 1830 → 1833 | 59 → 59 | 6.14 → 6.16 | 35 → 35 | 0 → 0 |

## Diff

```diff
diff --git a/seaborn/axisgrid.py b/seaborn/axisgrid.py
index 4958ed0..72bb2f0 100644
--- a/seaborn/axisgrid.py
+++ b/seaborn/axisgrid.py
@@ -1693,6 +1693,7 @@ class JointGrid(_BaseGrid):
         height=6, ratio=5, space=.2,
         palette=None, hue_order=None, hue_norm=None,
         dropna=False, xlim=None, ylim=None, marginal_ticks=False,
+        plotter_class=None,
     ):
 
         # Set up the subplot grid
@@ -1728,7 +1729,9 @@ class JointGrid(_BaseGrid):
             ax_marg_y.xaxis.grid(False)
 
         # Process the input variables
-        p = VectorPlotter(data=data, variables=dict(x=x, y=y, hue=hue))
+        if plotter_class is None:
+            plotter_class = VectorPlotter
+        p = plotter_class(data=data, variables=dict(x=x, y=y, hue=hue))
         plot_data = p.plot_data.loc[:, p.plot_data.notna().any()]
 
         # Possibly drop NA

```
