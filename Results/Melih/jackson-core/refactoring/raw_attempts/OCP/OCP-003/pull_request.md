# Refactor OCP-003 (OCP): Switch statement on token ID requires modification to handle new token types

**Status:** `applied_unverified`  
**Branch:** `refactor/OCP-003` -> `main`  
**Head commit:** `c445684d3c509e85f30ab38aa81d30048b3bda64`  
**LLM finish:** `FinishReason.STOP` (prompt 3702, completion 971)  

## Detected issue

- **File**: `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java`
- **Entity**: `UTF8StreamJsonParser.getStringLength` (class)
- **Lines (at detection time)**: L379–L398
- **Severity**: medium
- **Confidence**: detected by 3 scan(s)

**Description.** Switch statement on token ID requires modification to handle new token types

**Reasoning.** The getStringLength method uses a switch statement based on token IDs. Adding new token types would require modifying this switch block, violating the Open/Closed Principle.

## Fix logic

- **Model**: `gemini-2.5-flash` (temperature 0.2)
- **Patch blocks**: 3
- **Files modified** (1): `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java`

**Summary.** Refactor getStringLength to use a map-based strategy, adhering to OCP.

**Rationale.** The original getStringLength method used a switch statement on JsonToken IDs, which violates the Open/Closed Principle as new token types would require modifying the method. This refactoring introduces a TokenLengthGetter functional interface and a static map (TOKEN_LENGTH_GETTERS) to associate JsonTokens with their respective length calculation logic. This allows for extension (adding new token types and their length logic) without modifying the core getStringLength method, thus adhering to OCP. A new helper method, getTextBufferSize, is also introduced for consistency and to avoid code duplication in lambdas.

## Changes overview

_3 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java` (2-line block → 24-line replacement)

**Replaces:**

```java
        return _currToken.asCharArray();
    }
```

**With:**

```java
        return _currToken.asCharArray();
    }

    // --- OCP Refactoring for getStringLength ---
    @FunctionalInterface
    private interface TokenLengthGetter {
        int get(UTF8StreamJsonParser parser) throws JacksonException;
    }

    private static final java.util.Map<tools.jackson.core.JsonToken, TokenLengthGetter> TOKEN_LENGTH_GETTERS;

    static {
        TOKEN_LENGTH_GETTERS = new java.util.EnumMap<>(tools.jackson.core.JsonToken.class);
        TOKEN_LENGTH_GETTERS.put(tools.jackson.core.JsonToken.PROPERTY_NAME, parser -> parser._streamReadContext.currentName().length());
        TOKEN_LENGTH_GETTERS.put(tools.jackson.core.JsonToken.VALUE_STRING, parser -> {
            if (parser._tokenIncomplete) {
                parser._tokenIncomplete = false;
                parser._finishString();
            }
            return parser.getTextBufferSize();
        });
        TOKEN_LENGTH_GETTERS.put(tools.jackson.core.JsonToken.VALUE_NUMBER_INT, UTF8StreamJsonParser::getTextBufferSize);
        TOKEN_LENGTH_GETTERS.put(tools.jackson.core.JsonToken.VALUE_NUMBER_FLOAT, UTF8StreamJsonParser::getTextBufferSize);
    }
```

### 2. EDIT `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java` (4-line block → 9-line replacement)

**Replaces:**

```java
    // Helper method to avoid repeating _textBuffer.getTextBuffer() in lambda
    private char[] getTextBufferContents() {
        return _textBuffer.getTextBuffer();
    }
```

**With:**

```java
    // Helper method to avoid repeating _textBuffer.getTextBuffer() in lambda
    private char[] getTextBufferContents() {
        return _textBuffer.getTextBuffer();
    }

    // Helper method to avoid repeating _textBuffer.size() in lambda
    private int getTextBufferSize() {
        return _textBuffer.size();
    }
