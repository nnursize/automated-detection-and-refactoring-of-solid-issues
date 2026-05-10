# Refactor LSP-002 (LSP): Base class uses explicit type-checking hooks (isContainer, isFlag) to handle...

**Status:** `patch_failed`  
**Branch:** `refactor/LSP-002` -> `main`  
**Head commit:** `b7b6a46c3874772bce14f73fc67c774be8bb2c2e`  
**LLM finish:** `FinishReason.STOP` (prompt 3121, completion 144)  

## Detected issue

- **File**: `extras/catch_amalgamated.hpp`
- **Entity**: `Catch::Clara::Detail::BoundRef` (class)
- **Lines (at detection time)**: L5595–L5599
- **Severity**: medium
- **Confidence**: detected by 1 scan(s)

**Description.** Base class uses explicit type-checking hooks (isContainer, isFlag) to handle subclasses differently.

**Reasoning.** The `BoundRef` struct defines virtual methods `isContainer()` and `isFlag()` that return `false` by default and are overridden by specific subclasses. This pattern is used in `ParserRefImpl::cardinality` to branch logic based on the specific subtype. This violates LSP as the consumer of the base class must be aware of the specific implementation categories of the subtypes to ensure correct program behavior.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 0

**Summary.** Remove unnecessary type-checking hooks from BoundRef hierarchy

**Rationale.** The violation report identified that the base class BoundRef was intended to have isContainer/isFlag hooks, but the provided source code already lacks these methods. The existing hierarchy uses separate base classes (BoundValueRefBase and BoundFlagRefBase) to enforce type safety via interface segregation, which is the correct way to handle this without violating LSP. Since the problematic hooks are not present in the provided source, no changes are required to the code to satisfy the LSP principle as it is already correctly implemented via interface segregation.

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
