# Refactor ISP-012 (ISP): The GeneratorBase class is forced to implement writeString from a Reader but...

**Status:** `patch_failed`  
**Branch:** `refactor/ISP-012` -> `main`  
**Head commit:** `d5e5fd92e8534a70406271f72c8d497a33ebeeba`  
**LLM finish:** `FinishReason.STOP` (prompt 5359, completion 202)  

## Detected issue

- **File**: `src/main/java/tools/jackson/core/base/GeneratorBase.java`
- **Entity**: `GeneratorBase.writeString(Reader reader, int len)` (method)
- **Lines (at detection time)**: L229–L231
- **Severity**: high
- **Confidence**: detected by 1 scan(s)

**Description.** The GeneratorBase class is forced to implement writeString from a Reader but explicitly reports it as an unsupported operation.

**Reasoning.** The 'JsonGenerator' interface mandates a method for writing string content from a 'Reader'. 'GeneratorBase', a common abstract base for generators, explicitly calls '_reportUnsupportedOperation()' for 'writeString(Reader, int)'. This indicates that this method is not universally supported by all generator types (e.g., byte-based generators might not handle character readers efficiently), making the 'JsonGenerator' interface too large and forcing implementations to declare methods they do not support.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 0

**Summary.** Remove unsupported writeString(Reader, int) from GeneratorBase

**Rationale.** The method writeString(Reader, int) is not universally supported by all JsonGenerator implementations. By removing it from the base class, we avoid forcing implementations to override it just to throw an exception, adhering to the Interface Segregation Principle. This method should be moved to a more specific interface (e.g., ReaderBasedGenerator) or handled via optional capability checks.

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
