# Refactor ISP-028 (ISP): JsonNull inherits many 'getAs...' methods from JsonElement that are not appli...

**Status:** `patch_failed`  
**Branch:** `refactor/ISP-028` -> `main`  
**Head commit:** `9bf7aae60ed62cb559252a1e0bb2b0b2c9dc554d`  
**LLM finish:** `FinishReason.STOP` (prompt 2307, completion 143)  

## Detected issue

- **File**: `gson/src/main/java/com/google/gson/JsonNull.java`
- **Entity**: `JsonNull` (class)
- **Lines (at detection time)**: L21–L48
- **Severity**: high
- **Confidence**: detected by 2 scan(s)

**Description.** JsonNull inherits many 'getAs...' methods from JsonElement that are not applicable to a JSON null value, relying on UnsupportedOperationException.

**Reasoning.** `JsonNull` represents a single JSON null value. It inherits a large number of `getAs...` methods from the `JsonElement` abstract class (e.g., `getAsBoolean()`, `getAsNumber()`, `getAsString()`). `JsonNull` does not override these methods, effectively relying on the `UnsupportedOperationException` implementations from `JsonElement`. This forces `JsonNull` to conform to a contract that is vastly broader than its limited functionality, violating the Interface Segregation Principle by depending on many methods it does not use or support.

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
| `gson/src/main/java/com/google/gson/JsonNull.java` | 58 → - | 3 → - | 1.67 → - | 3 → - | 0 → - |

## Diff

*(no diff — patch was not applied)*
