# Refactor ISP-023 (ISP): GeneratorUntypedBase has methods related to capturing results and generator t...

**Status:** `patch_failed`  
**Branch:** `refactor/ISP-023` -> `main`  
**Head commit:** `2a3e90bc5cf75ef551e4552f2be95f31800d55c5`  
**LLM finish:** `FinishReason.STOP` (prompt 3543, completion 98)  

## Detected issue

- **File**: `extras/catch_amalgamated.hpp`
- **Entity**: `GeneratorUntypedBase` (class)
- **Lines (at detection time)**: L1062–L1136
- **Severity**: low
- **Confidence**: detected by 3 scan(s)

**Description.** GeneratorUntypedBase has methods related to capturing results and generator tracking, which might be unrelated to its core purpose.

**Reasoning.** The GeneratorUntypedBase class includes methods like missingCaptureInstance() and getResultCapture(). These methods seem to relate to result capturing and generator tracking, which might be separate concerns from the core generator functionality. If a concrete generator implementation doesn't need these, it's forced to depend on them.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 0

## Apply error

```
no patch blocks produced by LLM
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `extras/catch_amalgamated.hpp` | 10496 → - | 3 → - | 425 → - | 1273 → - | 0 → - |

## Diff

*(no diff — patch was not applied)*
