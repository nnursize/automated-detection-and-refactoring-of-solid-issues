# Refactor ISP-001 (ISP): Fat interface bundling data transformation with axis-specific UI logic

**Status:** `applied_passed`  
**Branch:** `refactor/ISP-001` -> `main`  
**Head commit:** `21f13251f9426b9375e5bf9e31e9793c9438265d`  
**LLM finish:** `FinishReason.STOP` (prompt 10741, completion 1255)  

## Detected issue

- **File**: `seaborn/_core/scales.py`
- **Entity**: `Scale` (class)
- **Lines (at detection time)**: L38–L100
- **Severity**: high
- **Confidence**: detected by 5 scan(s)

**Description.** Fat interface bundling data transformation with axis-specific UI logic

**Reasoning.** The Scale interface combines data transformation logic (__call__) with axis-specific UI logic (tick, label, _get_locators). This forces semantic scales (like color or size) to implement or mock axis-specific methods. The Identity scale subclass (lines 91-100) is forced to inherit these methods but cannot fulfill them, leading to NotImplementedError crashes if called.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 7
- **Files modified** (1): `seaborn/_core/scales.py`

**Summary.** Extract axis-related logic from Scale into a new AxisScale mixin

**Rationale.** The Scale base class was violating the Interface Segregation Principle by forcing all scales (including non-axis-based ones like Identity) to implement axis-specific methods. By introducing an AxisScale mixin, only scales that actually require axis-related functionality (like Continuous, Temporal, Nominal, Boolean) will inherit these methods, while simple scales remain clean.

## Changes overview

_7 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `seaborn/_core/scales.py` (44-line block → 16-line replacement)

**Replaces:**

```python
class Scale:
    """Base class for objects that map data values to visual properties."""

    values: tuple | str | list | dict | None

    _priority: ClassVar[int]
    _pipeline: Pipeline
    _matplotlib_scale: ScaleBase
    _spacer: staticmethod
    _legend: tuple[list[Any], list[str]] | None

    def __post_init__(self):

        self._tick_params = None
        self._label_params = None
        self._legend = None

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

    def _spacing(self, x: Series) -> float:
```

**With:**

```python
class Scale:
    """Base class for objects that map data values to visual properties."""

    values: tuple | str | list | dict | None

    _priority: ClassVar[int]
    _pipeline: Pipeline
    _matplotlib_scale: ScaleBase
    _spacer: staticmethod
    _legend: tuple[list[Any], list[str]] | None

    def __post_init__(self):

        self._legend = None

    def _spacing(self, x: Series) -> float:
```

### 2. EDIT `seaborn/_core/scales.py` (16-line block → 47-line replacement)

**Replaces:**

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

**With:**

```python
    @staticmethod
    def _identity():

        class Identity(Scale):
            _pipeline = []
            _spacer = _default_spacer
            _legend = None
            _matplotlib_scale = None

            def _setup(self, data, prop, axis=None): return self

        return Identity()


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

### 3. EDIT `seaborn/_core/scales.py` (2-line block → 2-line replacement)

**Replaces:**

```python
@dataclass
class Boolean(Scale):
```

**With:**

```python
@dataclass
class Boolean(AxisScale):
```

### 4. EDIT `seaborn/_core/scales.py` (2-line block → 2-line replacement)

**Replaces:**

```python
@dataclass
class Nominal(Scale):
```

**With:**

```python
@dataclass
class Nominal(AxisScale):
```

### 5. EDIT `seaborn/_core/scales.py` (2-line block → 2-line replacement)

**Replaces:**

```python
@dataclass
class Ordinal(Scale):
```

**With:**

```python
@dataclass
class Ordinal(AxisScale):
```

### 6. EDIT `seaborn/_core/scales.py` (2-line block → 2-line replacement)

**Replaces:**

```python
@dataclass
class ContinuousBase(Scale):
```

**With:**

```python
@dataclass
class ContinuousBase(AxisScale):
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
class Temporal(ContinuousBase):
```

## Test results

**PASSED** — 0/0 passed, 0 failed, 0 skipped, 0 errored (duration 2210 ms).

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
1 error in 1.36s

```

