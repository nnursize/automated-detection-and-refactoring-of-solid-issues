# Refactor LSP-001 (LSP): Subclass implementation of _closeInput() changes behavior by conditionally cl...

**Status:** `patch_failed`  
**Branch:** `refactor/LSP-001` -> `main`  
**Head commit:** `c445684d3c509e85f30ab38aa81d30048b3bda64`  
**LLM finish:** `FinishReason.STOP` (prompt 3665, completion 416)  

## Detected issue

- **File**: `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java`
- **Entity**: `UTF8StreamJsonParser._closeInput` (method)
- **Lines (at detection time)**: L182–L195
- **Severity**: high
- **Confidence**: detected by 4 scan(s)

**Description.** Subclass implementation of _closeInput() changes behavior by conditionally closing the underlying InputStream.

**Reasoning.** The base class JsonParserBase defines _closeInput() as a protected method intended to handle resource cleanup. The implementation in UTF8StreamJsonParser introduces conditional logic based on 'isResourceManaged()' or 'AUTO_CLOSE_SOURCE' features. While this is common in Jackson, it effectively changes the contract of the method from 'close the input' to 'conditionally close the input based on internal state', which can lead to unexpected resource leaks or premature closures if a caller expects the base class contract to be strictly followed.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 0

**Summary.** Refactor _closeInput to delegate resource management to the IOContext

**Rationale.** The LSP violation occurred because the subclass was making decisions about resource ownership that should be abstracted. By moving the logic into the IOContext (or ensuring the base class contract is respected), we decouple the parser from the specific resource management policy. Since I cannot modify the base class or IOContext without potentially breaking other parsers, I am refactoring the method to use a cleaner, more explicit delegation pattern that aligns with the intended contract of resource cleanup.

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
