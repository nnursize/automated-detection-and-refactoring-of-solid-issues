# Refactor LSP-008 (LSP): Subclass implementation throws UnsupportedOperationException for a method def...

**Status:** `patch_failed`  
**Branch:** `refactor/LSP-008` -> `main`  
**Head commit:** `c445684d3c509e85f30ab38aa81d30048b3bda64`  
**LLM finish:** `FinishReason.STOP` (prompt 3550, completion 373)  

## Detected issue

- **File**: `src/main/java/tools/jackson/core/json/WriterBasedJsonGenerator.java`
- **Entity**: `WriterBasedJsonGenerator.writeUTF8String` (class)
- **Lines (at detection time)**: L449–L452
- **Severity**: high
- **Confidence**: detected by 2 scan(s)

**Description.** Subclass implementation throws UnsupportedOperationException for a method defined in the base class.

**Reasoning.** Similar to writeRawUTF8String, the base class JsonGenerator defines writeUTF8String as part of its public API. The subclass implementation explicitly refuses to support this method, breaking the contract established by the base class.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 0

**Summary.** Implement writeUTF8String and writeRawUTF8String in WriterBasedJsonGenerator

**Rationale.** The previous implementation threw UnsupportedOperationException, violating the Liskov Substitution Principle. By implementing these methods using UTF-8 decoding, we satisfy the contract of the JsonGenerator base class.

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
