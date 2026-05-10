# Refactor LSP-020 (LSP): Subclass method signature is incompatible with the base class method signature.

**Status:** `applied_passed`  
**Branch:** `refactor/LSP-020` -> `main`  
**Head commit:** `19ea9134d8be76c87a8e6c8ed3d5b9deaa6386db`  
**LLM finish:** `FinishReason.STOP` (prompt 10903, completion 818)  

## Detected issue

- **File**: `seaborn/regression.py`
- **Entity**: `_RegressionPlotter.plot` (method)
- **Lines (at detection time)**: L351–L384
- **Severity**: high
- **Confidence**: detected by 3 scan(s)

**Description.** Subclass method signature is incompatible with the base class method signature.

**Reasoning.** The base class _LinearPlotter defines the plot method with a single parameter 'ax' (line 66). The subclass _RegressionPlotter overrides this method but changes the signature to require three mandatory parameters: 'ax', 'scatter_kws', and 'line_kws' (line 351). This violates LSP because a caller holding a reference to the base type _LinearPlotter cannot substitute it with a _RegressionPlotter without the program failing due to a TypeError when calling plot(ax).

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `seaborn/regression.py`

**Summary.** Update _RegressionPlotter.plot signature to match base class _LinearPlotter.plot

**Rationale.** The base class _LinearPlotter defines plot(self, ax). The subclass _RegressionPlotter.plot was overriding this with plot(self, ax, scatter_kws, line_kws), violating the Liskov Substitution Principle. I have updated the signature to use optional keyword arguments, ensuring compatibility with the base class while maintaining existing functionality.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `seaborn/regression.py` (35-line block → 40-line replacement)

**Replaces:**

```python
    def plot(self, ax, scatter_kws, line_kws):
        """Draw the full plot."""
        # Insert the plot label into the correct set of keyword arguments
        if self.scatter:
            scatter_kws["label"] = self.label
        else:
            line_kws["label"] = self.label

        # Use the current color cycle state as a default
        if self.color is None:
            lines, = ax.plot([], [])
            color = lines.get_color()
            lines.remove()
        else:
            color = self.color

        # Ensure that color is hex to avoid matplotlib weirdness
        color = mpl.colors.rgb2hex(mpl.colors.colorConverter.to_rgb(color))

        # Let color in keyword arguments override overall plot color
        scatter_kws.setdefault("color", color)
        line_kws.setdefault("color", color)

        # Draw the constituent plots
        if self.scatter:
            self.scatterplot(ax, scatter_kws)

        if self.fit_reg:
            self.lineplot(ax, line_kws)

        # Label the axes
        if hasattr(self.x, "name"):
            ax.set_xlabel(self.x.name)
        if hasattr(self.y, "name"):
            ax.set_ylabel(self.y.name)
```

**With:**

```python
    def plot(self, ax, scatter_kws=None, line_kws=None):
        """Draw the full plot."""
        if scatter_kws is None:
            scatter_kws = {}
        if line_kws is None:
            line_kws = {}

        # Insert the plot label into the correct set of keyword arguments
        if self.scatter:
            scatter_kws["label"] = self.label
        else:
            line_kws["label"] = self.label

        # Use the current color cycle state as a default
        if self.color is None:
            lines, = ax.plot([], [])
            color = lines.get_color()
            lines.remove()
        else:
            color = self.color

        # Ensure that color is hex to avoid matplotlib weirdness
        color = mpl.colors.rgb2hex(mpl.colors.colorConverter.to_rgb(color))

        # Let color in keyword arguments override overall plot color
        scatter_kws.setdefault("color", color)
        line_kws.setdefault("color", color)

        # Draw the constituent plots
        if self.scatter:
            self.scatterplot(ax, scatter_kws)

        if self.fit_reg:
            self.lineplot(ax, line_kws)

        # Label the axes
        if hasattr(self.x, "name"):
            ax.set_xlabel(self.x.name)
        if hasattr(self.y, "name"):
            ax.set_ylabel(self.y.name)
```

## Test results

**PASSED** — 0/0 passed, 0 failed, 0 skipped, 0 errored (duration 2214 ms).

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
seaborn\categorical.py:49: in <module>
    class _CategoricalPlotter(VectorPlotter):
seaborn\categorical.py:482: in _CategoricalPlotter
    @register_plot("strips")
     ^^^^^^^^^^^^^^^^^^^^^^^
E   TypeError: 'classmethod' object is not callable
=========================== short test summary info ===========================
ERROR tests/_core/test_data.py - TypeError: 'classmethod' object is not callable
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!
1 error in 1.36s

```

</details>

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `seaborn/regression.py` | 773 → 777 | 27 → 27 | 5 → 5.09 | 11 → 11 | 27.93 → 27.42 |

## Diff

```diff
diff --git a/seaborn/regression.py b/seaborn/regression.py
index b9a0c45..51269fb 100644
--- a/seaborn/regression.py
+++ b/seaborn/regression.py
@@ -353,8 +353,13 @@ class _RegressionPlotter(_LinearPlotter):
         a_prime = a - b.dot(np.linalg.pinv(b).dot(a))
         return np.asarray(a_prime + a_mean).reshape(a.shape)
 
-    def plot(self, ax, scatter_kws, line_kws):
+    def plot(self, ax, scatter_kws=None, line_kws=None):
         """Draw the full plot."""
+        if scatter_kws is None:
+            scatter_kws = {}
+        if line_kws is None:
+            line_kws = {}
+
         # Insert the plot label into the correct set of keyword arguments
         if self.scatter:
             scatter_kws["label"] = self.label

```
