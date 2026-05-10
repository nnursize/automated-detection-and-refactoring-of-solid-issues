# Refactor SRP-010 (SRP): Class handles data ingestion, semantic mapping, and Matplotlib axis state man...

**Status:** `applied_failed`  
**Branch:** `refactor/SRP-010` -> `main`  
**Head commit:** `11e83875a77e0bb4e9692f7d424a486dbeb007fc`  
**LLM finish:** `FinishReason.STOP` (prompt 11898, completion 2955)  

## Detected issue

- **File**: `seaborn/_base.py`
- **Entity**: `VectorPlotter` (class)
- **Lines (at detection time)**: L616–L1448
- **Severity**: high
- **Confidence**: detected by 1 scan(s)

**Description.** Class handles data ingestion, semantic mapping, and Matplotlib axis state management.

**Reasoning.** VectorPlotter manages three distinct concerns: 1) Data ingestion and transformation (wide-form vs long-form logic), 2) Semantic mapping (orchestrating Hue, Size, and Style mappings), and 3) Matplotlib integration (attaching to axes, managing unit conversions, and setting scales). These responsibilities are unrelated to the core logic of mapping data to visual properties.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 2
- **Files created** (1): `seaborn/_data.py`
- **Files modified** (1): `seaborn/_base.py`

**Summary.** Refactor VectorPlotter to delegate data ingestion to a new DataManager class.

**Rationale.** The VectorPlotter class is a 'God object' handling data ingestion, semantic mapping, and Matplotlib integration. By extracting the data ingestion logic into a dedicated DataManager class, we reduce the responsibility of VectorPlotter and improve maintainability.

## Changes overview

_2 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `seaborn/_base.py` (169-line block → 10-line replacement)

**Replaces:**

```python
    def assign_variables(self, data=None, variables={}):
        """Define plot variables, optionally using lookup from `data`."""
        x = variables.get("x", None)
        y = variables.get("y", None)

        if x is None and y is None:
            self.input_format = "wide"
            frame, names = self._assign_variables_wideform(data, **variables)
        else:
            # When dealing with long-form input, use the newer PlotData
            # object (internal but introduced for the objects interface)
            # to centralize / standardize data consumption logic.
            self.input_format = "long"
            plot_data = PlotData(data, variables)
            frame = plot_data.frame
            names = plot_data.names

        self.plot_data = frame
        self.variables = names
        self.var_types = {
            v: variable_type(
                frame[v],
                boolean_type="numeric" if v in "xy" else "categorical"
            )
            for v in names
        }

        return self

    def _assign_variables_wideform(self, data=None, **kwargs):
        """Define plot variables given wide-form data.

        Parameters
        ----------
        data : flat vector or collection of vectors
            Data can be a vector or mapping that is coerceable to a Series
            or a sequence- or mapping-based collection of such vectors, or a
            rectangular numpy array, or a Pandas DataFrame.
        kwargs : variable -> data mappings
            Behavior with keyword arguments is currently undefined.

        Returns
        -------
        plot_data : :class:`pandas.DataFrame`
            Long-form data object mapping seaborn variables (x, y, hue, ...)
            to data vectors.
        variables : dict
            Keys are defined seaborn variables; values are names inferred from
            the inputs (or None when no name can be determined).

        """
        # Raise if semantic or other variables are assigned in wide-form mode
        assigned = [k for k, v in kwargs.items() if v is not None]
        if any(assigned):
            s = "s" if len(assigned) > 1 else ""
            err = f"The following variable{s} cannot be assigned with wide-form data: "
            err += ", ".join(f"`{v}`" for v in assigned)
            raise ValueError(err)

        # Determine if the data object actually has any data in it
... (109 more line(s) truncated)
```

**With:**

```python
    def assign_variables(self, data=None, variables={}):
        """Define plot variables, optionally using lookup from `data`."""
        from ._data import DataManager
        manager = DataManager(self.wide_structure, self.flat_structure)
        frame, names, var_types, input_format = manager.assign_variables(data, variables)
        self.plot_data = frame
        self.variables = names
        self.var_types = var_types
        self.input_format = input_format
        return self
```

