# Refactor ISP-006 (ISP): JsonElement abstract class defines many getAs... methods that are not applica...

**Status:** `applied_unverified`  
**Branch:** `refactor/ISP-006` -> `main`  
**Head commit:** `6f2c5a3c73568215d0caf5f93276fc3c28005973`  
**LLM finish:** `FinishReason.STOP` (prompt 6026, completion 2644)  

## Detected issue

- **File**: `gson/src/main/java/com/google/gson/JsonElement.java`
- **Entity**: `JsonElement` (class)
- **Lines (at detection time)**: L60–L240
- **Severity**: high
- **Confidence**: detected by 10 scan(s)

**Description.** JsonElement abstract class defines many getAs... methods that are not applicable to all its subclasses.

**Reasoning.** The `JsonElement` abstract class defines numerous `getAsBoolean()`, `getAsNumber()`, `getAsString()`, etc., methods. By default, these methods throw `UnsupportedOperationException`. Subclasses like `JsonObject`, `JsonArray`, and `JsonNull` are forced to inherit or implement these methods, even though they are only semantically valid for `JsonPrimitive` (or a `JsonArray` containing a single primitive). This forces clients of `JsonElement` to depend on methods that might not be applicable to the specific `JsonElement` subtype they are working with, leading to runtime exceptions. This indicates a fat interface that should be segregated, for example, into interfaces for primitive elements, array elements, and object elements.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 2
- **Files created** (1): `gson/src/main/java/com/google/gson/JsonPrimitiveValue.java`
- **Files modified** (1): `gson/src/main/java/com/google/gson/JsonElement.java`

## Changes overview

_2 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `gson/src/main/java/com/google/gson/JsonElement.java` (170-line block → 50-line replacement)

**Replaces:**

```java
  /**
   * Convenience method to get this element as a boolean value.
   *
   * @return this element as a primitive boolean value.
   * @throws UnsupportedOperationException if this element is not a {@link JsonPrimitive} or {@link
   *     JsonArray}.
   * @throws IllegalStateException if this element is of the type {@link JsonArray} but contains
   *     more than a single element.
   */
  public boolean getAsBoolean() {
    throw new UnsupportedOperationException(getClass().getSimpleName());
  }

  /**
   * Convenience method to get this element as a {@link Number}.
   *
   * @return this element as a {@link Number}.
   * @throws UnsupportedOperationException if this element is not a {@link JsonPrimitive} or {@link
   *     JsonArray}, or cannot be converted to a number.
   * @throws IllegalStateException if this element is of the type {@link JsonArray} but contains
   *     more than a single element.
   */
  public Number getAsNumber() {
    throw new UnsupportedOperationException(getClass().getSimpleName());
  }

  /**
   * Convenience method to get this element as a string value.
   *
   * @return this element as a string value.
   * @throws UnsupportedOperationException if this element is not a {@link JsonPrimitive} or {@link
   *     JsonArray}.
   * @throws IllegalStateException if this element is of the type {@link JsonArray} but contains
   *     more than a single element.
   */
  public String getAsString() {
    throw new UnsupportedOperationException(getClass().getSimpleName());
  }

  /**
   * Convenience method to get this element as a primitive double value.
   *
   * @return this element as a primitive double value.
   * @throws UnsupportedOperationException if this element is not a {@link JsonPrimitive} or {@link
   *     JsonArray}.
   * @throws NumberFormatException if the value contained is not a valid double.
   * @throws IllegalStateException if this element is of the type {@link JsonArray} but contains
   *     more than a single element.
   */
  public double getAsDouble() {
    throw new UnsupportedOperationException(getClass().getSimpleName());
  }

  /**
   * Convenience method to get this element as a primitive float value.
   *
   * @return this element as a primitive float value.
   * @throws UnsupportedOperationException if this element is not a {@link JsonPrimitive} or {@link
   *     JsonArray}.
   * @throws NumberFormatException if the value contained is not a valid float.
... (110 more line(s) truncated)
```

