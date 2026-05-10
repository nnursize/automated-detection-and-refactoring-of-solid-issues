# Refactor SRP-001 (SRP): The constructor handles data reshaping, variable renaming, orientation infere...

**Status:** `patch_failed`  
**Branch:** `refactor/SRP-001` -> `main`  
**Head commit:** `11e83875a77e0bb4e9692f7d424a486dbeb007fc`  
**LLM finish:** `FinishReason.STOP` (prompt 4017, completion 1352)  

## Detected issue

- **File**: `seaborn/categorical.py`
- **Entity**: `_CategoricalPlotter.__init__` (class)
- **Lines (at detection time)**: L40–L96
- **Severity**: high
- **Confidence**: detected by 12 scan(s)

**Description.** The constructor handles data reshaping, variable renaming, orientation inference, legend initialization, and categorical level ordering.

**Reasoning.** This constructor bundles multiple responsibilities: data transformation (renaming x/y for wide data, adding anonymous category), configuration (inferring orient, setting legend), and data preparation (determining categorical levels). A change in wide-form data handling, orientation inference rules, or categorical ordering logic would all require modifying this method, indicating multiple reasons to change.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `seaborn/categorical.py`

**Summary.** Extract data preparation logic from _CategoricalPlotter.__init__ into helper methods.

**Rationale.** The constructor was performing multiple distinct tasks (wide-form data reshaping, hue cleanup, and categorical level setup). Moving these into dedicated private methods improves readability and adheres to the Single Responsibility Principle.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `seaborn/categorical.py` (58-line block → 45-line replacement)

**Replaces:**

```python
        # For wide data, orient determines assignment to x/y differently from the
        # default VectorPlotter rules. If we do decide to make orient part of the
        # _base variable assignment, we'll want to figure out how to express that.
        if self.input_format == "wide" and orient in ["h", "y"]:
            self.plot_data = self.plot_data.rename(columns={"x": "y", "y": "x"})
            orig_variables = set(self.variables)
            orig_x = self.variables.pop("x", None)
            orig_y = self.variables.pop("y", None)
            orig_x_type = self.var_types.pop("x", None)
            orig_y_type = self.var_types.pop("y", None)
            if "x" in orig_variables:
                self.variables["y"] = orig_x
                self.var_types["y"] = orig_x_type
            if "y" in orig_variables:
                self.variables["x"] = orig_y
                self.var_types["x"] = orig_x_type

        # Initially there was more special code for wide-form data where plots were
        # multi-colored by default and then either palette or color could be used.
        # We want to provide backwards compatibility for this behavior in a relatively
        # simply way, so we delete the hue information when color is specified.
        if (
            self.input_format == "wide"
            and "hue" in self.variables
            and color is not None
        ):
            self.plot_data.drop("hue", axis=1)
            self.variables.pop("hue")

        # The concept of an "orientation" is important to the original categorical
        # plots, but there's no provision for it in VectorPlotter, so we need it here.
        # Note that it could be useful for the other functions in at least two ways
        # (orienting a univariate distribution plot from long-form data and selecting
        # the aggregation axis in lineplot), so we may want to eventually refactor it.
        self.orient = infer_orient(
            x=self.plot_data.get("x", None),
            y=self.plot_data.get("y", None),
            orient=orient,
            require_numeric=False,
        )

        self.legend = legend

        # Short-circuit in the case of an empty plot
        if not self.has_xy_data:
            return

        # Categorical plots can be "univariate" in which case they get an anonymous
        # category label on the opposite axis. Note: this duplicates code in the core
        # scale_categorical function. We need to do it here because of the next line.
        if self.orient not in self.variables:
            self.variables[self.orient] = None
            self.var_types[self.orient] = "categorical"
            self.plot_data[self.orient] = ""

        # Categorical variables have discrete levels that we need to track
        cat_levels = categorical_order(self.plot_data[self.orient], order)
        self.var_levels[self.orient] = cat_levels
```

**With:**

```python
        self._handle_wide_data(orient, color)
        self.orient = infer_orient(
            x=self.plot_data.get("x", None),
            y=self.plot_data.get("y", None),
            orient=orient,
            require_numeric=False,
        )
        self.legend = legend

        if not self.has_xy_data:
            return

        self._setup_categorical_levels(order)

    def _handle_wide_data(self, orient, color):
        if self.input_format == "wide" and orient in ["h", "y"]:
            self.plot_data = self.plot_data.rename(columns={"x": "y", "y": "x"})
            orig_variables = set(self.variables)
            orig_x = self.variables.pop("x", None)
            orig_y = self.variables.pop("y", None)
            orig_x_type = self.var_types.pop("x", None)
            orig_y_type = self.var_types.pop("y", None)
            if "x" in orig_variables:
                self.variables["y"] = orig_x
                self.var_types["y"] = orig_x_type
            if "y" in orig_variables:
                self.variables["x"] = orig_y
                self.var_types["x"] = orig_y_type

        if (
            self.input_format == "wide"
            and "hue" in self.variables
            and color is not None
        ):
            self.plot_data.drop("hue", axis=1)
            self.variables.pop("hue")

    def _setup_categorical_levels(self, order):
        if self.orient not in self.variables:
            self.variables[self.orient] = None
            self.var_types[self.orient] = "categorical"
            self.plot_data[self.orient] = ""

        cat_levels = categorical_order(self.plot_data[self.orient], order)
        self.var_levels[self.orient] = cat_levels
```

## Apply error

```
search_text not found in seaborn/categorical.py (block 0)
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `seaborn/categorical.py` | 2717 → - | 53 → - | 7.85 → - | 53 → - | 0 → - |

## Diff

*(no diff — patch was not applied)*
