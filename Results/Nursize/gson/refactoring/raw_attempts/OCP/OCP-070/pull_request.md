# Refactor OCP-070 (OCP): If-else if chain and switch statements for reading different JSON element typ...

**Status:** `applied_unverified`  
**Branch:** `refactor/OCP-070` -> `main`  
**Head commit:** `4d4ab06f56c9761a94e12f064f60cea976d6d9d2`  
**LLM finish:** `FinishReason.STOP` (prompt 3106, completion 1292)  

## Detected issue

- **File**: `gson/src/main/java/com/google/gson/internal/bind/JsonElementTypeAdapter.java`
- **Entity**: `JsonElementTypeAdapter.read` (method)
- **Lines (at detection time)**: L44–L96
- **Severity**: high
- **Confidence**: detected by 3 scan(s)

**Description.** If-else if chain and switch statements for reading different JSON element types, requiring modification for new types.

**Reasoning.** The `read` method, particularly through its calls to `tryBeginNesting` and `readTerminal`, contains `switch` statements that dispatch logic based on `JsonToken` (e.g., `BEGIN_ARRAY`, `BEGIN_OBJECT`, `STRING`, `NUMBER`, `BOOLEAN`, `NULL`). Additionally, there's an `if (in instanceof JsonTreeReader)` check for optimization. If new JSON token types or new `JsonReader` subclasses that offer specialized reading were introduced, these conditional structures would need to be modified. This is a clear OCP violation, as extending JSON parsing capabilities or reader types requires altering existing code.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 2
- **Files modified** (1): `gson/src/main/java/com/google/gson/internal/bind/JsonElementTypeAdapter.java`

**Summary.** Refactor JsonElementTypeAdapter to use a strategy-based approach for reading JSON elements.

**Rationale.** The switch-based dispatching logic in tryBeginNesting and readTerminal is replaced by a functional interface (ReaderStrategy) that allows for extensible element creation without modifying the core adapter logic. This adheres to the Open/Closed Principle by allowing new token types to be handled via registration.

## Changes overview

_2 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `gson/src/main/java/com/google/gson/internal/bind/JsonElementTypeAdapter.java` (35-line block → 22-line replacement)

**Replaces:**

```java
  /**
   * Tries to begin reading a JSON array or JSON object, returning {@code null} if the next element
   * is neither of those.
   */
  private JsonElement tryBeginNesting(JsonReader in, JsonToken peeked) throws IOException {
    switch (peeked) {
      case BEGIN_ARRAY:
        in.beginArray();
        return new JsonArray();
      case BEGIN_OBJECT:
        in.beginObject();
        return new JsonObject();
      default:
        return null;
    }
  }

  /** Reads a {@link JsonElement} which cannot have any nested elements */
  private JsonElement readTerminal(JsonReader in, JsonToken peeked) throws IOException {
    switch (peeked) {
      case STRING:
        return new JsonPrimitive(in.nextString());
      case NUMBER:
        String number = in.nextString();
        return new JsonPrimitive(new LazilyParsedNumber(number));
      case BOOLEAN:
        return new JsonPrimitive(in.nextBoolean());
      case NULL:
        in.nextNull();
        return JsonNull.INSTANCE;
      default:
        // When read(JsonReader) is called with JsonReader in invalid state
        throw new IllegalStateException("Unexpected token: " + peeked);
    }
  }
```

**With:**

