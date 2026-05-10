# Refactor LSP-019 (LSP): The 'getAsNumber' method (and similar getAs... methods) throws IllegalStateEx...

**Status:** `patch_failed`  
**Branch:** `refactor/LSP-019` -> `main`  
**Head commit:** `ff4cb3ebe63508f4e8b76b6323080527463247f8`  
**LLM finish:** `FinishReason.STOP` (prompt 5782, completion 1790)  

## Detected issue

- **File**: `gson/src/main/java/com/google/gson/JsonArray.java`
- **Entity**: `JsonArray.getAsNumber` (method)
- **Lines (at detection time)**: L218–L220
- **Severity**: high
- **Confidence**: detected by 3 scan(s)

**Description.** The 'getAsNumber' method (and similar getAs... methods) throws IllegalStateException if the array contains more than one element, narrowing preconditions.

**Reasoning.** The `JsonArray.getAsNumber()` method (and all other `getAs...()` methods like `getAsString()`, `getAsDouble()`, etc.) overrides an abstract method in `JsonElement`. In `JsonElement`, these methods throw `UnsupportedOperationException`. `JsonArray` introduces a new precondition: the array must contain exactly one element, enforced by `getAsSingleElement()` throwing `IllegalStateException` if `size() != 1`. This narrows the method's precondition considerably. A client treating a `JsonArray` polymorphically as a `JsonElement` would not expect an `IllegalStateException` due to the array's size, as the base contract only specifies `UnsupportedOperationException`. This breaks substitutability.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 0

**Summary.** Remove LSP-violating overrides of getAs... methods in JsonArray

**Rationale.** The getAs... methods in JsonArray were overriding base class methods to throw IllegalStateException when the array size was not 1. This narrows the contract of the base class (which specifies UnsupportedOperationException) and violates the Liskov Substitution Principle. By removing these overrides, JsonArray will inherit the default behavior from JsonElement (throwing UnsupportedOperationException), which is consistent with the base class contract.

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
