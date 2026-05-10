# Refactor DIP-010 (DIP): 'VectorPlotter' directly instantiates 'PlotData' concrete dependency.

**Status:** `applied_passed`  
**Branch:** `refactor/DIP-010` -> `main`  
**Head commit:** `943cdcac73e25d1541cbf030745d787117b6916c`  
**LLM finish:** `FinishReason.STOP` (prompt 3928, completion 578)  

## Detected issue

- **File**: `seaborn/_base.py`
- **Entity**: `VectorPlotter.assign_variables` (method)
- **Lines (at detection time)**: L158–L158
- **Severity**: medium
- **Confidence**: detected by 7 scan(s)

**Description.** 'VectorPlotter' directly instantiates 'PlotData' concrete dependency.

**Reasoning.** The `VectorPlotter` is a base class for many plotting functionalities. Its `assign_variables` method directly instantiates `PlotData`, a concrete data abstraction. This couples a core plotting component to a specific data handling implementation, limiting the ability to inject different data processing strategies or data sources without modifying `VectorPlotter` itself.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 2
- **Files modified** (1): `seaborn/_base.py`

**Summary.** Inject PlotData dependency into VectorPlotter via constructor

**Rationale.** Decouples VectorPlotter from the concrete PlotData implementation by allowing it to be passed as an argument, defaulting to the original implementation to maintain backward compatibility.

## Changes overview

_2 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `seaborn/_base.py` (11-line block → 12-line replacement)

**Replaces:**

```python
    def __init__(self, data=None, variables={}):

        self._var_levels = {}
        # var_ordered is relevant only for categorical axis variables, and may
        # be better handled by an internal axis information object that tracks
        # such information and is set up by the scale_* methods. The analogous
        # information for numeric axes would be information about log scales.
        self._var_ordered = {"x": False, "y": False}  # alt., used DefaultDict
        self.assign_variables(data, variables)

        # TODO Lots of tests assume that these are called to initialize the
```

**With:**

```python
    def __init__(self, data=None, variables={}, plot_data_cls=None):

        self._var_levels = {}
        # var_ordered is relevant only for categorical axis variables, and may
        # be better handled by an internal axis information object that tracks
        # such information and is set up by the scale_* methods. The analogous
        # information for numeric axes would be information about log scales.
        self._var_ordered = {"x": False, "y": False}  # alt., used DefaultDict
        self.plot_data_cls = plot_data_cls or PlotData
        self.assign_variables(data, variables)

        # TODO Lots of tests assume that these are called to initialize the
```

### 2. EDIT `seaborn/_base.py` (8-line block → 8-line replacement)

**Replaces:**

```python
        else:
            # When dealing with long-form input, use the newer PlotData
            # object (internal but introduced for the objects interface)
            # to centralize / standardize data consumption logic.
            self.input_format = "long"
            plot_data = PlotData(data, variables)
            frame = plot_data.frame
            names = plot_data.names
```

**With:**

```python
        else:
            # When dealing with long-form input, use the newer PlotData
            # object (internal but introduced for the objects interface)
            # to centralize / standardize data consumption logic.
            self.input_format = "long"
            plot_data = self.plot_data_cls(data, variables)
            frame = plot_data.frame
            names = plot_data.names
```

## Test results

**PASSED** — 0/0 passed, 0 failed, 0 skipped, 0 errored (duration 2603 ms).

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
1 error in 1.54s

```

</details>

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `seaborn/_base.py` | 1147 → 1148 | 47 → 47 | 6.76 → 6.78 | 28 → 28 | 0 → 0 |

## Diff

```diff
diff --git a/seaborn/_base.py b/seaborn/_base.py
index 0d9f010..93ee868 100644
--- a/seaborn/_base.py
+++ b/seaborn/_base.py
@@ -623,7 +623,7 @@ class VectorPlotter:
 
     _default_size_range = 1, 2  # Unused but needed in tests, ugh
 
-    def __init__(self, data=None, variables={}):
+    def __init__(self, data=None, variables={}, plot_data_cls=None):
 
         self._var_levels = {}
         # var_ordered is relevant only for categorical axis variables, and may
@@ -631,6 +631,7 @@ class VectorPlotter:
         # such information and is set up by the scale_* methods. The analogous
         # information for numeric axes would be information about log scales.
         self._var_ordered = {"x": False, "y": False}  # alt., used DefaultDict
+        self.plot_data_cls = plot_data_cls or PlotData
         self.assign_variables(data, variables)
 
         # TODO Lots of tests assume that these are called to initialize the
@@ -676,7 +677,7 @@ class VectorPlotter:
             # object (internal but introduced for the objects interface)
             # to centralize / standardize data consumption logic.
             self.input_format = "long"
-            plot_data = PlotData(data, variables)
+            plot_data = self.plot_data_cls(data, variables)
             frame = plot_data.frame
             names = plot_data.names
 

```