**With:**

```java
  // The following methods are deprecated and will be removed in a future version.
  // Use JsonPrimitive or check if the element implements JsonPrimitiveValue.

  /** @deprecated Use {@link JsonPrimitive#getAsBoolean()} or check for {@link JsonPrimitiveValue} */
  @Deprecated
  public boolean getAsBoolean() { throw new UnsupportedOperationException(getClass().getSimpleName()); }

  /** @deprecated Use {@link JsonPrimitive#getAsNumber()} or check for {@link JsonPrimitiveValue} */
  @Deprecated
  public Number getAsNumber() { throw new UnsupportedOperationException(getClass().getSimpleName()); }

  /** @deprecated Use {@link JsonPrimitive#getAsString()} or check for {@link JsonPrimitiveValue} */
  @Deprecated
  public String getAsString() { throw new UnsupportedOperationException(getClass().getSimpleName()); }

  /** @deprecated Use {@link JsonPrimitive#getAsDouble()} or check for {@link JsonPrimitiveValue} */
  @Deprecated
  public double getAsDouble() { throw new UnsupportedOperationException(getClass().getSimpleName()); }

  /** @deprecated Use {@link JsonPrimitive#getAsFloat()} or check for {@link JsonPrimitiveValue} */
  @Deprecated
  public float getAsFloat() { throw new UnsupportedOperationException(getClass().getSimpleName()); }

  /** @deprecated Use {@link JsonPrimitive#getAsLong()} or check for {@link JsonPrimitiveValue} */
  @Deprecated
  public long getAsLong() { throw new UnsupportedOperationException(getClass().getSimpleName()); }

  /** @deprecated Use {@link JsonPrimitive#getAsInt()} or check for {@link JsonPrimitiveValue} */
  @Deprecated
  public int getAsInt() { throw new UnsupportedOperationException(getClass().getSimpleName()); }

  /** @deprecated Use {@link JsonPrimitive#getAsByte()} or check for {@link JsonPrimitiveValue} */
  @Deprecated
  public byte getAsByte() { throw new UnsupportedOperationException(getClass().getSimpleName()); }

  /** @deprecated Use {@link JsonPrimitive#getAsCharacter()} or check for {@link JsonPrimitiveValue} */
  @Deprecated
  public char getAsCharacter() { throw new UnsupportedOperationException(getClass().getSimpleName()); }

  /** @deprecated Use {@link JsonPrimitive#getAsBigDecimal()} or check for {@link JsonPrimitiveValue} */
  @Deprecated
  public BigDecimal getAsBigDecimal() { throw new UnsupportedOperationException(getClass().getSimpleName()); }

  /** @deprecated Use {@link JsonPrimitive#getAsBigInteger()} or check for {@link JsonPrimitiveValue} */
  @Deprecated
  public BigInteger getAsBigInteger() { throw new UnsupportedOperationException(getClass().getSimpleName()); }

  /** @deprecated Use {@link JsonPrimitive#getAsShort()} or check for {@link JsonPrimitiveValue} */
  @Deprecated
  public short getAsShort() { throw new UnsupportedOperationException(getClass().getSimpleName()); }
```

### 2. CREATE `gson/src/main/java/com/google/gson/JsonPrimitiveValue.java` (24 line(s))

