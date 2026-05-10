# Refactor LSP-011 (LSP): Subclass violates LSP by throwing UnsupportedOperationException for a method...

**Status:** `patch_failed`  
**Branch:** `refactor/LSP-011` -> `main`  
**Head commit:** `c445684d3c509e85f30ab38aa81d30048b3bda64`  
**LLM finish:** `FinishReason.STOP` (prompt 3558, completion 399)  

## Detected issue

- **File**: `src/main/java/tools/jackson/core/json/WriterBasedJsonGenerator.java`
- **Entity**: `WriterBasedJsonGenerator.writeRawUTF8String` (class)
- **Lines (at detection time)**: L490–L493
- **Severity**: high
- **Confidence**: detected by 1 scan(s)

**Description.** Subclass violates LSP by throwing UnsupportedOperationException for a method defined in the base contract.

**Reasoning.** Similar to UTF8JsonGenerator, the WriterBasedJsonGenerator implements JsonGenerator (via JsonGeneratorBase) and provides a non-functional implementation (UnsupportedOperationException) for writeRawUTF8String, breaking the behavioral contract expected by consumers of the base class.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 0

**Summary.** Implement writeRawUTF8String and writeUTF8String in WriterBasedJsonGenerator

**Rationale.** Replacing UnsupportedOperationException with actual implementations using UTF-8 decoding ensures Liskov Substitution Principle compliance, allowing the generator to handle UTF-8 byte arrays correctly as expected by the JsonGenerator contract.

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
