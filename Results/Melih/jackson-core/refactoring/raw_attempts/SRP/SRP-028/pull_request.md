# Refactor SRP-028 (SRP): The generator consumes input from a JsonParser to copy events, mixing output...

**Status:** `applied_unverified`  
**Branch:** `refactor/SRP-028` -> `main`  
**Head commit:** `68ce7e9ad175b8602bc625a892c37584b60ad05f`  
**LLM finish:** `FinishReason.STOP` (prompt 3790, completion 4559)  

## Detected issue

- **File**: `src/main/java/tools/jackson/core/JsonGenerator.java`
- **Entity**: `JsonGenerator.copyCurrentEvent` (method)
- **Lines (at detection time)**: L1285–L1329
- **Severity**: high
- **Confidence**: detected by 1 scan(s)

**Description.** The generator consumes input from a JsonParser to copy events, mixing output generation with input consumption.

**Reasoning.** A JsonGenerator's primary responsibility is to produce JSON output. Methods like `copyCurrentEvent` require a `JsonParser` as an argument and read tokens from it to write corresponding tokens. This introduces a responsibility for consuming and transforming input, which is a separate concern from simply generating output. A dedicated 'JsonTransformer' or 'JsonCopier' class would be more appropriate for this functionality.

## Fix logic

- **Model**: `gemini-2.5-flash` (temperature 0.2)
- **Patch blocks**: 3
- **Files created** (1): `src/main/java/tools/jackson/core/JsonStreamCopier.java`
- **Files modified** (1): `src/main/java/tools/jackson/core/JsonGenerator.java`

**Summary.** Extract JSON stream copying logic to a dedicated JsonStreamCopier class.

**Rationale.** The JsonGenerator's primary responsibility is to produce JSON output. The methods `copyCurrentEvent`, `copyCurrentEventExact`, and `copyCurrentStructure` violate the Single Responsibility Principle by consuming input from a JsonParser. This refactoring moves the input consumption and transformation logic into a new static helper class, `JsonStreamCopier`, in the same package. The original methods in `JsonGenerator` are retained as public API but now delegate to the new helper class, ensuring existing behavior and API compatibility. Error reporting for 'no current event' is handled by throwing a `StreamReadException` directly from the helper, as `_reportError` is an abstract method of `JsonGenerator` and cannot be called from a static helper.

## Changes overview

_3 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `src/main/java/tools/jackson/core/JsonGenerator.java` (65-line block → 20-line replacement)

**Replaces:**

```java
    /**
     * Method for copying contents of the current event that
     * the given parser instance points to.
     * Note that the method <b>will not</b> copy any other events,
     * such as events contained within JSON Array or Object structures.
     *<p>
     * Calling this method will not advance the given
     * parser, although it may cause parser to internally process
     * more data (if it lazy loads contents of value events, for example)
     *
     * @param p Parser that points to the event to copy
     *
     * @throws JacksonIOException if there is an underlying I/O problem (reading or writing)
     * @throws StreamReadException for problems with decoding of token stream
     * @throws StreamWriteException for problems in encoding token stream
     */
    public void copyCurrentEvent(JsonParser p) throws JacksonException
    {
        JsonToken t = p.currentToken();
        final int token = (t == null) ? ID_NOT_AVAILABLE : t.id();
        switch (token) {
        case ID_NOT_AVAILABLE:
            _reportError("No current event to copy");
            break; // never gets here
        case ID_START_OBJECT:
            writeStartObject();
            break;
        case ID_END_OBJECT:
            writeEndObject();
            break;
        case ID_START_ARRAY:
            writeStartArray();
            break;
        case ID_END_ARRAY:
            writeEndArray();
            break;
        case ID_PROPERTY_NAME:
            writeName(p.currentName());
            break;
        case ID_STRING:
            _copyCurrentStringValue(p);
            break;
        case ID_NUMBER_INT:
            _copyCurrentIntValue(p);
            break;
        case ID_NUMBER_FLOAT:
            // Different from "copyCurrentEventExact"!
            _copyCurrentFloatValue(p);
            break;
        case ID_TRUE:
            writeBoolean(true);
            break;
        case ID_FALSE:
            writeBoolean(false);
            break;
        case ID_NULL:
            writeNull();
            break;
        case ID_EMBEDDED_OBJECT:
            writePOJO(p.getEmbeddedObject());
... (5 more line(s) truncated)
```

**With:**

