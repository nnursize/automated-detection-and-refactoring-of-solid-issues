# Refactor SRP-019 (SRP): The class is a 'God Class' responsible for the entire plot compilation proces...

**Status:** `applied_failed`  
**Branch:** `refactor/SRP-019` -> `main`  
**Head commit:** `11e83875a77e0bb4e9692f7d424a486dbeb007fc`  
**LLM finish:** `FinishReason.STOP` (prompt 11147, completion 1508)  

## Detected issue

- **File**: `seaborn/_core/plot.py`
- **Entity**: `Plotter` (class)
- **Lines (at detection time)**: L366–L744
- **Severity**: high
- **Confidence**: detected by 1 scan(s)

**Description.** The class is a 'God Class' responsible for the entire plot compilation process, including figure setup, data preparation, statistical computation, scale application, Matplotlib rendering, legend management, and final output.

**Reasoning.** This class exhibits a severe 'God Class' smell. Its methods (`_setup_figure`, `_extract_data`, `_compute_stats`, `_setup_scales`, `_plot_layer`, `_make_legend`, `_finalize_figure`, `save`, `show`, `_repr_png_`, `_repr_svg_`) collectively handle nearly every aspect of turning a plot specification into a rendered Matplotlib figure. This includes: managing figure layout and axes, extracting and transforming data, performing statistical calculations, configuring and applying scales, drawing Matplotlib artists, managing legend contents, and handling output/display. This class has too many distinct reasons to change, making it highly unstable and difficult to maintain.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 2
- **Files modified** (1): `seaborn/_core/plot.py`

**Summary.** Extract legend management logic from Plotter to a new LegendManager class

**Rationale.** The Plotter class is a God Class. Extracting the legend management logic into a dedicated class reduces the responsibility of Plotter and improves maintainability by isolating the complex legend-building process.

## Changes overview

_2 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `seaborn/_core/plot.py` (48-line block → 3-line replacement)

**Replaces:**

```python
    def _make_legend(self, p: Plot) -> None:
        """Create the legend artist(s) and add onto the figure."""
        # Combine artists representing same information across layers
        # Input list has an entry for each distinct variable in each layer
        # Output dict has an entry for each distinct variable
        merged_contents: dict[
            tuple[str, str | int], tuple[list[tuple[Artist, ...]], list[str]],
        ] = {}
        for key, new_artists, labels in self._legend_contents:
            # Key is (name, id); we need the id to resolve variable uniqueness,
            # but will need the name in the next step to title the legend
            if key not in merged_contents:
                # Matplotlib accepts a tuple of artists and will overlay them
                new_artist_tuples = [tuple([a]) for a in new_artists]
                merged_contents[key] = new_artist_tuples, labels
            else:
                existing_artists = merged_contents[key][0]
                for i, new_artist in enumerate(new_artists):
                    existing_artists[i] += tuple([new_artist])

        # When using pyplot, an "external" legend won't be shown, so this
        # keeps it inside the axes (though still attached to the figure)
        # This is necessary because matplotlib layout engines currently don't
        # support figure legends — ideally this will change.
        loc = "center right" if self._pyplot else "center left"

        base_legend = None
        for (name, _), (handles, labels) in merged_contents.items():

            legend = mpl.legend.Legend(
                self._figure,
                handles,  # type: ignore  # matplotlib/issues/26639
                labels,
                title=name,
                loc=loc,
                bbox_to_anchor=(.98, .55),
            )

            if base_legend:
                # Matplotlib has no public API for this so it is a bit of a hack.
                # Ideally we'd define our own legend class with more flexibility,
                # but that is a lot of work!
                base_legend_box = base_legend.get_children()[0]
                this_legend_box = legend.get_children()[0]
                base_legend_box.get_children().extend(this_legend_box.get_children())
            else:
                base_legend = legend
                self._figure.legends.append(legend)
```

**With:**

```python
    def _make_legend(self, p: Plot) -> None:
        """Create the legend artist(s) and add onto the figure."""
        LegendManager().draw(self._figure, self._legend_contents, self._pyplot)
```

