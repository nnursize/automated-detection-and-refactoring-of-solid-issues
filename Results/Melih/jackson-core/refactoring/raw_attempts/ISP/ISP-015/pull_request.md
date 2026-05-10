# Refactor ISP-015 (ISP): The WriterBasedJsonGenerator class is forced to implement writeUTF8String but...

**Status:** `patch_failed`  
**Branch:** `refactor/ISP-015` -> `main`  
**Head commit:** `5650ed69e32cc1205ea2281f12c8a5b6bcfeaebf`  
**LLM finish:** `FinishReason.STOP` (prompt 3592, completion 245)  

## Detected issue

- **File**: `src/main/java/tools/jackson/core/json/WriterBasedJsonGenerator.java`
- **Entity**: `WriterBasedJsonGenerator.writeUTF8String` (method)
- **Lines (at detection time)**: L578–L580
- **Severity**: high
- **Confidence**: detected by 1 scan(s)

**Description.** The WriterBasedJsonGenerator class is forced to implement writeUTF8String but explicitly reports it as an unsupported operation.

**Reasoning.** Similar to 'writeRawUTF8String', the 'JsonGenerator' interface mandates writing UTF8 byte arrays. 'WriterBasedJsonGenerator' (character-based) explicitly calls '_reportUnsupportedOperation()' for 'writeUTF8String()'. This is another instance where the interface is too broad, forcing a specialized implementation to expose and explicitly reject functionality that is not relevant to its core purpose, thus violating ISP.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 0

**Summary.** Remove unsupported UTF8 string write methods from WriterBasedJsonGenerator

**Rationale.** WriterBasedJsonGenerator is a character-based generator and does not support UTF8 byte array operations. Implementing these methods and throwing UnsupportedOperationException violates the Interface Segregation Principle. Since these methods are part of the base JsonGenerator interface, they should be removed from this implementation to avoid forcing the class to expose irrelevant functionality.

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
