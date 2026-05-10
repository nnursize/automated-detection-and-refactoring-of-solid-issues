# Refactor LSP-010 (LSP): Manual RTTI methods indicate a leaky abstraction where subtypes are not subst...

**Status:** `patch_failed`  
**Branch:** `refactor/LSP-010` -> `main`  
**Head commit:** `b7b6a46c3874772bce14f73fc67c774be8bb2c2e`  
**LLM finish:** `FinishReason.STOP` (prompt 3555, completion 129)  

## Detected issue

- **File**: `extras/catch_amalgamated.hpp`
- **Entity**: `ITracker` (class)
- **Lines (at detection time)**: L2453–L2525
- **Severity**: medium
- **Confidence**: detected by 1 scan(s)

**Description.** Manual RTTI methods indicate a leaky abstraction where subtypes are not substitutable without type-checking

**Reasoning.** Type-checking smell -> LSP violation because the interface uses virtual boolean methods (isSectionTracker at line 2516, isGeneratorTracker at line 2522) to perform manual Run-Time Type Information (RTTI). This design pattern indicates that the base ITracker abstraction is insufficient, forcing callers to perform type-checks and downcasts to access subtype-specific behavior. This violates the principle that subtypes should be usable through their base interface without the caller needing to know or handle specific concrete classes differently.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 0

**Summary.** Remove manual RTTI methods from ITracker interface

**Rationale.** The violation report identified manual RTTI methods (isSectionTracker, isGeneratorTracker) as LSP violations. While the provided source code snippet for `extras/catch_amalgamated.hpp` does not explicitly show these methods in the `ITracker` class definition (they were likely in a different version or location), the interface design should be cleaned to ensure no such methods exist, enforcing proper polymorphism instead of type-checking.

## Apply error

```
no patch blocks produced by LLM
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `extras/catch_amalgamated.hpp` | 10459 → - | 3 → - | 425 → - | 1273 → - | 0 → - |

## Diff

*(no diff — patch was not applied)*
