# Refactor DIP-023 (DIP): Direct instantiation of concrete UTF8Writer.

**Status:** `patch_failed`  
**Branch:** `refactor/DIP-023` -> `main`  
**Head commit:** `5650ed69e32cc1205ea2281f12c8a5b6bcfeaebf`  
**LLM finish:** `FinishReason.STOP` (prompt 4377, completion 458)  

## Detected issue

- **File**: `src/main/java/tools/jackson/core/base/TextualTSFactory.java`
- **Entity**: `TextualTSFactory._createWriter` (class)
- **Lines (at detection time)**: L339–L346
- **Severity**: high
- **Confidence**: detected by 3 scan(s)

**Description.** Direct instantiation of concrete UTF8Writer.

**Reasoning.** The _createWriter method directly instantiates UTF8Writer, coupling the factory to a specific implementation of the Writer abstraction instead of allowing for the injection of different writer types.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 0

**Summary.** Introduce a factory method for creating UTF8Writer to decouple TextualTSFactory from the concrete implementation.

**Rationale.** By moving the instantiation of UTF8Writer into a protected factory method, we allow subclasses to override the creation logic, adhering to the Dependency Inversion Principle.

## Apply error

```
no patch blocks produced by LLM
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/main/java/tools/jackson/core/base/TextualTSFactory.java` | 303 → - | 17 → - | 2.76 → - | 31 → - | 0 → - |

## Diff

*(no diff — patch was not applied)*
