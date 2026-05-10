# Refactor SRP-018 (SRP): The function acts as a 'God Function' for figure-level joint plots, handling...

**Status:** `applied_failed`  
**Branch:** `refactor/SRP-018` -> `main`  
**Head commit:** `11e83875a77e0bb4e9692f7d424a486dbeb007fc`  
**LLM finish:** `FinishReason.STOP` (prompt 4727, completion 2138)  

## Detected issue

- **File**: `seaborn/axisgrid.py`
- **Entity**: `jointplot` (class)
- **Lines (at detection time)**: L1492–L1604
- **Severity**: high
- **Confidence**: detected by 1 scan(s)

**Description.** The function acts as a 'God Function' for figure-level joint plots, handling plot kind selection, extensive argument processing, JointGrid initialization, and orchestration of joint and marginal plotting functions.

**Reasoning.** This function exhibits the 'God Class' (or 'God Function') smell. It is responsible for handling deprecated arguments, validating plot `kind`, creating a colormap, initializing a `JointGrid`, and then orchestrating the calls to various joint and marginal plotting functions based on the chosen `kind`. It also has specific logic for passing `hue` to marginals and handling `bins` for histograms. This function changes for almost any change in joint plotting functionality, API, or argument handling, violating SRP.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 2
- **Files modified** (1): `seaborn/axisgrid.py`

**Summary.** Refactor jointplot to delegate plotting logic to specialized internal functions.

**Rationale.** The jointplot function was a 'God Function' handling argument validation, grid initialization, and complex conditional plotting logic. By extracting the plotting logic into a private helper class or set of functions, we separate the orchestration of the JointGrid from the specific implementation details of each plot kind, adhering to the Single Responsibility Principle.

## Changes overview

_2 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `seaborn/axisgrid.py` (84-line block → 5-line replacement)

**Replaces:**

```python
    # Plot the data using the grid
    if kind.startswith("scatter"):

        joint_kws.setdefault("color", color)
        grid.plot_joint(scatterplot, **joint_kws)

        if grid.hue is None:
            marg_func = histplot
        else:
            marg_func = kdeplot
            marginal_kws.setdefault("warn_singular", False)
            marginal_kws.setdefault("fill", True)

        marginal_kws.setdefault("color", color)
        grid.plot_marginals(marg_func, **marginal_kws)

    elif kind.startswith("hist"):

        # TODO process pair parameters for bins, etc. and pass
        # to both joint and marginal plots

        joint_kws.setdefault("color", color)
        grid.plot_joint(histplot, **joint_kws)

        marginal_kws.setdefault("kde", False)
        marginal_kws.setdefault("color", color)

        marg_x_kws = marginal_kws.copy()
        marg_y_kws = marginal_kws.copy()

        pair_keys = "bins", "binwidth", "binrange"
        for key in pair_keys:
            if isinstance(joint_kws.get(key), tuple):
                x_val, y_val = joint_kws[key]
                marg_x_kws.setdefault(key, x_val)
                marg_y_kws.setdefault(key, y_val)

        histplot(data=data, x=x, hue=hue, **marg_x_kws, ax=grid.ax_marg_x)
        histplot(data=data, y=y, hue=hue, **marg_y_kws, ax=grid.ax_marg_y)

    elif kind.startswith("kde"):

        joint_kws.setdefault("color", color)
        joint_kws.setdefault("warn_singular", False)
        grid.plot_joint(kdeplot, **joint_kws)

        marginal_kws.setdefault("color", color)
        if "fill" in joint_kws:
            marginal_kws.setdefault("fill", joint_kws["fill"])

        grid.plot_marginals(kdeplot, **marginal_kws)

    elif kind.startswith("hex"):

        x_bins = min(_freedman_diaconis_bins(grid.x), 50)
        y_bins = min(_freedman_diaconis_bins(grid.y), 50)
        gridsize = int(np.mean([x_bins, y_bins]))

        joint_kws.setdefault("gridsize", gridsize)
        joint_kws.setdefault("cmap", cmap)
... (24 more line(s) truncated)
```

**With:**

```python
    _plot_jointplot(
        grid, kind, color, cmap,
        joint_kws, marginal_kws,
        data=data, x=x, y=y, hue=hue
    )
```

### 2. EDIT `seaborn/axisgrid.py` (4-line block → 75-line replacement)

**Replaces:**

```python
    return grid


jointplot.__doc__ = """\
```

**With:**

