# Refactor LSP-007 (LSP): Subclass implementation throws UnsupportedOperationException for a method def...

**Status:** `patch_failed`  
**Branch:** `refactor/LSP-007` -> `main`  
**Head commit:** `c445684d3c509e85f30ab38aa81d30048b3bda64`  
**LLM finish:** `FinishReason.STOP` (prompt 3560, completion 388)  

## Detected issue

- **File**: `src/main/java/tools/jackson/core/json/WriterBasedJsonGenerator.java`
- **Entity**: `WriterBasedJsonGenerator.writeRawUTF8String` (class)
- **Lines (at detection time)**: L444–L447
- **Severity**: high
- **Confidence**: detected by 2 scan(s)

**Description.** Subclass implementation throws UnsupportedOperationException for a method defined in the base class.

**Reasoning.** The base class JsonGenerator defines writeRawUTF8String as part of its public API. By overriding it to throw an UnsupportedOperationException, the subclass violates the Liskov Substitution Principle because it cannot be used in any context where the base class is expected to support this operation.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 0

**Summary.** Implement writeRawUTF8String and writeUTF8String in WriterBasedJsonGenerator

**Rationale.** Replacing UnsupportedOperationException with actual implementations ensures Liskov Substitution Principle compliance. Since WriterBasedJsonGenerator uses a Writer, we convert the UTF-8 bytes to characters using a decoder or by writing them as raw bytes if the underlying writer supports it, but for simplicity and correctness in a character-based generator, we decode the UTF-8 bytes to a String and write it.

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
