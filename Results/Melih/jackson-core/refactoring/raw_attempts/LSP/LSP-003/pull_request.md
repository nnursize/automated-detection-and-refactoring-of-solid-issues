# Refactor LSP-003 (LSP): Subclass throws UnsupportedOperationException for a method inherited from bas...

**Status:** `patch_failed`  
**Branch:** `refactor/LSP-003` -> `main`  
**Head commit:** `c445684d3c509e85f30ab38aa81d30048b3bda64`  
**LLM finish:** `FinishReason.STOP` (prompt 3276, completion 239)  

## Detected issue

- **File**: `src/main/java/tools/jackson/core/json/async/NonBlockingUtf8JsonParserBase.java`
- **Entity**: `NonBlockingUtf8JsonParserBase._decodeEscaped` (method)
- **Lines (at detection time)**: L80–L84
- **Severity**: high
- **Confidence**: detected by 1 scan(s)

**Description.** Subclass throws UnsupportedOperationException for a method inherited from base class

**Reasoning.** The method _decodeEscaped() is inherited from the base class (likely NonBlockingJsonParserBase or JsonParserBase). By throwing an exception (via VersionUtil.throwInternal()), the subclass violates the contract of the base class, which expects this method to be functional. This prevents the subclass from being used as a drop-in replacement for the base class.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 0

**Summary.** Remove _decodeEscaped override that throws UnsupportedOperationException

**Rationale.** The _decodeEscaped method is intended for blocking parsers. In a non-blocking context, it should not be called. Instead of throwing an exception which violates the Liskov Substitution Principle, the method should be removed to rely on the base class implementation or, if necessary, be marked as not applicable without throwing an exception if the base class allows it. Since the base class defines it as a protected method, removing the override allows the code to inherit the base behavior, which is safer than throwing an internal error.

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