### 2. CREATE `seaborn/_data.py` (98 line(s))

```python
import pandas as pd
import numpy as np
from collections.abc import Iterable, Mapping, Sequence
from ._base import variable_type

class DataManager:
    """Handles data ingestion and transformation for seaborn plots."""
    
    def __init__(self, wide_structure, flat_structure):
        self.wide_structure = wide_structure
        self.flat_structure = flat_structure

    def assign_variables(self, data=None, variables={}):
        """Define plot variables, optionally using lookup from `data`."""
        x = variables.get("x", None)
        y = variables.get("y", None)

        if x is None and y is None:
            input_format = "wide"
            frame, names = self._assign_variables_wideform(data, **variables)
        else:
            input_format = "long"
            from ._base import PlotData
            plot_data = PlotData(data, variables)
            frame = plot_data.frame
            names = plot_data.names

        var_types = {
            v: variable_type(
                frame[v],
                boolean_type="numeric" if v in "xy" else "categorical"
            )
            for v in names
        }
        return frame, names, var_types, input_format

    def _assign_variables_wideform(self, data=None, **kwargs):
        assigned = [k for k, v in kwargs.items() if v is not None]
        if any(assigned):
            s = "s" if len(assigned) > 1 else ""
            err = f"The following variable{s} cannot be assigned with wide-form data: "
            err += ", ".join(f"`{v}`" for v in assigned)
            raise ValueError(err)

        empty = data is None or not len(data)
        if isinstance(data, dict):
            values = data.values()
        else:
            values = np.atleast_1d(np.asarray(data, dtype=object))
        flat = not any(isinstance(v, Iterable) and not isinstance(v, (str, bytes)) for v in values)

        if empty:
            return pd.DataFrame(), {}
        elif flat:
            flat_data = pd.Series(data).copy()
            names = {"@values": flat_data.name, "@index": flat_data.index.name}
            plot_data = {}
            variables = {}
            for var in ["x", "y"]:
                if var in self.flat_structure:
... (38 more line(s) truncated)
```

## Test results

**FAILED** — 754/762 passed, 1 failed, 1 skipped, 0 errored (duration 20941 ms).

- New failures introduced by this refactor: **1**
- Pre-existing failures (unrelated to this refactor): **0**

New-failure node IDs (first 25):

  - `tests/test_axisgrid.py::TestFacetGrid::test_normal_axes`

Command: `C:\Users\User\Desktop\SDP-Codex\S1-T7-Okeyish\refactor_workspaces\seaborn-master\.venv\Scripts\python.exe -m pytest --tb=short -q --no-header -p no:cacheprovider -x --json-report --json-report-file=C:\Users\User\Desktop\SDP-Codex\S1-T7-Okeyish\refactor_workspaces\seaborn-master\.pytest_report.json`

<details><summary>Output tail</summary>

