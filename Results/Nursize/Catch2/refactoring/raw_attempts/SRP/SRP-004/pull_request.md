# Refactor SRP-004 (SRP): Interface combines responsibilities for assertion handling, section tracking,...

**Status:** `patch_failed`  
**Branch:** `refactor/SRP-004` -> `main`  
**Head commit:** `35e191d1c2f08e9b285da19cba8ba76d54d727e1`  
**LLM finish:** `FinishReason.STOP` (prompt 3884, completion 1063)  

## Detected issue

- **File**: `extras/catch_amalgamated.hpp`
- **Entity**: `Catch::IResultCapture` (class)
- **Lines (at detection time)**: L357–L417
- **Severity**: high
- **Confidence**: detected by 1 scan(s)

**Description.** Interface combines responsibilities for assertion handling, section tracking, generator tracking, and benchmark reporting.

**Reasoning.** The `IResultCapture` interface defines methods for handling a wide array of distinct events: assertion lifecycle (`notifyAssertionStarted`, `handleExpr`, `handleMessage`, etc.), section lifecycle (`sectionStarted`, `sectionEnded`), generator lifecycle (`acquireGeneratorTracker`, `createGeneratorTracker`), and benchmark events (`benchmarkPreparing`, `benchmarkStarting`, `benchmarkEnded`, `benchmarkFailed`). These are separate reasons for a concrete implementation to change, making it difficult for any single class implementing this interface to adhere to SRP.

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
| `extras/catch_amalgamated.hpp` | 10495 → - | 3 → - | 433.67 → - | 1299 → - | 0 → - |

## Diff

*(no diff — patch was not applied)*
