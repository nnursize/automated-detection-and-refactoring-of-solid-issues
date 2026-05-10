# Refactor LSP-107 (LSP): Subclass throws UnsupportedOperationException for a method defined in the bas...

**Status:** `applied_unverified`  
**Branch:** `refactor/LSP-107` -> `main`  
**Head commit:** `e9b265a0cf3e526e139051b0affd09e0d70e8bff`  
**LLM finish:** `FinishReason.STOP` (prompt 4523, completion 478)  

## Detected issue

- **File**: `gson/src/main/java/com/google/gson/JsonPrimitive.java`
- **Entity**: `JsonPrimitive.getAsNumber` (method)
- **Lines (at detection time)**: L139–L145
- **Severity**: medium
- **Confidence**: detected by 3 scan(s)

**Description.** Subclass throws UnsupportedOperationException for a method defined in the base class contract.

**Reasoning.** `JsonElement` defines `getAsNumber()`. `JsonPrimitive.getAsNumber()` throws `UnsupportedOperationException` if the primitive is not a number or string (e.g., if it's a boolean primitive). This indicates that the operation is not supported for certain valid states of the `JsonPrimitive`, violating the contract implied by `JsonElement`. Instead, it should either return a default value (if contract allows) or throw a more appropriate exception like `IllegalStateException` or `JsonParseException`, consistent with other `getAsX` methods in the `JsonElement` hierarchy.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `gson/src/main/java/com/google/gson/JsonPrimitive.java`

**Summary.** Change UnsupportedOperationException to NumberFormatException in JsonPrimitive.getAsNumber()

**Rationale.** The Liskov Substitution Principle is violated when a method throws an exception not expected by the contract. Since getAsNumber() is expected to return a number or fail due to format issues, NumberFormatException is the standard and appropriate exception for conversion failures in the Gson library, consistent with other getAsX methods.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `gson/src/main/java/com/google/gson/JsonPrimitive.java` (16-line block → 16-line replacement)

**Replaces:**

```java
  /**
   * Convenience method to get this element as a {@link Number}. If this primitive {@linkplain
   * #isString() is a string}, a lazily parsed {@code Number} is constructed which parses the string
   * when any of its methods are called (which can lead to a {@link NumberFormatException}).
   *
   * @throws UnsupportedOperationException if this primitive is neither a number nor a string.
   */
  @Override
  public Number getAsNumber() {
    if (value instanceof Number) {
      return (Number) value;
    } else if (value instanceof String) {
      return new LazilyParsedNumber((String) value);
    }
    throw new UnsupportedOperationException("Primitive is neither a number nor a string");
  }
```

**With:**

```java
  /**
   * Convenience method to get this element as a {@link Number}. If this primitive {@linkplain
   * #isString() is a string}, a lazily parsed {@code Number} is constructed which parses the string
   * when any of its methods are called (which can lead to a {@link NumberFormatException}).
   *
   * @throws NumberFormatException if this primitive is neither a number nor a string.
   */
  @Override
  public Number getAsNumber() {
    if (value instanceof Number) {
      return (Number) value;
    } else if (value instanceof String) {
      return new LazilyParsedNumber((String) value);
    }
    throw new NumberFormatException("Primitive is neither a number nor a string");
  }
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `gson/src/main/java/com/google/gson/JsonPrimitive.java` | 287 → 287 | 19 → 19 | 3.32 → 3.32 | 45 → 45 | 0 → 0 |

## Diff

```diff
diff --git a/gson/src/main/java/com/google/gson/JsonPrimitive.java b/gson/src/main/java/com/google/gson/JsonPrimitive.java
index 88f4466..8d080e2 100644
--- a/gson/src/main/java/com/google/gson/JsonPrimitive.java
+++ b/gson/src/main/java/com/google/gson/JsonPrimitive.java
@@ -133,7 +133,7 @@ public final class JsonPrimitive extends JsonElement {
    * #isString() is a string}, a lazily parsed {@code Number} is constructed which parses the string
    * when any of its methods are called (which can lead to a {@link NumberFormatException}).
    *
-   * @throws UnsupportedOperationException if this primitive is neither a number nor a string.
+   * @throws NumberFormatException if this primitive is neither a number nor a string.
    */
   @Override
   public Number getAsNumber() {
@@ -142,7 +142,7 @@ public final class JsonPrimitive extends JsonElement {
     } else if (value instanceof String) {
       return new LazilyParsedNumber((String) value);
     }
-    throw new UnsupportedOperationException("Primitive is neither a number nor a string");
+    throw new NumberFormatException("Primitive is neither a number nor a string");
   }
 
   /**

```
