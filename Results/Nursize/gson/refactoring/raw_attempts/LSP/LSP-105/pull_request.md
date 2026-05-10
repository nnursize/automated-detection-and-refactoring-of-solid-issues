# Refactor LSP-105 (LSP): Base class contract for 'getAsX' methods is too broad, forcing subclasses to...

**Status:** `patch_failed`  
**Branch:** `refactor/LSP-105` -> `main`  
**Head commit:** `222eae250a0a4feb4064c8fb9cf8f3b5d4154aba`  
**LLM finish:** `FinishReason.STOP` (prompt 6053, completion 844)  

## Detected issue

- **File**: `gson/src/main/java/com/google/gson/JsonElement.java`
- **Entity**: `JsonElement.getAsJsonObject` (method)
- **Lines (at detection time)**: L159–L163
- **Severity**: high
- **Confidence**: detected by 2 scan(s)

**Description.** Base class contract for 'getAsX' methods is too broad, forcing subclasses to throw IllegalStateException.

**Reasoning.** The `JsonElement` abstract class defines numerous `getAsX()` methods (e.g., `getAsJsonObject()`, `getAsJsonArray()`, `getAsNumber()`, `getAsString()`). Its default implementations throw `IllegalStateException` if the element is not of the expected type. Subtypes like `JsonArray`, `JsonObject`, `JsonPrimitive`, and `JsonNull` cannot logically fulfill all these contracts. For example, a `JsonArray` cannot be converted to a `JsonObject` or a `Number`. This forces clients to perform type-checking (e.g., `isJsonArray()`) before calling `getAsJsonArray()`, which is a classic indicator of a 'fat interface' and an LSP violation. Subtypes are not substitutable for the base type without clients needing to know the concrete type to avoid runtime exceptions.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 0

## Apply error

```
no patch blocks produced by LLM
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `gson/src/main/java/com/google/gson/JsonElement.java` | 407 → - | 21 → - | 4.19 → - | 68 → - | 0 → - |

## Diff

*(no diff — patch was not applied)*
