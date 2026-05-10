# Refactor SRP-005 (SRP): Mixes data normalization, statistical clustering, and complex layout management.

**Status:** `applied_failed`  
**Branch:** `refactor/SRP-005` -> `main`  
**Head commit:** `11e83875a77e0bb4e9692f7d424a486dbeb007fc`  
**LLM finish:** `FinishReason.STOP` (prompt 13953, completion 1227)  

## Detected issue

- **File**: `seaborn/matrix.py`
- **Entity**: `ClusterGrid` (class)
- **Lines (at detection time)**: L696–L1143
- **Severity**: medium
- **Confidence**: detected by 4 scan(s)

**Description.** Mixes data normalization, statistical clustering, and complex layout management.

**Reasoning.** The class handles data transformation (z-scoring, standard scaling), statistical clustering (dendrogram calculation via scipy), and complex multi-axes layout management. These are three distinct responsibilities: data engineering, statistical analysis, and UI layout, each of which could change independently.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 2
- **Files modified** (1): `seaborn/matrix.py`

**Summary.** Extract data transformation logic from ClusterGrid into a DataTransformer class.

**Rationale.** The ClusterGrid class was violating SRP by handling data normalization (z-score, standard scaling) alongside layout management. Extracting these methods into a dedicated DataTransformer class separates data engineering from UI layout concerns.

## Changes overview

_2 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `seaborn/matrix.py` (83-line block → 45-line replacement)

**Replaces:**

```python
    def format_data(self, data, pivot_kws, z_score=None,
                    standard_scale=None):
        """Extract variables from data or use directly."""

        # Either the data is already in 2d matrix format, or need to do a pivot
        if pivot_kws is not None:
            data2d = data.pivot(**pivot_kws)
        else:
            data2d = data

        if z_score is not None and standard_scale is not None:
            raise ValueError(
                'Cannot perform both z-scoring and standard-scaling on data')

        if z_score is not None:
            data2d = self.z_score(data2d, z_score)
        if standard_scale is not None:
            data2d = self.standard_scale(data2d, standard_scale)
        return data2d

    @staticmethod
    def z_score(data2d, axis=1):
        """Standarize the mean and variance of the data axis

        Parameters
        ----------
        data2d : pandas.DataFrame
            Data to normalize
        axis : int
            Which axis to normalize across. If 0, normalize across rows, if 1,
            normalize across columns.

        Returns
        -------
        normalized : pandas.DataFrame
            Noramlized data with a mean of 0 and variance of 1 across the
            specified axis.
        """
        if axis == 1:
            z_scored = data2d
        else:
            z_scored = data2d.T

        z_scored = (z_scored - z_scored.mean()) / z_scored.std()

        if axis == 1:
            return z_scored
        else:
            return z_scored.T

    @staticmethod
    def standard_scale(data2d, axis=1):
        """Divide the data by the difference between the max and min

        Parameters
        ----------
        data2d : pandas.DataFrame
            Data to normalize
        axis : int
            Which axis to normalize across. If 0, normalize across rows, if 1,
... (23 more line(s) truncated)
```

**With:**

```python
class _DataTransformer:
    """Helper class to normalize and scale data for clustering."""

    @staticmethod
    def z_score(data2d, axis=1):
        """Standarize the mean and variance of the data axis."""
        if axis == 1:
            z_scored = data2d
        else:
            z_scored = data2d.T

        z_scored = (z_scored - z_scored.mean()) / z_scored.std()

        return z_scored if axis == 1 else z_scored.T

    @staticmethod
    def standard_scale(data2d, axis=1):
        """Divide the data by the difference between the max and min."""
        if axis == 1:
            standardized = data2d
        else:
            standardized = data2d.T

        subtract = standardized.min()
        standardized = (standardized - subtract) / (
            standardized.max() - standardized.min())

        return standardized if axis == 1 else standardized.T

    def transform(self, data, pivot_kws, z_score=None, standard_scale=None):
        """Extract variables from data and apply normalization."""
        if pivot_kws is not None:
            data2d = data.pivot(**pivot_kws)
        else:
            data2d = data

        if z_score is not None and standard_scale is not None:
            raise ValueError(
                'Cannot perform both z-scoring and standard-scaling on data')

        if z_score is not None:
            data2d = self.z_score(data2d, z_score)
        if standard_scale is not None:
            data2d = self.standard_scale(data2d, standard_scale)
        return data2d
```

