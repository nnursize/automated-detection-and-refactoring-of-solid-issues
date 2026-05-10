# Refactor SRP-006 (SRP): The class combines output stream management, JSON structural generation, JSON...

**Status:** `patch_failed`  
**Branch:** `refactor/SRP-006` -> `main`  
**Head commit:** `4235320743d5749dccc98566673fa73c105b16a6`  
**LLM finish:** `FinishReason.MAX_TOKENS` (prompt 24030, completion 34618)  

## Detected issue

- **File**: `src/main/java/tools/jackson/core/json/UTF8JsonGenerator.java`
- **Entity**: `UTF8JsonGenerator` (class)
- **Lines (at detection time)**: L14–L1032
- **Severity**: high
- **Confidence**: detected by 6 scan(s)

**Description.** The class combines output stream management, JSON structural generation, JSON name writing, string/text encoding and escaping, raw UTF-8 string handling, Base64 encoding, numeric formatting, boolean/null writing, and detailed character encoding/escaping logic.

**Reasoning.** This class is a severe SRP violator, acting as a 'God class' for UTF-8 JSON generation. It manages the `OutputStream` and internal byte buffers (`_flushBuffer()`, `_writeBytes()`), handles JSON structure (`writeStartArray()`), property names (`writeName()`), and various value types. Crucially, it contains highly specialized logic for character encoding and escaping (`_writeStringSegment2()`, `_outputSurrogatePair()`, `_writeGenericEscape()`), Base64 encoding (`_writeBinary()`), and numeric formatting (`writeNumber()`). A change in any of these areas would require modifying this single, large, and complex class.

## Fix logic

- **Model**: `gemini-2.5-flash` (temperature 0.2)
- **Patch blocks**: 0

**Summary.** Extracts character encoding, escaping, and Base64 logic into UTF8WriterDelegate.

**Rationale.** The `UTF8JsonGenerator` class was a 'God class' responsible for too many concerns, including detailed character encoding and escaping, and Base64 encoding. This refactoring extracts these specialized responsibilities into a new helper class, `UTF8WriterDelegate`. The delegate handles the complex byte-level transformations, while `UTF8JsonGenerator` retains its core responsibility of JSON structure generation and buffer management. This significantly reduces the complexity of `UTF8JsonGenerator` and improves adherence to the Single Responsibility Principle by separating concerns related to data transformation from concerns related to JSON structure and output buffering.

## Apply error

```
LLM response was truncated (finish_reason=FinishReason.MAX_TOKENS, completion_tokens=34618). Parsed patch blocks were discarded and no changes were applied. Try splitting the issue into a smaller refactor or switching models.
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/main/java/tools/jackson/core/json/UTF8JsonGenerator.java` | 2058 → - | 84 → - | 5.74 → - | 399 → - | 0 → - |

## Diff

*(no diff — patch was not applied)*
