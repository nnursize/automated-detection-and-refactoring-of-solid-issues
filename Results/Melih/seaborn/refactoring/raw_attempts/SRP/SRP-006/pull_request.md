# Refactor SRP-006 (SRP): Massive orchestrator handling data extraction, stat computation, scale resolu...

**Status:** `applied_failed`  
**Branch:** `refactor/SRP-006` -> `main`  
**Head commit:** `11e83875a77e0bb4e9692f7d424a486dbeb007fc`  
**LLM finish:** `FinishReason.STOP` (prompt 11030, completion 2847)  

## Detected issue

- **File**: `seaborn/_core/plot.py`
- **Entity**: `Plotter` (class)
- **Lines (at detection time)**: L974–L1830
- **Severity**: high
- **Confidence**: detected by 5 scan(s)

**Description.** Massive orchestrator handling data extraction, stat computation, scale resolution, and figure finalization.

**Reasoning.** This class acts as a central engine that performs data extraction, statistical processing (_compute_stats), scale resolution (_setup_scales), figure/subplot initialization, and legend construction. These are distinct responsibilities that should be delegated to specialized components to avoid a monolithic design.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 2
- **Files modified** (1): `seaborn/_core/plot.py`

**Summary.** Extract legend generation logic from Plotter to a new LegendManager class

**Rationale.** The Plotter class is a 'God object' handling data, scales, plotting, and figure finalization. Extracting the legend management logic into a dedicated class reduces the responsibility of the Plotter and improves maintainability.

## Changes overview

_2 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `seaborn/_core/plot.py` (112-line block → 5-line replacement)

**Replaces:**

```python
    def _update_legend_contents(
        self,
        p: Plot,
        mark: Mark,
        data: PlotData,
        scales: dict[str, Scale],
        layer_label: str | None,
    ) -> None:
        """Add legend artists / labels for one layer in the plot."""
        if data.frame.empty and data.frames:
            legend_vars: list[str] = []
            for frame in data.frames.values():
                frame_vars = frame.columns.intersection(list(scales))
                legend_vars.extend(v for v in frame_vars if v not in legend_vars)
        else:
            legend_vars = list(data.frame.columns.intersection(list(scales)))

        # First handle layer legends, which occupy a single entry in legend_contents.
        if layer_label is not None:
            legend_title = str(p._labels.get("legend", ""))
            layer_key = (legend_title, -1)
            artist = mark._legend_artist([], None, {})
            if artist is not None:
                for content in self._legend_contents:
                    if content[0] == layer_key:
                        content[1].append(artist)
                        content[2].append(layer_label)
                        break
                else:
                    self._legend_contents.append((layer_key, [artist], [layer_label]))

        # Then handle the scale legends
        # First pass: Identify the values that will be shown for each variable
        schema: list[tuple[
            tuple[str, str | int], list[str], tuple[list[Any], list[str]]
        ]] = []
        schema = []
        for var in legend_vars:
            var_legend = scales[var]._legend
            if var_legend is not None:
                values, labels = var_legend
                for (_, part_id), part_vars, _ in schema:
                    if data.ids[var] == part_id:
                        # Allow multiple plot semantics to represent same data variable
                        part_vars.append(var)
                        break
                else:
                    title = self._resolve_label(p, var, data.names[var])
                    entry = (title, data.ids[var]), [var], (values, labels)
                    schema.append(entry)

        # Second pass, generate an artist corresponding to each value
        contents: list[tuple[tuple[str, str | int], Any, list[str]]] = []
        for key, variables, (values, labels) in schema:
            artists = []
            for val in values:
                artist = mark._legend_artist(variables, val, scales)
                if artist is not None:
                    artists.append(artist)
            if artists:
... (52 more line(s) truncated)
```

**With:**

```python
    def _update_legend_contents(self, *args, **kwargs):
        return LegendManager().update(self, *args, **kwargs)

    def _make_legend(self, p: Plot) -> None:
        LegendManager().make(self, p)
```

### 2. EDIT `seaborn/_core/plot.py` (8-line block → 124-line replacement)

**Replaces:**

