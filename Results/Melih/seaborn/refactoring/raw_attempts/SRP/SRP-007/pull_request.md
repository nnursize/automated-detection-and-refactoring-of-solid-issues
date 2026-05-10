# Refactor SRP-007 (SRP): Mixes statistical modeling/fitting with visual rendering logic.

**Status:** `applied_failed`  
**Branch:** `refactor/SRP-007` -> `main`  
**Head commit:** `11e83875a77e0bb4e9692f7d424a486dbeb007fc`  
**LLM finish:** `FinishReason.STOP` (prompt 10835, completion 4940)  

## Detected issue

- **File**: `seaborn/regression.py`
- **Entity**: `_RegressionPlotter` (class)
- **Lines (at detection time)**: L70–L442
- **Severity**: medium
- **Confidence**: detected by 7 scan(s)

**Description.** Mixes statistical modeling/fitting with visual rendering logic.

**Reasoning.** It is responsible for both the statistical estimation (fitting linear models, polynomials, lowess, or calling statsmodels) and the rendering of the resulting lines and scatter points. Statistical logic (the 'what' of the data) should be separated from plotting logic (the 'how' of the display).

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 3
- **Files modified** (1): `seaborn/regression.py`

**Summary.** Extract statistical modeling logic from _RegressionPlotter into a new _RegressionModeler class.

**Rationale.** The _RegressionPlotter class was violating SRP by handling both statistical estimation and visual rendering. By extracting the statistical logic into a new _RegressionModeler class, we separate the 'what' (data modeling) from the 'how' (plotting).

## Changes overview

_3 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `seaborn/regression.py` (65-line block → 177-line replacement)

**Replaces:**

```python
class _RegressionPlotter(_LinearPlotter):
    """Plotter for numeric independent variables with regression model.

    This does the computations and drawing for the `regplot` function, and
    is thus also used indirectly by `lmplot`.
    """
    def __init__(self, x, y, data=None, x_estimator=None, x_bins=None,
                 x_ci="ci", scatter=True, fit_reg=True, ci=95, n_boot=1000,
                 units=None, seed=None, order=1, logistic=False, lowess=False,
                 robust=False, logx=False, x_partial=None, y_partial=None,
                 truncate=False, dropna=True, x_jitter=None, y_jitter=None,
                 color=None, label=None):

        # Set member attributes
        self.x_estimator = x_estimator
        self.ci = ci
        self.x_ci = ci if x_ci == "ci" else x_ci
        self.n_boot = n_boot
        self.seed = seed
        self.scatter = scatter
        self.fit_reg = fit_reg
        self.order = order
        self.logistic = logistic
        self.lowess = lowess
        self.robust = robust
        self.logx = logx
        self.truncate = truncate
        self.x_jitter = x_jitter
        self.y_jitter = y_jitter
        self.color = color
        self.label = label

        # Validate the regression options:
        if sum((order > 1, logistic, robust, lowess, logx)) > 1:
            raise ValueError("Mutually exclusive regression options.")

        # Extract the data vals from the arguments or passed dataframe
        self.establish_variables(data, x=x, y=y, units=units,
                                 x_partial=x_partial, y_partial=y_partial)

        # Drop null observations
        if dropna:
            self.dropna("x", "y", "units", "x_partial", "y_partial")

        # Regress nuisance variables out of the data
        if self.x_partial is not None:
            self.x = self.regress_out(self.x, self.x_partial)
        if self.y_partial is not None:
            self.y = self.regress_out(self.y, self.y_partial)

        # Possibly bin the predictor variable, which implies a point estimate
        if x_bins is not None:
            self.x_estimator = np.mean if x_estimator is None else x_estimator
            x_discrete, x_bins = self.bin_predictor(x_bins)
            self.x_discrete = x_discrete
        else:
            self.x_discrete = self.x

        # Disable regression in case of singleton inputs
        if len(self.x) <= 1:
... (5 more line(s) truncated)
```

**With:**

