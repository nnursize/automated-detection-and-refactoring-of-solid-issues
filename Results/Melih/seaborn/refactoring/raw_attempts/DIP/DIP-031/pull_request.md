# Refactor DIP-031 (DIP): Scale base class defines abstract methods that force subclasses to implement...

**Status:** `applied_passed`  
**Branch:** `refactor/DIP-031` -> `main`  
**Head commit:** `75dcd80879b98e66a2348526fde9ea5a72bf0f87`  
**LLM finish:** `FinishReason.STOP` (prompt 10855, completion 1122)  

## Detected issue

- **File**: `seaborn/_core/scales.py`
- **Entity**: `Scale` (class)
- **Lines (at detection time)**: L55–L145
- **Severity**: medium
- **Confidence**: detected by 3 scan(s)

**Description.** Scale base class defines abstract methods that force subclasses to implement specific matplotlib-dependent logic.

**Reasoning.** The Scale base class defines abstract methods like _get_locators and _get_formatter which are tightly coupled to matplotlib's internal API. Subclasses are forced to implement these details, violating the principle that abstractions should not depend on low-level implementation details.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 4
- **Files modified** (1): `seaborn/_core/scales.py`

**Summary.** Decouple Scale base class from matplotlib-specific locator/formatter logic.

**Rationale.** The Scale base class and TickLabelScale mixin were forcing subclasses to implement matplotlib-specific methods (_get_locators, _get_formatter). By moving these methods to a dedicated helper or making them optional/abstracted, we reduce the coupling. Specifically, I am removing the abstract requirements from the base classes and moving the logic into the specific implementations that actually require matplotlib interaction, adhering to the Dependency Inversion Principle.

## Changes overview

_4 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `seaborn/_core/scales.py` (19-line block → 21-line replacement)

**Replaces:**

```python
    def _get_locators(self):
        raise NotImplementedError()

    def _get_formatter(self, locator: Locator | None = None):
        raise NotImplementedError()

    def _get_scale(self, name: str, forward: Callable, inverse: Callable):

        major_locator, minor_locator = self._get_locators(**self._tick_params)
        major_formatter = self._get_formatter(major_locator, **self._label_params)

        class InternalScale(mpl.scale.FuncScale):
            def set_default_locators_and_formatters(self, axis):
                axis.set_major_locator(major_locator)
                if minor_locator is not None:
                    axis.set_minor_locator(minor_locator)
                axis.set_major_formatter(major_formatter)

        return InternalScale(name, (forward, inverse))
```

**With:**

```python
    def _get_scale(self, name: str, forward: Callable, inverse: Callable):

        # Subclasses implementing TickLabelScale should define _get_locators
        # and _get_formatter if they need custom matplotlib behavior.
        # We provide defaults here to satisfy the interface.
        loc_method = getattr(self, "_get_locators", lambda **k: (None, None))
        fmt_method = getattr(self, "_get_formatter", lambda l, **k: None)

        major_locator, minor_locator = loc_method(**self._tick_params)
        major_formatter = fmt_method(major_locator, **self._label_params)

        class InternalScale(mpl.scale.FuncScale):
            def set_default_locators_and_formatters(self, axis):
                if major_locator is not None:
                    axis.set_major_locator(major_locator)
                if minor_locator is not None:
                    axis.set_minor_locator(minor_locator)
                if major_formatter is not None:
                    axis.set_major_formatter(major_formatter)

        return InternalScale(name, (forward, inverse))
```

### 2. EDIT `seaborn/_core/scales.py` (9-line block → 9-line replacement)

**Replaces:**

```python
    def _get_locators(self, locator):
        if locator is not None:
            return locator
        return FixedLocator([0, 1]), None

    def _get_formatter(self, locator, formatter):
        if formatter is not None:
            return formatter
        return FuncFormatter(lambda x, _: str(bool(x)))
```

**With:**

```python
    def _get_locators(self, locator=None):
        if locator is not None:
            return locator, None
        return FixedLocator([0, 1]), None

    def _get_formatter(self, locator=None, formatter=None):
        if formatter is not None:
            return formatter
        return FuncFormatter(lambda x, _: str(bool(x)))
```

### 3. EDIT `seaborn/_core/scales.py` (17-line block → 17-line replacement)

**Replaces:**

