# Refactor SRP-004 (SRP): The TypeAdapters class acts as a monolithic registry and factory for a vast a...

**Status:** `applied_unverified`  
**Branch:** `refactor/SRP-004` -> `main`  
**Head commit:** `229cff91b95d0766b6ebe45a50f018a8a4d5ff7b`  
**LLM finish:** `FinishReason.STOP` (prompt 10624, completion 2739)  

## Detected issue

- **File**: `gson/src/main/java/com/google/gson/internal/bind/TypeAdapters.java`
- **Entity**: `TypeAdapters` (class)
- **Lines (at detection time)**: L27–L579
- **Severity**: high
- **Confidence**: detected by 6 scan(s)

**Description.** The TypeAdapters class acts as a monolithic registry and factory for a vast array of unrelated basic Java types.

**Reasoning.** This class bundles a multitude of distinct concerns: providing static `TypeAdapter` instances for various primitives, wrappers, standard library types (e.g., `BitSet`, `URL`, `Locale`, `Calendar`, atomic types), custom number parsing logic (`checkValidFloatingPoint`, `IntegerFieldsTypeAdapter`), and factory methods for creating generic type adapter factories. A change in the default adapter for any of these types, the logic for handling floating-point numbers, or the factory creation mechanism would all necessitate changes to this single class. This is a clear violation of SRP, indicating a 'God class' symptom.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 2
- **Files created** (1): `gson/src/main/java/com/google/gson/internal/bind/BasicTypeAdapters.java`
- **Files modified** (1): `gson/src/main/java/com/google/gson/internal/bind/TypeAdapters.java`

**Summary.** Extract basic type adapters into a separate class to reduce TypeAdapters god-class complexity.

**Rationale.** The TypeAdapters class is a monolithic registry. Extracting the basic primitive and wrapper type adapters into a dedicated 'BasicTypeAdapters' class improves maintainability and adheres to the Single Responsibility Principle by separating the registry logic from the specific adapter implementations.

## Changes overview

_2 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `gson/src/main/java/com/google/gson/internal/bind/TypeAdapters.java` (141-line block → 37-line replacement)

**Replaces:**

```java
  public static final TypeAdapter<Boolean> BOOLEAN =
      new TypeAdapter<Boolean>() {
        @Override
        public Boolean read(JsonReader in) throws IOException {
          JsonToken peek = in.peek();
          if (peek == JsonToken.NULL) {
            in.nextNull();
            return null;
          } else if (peek == JsonToken.STRING) {
            // support strings for compatibility with GSON 1.7
            return Boolean.parseBoolean(in.nextString());
          }
          return in.nextBoolean();
        }

        @Override
        public void write(JsonWriter out, Boolean value) throws IOException {
          out.value(value);
        }
      };

  /**
   * Writes a boolean as a string. Useful for map keys, where booleans aren't otherwise permitted.
   */
  public static final TypeAdapter<Boolean> BOOLEAN_AS_STRING =
      new TypeAdapter<Boolean>() {
        @Override
        public Boolean read(JsonReader in) throws IOException {
          if (in.peek() == JsonToken.NULL) {
            in.nextNull();
            return null;
          }
          return Boolean.valueOf(in.nextString());
        }

        @Override
        public void write(JsonWriter out, Boolean value) throws IOException {
          out.value(value == null ? "null" : value.toString());
        }
      };

  public static final TypeAdapterFactory BOOLEAN_FACTORY =
      newFactory(boolean.class, Boolean.class, BOOLEAN);

  public static final TypeAdapter<Number> BYTE =
      new TypeAdapter<Number>() {
        @Override
        public Number read(JsonReader in) throws IOException {
          if (in.peek() == JsonToken.NULL) {
            in.nextNull();
            return null;
          }

          int intValue;
          try {
            intValue = in.nextInt();
          } catch (NumberFormatException e) {
            throw new JsonSyntaxException(e);
          }
          // Allow up to 255 to support unsigned values
... (81 more line(s) truncated)
```

**With:**