</details>

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `seaborn/_core/scales.py` | 772 → 772 | 88 → 85 | 2.66 → 2.64 | 16 → 16 | 21.81 → 21.74 |

## Diff

```diff
diff --git a/seaborn/_core/scales.py b/seaborn/_core/scales.py
index d23bcda..61eaf91 100644
--- a/seaborn/_core/scales.py
+++ b/seaborn/_core/scales.py
@@ -65,36 +65,8 @@ class Scale:
 
     def __post_init__(self):
 
-        self._tick_params = None
-        self._label_params = None
         self._legend = None
 
-    def tick(self):
-        raise NotImplementedError()
-
-    def label(self):
-        raise NotImplementedError()
-
-    def _get_locators(self):
-        raise NotImplementedError()
-
-    def _get_formatter(self, locator: Locator | None = None):
-        raise NotImplementedError()
-
-    def _get_scale(self, name: str, forward: Callable, inverse: Callable):
-
-        major_locator, minor_locator = self._get_locators(**self._tick_params)
-        major_formatter = self._get_formatter(major_locator, **self._label_params)
-
-        class InternalScale(mpl.scale.FuncScale):
-            def set_default_locators_and_formatters(self, axis):
-                axis.set_major_locator(major_locator)
-                if minor_locator is not None:
-                    axis.set_minor_locator(minor_locator)
-                axis.set_major_formatter(major_formatter)
-
-        return InternalScale(name, (forward, inverse))
-
     def _spacing(self, x: Series) -> float:
         space = self._spacer(x)
         if np.isnan(space):
@@ -142,17 +114,48 @@ class Scale:
             _legend = None
             _matplotlib_scale = None
 
-            def tick(self): return self
-            def label(self): return self
-            def _get_locators(self): return None, None
-            def _get_formatter(self, locator=None): return None
             def _setup(self, data, prop, axis=None): return self
 
         return Identity()
 
 
+class AxisScale(Scale):
+    """Mixin for scales that interact with matplotlib axes."""
+
+    def __post_init__(self):
+        super().__post_init__()
+        self._tick_params = None
+        self._label_params = None
+
+    def tick(self):
+        raise NotImplementedError()
+
+    def label(self):
+        raise NotImplementedError()
+
+    def _get_locators(self):
+        raise NotImplementedError()
+
+    def _get_formatter(self, locator: Locator | None = None):
+        raise NotImplementedError()
+
+    def _get_scale(self, name: str, forward: Callable, inverse: Callable):
+
+        major_locator, minor_locator = self._get_locators(**self._tick_params)
+        major_formatter = self._get_formatter(major_locator, **self._label_params)
+
+        class InternalScale(mpl.scale.FuncScale):
+            def set_default_locators_and_formatters(self, axis):
+                axis.set_major_locator(major_locator)
+                if minor_locator is not None:
+                    axis.set_minor_locator(minor_locator)
+                axis.set_major_formatter(major_formatter)
+
+        return InternalScale(name, (forward, inverse))
+
+
 @dataclass
-class Boolean(Scale):
+class Boolean(AxisScale):
     """
     A scale with a discrete domain of True and False values.
 
@@ -245,7 +248,7 @@ class Boolean(Scale):
 
 
 @dataclass
-class Nominal(Scale):
+class Nominal(AxisScale):
     """
     A categorical scale without relative importance / magnitude.
     """
@@ -405,7 +408,7 @@ class Nominal(Scale):
 
 
 @dataclass
-class Ordinal(Scale):
+class Ordinal(AxisScale):
     # Categorical (convert to strings), sortable, can skip ticklabels
     values: tuple | str | list | dict | None = None
     order: list | None = None
@@ -445,7 +448,7 @@ class Discrete(Scale):
 
 
 @dataclass
-class ContinuousBase(Scale):
+class ContinuousBase(AxisScale):
 
     values: tuple | str | None = None
     norm: tuple | None = None

```
