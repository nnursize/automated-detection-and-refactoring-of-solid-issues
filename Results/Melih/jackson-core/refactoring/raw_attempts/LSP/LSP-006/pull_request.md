# Refactor LSP-006 (LSP): Subclass overrides getBinaryValue to throw an exception for tokens not suppor...

**Status:** `patch_failed`  
**Branch:** `refactor/LSP-006` -> `main`  
**Head commit:** `c445684d3c509e85f30ab38aa81d30048b3bda64`  
**LLM finish:** `FinishReason.STOP` (prompt 3963, completion 358)  

## Detected issue

- **File**: `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java`
- **Entity**: `UTF8StreamJsonParser.getBinaryValue` (class)
- **Lines (at detection time)**: L322–L343
- **Severity**: high
- **Confidence**: detected by 2 scan(s)

**Description.** Subclass overrides getBinaryValue to throw an exception for tokens not supported by the base class contract.

**Reasoning.** The base class JsonParser defines getBinaryValue() as a general method for accessing binary data. By explicitly restricting the allowed tokens to VALUE_STRING or VALUE_EMBEDDED_OBJECT and throwing an error for others, the subclass narrows the contract of the base class, making it non-substitutable in contexts where a caller might expect the base class to handle other token types or provide a different fallback mechanism.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 0

**Summary.** Remove restrictive token check in getBinaryValue to adhere to base class contract

**Rationale.** The base class JsonParser defines getBinaryValue() as a general method. By throwing an exception for tokens other than VALUE_STRING or VALUE_EMBEDDED_OBJECT, the subclass violates the Liskov Substitution Principle. The fix removes the explicit check, allowing the method to handle other tokens or return null/default behavior as expected by the base contract.

## Apply error

```
no patch blocks produced by LLM
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java` | 3558 → - | 114 → - | 9.62 → - | 984 → - | 0 → - |

## Diff

*(no diff — patch was not applied)*
