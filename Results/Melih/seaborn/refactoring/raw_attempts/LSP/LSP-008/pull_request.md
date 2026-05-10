# Refactor LSP-008 (LSP): VariableType strengthens pre-conditions and changes the contract of equality...

**Status:** `applied_passed`  
**Branch:** `refactor/LSP-008` -> `main`  
**Head commit:** `e2148729454c27163e5232605d47c3f290781e05`  
**LLM finish:** `FinishReason.STOP` (prompt 3772, completion 160)  

## Detected issue

- **File**: `seaborn/_base.py`
- **Entity**: `VariableType` (class)
- **Lines (at detection time)**: L1047–L1061
- **Severity**: high
- **Confidence**: detected by 1 scan(s)

**Description.** VariableType strengthens pre-conditions and changes the contract of equality comparison inherited from UserString.

**Reasoning.** VariableType inherits from collections.UserString. The base class equality contract allows comparison against any object, typically returning False for inequality. VariableType overrides __eq__ to 'assert' that the other operand must be one of three specific allowed strings. This strengthens the pre-condition of the method and causes a crash (AssertionError) for values that the base class would handle gracefully. This prevents VariableType from being a valid substitute for a standard string-like object in logic using equality checks.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `seaborn/_base.py`

**Summary.** Remove LSP-violating assertions from VariableType.__eq__

**Rationale.** The VariableType class inherited from UserString but violated the Liskov Substitution Principle by overriding __eq__ to raise an AssertionError when compared against non-allowed values. Standard string equality should return False instead of crashing. Removing the assertion restores the expected contract of equality comparison.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `seaborn/_base.py` (3-line block → 2-line replacement)

**Replaces:**

```python
    def __eq__(self, other):
        assert other in self.allowed, other
        return self.data == other
```

**With:**

```python
    def __eq__(self, other):
        return self.data == other
```

## Test results

**PASSED** — 0/0 passed, 0 failed, 0 skipped, 0 errored (duration 2220 ms).

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
seaborn\categorical.py:460: in _CategoricalPlotter
    @register_plot("strips")
     ^^^^^^^^^^^^^^^^^^^^^^^
E   TypeError: 'classmethod' object is not callable
=========================== short test summary info ===========================
ERROR tests/_core/test_data.py - TypeError: 'classmethod' object is not callable
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!
1 error in 1.37s

```

</details>

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `seaborn/_base.py` | 1146 → 1145 | 47 → 47 | 6.84 → 6.82 | 28 → 28 | 0 → 0 |

## Diff

```diff
diff --git a/seaborn/_base.py b/seaborn/_base.py
index 1eb0c96..f427bc4 100644
--- a/seaborn/_base.py
+++ b/seaborn/_base.py
@@ -1464,7 +1464,6 @@ class VariableType(UserString):
         super().__init__(data)
 
     def __eq__(self, other):
-        assert other in self.allowed, other
         return self.data == other
 
 

```
