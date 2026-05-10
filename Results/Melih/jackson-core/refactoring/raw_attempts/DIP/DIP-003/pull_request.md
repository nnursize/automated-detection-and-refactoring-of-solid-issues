# Refactor DIP-003 (DIP): Direct instantiation of StreamWriteException.

**Status:** `patch_failed`  
**Branch:** `refactor/DIP-003` -> `main`  
**Head commit:** `5650ed69e32cc1205ea2281f12c8a5b6bcfeaebf`  
**LLM finish:** `FinishReason.STOP` (prompt 4083, completion 444)  

## Detected issue

- **File**: `src/main/java/tools/jackson/core/JsonGenerator.java`
- **Entity**: `JsonGenerator._constructWriteException` (method)
- **Lines (at detection time)**: L1118–L1118
- **Severity**: low
- **Confidence**: detected by 4 scan(s)

**Description.** Direct instantiation of StreamWriteException.

**Reasoning.** The base class for generators directly instantiates a concrete exception type. While common in Java, strictly speaking, this couples the generator abstraction to a specific detail (the exception implementation).

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 0

**Summary.** Introduce an abstract factory method for creating StreamWriteException to decouple JsonGenerator from the concrete implementation.

**Rationale.** The JsonGenerator class was directly instantiating StreamWriteException. By introducing a protected abstract method _constructWriteException, subclasses can provide the specific exception implementation, adhering to the Dependency Inversion Principle.

## Apply error

```
no patch blocks produced by LLM
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/main/java/tools/jackson/core/JsonGenerator.java` | 2229 → - | 66 → - | 8.45 → - | 493 → - | 0 → - |

## Diff

*(no diff — patch was not applied)*
