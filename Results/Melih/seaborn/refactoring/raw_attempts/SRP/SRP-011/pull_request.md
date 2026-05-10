# Refactor SRP-011 (SRP): Class mixes data normalization/color mapping logic with rendering.

**Status:** `applied_failed`  
**Branch:** `refactor/SRP-011` -> `main`  
**Head commit:** `11e83875a77e0bb4e9692f7d424a486dbeb007fc`  
**LLM finish:** `FinishReason.STOP` (prompt 13967, completion 5121)  

## Detected issue

- **File**: `seaborn/matrix.py`
- **Entity**: `_HeatMapper` (class)
- **Lines (at detection time)**: L97–L352
- **Severity**: medium
- **Confidence**: detected by 2 scan(s)

**Description.** Class mixes data normalization/color mapping logic with rendering.

**Reasoning.** The class is responsible for data-level preprocessing (masking, calculating vmin/vmax, recentering divergent colormaps in _determine_cmap_params) and the actual drawing on the Axes (plot, _annotate_heatmap). Decisions about data distribution and color scales are business/logic concerns that should be decoupled from the Matplotlib drawing commands.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 3
- **Files modified** (1): `seaborn/matrix.py`

**Summary.** Extract heatmap data processing logic into a separate _HeatmapData class

**Rationale.** The _HeatMapper class was violating the Single Responsibility Principle by handling both data preprocessing (normalization, colormap determination, masking) and rendering. Extracting the data-level logic into a dedicated _HeatmapData class decouples these concerns, making the code easier to maintain and test.

## Changes overview

_3 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `seaborn/matrix.py` (151-line block → 128-line replacement)

**Replaces:**

```python
class _HeatMapper:
    """Draw a heatmap plot of a matrix with nice labels and colormaps."""

    def __init__(self, data, vmin, vmax, cmap, center, robust, annot, fmt,
                 annot_kws, cbar, cbar_kws,
                 xticklabels=True, yticklabels=True, mask=None):
        """Initialize the plotting object."""
        # We always want to have a DataFrame with semantic information
        # and an ndarray to pass to matplotlib
        if isinstance(data, pd.DataFrame):
            plot_data = data.values
        else:
            plot_data = np.asarray(data)
            data = pd.DataFrame(plot_data)

        # Validate the mask and convert to DataFrame
        mask = _matrix_mask(data, mask)

        plot_data = np.ma.masked_where(np.asarray(mask), plot_data)

        # Get good names for the rows and columns
        xtickevery = 1
        if isinstance(xticklabels, int):
            xtickevery = xticklabels
            xticklabels = _index_to_ticklabels(data.columns)
        elif xticklabels is True:
            xticklabels = _index_to_ticklabels(data.columns)
        elif xticklabels is False:
            xticklabels = []

        ytickevery = 1
        if isinstance(yticklabels, int):
            ytickevery = yticklabels
            yticklabels = _index_to_ticklabels(data.index)
        elif yticklabels is True:
            yticklabels = _index_to_ticklabels(data.index)
        elif yticklabels is False:
            yticklabels = []

        if not len(xticklabels):
            self.xticks = []
            self.xticklabels = []
        elif isinstance(xticklabels, str) and xticklabels == "auto":
            self.xticks = "auto"
            self.xticklabels = _index_to_ticklabels(data.columns)
        else:
            self.xticks, self.xticklabels = self._skip_ticks(xticklabels,
                                                             xtickevery)

        if not len(yticklabels):
            self.yticks = []
            self.yticklabels = []
        elif isinstance(yticklabels, str) and yticklabels == "auto":
            self.yticks = "auto"
            self.yticklabels = _index_to_ticklabels(data.index)
        else:
            self.yticks, self.yticklabels = self._skip_ticks(yticklabels,
                                                             ytickevery)

        # Get good names for the axis labels
... (91 more line(s) truncated)
```

**With:**

