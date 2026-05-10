# Refactor ISP-022 (ISP): JsonElement's getAsCharacter method throws UnsupportedOperationException for...

**Status:** `patch_failed`  
**Branch:** `refactor/ISP-022` -> `main`  
**Head commit:** `9bf7aae60ed62cb559252a1e0bb2b0b2c9dc554d`  
**LLM finish:** `FinishReason.STOP` (prompt 4906, completion 170)  

## Detected issue

- **File**: `gson/src/main/java/com/google/gson/JsonElement.java`
- **Entity**: `JsonElement.getAsCharacter` (method)
- **Lines (at detection time)**: L257–L259
- **Severity**: high
- **Confidence**: detected by 2 scan(s)

**Description.** JsonElement's getAsCharacter method throws UnsupportedOperationException for non-character types.

**Reasoning.** The abstract `JsonElement` class defines a contract with many `getAsX()` methods. Subclasses like `JsonObject` and `JsonNull` (and `JsonArray` in certain cases) inherit these methods but cannot meaningfully implement them, leading to `UnsupportedOperationException` or `IllegalStateException` being thrown. This forces clients (the subclasses) to depend on methods they do not use, indicating that the `JsonElement`'s contract is 'fat' and violates the Interface Segregation Principle.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 0

**Summary.** Remove deprecated getAsCharacter method from JsonElement to reduce interface bloat.

**Rationale.** The getAsCharacter method is deprecated and throws UnsupportedOperationException for most implementations, violating the Interface Segregation Principle. Removing it from the base class forces users to rely on the appropriate JsonPrimitive methods or interfaces, which is the intended design.

## Apply error

```
no patch blocks produced by LLM
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `gson/src/main/java/com/google/gson/JsonElement.java` | 284 → - | 21 → - | 3.24 → - | 48 → - | 0 → - |

## Diff

*(no diff — patch was not applied)*
