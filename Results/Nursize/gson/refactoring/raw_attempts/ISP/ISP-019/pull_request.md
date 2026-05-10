# Refactor ISP-019 (ISP): JsonObject's getAsBoolean method throws UnsupportedOperationException.

**Status:** `patch_failed`  
**Branch:** `refactor/ISP-019` -> `main`  
**Head commit:** `6f2c5a3c73568215d0caf5f93276fc3c28005973`  
**LLM finish:** `FinishReason.STOP` (prompt 4179, completion 359)  

## Detected issue

- **File**: `gson/src/main/java/com/google/gson/JsonObject.java`
- **Entity**: `JsonObject.getAsBoolean()` (method)
- **Lines (at detection time)**: L60–L62
- **Severity**: high
- **Confidence**: detected by 3 scan(s)

**Description.** JsonObject's getAsBoolean method throws UnsupportedOperationException.

**Reasoning.** The `JsonObject` class is forced to implement `getAsBoolean()` (and other `getAs...` methods) from `JsonElement`. A `JsonObject` itself is not a boolean. Its implementation throws an `UnsupportedOperationException`, indicating that this method is not applicable to `JsonObject` and violates ISP by forcing `JsonObject` to depend on a method it cannot directly fulfill.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `gson/src/main/java/com/google/gson/JsonObject.java`

**Summary.** Remove unnecessary getAsBoolean override from JsonObject

**Rationale.** The JsonObject class inherits getAsBoolean() from JsonElement. Since JsonObject does not override it, it currently uses the default implementation in JsonElement (which throws UnsupportedOperationException). Explicitly overriding it in JsonObject to throw the same exception is redundant and violates the principle of keeping interfaces clean by not forcing implementations that aren't needed. Removing the override allows the class to rely on the base class behavior.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `gson/src/main/java/com/google/gson/JsonObject.java` (10-line block → 10-line replacement)

**Replaces:**

```java
  /**
   * Convenience method to add a boolean member. The specified value is converted to a {@link
   * JsonPrimitive} of Boolean.
   *
   * @param property name of the member.
   * @param value the boolean value associated with the member.
   */
  public void addProperty(String property, Boolean value) {
    add(property, value == null ? JsonNull.INSTANCE : new JsonPrimitive(value));
  }
```

**With:**

```java
  /**
   * Convenience method to add a boolean member. The specified value is converted to a {@link
   * JsonPrimitive} of Boolean.
   *
   * @param property name of the member.
   * @param value the boolean value associated with the member.
   */
  public void addProperty(String property, Boolean value) {
    add(property, value == null ? JsonNull.INSTANCE : new JsonPrimitive(value));
  }
```

## Apply error

```
patch applied but produced no net source changes; the LLM replacement was likely identical to the matched text
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `gson/src/main/java/com/google/gson/JsonObject.java` | 235 → - | 18 → - | 2.22 → - | 23 → - | 0 → - |

## Diff

*(no diff — patch was not applied)*