### 2. EDIT `seaborn/matrix.py` (2-line block → 3-line replacement)

**Replaces:**

```python
        self.data2d = self.format_data(self.data, pivot_kws, z_score,
                                       standard_scale)
```

**With:**

```python
        self.data2d = _DataTransformer().transform(
            self.data, pivot_kws, z_score, standard_scale
        )
```

## Test results

**FAILED** — 169/176 passed, 1 failed, 1 skipped, 0 errored (duration 6245 ms).

- New failures introduced by this refactor: **1**
- Pre-existing failures (unrelated to this refactor): **0**

New-failure node IDs (first 25):

  - `tests/_core/test_plot.py::TestPlotting::test_show`

Command: `C:\Users\User\Desktop\SDP-Codex\S1-T7-Okeyish\refactor_workspaces\seaborn-master\.venv\Scripts\python.exe -m pytest --tb=short -q --no-header -p no:cacheprovider -x --json-report --json-report-file=C:\Users\User\Desktop\SDP-Codex\S1-T7-Okeyish\refactor_workspaces\seaborn-master\.pytest_report.json`

<details><summary>Output tail</summary>

```
....................................s................................... [  3%]
.................................x............x...x................x.x.. [  6%]
...............................F
================================== FAILURES ===================================
___________________________ TestPlotting.test_show ____________________________
tests\_core\test_plot.py:1060: in test_show
    out = p.show(block=False)
          ^^^^^^^^^^^^^^^^^^^
seaborn\_core\plot.py:925: in show
    self.plot(pyplot=True).show(**kwargs)
    ^^^^^^^^^^^^^^^^^^^^^^
seaborn\_core\plot.py:932: in plot
    return self._plot(pyplot)
           ^^^^^^^^^^^^^^^^^^
seaborn\_core\plot.py:943: in _plot
    plotter._setup_figure(self, common, layers)
seaborn\_core\plot.py:1127: in _setup_figure
    self._figure = subplots.init_figure(
seaborn\_core\subplots.py:185: in init_figure
    figure = plt.figure(**figure_kws)
             ^^^^^^^^^^^^^^^^^^^^^^^^
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
E   _tkinter.TclError: Can't find a usable tk.tcl in the following directories: 
E       C:/Users/User/miniconda3/Library/lib/tcl8.6/tk8.6 C:/Users/User/miniconda3/Library/lib/tk8.6 C:/Users/User/lib/tk8.6 C:/Users/User/lib/tk8.6 C:/Users/lib/tk8.6 C:/Users/User/library
E   
E   C:/Users/User/miniconda3/Library/lib/tk8.6/tk.tcl: couldn't read file "C:/Users/User/miniconda3/Library/lib/tk8.6/ttk/vistaTheme.tcl": no such file or directory
E   couldn't read file "C:/Users/User/miniconda3/Library/lib/tk8.6/ttk/vistaTheme.tcl": no such file or directory
E       while executing
E   "source -encoding utf-8 C:/Users/User/miniconda3/Library/lib/tk8.6/ttk/vistaTheme.tcl"
E       ("uplevel" body line 1)
E       invoked from within
E   "uplevel #0 [list source -encoding utf-8 [file join $library $script]]"
E       (procedure "ttk::LoadThemes" line 18)
E       invoked from within
E   "ttk::LoadThemes"
E       (file "C:/Users/User/miniconda3/Library/lib/tk8.6/ttk/ttk.tcl" line 144)
E       invoked from within
E   "source -encoding utf-8 C:/Users/User/miniconda3/Library/lib/tk8.6/ttk/ttk.tcl"
E       ("uplevel" body line 1)
E       invoked from within
E   "uplevel \#0 [list source -encoding utf-8 $::ttk::library/ttk.tcl]"
E       (file "C:/Users/User/miniconda3/Library/lib/tk8.6/tk.tcl" line 706)
E       invoked from within
E   "source C:/Users/User/miniconda3/Library/lib/tk8.6/tk.tcl"
E       ("uplevel" body line 1)
E       invoked from within
E   "uplevel #0 [list source $file]"
E   
E   
E   This probably means that tk wasn't installed properly.
=========================== short test summary info ===========================
FAILED tests/_core/test_plot.py::TestPlotting::test_show - _tkinter.TclError:...
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!
1 failed, 169 passed, 1 skipped, 5 xfailed in 5.20s

```

