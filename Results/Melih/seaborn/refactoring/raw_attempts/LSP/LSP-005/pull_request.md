# Refactor LSP-005 (LSP): Subclass fails to implement the abstract contract of the base class.

**Status:** `applied_passed`  
**Branch:** `refactor/LSP-005` -> `main`  
**Head commit:** `4abd85ca6b4ef4a98218b8f06a4ca1d58663d66f`  
**LLM finish:** `FinishReason.STOP` (prompt 10823, completion 374)  

## Detected issue

- **File**: `seaborn/_core/scales.py`
- **Entity**: `Scale._identity.<locals>.Identity` (class)
- **Lines (at detection time)**: L132–L141
- **Severity**: high
- **Confidence**: detected by 1 scan(s)

**Description.** Subclass fails to implement the abstract contract of the base class.

**Reasoning.** The base class 'Scale' defines an interface where methods like '_setup', 'tick', and 'label' are expected to be implemented by subtypes (they raise NotImplementedError in the base). The 'Identity' subclass, created within the '_identity' static method, inherits from 'Scale' but does not implement these methods. Consequently, an 'Identity' instance cannot be substituted for a 'Scale' instance in any context that requires setting up the scale or configuring ticks/labels, leading to runtime crashes.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `seaborn/_core/scales.py`

**Summary.** Implement missing abstract methods in Identity scale to satisfy Liskov Substitution Principle

**Rationale.** The Identity subclass of Scale was missing the 'tick', 'label', '_get_locators', and '_get_formatter' methods required by the contract established by TickLabelScale (or expected by the system). By adding these methods, the Identity scale can now be used in contexts where these methods are invoked, preventing runtime errors.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `seaborn/_core/scales.py` (16-line block → 28-line replacement)

**Replaces:**

```python
    @staticmethod
    def _identity():

        class Identity(Scale):
            _pipeline = []
            _spacer = _default_spacer
            _legend = None
            _matplotlib_scale = None

            def _setup(self, data, prop, axis=None):
                return self

            def _finalize(self, p, axis):
                pass

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

            def _setup(self, data, prop, axis=None):
                return self

            def _finalize(self, p, axis):
                pass

            def tick(self, locator=None):
                return self

            def label(self, formatter=None):
                return self

            def _get_locators(self, **kwargs):
                return None, None

            def _get_formatter(self, locator=None, **kwargs):
                return None

        return Identity()
```

## Test results

**PASSED** — 0/0 passed, 0 failed, 0 skipped, 0 errored (duration 2219 ms).

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
1 error in 1.36s

```

</details>

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `seaborn/_core/scales.py` | 775 → 783 | 87 → 91 | 2.57 → 2.57 | 16 → 16 | 21.88 → 21.68 |

## Diff

```diff
diff --git a/seaborn/_core/scales.py b/seaborn/_core/scales.py
index dd15623..82e56d5 100644
--- a/seaborn/_core/scales.py
+++ b/seaborn/_core/scales.py
@@ -120,6 +120,18 @@ class Scale:
             def _finalize(self, p, axis):
                 pass
 
+            def tick(self, locator=None):
+                return self
+
+            def label(self, formatter=None):
+                return self
+
+            def _get_locators(self, **kwargs):
+                return None, None
+
+            def _get_formatter(self, locator=None, **kwargs):
+                return None
+
         return Identity()
 
 

```