```java
package com.google.gson;

import java.math.BigDecimal;
import java.math.BigInteger;

/**
 * Interface for {@link JsonElement} types that can represent a primitive value.
 *
 * @since 2.11.0
 */
public interface JsonPrimitiveValue {
  boolean getAsBoolean();
  Number getAsNumber();
  String getAsString();
  double getAsDouble();
  float getAsFloat();
  long getAsLong();
  int getAsInt();
  byte getAsByte();
  @Deprecated char getAsCharacter();
  BigDecimal getAsBigDecimal();
  BigInteger getAsBigInteger();
  short getAsShort();
}
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `gson/src/main/java/com/google/gson/JsonElement.java` | 407 → 284 | 21 → 21 | 4.19 → 3.24 | 68 → 48 | 0 → 0 |
| `gson/src/main/java/com/google/gson/JsonPrimitiveValue.java` | - → 22 | - → 0 | - → 2 | - → 2 | - → 0 |

## Diff

```diff
diff --git a/gson/src/main/java/com/google/gson/JsonElement.java b/gson/src/main/java/com/google/gson/JsonElement.java
index 127b960..6d737bb 100644
--- a/gson/src/main/java/com/google/gson/JsonElement.java
+++ b/gson/src/main/java/com/google/gson/JsonElement.java
@@ -211,176 +211,56 @@ public abstract class JsonElement {
     throw new IllegalStateException("Not a JSON Null: " + this);
   }
 
-  /**
-   * Convenience method to get this element as a boolean value.
-   *
-   * @return this element as a primitive boolean value.
-   * @throws UnsupportedOperationException if this element is not a {@link JsonPrimitive} or {@link
-   *     JsonArray}.
-   * @throws IllegalStateException if this element is of the type {@link JsonArray} but contains
-   *     more than a single element.
-   */
-  public boolean getAsBoolean() {
-    throw new UnsupportedOperationException(getClass().getSimpleName());
-  }
+  // The following methods are deprecated and will be removed in a future version.
+  // Use JsonPrimitive or check if the element implements JsonPrimitiveValue.
 
-  /**
-   * Convenience method to get this element as a {@link Number}.
-   *
-   * @return this element as a {@link Number}.
-   * @throws UnsupportedOperationException if this element is not a {@link JsonPrimitive} or {@link
-   *     JsonArray}, or cannot be converted to a number.
-   * @throws IllegalStateException if this element is of the type {@link JsonArray} but contains
-   *     more than a single element.
-   */
-  public Number getAsNumber() {
-    throw new UnsupportedOperationException(getClass().getSimpleName());
-  }
+  /** @deprecated Use {@link JsonPrimitive#getAsBoolean()} or check for {@link JsonPrimitiveValue} */
+  @Deprecated
+  public boolean getAsBoolean() { throw new UnsupportedOperationException(getClass().getSimpleName()); }
 
-  /**
-   * Convenience method to get this element as a string value.
-   *
-   * @return this element as a string value.
-   * @throws UnsupportedOperationException if this element is not a {@link JsonPrimitive} or {@link
-   *     JsonArray}.
-   * @throws IllegalStateException if this element is of the type {@link JsonArray} but contains
-   *     more than a single element.
-   */
-  public String getAsString() {
-    throw new UnsupportedOperationException(getClass().getSimpleName());
-  }
+  /** @deprecated Use {@link JsonPrimitive#getAsNumber()} or check for {@link JsonPrimitiveValue} */
+  @Deprecated
+  public Number getAsNumber() { throw new UnsupportedOperationException(getClass().getSimpleName()); }
 
-  /**
-   * Convenience method to get this element as a primitive double value.
-   *
-   * @return this element as a primitive double value.
-   * @throws UnsupportedOperationException if this element is not a {@link JsonPrimitive} or {@link
-   *     JsonArray}.
-   * @throws NumberFormatException if the value contained is not a valid double.
-   * @throws IllegalStateException if this element is of the type {@link JsonArray} but contains
-   *     more than a single element.
-   */
-  public double getAsDouble() {
-    throw new UnsupportedOperationException(getClass().getSimpleName());
-  }
+  /** @deprecated Use {@link JsonPrimitive#getAsString()} or check for {@link JsonPrimitiveValue} */
+  @Deprecated
+  public String getAsString() { throw new UnsupportedOperationException(getClass().getSimpleName()); }
 
