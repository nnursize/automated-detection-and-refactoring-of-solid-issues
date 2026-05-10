# Refactor ISP-008 (ISP): The `BinaryTSFactory` is forced to implement character-based parser creation...

**Status:** `patch_failed`  
**Branch:** `refactor/ISP-008` -> `main`  
**Head commit:** `5650ed69e32cc1205ea2281f12c8a5b6bcfeaebf`  
**LLM finish:** `FinishReason.STOP` (prompt 3357, completion 224)  

## Detected issue

- **File**: `src/main/java/tools/jackson/core/base/BinaryTSFactory.java`
- **Entity**: `BinaryTSFactory` (class)
- **Lines (at detection time)**: L15–L247
- **Severity**: medium
- **Confidence**: detected by 1 scan(s)

**Description.** The `BinaryTSFactory` is forced to implement character-based parser creation methods but explicitly throws `_nonByteSource()` (which throws `UnsupportedOperationException`).

**Reasoning.** The `BinaryTSFactory` is designed to create parsers for binary input. However, it inherits methods like `createParser(Reader r)`, `createParser(String content)`, and `createParser(char[] content, int offset, int len)` from `TokenStreamFactory`. For these character-based input types, `BinaryTSFactory` explicitly calls `_nonByteSource()` (L97, L118, L124), which then throws `UnsupportedOperationException`. This forces the factory to implement methods for input types it does not support, violating ISP. These methods should be segregated into a `CharSourceTokenStreamFactory` or similar interface.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 0

**Summary.** Refactor BinaryTSFactory to avoid implementing character-based parser/generator methods.

**Rationale.** The Interface Segregation Principle is violated because BinaryTSFactory is forced to implement methods for character-based inputs that it cannot support. By moving these methods to a separate interface (or in this case, acknowledging that the current hierarchy forces this, and the requested fix is to segregate), I am unable to modify the base class TokenStreamFactory without breaking the entire library's API. However, the prompt asks to resolve the ISP violation. Since I cannot change the base class hierarchy (TokenStreamFactory) without breaking the public API, I will provide a solution that removes the explicit UnsupportedOperationException methods from BinaryTSFactory by ensuring it doesn't implement the full interface if possible, or by acknowledging that the current design is constrained by the base class. Given the constraints, I will output NO blocks as a safe refactor is not possible without breaking the public API of TokenStreamFactory.

## Apply error

```
no patch blocks produced by LLM
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/main/java/tools/jackson/core/base/BinaryTSFactory.java` | 206 → - | 17 → - | 1.65 → - | 12 → - | 0 → - |

## Diff

*(no diff — patch was not applied)*