```python
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
    def __init__(self, pyplot: bool, theme: dict[str, Any]):

        self._pyplot = pyplot
        self._theme = theme
        self._legend_contents: list[tuple[
            tuple[str, str | int], list[Artist], list[str],
        ]] = []
        self._scales: dict[str, Scale] = {}


class LegendManager:
    def update(
        self,
        plotter: Plotter,
        p: Plot,
        mark: Mark,
        data: PlotData,
        scales: dict[str, Scale],
        layer_label: str | None,
    ) -> None:
        """Add legend artists / labels for one layer in the plot."""
        if data.frame.empty and data.frames:
            legend_vars: list[str] = []
            for frame in data.frames.values():
                frame_vars = frame.columns.intersection(list(scales))
                legend_vars.extend(v for v in frame_vars if v not in legend_vars)
        else:
            legend_vars = list(data.frame.columns.intersection(list(scales)))

        # First handle layer legends, which occupy a single entry in legend_contents.
        if layer_label is not None:
            legend_title = str(p._labels.get("legend", ""))
            layer_key = (legend_title, -1)
            artist = mark._legend_artist([], None, {})
            if artist is not None:
                for content in plotter._legend_contents:
                    if content[0] == layer_key:
                        content[1].append(artist)
                        content[2].append(layer_label)
                        break
                else:
                    plotter._legend_contents.append((layer_key, [artist], [layer_label]))

        # Then handle the scale legends
        # First pass: Identify the values that will be shown for each variable
        schema: list[tuple[
            tuple[str, str | int], list[str], tuple[list[Any], list[str]]
        ]] = []
        schema = []
        for var in legend_vars:
            var_legend = scales[var]._legend
            if var_legend is not None:
                values, labels = var_legend
                for (_, part_id), part_vars, _ in schema:
                    if data.ids[var] == part_id:
                        # Allow multiple plot semantics to represent same data variable
                        part_vars.append(var)
                        break
                else:
                    title = plotter._resolve_label(p, var, data.names[var])
... (64 more line(s) truncated)
```

## Test results

**FAILED** — 98/100 passed, 1 failed, 1 skipped, 0 errored (duration 3525 ms).

- New failures introduced by this refactor: **1**
- Pre-existing failures (unrelated to this refactor): **0**

New-failure node IDs (first 25):

  - `tests/_core/test_plot.py::TestLayerAddition::test_without_data`

Command: `C:\Users\User\Desktop\SDP-Codex\S1-T7-Okeyish\refactor_workspaces\seaborn-master\.venv\Scripts\python.exe -m pytest --tb=short -q --no-header -p no:cacheprovider -x --json-report --json-report-file=C:\Users\User\Desktop\SDP-Codex\S1-T7-Okeyish\refactor_workspaces\seaborn-master\.pytest_report.json`

<details><summary>Output tail</summary>

