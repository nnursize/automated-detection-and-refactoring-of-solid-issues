# Refactor LSP-002 (LSP): Method uses explicit type-checking to handle subclasses differently, violatin...

**Status:** `patch_failed`  
**Branch:** `refactor/LSP-002` -> `main`  
**Head commit:** `19ea9134d8be76c87a8e6c8ed3d5b9deaa6386db`  
**LLM finish:** `FinishReason.STOP` (prompt 8782, completion 1075)  

## Detected issue

- **File**: `seaborn/_core/properties.py`
- **Entity**: `IntervalProperty.get_mapping` (method)
- **Lines (at detection time)**: L133–L158
- **Severity**: medium
- **Confidence**: detected by 3 scan(s)

**Description.** Method uses explicit type-checking to handle subclasses differently, violating the abstraction of the base class.

**Reasoning.** The get_mapping method in IntervalProperty uses isinstance to check for specific subclasses of Scale (Nominal and Boolean). This violates LSP as it indicates that the Property hierarchy is not truly decoupled from the Scale hierarchy; the base class contract of Scale is insufficient for IntervalProperty, which must instead rely on specific knowledge of Scale's subtypes to function correctly.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 0

**Summary.** Refactor IntervalProperty.get_mapping to use polymorphic dispatch instead of isinstance checks.

**Rationale.** By adding a get_mapping method to the Scale classes (Nominal and Boolean), IntervalProperty can delegate the mapping logic to the scale object itself, removing the need for explicit type-checking and adhering to the Liskov Substitution Principle.

## Apply error

```
no patch blocks produced by LLM
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `seaborn/_core/properties.py` | 587 → - | 55 → - | 2.89 → - | 12 → - | 23.43 → - |

## Diff

*(no diff — patch was not applied)*
