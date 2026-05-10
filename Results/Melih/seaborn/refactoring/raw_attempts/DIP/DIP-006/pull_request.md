# Refactor DIP-006 (DIP): High-level API function instantiating a concrete plotter.

**Status:** `applied_passed`  
**Branch:** `refactor/DIP-006` -> `main`  
**Head commit:** `a2f681d99ab0fe40df9069b65c343785c681bb96`  
**LLM finish:** `FinishReason.STOP` (prompt 4153, completion 1008)  

## Detected issue

- **File**: `seaborn/categorical.py`
- **Entity**: `boxplot` (class)
- **Lines (at detection time)**: L1125–L1167
- **Severity**: medium
- **Confidence**: detected by 3 scan(s)

**Description.** High-level API function instantiating a concrete plotter.

**Reasoning.** The boxplot function (and other similar functions like violinplot, barplot, etc.) directly instantiates _CategoricalPlotter. While these act as entry points, the tight coupling to concrete plotter classes prevents the injection of alternative plotting engines or the ability to unit test the parameter processing logic in isolation from the plotting implementation.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 2
- **Files modified** (1): `seaborn/categorical.py`

**Summary.** Inject CategoricalPlotter class into boxplot and violinplot functions

**Rationale.** To resolve the DIP violation, I am introducing a default plotter class reference that can be overridden, allowing for dependency injection. This decouples the high-level API functions from the concrete implementation of the plotter.

## Changes overview

_2 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `seaborn/categorical.py` (16-line block → 16-line replacement)

**Replaces:**

```python
def boxplot(
    data=None, *, x=None, y=None, hue=None, order=None, hue_order=None,
    orient=None, color=None, palette=None, saturation=.75, fill=True,
    dodge="auto", width=.8, gap=0, whis=1.5, linecolor="auto", linewidth=None,
    fliersize=None, hue_norm=None, native_scale=False, log_scale=None, formatter=None,
    legend="auto", ax=None, **kwargs
):

    p = _CategoricalPlotter(
        data=data,
        variables=dict(x=x, y=y, hue=hue),
        order=order,
        orient=orient,
        color=color,
        legend=legend,
    )
```

**With:**

```python
def boxplot(
    data=None, *, x=None, y=None, hue=None, order=None, hue_order=None,
    orient=None, color=None, palette=None, saturation=.75, fill=True,
    dodge="auto", width=.8, gap=0, whis=1.5, linecolor="auto", linewidth=None,
    fliersize=None, hue_norm=None, native_scale=False, log_scale=None, formatter=None,
    legend="auto", ax=None, plotter_cls=_CategoricalPlotter, **kwargs
):

    p = plotter_cls(
        data=data,
        variables=dict(x=x, y=y, hue=hue),
        order=order,
        orient=orient,
        color=color,
        legend=legend,
    )
```

### 2. EDIT `seaborn/categorical.py` (19-line block → 19-line replacement)

**Replaces:**

```python
def violinplot(
    data=None, *, x=None, y=None, hue=None, order=None, hue_order=None,
    orient=None, color=None, palette=None, saturation=.75, fill=True,
    inner="box", split=False, width=.8, dodge="auto", gap=0,
    linewidth=None, linecolor="auto", cut=2, gridsize=100,
    bw_method="scott", bw_adjust=1, density_norm="area", common_norm=False,
    hue_norm=None, formatter=None, log_scale=None, native_scale=False,
    legend="auto", scale=deprecated, scale_hue=deprecated, bw=deprecated,
    inner_kws=None, ax=None, **kwargs,
):

    p = _CategoricalPlotter(
        data=data,
        variables=dict(x=x, y=y, hue=hue),
        order=order,
        orient=orient,
        color=color,
        legend=legend,
    )
```

**With:**

```python
def violinplot(
    data=None, *, x=None, y=None, hue=None, order=None, hue_order=None,
    orient=None, color=None, palette=None, saturation=.75, fill=True,
    inner="box", split=False, width=.8, dodge="auto", gap=0,
    linewidth=None, linecolor="auto", cut=2, gridsize=100,
    bw_method="scott", bw_adjust=1, density_norm="area", common_norm=False,
    hue_norm=None, formatter=None, log_scale=None, native_scale=False,
    legend="auto", scale=deprecated, scale_hue=deprecated, bw=deprecated,
    inner_kws=None, ax=None, plotter_cls=_CategoricalPlotter, **kwargs,
):

    p = plotter_cls(
        data=data,
        variables=dict(x=x, y=y, hue=hue),
        order=order,
        orient=orient,
        color=color,
        legend=legend,
    )
```

## Test results

**PASSED** — 0/0 passed, 0 failed, 0 skipped, 0 errored (duration 2438 ms).

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
1 error in 1.49s

```

</details>

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `seaborn/categorical.py` | 2596 → 2596 | 62 → 62 | 7.21 → 7.21 | 39 → 39 | 0 → 0 |

## Diff

```diff
diff --git a/seaborn/categorical.py b/seaborn/categorical.py
index 4a9cae1..5d95e05 100644
--- a/seaborn/categorical.py
+++ b/seaborn/categorical.py
@@ -1614,10 +1614,10 @@ def boxplot(
     orient=None, color=None, palette=None, saturation=.75, fill=True,
     dodge="auto", width=.8, gap=0, whis=1.5, linecolor="auto", linewidth=None,
     fliersize=None, hue_norm=None, native_scale=False, log_scale=None, formatter=None,
-    legend="auto", ax=None, **kwargs
+    legend="auto", ax=None, plotter_cls=_CategoricalPlotter, **kwargs
 ):
 
-    p = _CategoricalPlotter(
+    p = plotter_cls(
         data=data,
         variables=dict(x=x, y=y, hue=hue),
         order=order,
@@ -1742,10 +1742,10 @@ def violinplot(
     bw_method="scott", bw_adjust=1, density_norm="area", common_norm=False,
     hue_norm=None, formatter=None, log_scale=None, native_scale=False,
     legend="auto", scale=deprecated, scale_hue=deprecated, bw=deprecated,
-    inner_kws=None, ax=None, **kwargs,
+    inner_kws=None, ax=None, plotter_cls=_CategoricalPlotter, **kwargs,
 ):
 
-    p = _CategoricalPlotter(
+    p = plotter_cls(
         data=data,
         variables=dict(x=x, y=y, hue=hue),
         order=order,

```
