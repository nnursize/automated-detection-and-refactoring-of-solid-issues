# Refactor OCP-020 (OCP): Hardcoded switch on configuration protocol strings

**Status:** `patch_failed`  
**Branch:** `refactor/OCP-020` -> `main`  
**Head commit:** `705051ab73604540c6a9008bdafefcf491c9fc04`  
**LLM finish:** `FinishReason.STOP` (prompt 12262, completion 722)  

## Detected issue

- **File**: `logstash-core/src/main/java/org/logstash/execution/AbstractPipelineExt.java`
- **Entity**: `AbstractPipelineExt.getPipelineSourceDetails` (method)
- **Lines (at detection time)**: L582–L605
- **Severity**: medium
- **Confidence**: detected by 3 scan(s)

**Description.** Hardcoded switch on configuration protocol strings

**Reasoning.** The method uses a switch statement to map protocol strings ('string', 'file', 'x-pack-metrics', etc.) to human-readable descriptions. This violates OCP because introducing a new configuration source requires modifying the core pipeline class. Instead, the source metadata objects should provide their own descriptive details polymorphically.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 0

**Summary.** Refactor pipeline source details to use polymorphic description method

**Rationale.** The switch statement in AbstractPipelineExt.getPipelineSourceDetails violates the Open/Closed Principle. By moving the responsibility of providing a description to the SourceWithMetadata class (or a new interface), we allow new source types to be added without modifying the core pipeline logic.

## Apply error

```
no patch blocks produced by LLM
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `logstash-core/src/main/java/org/logstash/execution/AbstractPipelineExt.java` | 777 → - | 61 → - | 1.82 → - | 51 → - | 0 → - |

## Diff

*(no diff — patch was not applied)*
