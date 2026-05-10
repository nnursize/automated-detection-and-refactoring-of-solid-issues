# Refactor ISP-008 (ISP): Class depends on unused legend and tick parameter management methods from its...

**Status:** `applied_passed`  
**Branch:** `refactor/ISP-008` -> `main`  
**Head commit:** `8f9eb9b6ced81174fa9e1c93114df163ba5f9690`  
**LLM finish:** `FinishReason.STOP` (prompt 14025, completion 168)  

## Detected issue

- **File**: `seaborn/matrix.py`
- **Entity**: `ClusterGrid` (class)
- **Lines (at detection time)**: L696–L1143
- **Severity**: high
- **Confidence**: detected by 2 scan(s)

**Description.** Class depends on unused legend and tick parameter management methods from its base interface.

**Reasoning.** The ClusterGrid class inherits from Grid, which provides methods for general legend management (e.g., add_legend, _update_legend_data, _get_palette, legend property) and tick parameter configuration (tick_params). ClusterGrid, being specialized for clustered heatmaps, handles its color processing and legend/colorbar (cbar) logic differently and does not utilize or override these inherited methods in a meaningful way. This forces ClusterGrid to depend on parts of the Grid interface that are not relevant to its specific responsibilities, violating ISP.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `seaborn/matrix.py`

**Summary.** Remove inheritance from Grid in ClusterGrid to satisfy ISP

**Rationale.** ClusterGrid does not use the legend or tick management methods provided by the Grid base class. Removing the inheritance avoids forcing ClusterGrid to depend on an interface it does not use, resolving the ISP violation.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `seaborn/matrix.py` (3-line block → 3-line replacement)

**Replaces:**

```python
class ClusterGrid(Grid):

    def __init__(self, data, pivot_kws=None, z_score=None, standard_scale=None,
```

**With:**

```python
class ClusterGrid:

    def __init__(self, data, pivot_kws=None, z_score=None, standard_scale=None,
```

## Test results

**PASSED** — 0/0 passed, 0 failed, 0 skipped, 0 errored (duration 2225 ms).

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
seaborn\categorical.py:460: in <module>
    class _StripPlotter(_CategoricalPlotter):
seaborn\categorical.py:461: in _StripPlotter
    @register_plot("strips")
     ^^^^^^^^^^^^^
E   NameError: name 'register_plot' is not defined
=========================== short test summary info ===========================
ERROR tests/_core/test_data.py - NameError: name 'register_plot' is not defined
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!
1 error in 1.34s

```

</details>

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `seaborn/matrix.py` | 978 → 978 | 31 → 31 | 5.76 → 5.76 | 22 → 22 | 20.95 → 20.95 |

## Diff

```diff
diff --git a/seaborn/matrix.py b/seaborn/matrix.py
index 4e96132..102a202 100644
--- a/seaborn/matrix.py
+++ b/seaborn/matrix.py
@@ -693,7 +693,7 @@ def dendrogram(
     return plotter.plot(ax=ax, tree_kws=tree_kws)
 
 
-class ClusterGrid(Grid):
+class ClusterGrid:
 
     def __init__(self, data, pivot_kws=None, z_score=None, standard_scale=None,
                  figsize=None, row_colors=None, col_colors=None, mask=None,

```