</details>

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `seaborn/matrix.py` | 978 → - | 31 → - | 5.76 → - | 22 → - | 20.95 → - |

## Diff

```diff
diff --git a/seaborn/matrix.py b/seaborn/matrix.py
index 4e96132..40b01ad 100644
--- a/seaborn/matrix.py
+++ b/seaborn/matrix.py
@@ -707,8 +707,9 @@ class ClusterGrid(Grid):
         else:
             self.data = pd.DataFrame(data)
 
-        self.data2d = self.format_data(self.data, pivot_kws, z_score,
-                                       standard_scale)
+        self.data2d = _DataTransformer().transform(
+            self.data, pivot_kws, z_score, standard_scale
+        )
 
         self.mask = _matrix_mask(self.data2d, mask)
 
@@ -813,44 +814,12 @@ class ClusterGrid(Grid):
 
         return colors, labels
 
-    def format_data(self, data, pivot_kws, z_score=None,
-                    standard_scale=None):
-        """Extract variables from data or use directly."""
-
-        # Either the data is already in 2d matrix format, or need to do a pivot
-        if pivot_kws is not None:
-            data2d = data.pivot(**pivot_kws)
-        else:
-            data2d = data
-
-        if z_score is not None and standard_scale is not None:
-            raise ValueError(
-                'Cannot perform both z-scoring and standard-scaling on data')
-
-        if z_score is not None:
-            data2d = self.z_score(data2d, z_score)
-        if standard_scale is not None:
-            data2d = self.standard_scale(data2d, standard_scale)
-        return data2d
+class _DataTransformer:
+    """Helper class to normalize and scale data for clustering."""
 
     @staticmethod
     def z_score(data2d, axis=1):
-        """Standarize the mean and variance of the data axis
-
-        Parameters
-        ----------
-        data2d : pandas.DataFrame
-            Data to normalize
-        axis : int
-            Which axis to normalize across. If 0, normalize across rows, if 1,
-            normalize across columns.
-
-        Returns
-        -------
-        normalized : pandas.DataFrame
-            Noramlized data with a mean of 0 and variance of 1 across the
-            specified axis.
-        """
+        """Standarize the mean and variance of the data axis."""
         if axis == 1:
             z_scored = data2d
         else:
@@ -858,31 +827,11 @@ class ClusterGrid(Grid):
 
         z_scored = (z_scored - z_scored.mean()) / z_scored.std()
 
-        if axis == 1:
-            return z_scored
-        else:
-            return z_scored.T
+        return z_scored if axis == 1 else z_scored.T
 
     @staticmethod
     def standard_scale(data2d, axis=1):
-        """Divide the data by the difference between the max and min
-
-        Parameters
-        ----------
-        data2d : pandas.DataFrame
-            Data to normalize
-        axis : int
-            Which axis to normalize across. If 0, normalize across rows, if 1,
-            normalize across columns.
-
-        Returns
-        -------
-        standardized : pandas.DataFrame
-            Noramlized data with a mean of 0 and variance of 1 across the
-            specified axis.
-
-        """
-        # Normalize these values to range from 0 to 1
+        """Divide the data by the difference between the max and min."""
         if axis == 1:
             standardized = data2d
         else:
@@ -892,10 +841,24 @@ class ClusterGrid(Grid):
         standardized = (standardized - subtract) / (
             standardized.max() - standardized.min())
 
-        if axis == 1:
-            return standardized
+        return standardized if axis == 1 else standardized.T
+
+    def transform(self, data, pivot_kws, z_score=None, standard_scale=None):
+        """Extract variables from data and apply normalization."""
+        if pivot_kws is not None:
+            data2d = data.pivot(**pivot_kws)
         else:
-            return standardized.T
+            data2d = data
+
+        if z_score is not None and standard_scale is not None:
+            raise ValueError(
+                'Cannot perform both z-scoring and standard-scaling on data')
+
+        if z_score is not None:
+            data2d = self.z_score(data2d, z_score)
+        if standard_scale is not None:
+            data2d = self.standard_scale(data2d, standard_scale)
+        return data2d
 
     def dim_ratios(self, colors, dendrogram_ratio, colors_ratio):
         """Get the proportions of the figure taken up by each axes."""

```