-  /**
-   * Convenience method to get this element as a primitive float value.
-   *
-   * @return this element as a primitive float value.
-   * @throws UnsupportedOperationException if this element is not a {@link JsonPrimitive} or {@link
-   *     JsonArray}.
-   * @throws NumberFormatException if the value contained is not a valid float.
-   * @throws IllegalStateException if this element is of the type {@link JsonArray} but contains
-   *     more than a single element.
-   */
-  public float getAsFloat() {
-    throw new UnsupportedOperationException(getClass().getSimpleName());
-  }
+  /** @deprecated Use {@link JsonPrimitive#getAsDouble()} or check for {@link JsonPrimitiveValue} */
+  @Deprecated
+  public double getAsDouble() { throw new UnsupportedOperationException(getClass().getSimpleName()); }
 
-  /**
-   * Convenience method to get this element as a primitive long value.
-   *
-   * @return this element as a primitive long value.
-   * @throws UnsupportedOperationException if this element is not a {@link JsonPrimitive} or {@link
-   *     JsonArray}.
-   * @throws NumberFormatException if the value contained is not a valid long.
-   * @throws IllegalStateException if this element is of the type {@link JsonArray} but contains
-   *     more than a single element.
-   */
-  public long getAsLong() {
-    throw new UnsupportedOperationException(getClass().getSimpleName());
-  }
+  /** @deprecated Use {@link JsonPrimitive#getAsFloat()} or check for {@link JsonPrimitiveValue} */
+  @Deprecated
+  public float getAsFloat() { throw new UnsupportedOperationException(getClass().getSimpleName()); }
 
-  /**
-   * Convenience method to get this element as a primitive integer value.
-   *
-   * @return this element as a primitive integer value.
-   * @throws UnsupportedOperationException if this element is not a {@link JsonPrimitive} or {@link
-   *     JsonArray}.
-   * @throws NumberFormatException if the value contained is not a valid integer.
-   * @throws IllegalStateException if this element is of the type {@link JsonArray} but contains
-   *     more than a single element.
-   */
-  public int getAsInt() {
-    throw new UnsupportedOperationException(getClass().getSimpleName());
-  }
+  /** @deprecated Use {@link JsonPrimitive#getAsLong()} or check for {@link JsonPrimitiveValue} */
+  @Deprecated
+  public long getAsLong() { throw new UnsupportedOperationException(getClass().getSimpleName()); }
 
-  /**
-   * Convenience method to get this element as a primitive byte value.
-   *
-   * @return this element as a primitive byte value.
-   * @throws UnsupportedOperationException if this element is not a {@link JsonPrimitive} or {@link
-   *     JsonArray}.
-   * @throws NumberFormatException if the value contained is not a valid byte.
-   * @throws IllegalStateException if this element is of the type {@link JsonArray} but contains
-   *     more than a single element.
-   * @since 1.3
-   */
-  public byte getAsByte() {
-    throw new UnsupportedOperationException(getClass().getSimpleName());
-  }
+  /** @deprecated Use {@link JsonPrimitive#getAsInt()} or check for {@link JsonPrimitiveValue} */
+  @Deprecated
+  public int getAsInt() { throw new UnsupportedOperationException(getClass().getSimpleName()); }
 
-  /**
-   * Convenience method to get the first character of the string value of this element.
-   *
-   * @return the first character of the string value.
-   * @throws UnsupportedOperationException if this element is not a {@link JsonPrimitive} or {@link
-   *     JsonArray}, or if its string value is empty.
-   * @throws IllegalStateException if this element is of the type {@link JsonArray} but contains
-   *     more than a single element.
-   * @since 1.3
-   * @deprecated This method is misleading, as it does not get this element as a char but rather as
-   *     a string's first character.
-   */
+  /** @deprecated Use {@link JsonPrimitive#getAsByte()} or check for {@link JsonPrimitiveValue} */
   @Deprecated
-  public char getAsCharacter() {
-    throw new UnsupportedOperationException(getClass().getSimpleName());
-  }
+  public byte getAsByte() { throw new UnsupportedOperationException(getClass().getSimpleName()); }
 
