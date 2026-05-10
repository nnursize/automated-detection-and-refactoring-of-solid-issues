# Refactor ISP-014 (ISP): The WriterBasedJsonGenerator class is forced to implement writeRawUTF8String...

**Status:** `patch_failed`  
**Branch:** `refactor/ISP-014` -> `main`  
**Head commit:** `5650ed69e32cc1205ea2281f12c8a5b6bcfeaebf`  
**LLM finish:** `FinishReason.STOP` (prompt 3599, completion 258)  

## Detected issue

- **File**: `src/main/java/tools/jackson/core/json/WriterBasedJsonGenerator.java`
- **Entity**: `WriterBasedJsonGenerator.writeRawUTF8String` (method)
- **Lines (at detection time)**: L572–L574
- **Severity**: high
- **Confidence**: detected by 1 scan(s)

**Description.** The WriterBasedJsonGenerator class is forced to implement writeRawUTF8String but explicitly reports it as an unsupported operation.

**Reasoning.** The 'JsonGenerator' interface mandates writing raw UTF8 byte arrays. However, 'WriterBasedJsonGenerator' operates on character streams (Writer). It explicitly calls '_reportUnsupportedOperation()' for 'writeRawUTF8String()', demonstrating it cannot natively support this byte-oriented operation. This forces the class to implement a method it doesn't need or can't efficiently handle, indicating a violation of ISP in the 'JsonGenerator' interface.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 0

**Summary.** Remove unsupported UTF8-based write methods from WriterBasedJsonGenerator

**Rationale.** WriterBasedJsonGenerator is a character-based generator and does not support byte-based UTF8 writing. By removing these methods, we avoid the ISP violation of forcing an implementation that only throws an exception. Note: This assumes the JsonGenerator interface allows for these methods to be optional or that the hierarchy can be refactored to separate byte-based and character-based generators.

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
