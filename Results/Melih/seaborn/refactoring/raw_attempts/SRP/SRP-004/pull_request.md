# Refactor SRP-004 (SRP): The class mixes data preparation and multi-group resolution logic with render...

**Status:** `patch_failed`  
**Branch:** `refactor/SRP-004` -> `main`  
**Head commit:** `11e83875a77e0bb4e9692f7d424a486dbeb007fc`  
**LLM finish:** `FinishReason.STOP` (prompt 14838, completion 2727)  

## Detected issue

- **File**: `seaborn/distributions.py`
- **Entity**: `_DistributionPlotter` (class)
- **Lines (at detection time)**: L45–L800
- **Severity**: high
- **Confidence**: detected by 10 scan(s)

**Description.** The class mixes data preparation and multi-group resolution logic with rendering logic for multiple distinct distribution plot types.

**Reasoning.** The `_DistributionPlotter` class is responsible for plotting distributions, but it directly implements the rendering logic for several distinct types of distribution plots (histograms, KDEs, ECDFs, rug plots), each with univariate and/or bivariate variants (e.g., `plot_univariate_histogram`, `plot_bivariate_density`, `plot_univariate_ecdf`). Furthermore, it contains complex logic in `_resolve_multiple` for handling how multiple distributions are displayed (stack, fill, dodge). A change to how histograms are rendered is a different reason to change than how stacking of densities is calculated, or how KDEs are plotted. This indicates multiple responsibilities, leading to a 'God Class' smell.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 14
- **Files modified** (1): `seaborn/distributions.py`

**Summary.** Extract distribution rendering logic into a separate _DistributionRenderer class.

**Rationale.** The _DistributionPlotter class was violating SRP by handling both data preparation/grouping and the rendering logic for multiple plot types. By extracting the rendering methods into a _DistributionRenderer class, we separate the concerns of data orchestration from the visual representation of the plots.

## Changes overview

_14 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `seaborn/distributions.py` (12-line block → 72-line replacement)

**Replaces:**

```python
class _DistributionPlotter(VectorPlotter):

    wide_structure = {"x": "@values", "hue": "@columns"}
    flat_structure = {"x": "@values"}

    def __init__(
        self,
        data=None,
        variables={},
    ):

        super().__init__(data=data, variables=variables)
```

**With:**

```python
class _DistributionRenderer:
    """Helper class to handle rendering logic for distribution plots."""
    def __init__(self, plotter):
        self.plotter = plotter

    def __getattr__(self, name):
        return getattr(self.plotter, name)

    def _add_legend(self, *args, **kwargs):
        return self.plotter._add_legend(*args, **kwargs)

    def _artist_kws(self, *args, **kwargs):
        return self.plotter._artist_kws(*args, **kwargs)

    def _get_axes(self, *args, **kwargs):
        return self.plotter._get_axes(*args, **kwargs)

    def _add_axis_labels(self, *args, **kwargs):
        return self.plotter._add_axis_labels(*args, **kwargs)

    def _cmap_from_color(self, *args, **kwargs):
        return self.plotter._cmap_from_color(*args, **kwargs)

    def _plot_single_rug(self, *args, **kwargs):
        return self.plotter._plot_single_rug(*args, **kwargs)

    @property
    def data_variable(self):
        return self.plotter.data_variable

    @property
    def variables(self):
        return self.plotter.variables

    @property
    def iter_data(self):
        return self.plotter.iter_data

    @property
    def comp_data(self):
        return self.plotter.comp_data

    @property
    def ax(self):
        return self.plotter.ax

    @property
    def facets(self):
        return self.plotter.facets

    @property
    def _hue_map(self):
        return self.plotter._hue_map

    @property
    def var_levels(self):
        return self.plotter.var_levels


class _DistributionPlotter(VectorPlotter):
... (12 more line(s) truncated)
```

### 2. EDIT `seaborn/distributions.py` (16-line block → 19-line replacement)

**Replaces:**

