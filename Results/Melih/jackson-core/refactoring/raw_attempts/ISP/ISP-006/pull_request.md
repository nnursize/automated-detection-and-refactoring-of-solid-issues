# Refactor ISP-006 (ISP): Implementation forced to throw UnsupportedOperationException for a method it...

**Status:** `patch_failed`  
**Branch:** `refactor/ISP-006` -> `main`  
**Head commit:** `d5e5fd92e8534a70406271f72c8d497a33ebeeba`  
**LLM finish:** `FinishReason.STOP` (prompt 3528, completion 227)  

## Detected issue

- **File**: `src/main/java/tools/jackson/core/json/WriterBasedJsonGenerator.java`
- **Entity**: `WriterBasedJsonGenerator.writeRawUTF8String` (class)
- **Lines (at detection time)**: L361–L364
- **Severity**: low
- **Confidence**: detected by 2 scan(s)

**Description.** Implementation forced to throw UnsupportedOperationException for a method it cannot support.

**Reasoning.** Similar to UTF8JsonGenerator, this class is forced to implement a method from the fat JsonGenerator interface that it cannot support, violating ISP.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 0

**Summary.** Remove unsupported UTF8 string writing methods from WriterBasedJsonGenerator

**Rationale.** WriterBasedJsonGenerator is designed for character-based output (Writer). Implementing UTF8-specific methods that throw UnsupportedOperationException violates the Interface Segregation Principle. These methods should be removed as they are not applicable to this implementation.

## Apply error

```
no patch blocks produced by LLM
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/main/java/tools/jackson/core/json/WriterBasedJsonGenerator.java` | 1820 → - | 80 → - | 5.03 → - | 323 → - | 0 → - |

## Diff

*(no diff — patch was not applied)*