```python
    return grid


def _plot_jointplot(grid, kind, color, cmap, joint_kws, marginal_kws, **data_kws):
    """Helper to dispatch plotting to the correct function."""
    from .relational import scatterplot
    from .regression import regplot, residplot
    from .distributions import histplot, kdeplot, _freedman_diaconis_bins

    data, x, y, hue = data_kws["data"], data_kws["x"], data_kws["y"], data_kws["hue"]

    if kind.startswith("scatter"):
        joint_kws.setdefault("color", color)
        grid.plot_joint(scatterplot, **joint_kws)
        if grid.hue is None:
            marg_func = histplot
        else:
            marg_func = kdeplot
            marginal_kws.setdefault("warn_singular", False)
            marginal_kws.setdefault("fill", True)
        marginal_kws.setdefault("color", color)
        grid.plot_marginals(marg_func, **marginal_kws)

    elif kind.startswith("hist"):
        joint_kws.setdefault("color", color)
        grid.plot_joint(histplot, **joint_kws)
        marginal_kws.setdefault("kde", False)
        marginal_kws.setdefault("color", color)
        marg_x_kws = marginal_kws.copy()
        marg_y_kws = marginal_kws.copy()
        for key in ["bins", "binwidth", "binrange"]:
            if isinstance(joint_kws.get(key), tuple):
                x_val, y_val = joint_kws[key]
                marg_x_kws.setdefault(key, x_val)
                marg_y_kws.setdefault(key, y_val)
        histplot(data=data, x=x, hue=hue, **marg_x_kws, ax=grid.ax_marg_x)
        histplot(data=data, y=y, hue=hue, **marg_y_kws, ax=grid.ax_marg_y)

    elif kind.startswith("kde"):
        joint_kws.setdefault("color", color)
        joint_kws.setdefault("warn_singular", False)
        grid.plot_joint(kdeplot, **joint_kws)
        marginal_kws.setdefault("color", color)
        if "fill" in joint_kws:
            marginal_kws.setdefault("fill", joint_kws["fill"])
        grid.plot_marginals(kdeplot, **marginal_kws)

    elif kind.startswith("hex"):
        x_bins = min(_freedman_diaconis_bins(grid.x), 50)
        y_bins = min(_freedman_diaconis_bins(grid.y), 50)
        gridsize = int(np.mean([x_bins, y_bins]))
        joint_kws.setdefault("gridsize", gridsize)
        joint_kws.setdefault("cmap", cmap)
        grid.plot_joint(plt.hexbin, **joint_kws)
        marginal_kws.setdefault("kde", False)
        marginal_kws.setdefault("color", color)
        grid.plot_marginals(histplot, **marginal_kws)

    elif kind.startswith("reg"):
        marginal_kws.setdefault("color", color)
... (15 more line(s) truncated)
```

## Test results

**FAILED** — 815/823 passed, 1 failed, 1 skipped, 0 errored (duration 41656 ms).

- New failures introduced by this refactor: **1**
- Pre-existing failures (unrelated to this refactor): **0**

New-failure node IDs (first 25):

  - `tests/test_axisgrid.py::TestPairGrid::test_palette`

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
........................................................................ [ 33%]
..............................F
================================== FAILURES ===================================
__________________________ TestPairGrid.test_palette __________________________
tests\test_axisgrid.py:1106: in test_palette
    g = ag.PairGrid(self.df, hue="a", palette="Set2")
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
seaborn\axisgrid.py:1280: in __init__
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
E   _tkinter.TclError: Can't find a usable tk.tcl in the following directories: 
E       C:/Users/User/miniconda3/Library/lib/tcl8.6/tk8.6 C:/Users/User/miniconda3/Library/lib/tk8.6 C:/Users/User/lib/tk8.6 C:/Users/User/lib/tk8.6 C:/Users/lib/tk8.6 C:/Users/User/library
E   
E   C:/Users/User/miniconda3/Library/lib/tk8.6/tk.tcl: couldn't read file "C:/Users/User/miniconda3/Library/lib/tk8.6/scrlbar.tcl": no such file or directory
E   couldn't read file "C:/Users/User/miniconda3/Library/lib/tk8.6/scrlbar.tcl": no such file or directory
E       while executing
E   "source -encoding utf-8 C:/Users/User/miniconda3/Library/lib/tk8.6/scrlbar.tcl"
E       (in namespace eval "::" script line 1)
E       invoked from within
E   "namespace eval :: [list source -encoding utf-8 [file join $::tk_library $file.tcl]]"
E       (procedure "SourceLibFile" line 2)
E       invoked from within
E   "SourceLibFile scrlbar"
E       (in namespace eval "::tk" script line 9)
E       invoked from within
E   "namespace eval ::tk {
E   	SourceLibFile icons
E   	SourceLibFile button
E   	SourceLibFile entry
E   	SourceLibFile listbox
E   	SourceLibFile menu
E   	SourceLibFile panedw..."
E       (file "C:/Users/User/miniconda3/Library/lib/tk8.6/tk.tcl" line 501)
E       invoked from within
E   "source C:/Users/User/miniconda3/Library/lib/tk8.6/tk.tcl"
E       ("uplevel" body line 1)
E       invoked from within
E   "uplevel #0 [list source $file]"
E   
E   
E   This probably means that tk wasn't installed properly.
=========================== short test summary info ===========================
FAILED tests/test_axisgrid.py::TestPairGrid::test_palette - _tkinter.TclError...
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!
1 failed, 815 passed, 1 skipped, 6 xfailed in 40.50s

