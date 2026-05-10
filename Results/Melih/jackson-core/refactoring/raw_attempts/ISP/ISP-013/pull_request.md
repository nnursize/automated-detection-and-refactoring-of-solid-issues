# Refactor ISP-013 (ISP): The GeneratorBase class is forced to implement writeBinary from an InputStrea...

**Status:** `patch_failed`  
**Branch:** `refactor/ISP-013` -> `main`  
**Head commit:** `d5e5fd92e8534a70406271f72c8d497a33ebeeba`  
**LLM finish:** `FinishReason.STOP` (prompt 5361, completion 203)  

## Detected issue

- **File**: `src/main/java/tools/jackson/core/base/GeneratorBase.java`
- **Entity**: `GeneratorBase.writeBinary(Base64Variant b64variant, InputStream data, int dataLength)` (method)
- **Lines (at detection time)**: L264–L266
- **Severity**: high
- **Confidence**: detected by 1 scan(s)

**Description.** The GeneratorBase class is forced to implement writeBinary from an InputStream but explicitly reports it as an unsupported operation.

**Reasoning.** The 'JsonGenerator' interface mandates a method for writing binary content from an 'InputStream'. 'GeneratorBase' explicitly calls '_reportUnsupportedOperation()' for 'writeBinary(Base64Variant, InputStream, int)'. This suggests that this method is not supported by all generator types (e.g., character-based generators), indicating the 'JsonGenerator' interface is too broad and violates ISP by forcing implementations to support irrelevant functionalities.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 0

**Summary.** Remove unsupported writeBinary(InputStream) from GeneratorBase

**Rationale.** GeneratorBase is a base class for various generators, including textual ones that do not support binary streaming. Forcing this method into the base class violates ISP. By removing it from the base class, we allow only specific implementations that support binary streaming to define it, while others remain unaffected.

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
