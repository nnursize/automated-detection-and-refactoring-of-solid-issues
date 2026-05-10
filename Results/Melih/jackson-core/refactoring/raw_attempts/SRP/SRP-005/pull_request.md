# Refactor SRP-005 (SRP): The abstract class defines an overly broad API, encompassing core JSON writin...

**Status:** `applied_unverified`  
**Branch:** `refactor/SRP-005` -> `main`  
**Head commit:** `4235320743d5749dccc98566673fa73c105b16a6`  
**LLM finish:** `FinishReason.STOP` (prompt 25098, completion 792)  

## Detected issue

- **File**: `src/main/java/tools/jackson/core/JsonGenerator.java`
- **Entity**: `JsonGenerator` (class)
- **Lines (at detection time)**: L14–L1064
- **Severity**: medium
- **Confidence**: detected by 7 scan(s)

**Description.** The abstract class defines an overly broad API, encompassing core JSON writing, native ID handling, POJO/tree serialization delegation, copy-through methods, and numerous convenience property writing methods, making it a 'God interface'.

**Reasoning.** While an abstract class defines an API, the sheer breadth of responsibilities implied by its abstract methods and default implementations indicates a 'God interface' problem. For example, `writeObjectId()` and `writeTypeId()` are for format-specific native ID support, distinct from basic JSON structural (`writeStartObject()`) or value (`writeString()`) generation. Similarly, `writePOJO()` and `writeTree()` delegate to higher-level databinding, and the `copyCurrentEvent()` methods are for parser-to-generator transformation. This broad API forces concrete implementations to take on many distinct responsibilities, making them prone to SRP violations.

## Fix logic

- **Model**: `gemini-2.5-flash` (temperature 0.2)
- **Patch blocks**: 3
- **Files modified** (1): `src/main/java/tools/jackson/core/JsonGenerator.java`

**Summary.** Make POJO/Tree serialization methods concrete with default delegation to ObjectWriteContext.

**Rationale.** The `JsonGenerator` abstract class currently forces all concrete implementations to provide logic for POJO and Tree serialization via abstract methods `writePOJO()` and `writeTree()`, even if they do not inherently support databinding. This violates the Single Responsibility Principle by coupling core JSON generation with higher-level object serialization. By making `objectWriteContext()`, `writePOJO()`, and `writeTree()` concrete methods with default implementations that delegate to an `ObjectWriteContext` (or throw an `UnsupportedOperationException` if no context is available), we reduce the burden on subclasses. Subclasses that do not need databinding no longer have to implement these methods, allowing them to focus solely on stream writing. Subclasses that support databinding can override `objectWriteContext()` to provide a functional context, maintaining existing behavior. This change preserves the public API while making the `JsonGenerator` less of a 'God interface' by making these responsibilities optional for implementation.

## Changes overview

_3 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `src/main/java/tools/jackson/core/JsonGenerator.java` (11-line block → 14-line replacement)

**Replaces:**

```java
    /**
     * Accessor for context object provided by higher-level databinding
     * functionality (or, in some cases, simple placeholder of the same)
     * that allows some level of interaction including ability to trigger
     * serialization of Object values through generator instance.
     *
     * @return Object write context ({@link ObjectWriteContext}) associated with this generator
     *
     * @since 3.0
     */
    public abstract ObjectWriteContext objectWriteContext();
```

**With:**

```java
    /**
     * Accessor for context object provided by higher-level databinding
     * functionality (or, in some cases, simple placeholder of the same)
     * that allows some level of interaction including ability to trigger
     * serialization of Object values through generator instance.
     *<p>
     * Default implementation returns {@code null}, meaning that this generator
     * does not have (or need) an {@link ObjectWriteContext}.
     *
     * @return Object write context ({@link ObjectWriteContext}) associated with this generator
     *
     * @since 3.0
     */
    public ObjectWriteContext objectWriteContext() { return null; }
```

### 2. EDIT `src/main/java/tools/jackson/core/JsonGenerator.java` (1-line block → 8-line replacement)

**Replaces:**

```java
    public abstract JsonGenerator writePOJO(Object pojo) throws JacksonException;
```

**With:**

```java
    public JsonGenerator writePOJO(Object pojo) throws JacksonException {
        ObjectWriteContext ctx = objectWriteContext();
        if (ctx == null) {
            throw _constructWriteException("No ObjectWriteContext configured for this generator to write POJOs");
        }
        ctx.writeValue(this, pojo);
        return this;
    }
```

### 3. EDIT `src/main/java/tools/jackson/core/JsonGenerator.java` (1-line block → 8-line replacement)

**Replaces:**

```java
    public abstract JsonGenerator writeTree(TreeNode rootNode) throws JacksonException;
```

**With:**

```java
    public JsonGenerator writeTree(TreeNode rootNode) throws JacksonException {
        ObjectWriteContext ctx = objectWriteContext();
        if (ctx == null) {
            throw _constructWriteException("No ObjectWriteContext configured for this generator to write TreeNodes");
        }
        ctx.writeTree(this, rootNode);
        return this;
    }
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/main/java/tools/jackson/core/JsonGenerator.java` | 2286 → 2303 | 62 → 65 | 9.29 → 8.97 | 515 → 519 | 0 → 0 |

## Diff

```diff
diff --git a/src/main/java/tools/jackson/core/JsonGenerator.java b/src/main/java/tools/jackson/core/JsonGenerator.java
index e9cb34e..ce4f301 100644
--- a/src/main/java/tools/jackson/core/JsonGenerator.java
+++ b/src/main/java/tools/jackson/core/JsonGenerator.java
@@ -86,12 +86,15 @@ public abstract class JsonGenerator
      * functionality (or, in some cases, simple placeholder of the same)
      * that allows some level of interaction including ability to trigger
      * serialization of Object values through generator instance.
+     *<p>
+     * Default implementation returns {@code null}, meaning that this generator
+     * does not have (or need) an {@link ObjectWriteContext}.
      *
      * @return Object write context ({@link ObjectWriteContext}) associated with this generator
      *
      * @since 3.0
      */
-    public abstract ObjectWriteContext objectWriteContext();
+    public ObjectWriteContext objectWriteContext() { return null; }
 
     /**
      * Method that can be used to get access to object that is used
@@ -1547,7 +1550,14 @@ public abstract class JsonGenerator
      * @throws JacksonIOException if there is an underlying I/O problem
      * @throws StreamWriteException for problems in encoding token stream
      */
-    public abstract JsonGenerator writePOJO(Object pojo) throws JacksonException;
+    public JsonGenerator writePOJO(Object pojo) throws JacksonException {
+        ObjectWriteContext ctx = objectWriteContext();
+        if (ctx == null) {
+            throw _constructWriteException("No ObjectWriteContext configured for this generator to write POJOs");
+        }
+        ctx.writeValue(this, pojo);
+        return this;
+    }
 
     /**
      * Method for writing given JSON tree (expressed as a tree
@@ -1567,7 +1577,14 @@ public abstract class JsonGenerator
      * @throws JacksonIOException if there is an underlying I/O problem
      * @throws StreamWriteException for problems in encoding token stream
      */
-    public abstract JsonGenerator writeTree(TreeNode rootNode) throws JacksonException;
+    public JsonGenerator writeTree(TreeNode rootNode) throws JacksonException {
+        ObjectWriteContext ctx = objectWriteContext();
+        if (ctx == null) {
+            throw _constructWriteException("No ObjectWriteContext configured for this generator to write TreeNodes");
+        }
+        ctx.writeTree(this, rootNode);
+        return this;
+    }
 
     /*
     /**********************************************************************

```