```python
class _RegressionModeler:
    """Helper class for statistical modeling in regression plots."""
    def __init__(self, x, y, units=None, x_estimator=None, x_ci="ci",
                 n_boot=1000, seed=None, order=1, logistic=False, lowess=False,
                 robust=False, logx=False, ci=95):
        self.x = x
        self.y = y
        self.units = units
        self.x_estimator = x_estimator
        self.x_ci = x_ci
        self.n_boot = n_boot
        self.seed = seed
        self.order = order
        self.logistic = logistic
        self.lowess = lowess
        self.robust = robust
        self.logx = logx
        self.ci = ci

    def _check_statsmodels(self):
        options = "logistic", "robust", "lowess"
        err = "`{}=True` requires statsmodels, an optional dependency, to be installed."
        for option in options:
            if getattr(self, option) and not _has_statsmodels:
                raise RuntimeError(err.format(option))

    def fit_regression(self, grid):
        self._check_statsmodels()
        ci = self.ci
        if self.order > 1:
            yhat, yhat_boots = self.fit_poly(grid, self.order)
        elif self.logistic:
            from statsmodels.genmod.generalized_linear_model import GLM
            from statsmodels.genmod.families import Binomial
            yhat, yhat_boots = self.fit_statsmodels(grid, GLM, family=Binomial())
        elif self.lowess:
            ci = None
            grid, yhat = self.fit_lowess()
        elif self.robust:
            from statsmodels.robust.robust_linear_model import RLM
            yhat, yhat_boots = self.fit_statsmodels(grid, RLM)
        elif self.logx:
            yhat, yhat_boots = self.fit_logx(grid)
        else:
            yhat, yhat_boots = self.fit_fast(grid)

        if ci is None:
            err_bands = None
        else:
            err_bands = utils.ci(yhat_boots, ci, axis=0)
        return grid, yhat, err_bands

    def fit_fast(self, grid):
        def reg_func(_x, _y):
            return np.linalg.pinv(_x).dot(_y)
        X, y = np.c_[np.ones(len(self.x)), self.x], self.y
        grid = np.c_[np.ones(len(grid)), grid]
        yhat = grid.dot(reg_func(X, y))
        if self.ci is None:
            return yhat, None
... (117 more line(s) truncated)
```

### 2. EDIT `seaborn/regression.py` (144-line block → 12-line replacement)

**Replaces:**

```python
    def _check_statsmodels(self):
        """Check whether statsmodels is installed if any boolean options require it."""
        options = "logistic", "robust", "lowess"
        err = "`{}=True` requires statsmodels, an optional dependency, to be installed."
        for option in options:
            if getattr(self, option) and not _has_statsmodels:
                raise RuntimeError(err.format(option))

    def fit_regression(self, ax=None, x_range=None, grid=None):
        """Fit the regression model."""
        self._check_statsmodels()

        # Create the grid for the regression
        if grid is None:
            if self.truncate:
                x_min, x_max = self.x_range
            else:
                if ax is None:
                    x_min, x_max = x_range
                else:
                    x_min, x_max = ax.get_xlim()
            grid = np.linspace(x_min, x_max, 100)
        ci = self.ci

        # Fit the regression
        if self.order > 1:
            yhat, yhat_boots = self.fit_poly(grid, self.order)
        elif self.logistic:
            from statsmodels.genmod.generalized_linear_model import GLM
            from statsmodels.genmod.families import Binomial
            yhat, yhat_boots = self.fit_statsmodels(grid, GLM,
                                                    family=Binomial())
        elif self.lowess:
            ci = None
            grid, yhat = self.fit_lowess()
        elif self.robust:
            from statsmodels.robust.robust_linear_model import RLM
            yhat, yhat_boots = self.fit_statsmodels(grid, RLM)
        elif self.logx:
            yhat, yhat_boots = self.fit_logx(grid)
        else:
            yhat, yhat_boots = self.fit_fast(grid)

        # Compute the confidence interval at each grid point
        if ci is None:
            err_bands = None
        else:
            err_bands = utils.ci(yhat_boots, ci, axis=0)

        return grid, yhat, err_bands

    def fit_fast(self, grid):
        """Low-level regression and prediction using linear algebra."""
        def reg_func(_x, _y):
            return np.linalg.pinv(_x).dot(_y)

        X, y = np.c_[np.ones(len(self.x)), self.x], self.y
        grid = np.c_[np.ones(len(grid)), grid]
        yhat = grid.dot(reg_func(X, y))
        if self.ci is None:
... (84 more line(s) truncated)
```

