# Refactor OCP-004 (OCP): The IConfig interface is too large, requiring modification for new configurat...

**Status:** `patch_failed`  
**Branch:** `refactor/OCP-004` -> `main`  
**Head commit:** `017928ca08b9fa5c327391e5c70d8798c14ddeb2`  
**LLM finish:** `FinishReason.STOP` (prompt 3868, completion 111)  

## Detected issue

- **File**: `extras/catch_amalgamated.hpp`
- **Entity**: `Catch::IConfig` (class)
- **Lines (at detection time)**: L485–L535
- **Severity**: medium
- **Confidence**: detected by 2 scan(s)

**Description.** The IConfig interface is too large, requiring modification for new configuration options.

**Reasoning.** The 'Fat Interface' smell is present in `IConfig`. It exposes a wide range of configuration settings. If a new configuration option is introduced in Catch2, a new pure virtual getter method would need to be added to `IConfig`. This would necessitate modifying all concrete implementations of `IConfig` (e.g., `Catch::Config`), violating the Open/Closed Principle.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 0

**Summary.** No changes possible to resolve OCP violation in IConfig without breaking binary compatibility or public API.

**Rationale.** The IConfig interface in Catch2 is a core, stable public interface. Modifying it to use a generic property bag or visitor pattern would require changing every single implementation and consumer of the interface, which violates the requirement to preserve public API and existing behavior. Given the constraints, no safe refactor is possible.

## Apply error

```
no patch blocks produced by LLM
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `extras/catch_amalgamated.hpp` | 10491 → - | 3 → - | 433 → - | 1297 → - | 0 → - |

## Diff

*(no diff — patch was not applied)*