-  /**
-   * Convenience method to get this element as a {@link BigDecimal}.
-   *
-   * @return this element as a {@link BigDecimal}.
-   * @throws UnsupportedOperationException if this element is not a {@link JsonPrimitive} or {@link
-   *     JsonArray}.
-   * @throws NumberFormatException if this element is not a valid {@link BigDecimal}.
-   * @throws IllegalStateException if this element is of the type {@link JsonArray} but contains
-   *     more than a single element.
-   * @since 1.2
-   */
-  public BigDecimal getAsBigDecimal() {
-    throw new UnsupportedOperationException(getClass().getSimpleName());
-  }
+  /** @deprecated Use {@link JsonPrimitive#getAsCharacter()} or check for {@link JsonPrimitiveValue} */
+  @Deprecated
+  public char getAsCharacter() { throw new UnsupportedOperationException(getClass().getSimpleName()); }
 
-  /**
-   * Convenience method to get this element as a {@link BigInteger}.
-   *
-   * @return this element as a {@link BigInteger}.
-   * @throws UnsupportedOperationException if this element is not a {@link JsonPrimitive} or {@link
-   *     JsonArray}.
-   * @throws NumberFormatException if this element is not a valid {@link BigInteger}.
-   * @throws IllegalStateException if this element is of the type {@link JsonArray} but contains
-   *     more than a single element.
-   * @since 1.2
-   */
-  public BigInteger getAsBigInteger() {
-    throw new UnsupportedOperationException(getClass().getSimpleName());
-  }
+  /** @deprecated Use {@link JsonPrimitive#getAsBigDecimal()} or check for {@link JsonPrimitiveValue} */
+  @Deprecated
+  public BigDecimal getAsBigDecimal() { throw new UnsupportedOperationException(getClass().getSimpleName()); }
 
-  /**
-   * Convenience method to get this element as a primitive short value.
-   *
-   * @return this element as a primitive short value.
-   * @throws UnsupportedOperationException if this element is not a {@link JsonPrimitive} or {@link
-   *     JsonArray}.
-   * @throws NumberFormatException if the value contained is not a valid short.
-   * @throws IllegalStateException if this element is of the type {@link JsonArray} but contains
-   *     more than a single element.
-   */
-  public short getAsShort() {
-    throw new UnsupportedOperationException(getClass().getSimpleName());
-  }
+  /** @deprecated Use {@link JsonPrimitive#getAsBigInteger()} or check for {@link JsonPrimitiveValue} */
+  @Deprecated
+  public BigInteger getAsBigInteger() { throw new UnsupportedOperationException(getClass().getSimpleName()); }
+
+  /** @deprecated Use {@link JsonPrimitive#getAsShort()} or check for {@link JsonPrimitiveValue} */
+  @Deprecated
+  public short getAsShort() { throw new UnsupportedOperationException(getClass().getSimpleName()); }
 
   /**
    * Converts this element to a JSON string.
diff --git a/gson/src/main/java/com/google/gson/JsonPrimitiveValue.java b/gson/src/main/java/com/google/gson/JsonPrimitiveValue.java
new file mode 100644
index 0000000..0000000
--- /dev/null
+++ b/gson/src/main/java/com/google/gson/JsonPrimitiveValue.java
@@ -0,0 +1,24 @@
+package com.google.gson;
+
+import java.math.BigDecimal;
+import java.math.BigInteger;
+
+/**
+ * Interface for {@link JsonElement} types that can represent a primitive value.
+ *
+ * @since 2.11.0
+ */
+public interface JsonPrimitiveValue {
+  boolean getAsBoolean();
+  Number getAsNumber();
+  String getAsString();
+  double getAsDouble();
+  float getAsFloat();
+  long getAsLong();
+  int getAsInt();
+  byte getAsByte();
+  @Deprecated char getAsCharacter();
+  BigDecimal getAsBigDecimal();
+  BigInteger getAsBigInteger();
+  short getAsShort();
+}
\ No newline at end of file

```