```java
  public static final TypeAdapter<Boolean> BOOLEAN = BasicTypeAdapters.BOOLEAN;

  /**
   * Writes a boolean as a string. Useful for map keys, where booleans aren't otherwise permitted.
   */
  public static final TypeAdapter<Boolean> BOOLEAN_AS_STRING =
      new TypeAdapter<Boolean>() {
        @Override
        public Boolean read(JsonReader in) throws IOException {
          if (in.peek() == JsonToken.NULL) {
            in.nextNull();
            return null;
          }
          return Boolean.valueOf(in.nextString());
        }

        @Override
        public void write(JsonWriter out, Boolean value) throws IOException {
          out.value(value == null ? "null" : value.toString());
        }
      };

  public static final TypeAdapterFactory BOOLEAN_FACTORY =
      newFactory(boolean.class, Boolean.class, BOOLEAN);

  public static final TypeAdapter<Number> BYTE = BasicTypeAdapters.BYTE;

  public static final TypeAdapterFactory BYTE_FACTORY = newFactory(byte.class, Byte.class, BYTE);

  public static final TypeAdapter<Number> SHORT = BasicTypeAdapters.SHORT;

  public static final TypeAdapterFactory SHORT_FACTORY =
      newFactory(short.class, Short.class, SHORT);

  public static final TypeAdapter<Number> INTEGER = BasicTypeAdapters.INTEGER;
  public static final TypeAdapterFactory INTEGER_FACTORY =
      newFactory(int.class, Integer.class, INTEGER);
```

### 2. CREATE `gson/src/main/java/com/google/gson/internal/bind/BasicTypeAdapters.java` (138 line(s))

