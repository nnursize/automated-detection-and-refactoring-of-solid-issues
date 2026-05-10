# Refactor ISP-002 (ISP): IConfig interface has too many methods, potentially forcing implementations t...

**Status:** `patch_failed`  
**Branch:** `refactor/ISP-002` -> `main`  
**Head commit:** `4e2fc2dad834aa20fef855b5c3f9c851106412f3`  
**LLM finish:** `FinishReason.STOP` (prompt 3166, completion 136)  

## Detected issue

- **File**: `src/catch2/internal/catch_run_context.hpp`
- **Entity**: `IConfig` (class)
- **Lines (at detection time)**: L30–L161
- **Severity**: medium
- **Confidence**: detected by 3 scan(s)

**Description.** IConfig interface has too many methods, potentially forcing implementations to provide unused functionality.

**Reasoning.** The IConfig interface appears to be quite large, with numerous methods for configuring various aspects of the test runner. If an implementation of IConfig only needs a subset of these configurations, it would be forced to implement all methods, even those it doesn't use. This violates the ISP, as clients (or the RunContext in this case) that only depend on a few configuration options are indirectly coupled to the entire interface. It would be better to break this down into smaller, more focused interfaces.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 0

**Summary.** Refactor IConfig to avoid modifying it directly, as it is defined in a different header.

**Rationale.** The IConfig interface is defined in `catch2/interfaces/catch_interfaces_config.hpp` (implied by the project structure), not `catch2/internal/catch_run_context.hpp`. Modifying it here would be incorrect. The violation report incorrectly identified the file as the location of the interface definition. I will not perform an unsafe refactor on a file that only forward-declares the interface.

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