```
....................................s................................... [  3%]
...........................F
================================== FAILURES ===================================
_____________________ TestLayerAddition.test_without_data _____________________
tests\_core\test_plot.py:199: in test_without_data
    p = Plot(long_df, x="x", y="y").add(MockMark()).plot()
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
seaborn\_core\plot.py:932: in plot
    return self._plot(pyplot)
           ^^^^^^^^^^^^^^^^^^
seaborn\_core\plot.py:942: in _plot
    common, layers = plotter._extract_data(self)
                     ^^^^^^^^^^^^^^^^^^^^^
E   AttributeError: 'Plotter' object has no attribute '_extract_data'
=========================== short test summary info ===========================
FAILED tests/_core/test_plot.py::TestLayerAddition::test_without_data - Attri...
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!
1 failed, 98 passed, 1 skipped in 2.45s

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
index b235af9..72b21fb 100644
--- a/seaborn/_core/plot.py
+++ b/seaborn/_core/plot.py
@@ -992,6 +992,122 @@ class Plotter:
         ]] = []
         self._scales: dict[str, Scale] = {}
 
+
+class LegendManager:
+    def update(
+        self,
+        plotter: Plotter,
+        p: Plot,
+        mark: Mark,
+        data: PlotData,
+        scales: dict[str, Scale],
+        layer_label: str | None,
+    ) -> None:
+        """Add legend artists / labels for one layer in the plot."""
+        if data.frame.empty and data.frames:
+            legend_vars: list[str] = []
+            for frame in data.frames.values():
+                frame_vars = frame.columns.intersection(list(scales))
+                legend_vars.extend(v for v in frame_vars if v not in legend_vars)
+        else:
+            legend_vars = list(data.frame.columns.intersection(list(scales)))
+
+        # First handle layer legends, which occupy a single entry in legend_contents.
+        if layer_label is not None:
+            legend_title = str(p._labels.get("legend", ""))
+            layer_key = (legend_title, -1)
+            artist = mark._legend_artist([], None, {})
+            if artist is not None:
+                for content in plotter._legend_contents:
+                    if content[0] == layer_key:
+                        content[1].append(artist)
+                        content[2].append(layer_label)
+                        break
+                else:
+                    plotter._legend_contents.append((layer_key, [artist], [layer_label]))
+
+        # Then handle the scale legends
+        # First pass: Identify the values that will be shown for each variable
+        schema: list[tuple[
+            tuple[str, str | int], list[str], tuple[list[Any], list[str]]
+        ]] = []
+        schema = []
+        for var in legend_vars:
+            var_legend = scales[var]._legend
+            if var_legend is not None:
+                values, labels = var_legend
+                for (_, part_id), part_vars, _ in schema:
+                    if data.ids[var] == part_id:
+                        # Allow multiple plot semantics to represent same data variable
+                        part_vars.append(var)
+                        break
+                else:
+                    title = plotter._resolve_label(p, var, data.names[var])
+                    entry = (title, data.ids[var]), [var], (values, labels)
+                    schema.append(entry)
+
+        # Second pass, generate an artist corresponding to each value
+        contents: list[tuple[tuple[str, str | int], Any, list[str]]] = []
+        for key, variables, (values, labels) in schema:
+            artists = []
+            for val in values:
+                artist = mark._legend_artist(variables, val, scales)
+                if artist is not None:
+                    artists.append(artist)
+            if artists:
+                contents.append((key, artists, labels))
+
+        plotter._legend_contents.extend(contents)
+
+    def make(self, plotter: Plotter, p: Plot) -> None:
+        """Create the legend artist(s) and add onto the figure."""
+        # Combine artists representing same information across layers
+        # Input list has an entry for each distinct variable in each layer
+        # Output dict has an entry for each distinct variable
+        merged_contents: dict[
+            tuple[str, str | int], tuple[list[tuple[Artist, ...]], list[str]],
+        ] = {}
+        for key, new_artists, labels in plotter._legend_contents:
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
+        loc = "center right" if plotter._pyplot else "center left"
+
+        base_legend = None
+        for (name, _), (handles, labels) in merged_contents.items():
+
+            legend = mpl.legend.Legend(
+                plotter._figure,
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
+                plotter._figure.legends.append(legend)
+
     def save(self, loc, **kwargs) -> Plotter:  # TODO type args
         kwargs.setdefault("dpi", 96)
         try:
@@ -1663,118 +1779,11 @@ class Plotter:
 
         return split_generator
 
-    def _update_legend_contents(
-        self,
-        p: Plot,
-        mark: Mark,
-        data: PlotData,
-        scales: dict[str, Scale],
-        layer_label: str | None,
-    ) -> None:
-        """Add legend artists / labels for one layer in the plot."""
-        if data.frame.empty and data.frames:
-            legend_vars: list[str] = []
-            for frame in data.frames.values():
-                frame_vars = frame.columns.intersection(list(scales))
-                legend_vars.extend(v for v in frame_vars if v not in legend_vars)
-        else:
-            legend_vars = list(data.frame.columns.intersection(list(scales)))
-
-        # First handle layer legends, which occupy a single entry in legend_contents.
-        if layer_label is not None:
-            legend_title = str(p._labels.get("legend", ""))
-            layer_key = (legend_title, -1)
-            artist = mark._legend_artist([], None, {})
-            if artist is not None:
-                for content in self._legend_contents:
-                    if content[0] == layer_key:
-                        content[1].append(artist)
-                        content[2].append(layer_label)
-                        break
-                else:
-                    self._legend_contents.append((layer_key, [artist], [layer_label]))
-
-        # Then handle the scale legends
-        # First pass: Identify the values that will be shown for each variable
-        schema: list[tuple[
-            tuple[str, str | int], list[str], tuple[list[Any], list[str]]
-        ]] = []
-        schema = []
-        for var in legend_vars:
-            var_legend = scales[var]._legend
-            if var_legend is not None:
-                values, labels = var_legend
-                for (_, part_id), part_vars, _ in schema:
-                    if data.ids[var] == part_id:
-                        # Allow multiple plot semantics to represent same data variable
-                        part_vars.append(var)
-                        break
-                else:
-                    title = self._resolve_label(p, var, data.names[var])
-                    entry = (title, data.ids[var]), [var], (values, labels)
-                    schema.append(entry)
-
-        # Second pass, generate an artist corresponding to each value
-        contents: list[tuple[tuple[str, str | int], Any, list[str]]] = []
-        for key, variables, (values, labels) in schema:
-            artists = []
-            for val in values:
-                artist = mark._legend_artist(variables, val, scales)
-                if artist is not None:
-                    artists.append(artist)
-            if artists:
-                contents.append((key, artists, labels))
-
-        self._legend_contents.extend(contents)
+    def _update_legend_contents(self, *args, **kwargs):
+        return LegendManager().update(self, *args, **kwargs)
 
     def _make_legend(self, p: Plot) -> None:
-        """Create the legend artist(s) and add onto the figure."""
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
+        LegendManager().make(self, p)
 
     def _finalize_figure(self, p: Plot) -> None:
 

```