```
....................................s................................... [  3%]
.................................x............x...x................x.x.. [  6%]
........................................................................ [  9%]
........................................................................ [ 12%]
........................................................................ [ 15%]
........................................................................ [ 18%]
.....................................................................x.. [ 21%]
........................................................................ [ 24%]
........................................................................ [ 27%]
........................................................................ [ 30%]
.........................................F
================================== FAILURES ===================================
_______________________ TestFacetGrid.test_normal_axes ________________________
tests\test_axisgrid.py:143: in test_normal_axes
    g = ag.FacetGrid(self.df, col="a", row="c")
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
seaborn\axisgrid.py:453: in __init__
    fig = plt.figure(figsize=figsize)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^
.venv\Lib\site-packages\matplotlib\pyplot.py:1041: in figure
    manager = new_figure_manager(
.venv\Lib\site-packages\matplotlib\pyplot.py:551: in new_figure_manager
    return _get_backend_mod().new_figure_manager(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.venv\Lib\site-packages\matplotlib\backend_bases.py:3504: in new_figure_manager
    return cls.new_figure_manager_given_figure(num, fig)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.venv\Lib\site-packages\matplotlib\backend_bases.py:3509: in new_figure_manager_given_figure
    return cls.FigureCanvas.new_manager(figure, num)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.venv\Lib\site-packages\matplotlib\backend_bases.py:1785: in new_manager
    return cls.manager_class.create_with_canvas(cls, figure, num)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.venv\Lib\site-packages\matplotlib\backends\_backend_tk.py:535: in create_with_canvas
    window = tk.Tk(className="matplotlib")
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Users\User\miniconda3\Lib\tkinter\__init__.py:2326: in __init__
    self.tk = _tkinter.create(screenName, baseName, className, interactive, wantobjects, useTk, sync, use)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   _tkinter.TclError: Can't find a usable init.tcl in the following directories: 
E       C:/Users/User/miniconda3/Library/lib/tcl8.6 C:/Users/User/lib/tcl8.6 C:/Users/lib/tcl8.6 C:/Users/User/library C:/Users/library C:/Users/tcl8.6.12/library C:/tcl8.6.12/library
E   
E   C:/Users/User/miniconda3/Library/lib/tcl8.6/init.tcl: couldn't read file "C:/Users/User/miniconda3/Library/lib/tcl8.6/init.tcl": No error
E   couldn't read file "C:/Users/User/miniconda3/Library/lib/tcl8.6/init.tcl": No error
E       while executing
E   "source C:/Users/User/miniconda3/Library/lib/tcl8.6/init.tcl"
E       ("uplevel" body line 1)
E       invoked from within
E   "uplevel #0 [list source $tclfile]"
E   
E   
E   This probably means that Tcl wasn't installed properly.
=========================== short test summary info ===========================
FAILED tests/test_axisgrid.py::TestFacetGrid::test_normal_axes - _tkinter.Tcl...
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!
1 failed, 754 passed, 1 skipped, 6 xfailed in 19.81s

```

</details>

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `seaborn/_base.py` | 1146 → - | 47 → - | 6.84 → - | 28 → - | 0 → - |

## Diff

