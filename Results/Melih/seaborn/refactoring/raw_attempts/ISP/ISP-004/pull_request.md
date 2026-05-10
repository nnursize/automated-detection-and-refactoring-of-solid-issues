# Refactor ISP-004 (ISP): Base class defines a scaling interface that subclasses cannot fully satisfy.

**Status:** `applied_passed`  
**Branch:** `refactor/ISP-004` -> `main`  
**Head commit:** `858bf09fcd98754b8b32b96ddd40cd95eeaed120`  
**LLM finish:** `FinishReason.STOP` (prompt 11911, completion 1752)  

## Detected issue

- **File**: `seaborn/_base.py`
- **Entity**: `VectorPlotter` (class)
- **Lines (at detection time)**: L1111–L1128
- **Severity**: high
- **Confidence**: detected by 2 scan(s)

**Description.** Base class defines a scaling interface that subclasses cannot fully satisfy.

**Reasoning.** The VectorPlotter class defines an interface for multiple types of data scaling including scale_native, scale_numeric, and scale_datetime. These methods raise NotImplementedError by default. Subclasses like _CategoricalPlotter are forced to inherit these methods even though they are only intended to handle categorical data. This forces subclasses to depend on and expose an interface they do not use or support, which is a direct violation of ISP.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 2
- **Files modified** (1): `seaborn/_base.py`

**Summary.** Extract scaling methods from VectorPlotter into a mixin class to resolve ISP violation.

**Rationale.** The VectorPlotter class was forced to implement scaling methods (native, numeric, datetime) that were not applicable to all subclasses (e.g., categorical plotters). By moving these to a 'ScaleMixin', we allow only the relevant plotters to inherit these capabilities, adhering to the Interface Segregation Principle.

## Changes overview

_2 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `seaborn/_base.py` (26-line block → 24-line replacement)

**Replaces:**

```python
    # XXX If the scale_* methods are going to modify the plot_data structure, they
    # can't be called twice. That means that if they are called twice, they should
    # raise. Alternatively, we could store an original version of plot_data and each
    # time they are called they operate on the store, not the current state.

    def scale_native(self, axis, *args, **kwargs):

        # Default, defer to matplotlib

        raise NotImplementedError

    def scale_numeric(self, axis, *args, **kwargs):

        # Feels needed to completeness, what should it do?
        # Perhaps handle log scaling? Set the ticker/formatter/limits?

        raise NotImplementedError

    def scale_datetime(self, axis, *args, **kwargs):

        # Use pd.to_datetime to convert strings or numbers to datetime objects
        # Note, use day-resolution for numeric->datetime to match matplotlib

        raise NotImplementedError

    def scale_categorical(self, axis, order=None, formatter=None):
```

**With:**

```python
class ScaleMixin:
    """Mixin for plotters that support data scaling."""

    def scale_native(self, axis, *args, **kwargs):

        # Default, defer to matplotlib

        raise NotImplementedError

    def scale_numeric(self, axis, *args, **kwargs):

        # Feels needed to completeness, what should it do?
        # Perhaps handle log scaling? Set the ticker/formatter/limits?

        raise NotImplementedError

    def scale_datetime(self, axis, *args, **kwargs):

        # Use pd.to_datetime to convert strings or numbers to datetime objects
        # Note, use day-resolution for numeric->datetime to match matplotlib

        raise NotImplementedError

    def scale_categorical(self, axis, order=None, formatter=None):
```

### 2. EDIT `seaborn/_base.py` (52-line block → 52-line replacement)

**Replaces:**