```java
    /**
     * Method for copying contents of the current event that
     * the given parser instance points to.
     * Note that the method <b>will not</b> copy any other events,
     * such as events contained within JSON Array or Object structures.
     *<p>
     * Calling this method will not advance the given
     * parser, although it may cause parser to internally process
     * more data (if it lazy loads contents of value events, for example)
     *
     * @param p Parser that points to the event to copy
     *
     * @throws JacksonIOException if there is an underlying I/O problem (reading or writing)
     * @throws StreamReadException for problems with decoding of token stream
     * @throws StreamWriteException for problems in encoding token stream
     */
    public void copyCurrentEvent(JsonParser p) throws JacksonException
    {
        JsonStreamCopier.copyCurrentEvent(p, this);
    }
```

### 2. EDIT `src/main/java/tools/jackson/core/JsonGenerator.java` (71-line block → 58-line replacement)

**Replaces:**

```java
    /**
     * Same as {@link #copyCurrentEvent} with the exception that copying of numeric
     * values tries to avoid any conversion losses; in particular for floating-point
     * numbers. This usually matters when transcoding from textual format like JSON
     * to a binary format.
     * See {@link #_copyCurrentFloatValueExact} for details.
     *
     * @param p Parser that points to the event to copy
     *
     * @throws JacksonIOException if there is an underlying I/O problem (reading or writing)
     * @throws StreamReadException for problems with decoding of token stream
     * @throws StreamWriteException for problems in encoding token stream
     */
    public void copyCurrentEventExact(JsonParser p) throws JacksonException
    {
        JsonToken t = p.currentToken();
        final int token = (t == null) ? ID_NOT_AVAILABLE : t.id();
        switch (token) {
        case ID_NOT_AVAILABLE:
            _reportError("No current event to copy");
            break; // never gets here
        case ID_START_OBJECT:
            writeStartObject();
            break;
        case ID_END_OBJECT:
            writeEndObject();
            break;
        case ID_START_ARRAY:
            writeStartArray();
            break;
        case ID_END_ARRAY:
            writeEndArray();
            break;
        case ID_PROPERTY_NAME:
            writeName(p.currentName());
            break;
        case ID_STRING:
            _copyCurrentStringValue(p);
            break;
        case ID_NUMBER_INT:
            _copyCurrentIntValue(p);
            break;
        case ID_NUMBER_FLOAT:
            // Different from "copyCurrentEvent"!
            _copyCurrentFloatValueExact(p);
            break;
        case ID_TRUE:
            writeBoolean(true);
            break;
        case ID_FALSE:
            writeBoolean(false);
            break;
        case ID_NULL:
            writeNull();
            break;
        case ID_EMBEDDED_OBJECT:
            writePOJO(p.getEmbeddedObject());
            break;
        default:
            throw new IllegalStateException("Internal error: unknown current token, "+t);
... (11 more line(s) truncated)
```

**With:**

```java
    /**
     * Same as {@link #copyCurrentEvent} with the exception that copying of numeric
     * values tries to avoid any conversion losses; in particular for floating-point
     * numbers. This usually matters when transcoding from textual format like JSON
     * to a binary format.
     * See {@link #_copyCurrentFloatValueExact} for details.
     *
     * @param p Parser that points to the event to copy
     *
     * @throws JacksonIOException if there is an underlying I/O problem (reading or writing)
     * @throws StreamReadException for problems with decoding of token stream
     * @throws StreamWriteException for problems in encoding token stream
     */
    public void copyCurrentEventExact(JsonParser p) throws JacksonException
    {
        JsonStreamCopier.copyCurrentEventExact(p, this);
    }

    /**
     * Method for copying contents of the current event
     * <b>and following events that it encloses</b>
     * the given parser instance points to.
     *<p>
     * So what constitutes enclosing? Here is the list of
     * events that have associated enclosed events that will
     * get copied:
     *<ul>
     * <li>{@link JsonToken#START_OBJECT Object Start}:
     *  all events up to and including matching {@link JsonToken#END_OBJECT Object End}
     *  will be copied
     *  </li>
     * <li>{@link JsonToken#START_ARRAY Array Start}:
     *  all events up to and including matching {@link JsonToken#END_ARRAY Array End}
     *  will be copied
     *  </li>
     * <li>All other events (simple values, field names):
     *  only the current event is copied
     *  </li>
     *</ul>
     * This method is more efficient than {@link #copyCurrentEvent} as it can
     * make use of internal buffering; and it is the method that should be
     * used when an entire Object or Array needs to be copied.
     *<p>
     * Calling this method will advance the given parser past the copied
     * event(s).
     *
     * @param p Parser that points to the event to copy
     *
     * @return The parser, to allow call chaining
     *
     * @throws JacksonIOException if there is an underlying I/O problem (reading or writing)
     * @throws StreamReadException for problems with decoding of token stream
     * @throws StreamWriteException for problems in encoding token stream
     */
    public JsonParser copyCurrentStructure(JsonParser p) throws JacksonException
    {
        return JsonStreamCopier.copyCurrentStructure(p, this);
    }
```

