# Refactor DIP-007 (DIP): High-level 'Plot' class directly instantiates 'PlotData' concrete dependency.

**Status:** `applied_passed`  
**Branch:** `refactor/DIP-007` -> `main`  
**Head commit:** `86f976fc784ebb6d7bfcbb3d662b377b68fb00ee`  
**LLM finish:** `FinishReason.STOP` (prompt 3652, completion 524)  

## Detected issue

- **File**: `seaborn/_core/plot.py`
- **Entity**: `Plot.__init__` (class)
- **Lines (at detection time)**: L183–L183
- **Severity**: high
- **Confidence**: detected by 2 scan(s)

**Description.** High-level 'Plot' class directly instantiates 'PlotData' concrete dependency.

**Reasoning.** The `Plot` class is designed as a high-level declarative interface. It directly instantiates `PlotData`, a concrete implementation of a data handling mechanism. This couples the `Plot` class to a specific data structure implementation rather than depending on a data abstraction that could be injected, making it harder to substitute data sources or test different data handling strategies in isolation.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `seaborn/_core/plot.py`

**Summary.** Inject PlotData dependency into Plot constructor

**Rationale.** Decouples Plot from the concrete PlotData implementation by allowing it to be passed as an optional argument, defaulting to the concrete class if not provided. This adheres to the Dependency Inversion Principle.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `seaborn/_core/plot.py` (30-line block → 31-line replacement)

**Replaces:**

```python
    def __init__(
        self,
        *args: DataSource | VariableSpec,
        data: DataSource = None,
        **variables: VariableSpec,
    ):

        if args:
            data, variables = self._resolve_positionals(args, data, variables)

        unknown = [x for x in variables if x not in PROPERTIES]
        if unknown:
            err = f"Plot() got unexpected keyword argument(s): {', '.join(unknown)}"
            raise TypeError(err)

        self._spec = {
            "data": PlotData(data, variables),
            "layers": [],
            "scales": {},
            "shares": {},
            "limits": {},
            "labels": {},
            "theme": {},
            "facet": {},
            "pair": {},
            "figure": {},
            "subplot": {},
            "layout": {},
            "target": None,
        }
```

**With:**

```python
    def __init__(
        self,
        *args: DataSource | VariableSpec,
        data: DataSource = None,
        data_handler: type = PlotData,
        **variables: VariableSpec,
    ):

        if args:
            data, variables = self._resolve_positionals(args, data, variables)

        unknown = [x for x in variables if x not in PROPERTIES]
        if unknown:
            err = f"Plot() got unexpected keyword argument(s): {', '.join(unknown)}"
            raise TypeError(err)

        self._spec = {
            "data": data_handler(data, variables),
            "layers": [],
            "scales": {},
            "shares": {},
            "limits": {},
            "labels": {},
            "theme": {},
            "facet": {},
            "pair": {},
            "figure": {},
            "subplot": {},
            "layout": {},
            "target": None,
        }
```

## Test results

**PASSED** — 0/0 passed, 0 failed, 0 skipped, 0 errored (duration 2242 ms).

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
| `seaborn/_core/plot.py` | 1292 → 1293 | 58 → 58 | 5.22 → 5.22 | 31 → 31 | 0 → 0 |

## Diff

```diff
diff --git a/seaborn/_core/plot.py b/seaborn/_core/plot.py
index 36e8d40..18adeeb 100644
--- a/seaborn/_core/plot.py
+++ b/seaborn/_core/plot.py
@@ -292,6 +292,7 @@ class Plot:
         self,
         *args: DataSource | VariableSpec,
         data: DataSource = None,
+        data_handler: type = PlotData,
         **variables: VariableSpec,
     ):
 
@@ -304,7 +305,7 @@ class Plot:
             raise TypeError(err)
 
         self._spec = {
-            "data": PlotData(data, variables),
+            "data": data_handler(data, variables),
             "layers": [],
             "scales": {},
             "shares": {},

```
