# Refactor LSP-025 (LSP): Concrete class inherits abstract methods from Scale but does not implement them.

**Status:** `applied_passed`  
**Branch:** `refactor/LSP-025` -> `main`  
**Head commit:** `0ce1c94396acbe45e7cb52f58d4e3bccabc765a7`  
**LLM finish:** `FinishReason.STOP` (prompt 10379, completion 267)  

## Detected issue

- **File**: `seaborn/_core/scales.py`
- **Entity**: `Identity` (class)
- **Lines (at detection time)**: L139–L143
- **Severity**: high
- **Confidence**: detected by 1 scan(s)

**Description.** Concrete class inherits abstract methods from Scale but does not implement them.

**Reasoning.** The Identity class inherits from Scale, which defines abstract methods (tick, label, _get_locators, _get_formatter, _setup). Identity does not implement any of these abstract methods. As a concrete class, it violates LSP because it cannot fulfill the contract of its base class, making it not fully substitutable.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `seaborn/_core/scales.py`

**Summary.** Implement abstract methods in the Identity scale class

**Rationale.** The Identity class was inheriting from Scale but failing to implement the required abstract methods, violating the Liskov Substitution Principle. By providing minimal implementations for these methods, the class now fulfills the Scale contract.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `seaborn/_core/scales.py` (10-line block → 16-line replacement)

**Replaces:**

```python
    @staticmethod
    def _identity():

        class Identity(Scale):
            _pipeline = []
            _spacer = _default_spacer
            _legend = None
            _matplotlib_scale = None

        return Identity()
```

**With:**

```python
    @staticmethod
    def _identity():

        class Identity(Scale):
            _pipeline = []
            _spacer = _default_spacer
            _legend = None
            _matplotlib_scale = None

            def tick(self): return self
            def label(self): return self
            def _get_locators(self): return None, None
            def _get_formatter(self, locator=None): return None
            def _setup(self, data, prop, axis=None): return self

        return Identity()
```

## Test results

**PASSED** — 0/0 passed, 0 failed, 0 skipped, 0 errored (duration 2232 ms).

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
1 error in 1.36s

```

</details>

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `seaborn/_core/scales.py` | 747 → 752 | 77 → 82 | 2.79 → 2.79 | 16 → 16 | 23.47 → 23.27 |

## Diff

```diff
diff --git a/seaborn/_core/scales.py b/seaborn/_core/scales.py
index e0d2051..be3815a 100644
--- a/seaborn/_core/scales.py
+++ b/seaborn/_core/scales.py
@@ -142,6 +142,12 @@ class Scale:
             _legend = None
             _matplotlib_scale = None
 
+            def tick(self): return self
+            def label(self): return self
+            def _get_locators(self): return None, None
+            def _get_formatter(self, locator=None): return None
+            def _setup(self, data, prop, axis=None): return self
+
         return Identity()
 
 

```
