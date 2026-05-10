# Refactor OCP-013 (OCP): Long if/elif chain for dispatching tick formatter strategies.

**Status:** `applied_passed`  
**Branch:** `refactor/OCP-013` -> `main`  
**Head commit:** `901bc653086ead958014a9f54cb1288b89f798e3`  
**LLM finish:** `FinishReason.STOP` (prompt 10358, completion 667)  

## Detected issue

- **File**: `seaborn/_core/scales.py`
- **Entity**: `Continuous._get_formatter` (method)
- **Lines (at detection time)**: L430–L459
- **Severity**: high
- **Confidence**: detected by 2 scan(s)

**Description.** Long if/elif chain for dispatching tick formatter strategies.

**Reasoning.** The `_get_formatter` method uses a long `if/elif` chain to determine the appropriate `Formatter` based on various parameters (`formatter`, `like`, `base`, `unit`). Adding a new tick label formatting strategy would require modifying this method to add a new `elif` branch, directly violating the Open/Closed Principle.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `seaborn/_core/scales.py`

**Summary.** Refactor Continuous._get_formatter to use a registry-like dispatch pattern

**Rationale.** Replaced the if/elif chain with a strategy-based approach using a list of handlers. This allows new formatting strategies to be added without modifying the core logic of _get_formatter, adhering to the Open/Closed Principle.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `seaborn/_core/scales.py` (38-line block → 33-line replacement)

**Replaces:**

```python
    def _get_formatter(self, locator, formatter, like, base, unit):

        log_base, symlog_thresh = self._parse_for_log_params(self.trans)
        if base is default:
            if symlog_thresh:
                log_base = 10
            base = log_base

        if formatter is not None:
            return formatter

        if like is not None:
            if isinstance(like, str):
                if "{x" in like or "{pos" in like:
                    fmt = like
                else:
                    fmt = f"{{x:{like}}}"
                formatter = StrMethodFormatter(fmt)
            else:
                formatter = FuncFormatter(like)

        elif base is not None:
            # We could add other log options if necessary
            formatter = LogFormatterSciNotation(base)

        elif unit is not None:
            if isinstance(unit, tuple):
                sep, unit = unit
            elif not unit:
                sep = ""
            else:
                sep = " "
            formatter = EngFormatter(unit, sep=sep)

        else:
            formatter = ScalarFormatter()

        return formatter
```

**With:**

```python
    def _get_formatter(self, locator, formatter, like, base, unit):

        if formatter is not None:
            return formatter

        log_base, symlog_thresh = self._parse_for_log_params(self.trans)
        if base is default:
            base = 10 if symlog_thresh else log_base

        handlers = [
            (lambda: like is not None, self._format_like),
            (lambda: base is not None, lambda: LogFormatterSciNotation(base)),
            (lambda: unit is not None, lambda: self._format_unit(unit)),
        ]

        for condition, handler in handlers:
            if condition():
                return handler()

        return ScalarFormatter()

    def _format_like(self, like):
        if isinstance(like, str):
            fmt = like if ("{x" in like or "{pos" in like) else f"{{x:{like}}}"
            return StrMethodFormatter(fmt)
        return FuncFormatter(like)

    def _format_unit(self, unit):
        if isinstance(unit, tuple):
            sep, unit = unit
        else:
            sep = "" if not unit else " "
        return EngFormatter(unit, sep=sep)
```

## Test results

**PASSED** — 0/0 passed, 0 failed, 0 skipped, 0 errored (duration 2231 ms).

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
1 error in 1.37s

```

</details>

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `seaborn/_core/scales.py` | 751 → 747 | 75 → 77 | 2.89 → 2.79 | 16 → 16 | 23.49 → 23.47 |

## Diff

```diff
diff --git a/seaborn/_core/scales.py b/seaborn/_core/scales.py
index 429a1e5..fdfd6cb 100644
--- a/seaborn/_core/scales.py
+++ b/seaborn/_core/scales.py
@@ -714,42 +714,37 @@ class Continuous(ContinuousBase):
 
     def _get_formatter(self, locator, formatter, like, base, unit):
 
+        if formatter is not None:
+            return formatter
+
         log_base, symlog_thresh = self._parse_for_log_params(self.trans)
         if base is default:
-            if symlog_thresh:
-                log_base = 10
-            base = log_base
+            base = 10 if symlog_thresh else log_base
 
-        if formatter is not None:
-            return formatter
+        handlers = [
+            (lambda: like is not None, self._format_like),
+            (lambda: base is not None, lambda: LogFormatterSciNotation(base)),
+            (lambda: unit is not None, lambda: self._format_unit(unit)),
+        ]
 
-        if like is not None:
-            if isinstance(like, str):
-                if "{x" in like or "{pos" in like:
-                    fmt = like
-                else:
-                    fmt = f"{{x:{like}}}"
-                formatter = StrMethodFormatter(fmt)
-            else:
-                formatter = FuncFormatter(like)
+        for condition, handler in handlers:
+            if condition():
+                return handler()
 
-        elif base is not None:
-            # We could add other log options if necessary
-            formatter = LogFormatterSciNotation(base)
+        return ScalarFormatter()
 
-        elif unit is not None:
-            if isinstance(unit, tuple):
-                sep, unit = unit
-            elif not unit:
-                sep = ""
-            else:
-                sep = " "
-            formatter = EngFormatter(unit, sep=sep)
+    def _format_like(self, like):
+        if isinstance(like, str):
+            fmt = like if ("{x" in like or "{pos" in like) else f"{{x:{like}}}"
+            return StrMethodFormatter(fmt)
+        return FuncFormatter(like)
 
+    def _format_unit(self, unit):
+        if isinstance(unit, tuple):
+            sep, unit = unit
         else:
-            formatter = ScalarFormatter()
-
-        return formatter
+            sep = "" if not unit else " "
+        return EngFormatter(unit, sep=sep)
 
 
 @dataclass

```
