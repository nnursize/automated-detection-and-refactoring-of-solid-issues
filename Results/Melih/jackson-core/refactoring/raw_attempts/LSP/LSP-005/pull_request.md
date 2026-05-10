# Refactor LSP-005 (LSP): Subclass throws UnsupportedOperationException for a method inherited from the...

**Status:** `patch_failed`  
**Branch:** `refactor/LSP-005` -> `main`  
**Head commit:** `c445684d3c509e85f30ab38aa81d30048b3bda64`  
**LLM finish:** `FinishReason.STOP` (prompt 3262, completion 190)  

## Detected issue

- **File**: `src/main/java/tools/jackson/core/json/async/NonBlockingUtf8JsonParserBase.java`
- **Entity**: `NonBlockingUtf8JsonParserBase._decodeEscaped` (method)
- **Lines (at detection time)**: L82–L86
- **Severity**: high
- **Confidence**: detected by 3 scan(s)

**Description.** Subclass throws UnsupportedOperationException for a method inherited from the base class.

**Reasoning.** The method _decodeEscaped() is inherited from the base class (JsonParserBase) and is expected to return a char. By throwing an exception (via VersionUtil.throwInternal()), the subclass violates the behavioral contract of the base class, making it non-substitutable.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 0

**Summary.** Remove _decodeEscaped override that throws UnsupportedOperationException

**Rationale.** The method _decodeEscaped is not used by non-blocking parsers, and throwing an exception violates the Liskov Substitution Principle. Removing the override allows the base class implementation (which is likely safer or empty) to be used, or simply avoids the illegal state transition.

## Apply error

```
no patch blocks produced by LLM
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/main/java/tools/jackson/core/json/async/NonBlockingUtf8JsonParserBase.java` | 2634 → - | 63 → - | 12.56 → - | 729 → - | 0 → - |

## Diff

*(no diff — patch was not applied)*
