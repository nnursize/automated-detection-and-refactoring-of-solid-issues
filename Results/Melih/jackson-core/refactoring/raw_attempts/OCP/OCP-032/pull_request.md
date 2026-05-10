# Refactor OCP-032 (OCP): Switch statement on JsonToken ID requires modification to support new token t...

**Status:** `applied_unverified`  
**Branch:** `refactor/OCP-032` -> `main`  
**Head commit:** `3bd25e544e5cf1956a7ae004f360f589ba35cf21`  
**LLM finish:** `FinishReason.STOP` (prompt 3558, completion 1154)  

## Detected issue

- **File**: `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java`
- **Entity**: `UTF8StreamJsonParser.getStringCharacters` (method)
- **Lines (at detection time)**: L311–L331
- **Severity**: medium
- **Confidence**: detected by 3 scan(s)

**Description.** Switch statement on JsonToken ID requires modification to support new token types.

**Reasoning.** The switch statement on `_currToken.id()` necessitates changes to existing code whenever new token types are introduced in the Jackson framework.

## Fix logic

- **Model**: `gemini-2.5-flash` (temperature 0.2)
- **Patch blocks**: 2
- **Files modified** (1): `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java`

**Summary.** Replaced switch statement in `getStringCharacters` with an EnumMap for OCP adherence.

**Rationale.** The original `getStringCharacters` method contained a switch statement on `_currToken.id()`, which violates the Open/Closed Principle (OCP) because adding new `JsonToken` types would necessitate modifying this method. The refactoring replaces the switch statement with a static `EnumMap` that maps `JsonToken` instances to `TokenCharGetter` functional interfaces. This approach centralizes the token-specific logic into the map's initialization block. Now, `getStringCharacters` is closed for modification; if a new `JsonToken` requires special handling, only the `TOKEN_CHAR_GETTERS` map needs to be updated, rather than altering the method's core logic. For tokens not explicitly in the map, the default `_currToken.asCharArray()` is used, leveraging existing polymorphism.

## Changes overview

_2 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java` (21-line block → 48-line replacement)

**Replaces:**

```java
    protected final String _getText2(JsonToken t) throws JacksonException
    {
        if (t == null) {
            return null;
        }
        switch (t.id()) {
        case ID_PROPERTY_NAME:
            return _streamReadContext.currentName();

        case ID_STRING:
            // fall through
        case ID_NUMBER_INT:
        case ID_NUMBER_FLOAT:
            return _textBuffer.contentsAsString();
        default:
        	return t.asString();
        }
    }

    @Override
    public char[] getStringCharacters() throws JacksonException
```

**With:**

```java
    protected final String _getText2(JsonToken t) throws JacksonException
    {
        if (t == null) {
            return null;
        }
        switch (t.id()) {
        case ID_PROPERTY_NAME:
            return _streamReadContext.currentName();

        case ID_STRING:
            // fall through
        case ID_NUMBER_INT:
        case ID_NUMBER_FLOAT:
            return _textBuffer.contentsAsString();
        default:
        	return t.asString();
        }
    }

    // --- OCP Refactoring for getStringCharacters ---
    @FunctionalInterface
    private interface TokenCharGetter {
        char[] get(UTF8StreamJsonParser parser) throws JacksonException;
    }

    private static final java.util.Map<tools.jackson.core.JsonToken, TokenCharGetter> TOKEN_CHAR_GETTERS;

    static {
        TOKEN_CHAR_GETTERS = new java.util.EnumMap<>(tools.jackson.core.JsonToken.class);
        TOKEN_CHAR_GETTERS.put(tools.jackson.core.JsonToken.PROPERTY_NAME, UTF8StreamJsonParser::currentNameInBuffer);
        TOKEN_CHAR_GETTERS.put(tools.jackson.core.JsonToken.VALUE_STRING, parser -> {
            if (parser._tokenIncomplete) {
                parser._tokenIncomplete = false;
                parser._finishString();
            }
            return parser._textBuffer.getTextBuffer();
        });
        TOKEN_CHAR_GETTERS.put(tools.jackson.core.JsonToken.VALUE_NUMBER_INT, UTF8StreamJsonParser::getTextBufferContents);
        TOKEN_CHAR_GETTERS.put(tools.jackson.core.JsonToken.VALUE_NUMBER_FLOAT, UTF8StreamJsonParser::getTextBufferContents);
    }

    // Helper method to avoid repeating _textBuffer.getTextBuffer() in lambda
    private char[] getTextBufferContents() {
        return _textBuffer.getTextBuffer();
    }

    @Override
    public char[] getStringCharacters() throws JacksonException
