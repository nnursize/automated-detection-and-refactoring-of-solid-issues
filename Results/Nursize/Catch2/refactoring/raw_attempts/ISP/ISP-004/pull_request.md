# Refactor ISP-004 (ISP): IEventListener interface has too many methods, potentially forcing implementa...

**Status:** `patch_failed`  
**Branch:** `refactor/ISP-004` -> `main`  
**Head commit:** `4e2fc2dad834aa20fef855b5c3f9c851106412f3`  
**LLM finish:** `FinishReason.STOP` (prompt 3160, completion 111)  

## Detected issue

- **File**: `src/catch2/internal/catch_run_context.hpp`
- **Entity**: `IEventListener` (class)
- **Lines (at detection time)**: L31–L161
- **Severity**: medium
- **Confidence**: detected by 3 scan(s)

**Description.** IEventListener interface has too many methods, potentially forcing implementations to provide unused functionality.

**Reasoning.** The IEventListener interface seems to have a large number of methods for reporting various events during test execution. An implementation that only cares about a subset of these events (e.g., only test start/end, or only assertion failures) would still need to provide implementations for all methods. This violates ISP, as clients that only need a few event notifications are forced to depend on the entire interface. It might be beneficial to split this into smaller, more specific listener interfaces.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 0

**Summary.** Give up on ISP refactoring for IEventListener due to high complexity and risk of breaking public API.

**Rationale.** The IEventListener interface is a core component of Catch2's reporter system. Splitting it into smaller interfaces would require significant changes to the entire reporter infrastructure, including all existing reporter implementations, which would break the public API and violate the constraint of preserving existing behavior without massive, high-risk refactoring.

## Apply error

```
no patch blocks produced by LLM
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/catch2/internal/catch_run_context.hpp` | 116 → - | 0 → - | 12 → - | 12 → - | 0 → - |

## Diff

*(no diff — patch was not applied)*