### 2. EDIT `seaborn/_core/plot.py` (13-line block → 63-line replacement)

**Replaces:**

```python
class Plotter:
    """
    Engine for compiling a :class:`Plot` spec into a Matplotlib figure.

    This class is not intended to be instantiated directly by users.

    """
    # TODO decide if we ever want these (Plot.plot(debug=True))?
    _data: PlotData
    _layers: list[Layer]
    _figure: Figure

    def __init__(self, pyplot: bool, theme: dict[str, Any]):
```

**With:**

```python
class LegendManager:
    def draw(self, figure, contents, pyplot):
        # Combine artists representing same information across layers
        # Input list has an entry for each distinct variable in each layer
        # Output dict has an entry for each distinct variable
        merged_contents: dict[
            tuple[str, str | int], tuple[list[tuple[Artist, ...]], list[str]],
        ] = {}
        for key, new_artists, labels in contents:
            # Key is (name, id); we need the id to resolve variable uniqueness,
            # but will need the name in the next step to title the legend
            if key not in merged_contents:
                # Matplotlib accepts a tuple of artists and will overlay them
                new_artist_tuples = [tuple([a]) for a in new_artists]
                merged_contents[key] = new_artist_tuples, labels
            else:
                existing_artists = merged_contents[key][0]
                for i, new_artist in enumerate(new_artists):
                    existing_artists[i] += tuple([new_artist])

        # When using pyplot, an "external" legend won't be shown, so this
        # keeps it inside the axes (though still attached to the figure)
        # This is necessary because matplotlib layout engines currently don't
        # support figure legends — ideally this will change.
        loc = "center right" if pyplot else "center left"

        base_legend = None
        for (name, _), (handles, labels) in merged_contents.items():

            legend = mpl.legend.Legend(
                figure,
                handles,  # type: ignore  # matplotlib/issues/26639
                labels,
                title=name,
                loc=loc,
                bbox_to_anchor=(.98, .55),
            )

            if base_legend:
                # Matplotlib has no public API for this so it is a bit of a hack.
                # Ideally we'd define our own legend class with more flexibility,
                # but that is a lot of work!
                base_legend_box = base_legend.get_children()[0]
                this_legend_box = legend.get_children()[0]
                base_legend_box.get_children().extend(this_legend_box.get_children())
            else:
                base_legend = legend
                figure.legends.append(legend)


class Plotter:
    """
    Engine for compiling a :class:`Plot` spec into a Matplotlib figure.

    This class is not intended to be instantiated directly by users.

    """
    # TODO decide if we ever want these (Plot.plot(debug=True))?
    _data: PlotData
    _layers: list[Layer]
... (3 more line(s) truncated)
```

## Test results

**FAILED** — 169/176 passed, 1 failed, 1 skipped, 0 errored (duration 5947 ms).

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
seaborn\_core\plot.py:1177: in _setup_figure
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
FAILED tests/_core/test_plot.py::TestPlotting::test_show - _tkinter.TclError:...
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!
1 failed, 169 passed, 1 skipped, 5 xfailed in 4.94s

```

</details>

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `seaborn/_core/plot.py` | 1311 → - | 57 → - | 5.19 → - | 31 → - | 0 → - |

## Diff

```diff
diff --git a/seaborn/_core/plot.py b/seaborn/_core/plot.py
index b235af9..0f7e06f 100644
--- a/seaborn/_core/plot.py
+++ b/seaborn/_core/plot.py
@@ -971,6 +971,56 @@ class Plot:
 # ---- The plot compilation engine ---------------------------------------------- #
 
 