```java
  private interface ReaderStrategy {
    JsonElement read(JsonReader in) throws IOException;
  }

  private static final java.util.Map<JsonToken, ReaderStrategy> STRATEGIES = new java.util.EnumMap<>(JsonToken.class);

  static {
    STRATEGIES.put(JsonToken.BEGIN_ARRAY, in -> { in.beginArray(); return new JsonArray(); });
    STRATEGIES.put(JsonToken.BEGIN_OBJECT, in -> { in.beginObject(); return new JsonObject(); });
    STRATEGIES.put(JsonToken.STRING, in -> new JsonPrimitive(in.nextString()));
    STRATEGIES.put(JsonToken.NUMBER, in -> new JsonPrimitive(new LazilyParsedNumber(in.nextString())));
    STRATEGIES.put(JsonToken.BOOLEAN, in -> new JsonPrimitive(in.nextBoolean()));
    STRATEGIES.put(JsonToken.NULL, in -> { in.nextNull(); return JsonNull.INSTANCE; });
  }

  private JsonElement readElement(JsonReader in, JsonToken peeked) throws IOException {
    ReaderStrategy strategy = STRATEGIES.get(peeked);
    if (strategy == null) {
      throw new IllegalStateException("Unexpected token: " + peeked);
    }
    return strategy.read(in);
  }
```

### 2. EDIT `gson/src/main/java/com/google/gson/internal/bind/JsonElementTypeAdapter.java` (38-line block → 34-line replacement)

**Replaces:**

```java
    // Either JsonArray or JsonObject
    JsonElement current;
    JsonToken peeked = in.peek();

    current = tryBeginNesting(in, peeked);
    if (current == null) {
      return readTerminal(in, peeked);
    }

    Deque<JsonElement> stack = new ArrayDeque<>();

    while (true) {
      while (in.hasNext()) {
        String name = null;
        // Name is only used for JSON object members
        if (current instanceof JsonObject) {
          name = in.nextName();
        }

        peeked = in.peek();
        JsonElement value = tryBeginNesting(in, peeked);
        boolean isNesting = value != null;

        if (value == null) {
          value = readTerminal(in, peeked);
        }

        if (current instanceof JsonArray) {
          ((JsonArray) current).add(value);
        } else {
          ((JsonObject) current).add(name, value);
        }

        if (isNesting) {
          stack.addLast(current);
          current = value;
        }
      }
```

**With:**

