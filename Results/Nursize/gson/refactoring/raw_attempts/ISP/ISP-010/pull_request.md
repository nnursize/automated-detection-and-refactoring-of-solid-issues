# Refactor ISP-010 (ISP): JsonArray's getAsBigDecimal method delegates to a single element or throws Il...

**Status:** `patch_failed`  
**Branch:** `refactor/ISP-010` -> `main`  
**Head commit:** `9bf7aae60ed62cb559252a1e0bb2b0b2c9dc554d`  
**LLM finish:** `FinishReason.STOP` (prompt 5700, completion 253)  

## Detected issue

- **File**: `gson/src/main/java/com/google/gson/JsonArray.java`
- **Entity**: `JsonArray.getAsBigDecimal()` (method)
- **Lines (at detection time)**: L234–L236
- **Severity**: high
- **Confidence**: detected by 2 scan(s)

**Description.** JsonArray's getAsBigDecimal method delegates to a single element or throws IllegalStateException.

**Reasoning.** Similar to `getAsNumber()`, `JsonArray` is forced to implement `getAsBigDecimal()` from `JsonElement`. A `JsonArray` itself is not a BigDecimal. Its implementation delegates to `getAsSingleElement()`, which throws an `IllegalStateException` if the array does not contain exactly one element. This violates ISP by forcing `JsonArray` to depend on a method it cannot directly fulfill.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 0

**Summary.** Remove getAsBigDecimal from JsonArray to adhere to ISP

**Rationale.** JsonArray is not a BigDecimal and should not be forced to implement this method. The method was only acting as a proxy for single-element arrays, which is a design smell that violates the Interface Segregation Principle.

## Apply error

```
no patch blocks produced by LLM
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `gson/src/main/java/com/google/gson/JsonArray.java` | 400 → - | 31 → - | 2.87 → - | 59 → - | 0 → - |

## Diff

*(no diff — patch was not applied)*