```python
class _HeatmapData:
    """Data processing for heatmap plots."""
    def __init__(self, data, vmin, vmax, cmap, center, robust, annot, fmt,
                 annot_kws, cbar, cbar_kws, xticklabels, yticklabels, mask):
        if isinstance(data, pd.DataFrame):
            plot_data = data.values
        else:
            plot_data = np.asarray(data)
            data = pd.DataFrame(plot_data)

        mask = _matrix_mask(data, mask)
        plot_data = np.ma.masked_where(np.asarray(mask), plot_data)

        self.data = data
        self.plot_data = plot_data
        self.fmt = fmt
        self.annot_kws = {} if annot_kws is None else annot_kws.copy()
        self.cbar = cbar
        self.cbar_kws = {} if cbar_kws is None else cbar_kws.copy()

        self._setup_labels(xticklabels, yticklabels)
        self._determine_cmap_params(plot_data, vmin, vmax, cmap, center, robust)
        self._setup_annotations(annot, plot_data)

    def _setup_labels(self, xticklabels, yticklabels):
        xtickevery = 1
        if isinstance(xticklabels, int):
            xtickevery = xticklabels
            xticklabels = _index_to_ticklabels(self.data.columns)
        elif xticklabels is True:
            xticklabels = _index_to_ticklabels(self.data.columns)
        elif xticklabels is False:
            xticklabels = []

        ytickevery = 1
        if isinstance(yticklabels, int):
            ytickevery = yticklabels
            yticklabels = _index_to_ticklabels(self.data.index)
        elif yticklabels is True:
            yticklabels = _index_to_ticklabels(self.data.index)
        elif yticklabels is False:
            yticklabels = []

        if not len(xticklabels):
            self.xticks = []
            self.xticklabels = []
        elif isinstance(xticklabels, str) and xticklabels == "auto":
            self.xticks = "auto"
            self.xticklabels = _index_to_ticklabels(self.data.columns)
        else:
            self.xticks, self.xticklabels = _HeatMapper._skip_ticks(xticklabels, xtickevery)

        if not len(yticklabels):
            self.yticks = []
            self.yticklabels = []
        elif isinstance(yticklabels, str) and yticklabels == "auto":
            self.yticks = "auto"
            self.yticklabels = _index_to_ticklabels(self.data.index)
        else:
            self.yticks, self.yticklabels = _HeatMapper._skip_ticks(yticklabels, ytickevery)
... (68 more line(s) truncated)
```

### 2. EDIT `seaborn/matrix.py` (17-line block → 18-line replacement)

**Replaces:**

```python
    def _annotate_heatmap(self, ax, mesh):
        """Add textual labels with the value in each cell."""
        mesh.update_scalarmappable()
        height, width = self.annot_data.shape
        xpos, ypos = np.meshgrid(np.arange(width) + .5, np.arange(height) + .5)
        for x, y, m, color, val in zip(xpos.flat, ypos.flat,
                                       mesh.get_array().flat, mesh.get_facecolors(),
                                       self.annot_data.flat):
            if m is not np.ma.masked:
                lum = relative_luminance(color)
                text_color = ".15" if lum > .408 else "w"
                annotation = ("{:" + self.fmt + "}").format(val)
                text_kwargs = dict(color=text_color, ha="center", va="center")
                text_kwargs.update(self.annot_kws)
                ax.text(x, y, annotation, **text_kwargs)

    def _skip_ticks(self, labels, tickevery):
```

**With:**

```python
    def _annotate_heatmap(self, ax, mesh):
        """Add textual labels with the value in each cell."""
        mesh.update_scalarmappable()
        height, width = self.data_manager.annot_data.shape
        xpos, ypos = np.meshgrid(np.arange(width) + .5, np.arange(height) + .5)
        for x, y, m, color, val in zip(xpos.flat, ypos.flat,
                                       mesh.get_array().flat, mesh.get_facecolors(),
                                       self.data_manager.annot_data.flat):
            if m is not np.ma.masked:
                lum = relative_luminance(color)
                text_color = ".15" if lum > .408 else "w"
                annotation = ("{:" + self.data_manager.fmt + "}").format(val)
                text_kwargs = dict(color=text_color, ha="center", va="center")
                text_kwargs.update(self.data_manager.annot_kws)
                ax.text(x, y, annotation, **text_kwargs)

    @staticmethod
    def _skip_ticks(labels, tickevery):
```

