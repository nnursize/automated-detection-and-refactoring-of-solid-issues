# Refactor LSP-010 (LSP): Subclass violates LSP by throwing UnsupportedOperationException for a method...

**Status:** `patch_failed`  
**Branch:** `refactor/LSP-010` -> `main`  
**Head commit:** `c445684d3c509e85f30ab38aa81d30048b3bda64`  
**LLM finish:** `FinishReason.STOP` (prompt 3759, completion 351)  

## Detected issue

- **File**: `src/main/java/tools/jackson/core/json/UTF8JsonGenerator.java`
- **Entity**: `UTF8JsonGenerator.writeRawUTF8String` (class)
- **Lines (at detection time)**: L444–L448
- **Severity**: high
- **Confidence**: detected by 1 scan(s)

**Description.** Subclass violates LSP by throwing UnsupportedOperationException for a method defined in the base contract.

**Reasoning.** The JsonGenerator (base) class defines writeRawUTF8String as an abstract method, implying it is part of the contract for all generators. The UTF8JsonGenerator implementation throws an UnsupportedOperationException, meaning it is not substitutable for a general JsonGenerator where this method is expected to work.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 0

**Summary.** Implement writeRawUTF8String in UTF8JsonGenerator to satisfy LSP

**Rationale.** The method was previously throwing UnsupportedOperationException, violating the Liskov Substitution Principle. Since UTF8JsonGenerator is a byte-based generator, it can natively support writing raw UTF-8 bytes without escaping, which is the expected behavior for this method.

## Apply error

```
no patch blocks produced by LLM
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/main/java/tools/jackson/core/json/UTF8JsonGenerator.java` | 2058 → - | 84 → - | 5.74 → - | 399 → - | 0 → - |

## Diff

*(no diff — patch was not applied)*