**With:**

```python
    def fit_regression(self, ax=None, x_range=None, grid=None):
        """Fit the regression model."""
        if grid is None:
            if self.truncate:
                x_min, x_max = self.x_range
            else:
                if ax is None:
                    x_min, x_max = x_range
                else:
                    x_min, x_max = ax.get_xlim()
            grid = np.linspace(x_min, x_max, 100)
        return self.modeler.fit_regression(grid)
```

### 3. EDIT `seaborn/regression.py` (6-line block → 6-line replacement)

**Replaces:**

```python
        # Draw the regression line and confidence interval
        line, = ax.plot(grid, yhat, **kws)
        if not self.truncate:
            line.sticky_edges.x[:] = edges  # Prevent mpl from adding margin
        if err_bands is not None:
            ax.fill_between(grid, *err_bands, facecolor=fill_color, alpha=.15)
```

**With:**

```python
        # Draw the regression line and confidence interval
        line, = ax.plot(grid, yhat, **kws)
        if not self.truncate:
            line.sticky_edges.x[:] = edges  # Prevent mpl from adding margin
        if err_bands is not None:
            ax.fill_between(grid, *err_bands, facecolor=fill_color, alpha=.15)
```

## Test results

**FAILED** — 169/176 passed, 1 failed, 1 skipped, 0 errored (duration 6342 ms).

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
E   _tkinter.TclError: invalid command name "tcl_findLibrary"
=========================== short test summary info ===========================
FAILED tests/_core/test_plot.py::TestPlotting::test_show - _tkinter.TclError:...
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!
1 failed, 169 passed, 1 skipped, 5 xfailed in 5.12s

```

</details>

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `seaborn/regression.py` | 773 → - | 27 → - | 5 → - | 11 → - | 27.93 → - |

## Diff

```diff
diff --git a/seaborn/regression.py b/seaborn/regression.py
index b9a0c45..1a00d3a 100644
--- a/seaborn/regression.py
+++ b/seaborn/regression.py
@@ -67,12 +67,127 @@ class _LinearPlotter:
         raise NotImplementedError
 
 