### 3. EDIT `seaborn/matrix.py` (59-line block → 59-line replacement)

**Replaces:**

```python
    def plot(self, ax, cax, kws):
        """Draw the heatmap on the provided Axes."""
        # Remove all the Axes spines
        despine(ax=ax, left=True, bottom=True)

        # setting vmin/vmax in addition to norm is deprecated
        # so avoid setting if norm is set
        if kws.get("norm") is None:
            kws.setdefault("vmin", self.vmin)
            kws.setdefault("vmax", self.vmax)

        # Draw the heatmap
        mesh = ax.pcolormesh(self.plot_data, cmap=self.cmap, **kws)

        # Set the axis limits
        ax.set(xlim=(0, self.data.shape[1]), ylim=(0, self.data.shape[0]))

        # Invert the y axis to show the plot in matrix form
        ax.invert_yaxis()

        # Possibly add a colorbar
        if self.cbar:
            cb = ax.figure.colorbar(mesh, cax, ax, **self.cbar_kws)
            cb.outline.set_linewidth(0)
            # If rasterized is passed to pcolormesh, also rasterize the
            # colorbar to avoid white lines on the PDF rendering
            if kws.get('rasterized', False):
                cb.solids.set_rasterized(True)

        # Add row and column labels
        if isinstance(self.xticks, str) and self.xticks == "auto":
            xticks, xticklabels = self._auto_ticks(ax, self.xticklabels, 0)
        else:
            xticks, xticklabels = self.xticks, self.xticklabels

        if isinstance(self.yticks, str) and self.yticks == "auto":
            yticks, yticklabels = self._auto_ticks(ax, self.yticklabels, 1)
        else:
            yticks, yticklabels = self.yticks, self.yticklabels

        ax.set(xticks=xticks, yticks=yticks)
        xtl = ax.set_xticklabels(xticklabels)
        ytl = ax.set_yticklabels(yticklabels, rotation="vertical")
        plt.setp(ytl, va="center")  # GH2484

        # Possibly rotate them if they overlap
        _draw_figure(ax.figure)

        if axis_ticklabels_overlap(xtl):
            plt.setp(xtl, rotation="vertical")
        if axis_ticklabels_overlap(ytl):
            plt.setp(ytl, rotation="horizontal")

        # Add the axis labels
        ax.set(xlabel=self.xlabel, ylabel=self.ylabel)

        # Annotate the cells with the formatted values
        if self.annot:
            self._annotate_heatmap(ax, mesh)
```

**With:**

```python
    def plot(self, ax, cax, kws):
        """Draw the heatmap on the provided Axes."""
        # Remove all the Axes spines
        despine(ax=ax, left=True, bottom=True)

        # setting vmin/vmax in addition to norm is deprecated
        # so avoid setting if norm is set
        if kws.get("norm") is None:
            kws.setdefault("vmin", self.data_manager.vmin)
            kws.setdefault("vmax", self.data_manager.vmax)

        # Draw the heatmap
        mesh = ax.pcolormesh(self.data_manager.plot_data, cmap=self.data_manager.cmap, **kws)

        # Set the axis limits
        ax.set(xlim=(0, self.data_manager.data.shape[1]), ylim=(0, self.data_manager.data.shape[0]))

        # Invert the y axis to show the plot in matrix form
        ax.invert_yaxis()

        # Possibly add a colorbar
        if self.data_manager.cbar:
            cb = ax.figure.colorbar(mesh, cax, ax, **self.data_manager.cbar_kws)
            cb.outline.set_linewidth(0)
            # If rasterized is passed to pcolormesh, also rasterize the
            # colorbar to avoid white lines on the PDF rendering
            if kws.get('rasterized', False):
                cb.solids.set_rasterized(True)

        # Add row and column labels
        if isinstance(self.xticks, str) and self.xticks == "auto":
            xticks, xticklabels = self._auto_ticks(ax, self.xticklabels, 0)
        else:
            xticks, xticklabels = self.xticks, self.xticklabels

        if isinstance(self.yticks, str) and self.yticks == "auto":
            yticks, yticklabels = self._auto_ticks(ax, self.yticklabels, 1)
        else:
            yticks, yticklabels = self.yticks, self.yticklabels

        ax.set(xticks=xticks, yticks=yticks)
        xtl = ax.set_xticklabels(xticklabels)
        ytl = ax.set_yticklabels(yticklabels, rotation="vertical")
        plt.setp(ytl, va="center")  # GH2484

        # Possibly rotate them if they overlap
        _draw_figure(ax.figure)

        if axis_ticklabels_overlap(xtl):
            plt.setp(xtl, rotation="vertical")
        if axis_ticklabels_overlap(ytl):
            plt.setp(ytl, rotation="horizontal")

        # Add the axis labels
        ax.set(xlabel=self.xlabel, ylabel=self.ylabel)

        # Annotate the cells with the formatted values
        if self.data_manager.annot:
            self._annotate_heatmap(ax, mesh)
```

