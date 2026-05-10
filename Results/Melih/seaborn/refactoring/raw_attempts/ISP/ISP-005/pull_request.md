# Refactor ISP-005 (ISP): ContinuousBase fails to implement multiple methods of the Scale interface.

**Status:** `applied_passed`  
**Branch:** `refactor/ISP-005` -> `main`  
**Head commit:** `2682fe601550ef9b10a85e5ae8950b695961a943`  
**LLM finish:** `FinishReason.STOP` (prompt 10742, completion 1143)  

## Detected issue

- **File**: `seaborn/_core/scales.py`
- **Entity**: `ContinuousBase` (class)
- **Lines (at detection time)**: L255–L334
- **Severity**: high
- **Confidence**: detected by 1 scan(s)

**Description.** ContinuousBase fails to implement multiple methods of the Scale interface.

**Reasoning.** ContinuousBase implements the Scale interface but fails to provide implementations for tick, label, _get_locators, and _get_formatter, leaving them to raise NotImplementedError. This indicates that the Scale interface is too broad (fat) for this specific base class, which is designed only to handle setup and transformation logic rather than axis decoration.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 7
- **Files modified** (1): `seaborn/_core/scales.py`

**Summary.** Split AxisScale into AxisScale and TickLabelScale to resolve ISP violation

**Rationale.** The Scale interface was too broad for classes that only need basic axis interaction but not necessarily tick/label configuration logic. By splitting the interface, classes like ContinuousBase (which handles transformation logic) are no longer forced to implement tick/label methods that were previously raising NotImplementedError.

## Changes overview

_7 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `seaborn/_core/scales.py` (33-line block → 40-line replacement)

**Replaces:**

```python
class AxisScale(Scale):
    """Mixin for scales that interact with matplotlib axes."""

    def __post_init__(self):
        super().__post_init__()
        self._tick_params = None
        self._label_params = None

    def tick(self):
        raise NotImplementedError()

    def label(self):
        raise NotImplementedError()

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
class AxisScale(Scale):
    """Mixin for scales that interact with matplotlib axes."""

    def _get_scale(self, name: str, forward: Callable, inverse: Callable):
        return mpl.scale.FuncScale(name, (forward, inverse))


class TickLabelScale(AxisScale):
    """Mixin for scales that support tick and label configuration."""

    def __post_init__(self):
        super().__post_init__()
        self._tick_params = None
        self._label_params = None

    def tick(self):
        raise NotImplementedError()

    def label(self):
        raise NotImplementedError()

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

### 2. EDIT `seaborn/_core/scales.py` (2-line block → 2-line replacement)

**Replaces:**

```python
@dataclass
class Boolean(AxisScale):
```

**With:**

```python
@dataclass
class Boolean(TickLabelScale):
```

### 3. EDIT `seaborn/_core/scales.py` (2-line block → 2-line replacement)

**Replaces:**

```python
@dataclass
class Nominal(AxisScale):
```

**With:**

```python
@dataclass
class Nominal(TickLabelScale):
```

### 4. EDIT `seaborn/_core/scales.py` (2-line block → 2-line replacement)

**Replaces:**

```python
@dataclass
class Ordinal(AxisScale):
```

**With:**

```python
@dataclass
class Ordinal(TickLabelScale):
```

### 5. EDIT `seaborn/_core/scales.py` (17-line block → 12-line replacement)

**Replaces:**

```python
@dataclass
class ContinuousBase(AxisScale):

    values: tuple | str | None = None
    norm: tuple | None = None

    def _setup(
        self, data: Series, prop: Property, axis: Axis | None = None,
    ) -> Scale:

        new = copy(self)
        if new._tick_params is None:
            new = new.tick()
        if new._label_params is None:
            new = new.label()

        forward, inverse = new._get_transform()
```

**With:**

```python
@dataclass
class ContinuousBase(AxisScale):

    values: tuple | str | None = None
    norm: tuple | None = None

    def _setup(
        self, data: Series, prop: Property, axis: Axis | None = None,
    ) -> Scale:

        new = copy(self)
        forward, inverse = new._get_transform()
```

### 6. EDIT `seaborn/_core/scales.py` (2-line block → 2-line replacement)

**Replaces:**

```python
@dataclass
class Continuous(ContinuousBase):
```

**With:**

```python
@dataclass
class Continuous(ContinuousBase, TickLabelScale):
```

### 7. EDIT `seaborn/_core/scales.py` (2-line block → 2-line replacement)

**Replaces:**

```python
@dataclass
class Temporal(ContinuousBase):
```

**With:**

```python
@dataclass
class Temporal(ContinuousBase, TickLabelScale):
```

## Test results

**PASSED** — 0/0 passed, 0 failed, 0 skipped, 0 errored (duration 2421 ms).

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
1 error in 1.50s

```

</details>

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `seaborn/_core/scales.py` | 775 → 775 | 86 → 87 | 2.64 → 2.57 | 16 → 16 | 21.69 → 21.88 |

## Diff

```diff
diff --git a/seaborn/_core/scales.py b/seaborn/_core/scales.py
index bbbfa96..1abc9f9 100644
--- a/seaborn/_core/scales.py
+++ b/seaborn/_core/scales.py
@@ -126,6 +126,13 @@ class Scale:
 class AxisScale(Scale):
     """Mixin for scales that interact with matplotlib axes."""
 
+    def _get_scale(self, name: str, forward: Callable, inverse: Callable):
+        return mpl.scale.FuncScale(name, (forward, inverse))
+
+
+class TickLabelScale(AxisScale):
+    """Mixin for scales that support tick and label configuration."""
+
     def __post_init__(self):
         super().__post_init__()
         self._tick_params = None
@@ -159,7 +166,7 @@ class AxisScale(Scale):
 
 
 @dataclass
-class Boolean(AxisScale):
+class Boolean(TickLabelScale):
     """
     A scale with a discrete domain of True and False values.
 
@@ -252,7 +259,7 @@ class Boolean(AxisScale):
 
 
 @dataclass
-class Nominal(AxisScale):
+class Nominal(TickLabelScale):
     """
     A categorical scale without relative importance / magnitude.
     """
@@ -412,7 +419,7 @@ class Nominal(AxisScale):
 
 
 @dataclass
-class Ordinal(AxisScale):
+class Ordinal(TickLabelScale):
     # Categorical (convert to strings), sortable, can skip ticklabels
     values: tuple | str | list | dict | None = None
     order: list | None = None
@@ -462,11 +469,6 @@ class ContinuousBase(AxisScale):
     ) -> Scale:
 
         new = copy(self)
-        if new._tick_params is None:
-            new = new.tick()
-        if new._label_params is None:
-            new = new.label()
-
         forward, inverse = new._get_transform()
 
         mpl_scale = new._get_scale(str(data.name), forward, inverse)
@@ -564,7 +566,7 @@ class ContinuousBase(AxisScale):
 
 
 @dataclass
-class Continuous(ContinuousBase):
+class Continuous(ContinuousBase, TickLabelScale):
     """
     A numeric scale supporting norms and functional transforms.
     """
@@ -789,7 +791,7 @@ class Continuous(ContinuousBase):
 
 
 @dataclass
-class Temporal(ContinuousBase):
+class Temporal(ContinuousBase, TickLabelScale):
     """
     A scale for date/time data.
     """

```
