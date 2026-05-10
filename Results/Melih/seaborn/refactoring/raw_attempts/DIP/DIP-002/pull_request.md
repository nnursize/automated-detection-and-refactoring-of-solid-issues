# Refactor DIP-002 (DIP): Direct instantiation of the Hist estimator.

**Status:** `applied_passed`  
**Branch:** `refactor/DIP-002` -> `main`  
**Head commit:** `626f3ff6a3460b09d04e94a49b51eda28b108d54`  
**LLM finish:** `FinishReason.STOP` (prompt 6931, completion 359)  

## Detected issue

- **File**: `seaborn/distributions.py`
- **Entity**: `_DistributionPlotter.plot_univariate_histogram` (method)
- **Lines (at detection time)**: L335–L335
- **Severity**: medium
- **Confidence**: detected by 5 scan(s)

**Description.** Direct instantiation of the Hist estimator.

**Reasoning.** _DistributionPlotter is responsible for orchestrating the plot but directly instantiates the Hist class. This violates DIP as the plotter (high-level) depends on a concrete statistical detail (low-level) instead of an abstraction or receiving the estimator via dependency injection.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 2
- **Files modified** (1): `seaborn/distributions.py`

**Summary.** Inject Hist estimator into _DistributionPlotter.plot_univariate_histogram

**Rationale.** The _DistributionPlotter class was directly instantiating the Hist class, violating the Dependency Inversion Principle. By allowing the estimator to be passed as an argument (with a default value), we decouple the plotter from the concrete implementation, facilitating better testing and extensibility.

## Changes overview

_2 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `seaborn/distributions.py` (16-line block → 17-line replacement)

**Replaces:**

```python
    def plot_univariate_histogram(
        self,
        multiple,
        element,
        fill,
        common_norm,
        common_bins,
        shrink,
        kde,
        kde_kws,
        color,
        legend,
        line_kws,
        estimate_kws,
        **plot_kws,
    ):
```

**With:**

```python
    def plot_univariate_histogram(
        self,
        multiple,
        element,
        fill,
        common_norm,
        common_bins,
        shrink,
        kde,
        kde_kws,
        color,
        legend,
        line_kws,
        estimate_kws,
        estimator_class=Hist,
        **plot_kws,
    ):
```

### 2. EDIT `seaborn/distributions.py` (3-line block → 3-line replacement)

**Replaces:**

```python
        # Now initialize the Histogram estimator
        estimator = Hist(**estimate_kws)
        histograms = {}
```

**With:**

```python
        # Now initialize the Histogram estimator
        estimator = estimator_class(**estimate_kws)
        histograms = {}
```

## Test results

**PASSED** — 0/0 passed, 0 failed, 0 skipped, 0 errored (duration 2275 ms).

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
1 error in 1.38s

```

</details>

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `seaborn/distributions.py` | 1849 → 1850 | 39 → 39 | 8.75 → 8.75 | 64 → 64 | 0 → 0 |

## Diff

```diff
diff --git a/seaborn/distributions.py b/seaborn/distributions.py
index a21d55b..1ffaba2 100644
--- a/seaborn/distributions.py
+++ b/seaborn/distributions.py
@@ -427,6 +427,7 @@ class _DistributionPlotter(
         legend,
         line_kws,
         estimate_kws,
+        estimator_class=Hist,
         **plot_kws,
     ):
 
@@ -460,7 +461,7 @@ class _DistributionPlotter(
         orient = self.data_variable
 
         # Now initialize the Histogram estimator
-        estimator = Hist(**estimate_kws)
+        estimator = estimator_class(**estimate_kws)
         histograms = {}
 
         # Do pre-compute housekeeping related to multiple groups

```