## Test results

**FAILED** — 748/756 passed, 1 failed, 1 skipped, 0 errored (duration 17491 ms).

- New failures introduced by this refactor: **1**
- Pre-existing failures (unrelated to this refactor): **0**

New-failure node IDs (first 25):

  - `tests/test_axisgrid.py::TestFacetGrid::test_self_data`

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
...................................F
================================== FAILURES ===================================
________________________ TestFacetGrid.test_self_data _________________________
tests\test_axisgrid.py:39: in test_self_data
    g = ag.FacetGrid(self.df)
        ^^^^^^^^^^^^^^^^^^^^^
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
E   _tkinter.TclError: Can't find a usable tk.tcl in the following directories: 
E       C:/Users/User/miniconda3/Library/lib/tcl8.6/tk8.6 C:/Users/User/miniconda3/Library/lib/tk8.6 C:/Users/User/lib/tk8.6 C:/Users/User/lib/tk8.6 C:/Users/lib/tk8.6 C:/Users/User/library
E   
E   C:/Users/User/miniconda3/Library/lib/tk8.6/tk.tcl: couldn't read file "C:/Users/User/miniconda3/Library/lib/tk8.6/msgs/en.msg": no such file or directory
E   couldn't read file "C:/Users/User/miniconda3/Library/lib/tk8.6/msgs/en.msg": no such file or directory
E       while executing
E   "::source -encoding utf-8 C:/Users/User/miniconda3/Library/lib/tk8.6/msgs/en.msg"
E       (in namespace inscope "::tk::msgcat" script line 1)
E       invoked from within
E   "namespace inscope $ns [list ::source -encoding utf-8 $langfile]"
E       (procedure "Load" line 34)
E       invoked from within
E   "Load $ns [PackageLocales $ns]"
E       (procedure "::msgcat::mcpackageconfig" line 46)
E       invoked from within
E   "::msgcat::mcpackageconfig set mcfolder C:/Users/User/miniconda3/Library/lib/tk8.6/msgs"
E       ("uplevel" body line 1)
E       invoked from within
E   "uplevel 1 [list [namespace origin mcpackageconfig] set mcfolder $langdir]"
E       (procedure "::msgcat::mcload" line 2)
E       invoked from within
E   "::msgcat::mcload [file join $::tk_library msgs]"
E       (in namespace eval "::tk::msgcat" script line 23)
E       invoked from within
E   "namespace eval msgcat {
E   	namespace export mc mcmax
E           if {[interp issafe] || [catch {package require msgcat}]} {
E               # The msgcat package..."
E       (in namespace eval "::tk" script line 3)
E       invoked from within
E   "namespace eval ::tk {
E       # Set up the msgcat commands
E       namespace eval msgcat {
E   	namespace export mc mcmax
E           if {[interp issafe] || [catch {p..."
E       (file "C:/Users/User/miniconda3/Library/lib/tk8.6/tk.tcl" line 17)
E       invoked from within
E   "source C:/Users/User/miniconda3/Library/lib/tk8.6/tk.tcl"
E       ("uplevel" body line 1)
E       invoked from within
E   "uplevel #0 [list source $file]"
E   
E   
E   This probably means that tk wasn't installed properly.
=========================== short test summary info ===========================
FAILED tests/test_axisgrid.py::TestFacetGrid::test_self_data - _tkinter.TclEr...
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!
1 failed, 748 passed, 1 skipped, 6 xfailed in 16.43s

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
index 4e96132..8734403 100644
--- a/seaborn/matrix.py
+++ b/seaborn/matrix.py
@@ -94,42 +94,46 @@ def _matrix_mask(data, mask):
     return mask
 
 
-class _HeatMapper:
-    """Draw a heatmap plot of a matrix with nice labels and colormaps."""
-
+class _HeatmapData:
+    """Data processing for heatmap plots."""
     def __init__(self, data, vmin, vmax, cmap, center, robust, annot, fmt,
-                 annot_kws, cbar, cbar_kws,
-                 xticklabels=True, yticklabels=True, mask=None):
-        """Initialize the plotting object."""
-        # We always want to have a DataFrame with semantic information
-        # and an ndarray to pass to matplotlib
+                 annot_kws, cbar, cbar_kws, xticklabels, yticklabels, mask):
         if isinstance(data, pd.DataFrame):
             plot_data = data.values
         else:
             plot_data = np.asarray(data)
             data = pd.DataFrame(plot_data)
 
-        # Validate the mask and convert to DataFrame
         mask = _matrix_mask(data, mask)
-
         plot_data = np.ma.masked_where(np.asarray(mask), plot_data)
 
-        # Get good names for the rows and columns
+        self.data = data
+        self.plot_data = plot_data
+        self.fmt = fmt
+        self.annot_kws = {} if annot_kws is None else annot_kws.copy()
+        self.cbar = cbar
+        self.cbar_kws = {} if cbar_kws is None else cbar_kws.copy()
+
+        self._setup_labels(xticklabels, yticklabels)
+        self._determine_cmap_params(plot_data, vmin, vmax, cmap, center, robust)
+        self._setup_annotations(annot, plot_data)
+
+    def _setup_labels(self, xticklabels, yticklabels):
         xtickevery = 1
         if isinstance(xticklabels, int):
             xtickevery = xticklabels
-            xticklabels = _index_to_ticklabels(data.columns)
+            xticklabels = _index_to_ticklabels(self.data.columns)
         elif xticklabels is True:
-            xticklabels = _index_to_ticklabels(data.columns)
+            xticklabels = _index_to_ticklabels(self.data.columns)
         elif xticklabels is False:
             xticklabels = []
 
         ytickevery = 1
         if isinstance(yticklabels, int):
             ytickevery = yticklabels
-            yticklabels = _index_to_ticklabels(data.index)
+            yticklabels = _index_to_ticklabels(self.data.index)
         elif yticklabels is True:
-            yticklabels = _index_to_ticklabels(data.index)
+            yticklabels = _index_to_ticklabels(self.data.index)
         elif yticklabels is False:
             yticklabels = []
 
@@ -138,81 +142,34 @@ class _HeatMapper:
             self.xticklabels = []
         elif isinstance(xticklabels, str) and xticklabels == "auto":
             self.xticks = "auto"
-            self.xticklabels = _index_to_ticklabels(data.columns)
+            self.xticklabels = _index_to_ticklabels(self.data.columns)
         else:
-            self.xticks, self.xticklabels = self._skip_ticks(xticklabels,
-                                                             xtickevery)
+            self.xticks, self.xticklabels = _HeatMapper._skip_ticks(xticklabels, xtickevery)
 
         if not len(yticklabels):
             self.yticks = []
             self.yticklabels = []
         elif isinstance(yticklabels, str) and yticklabels == "auto":
             self.yticks = "auto"
-            self.yticklabels = _index_to_ticklabels(data.index)
+            self.yticklabels = _index_to_ticklabels(self.data.index)
         else:
-            self.yticks, self.yticklabels = self._skip_ticks(yticklabels,
-                                                             ytickevery)
+            self.yticks, self.yticklabels = _HeatMapper._skip_ticks(yticklabels, ytickevery)
 
-        # Get good names for the axis labels
-        xlabel = _index_to_label(data.columns)
-        ylabel = _index_to_label(data.index)
+        xlabel = _index_to_label(self.data.columns)
+        ylabel = _index_to_label(self.data.index)
         self.xlabel = xlabel if xlabel is not None else ""
         self.ylabel = ylabel if ylabel is not None else ""
 
-        # Determine good default values for the colormapping
-        self._determine_cmap_params(plot_data, vmin, vmax,
-                                    cmap, center, robust)
-
-        # Sort out the annotations
-        if annot is None or annot is False:
-            annot = False
-            annot_data = None
-        else:
-            if isinstance(annot, bool):
-                annot_data = plot_data
-            else:
-                annot_data = np.asarray(annot)
-                if annot_data.shape != plot_data.shape:
-                    err = "`data` and `annot` must have same shape."
-                    raise ValueError(err)
-            annot = True
-
-        # Save other attributes to the object
-        self.data = data
-        self.plot_data = plot_data
-
-        self.annot = annot
-        self.annot_data = annot_data
-
-        self.fmt = fmt
-        self.annot_kws = {} if annot_kws is None else annot_kws.copy()
-        self.cbar = cbar
-        self.cbar_kws = {} if cbar_kws is None else cbar_kws.copy()
-
-    def _determine_cmap_params(self, plot_data, vmin, vmax,
-                               cmap, center, robust):
-        """Use some heuristics to set good defaults for colorbar and range."""
-
-        # plot_data is a np.ma.array instance
+    def _determine_cmap_params(self, plot_data, vmin, vmax, cmap, center, robust):
         calc_data = plot_data.astype(float).filled(np.nan)
         if vmin is None:
-            if robust:
-                vmin = np.nanpercentile(calc_data, 2)
-            else:
-                vmin = np.nanmin(calc_data)
+            vmin = np.nanpercentile(calc_data, 2) if robust else np.nanmin(calc_data)
         if vmax is None:
-            if robust:
-                vmax = np.nanpercentile(calc_data, 98)
-            else:
-                vmax = np.nanmax(calc_data)
+            vmax = np.nanpercentile(calc_data, 98) if robust else np.nanmax(calc_data)
         self.vmin, self.vmax = vmin, vmax
 
-        # Choose default colormaps if not provided
         if cmap is None:
-            if center is None:
-                self.cmap = cm.rocket
-            else:
-                self.cmap = cm.icefire
+            self.cmap = cm.rocket if center is None else cm.icefire
         elif isinstance(cmap, str):
             self.cmap = get_colormap(cmap)
         elif isinstance(cmap, list):
@@ -220,49 +177,70 @@ class _HeatMapper:
         else:
             self.cmap = cmap
 
-        # Recenter a divergent colormap
         if center is not None:
-
-            # Copy bad values
-            # in mpl<3.2 only masked values are honored with "bad" color spec
-            # (see https://github.com/matplotlib/matplotlib/pull/14257)
             bad = self.cmap(np.ma.masked_invalid([np.nan]))[0]
-
-            # under/over values are set for sure when cmap extremes
-            # do not map to the same color as +-inf
             under = self.cmap(-np.inf)
             over = self.cmap(np.inf)
             under_set = under != self.cmap(0)
             over_set = over != self.cmap(self.cmap.N - 1)
-
             vrange = max(vmax - center, center - vmin)
             normlize = mpl.colors.Normalize(center - vrange, center + vrange)
             cmin, cmax = normlize([vmin, vmax])
             cc = np.linspace(cmin, cmax, 256)
             self.cmap = mpl.colors.ListedColormap(self.cmap(cc))
             self.cmap.set_bad(bad)
-            if under_set:
-                self.cmap.set_under(under)
-            if over_set:
-                self.cmap.set_over(over)
+            if under_set: self.cmap.set_under(under)
+            if over_set: self.cmap.set_over(over)
+
+    def _setup_annotations(self, annot, plot_data):
+        if annot is None or annot is False:
+            self.annot = False
+            self.annot_data = None
+        else:
+            self.annot = True
+            if isinstance(annot, bool):
+                self.annot_data = plot_data
+            else:
+                annot_data = np.asarray(annot)
+                if annot_data.shape != plot_data.shape:
+                    raise ValueError("`data` and `annot` must have same shape.")
+                self.annot_data = annot_data
+
+class _HeatMapper:
+    """Draw a heatmap plot of a matrix with nice labels and colormaps."""
+
+    def __init__(self, data, vmin, vmax, cmap, center, robust, annot, fmt,
+                 annot_kws, cbar, cbar_kws,
+                 xticklabels=True, yticklabels=True, mask=None):
+        self.data_manager = _HeatmapData(
+            data, vmin, vmax, cmap, center, robust, annot, fmt,
+            annot_kws, cbar, cbar_kws, xticklabels, yticklabels, mask
+        )
+        self.xticks = self.data_manager.xticks
+        self.xticklabels = self.data_manager.xticklabels
+        self.yticks = self.data_manager.yticks
+        self.yticklabels = self.data_manager.yticklabels
+        self.xlabel = self.data_manager.xlabel
+        self.ylabel = self.data_manager.ylabel
 
     def _annotate_heatmap(self, ax, mesh):
         """Add textual labels with the value in each cell."""
         mesh.update_scalarmappable()
-        height, width = self.annot_data.shape
+        height, width = self.data_manager.annot_data.shape
         xpos, ypos = np.meshgrid(np.arange(width) + .5, np.arange(height) + .5)
         for x, y, m, color, val in zip(xpos.flat, ypos.flat,
                                        mesh.get_array().flat, mesh.get_facecolors(),
-                                       self.annot_data.flat):
+                                       self.data_manager.annot_data.flat):
             if m is not np.ma.masked:
                 lum = relative_luminance(color)
                 text_color = ".15" if lum > .408 else "w"
-                annotation = ("{:" + self.fmt + "}").format(val)
+                annotation = ("{:" + self.data_manager.fmt + "}").format(val)
                 text_kwargs = dict(color=text_color, ha="center", va="center")
-                text_kwargs.update(self.annot_kws)
+                text_kwargs.update(self.data_manager.annot_kws)
                 ax.text(x, y, annotation, **text_kwargs)
 
-    def _skip_ticks(self, labels, tickevery):
+    @staticmethod
+    def _skip_ticks(labels, tickevery):
         """Return ticks and labels at evenly spaced intervals."""
         n = len(labels)
         if tickevery == 0:
@@ -299,21 +277,21 @@ class _HeatMapper:
         # setting vmin/vmax in addition to norm is deprecated
         # so avoid setting if norm is set
         if kws.get("norm") is None:
-            kws.setdefault("vmin", self.vmin)
-            kws.setdefault("vmax", self.vmax)
+            kws.setdefault("vmin", self.data_manager.vmin)
+            kws.setdefault("vmax", self.data_manager.vmax)
 
         # Draw the heatmap
-        mesh = ax.pcolormesh(self.plot_data, cmap=self.cmap, **kws)
+        mesh = ax.pcolormesh(self.data_manager.plot_data, cmap=self.data_manager.cmap, **kws)
 
         # Set the axis limits
-        ax.set(xlim=(0, self.data.shape[1]), ylim=(0, self.data.shape[0]))
+        ax.set(xlim=(0, self.data_manager.data.shape[1]), ylim=(0, self.data_manager.data.shape[0]))
 
         # Invert the y axis to show the plot in matrix form
         ax.invert_yaxis()
 
         # Possibly add a colorbar
-        if self.cbar:
-            cb = ax.figure.colorbar(mesh, cax, ax, **self.cbar_kws)
+        if self.data_manager.cbar:
+            cb = ax.figure.colorbar(mesh, cax, ax, **self.data_manager.cbar_kws)
             cb.outline.set_linewidth(0)
             # If rasterized is passed to pcolormesh, also rasterize the
             # colorbar to avoid white lines on the PDF rendering
@@ -348,7 +326,7 @@ class _HeatMapper:
         ax.set(xlabel=self.xlabel, ylabel=self.ylabel)
 
         # Annotate the cells with the formatted values
-        if self.annot:
+        if self.data_manager.annot:
             self._annotate_heatmap(ax, mesh)
 
 

```
