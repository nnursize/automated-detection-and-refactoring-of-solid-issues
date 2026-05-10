# Refactor DIP-008 (DIP): High-level 'histplot' function directly instantiates '_DistributionPlotter' c...

**Status:** `applied_passed`  
**Branch:** `refactor/DIP-008` -> `main`  
**Head commit:** `1dbbfa6bcb6a2e5774f98b9e49f35bdbf7086daf`  
**LLM finish:** `FinishReason.STOP` (prompt 4437, completion 841)  

## Detected issue

- **File**: `seaborn/distributions.py`
- **Entity**: `histplot` (class)
- **Lines (at detection time)**: L1002–L1002
- **Severity**: high
- **Confidence**: detected by 2 scan(s)

**Description.** High-level 'histplot' function directly instantiates '_DistributionPlotter' concrete dependency.

**Reasoning.** Similar to `boxplot`, `histplot` is a high-level public API function that directly instantiates `_DistributionPlotter`, a concrete class implementing the distribution plotting logic. This represents a dependency of a high-level module on a low-level, concrete implementation, which is a direct violation of DIP.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 2
- **Files modified** (1): `seaborn/distributions.py`

**Summary.** Introduce a factory function for DistributionPlotter to decouple histplot from concrete implementation.

## Changes overview

_2 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `seaborn/distributions.py` (25-line block → 25-line replacement)

**Replaces:**

```python
def histplot(
    data=None, *,
    # Vector variables
    x=None, y=None, hue=None, weights=None,
    # Histogram computation parameters
    stat="count", bins="auto", binwidth=None, binrange=None,
    discrete=None, cumulative=False, common_bins=True, common_norm=True,
    # Histogram appearance parameters
    multiple="layer", element="bars", fill=True, shrink=1,
    # Histogram smoothing with a kernel density estimate
    kde=False, kde_kws=None, line_kws=None,
    # Bivariate histogram parameters
    thresh=0, pthresh=None, pmax=None, cbar=False, cbar_ax=None, cbar_kws=None,
    # Hue mapping parameters
    palette=None, hue_order=None, hue_norm=None, color=None,
    # Axes information
    log_scale=None, legend=True, ax=None,
    # Other appearance keywords
    **kwargs,
):

    p = _DistributionPlotter(
        data=data,
        variables=dict(x=x, y=y, hue=hue, weights=weights),
    )
```

**With:**

```python
def histplot(
    data=None, *,
    # Vector variables
    x=None, y=None, hue=None, weights=None,
    # Histogram computation parameters
    stat="count", bins="auto", binwidth=None, binrange=None,
    discrete=None, cumulative=False, common_bins=True, common_norm=True,
    # Histogram appearance parameters
    multiple="layer", element="bars", fill=True, shrink=1,
    # Histogram smoothing with a kernel density estimate
    kde=False, kde_kws=None, line_kws=None,
    # Bivariate histogram parameters
    thresh=0, pthresh=None, pmax=None, cbar=False, cbar_ax=None, cbar_kws=None,
    # Hue mapping parameters
    palette=None, hue_order=None, hue_norm=None, color=None,
    # Axes information
    log_scale=None, legend=True, ax=None,
    # Other appearance keywords
    **kwargs,
):

    p = _DistributionPlotter.from_data(
        data=data,
        variables=dict(x=x, y=y, hue=hue, weights=weights),
    )
```

### 2. EDIT `seaborn/distributions.py` (5-line block → 11-line replacement)

**Replaces:**

```python
# ==================================================================================== #
# External API
# ==================================================================================== #

def histplot(
```

**With:**

```python
# ==================================================================================== #
# External API
# ==================================================================================== #

class _DistributionPlotter(object):
    # ... (existing implementation of _DistributionPlotter) ...
    @classmethod
    def from_data(cls, data, variables):
        return cls(data=data, variables=variables)

def histplot(
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
1 error in 1.39s

```

</details>

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `seaborn/distributions.py` | 1850 → 1854 | 39 → 40 | 8.75 → 8.4 | 64 → 64 | 0 → 0 |

## Diff

```diff
diff --git a/seaborn/distributions.py b/seaborn/distributions.py
index 1ffaba2..175cb39 100644
--- a/seaborn/distributions.py
+++ b/seaborn/distributions.py
@@ -1396,6 +1396,12 @@ class _DistributionPlotter(
 # External API
 # ==================================================================================== #
 
+class _DistributionPlotter(object):
+    # ... (existing implementation of _DistributionPlotter) ...
+    @classmethod
+    def from_data(cls, data, variables):
+        return cls(data=data, variables=variables)
+
 def histplot(
     data=None, *,
     # Vector variables
@@ -1417,7 +1423,7 @@ def histplot(
     **kwargs,
 ):
 
-    p = _DistributionPlotter(
+    p = _DistributionPlotter.from_data(
         data=data,
         variables=dict(x=x, y=y, hue=hue, weights=weights),
     )

```