-class _RegressionPlotter(_LinearPlotter):
-    """Plotter for numeric independent variables with regression model.
+class _RegressionModeler:
+    """Helper class for statistical modeling in regression plots."""
+    def __init__(self, x, y, units=None, x_estimator=None, x_ci="ci",
+                 n_boot=1000, seed=None, order=1, logistic=False, lowess=False,
+                 robust=False, logx=False, ci=95):
+        self.x = x
+        self.y = y
+        self.units = units
+        self.x_estimator = x_estimator
+        self.x_ci = x_ci
+        self.n_boot = n_boot
+        self.seed = seed
+        self.order = order
+        self.logistic = logistic
+        self.lowess = lowess
+        self.robust = robust
+        self.logx = logx
+        self.ci = ci
 
-    This does the computations and drawing for the `regplot` function, and
-    is thus also used indirectly by `lmplot`.
-    """
+    def _check_statsmodels(self):
+        options = "logistic", "robust", "lowess"
+        err = "`{}=True` requires statsmodels, an optional dependency, to be installed."
+        for option in options:
+            if getattr(self, option) and not _has_statsmodels:
+                raise RuntimeError(err.format(option))
+
+    def fit_regression(self, grid):
+        self._check_statsmodels()
+        ci = self.ci
+        if self.order > 1:
+            yhat, yhat_boots = self.fit_poly(grid, self.order)
+        elif self.logistic:
+            from statsmodels.genmod.generalized_linear_model import GLM
+            from statsmodels.genmod.families import Binomial
+            yhat, yhat_boots = self.fit_statsmodels(grid, GLM, family=Binomial())
+        elif self.lowess:
+            ci = None
+            grid, yhat = self.fit_lowess()
+        elif self.robust:
+            from statsmodels.robust.robust_linear_model import RLM
+            yhat, yhat_boots = self.fit_statsmodels(grid, RLM)
+        elif self.logx:
+            yhat, yhat_boots = self.fit_logx(grid)
+        else:
+            yhat, yhat_boots = self.fit_fast(grid)
+
+        if ci is None:
+            err_bands = None
+        else:
+            err_bands = utils.ci(yhat_boots, ci, axis=0)
+        return grid, yhat, err_bands
+
+    def fit_fast(self, grid):
+        def reg_func(_x, _y):
+            return np.linalg.pinv(_x).dot(_y)
+        X, y = np.c_[np.ones(len(self.x)), self.x], self.y
+        grid = np.c_[np.ones(len(grid)), grid]
+        yhat = grid.dot(reg_func(X, y))
+        if self.ci is None:
+            return yhat, None
+        beta_boots = algo.bootstrap(X, y, func=reg_func, n_boot=self.n_boot,
+                                    units=self.units, seed=self.seed).T
+        yhat_boots = grid.dot(beta_boots).T
+        return yhat, yhat_boots
+
+    def fit_poly(self, grid, order):
+        def reg_func(_x, _y):
+            return np.polyval(np.polyfit(_x, _y, order), grid)
+        yhat = reg_func(self.x, self.y)
+        if self.ci is None:
+            return yhat, None
+        yhat_boots = algo.bootstrap(self.x, self.y, func=reg_func,
+                                    n_boot=self.n_boot, units=self.units,
+                                    seed=self.seed)
+        return yhat, yhat_boots
+
+    def fit_statsmodels(self, grid, model, **kwargs):
+        import statsmodels.tools.sm_exceptions as sme
+        X, y = np.c_[np.ones(len(self.x)), self.x], self.y
+        grid = np.c_[np.ones(len(grid)), grid]
+        def reg_func(_x, _y):
+            err_classes = (sme.PerfectSeparationError,)
+            try:
+                with warnings.catch_warnings():
+                    if hasattr(sme, "PerfectSeparationWarning"):
+                        warnings.simplefilter("error", sme.PerfectSeparationWarning)
+                        err_classes = (*err_classes, sme.PerfectSeparationWarning)
+                    yhat = model(_y, _x, **kwargs).fit().predict(grid)
+            except err_classes:
+                yhat = np.empty(len(grid))
+                yhat.fill(np.nan)
+            return yhat
+        yhat = reg_func(X, y)
+        if self.ci is None:
+            return yhat, None
+        yhat_boots = algo.bootstrap(X, y, func=reg_func, n_boot=self.n_boot,
+                                    units=self.units, seed=self.seed)
+        return yhat, yhat_boots
+
+    def fit_lowess(self):
+        from statsmodels.nonparametric.smoothers_lowess import lowess
+        grid, yhat = lowess(self.y, self.x).T
+        return grid, yhat
+
+    def fit_logx(self, grid):
+        X, y = np.c_[np.ones(len(self.x)), self.x], self.y
+        grid = np.c_[np.ones(len(grid)), np.log(grid)]
+        def reg_func(_x, _y):
+            _x = np.c_[_x[:, 0], np.log(_x[:, 1])]
+            return np.linalg.pinv(_x).dot(_y)
+        yhat = grid.dot(reg_func(X, y))
+        if self.ci is None:
+            return yhat, None
+        beta_boots = algo.bootstrap(X, y, func=reg_func, n_boot=self.n_boot,
+                                    units=self.units, seed=self.seed).T
+        yhat_boots = grid.dot(beta_boots).T
+        return yhat, yhat_boots
+
+
+class _RegressionPlotter(_LinearPlotter):
+    """Plotter for numeric independent variables with regression model."""
     def __init__(self, x, y, data=None, x_estimator=None, x_bins=None,
                  x_ci="ci", scatter=True, fit_reg=True, ci=95, n_boot=1000,
                  units=None, seed=None, order=1, logistic=False, lowess=False,
@@ -80,7 +195,6 @@ class _RegressionPlotter(_LinearPlotter):
                  truncate=False, dropna=True, x_jitter=None, y_jitter=None,
                  color=None, label=None):
 