```

</details>

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `seaborn/axisgrid.py` | 1827 → - | 59 → - | 6.13 → - | 34 → - | 0 → - |

## Diff

```diff
diff --git a/seaborn/axisgrid.py b/seaborn/axisgrid.py
index 17d333b..8707ec6 100644
--- a/seaborn/axisgrid.py
+++ b/seaborn/axisgrid.py
@@ -2250,95 +2250,87 @@ def jointplot(
     if grid.hue is not None:
         marginal_kws.setdefault("legend", False)
 
-    # Plot the data using the grid
-    if kind.startswith("scatter"):
+    _plot_jointplot(
+        grid, kind, color, cmap,
+        joint_kws, marginal_kws,
+        data=data, x=x, y=y, hue=hue
+    )
+
+    # Make the main axes active in the matplotlib state machine
+    plt.sca(grid.ax_joint)
 
+    return grid
+
+
+def _plot_jointplot(grid, kind, color, cmap, joint_kws, marginal_kws, **data_kws):
+    """Helper to dispatch plotting to the correct function."""
+    from .relational import scatterplot
+    from .regression import regplot, residplot
+    from .distributions import histplot, kdeplot, _freedman_diaconis_bins
+
+    data, x, y, hue = data_kws["data"], data_kws["x"], data_kws["y"], data_kws["hue"]
+
+    if kind.startswith("scatter"):
         joint_kws.setdefault("color", color)
         grid.plot_joint(scatterplot, **joint_kws)
-
         if grid.hue is None:
             marg_func = histplot
         else:
             marg_func = kdeplot
             marginal_kws.setdefault("warn_singular", False)
             marginal_kws.setdefault("fill", True)
-
         marginal_kws.setdefault("color", color)
         grid.plot_marginals(marg_func, **marginal_kws)
 
     elif kind.startswith("hist"):
-
-        # TODO process pair parameters for bins, etc. and pass
-        # to both joint and marginal plots
-
         joint_kws.setdefault("color", color)
         grid.plot_joint(histplot, **joint_kws)
-
         marginal_kws.setdefault("kde", False)
         marginal_kws.setdefault("color", color)
-
         marg_x_kws = marginal_kws.copy()
         marg_y_kws = marginal_kws.copy()
-
-        pair_keys = "bins", "binwidth", "binrange"
-        for key in pair_keys:
+        for key in ["bins", "binwidth", "binrange"]:
             if isinstance(joint_kws.get(key), tuple):
                 x_val, y_val = joint_kws[key]
                 marg_x_kws.setdefault(key, x_val)
                 marg_y_kws.setdefault(key, y_val)
-
         histplot(data=data, x=x, hue=hue, **marg_x_kws, ax=grid.ax_marg_x)
         histplot(data=data, y=y, hue=hue, **marg_y_kws, ax=grid.ax_marg_y)
 
     elif kind.startswith("kde"):
-
         joint_kws.setdefault("color", color)
         joint_kws.setdefault("warn_singular", False)
         grid.plot_joint(kdeplot, **joint_kws)
-
         marginal_kws.setdefault("color", color)
         if "fill" in joint_kws:
             marginal_kws.setdefault("fill", joint_kws["fill"])
-
         grid.plot_marginals(kdeplot, **marginal_kws)
 
     elif kind.startswith("hex"):
-
         x_bins = min(_freedman_diaconis_bins(grid.x), 50)
         y_bins = min(_freedman_diaconis_bins(grid.y), 50)
         gridsize = int(np.mean([x_bins, y_bins]))
-
         joint_kws.setdefault("gridsize", gridsize)
         joint_kws.setdefault("cmap", cmap)
         grid.plot_joint(plt.hexbin, **joint_kws)
-
         marginal_kws.setdefault("kde", False)
         marginal_kws.setdefault("color", color)
         grid.plot_marginals(histplot, **marginal_kws)
 
     elif kind.startswith("reg"):
-
         marginal_kws.setdefault("color", color)
         marginal_kws.setdefault("kde", True)
         grid.plot_marginals(histplot, **marginal_kws)
-
         joint_kws.setdefault("color", color)
         grid.plot_joint(regplot, **joint_kws)
 
     elif kind.startswith("resid"):
-
         joint_kws.setdefault("color", color)
         grid.plot_joint(residplot, **joint_kws)
-
-        x, y = grid.ax_joint.collections[0].get_offsets().T
+        x_data, y_data = grid.ax_joint.collections[0].get_offsets().T
         marginal_kws.setdefault("color", color)
-        histplot(x=x, hue=hue, ax=grid.ax_marg_x, **marginal_kws)
-        histplot(y=y, hue=hue, ax=grid.ax_marg_y, **marginal_kws)
-
-    # Make the main axes active in the matplotlib state machine
-    plt.sca(grid.ax_joint)
-
-    return grid
+        histplot(x=x_data, hue=hue, ax=grid.ax_marg_x, **marginal_kws)
+        histplot(y=y_data, hue=hue, ax=grid.ax_marg_y, **marginal_kws)
 
 
 jointplot.__doc__ = """\

```
