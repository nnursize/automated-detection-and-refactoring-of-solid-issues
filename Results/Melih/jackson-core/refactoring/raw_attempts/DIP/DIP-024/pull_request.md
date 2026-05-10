# Refactor DIP-024 (DIP): Abstract base class hard-codes dependency on concrete PrettyPrinter

**Status:** `patch_failed`  
**Branch:** `refactor/DIP-024` -> `main`  
**Head commit:** `ad97fd088b013aa530f0a76273739381cb67c8cd`  
**LLM finish:** `FinishReason.STOP` (prompt 5336, completion 295)  

## Detected issue

- **File**: `src/main/java/tools/jackson/core/base/GeneratorBase.java`
- **Entity**: `GeneratorBase._constructDefaultPrettyPrinter` (method)
- **Lines (at detection time)**: L377–L379
- **Severity**: medium
- **Confidence**: detected by 2 scan(s)

**Description.** Abstract base class hard-codes dependency on concrete PrettyPrinter

**Reasoning.** The abstract class GeneratorBase directly instantiates DefaultPrettyPrinter (L378). Abstractions should not depend on details; hard-coding a specific implementation of an interface in a base class prevents users from easily substituting different defaults.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 0

**Summary.** Remove hard-coded dependency on DefaultPrettyPrinter in GeneratorBase

**Rationale.** The Dependency Inversion Principle is violated when an abstract class directly instantiates a concrete implementation. By changing _constructDefaultPrettyPrinter to return a new instance of DefaultPrettyPrinter, we keep the existing behavior while allowing subclasses to override this factory method to provide different implementations if needed.

## Apply error

```
no patch blocks produced by LLM
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/main/java/tools/jackson/core/base/GeneratorBase.java` | 387 → - | 23 → - | 2.87 → - | 44 → - | 0 → - |

## Diff

*(no diff — patch was not applied)*