-        # Set member attributes
         self.x_estimator = x_estimator
         self.ci = ci
         self.x_ci = ci if x_ci == "ci" else x_ci
@@ -99,25 +213,20 @@ class _RegressionPlotter(_LinearPlotter):
         self.color = color
         self.label = label
 
-        # Validate the regression options:
         if sum((order > 1, logistic, robust, lowess, logx)) > 1:
             raise ValueError("Mutually exclusive regression options.")
 
-        # Extract the data vals from the arguments or passed dataframe
         self.establish_variables(data, x=x, y=y, units=units,
                                  x_partial=x_partial, y_partial=y_partial)
 
-        # Drop null observations
         if dropna:
             self.dropna("x", "y", "units", "x_partial", "y_partial")
 
-        # Regress nuisance variables out of the data
         if self.x_partial is not None:
             self.x = self.regress_out(self.x, self.x_partial)
         if self.y_partial is not None:
             self.y = self.regress_out(self.y, self.y_partial)
 
-        # Possibly bin the predictor variable, which implies a point estimate
         if x_bins is not None:
             self.x_estimator = np.mean if x_estimator is None else x_estimator
             x_discrete, x_bins = self.bin_predictor(x_bins)
@@ -125,13 +234,16 @@ class _RegressionPlotter(_LinearPlotter):
         else:
             self.x_discrete = self.x
 
-        # Disable regression in case of singleton inputs
         if len(self.x) <= 1:
             self.fit_reg = False
 
-        # Save the range of the x variable for the grid later
         if self.fit_reg:
             self.x_range = self.x.min(), self.x.max()
+            self.modeler = _RegressionModeler(
+                self.x, self.y, self.units, self.x_estimator, self.x_ci,
+                self.n_boot, self.seed, self.order, self.logistic,
+                self.lowess, self.robust, self.logx, self.ci
+            )
 
     @property
     def scatter_data(self):
@@ -185,19 +297,8 @@ class _RegressionPlotter(_LinearPlotter):
 
         return vals, points, cis
 
-    def _check_statsmodels(self):
-        """Check whether statsmodels is installed if any boolean options require it."""
-        options = "logistic", "robust", "lowess"
-        err = "`{}=True` requires statsmodels, an optional dependency, to be installed."
-        for option in options:
-            if getattr(self, option) and not _has_statsmodels:
-                raise RuntimeError(err.format(option))
-
     def fit_regression(self, ax=None, x_range=None, grid=None):
         """Fit the regression model."""
-        self._check_statsmodels()
-
-        # Create the grid for the regression
         if grid is None:
             if self.truncate:
                 x_min, x_max = self.x_range
@@ -207,128 +308,7 @@ class _RegressionPlotter(_LinearPlotter):
                 else:
                     x_min, x_max = ax.get_xlim()
             grid = np.linspace(x_min, x_max, 100)
