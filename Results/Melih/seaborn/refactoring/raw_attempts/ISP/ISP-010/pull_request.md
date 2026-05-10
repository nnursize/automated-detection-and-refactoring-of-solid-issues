# Refactor ISP-010 (ISP): Bloated class responsible for diverse plotting execution and rendering concerns.

**Status:** `applied_passed`  
**Branch:** `refactor/ISP-010` -> `main`  
**Head commit:** `ca21f7d408709b2310eba3f8a41c16039778d12b`  
**LLM finish:** `FinishReason.STOP` (prompt 11054, completion 1447)  

## Detected issue

- **File**: `seaborn/_core/plot.py`
- **Entity**: `Plotter` (class)
- **Lines (at detection time)**: L974–L1830
- **Severity**: high
- **Confidence**: detected by 1 scan(s)

**Description.** Bloated class responsible for diverse plotting execution and rendering concerns.

**Reasoning.** The `Plotter` class handles a wide range of responsibilities related to plot execution, including data extraction, label resolution, figure setup, statistics computation, scale setup, layer plotting, coordinate unscaling, pairing generation, subplot filtering, and legend management. This broad interface forces clients to depend on many unrelated functionalities, making it a fat interface and violating ISP.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 2
- **Files modified** (1): `seaborn/_core/plot.py`

**Summary.** Refactor Plotter to separate legend management into a dedicated class

**Rationale.** The Plotter class is bloated with legend-specific logic. Moving this to a LegendManager class improves cohesion and reduces the size of the Plotter interface, adhering to the Interface Segregation Principle.

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
        LegendManager().make_legend(self, p)
```

### 2. EDIT `seaborn/_core/plot.py` (20-line block → 55-line replacement)

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

        self._pyplot = pyplot
        self._theme = theme
        self._legend_contents: list[tuple[
            tuple[str, str | int], list[Artist], list[str],
        ]] = []
        self._scales: dict[str, Scale] = {}
```

**With:**

```python
class LegendManager:
    def make_legend(self, plotter: "Plotter", p: Plot) -> None:
        """Combine artists representing same information across layers."""
        merged_contents: dict[
            tuple[str, str | int], tuple[list[tuple[Artist, ...]], list[str]],
        ] = {}
        for key, new_artists, labels in plotter._legend_contents:
            if key not in merged_contents:
                new_artist_tuples = [tuple([a]) for a in new_artists]
                merged_contents[key] = new_artist_tuples, labels
            else:
                existing_artists = merged_contents[key][0]
                for i, new_artist in enumerate(new_artists):
                    existing_artists[i] += tuple([new_artist])

        loc = "center right" if plotter._pyplot else "center left"
        base_legend = None
        for (name, _), (handles, labels) in merged_contents.items():
            legend = mpl.legend.Legend(
                plotter._figure,
                handles,
                labels,
                title=name,
                loc=loc,
                bbox_to_anchor=(.98, .55),
            )
            if base_legend:
                base_legend_box = base_legend.get_children()[0]
                this_legend_box = legend.get_children()[0]
                base_legend_box.get_children().extend(this_legend_box.get_children())
            else:
                base_legend = legend
                plotter._figure.legends.append(legend)


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

        self._pyplot = pyplot
        self._theme = theme
        self._legend_contents: list[tuple[
            tuple[str, str | int], list[Artist], list[str],
        ]] = []
        self._scales: dict[str, Scale] = {}
```

## Test results

**PASSED** — 0/0 passed, 0 failed, 0 skipped, 0 errored (duration 2223 ms).

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
1 error in 1.37s

```

</details>

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `seaborn/_core/plot.py` | 1288 → 1292 | 57 → 58 | 5.22 → 5.22 | 31 → 31 | 0 → 0 |

## Diff

```diff
diff --git a/seaborn/_core/plot.py b/seaborn/_core/plot.py
index 004727b..36e8d40 100644
--- a/seaborn/_core/plot.py
+++ b/seaborn/_core/plot.py
@@ -926,6 +926,41 @@ class Plot:
 # ---- The plot compilation engine ---------------------------------------------- #
 
 
+class LegendManager:
+    def make_legend(self, plotter: "Plotter", p: Plot) -> None:
+        """Combine artists representing same information across layers."""
+        merged_contents: dict[
+            tuple[str, str | int], tuple[list[tuple[Artist, ...]], list[str]],
+        ] = {}
+        for key, new_artists, labels in plotter._legend_contents:
+            if key not in merged_contents:
+                new_artist_tuples = [tuple([a]) for a in new_artists]
+                merged_contents[key] = new_artist_tuples, labels
+            else:
+                existing_artists = merged_contents[key][0]
+                for i, new_artist in enumerate(new_artists):
+                    existing_artists[i] += tuple([new_artist])
+
+        loc = "center right" if plotter._pyplot else "center left"
+        base_legend = None
+        for (name, _), (handles, labels) in merged_contents.items():
+            legend = mpl.legend.Legend(
+                plotter._figure,
+                handles,
+                labels,
+                title=name,
+                loc=loc,
+                bbox_to_anchor=(.98, .55),
+            )
+            if base_legend:
+                base_legend_box = base_legend.get_children()[0]
+                this_legend_box = legend.get_children()[0]
+                base_legend_box.get_children().extend(this_legend_box.get_children())
+            else:
+                base_legend = legend
+                plotter._figure.legends.append(legend)
+
+
 class Plotter:
     """
     Engine for compiling a :class:`Plot` spec into a Matplotlib figure.
@@ -1684,52 +1719,7 @@ class Plotter:
 
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
+        LegendManager().make_legend(self, p)
 
     def _finalize_figure(self, p: Plot) -> None:
 

```