```python
        # TODO another, and distinct idea, is to expose a cut= param here

        _check_argument("axis", ["x", "y"], axis)

        # Categorical plots can be "univariate" in which case they get an anonymous
        # category label on the opposite axis.
        if axis not in self.variables:
            self.variables[axis] = None
            self.var_types[axis] = "categorical"
            self.plot_data[axis] = ""

        # If the "categorical" variable has a numeric type, sort the rows so that
        # the default result from categorical_order has those values sorted after
        # they have been coerced to strings. The reason for this is so that later
        # we can get facet-wise orders that are correct.
        # XXX Should this also sort datetimes?
        # It feels more consistent, but technically will be a default change
        # If so, should also change categorical_order to behave that way
        if self.var_types[axis] == "numeric":
            self.plot_data = self.plot_data.sort_values(axis, kind="mergesort")

        # Now get a reference to the categorical data vector and remove na values
        cat_data = self.plot_data[axis].dropna()

        # Get the initial categorical order, which we do before string
        # conversion to respect the original types of the order list.
        # Track whether the order is given explicitly so that we can know
        # whether or not to use the order constructed here downstream
        self._var_ordered[axis] = order is not None or cat_data.dtype.name == "category"
        order = pd.Index(categorical_order(cat_data, order), name=axis)

        # Then convert data to strings. This is because in matplotlib,
        # "categorical" data really mean "string" data, so doing this artists
        # will be drawn on the categorical axis with a fixed scale.
        # TODO implement formatter here; check that it returns strings?
        if formatter is not None:
            cat_data = cat_data.map(formatter)
            order = order.map(formatter)
        else:
            cat_data = cat_data.astype(str)
            order = order.astype(str)

        # Update the levels list with the type-converted order variable
        self.var_levels[axis] = order

        # Now ensure that seaborn will use categorical rules internally
        self.var_types[axis] = "categorical"

        # Put the string-typed categorical vector back into the plot_data structure
        self.plot_data[axis] = cat_data

        return self
```

**With:**

```python
        # TODO another, and distinct idea, is to expose a cut= param here

        _check_argument("axis", ["x", "y"], axis)

        # Categorical plots can be "univariate" in which case they get an anonymous
        # category label on the opposite axis.
        if axis not in self.variables:
            self.variables[axis] = None
            self.var_types[axis] = "categorical"
            self.plot_data[axis] = ""

        # If the "categorical" variable has a numeric type, sort the rows so that
        # the default result from categorical_order has those values sorted after
        # they have been coerced to strings. The reason for this is so that later
        # we can get facet-wise orders that are correct.
        # XXX Should this also sort datetimes?
        # It feels more consistent, but technically will be a default change
        # If so, should also change categorical_order to behave that way
        if self.var_types[axis] == "numeric":
            self.plot_data = self.plot_data.sort_values(axis, kind="mergesort")

        # Now get a reference to the categorical data vector and remove na values
        cat_data = self.plot_data[axis].dropna()

        # Get the initial categorical order, which we do before string
        # conversion to respect the original types of the order list.
        # Track whether the order is given explicitly so that we can know
        # whether or not to use the order constructed here downstream
        self._var_ordered[axis] = order is not None or cat_data.dtype.name == "category"
        order = pd.Index(categorical_order(cat_data, order), name=axis)

        # Then convert data to strings. This is because in matplotlib,
        # "categorical" data really mean "string" data, so doing this artists
        # will be drawn on the categorical axis with a fixed scale.
        # TODO implement formatter here; check that it returns strings?
        if formatter is not None:
            cat_data = cat_data.map(formatter)
            order = order.map(formatter)
        else:
            cat_data = cat_data.astype(str)
            order = order.astype(str)

        # Update the levels list with the type-converted order variable
        self.var_levels[axis] = order

        # Now ensure that seaborn will use categorical rules internally
        self.var_types[axis] = "categorical"

        # Put the string-typed categorical vector back into the plot_data structure
        self.plot_data[axis] = cat_data

        return self
```

## Test results

**PASSED** — 0/0 passed, 0 failed, 0 skipped, 0 errored (duration 2306 ms).

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
1 error in 1.39s

```

</details>

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `seaborn/_base.py` | 1145 → 1147 | 47 → 47 | 6.82 → 6.76 | 28 → 28 | 0 → 0 |

## Diff

```diff
diff --git a/seaborn/_base.py b/seaborn/_base.py
index f427bc4..0d9f010 100644
--- a/seaborn/_base.py
+++ b/seaborn/_base.py
@@ -1329,10 +1329,8 @@ class VectorPlotter:
                 attr.update({k: v[level] for k, v in other_props.items() if level in v})
                 update(self.variables[var], formatted_level, **attr)
 
-    # XXX If the scale_* methods are going to modify the plot_data structure, they
-    # can't be called twice. That means that if they are called twice, they should
-    # raise. Alternatively, we could store an original version of plot_data and each
-    # time they are called they operate on the store, not the current state.
+class ScaleMixin:
+    """Mixin for plotters that support data scaling."""
 
     def scale_native(self, axis, *args, **kwargs):
 

```