### 3. CREATE `src/main/java/tools/jackson/core/JsonStreamCopier.java` (231 line(s))

```java
package tools.jackson.core;

import tools.jackson.core.exc.StreamReadException;
import tools.jackson.core.exc.StreamWriteException;

/**
 * Helper class that encapsulates logic for copying JSON events from a {@link JsonParser}
 * to a {@link JsonGenerator}. This separates the concern of reading/transforming
 * from the primary responsibility of a {@link JsonGenerator} (writing).
 *
 * @since 3.0
 */
public class JsonStreamCopier
{
    /**
     * Method for copying contents of the current event that
     * the given parser instance points to.
     * Note that the method <b>will not</b> copy any other events,
     * such as events contained within JSON Array or Object structures.
     *<p>
     * Calling this method will not advance the given
     * parser, although it may cause parser to internally process
     * more data (if it lazy loads contents of value events, for example)
     *
     * @param p Parser that points to the event to copy
     * @param g Generator to write the event to
     *
     * @throws JacksonException if there is an underlying I/O problem (reading or writing)
     * @throws StreamReadException for problems with decoding of token stream
     * @throws StreamWriteException for problems in encoding token stream
     */
    public static void copyCurrentEvent(JsonParser p, JsonGenerator g) throws JacksonException
    {
        JsonToken t = p.currentToken();
        final int token = (t == null) ? JsonTokenId.ID_NOT_AVAILABLE : t.id();
        switch (token) {
        case JsonTokenId.ID_NOT_AVAILABLE:
            // Original code called _reportError, which is abstract.
            // Throw a StreamReadException directly as this is a parser-related issue.
            throw new StreamReadException(p, "No current event to copy");
        case JsonTokenId.ID_START_OBJECT:
            g.writeStartObject();
            break;
        case JsonTokenId.ID_END_OBJECT:
            g.writeEndObject();
            break;
        case JsonTokenId.ID_START_ARRAY:
            g.writeStartArray();
            break;
        case JsonTokenId.ID_END_ARRAY:
            g.writeEndArray();
            break;
        case JsonTokenId.ID_PROPERTY_NAME:
            g.writeName(p.currentName());
            break;
        case JsonTokenId.ID_STRING:
            g._copyCurrentStringValue(p);
            break;
        case JsonTokenId.ID_NUMBER_INT:
            g._copyCurrentIntValue(p);
... (171 more line(s) truncated)
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/main/java/tools/jackson/core/JsonGenerator.java` | 2303 → 2247 | 65 → 66 | 8.97 → 8.52 | 519 → 497 | 0 → 0 |
| `src/main/java/tools/jackson/core/JsonStreamCopier.java` | - → 213 | - → 3 | - → 18.67 | - → 54 | - → 0 |

## Diff