```python
    def plot_univariate_histogram(
        self,
        multiple,
        element,
        fill,
        common_norm,
        common_bins,
        shrink,
        kde,
        kde_kws,
        color,
        legend,
        line_kws,
        estimate_kws,
        **plot_kws,
    ):
```

**With:**

```python
    def plot_univariate_histogram(self, *args, **kwargs):
        return self.renderer.plot_univariate_histogram(*args, **kwargs)

    def _render_univariate_histogram(
        self,
        multiple,
        element,
        fill,
        common_norm,
        common_bins,
        shrink,
        kde,
        kde_kws,
        color,
        legend,
        line_kws,
        estimate_kws,
        **plot_kws,
    ):
```

### 3. EDIT `seaborn/distributions.py` (9-line block → 12-line replacement)

**Replaces:**

```python
    def plot_bivariate_histogram(
        self,
        common_bins, common_norm,
        thresh, pthresh, pmax,
        color, legend,
        cbar, cbar_ax, cbar_kws,
        estimate_kws,
        **plot_kws,
    ):
```

**With:**

```python
    def plot_bivariate_histogram(self, *args, **kwargs):
        return self.renderer.plot_bivariate_histogram(*args, **kwargs)

    def _render_bivariate_histogram(
        self,
        common_bins, common_norm,
        thresh, pthresh, pmax,
        color, legend,
        cbar, cbar_ax, cbar_kws,
        estimate_kws,
        **plot_kws,
    ):
```

### 4. EDIT `seaborn/distributions.py` (12-line block → 15-line replacement)

**Replaces:**

```python
    def plot_univariate_density(
        self,
        multiple,
        common_norm,
        common_grid,
        warn_singular,
        fill,
        color,
        legend,
        estimate_kws,
        **plot_kws,
    ):
```

**With:**

```python
    def plot_univariate_density(self, *args, **kwargs):
        return self.renderer.plot_univariate_density(*args, **kwargs)

    def _render_univariate_density(
        self,
        multiple,
        common_norm,
        common_grid,
        warn_singular,
        fill,
        color,
        legend,
        estimate_kws,
        **plot_kws,
    ):
```

### 5. EDIT `seaborn/distributions.py` (15-line block → 18-line replacement)

**Replaces:**

```python
    def plot_bivariate_density(
        self,
        common_norm,
        fill,
        levels,
        thresh,
        color,
        legend,
        cbar,
        warn_singular,
        cbar_ax,
        cbar_kws,
        estimate_kws,
        **contour_kws,
    ):
```

**With:**

```python
    def plot_bivariate_density(self, *args, **kwargs):
        return self.renderer.plot_bivariate_density(*args, **kwargs)

    def _render_bivariate_density(
        self,
        common_norm,
        fill,
        levels,
        thresh,
        color,
        legend,
        cbar,
        warn_singular,
        cbar_ax,
        cbar_kws,
        estimate_kws,
        **contour_kws,
    ):
```

### 6. EDIT `seaborn/distributions.py` (1-line block → 4-line replacement)

**Replaces:**

```python
    def plot_univariate_ecdf(self, estimate_kws, legend, **plot_kws):
```

**With:**

```python
    def plot_univariate_ecdf(self, *args, **kwargs):
        return self.renderer.plot_univariate_ecdf(*args, **kwargs)

    def _render_univariate_ecdf(self, estimate_kws, legend, **plot_kws):
```

### 7. EDIT `seaborn/distributions.py` (1-line block → 4-line replacement)

**Replaces:**

```python
    def plot_rug(self, height, expand_margins, legend, **kws):
```

**With:**

```python
    def plot_rug(self, *args, **kwargs):
        return self.renderer.plot_rug(*args, **kwargs)

    def _render_rug(self, height, expand_margins, legend, **kws):
```

### 8. EDIT `seaborn/distributions.py` (16-line block → 16-line replacement)

**Replaces:**

```python
    def plot_univariate_histogram(
        self,
        multiple,
        element,
        fill,
        common_norm,
        common_bins,
        shrink,
        kde,
        kde_kws,
        color,
        legend,
        line_kws,
        estimate_kws,
        **plot_kws,
    ):
```