```java
    // Either JsonArray or JsonObject
    JsonToken peeked = in.peek();
    JsonElement current = readElement(in, peeked);
    boolean isNesting = (peeked == JsonToken.BEGIN_ARRAY || peeked == JsonToken.BEGIN_OBJECT);

    if (!isNesting) {
      return current;
    }

    Deque<JsonElement> stack = new ArrayDeque<>();

    while (true) {
      while (in.hasNext()) {
        String name = null;
        // Name is only used for JSON object members
        if (current instanceof JsonObject) {
          name = in.nextName();
        }

        peeked = in.peek();
        JsonElement value = readElement(in, peeked);
        boolean isValueNesting = (peeked == JsonToken.BEGIN_ARRAY || peeked == JsonToken.BEGIN_OBJECT);

        if (current instanceof JsonArray) {
          ((JsonArray) current).add(value);
        } else {
          ((JsonObject) current).add(name, value);
        }

        if (isValueNesting) {
          stack.addLast(current);
          current = value;
        }
      }
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `gson/src/main/java/com/google/gson/internal/bind/JsonElementTypeAdapter.java` | 144 → 127 | 4 → 3 | 8.5 → 9.33 | 31 → 26 | 0 → 0 |

## Diff

```diff
diff --git a/gson/src/main/java/com/google/gson/internal/bind/JsonElementTypeAdapter.java b/gson/src/main/java/com/google/gson/internal/bind/JsonElementTypeAdapter.java
index e594fae..139b329 100644
--- a/gson/src/main/java/com/google/gson/internal/bind/JsonElementTypeAdapter.java
+++ b/gson/src/main/java/com/google/gson/internal/bind/JsonElementTypeAdapter.java
@@ -37,40 +37,27 @@ public class JsonElementTypeAdapter extends TypeAdapter<JsonElement> {
 
   private JsonElementTypeAdapter() {}
 
-  /**
-   * Tries to begin reading a JSON array or JSON object, returning {@code null} if the next element
-   * is neither of those.
-   */
-  private JsonElement tryBeginNesting(JsonReader in, JsonToken peeked) throws IOException {
-    switch (peeked) {
-      case BEGIN_ARRAY:
-        in.beginArray();
-        return new JsonArray();
-      case BEGIN_OBJECT:
-        in.beginObject();
-        return new JsonObject();
-      default:
-        return null;
-    }
+  private interface ReaderStrategy {
+    JsonElement read(JsonReader in) throws IOException;
+  }
+
+  private static final java.util.Map<JsonToken, ReaderStrategy> STRATEGIES = new java.util.EnumMap<>(JsonToken.class);
+
+  static {
+    STRATEGIES.put(JsonToken.BEGIN_ARRAY, in -> { in.beginArray(); return new JsonArray(); });
+    STRATEGIES.put(JsonToken.BEGIN_OBJECT, in -> { in.beginObject(); return new JsonObject(); });
+    STRATEGIES.put(JsonToken.STRING, in -> new JsonPrimitive(in.nextString()));
+    STRATEGIES.put(JsonToken.NUMBER, in -> new JsonPrimitive(new LazilyParsedNumber(in.nextString())));
+    STRATEGIES.put(JsonToken.BOOLEAN, in -> new JsonPrimitive(in.nextBoolean()));
+    STRATEGIES.put(JsonToken.NULL, in -> { in.nextNull(); return JsonNull.INSTANCE; });
   }
 
-  /** Reads a {@link JsonElement} which cannot have any nested elements */
-  private JsonElement readTerminal(JsonReader in, JsonToken peeked) throws IOException {
-    switch (peeked) {
-      case STRING:
-        return new JsonPrimitive(in.nextString());
-      case NUMBER:
-        String number = in.nextString();
-        return new JsonPrimitive(new LazilyParsedNumber(number));
-      case BOOLEAN:
-        return new JsonPrimitive(in.nextBoolean());
-      case NULL:
-        in.nextNull();
-        return JsonNull.INSTANCE;
-      default:
-        // When read(JsonReader) is called with JsonReader in invalid state
-        throw new IllegalStateException("Unexpected token: " + peeked);
+  private JsonElement readElement(JsonReader in, JsonToken peeked) throws IOException {
+    ReaderStrategy strategy = STRATEGIES.get(peeked);
+    if (strategy == null) {
+      throw new IllegalStateException("Unexpected token: " + peeked);
     }
+    return strategy.read(in);
   }
 
   @Override
@@ -81,12 +68,12 @@ public class JsonElementTypeAdapter extends TypeAdapter<JsonElement> {
     }
 
     // Either JsonArray or JsonObject
-    JsonElement current;
     JsonToken peeked = in.peek();
+    JsonElement current = readElement(in, peeked);
+    boolean isNesting = (peeked == JsonToken.BEGIN_ARRAY || peeked == JsonToken.BEGIN_OBJECT);
 
-    current = tryBeginNesting(in, peeked);
-    if (current == null) {
-      return readTerminal(in, peeked);
+    if (!isNesting) {
+      return current;
     }
 
     Deque<JsonElement> stack = new ArrayDeque<>();
@@ -100,12 +87,8 @@ public class JsonElementTypeAdapter extends TypeAdapter<JsonElement> {
         }
 
         peeked = in.peek();
-        JsonElement value = tryBeginNesting(in, peeked);
-        boolean isNesting = value != null;
-
-        if (value == null) {
-          value = readTerminal(in, peeked);
-        }
+        JsonElement value = readElement(in, peeked);
+        boolean isValueNesting = (peeked == JsonToken.BEGIN_ARRAY || peeked == JsonToken.BEGIN_OBJECT);
 
         if (current instanceof JsonArray) {
           ((JsonArray) current).add(value);
@@ -113,7 +96,7 @@ public class JsonElementTypeAdapter extends TypeAdapter<JsonElement> {
           ((JsonObject) current).add(name, value);
         }
 
-        if (isNesting) {
+        if (isValueNesting) {
           stack.addLast(current);
           current = value;
         }

```