```diff
diff --git a/seaborn/_base.py b/seaborn/_base.py
index 1eb0c96..e0cc1e5 100644
--- a/seaborn/_base.py
+++ b/seaborn/_base.py
@@ -665,174 +665,15 @@ class VectorPlotter:
 
     def assign_variables(self, data=None, variables={}):
         """Define plot variables, optionally using lookup from `data`."""
-        x = variables.get("x", None)
-        y = variables.get("y", None)
-
-        if x is None and y is None:
-            self.input_format = "wide"
-            frame, names = self._assign_variables_wideform(data, **variables)
-        else:
-            # When dealing with long-form input, use the newer PlotData
-            # object (internal but introduced for the objects interface)
-            # to centralize / standardize data consumption logic.
-            self.input_format = "long"
-            plot_data = PlotData(data, variables)
-            frame = plot_data.frame
-            names = plot_data.names
-
+        from ._data import DataManager
+        manager = DataManager(self.wide_structure, self.flat_structure)
+        frame, names, var_types, input_format = manager.assign_variables(data, variables)
         self.plot_data = frame
         self.variables = names
-        self.var_types = {
-            v: variable_type(
-                frame[v],
-                boolean_type="numeric" if v in "xy" else "categorical"
-            )
-            for v in names
-        }
-
+        self.var_types = var_types
+        self.input_format = input_format
         return self
 
-    def _assign_variables_wideform(self, data=None, **kwargs):
-        """Define plot variables given wide-form data.
-
-        Parameters
-        ----------
-        data : flat vector or collection of vectors
-            Data can be a vector or mapping that is coerceable to a Series
-            or a sequence- or mapping-based collection of such vectors, or a
-            rectangular numpy array, or a Pandas DataFrame.
-        kwargs : variable -> data mappings
-            Behavior with keyword arguments is currently undefined.
-
-        Returns
-        -------
-        plot_data : :class:`pandas.DataFrame`
-            Long-form data object mapping seaborn variables (x, y, hue, ...)
-            to data vectors.
-        variables : dict
-            Keys are defined seaborn variables; values are names inferred from
-            the inputs (or None when no name can be determined).
-
-        """
-        # Raise if semantic or other variables are assigned in wide-form mode
-        assigned = [k for k, v in kwargs.items() if v is not None]
-        if any(assigned):
-            s = "s" if len(assigned) > 1 else ""
-            err = f"The following variable{s} cannot be assigned with wide-form data: "
-            err += ", ".join(f"`{v}`" for v in assigned)
-            raise ValueError(err)
-
-        # Determine if the data object actually has any data in it
-        empty = data is None or not len(data)
-
-        # Then, determine if we have "flat" data (a single vector)
-        if isinstance(data, dict):
-            values = data.values()
-        else:
-            values = np.atleast_1d(np.asarray(data, dtype=object))
-        flat = not any(
-            isinstance(v, Iterable) and not isinstance(v, (str, bytes))
-            for v in values
-        )
-
-        if empty:
-
-            # Make an object with the structure of plot_data, but empty
-            plot_data = pd.DataFrame()
-            variables = {}
-
-        elif flat:
-
-            # Handle flat data by converting to pandas Series and using the
-            # index and/or values to define x and/or y
-            # (Could be accomplished with a more general to_series() interface)
-            flat_data = pd.Series(data).copy()
-            names = {
-                "@values": flat_data.name,
-                "@index": flat_data.index.name
-            }
-
-            plot_data = {}
-            variables = {}
-
-            for var in ["x", "y"]:
-                if var in self.flat_structure:
-                    attr = self.flat_structure[var]
-                    plot_data[var] = getattr(flat_data, attr[1:])
-                    variables[var] = names[self.flat_structure[var]]
-
-            plot_data = pd.DataFrame(plot_data)
-
-        else:
-
-            # Otherwise assume we have some collection of vectors.
-
-            # Handle Python sequences such that entries end up in the columns,
-            # not in the rows, of the intermediate wide DataFrame.
-            # One way to accomplish this is to convert to a dict of Series.
-            if isinstance(data, Sequence):
-                data_dict = {}
-                for i, var in enumerate(data):
-                    key = getattr(var, "name", i)
-                    # TODO is there a safer/more generic way to ensure Series?
-                    # sort of like np.asarray, but for pandas?
-                    data_dict[key] = pd.Series(var)
-
-                data = data_dict
-
-            # Pandas requires that dict values either be Series objects
-            # or all have the same length, but we want to allow "ragged" inputs
-            if isinstance(data, Mapping):
-                data = {key: pd.Series(val) for key, val in data.items()}
-
-            # Otherwise, delegate to the pandas DataFrame constructor
-            # This is where we'd prefer to use a general interface that says
-            # "give me this data as a pandas DataFrame", so we can accept
-            # DataFrame objects from other libraries
-            wide_data = pd.DataFrame(data, copy=True)
-
-            # At this point we should reduce the dataframe to numeric cols
-            numeric_cols = [
-                k for k, v in wide_data.items() if variable_type(v) == "numeric"
-            ]
-            wide_data = wide_data[numeric_cols]
-
-            # Now melt the data to long form
-            melt_kws = {"var_name": "@columns", "value_name": "@values"}
-            use_index = "@index" in self.wide_structure.values()
-            if use_index:
-                melt_kws["id_vars"] = "@index"
-                try:
-                    orig_categories = wide_data.columns.categories
-                    orig_ordered = wide_data.columns.ordered
-                except AttributeError:
-                    category_columns = False
-                else:
-                    category_columns = True
-                wide_data["@index"] = wide_data.index.to_series()
-
-            plot_data = wide_data.melt(**melt_kws)
-
-            if use_index and category_columns:
-                plot_data["@columns"] = pd.Categorical(plot_data["@columns"],
-                                                       orig_categories,
-                                                       orig_ordered)
-
-            # Assign names corresponding to plot semantics
-            for var, attr in self.wide_structure.items():
-                plot_data[var] = plot_data[attr]
-
-            # Define the variable names
-            variables = {}
-            for var, attr in self.wide_structure.items():
-                obj = getattr(wide_data, attr[1:])
-                variables[var] = getattr(obj, "name", None)
-
-            # Remove redundant columns from plot_data
-            plot_data = plot_data[list(variables)]
-
-        return plot_data, variables
-
     def map_hue(self, palette=None, order=None, norm=None, saturation=1):
         mapping = HueMapping(self, palette, order, norm, saturation)
         self._hue_map = mapping
diff --git a/seaborn/_data.py b/seaborn/_data.py
new file mode 100644
index 0000000..0000000
--- /dev/null
+++ b/seaborn/_data.py
@@ -0,0 +1,98 @@
+import pandas as pd
+import numpy as np
+from collections.abc import Iterable, Mapping, Sequence
+from ._base import variable_type
+
+class DataManager:
+    """Handles data ingestion and transformation for seaborn plots."""
+    
+    def __init__(self, wide_structure, flat_structure):
+        self.wide_structure = wide_structure
+        self.flat_structure = flat_structure
+
+    def assign_variables(self, data=None, variables={}):
+        """Define plot variables, optionally using lookup from `data`."""
+        x = variables.get("x", None)
+        y = variables.get("y", None)
+
+        if x is None and y is None:
+            input_format = "wide"
+            frame, names = self._assign_variables_wideform(data, **variables)
+        else:
+            input_format = "long"
+            from ._base import PlotData
+            plot_data = PlotData(data, variables)
+            frame = plot_data.frame
+            names = plot_data.names
+
+        var_types = {
+            v: variable_type(
+                frame[v],
+                boolean_type="numeric" if v in "xy" else "categorical"
+            )
+            for v in names
+        }
+        return frame, names, var_types, input_format
+
+    def _assign_variables_wideform(self, data=None, **kwargs):
+        assigned = [k for k, v in kwargs.items() if v is not None]
+        if any(assigned):
+            s = "s" if len(assigned) > 1 else ""
+            err = f"The following variable{s} cannot be assigned with wide-form data: "
+            err += ", ".join(f"`{v}`" for v in assigned)
+            raise ValueError(err)
+
+        empty = data is None or not len(data)
+        if isinstance(data, dict):
+            values = data.values()
+        else:
+            values = np.atleast_1d(np.asarray(data, dtype=object))
+        flat = not any(isinstance(v, Iterable) and not isinstance(v, (str, bytes)) for v in values)
+
+        if empty:
+            return pd.DataFrame(), {}
+        elif flat:
+            flat_data = pd.Series(data).copy()
+            names = {"@values": flat_data.name, "@index": flat_data.index.name}
+            plot_data = {}
+            variables = {}
+            for var in ["x", "y"]:
+                if var in self.flat_structure:
+                    attr = self.flat_structure[var]
+                    plot_data[var] = getattr(flat_data, attr[1:])
+                    variables[var] = names[self.flat_structure[var]]
+            return pd.DataFrame(plot_data), variables
+        else:
+            if isinstance(data, Sequence):
+                data_dict = {}
+                for i, var in enumerate(data):
+                    key = getattr(var, "name", i)
+                    data_dict[key] = pd.Series(var)
+                data = data_dict
+            if isinstance(data, Mapping):
+                data = {key: pd.Series(val) for key, val in data.items()}
+            wide_data = pd.DataFrame(data, copy=True)
+            numeric_cols = [k for k, v in wide_data.items() if variable_type(v) == "numeric"]
+            wide_data = wide_data[numeric_cols]
+            melt_kws = {"var_name": "@columns", "value_name": "@values"}
+            use_index = "@index" in self.wide_structure.values()
+            if use_index:
+                melt_kws["id_vars"] = "@index"
+                try:
+                    orig_categories = wide_data.columns.categories
+                    orig_ordered = wide_data.columns.ordered
+                    category_columns = True
+                except AttributeError:
+                    category_columns = False
+                wide_data["@index"] = wide_data.index.to_series()
+            plot_data = wide_data.melt(**melt_kws)
+            if use_index and category_columns:
+                plot_data["@columns"] = pd.Categorical(plot_data["@columns"], orig_categories, orig_ordered)
+            for var, attr in self.wide_structure.items():
+                plot_data[var] = plot_data[attr]
+            variables = {}
+            for var, attr in self.wide_structure.items():
+                obj = getattr(wide_data, attr[1:])
+                variables[var] = getattr(obj, "name", None)
+            plot_data = plot_data[list(variables)]
+            return plot_data, variables
\ No newline at end of file

```