```

### 2. EDIT `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java` (23-line block → 11-line replacement)

**Replaces:**

```java
    public char[] getStringCharacters() throws JacksonException
    {
        if (_currToken != null) { // null only before/after document
            switch (_currToken.id()) {

            case ID_PROPERTY_NAME:
                return currentNameInBuffer();
            case ID_STRING:
                if (_tokenIncomplete) {
                    _tokenIncomplete = false;
                    _finishString(); // only strings can be incomplete
                }
                // fall through
            case ID_NUMBER_INT:
            case ID_NUMBER_FLOAT:
                return _textBuffer.getTextBuffer();

            default:
                return _currToken.asCharArray();
            }
        }
        return null;
    }
```

**With:**

```java
    public char[] getStringCharacters() throws JacksonException
    {
        if (_currToken == null) { // null only before/after document
            return null;
        }
        TokenCharGetter getter = TOKEN_CHAR_GETTERS.get(_currToken);
        if (getter != null) {
            return getter.get(this);
        }
        return _currToken.asCharArray();
    }
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java` | 3534 → 3546 | 112 → 113 | 9.81 → 9.72 | 988 → 986 | 0 → 0 |

## Diff

```diff
diff --git a/src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java b/src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java
index 8a3e347..39108fe 100644
--- a/src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java
+++ b/src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java
@@ -422,29 +422,44 @@ public class UTF8StreamJsonParser
         }
     }
 
-    @Override
-    public char[] getStringCharacters() throws JacksonException
-    {
-        if (_currToken != null) { // null only before/after document
-            switch (_currToken.id()) {
+    // --- OCP Refactoring for getStringCharacters ---
+    @FunctionalInterface
+    private interface TokenCharGetter {
+        char[] get(UTF8StreamJsonParser parser) throws JacksonException;
+    }
 
-            case ID_PROPERTY_NAME:
-                return currentNameInBuffer();
-            case ID_STRING:
-                if (_tokenIncomplete) {
-                    _tokenIncomplete = false;
-                    _finishString(); // only strings can be incomplete
-                }
-                // fall through
-            case ID_NUMBER_INT:
-            case ID_NUMBER_FLOAT:
-                return _textBuffer.getTextBuffer();
+    private static final java.util.Map<tools.jackson.core.JsonToken, TokenCharGetter> TOKEN_CHAR_GETTERS;
 
-            default:
-                return _currToken.asCharArray();
+    static {
+        TOKEN_CHAR_GETTERS = new java.util.EnumMap<>(tools.jackson.core.JsonToken.class);
+        TOKEN_CHAR_GETTERS.put(tools.jackson.core.JsonToken.PROPERTY_NAME, UTF8StreamJsonParser::currentNameInBuffer);
+        TOKEN_CHAR_GETTERS.put(tools.jackson.core.JsonToken.VALUE_STRING, parser -> {
+            if (parser._tokenIncomplete) {
+                parser._tokenIncomplete = false;
+                parser._finishString();
             }
+            return parser._textBuffer.getTextBuffer();
+        });
+        TOKEN_CHAR_GETTERS.put(tools.jackson.core.JsonToken.VALUE_NUMBER_INT, UTF8StreamJsonParser::getTextBufferContents);
+        TOKEN_CHAR_GETTERS.put(tools.jackson.core.JsonToken.VALUE_NUMBER_FLOAT, UTF8StreamJsonParser::getTextBufferContents);
+    }
+
+    // Helper method to avoid repeating _textBuffer.getTextBuffer() in lambda
+    private char[] getTextBufferContents() {
+        return _textBuffer.getTextBuffer();
+    }
+
+    @Override
+    public char[] getStringCharacters() throws JacksonException
+    {
+        if (_currToken == null) { // null only before/after document
+            return null;
         }
-        return null;
+        TokenCharGetter getter = TOKEN_CHAR_GETTERS.get(_currToken);
+        if (getter != null) {
+            return getter.get(this);
+        }
+        return _currToken.asCharArray();
     }
 
     @Override

```