**With:**

```python
    def _render_univariate_histogram(
        self,
        multiple,
        element,
        fill,
        common_norm,
        common_bins,
        shrink,
        kde,
        kde_kws,
        color,
        legend,
        line_kws,
        estimate_kws,
        **plot_kws,
    ):
```

### 9. EDIT `seaborn/distributions.py` (9-line block → 9-line replacement)

**Replaces:**

```python
    def plot_bivariate_histogram(
        self,
        common_bins, common_norm,
        thresh, pthresh, pmax,
        color, legend,
        cbar, cbar_ax, cbar_kws,
        estimate_kws,
        **plot_kws,
    ):
```

**With:**

```python
    def _render_bivariate_histogram(
        self,
        common_bins, common_norm,
        thresh, pthresh, pmax,
        color, legend,
        cbar, cbar_ax, cbar_kws,
        estimate_kws,
        **plot_kws,
    ):
```

### 10. EDIT `seaborn/distributions.py` (12-line block → 12-line replacement)

**Replaces:**

```python
    def plot_univariate_density(
        self,
        multiple,
        common_norm,
        common_grid,
        warn_singular,
        fill,
        color,
        legend,
        estimate_kws,
        **plot_kws,
    ):
```

**With:**

```python
    def _render_univariate_density(
        self,
        multiple,
        common_norm,
        common_grid,
        warn_singular,
        fill,
        color,
        legend,
        estimate_kws,
        **plot_kws,
    ):
```

### 11. EDIT `seaborn/distributions.py` (15-line block → 15-line replacement)

**Replaces:**

```python
    def plot_bivariate_density(
        self,
        common_norm,
        fill,
        levels,
        thresh,
        color,
        legend,
        cbar,
        warn_singular,
        cbar_ax,
        cbar_kws,
        estimate_kws,
        **contour_kws,
    ):
```

**With:**

```python
    def _render_bivariate_density(
        self,
        common_norm,
        fill,
        levels,
        thresh,
        color,
        legend,
        cbar,
        warn_singular,
        cbar_ax,
        cbar_kws,
        estimate_kws,
        **contour_kws,
    ):
```

### 12. EDIT `seaborn/distributions.py` (1-line block → 1-line replacement)

**Replaces:**

```python
    def plot_univariate_ecdf(self, estimate_kws, legend, **plot_kws):
```

**With:**

```python
    def _render_univariate_ecdf(self, estimate_kws, legend, **plot_kws):
```

### 13. EDIT `seaborn/distributions.py` (1-line block → 1-line replacement)

**Replaces:**

```python
    def plot_rug(self, height, expand_margins, legend, **kws):
```

**With:**

```python
    def _render_rug(self, height, expand_margins, legend, **kws):
```

### 14. EDIT `seaborn/distributions.py` (3-line block → 14-line replacement)

**Replaces:**

```python
# ==================================================================================== #
# External API
# ==================================================================================== #
```

**With:**

```python
# ==================================================================================== #
# Renderer Implementation
# ==================================================================================== #

_DistributionRenderer.plot_univariate_histogram = _DistributionPlotter._render_univariate_histogram
_DistributionRenderer.plot_bivariate_histogram = _DistributionPlotter._render_bivariate_histogram
_DistributionRenderer.plot_univariate_density = _DistributionPlotter._render_univariate_density
_DistributionRenderer.plot_bivariate_density = _DistributionPlotter._render_bivariate_density
_DistributionRenderer.plot_univariate_ecdf = _DistributionPlotter._render_univariate_ecdf
_DistributionRenderer.plot_rug = _DistributionPlotter._render_rug

# ==================================================================================== #
# External API
# ==================================================================================== #
```

## Apply error

```
search_text not found in seaborn/distributions.py (block 7)
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `seaborn/distributions.py` | 1802 → - | 26 → - | 13.19 → - | 64 → - | 0 → - |

## Diff

*(no diff — patch was not applied)*
