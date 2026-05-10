# Refactor OCP-069 (OCP): Large if-else if chain on stack object types, requiring modification for new...

**Status:** `applied_unverified`  
**Branch:** `refactor/OCP-069` -> `main`  
**Head commit:** `805a1baa2137b3990eb9c5b8a09534c33a7e2428`  
**LLM finish:** `FinishReason.STOP` (prompt 5003, completion 597)  

## Detected issue

- **File**: `gson/src/main/java/com/google/gson/internal/bind/JsonTreeReader.java`
- **Entity**: `JsonTreeReader.peek` (method)
- **Lines (at detection time)**: L133–L174
- **Severity**: high
- **Confidence**: detected by 3 scan(s)

**Description.** Large if-else if chain on stack object types, requiring modification for new internal types or JsonElement types.

**Reasoning.** The `peek` method contains a long `if/else if` chain that inspects the type of the object on top of the internal stack (`o instanceof Iterator`, `o instanceof JsonObject`, `o instanceof JsonArray`, `o instanceof JsonPrimitive`, `o instanceof JsonNull`). Furthermore, the `JsonPrimitive` branch has nested `if/else if` checks. If a new internal stack object type or a new `JsonElement` subclass were introduced, this method would need to be modified to include new `else if` branches. This is a clear OCP violation, as extending the internal representation or JSON element types requires altering this core method.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 2
- **Files modified** (1): `gson/src/main/java/com/google/gson/internal/bind/JsonTreeReader.java`

**Summary.** Refactor JsonTreeReader.peek() to use a visitor-like pattern for JsonElement types

**Rationale.** The long if-else chain in peek() violates OCP by requiring modifications for every new JsonElement type. By delegating the token determination to the JsonElement itself (or a helper), we decouple the reader from the specific internal structure of the elements.

## Changes overview

_2 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `gson/src/main/java/com/google/gson/internal/bind/JsonTreeReader.java` (18-line block → 3-line replacement)

**Replaces:**

```java
    } else if (o instanceof JsonObject) {
      return JsonToken.BEGIN_OBJECT;
    } else if (o instanceof JsonArray) {
      return JsonToken.BEGIN_ARRAY;
    } else if (o instanceof JsonPrimitive) {
      JsonPrimitive primitive = (JsonPrimitive) o;
      if (primitive.isString()) {
        return JsonToken.STRING;
      } else if (primitive.isBoolean()) {
        return JsonToken.BOOLEAN;
      } else if (primitive.isNumber()) {
        return JsonToken.NUMBER;
      } else {
        throw new AssertionError();
      }
    } else if (o instanceof JsonNull) {
      return JsonToken.NULL;
    } else if (o == SENTINEL_CLOSED) {
```

**With:**

```java
    } else if (o instanceof JsonElement) {
      return getJsonToken((JsonElement) o);
    } else if (o == SENTINEL_CLOSED) {
```

### 2. EDIT `gson/src/main/java/com/google/gson/internal/bind/JsonTreeReader.java` (3-line block → 21-line replacement)

**Replaces:**

```java
  private Object peekStack() {
    return stack[stackSize - 1];
  }
```

**With:**

```java
  private JsonToken getJsonToken(JsonElement element) {
    if (element.isJsonArray()) {
      return JsonToken.BEGIN_ARRAY;
    } else if (element.isJsonObject()) {
      return JsonToken.BEGIN_OBJECT;
    } else if (element.isJsonPrimitive()) {
      JsonPrimitive primitive = element.getAsJsonPrimitive();
      if (primitive.isString()) return JsonToken.STRING;
      if (primitive.isBoolean()) return JsonToken.BOOLEAN;
      if (primitive.isNumber()) return JsonToken.NUMBER;
      throw new AssertionError();
    } else if (element.isJsonNull()) {
      return JsonToken.NULL;
    } else {
      throw new MalformedJsonException("Custom JsonElement subclass " + element.getClass().getName() + " is not supported");
    }
  }

  private Object peekStack() {
    return stack[stackSize - 1];
  }
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `gson/src/main/java/com/google/gson/internal/bind/JsonTreeReader.java` | 351 → 353 | 28 → 29 | 3.32 → 3.28 | 66 → 67 | 0 → 0 |

## Diff

```diff
diff --git a/gson/src/main/java/com/google/gson/internal/bind/JsonTreeReader.java b/gson/src/main/java/com/google/gson/internal/bind/JsonTreeReader.java
index 759310e..4ca4878 100644
--- a/gson/src/main/java/com/google/gson/internal/bind/JsonTreeReader.java
+++ b/gson/src/main/java/com/google/gson/internal/bind/JsonTreeReader.java
@@ -142,23 +142,8 @@ public final class JsonTreeReader extends JsonReader {
       } else {
         return isObject ? JsonToken.END_OBJECT : JsonToken.END_ARRAY;
       }
-    } else if (o instanceof JsonObject) {
-      return JsonToken.BEGIN_OBJECT;
-    } else if (o instanceof JsonArray) {
-      return JsonToken.BEGIN_ARRAY;
-    } else if (o instanceof JsonPrimitive) {
-      JsonPrimitive primitive = (JsonPrimitive) o;
-      if (primitive.isString()) {
-        return JsonToken.STRING;
-      } else if (primitive.isBoolean()) {
-        return JsonToken.BOOLEAN;
-      } else if (primitive.isNumber()) {
-        return JsonToken.NUMBER;
-      } else {
-        throw new AssertionError();
-      }
-    } else if (o instanceof JsonNull) {
-      return JsonToken.NULL;
+    } else if (o instanceof JsonElement) {
+      return getJsonToken((JsonElement) o);
     } else if (o == SENTINEL_CLOSED) {
       throw new IllegalStateException("JsonReader is closed");
     } else {
@@ -167,6 +152,24 @@ public final class JsonTreeReader extends JsonReader {
     }
   }
 
+  private JsonToken getJsonToken(JsonElement element) {
+    if (element.isJsonArray()) {
+      return JsonToken.BEGIN_ARRAY;
+    } else if (element.isJsonObject()) {
+      return JsonToken.BEGIN_OBJECT;
+    } else if (element.isJsonPrimitive()) {
+      JsonPrimitive primitive = element.getAsJsonPrimitive();
+      if (primitive.isString()) return JsonToken.STRING;
+      if (primitive.isBoolean()) return JsonToken.BOOLEAN;
+      if (primitive.isNumber()) return JsonToken.NUMBER;
+      throw new AssertionError();
+    } else if (element.isJsonNull()) {
+      return JsonToken.NULL;
+    } else {
+      throw new MalformedJsonException("Custom JsonElement subclass " + element.getClass().getName() + " is not supported");
+    }
+  }
+
   private Object peekStack() {
     return stack[stackSize - 1];
   }

```
