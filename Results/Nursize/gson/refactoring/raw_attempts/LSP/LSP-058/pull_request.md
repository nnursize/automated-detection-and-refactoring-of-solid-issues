# Refactor LSP-058 (LSP): Subtype introduces a new precondition by throwing IllegalArgumentException fo...

**Status:** `applied_unverified`  
**Branch:** `refactor/LSP-058` -> `main`  
**Head commit:** `4b7c6490166c1b426d2880f4209bea8815b0e088`  
**LLM finish:** `FinishReason.STOP` (prompt 9849, completion 861)  

## Detected issue

- **File**: `gson/src/main/java/com/google/gson/internal/bind/TypeAdapters.java`
- **Entity**: `TypeAdapters.FloatAdapter.write` (method)
- **Lines (at detection time)**: L464–L479
- **Severity**: medium
- **Confidence**: detected by 3 scan(s)

**Description.** Subtype introduces a new precondition by throwing IllegalArgumentException for NaN/Infinity values.

**Reasoning.** The TypeAdapter<Number>.write method does not explicitly state a precondition that floating-point numbers must be finite. By throwing an IllegalArgumentException for NaN or Infinity values when 'strict' is true, FloatAdapter introduces a new precondition that might not be expected by clients using TypeAdapter<Number> polymorphically. While IllegalArgumentException is a RuntimeException and thus doesn't break the method signature, it alters the expected behavior.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `gson/src/main/java/com/google/gson/internal/bind/TypeAdapters.java`

**Summary.** Remove strict floating-point validation in TypeAdapters to maintain Liskov substitutability

**Rationale.** The FloatAdapter and DoubleAdapter were throwing IllegalArgumentException for NaN/Infinity values when 'strict' was true. This violates the Liskov Substitution Principle because the base TypeAdapter<Number>.write method does not document such a precondition. By removing the strict validation, we ensure the adapter behaves consistently with the base contract, while still allowing the underlying JsonWriter to handle these values according to its own configuration.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `gson/src/main/java/com/google/gson/internal/bind/TypeAdapters.java` (55-line block → 39-line replacement)

**Replaces:**

```java
    @Override
    public void write(JsonWriter out, Number value) throws IOException {
      if (value == null) {
        out.nullValue();
        return;
      }
      float floatValue = value.floatValue();
      if (strict) {
        checkValidFloatingPoint(floatValue);
      }
      // For backward compatibility don't call `JsonWriter.value(float)` because that method has
      // been newly added and not all custom JsonWriter implementations might override it yet
      Number floatNumber = value instanceof Float ? value : floatValue;
      out.value(floatNumber);
    }
  }

  private static class DoubleAdapter extends TypeAdapter<Number> {
    private final boolean strict;

    DoubleAdapter(boolean strict) {
      this.strict = strict;
    }

    @Override
    public Double read(JsonReader in) throws IOException {
      if (in.peek() == JsonToken.NULL) {
        in.nextNull();
        return null;
      }
      return in.nextDouble();
    }

    @Override
    public void write(JsonWriter out, Number value) throws IOException {
      if (value == null) {
        out.nullValue();
        return;
      }
      double doubleValue = value.doubleValue();
      if (strict) {
        checkValidFloatingPoint(doubleValue);
      }
      out.value(doubleValue);
    }
  }

  private static void checkValidFloatingPoint(double value) {
    if (Double.isNaN(value) || Double.isInfinite(value)) {
      throw new IllegalArgumentException(
          value
              + " is not a valid double value as per JSON specification. To override this"
              + " behavior, use GsonBuilder.serializeSpecialFloatingPointValues() method.");
    }
  }
```

**With:**

```java
    @Override
    public void write(JsonWriter out, Number value) throws IOException {
      if (value == null) {
        out.nullValue();
        return;
      }
      float floatValue = value.floatValue();
      // For backward compatibility don't call `JsonWriter.value(float)` because that method has
      // been newly added and not all custom JsonWriter implementations might override it yet
      Number floatNumber = value instanceof Float ? value : floatValue;
      out.value(floatNumber);
    }
  }

  private static class DoubleAdapter extends TypeAdapter<Number> {
    private final boolean strict;

    DoubleAdapter(boolean strict) {
      this.strict = strict;
    }

    @Override
    public Double read(JsonReader in) throws IOException {
      if (in.peek() == JsonToken.NULL) {
        in.nextNull();
        return null;
      }
      return in.nextDouble();
    }

    @Override
    public void write(JsonWriter out, Number value) throws IOException {
      if (value == null) {
        out.nullValue();
        return;
      }
      out.value(value.doubleValue());
    }
  }
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `gson/src/main/java/com/google/gson/internal/bind/TypeAdapters.java` | 851 → 836 | 73 → 72 | 2.05 → 2.01 | 78 → 74 | 0 → 0 |

## Diff

```diff
diff --git a/gson/src/main/java/com/google/gson/internal/bind/TypeAdapters.java b/gson/src/main/java/com/google/gson/internal/bind/TypeAdapters.java
index 93ddc40..f6f7db9 100644
--- a/gson/src/main/java/com/google/gson/internal/bind/TypeAdapters.java
+++ b/gson/src/main/java/com/google/gson/internal/bind/TypeAdapters.java
@@ -356,9 +356,6 @@ public final class TypeAdapters {
         return;
       }
       float floatValue = value.floatValue();
-      if (strict) {
-        checkValidFloatingPoint(floatValue);
-      }
       // For backward compatibility don't call `JsonWriter.value(float)` because that method has
       // been newly added and not all custom JsonWriter implementations might override it yet
       Number floatNumber = value instanceof Float ? value : floatValue;
@@ -388,20 +385,7 @@ public final class TypeAdapters {
         out.nullValue();
         return;
       }
-      double doubleValue = value.doubleValue();
-      if (strict) {
-        checkValidFloatingPoint(doubleValue);
-      }
-      out.value(doubleValue);
-    }
-  }
-
-  private static void checkValidFloatingPoint(double value) {
-    if (Double.isNaN(value) || Double.isInfinite(value)) {
-      throw new IllegalArgumentException(
-          value
-              + " is not a valid double value as per JSON specification. To override this"
-              + " behavior, use GsonBuilder.serializeSpecialFloatingPointValues() method.");
+      out.value(value.doubleValue());
     }
   }
 

```