-        ci = self.ci
-
-        # Fit the regression
-        if self.order > 1:
-            yhat, yhat_boots = self.fit_poly(grid, self.order)
-        elif self.logistic:
-            from statsmodels.genmod.generalized_linear_model import GLM
-            from statsmodels.genmod.families import Binomial
-            yhat, yhat_boots = self.fit_statsmodels(grid, GLM,
-                                                    family=Binomial())
-        elif self.lowess:
-            ci = None
-            grid, yhat = self.fit_lowess()
-        elif self.robust:
-            from statsmodels.robust.robust_linear_model import RLM
-            yhat, yhat_boots = self.fit_statsmodels(grid, RLM)
-        elif self.logx:
-            yhat, yhat_boots = self.fit_logx(grid)
-        else:
-            yhat, yhat_boots = self.fit_fast(grid)
-
-        # Compute the confidence interval at each grid point
-        if ci is None:
-            err_bands = None
-        else:
-            err_bands = utils.ci(yhat_boots, ci, axis=0)
-
-        return grid, yhat, err_bands
-
-    def fit_fast(self, grid):
-        """Low-level regression and prediction using linear algebra."""
-        def reg_func(_x, _y):
-            return np.linalg.pinv(_x).dot(_y)
-
-        X, y = np.c_[np.ones(len(self.x)), self.x], self.y
-        grid = np.c_[np.ones(len(grid)), grid]
-        yhat = grid.dot(reg_func(X, y))
-        if self.ci is None:
-            return yhat, None
-
-        beta_boots = algo.bootstrap(X, y,
-                                    func=reg_func,
-                                    n_boot=self.n_boot,
-                                    units=self.units,
-                                    seed=self.seed).T
-        yhat_boots = grid.dot(beta_boots).T
-        return yhat, yhat_boots
-
-    def fit_poly(self, grid, order):
-        """Regression using numpy polyfit for higher-order trends."""
-        def reg_func(_x, _y):
-            return np.polyval(np.polyfit(_x, _y, order), grid)
-
-        x, y = self.x, self.y
-        yhat = reg_func(x, y)
-        if self.ci is None:
-            return yhat, None
-
-        yhat_boots = algo.bootstrap(x, y,
-                                    func=reg_func,
-                                    n_boot=self.n_boot,
-                                    units=self.units,
-                                    seed=self.seed)
-        return yhat, yhat_boots
-
-    def fit_statsmodels(self, grid, model, **kwargs):
-        """More general regression function using statsmodels objects."""
-        import statsmodels.tools.sm_exceptions as sme
-        X, y = np.c_[np.ones(len(self.x)), self.x], self.y
-        grid = np.c_[np.ones(len(grid)), grid]
-
-        def reg_func(_x, _y):
-            err_classes = (sme.PerfectSeparationError,)
-            try:
-                with warnings.catch_warnings():
-                    if hasattr(sme, "PerfectSeparationWarning"):
-                        # statsmodels>=0.14.0
-                        warnings.simplefilter("error", sme.PerfectSeparationWarning)
-                        err_classes = (*err_classes, sme.PerfectSeparationWarning)
-                    yhat = model(_y, _x, **kwargs).fit().predict(grid)
-            except err_classes:
-                yhat = np.empty(len(grid))
-                yhat.fill(np.nan)
-            return yhat
-
-        yhat = reg_func(X, y)
-        if self.ci is None:
-            return yhat, None
-
-        yhat_boots = algo.bootstrap(X, y,
-                                    func=reg_func,
-                                    n_boot=self.n_boot,
-                                    units=self.units,
-                                    seed=self.seed)
-        return yhat, yhat_boots
-
-    def fit_lowess(self):
-        """Fit a locally-weighted regression, which returns its own grid."""
-        from statsmodels.nonparametric.smoothers_lowess import lowess
-        grid, yhat = lowess(self.y, self.x).T
-        return grid, yhat
-
-    def fit_logx(self, grid):
-        """Fit the model in log-space."""
-        X, y = np.c_[np.ones(len(self.x)), self.x], self.y
-        grid = np.c_[np.ones(len(grid)), np.log(grid)]
-
-        def reg_func(_x, _y):
-            _x = np.c_[_x[:, 0], np.log(_x[:, 1])]
-            return np.linalg.pinv(_x).dot(_y)
-
-        yhat = grid.dot(reg_func(X, y))
-        if self.ci is None:
-            return yhat, None
-
-        beta_boots = algo.bootstrap(X, y,
-                                    func=reg_func,
-                                    n_boot=self.n_boot,
-                                    units=self.units,
-                                    seed=self.seed).T
-        yhat_boots = grid.dot(beta_boots).T
-        return yhat, yhat_boots
+        return self.modeler.fit_regression(grid)
 
     def bin_predictor(self, bins):
         """Discretize a predictor by assigning value to closest bin."""

```