```java
/*
 * Copyright (C) 2024 Google Inc.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package com.google.gson.internal.bind;

import com.google.gson.JsonSyntaxException;
import com.google.gson.TypeAdapter;
import com.google.gson.stream.JsonReader;
import com.google.gson.stream.JsonToken;
import com.google.gson.stream.JsonWriter;
import java.io.IOException;

/**
 * Basic type adapters for primitives and wrappers.
 */
public final class BasicTypeAdapters {
  private BasicTypeAdapters() {}

  public static final TypeAdapter<Boolean> BOOLEAN =
      new TypeAdapter<Boolean>() {
        @Override
        public Boolean read(JsonReader in) throws IOException {
          JsonToken peek = in.peek();
          if (peek == JsonToken.NULL) {
            in.nextNull();
            return null;
          } else if (peek == JsonToken.STRING) {
            return Boolean.parseBoolean(in.nextString());
          }
          return in.nextBoolean();
        }

        @Override
        public void write(JsonWriter out, Boolean value) throws IOException {
          out.value(value);
        }
      };

  public static final TypeAdapter<Number> BYTE =
      new TypeAdapter<Number>() {
        @Override
        public Number read(JsonReader in) throws IOException {
          if (in.peek() == JsonToken.NULL) {
            in.nextNull();
            return null;
          }
          int intValue;
... (78 more line(s) truncated)
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `gson/src/main/java/com/google/gson/internal/bind/BasicTypeAdapters.java` | - → 127 | - → 8 | - → 3.12 | - → 18 | - → 0 |
| `gson/src/main/java/com/google/gson/internal/bind/TypeAdapters.java` | 956 → 861 | 81 → 73 | 2.17 → 2.08 | 96 → 80 | 0 → 0 |

## Diff

```diff
diff --git a/gson/src/main/java/com/google/gson/internal/bind/TypeAdapters.java b/gson/src/main/java/com/google/gson/internal/bind/TypeAdapters.java
index 852ae56..605afdb 100644
--- a/gson/src/main/java/com/google/gson/internal/bind/TypeAdapters.java
+++ b/gson/src/main/java/com/google/gson/internal/bind/TypeAdapters.java
@@ -142,26 +142,7 @@ public final class TypeAdapters {
 
   public static final TypeAdapterFactory BIT_SET_FACTORY = newFactory(BitSet.class, BIT_SET);
 
-  public static final TypeAdapter<Boolean> BOOLEAN =
-      new TypeAdapter<Boolean>() {
-        @Override
-        public Boolean read(JsonReader in) throws IOException {
-          JsonToken peek = in.peek();
-          if (peek == JsonToken.NULL) {
-            in.nextNull();
-            return null;
-          } else if (peek == JsonToken.STRING) {
-            // support strings for compatibility with GSON 1.7
-            return Boolean.parseBoolean(in.nextString());
-          }
-          return in.nextBoolean();
-        }
-
-        @Override
-        public void write(JsonWriter out, Boolean value) throws IOException {
-          out.value(value);
-        }
-      };
+  public static final TypeAdapter<Boolean> BOOLEAN = BasicTypeAdapters.BOOLEAN;
 
   /**
    * Writes a boolean as a string. Useful for map keys, where booleans aren't otherwise permitted.
@@ -186,101 +167,16 @@ public final class TypeAdapters {
   public static final TypeAdapterFactory BOOLEAN_FACTORY =
       newFactory(boolean.class, Boolean.class, BOOLEAN);
 
-  public static final TypeAdapter<Number> BYTE =
-      new TypeAdapter<Number>() {
-        @Override
-        public Number read(JsonReader in) throws IOException {
-          if (in.peek() == JsonToken.NULL) {
-            in.nextNull();
-            return null;
-          }
-
-          int intValue;
-          try {
-            intValue = in.nextInt();
-          } catch (NumberFormatException e) {
-            throw new JsonSyntaxException(e);
-          }
-          // Allow up to 255 to support unsigned values
-          if (intValue > 255 || intValue < Byte.MIN_VALUE) {
-            throw new JsonSyntaxException(
-                "Lossy conversion from " + intValue + " to byte; at path " + in.getPreviousPath());
-          }
-          return (byte) intValue;
-        }
-
-        @Override
-        public void write(JsonWriter out, Number value) throws IOException {
-          if (value == null) {
-            out.nullValue();
-          } else {
-            out.value(value.byteValue());
-          }
-        }
-      };
+  public static final TypeAdapter<Number> BYTE = BasicTypeAdapters.BYTE;
 
   public static final TypeAdapterFactory BYTE_FACTORY = newFactory(byte.class, Byte.class, BYTE);
 
-  public static final TypeAdapter<Number> SHORT =
-      new TypeAdapter<Number>() {
-        @Override
-        public Number read(JsonReader in) throws IOException {
-          if (in.peek() == JsonToken.NULL) {
-            in.nextNull();
-            return null;
-          }
-
-          int intValue;
-          try {
-            intValue = in.nextInt();
-          } catch (NumberFormatException e) {
-            throw new JsonSyntaxException(e);
-          }
-          // Allow up to 65535 to support unsigned values
-          if (intValue > 65535 || intValue < Short.MIN_VALUE) {
-            throw new JsonSyntaxException(
-                "Lossy conversion from " + intValue + " to short; at path " + in.getPreviousPath());
-          }
-          return (short) intValue;
-        }
-
-        @Override
-        public void write(JsonWriter out, Number value) throws IOException {
-          if (value == null) {
-            out.nullValue();
-          } else {
-            out.value(value.shortValue());
-          }
-        }
-      };
+  public static final TypeAdapter<Number> SHORT = BasicTypeAdapters.SHORT;
 
   public static final TypeAdapterFactory SHORT_FACTORY =
       newFactory(short.class, Short.class, SHORT);
 
-  public static final TypeAdapter<Number> INTEGER =
-      new TypeAdapter<Number>() {
-        @Override
-        public Number read(JsonReader in) throws IOException {
-          if (in.peek() == JsonToken.NULL) {
-            in.nextNull();
-            return null;
-          }
-          try {
-            return in.nextInt();
-          } catch (NumberFormatException e) {
-            throw new JsonSyntaxException(e);
-          }
-        }
-
-        @Override
-        public void write(JsonWriter out, Number value) throws IOException {
-          if (value == null) {
-            out.nullValue();
-          } else {
-            out.value(value.intValue());
-          }
-        }
-      };
+  public static final TypeAdapter<Number> INTEGER = BasicTypeAdapters.INTEGER;
   public static final TypeAdapterFactory INTEGER_FACTORY =
       newFactory(int.class, Integer.class, INTEGER);
 
diff --git a/gson/src/main/java/com/google/gson/internal/bind/BasicTypeAdapters.java b/gson/src/main/java/com/google/gson/internal/bind/BasicTypeAdapters.java
new file mode 100644
index 0000000..0000000
--- /dev/null
+++ b/gson/src/main/java/com/google/gson/internal/bind/BasicTypeAdapters.java
@@ -0,0 +1,138 @@
+/*
+ * Copyright (C) 2024 Google Inc.
+ *
+ * Licensed under the Apache License, Version 2.0 (the "License");
+ * you may not use this file except in compliance with the License.
+ * You may obtain a copy of the License at
+ *
+ *      http://www.apache.org/licenses/LICENSE-2.0
+ *
+ * Unless required by applicable law or agreed to in writing, software
+ * distributed under the License is distributed on an "AS IS" BASIS,
+ * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
+ * See the License for the specific language governing permissions and
+ * limitations under the License.
+ */
+
+package com.google.gson.internal.bind;
+
+import com.google.gson.JsonSyntaxException;
+import com.google.gson.TypeAdapter;
+import com.google.gson.stream.JsonReader;
+import com.google.gson.stream.JsonToken;
+import com.google.gson.stream.JsonWriter;
+import java.io.IOException;
+
+/**
+ * Basic type adapters for primitives and wrappers.
+ */
+public final class BasicTypeAdapters {
+  private BasicTypeAdapters() {}
+
+  public static final TypeAdapter<Boolean> BOOLEAN =
+      new TypeAdapter<Boolean>() {
+        @Override
+        public Boolean read(JsonReader in) throws IOException {
+          JsonToken peek = in.peek();
+          if (peek == JsonToken.NULL) {
+            in.nextNull();
+            return null;
+          } else if (peek == JsonToken.STRING) {
+            return Boolean.parseBoolean(in.nextString());
+          }
+          return in.nextBoolean();
+        }
+
+        @Override
+        public void write(JsonWriter out, Boolean value) throws IOException {
+          out.value(value);
+        }
+      };
+
+  public static final TypeAdapter<Number> BYTE =
+      new TypeAdapter<Number>() {
+        @Override
+        public Number read(JsonReader in) throws IOException {
+          if (in.peek() == JsonToken.NULL) {
+            in.nextNull();
+            return null;
+          }
+          int intValue;
+          try {
+            intValue = in.nextInt();
+          } catch (NumberFormatException e) {
+            throw new JsonSyntaxException(e);
+          }
+          if (intValue > 255 || intValue < Byte.MIN_VALUE) {
+            throw new JsonSyntaxException(
+                "Lossy conversion from " + intValue + " to byte; at path " + in.getPreviousPath());
+          }
+          return (byte) intValue;
+        }
+
+        @Override
+        public void write(JsonWriter out, Number value) throws IOException {
+          if (value == null) {
+            out.nullValue();
+          } else {
+            out.value(value.byteValue());
+          }
+        }
+      };
+
+  public static final TypeAdapter<Number> SHORT =
+      new TypeAdapter<Number>() {
+        @Override
+        public Number read(JsonReader in) throws IOException {
+          if (in.peek() == JsonToken.NULL) {
+            in.nextNull();
+            return null;
+          }
+          int intValue;
+          try {
+            intValue = in.nextInt();
+          } catch (NumberFormatException e) {
+            throw new JsonSyntaxException(e);
+          }
+          if (intValue > 65535 || intValue < Short.MIN_VALUE) {
+            throw new JsonSyntaxException(
+                "Lossy conversion from " + intValue + " to short; at path " + in.getPreviousPath());
+          }
+          return (short) intValue;
+        }
+
+        @Override
+        public void write(JsonWriter out, Number value) throws IOException {
+          if (value == null) {
+            out.nullValue();
+          } else {
+            out.value(value.shortValue());
+          }
+        }
+      };
+
+  public static final TypeAdapter<Number> INTEGER =
+      new TypeAdapter<Number>() {
+        @Override
+        public Number read(JsonReader in) throws IOException {
+          if (in.peek() == JsonToken.NULL) {
+            in.nextNull();
+            return null;
+          }
+          try {
+            return in.nextInt();
+          } catch (NumberFormatException e) {
+            throw new JsonSyntaxException(e);
+          }
+        }
+
+        @Override
+        public void write(JsonWriter out, Number value) throws IOException {
+          if (value == null) {
+            out.nullValue();
+          } else {
+            out.value(value.intValue());
+          }
+        }
+      };
+}
\ No newline at end of file

```
