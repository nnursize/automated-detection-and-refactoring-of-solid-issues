# Refactor SRP-051 (SRP): The RunContext class acts as a 'God Object,' encompassing responsibilities fo...

**Status:** `llm_error`  
**Branch:** `refactor/SRP-051` -> `main`  
**Head commit:** `41de562d56a553d72414f348724359c474bc5345`  

## Detected issue

- **File**: `extras/catch_amalgamated.hpp`
- **Entity**: `RunContext` (class)
- **Lines (at detection time)**: L10653–L10786
- **Severity**: high
- **Confidence**: detected by 3 scan(s)

**Description.** The RunContext class acts as a 'God Object,' encompassing responsibilities for test execution, assertion capture, section management, generator tracking, benchmark handling, reporting coordination, configuration caching, output redirection, fatal error handling, and concurrency management.

**Reasoning.** This class is responsible for nearly every aspect of a test run. Any change to how tests are executed, how results are captured, how sections or generators are managed, how benchmarks are processed, how reporting is coordinated, or how fatal errors are handled would require modifications to this single class. This violates SRP by having far too many reasons to change and managing too many disparate concerns.

## LLM / runtime error

```
unhandled error: FatalLLMError: Server unavailable (503) — skipping to preserve quota: 503 UNAVAILABLE. {'error': {'code': 503, 'message': 'This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.', 'status': 'UNAVAILABLE'}}
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `extras/catch_amalgamated.hpp` | 10500 → - | 3 → - | 433.67 → - | 1299 → - | 0 → - |

## Diff

*(no diff — patch was not applied)*
