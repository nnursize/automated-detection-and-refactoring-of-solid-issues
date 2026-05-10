# Refactor ISP-002 (ISP): Fat interface for scaling different data types

**Status:** `patch_failed`  
**Branch:** `refactor/ISP-002` -> `main`  
**Head commit:** `14f086e1720df31de4efa70f9f8dae75c317a42e`  
**LLM finish:** `FinishReason.STOP` (prompt 11888, completion 2135)  

## Detected issue

- **File**: `seaborn/_base.py`
- **Entity**: `VectorPlotter` (class)
- **Lines (at detection time)**: L1042–L1110
- **Severity**: medium
- **Confidence**: detected by 9 scan(s)

**Description.** Fat interface for scaling different data types

**Reasoning.** VectorPlotter defines a broad scaling interface (scale_native, scale_numeric, scale_datetime, scale_categorical). Subclasses like _CategoricalPlotter are forced to inherit and carry methods for data types they do not support, leaving them as the default NotImplementedError. This forces subclasses to depend on methods they do not use.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `seaborn/_base.py`

**Summary.** Extract scaling methods from VectorPlotter into a mixin class to satisfy ISP

**Rationale.** The VectorPlotter class contained generic scaling methods (scale_native, scale_numeric, scale_datetime, scale_categorical) that were not applicable to all subclasses. By moving these to a separate 'PlotterScaler' mixin, we allow subclasses to opt-in to these scaling capabilities only if needed, resolving the ISP violation.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `seaborn/_base.py` (114-line block → 90-line replacement)

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
        """
        Enforce categorical (fixed-scale) rules for the data on given axis.

        Parameters
        ----------
        axis : "x" or "y"
            Axis of the plot to operate on.
        order : list
            Order that unique values should appear in.
        formatter : callable
            Function mapping values to a string representation.

        Returns
        -------
        self

        """
        # This method both modifies the internal representation of the data
        # (converting it to string) and sets some attributes on self. It might be
        # a good idea to have a separate object attached to self that contains the
        # information in those attributes (i.e. whether to enforce variable order
        # across facets, the order to use) similar to the SemanticMapping objects
        # we have for semantic variables. That object could also hold the converter
        # objects that get used, if we can decouple those from an existing axis
        # (cf. https://github.com/matplotlib/matplotlib/issues/19229).
        # There are some interactions with faceting information that would need
        # to be thought through, since the converts to use depend on facets.
        # If we go that route, these methods could become "borrowed" methods similar
        # to what happens with the alternate semantic mapper constructors, although
        # that approach is kind of fussy and confusing.

        # TODO this method could also set the grid state? Since we like to have no
        # grid on the categorical axis by default. Again, a case where we'll need to
        # store information until we use it, so best to have a way to collect the
... (54 more line(s) truncated)
```

**With:**

```python
class PlotterScaler:
    """Mixin for scaling data on plot axes."""

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
        """
        Enforce categorical (fixed-scale) rules for the data on given axis.

        Parameters
        ----------
        axis : "x" or "y"
            Axis of the plot to operate on.
        order : list
            Order that unique values should appear in.
        formatter : callable
            Function mapping values to a string representation.

        Returns
        -------
        self

        """
        _check_argument("axis", ["x", "y"], axis)

        # Categorical plots can be "univariate" in which case they get an anonymous
        # category label on the opposite axis.
        if axis not in self.variables:
            self.variables[axis] = None
            self.var_types[axis] = "categorical"
            self.plot_data[axis] = ""

        # If the "categorical" variable has a numeric type, sort the rows so that
        # the default result from categorical_order has those values sorted after
        # they have been coerced to strings.
        if self.var_types[axis] == "numeric":
            self.plot_data = self.plot_data.sort_values(axis, kind="mergesort")
... (30 more line(s) truncated)
```

## Apply error

```
search_text not found in seaborn/_base.py (block 0)
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `seaborn/_base.py` | 1145 → - | 47 → - | 6.82 → - | 28 → - | 0 → - |

## Diff

*(no diff — patch was not applied)*