```

### 3. EDIT `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java` (24-line block → 12-line replacement)

**Replaces:**

```java
    @Override
    public int getStringLength() throws JacksonException
    {
        if (_currToken != null) { // null only before/after document
            switch (_currToken.id()) {

            case ID_PROPERTY_NAME:
                return _streamReadContext.currentName().length();
            case ID_STRING:
                if (_tokenIncomplete) {
                    _tokenIncomplete = false;
                    _finishString(); // only strings can be incomplete
                }
                // fall through
            case ID_NUMBER_INT:
            case ID_NUMBER_FLOAT:
                return _textBuffer.size();

            default:
                return _currToken.asCharArray().length;
            }
        }
        return 0;
    }
```

**With:**

```java
    @Override
    public int getStringLength() throws JacksonException
    {
        if (_currToken == null) { // null only before/after document
            return 0;
        }
        TokenLengthGetter getter = TOKEN_LENGTH_GETTERS.get(_currToken);
        if (getter != null) {
            return getter.get(this);
        }
        return _currToken.asCharArray().length;
    }
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java` | 3546 → 3558 | 113 → 114 | 9.72 → 9.62 | 986 → 984 | 0 → 0 |

## Diff

```diff
diff --git a/src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java b/src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java
index 39108fe..a1c1f9c 100644
--- a/src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java
+++ b/src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java
@@ -449,6 +449,11 @@ public class UTF8StreamJsonParser
         return _textBuffer.getTextBuffer();
     }
 
+    // Helper method to avoid repeating _textBuffer.size() in lambda
+    private int getTextBufferSize() {
+        return _textBuffer.size();
+    }
+
     @Override
     public char[] getStringCharacters() throws JacksonException
     {
@@ -462,29 +467,39 @@ public class UTF8StreamJsonParser
         return _currToken.asCharArray();
     }
 
-    @Override
-    public int getStringLength() throws JacksonException
-    {
-        if (_currToken != null) { // null only before/after document
-            switch (_currToken.id()) {
+    // --- OCP Refactoring for getStringLength ---
+    @FunctionalInterface
+    private interface TokenLengthGetter {
+        int get(UTF8StreamJsonParser parser) throws JacksonException;
+    }
 
-            case ID_PROPERTY_NAME:
-                return _streamReadContext.currentName().length();
-            case ID_STRING:
-                if (_tokenIncomplete) {
-                    _tokenIncomplete = false;
-                    _finishString(); // only strings can be incomplete
-                }
-                // fall through
-            case ID_NUMBER_INT:
-            case ID_NUMBER_FLOAT:
-                return _textBuffer.size();
+    private static final java.util.Map<tools.jackson.core.JsonToken, TokenLengthGetter> TOKEN_LENGTH_GETTERS;
 
-            default:
-                return _currToken.asCharArray().length;
+    static {
+        TOKEN_LENGTH_GETTERS = new java.util.EnumMap<>(tools.jackson.core.JsonToken.class);
+        TOKEN_LENGTH_GETTERS.put(tools.jackson.core.JsonToken.PROPERTY_NAME, parser -> parser._streamReadContext.currentName().length());
+        TOKEN_LENGTH_GETTERS.put(tools.jackson.core.JsonToken.VALUE_STRING, parser -> {
+            if (parser._tokenIncomplete) {
+                parser._tokenIncomplete = false;
+                parser._finishString();
             }
+            return parser.getTextBufferSize();
+        });
+        TOKEN_LENGTH_GETTERS.put(tools.jackson.core.JsonToken.VALUE_NUMBER_INT, UTF8StreamJsonParser::getTextBufferSize);
+        TOKEN_LENGTH_GETTERS.put(tools.jackson.core.JsonToken.VALUE_NUMBER_FLOAT, UTF8StreamJsonParser::getTextBufferSize);
+    }
+
+    @Override
+    public int getStringLength() throws JacksonException
+    {
+        if (_currToken == null) { // null only before/after document
+            return 0;
         }
-        return 0;
+        TokenLengthGetter getter = TOKEN_LENGTH_GETTERS.get(_currToken);
+        if (getter != null) {
+            return getter.get(this);
+        }
+        return _currToken.asCharArray().length;
     }
 
     @Override

```
