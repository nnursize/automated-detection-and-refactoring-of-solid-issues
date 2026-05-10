# Refactor LSP-023 (LSP): Empty concrete class inherits abstract methods from Scale but does not implem...

**Status:** `applied_passed`  
**Branch:** `refactor/LSP-023` -> `main`  
**Head commit:** `e3c6fbb3995590714fd97e241badeebaff3f3258`  
**LLM finish:** `FinishReason.STOP` (prompt 10461, completion 475)  

## Detected issue

- **File**: `seaborn/_core/scales.py`
- **Entity**: `Ordinal` (class)
- **Lines (at detection time)**: L402–L404
- **Severity**: high
- **Confidence**: detected by 1 scan(s)

**Description.** Empty concrete class inherits abstract methods from Scale but does not implement them.

**Reasoning.** The Ordinal class is an empty class inheriting from Scale, which defines multiple abstract methods (tick, label, _get_locators, _get_formatter, _setup). An empty class in Python is concrete. Therefore, Ordinal is a concrete class that fails to implement the abstract contract of its base class, violating LSP. Instances of Ordinal would not be fully substitutable for Scale.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `seaborn/_core/scales.py`

**Summary.** Implement abstract methods in Ordinal class to satisfy Scale contract

**Rationale.** The Ordinal class was an empty subclass of Scale, which defines abstract methods (tick, label, _get_locators, _get_formatter, _setup). This violated the Liskov Substitution Principle. I have implemented these methods to match the expected behavior of a categorical scale, similar to the Nominal class.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `seaborn/_core/scales.py` (4-line block → 32-line replacement)

**Replaces:**

```python
@dataclass
class Ordinal(Scale):
    # Categorical (convert to strings), sortable, can skip ticklabels
    ...
```

**With:**

```python
@dataclass
class Ordinal(Scale):
    # Categorical (convert to strings), sortable, can skip ticklabels
    values: tuple | str | list | dict | None = None
    order: list | None = None

    _priority: ClassVar[int] = 4

    def _setup(
        self, data: Series, prop: Property, axis: Axis | None = None,
    ) -> Scale:
        # Ordinal behaves like Nominal for setup
        return Nominal(values=self.values, order=self.order)._setup(data, prop, axis)

    def _finalize(self, p: Plot, axis: Axis) -> None:
        return Nominal(values=self.values, order=self.order)._finalize(p, axis)

    def tick(self, locator: Locator | None = None) -> Ordinal:
        new = copy(self)
        new._tick_params = {"locator": locator}
        return new

    def label(self, formatter: Formatter | None = None) -> Ordinal:
        new = copy(self)
        new._label_params = {"formatter": formatter}
        return new

    def _get_locators(self, locator):
        return Nominal()._get_locators(locator)

    def _get_formatter(self, locator, formatter):
        return Nominal()._get_formatter(locator, formatter)
```

## Test results

**PASSED** — 0/0 passed, 0 failed, 0 skipped, 0 errored (duration 2661 ms).

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
1 error in 1.59s

```

</details>

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `seaborn/_core/scales.py` | 752 → 772 | 82 → 88 | 2.79 → 2.66 | 16 → 16 | 23.27 → 21.81 |

## Diff

```diff
diff --git a/seaborn/_core/scales.py b/seaborn/_core/scales.py
index be3815a..d23bcda 100644
--- a/seaborn/_core/scales.py
+++ b/seaborn/_core/scales.py
@@ -407,7 +407,35 @@ class Nominal(Scale):
 @dataclass
 class Ordinal(Scale):
     # Categorical (convert to strings), sortable, can skip ticklabels
-    ...
+    values: tuple | str | list | dict | None = None
+    order: list | None = None
+
+    _priority: ClassVar[int] = 4
+
+    def _setup(
+        self, data: Series, prop: Property, axis: Axis | None = None,
+    ) -> Scale:
+        # Ordinal behaves like Nominal for setup
+        return Nominal(values=self.values, order=self.order)._setup(data, prop, axis)
+
+    def _finalize(self, p: Plot, axis: Axis) -> None:
+        return Nominal(values=self.values, order=self.order)._finalize(p, axis)
+
+    def tick(self, locator: Locator | None = None) -> Ordinal:
+        new = copy(self)
+        new._tick_params = {"locator": locator}
+        return new
+
+    def label(self, formatter: Formatter | None = None) -> Ordinal:
+        new = copy(self)
+        new._label_params = {"formatter": formatter}
+        return new
+
+    def _get_locators(self, locator):
+        return Nominal()._get_locators(locator)
+
+    def _get_formatter(self, locator, formatter):
+        return Nominal()._get_formatter(locator, formatter)
 
 
 @dataclass

```