+class LegendManager:
+    def draw(self, figure, contents, pyplot):
+        # Combine artists representing same information across layers
+        # Input list has an entry for each distinct variable in each layer
+        # Output dict has an entry for each distinct variable
+        merged_contents: dict[
+            tuple[str, str | int], tuple[list[tuple[Artist, ...]], list[str]],
+        ] = {}
+        for key, new_artists, labels in contents:
+            # Key is (name, id); we need the id to resolve variable uniqueness,
+            # but will need the name in the next step to title the legend
+            if key not in merged_contents:
+                # Matplotlib accepts a tuple of artists and will overlay them
+                new_artist_tuples = [tuple([a]) for a in new_artists]
+                merged_contents[key] = new_artist_tuples, labels
+            else:
+                existing_artists = merged_contents[key][0]
+                for i, new_artist in enumerate(new_artists):
+                    existing_artists[i] += tuple([new_artist])
+
+        # When using pyplot, an "external" legend won't be shown, so this
+        # keeps it inside the axes (though still attached to the figure)
+        # This is necessary because matplotlib layout engines currently don't
+        # support figure legends â€” ideally this will change.
+        loc = "center right" if pyplot else "center left"
+
+        base_legend = None
+        for (name, _), (handles, labels) in merged_contents.items():
+
+            legend = mpl.legend.Legend(
+                figure,
+                handles,  # type: ignore  # matplotlib/issues/26639
+                labels,
+                title=name,
+                loc=loc,
+                bbox_to_anchor=(.98, .55),
+            )
+
+            if base_legend:
+                # Matplotlib has no public API for this so it is a bit of a hack.
+                # Ideally we'd define our own legend class with more flexibility,
+                # but that is a lot of work!
+                base_legend_box = base_legend.get_children()[0]
+                this_legend_box = legend.get_children()[0]
+                base_legend_box.get_children().extend(this_legend_box.get_children())
+            else:
+                base_legend = legend
+                figure.legends.append(legend)
+
+
 class Plotter:
     """
     Engine for compiling a :class:`Plot` spec into a Matplotlib figure.
@@ -1729,52 +1779,7 @@ class Plotter:
 
     def _make_legend(self, p: Plot) -> None:
         """Create the legend artist(s) and add onto the figure."""
-        # Combine artists representing same information across layers
-        # Input list has an entry for each distinct variable in each layer
-        # Output dict has an entry for each distinct variable
-        merged_contents: dict[
-            tuple[str, str | int], tuple[list[tuple[Artist, ...]], list[str]],
-        ] = {}
-        for key, new_artists, labels in self._legend_contents:
-            # Key is (name, id); we need the id to resolve variable uniqueness,
-            # but will need the name in the next step to title the legend
-            if key not in merged_contents:
-                # Matplotlib accepts a tuple of artists and will overlay them
-                new_artist_tuples = [tuple([a]) for a in new_artists]
-                merged_contents[key] = new_artist_tuples, labels
-            else:
-                existing_artists = merged_contents[key][0]
-                for i, new_artist in enumerate(new_artists):
-                    existing_artists[i] += tuple([new_artist])
-
-        # When using pyplot, an "external" legend won't be shown, so this
-        # keeps it inside the axes (though still attached to the figure)
-        # This is necessary because matplotlib layout engines currently don't
-        # support figure legends â€” ideally this will change.
-        loc = "center right" if self._pyplot else "center left"
-
-        base_legend = None
-        for (name, _), (handles, labels) in merged_contents.items():
-
-            legend = mpl.legend.Legend(
-                self._figure,
-                handles,  # type: ignore  # matplotlib/issues/26639
-                labels,
-                title=name,
-                loc=loc,
-                bbox_to_anchor=(.98, .55),
-            )
-
-            if base_legend:
-                # Matplotlib has no public API for this so it is a bit of a hack.
-                # Ideally we'd define our own legend class with more flexibility,
-                # but that is a lot of work!
-                base_legend_box = base_legend.get_children()[0]
-                this_legend_box = legend.get_children()[0]
-                base_legend_box.get_children().extend(this_legend_box.get_children())
-            else:
-                base_legend = legend
-                self._figure.legends.append(legend)
+        LegendManager().draw(self._figure, self._legend_contents, self._pyplot)
 
     def _finalize_figure(self, p: Plot) -> None:
 

```
