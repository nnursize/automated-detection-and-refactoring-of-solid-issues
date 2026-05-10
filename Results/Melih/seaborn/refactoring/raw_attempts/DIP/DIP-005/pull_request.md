# Refactor DIP-005 (DIP): Direct instantiation of Subplots manager.

**Status:** `patch_failed`  
**Branch:** `refactor/DIP-005` -> `main`  
**Head commit:** `a2f681d99ab0fe40df9069b65c343785c681bb96`  
**LLM finish:** `FinishReason.STOP` (prompt 4502, completion 373)  

## Detected issue

- **File**: `seaborn/_core/plot.py`
- **Entity**: `Plotter._setup_figure` (method)
- **Lines (at detection time)**: L955–L955
- **Severity**: low
- **Confidence**: detected by 3 scan(s)

**Description.** Direct instantiation of Subplots manager.

**Reasoning.** The Plotter class directly instantiates the Subplots class. While both are internal to the new objects interface, this direct creation prevents the inversion of control that would allow different subplot strategies to be injected into the compilation engine.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 2
- **Files modified** (1): `seaborn/_core/plot.py`

**Summary.** Inject Subplots factory into Plotter to decouple from concrete Subplots class.

**Rationale.** By allowing the Subplots manager to be provided (or defaulting to the concrete class), we remove the hard-coded dependency in Plotter._setup_figure, adhering to the Dependency Inversion Principle.

## Changes overview

_2 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `seaborn/_core/plot.py` (10-line block → 14-line replacement)

**Replaces:**

```python
    def __init__(self, pyplot=None, theme=None):
        if pyplot is None:
            import matplotlib.pyplot as plt
            pyplot = plt
        if theme is None:
            from seaborn._core.rules import theme_context
            theme = {}

        self._pyplot = pyplot
        self._theme = theme
```

**With:**

```python
    def __init__(self, pyplot=None, theme=None, subplots_cls=None):
        if pyplot is None:
            import matplotlib.pyplot as plt
            pyplot = plt
        if theme is None:
            from seaborn._core.rules import theme_context
            theme = {}
        if subplots_cls is None:
            from seaborn._core.subplots import Subplots
            subplots_cls = Subplots

        self._pyplot = pyplot
        self._theme = theme
        self._subplots_cls = subplots_cls
```

### 2. EDIT `seaborn/_core/plot.py` (3-line block → 3-line replacement)

**Replaces:**

```python
        self._subplots = subplots = Subplots(subplot_spec, facet_spec, pair_spec)

        # --- Figure initialization
```

**With:**

```python
        self._subplots = subplots = self._subplots_cls(subplot_spec, facet_spec, pair_spec)

        # --- Figure initialization
```

## Apply error

```
search_text not found in seaborn/_core/plot.py (block 0)
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `seaborn/_core/plot.py` | 1292 → - | 58 → - | 5.22 → - | 31 → - | 0 → - |

## Diff

*(no diff — patch was not applied)*