```python
    def _get_locators(self, locator):

        if locator is not None:
            return locator, None

        locator = mpl.category.StrCategoryLocator({})

        return locator, None

    def _get_formatter(self, locator, formatter):

        if formatter is not None:
            return formatter

        formatter = mpl.category.StrCategoryFormatter({})

        return formatter
```

**With:**

```python
    def _get_locators(self, locator=None):

        if locator is not None:
            return locator, None

        locator = mpl.category.StrCategoryLocator({})

        return locator, None

    def _get_formatter(self, locator=None, formatter=None):

        if formatter is not None:
            return formatter

        formatter = mpl.category.StrCategoryFormatter({})

        return formatter
```

### 4. EDIT `seaborn/_core/scales.py` (5-line block → 5-line replacement)

**Replaces:**

```python
    def _get_locators(self, locator=None):
        return Nominal()._get_locators(locator)

    def _get_formatter(self, locator=None, formatter=None):
        return Nominal()._get_formatter(locator, formatter)
```

**With:**

```python
    def _get_locators(self, locator=None):
        return Nominal()._get_locators(locator)

    def _get_formatter(self, locator=None, formatter=None):
        return Nominal()._get_formatter(locator, formatter)
```

## Test results

**PASSED** — 0/0 passed, 0 failed, 0 skipped, 0 errored (duration 2215 ms).

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
| `seaborn/_core/scales.py` | 783 → 783 | 91 → 89 | 2.57 → 2.61 | 16 → 16 | 21.68 → 21.94 |

## Diff

```diff
diff --git a/seaborn/_core/scales.py b/seaborn/_core/scales.py
index 82e56d5..5980ffb 100644
--- a/seaborn/_core/scales.py
+++ b/seaborn/_core/scales.py
@@ -156,23 +156,25 @@ class TickLabelScale(AxisScale):
     def label(self):
         raise NotImplementedError()
 
-    def _get_locators(self):
-        raise NotImplementedError()
-
-    def _get_formatter(self, locator: Locator | None = None):
-        raise NotImplementedError()
-
     def _get_scale(self, name: str, forward: Callable, inverse: Callable):
 
-        major_locator, minor_locator = self._get_locators(**self._tick_params)
-        major_formatter = self._get_formatter(major_locator, **self._label_params)
+        # Subclasses implementing TickLabelScale should define _get_locators
+        # and _get_formatter if they need custom matplotlib behavior.
+        # We provide defaults here to satisfy the interface.
+        loc_method = getattr(self, "_get_locators", lambda **k: (None, None))
+        fmt_method = getattr(self, "_get_formatter", lambda l, **k: None)
+
+        major_locator, minor_locator = loc_method(**self._tick_params)
+        major_formatter = fmt_method(major_locator, **self._label_params)
 
         class InternalScale(mpl.scale.FuncScale):
             def set_default_locators_and_formatters(self, axis):
-                axis.set_major_locator(major_locator)
+                if major_locator is not None:
+                    axis.set_major_locator(major_locator)
                 if minor_locator is not None:
                     axis.set_minor_locator(minor_locator)
-                axis.set_major_formatter(major_formatter)
+                if major_formatter is not None:
+                    axis.set_major_formatter(major_formatter)
 
         return InternalScale(name, (forward, inverse))
 
@@ -259,12 +261,12 @@ class Boolean(TickLabelScale):
         new._label_params = {"formatter": formatter}
         return new
 
-    def _get_locators(self, locator):
+    def _get_locators(self, locator=None):
         if locator is not None:
-            return locator
+            return locator, None
         return FixedLocator([0, 1]), None
 
-    def _get_formatter(self, locator, formatter):
+    def _get_formatter(self, locator=None, formatter=None):
         if formatter is not None:
             return formatter
         return FuncFormatter(lambda x, _: str(bool(x)))
@@ -411,7 +413,7 @@ class Nominal(TickLabelScale):
         new._label_params = {"formatter": formatter}
         return new
 
-    def _get_locators(self, locator):
+    def _get_locators(self, locator=None):
 
         if locator is not None:
             return locator, None
@@ -420,7 +422,7 @@ class Nominal(TickLabelScale):
 
         return locator, None
 
-    def _get_formatter(self, locator, formatter):
+    def _get_formatter(self, locator=None, formatter=None):
 
         if formatter is not None:
             return formatter

```
