# Refactor LSP-013 (LSP): Subclasses are forced to throw UnsupportedOperationException for specific wri...

**Status:** `patch_failed`  
**Branch:** `refactor/LSP-013` -> `main`  
**Head commit:** `c445684d3c509e85f30ab38aa81d30048b3bda64`  
**LLM finish:** `FinishReason.STOP` (prompt 5302, completion 463)  

## Detected issue

- **File**: `src/main/java/tools/jackson/core/base/GeneratorBase.java`
- **Entity**: `GeneratorBase.writeString` (class)
- **Lines (at detection time)**: L229–L231
- **Severity**: high
- **Confidence**: detected by 1 scan(s)

**Description.** Subclasses are forced to throw UnsupportedOperationException for specific write methods

**Reasoning.** The base class provides an implementation that throws UnsupportedOperationException for methods like writeString(Reader, int). This breaks the substitutability principle because a client expects a working JsonGenerator implementation, not one that fails at runtime for standard interface methods.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 0

**Summary.** Remove UnsupportedOperationException from default implementations in GeneratorBase

**Rationale.** The Liskov Substitution Principle is violated when base class methods throw UnsupportedOperationException for standard interface operations. While these methods are intended to be overridden, they should provide a default implementation (e.g., using writeString(String)) or be marked abstract to force implementation, rather than throwing runtime exceptions that break client expectations.

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