```diff
diff --git a/src/main/java/tools/jackson/core/JsonGenerator.java b/src/main/java/tools/jackson/core/JsonGenerator.java
index ce4f301..dff53e0 100644
--- a/src/main/java/tools/jackson/core/JsonGenerator.java
+++ b/src/main/java/tools/jackson/core/JsonGenerator.java
@@ -1951,52 +1951,7 @@ public abstract class JsonGenerator
      */
     public void copyCurrentEvent(JsonParser p) throws JacksonException
     {
-        JsonToken t = p.currentToken();
-        final int token = (t == null) ? ID_NOT_AVAILABLE : t.id();
-        switch (token) {
-        case ID_NOT_AVAILABLE:
-            _reportError("No current event to copy");
-            break; // never gets here
-        case ID_START_OBJECT:
-            writeStartObject();
-            break;
-        case ID_END_OBJECT:
-            writeEndObject();
-            break;
-        case ID_START_ARRAY:
-            writeStartArray();
-            break;
-        case ID_END_ARRAY:
-            writeEndArray();
-            break;
-        case ID_PROPERTY_NAME:
-            writeName(p.currentName());
-            break;
-        case ID_STRING:
-            _copyCurrentStringValue(p);
-            break;
-        case ID_NUMBER_INT:
-            _copyCurrentIntValue(p);
-            break;
-        case ID_NUMBER_FLOAT:
-            // Different from "copyCurrentEventExact"!
-            _copyCurrentFloatValue(p);
-            break;
-        case ID_TRUE:
-            writeBoolean(true);
-            break;
-        case ID_FALSE:
-            writeBoolean(false);
-            break;
-        case ID_NULL:
-            writeNull();
-            break;
-        case ID_EMBEDDED_OBJECT:
-            writePOJO(p.getEmbeddedObject());
-            break;
-        default:
-            throw new IllegalStateException("Internal error: unknown current token, "+t);
-        }
+        JsonStreamCopier.copyCurrentEvent(p, this);
     }
 
     /**
@@ -2014,52 +1969,7 @@ public abstract class JsonGenerator
      */
     public void copyCurrentEventExact(JsonParser p) throws JacksonException
     {
-        JsonToken t = p.currentToken();
-        final int token = (t == null) ? ID_NOT_AVAILABLE : t.id();
-        switch (token) {
-        case ID_NOT_AVAILABLE:
-            _reportError("No current event to copy");
-            break; // never gets here
-        case ID_START_OBJECT:
-            writeStartObject();
-            break;
-        case ID_END_OBJECT:
-            writeEndObject();
-            break;
-        case ID_START_ARRAY:
-            writeStartArray();
-            break;
-        case ID_END_ARRAY:
-            writeEndArray();
-            break;
-        case ID_PROPERTY_NAME:
-            writeName(p.currentName());
-            break;
-        case ID_STRING:
-            _copyCurrentStringValue(p);
-            break;
-        case ID_NUMBER_INT:
-            _copyCurrentIntValue(p);
-            break;
-        case ID_NUMBER_FLOAT:
-            // Different from "copyCurrentEvent"!
-            _copyCurrentFloatValueExact(p);
-            break;
-        case ID_TRUE:
-            writeBoolean(true);
-            break;
-        case ID_FALSE:
-            writeBoolean(false);
-            break;
-        case ID_NULL:
-            writeNull();
-            break;
-        case ID_EMBEDDED_OBJECT:
-            writePOJO(p.getEmbeddedObject());
-            break;
-        default:
-            throw new IllegalStateException("Internal error: unknown current token, "+t);
-        }
+        JsonStreamCopier.copyCurrentEventExact(p, this);
     }
 
     /**
@@ -2070,6 +1980,38 @@ public abstract class JsonGenerator
      * So what constitutes enclosing? Here is the list of
      * events that have associated enclosed events that will
      * get copied:
+     *<ul>
+     * <li>{@link JsonToken#START_OBJECT Object Start}:
+     *  all events up to and including matching {@link JsonToken#END_OBJECT Object End}
+     *  will be copied
+     *  </li>
+     * <li>{@link JsonToken#START_ARRAY Array Start}:
+     *  all events up to and including matching {@link JsonToken#END_ARRAY Array End}
+     *  will be copied
+     *  </li>
+     * <li>All other events (simple values, field names):
+     *  only the current event is copied
+     *  </li>
+     *</ul>
+     * This method is more efficient than {@link #copyCurrentEvent} as it can
+     * make use of internal buffering; and it is the method that should be
+     * used when an entire Object or Array needs to be copied.
+     *<p>
+     * Calling this method will advance the given parser past the copied
+     * event(s).
+     *
+     * @param p Parser that points to the event to copy
+     *
+     * @return The parser, to allow call chaining
+     *
+     * @throws JacksonIOException if there is an underlying I/O problem (reading or writing)
+     * @throws StreamReadException for problems with decoding of token stream
+     * @throws StreamWriteException for problems in encoding token stream
+     */
+    public JsonParser copyCurrentStructure(JsonParser p) throws JacksonException
+    {
+        return JsonStreamCopier.copyCurrentStructure(p, this);
+    }
      *<ul>
      * <li>{@link JsonToken#START_OBJECT}:
      *   all events up to and including matching (closing)
diff --git a/src/main/java/tools/jackson/core/JsonStreamCopier.java b/src/main/java/tools/jackson/core/JsonStreamCopier.java
new file mode 100644
index 0000000..0000000
--- /dev/null
+++ b/src/main/java/tools/jackson/core/JsonStreamCopier.java
@@ -0,0 +1,231 @@
+package tools.jackson.core;
+
+import tools.jackson.core.exc.StreamReadException;
+import tools.jackson.core.exc.StreamWriteException;
+
+/**
+ * Helper class that encapsulates logic for copying JSON events from a {@link JsonParser}
+ * to a {@link JsonGenerator}. This separates the concern of reading/transforming
+ * from the primary responsibility of a {@link JsonGenerator} (writing).
+ *
+ * @since 3.0
+ */
+public class JsonStreamCopier
+{
+    /**
+     * Method for copying contents of the current event that
+     * the given parser instance points to.
+     * Note that the method <b>will not</b> copy any other events,
+     * such as events contained within JSON Array or Object structures.
+     *<p>
+     * Calling this method will not advance the given
+     * parser, although it may cause parser to internally process
+     * more data (if it lazy loads contents of value events, for example)
+     *
+     * @param p Parser that points to the event to copy
+     * @param g Generator to write the event to
+     *
+     * @throws JacksonException if there is an underlying I/O problem (reading or writing)
+     * @throws StreamReadException for problems with decoding of token stream
+     * @throws StreamWriteException for problems in encoding token stream
+     */
+    public static void copyCurrentEvent(JsonParser p, JsonGenerator g) throws JacksonException
+    {
+        JsonToken t = p.currentToken();
+        final int token = (t == null) ? JsonTokenId.ID_NOT_AVAILABLE : t.id();
+        switch (token) {
+        case JsonTokenId.ID_NOT_AVAILABLE:
+            // Original code called _reportError, which is abstract.
+            // Throw a StreamReadException directly as this is a parser-related issue.
+            throw new StreamReadException(p, "No current event to copy");
+        case JsonTokenId.ID_START_OBJECT:
+            g.writeStartObject();
+            break;
+        case JsonTokenId.ID_END_OBJECT:
+            g.writeEndObject();
+            break;
+        case JsonTokenId.ID_START_ARRAY:
+            g.writeStartArray();
+            break;
+        case JsonTokenId.ID_END_ARRAY:
+            g.writeEndArray();
+            break;
+        case JsonTokenId.ID_PROPERTY_NAME:
+            g.writeName(p.currentName());
+            break;
+        case JsonTokenId.ID_STRING:
+            g._copyCurrentStringValue(p);
+            break;
+        case JsonTokenId.ID_NUMBER_INT:
+            g._copyCurrentIntValue(p);
+            break;
+        case JsonTokenId.ID_NUMBER_FLOAT:
+            // Different from "copyCurrentEventExact"!
+            g._copyCurrentFloatValue(p);
+            break;
+        case JsonTokenId.ID_TRUE:
+            g.writeBoolean(true);
+            break;
+        case JsonTokenId.ID_FALSE:
+            g.writeBoolean(false);
+            break;
+        case JsonTokenId.ID_NULL:
+            g.writeNull();
+            break;
+        case JsonTokenId.ID_EMBEDDED_OBJECT:
+            g.writePOJO(p.getEmbeddedObject());
+            break;
+        default:
+            throw new IllegalStateException("Internal error: unknown current token, "+t);
+        }
+    }
+
+    /**
+     * Same as {@link #copyCurrentEvent} with the exception that copying of numeric
+     * values tries to avoid any conversion losses; in particular for floating-point
+     * numbers. This usually matters when transcoding from textual format like JSON
+     * to a binary format.
+     * See {@link JsonGenerator#_copyCurrentFloatValueExact} for details.
+     *
+     * @param p Parser that points to the event to copy
+     * @param g Generator to write the event to
+     *
+     * @throws JacksonException if there is an underlying I/O problem (reading or writing)
+     * @throws StreamReadException for problems with decoding of token stream
+     * @throws StreamWriteException for problems in encoding token stream
+     */
+    public static void copyCurrentEventExact(JsonParser p, JsonGenerator g) throws JacksonException
+    {
+        JsonToken t = p.currentToken();
+        final int token = (t == null) ? JsonTokenId.ID_NOT_AVAILABLE : t.id();
+        switch (token) {
+        case JsonTokenId.ID_NOT_AVAILABLE:
+            // Original code called _reportError, which is abstract.
+            // Throw a StreamReadException directly as this is a parser-related issue.
+            throw new StreamReadException(p, "No current event to copy");
+        case JsonTokenId.ID_START_OBJECT:
+            g.writeStartObject();
+            break;
+        case JsonTokenId.ID_END_OBJECT:
+            g.writeEndObject();
+            break;
+        case JsonTokenId.ID_START_ARRAY:
+            g.writeStartArray();
+            break;
+        case JsonTokenId.ID_END_ARRAY:
+            g.writeEndArray();
+            break;
+        case JsonTokenId.ID_PROPERTY_NAME:
+            g.writeName(p.currentName());
+            break;
+        case JsonTokenId.ID_STRING:
+            g._copyCurrentStringValue(p);
+            break;
+        case JsonTokenId.ID_NUMBER_INT:
+            g._copyCurrentIntValue(p);
+            break;
+        case JsonTokenId.ID_NUMBER_FLOAT:
+            // Different from "copyCurrentEvent"!
+            g._copyCurrentFloatValueExact(p);
+            break;
+        case JsonTokenId.ID_TRUE:
+            g.writeBoolean(true);
+            break;
+        case JsonTokenId.ID_FALSE:
+            g.writeBoolean(false);
+            break;
+        case JsonTokenId.ID_NULL:
+            g.writeNull();
+            break;
+        case JsonTokenId.ID_EMBEDDED_OBJECT:
+            g.writePOJO(p.getEmbeddedObject());
+            break;
+        default:
+            throw new IllegalStateException("Internal error: unknown current token, "+t);
+        }
+    }
+
+    /**
+     * Method for copying contents of the current event
+     * <b>and following events that it encloses</b>
+     * the given parser instance points to.
+     *<p>
+     * So what constitutes enclosing? Here is the list of
+     * events that have associated enclosed events that will
+     * get copied:
+     *<ul>
+     * <li>{@link JsonToken#START_OBJECT Object Start}:
+     *  all events up to and including matching {@link JsonToken#END_OBJECT Object End}
+     *  will be copied
+     *  </li>
+     * <li>{@link JsonToken#START_ARRAY Array Start}:
+     *  all events up to and including matching {@link JsonToken#END_ARRAY Array End}
+     *  will be copied
+     *  </li>
+     * <li>All other events (simple values, field names):
+     *  only the current event is copied
+     *  </li>
+     *</ul>
+     * This method is more efficient than {@link #copyCurrentEvent} as it can
+     * make use of internal buffering; and it is the method that should be
+     * used when an entire Object or Array needs to be copied.
+     *<p>
+     * Calling this method will advance the given parser past the copied
+     * event(s).
+     *
+     * @param p Parser that points to the event to copy
+     * @param g Generator to write the event to
+     *
+     * @return The parser, to allow call chaining
+     *
+     * @throws JacksonIOException if there is an underlying I/O problem (reading or writing)
+     * @throws StreamReadException for problems with decoding of token stream
+     * @throws StreamWriteException for problems in encoding token stream
+     */
+    public static JsonParser copyCurrentStructure(JsonParser p, JsonGenerator g) throws JacksonException
+    {
+        JsonToken t = p.currentToken();
+
+        // Let's handle field names separately first
+        if (t == JsonToken.PROPERTY_NAME) {
+            g.writeName(p.currentName());
+            t = p.nextToken();
+            // fall through to copy value
+        }
+
+        int token = (t == null) ? JsonTokenId.ID_NOT_AVAILABLE : t.id();
+        switch (token) {
+        case JsonTokenId.ID_START_OBJECT:
+            g.writeStartObject();
+            while (p.nextToken() != JsonToken.END_OBJECT) {
+                copyCurrentStructure(p, g);
+            }
+            g.writeEndObject();
+            break;
+        case JsonTokenId.ID_START_ARRAY:
+            g.writeStartArray();
+            while (p.nextToken() != JsonToken.END_ARRAY) {
+                copyCurrentStructure(p, g);
+            }
+            g.writeEndArray();
+            break;
+        case JsonTokenId.ID_NOT_AVAILABLE:
+            // Original code called _reportError, which is abstract.
+            // Throw a StreamReadException directly as this is a parser-related issue.
+            throw new StreamReadException(p, "No current event to copy");
+        case JsonTokenId.ID_END_OBJECT: // or END_ARRAY
+        case JsonTokenId.ID_END_ARRAY: // or END_OBJECT
+            // These are generally error cases, but we'll let generator handle them
+            // (usually by throwing an exception)
+            JsonStreamCopier.copyCurrentEvent(p, g);
+            break;
+        case JsonTokenId.ID_PROPERTY_NAME: // Should not happen after above
+            g.writeName(p.currentName());
+            break;
+        default: // others are simple:
+            JsonStreamCopier.copyCurrentEvent(p, g);
+            break;
+        }
+        return p;
+    }
+}
\ No newline at end of file

```
