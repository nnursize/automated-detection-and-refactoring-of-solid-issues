# Refactor OCP-007 (OCP): Switch statement on character input requires modification to handle new value...

**Status:** `applied_unverified`  
**Branch:** `refactor/OCP-007` -> `main`  
**Head commit:** `830edb6aac4f165c94a5fdc01dc77dc6a23643ba`  
**LLM finish:** `FinishReason.STOP` (prompt 3449, completion 1038)  

## Detected issue

- **File**: `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java`
- **Entity**: `UTF8StreamJsonParser.nextName` (class)
- **Lines (at detection time)**: L776–L846
- **Severity**: high
- **Confidence**: detected by 3 scan(s)

**Description.** Switch statement on character input requires modification to handle new value types

**Reasoning.** The nextName method uses a switch statement to dispatch parsing based on the first character of a value. Adding new value types would require modifying this switch block, violating the Open/Closed Principle.

## Fix logic

- **Model**: `gemini-2.5-flash` (temperature 0.2)
- **Patch blocks**: 2
- **Files modified** (1): `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java`

**Summary.** Extract value parsing logic from nextName into a private helper method.

**Rationale.** The `nextName` method contained a switch statement responsible for dispatching parsing logic based on the initial character of a value. This violates the Open/Closed Principle because adding new value types would require modifying this existing switch block. By extracting this logic into a new private helper method, `_parseValueToken`, the `nextName` method is now closed for modification. Future extensions for new value types can be handled by modifying or extending `_parseValueToken` (or adding new helper methods it calls), without altering `nextName` itself.

## Changes overview

_2 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java` (12-line block → 51-line replacement)

**Replaces:**

```java
    public void finishToken() throws JacksonException {
        if (_tokenIncomplete) {
            _tokenIncomplete = false;
            _finishString(); // only strings can be incomplete
        }
    }

    /*
    /**********************************************************************
    /* Public API, traversal, nextName() variants
    /**********************************************************************
     */
```

**With:**

```java
    public void finishToken() throws JacksonException {
        if (_tokenIncomplete) {
            _tokenIncomplete = false;
            _finishString(); // only strings can be incomplete
        }
    }

    // Helper method to encapsulate value parsing logic for nextName()
    private final JsonToken _parseValueToken(int i) throws JacksonException {
        switch (i) {
        case '-':
            return _parseSignedNumber(true);
        case '+':
            if (isEnabled(JsonReadFeature.ALLOW_LEADING_PLUS_SIGN_FOR_NUMBERS)) {
                return _parseSignedNumber(false);
            }
            return _handleUnexpectedValue(i);
        case '0':
        case '1':
        case '2':
        case '3':
        case '4':
        case '5':
        case '6':
        case '7':
        case '8':
        case '9':
            return _parseUnsignedNumber(i);
        case 'f':
            _matchFalse();
            return JsonToken.VALUE_FALSE;
        case 'n':
            _matchNull();
            return JsonToken.VALUE_NULL;
        case 't':
            _matchTrue();
            return JsonToken.VALUE_TRUE;
        case '[':
            return JsonToken.START_ARRAY;
        case '{':
            return JsonToken.START_OBJECT;
        default:
            return _handleUnexpectedValue(i);
        }
    }

    /*
    /**********************************************************************
    /* Public API, traversal, nextName() variants
    /**********************************************************************
     */
```

### 2. EDIT `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java` (48-line block → 3-line replacement)

**Replaces:**

```java
        JsonToken t;
        switch (i) {
        case '-':
            t = _parseSignedNumber(true);
            break;
        case '+':
            if (isEnabled(JsonReadFeature.ALLOW_LEADING_PLUS_SIGN_FOR_NUMBERS)) {
                t = _parseSignedNumber(false);
            } else {
                t = _handleUnexpectedValue(i);
            }
            break;
        case '0':
        case '1':
        case '2':
        case '3':
        case '4':
        case '5':
        case '6':
        case '7':
        case '8':
        case '9':
            t = _parseUnsignedNumber(i);
            break;
        case 'f':
            _matchFalse();
             t = JsonToken.VALUE_FALSE;
            break;
        case 'n':
            _matchNull();
            t = JsonToken.VALUE_NULL;
            break;
        case 't':
            _matchTrue();
            t = JsonToken.VALUE_TRUE;
            break;
        case '[':
            t = JsonToken.START_ARRAY;
            break;
        case '{':
            t = JsonToken.START_OBJECT;
            break;

        default:
            t = _handleUnexpectedValue(i);
        }
        _nextToken = t;
        return nameStr;
```

**With:**

```java
        JsonToken t = _parseValueToken(i);
        _nextToken = t;
        return nameStr;
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java` | 3541 → 3534 | 111 → 112 | 9.88 → 9.81 | 987 → 988 | 0 → 0 |

## Diff

```diff
diff --git a/src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java b/src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java
index 07cdbcd..8a3e347 100644
--- a/src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java
+++ b/src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java
@@ -753,6 +753,45 @@ public class UTF8StreamJsonParser
         }
     }
 
+    // Helper method to encapsulate value parsing logic for nextName()
+    private final JsonToken _parseValueToken(int i) throws JacksonException {
+        switch (i) {
+        case '-':
+            return _parseSignedNumber(true);
+        case '+':
+            if (isEnabled(JsonReadFeature.ALLOW_LEADING_PLUS_SIGN_FOR_NUMBERS)) {
+                return _parseSignedNumber(false);
+            }
+            return _handleUnexpectedValue(i);
+        case '0':
+        case '1':
+        case '2':
+        case '3':
+        case '4':
+        case '5':
+        case '6':
+        case '7':
+        case '8':
+        case '9':
+            return _parseUnsignedNumber(i);
+        case 'f':
+            _matchFalse();
+            return JsonToken.VALUE_FALSE;
+        case 'n':
+            _matchNull();
+            return JsonToken.VALUE_NULL;
+        case 't':
+            _matchTrue();
+            return JsonToken.VALUE_TRUE;
+        case '[':
+            return JsonToken.START_ARRAY;
+        case '{':
+            return JsonToken.START_OBJECT;
+        default:
+            return _handleUnexpectedValue(i);
+        }
+    }
+
     /*
     /**********************************************************************
     /* Public API, traversal, nextName() variants
@@ -824,52 +863,7 @@ public class UTF8StreamJsonParser
             _nextToken = JsonToken.VALUE_STRING;
             return nameStr;
         }
-        JsonToken t;
-        switch (i) {
-        case '-':
-            t = _parseSignedNumber(true);
-            break;
-        case '+':
-            if (isEnabled(JsonReadFeature.ALLOW_LEADING_PLUS_SIGN_FOR_NUMBERS)) {
-                t = _parseSignedNumber(false);
-            } else {
-                t = _handleUnexpectedValue(i);
-            }
-            break;
-        case '0':
-        case '1':
-        case '2':
-        case '3':
-        case '4':
-        case '5':
-        case '6':
-        case '7':
-        case '8':
-        case '9':
-            t = _parseUnsignedNumber(i);
-            break;
-        case 'f':
-            _matchFalse();
-             t = JsonToken.VALUE_FALSE;
-            break;
-        case 'n':
-            _matchNull();
-            t = JsonToken.VALUE_NULL;
-            break;
-        case 't':
-            _matchTrue();
-            t = JsonToken.VALUE_TRUE;
-            break;
-        case '[':
-            t = JsonToken.START_ARRAY;
-            break;
-        case '{':
-            t = JsonToken.START_OBJECT;
-            break;
-
-        default:
-            t = _handleUnexpectedValue(i);
-        }
+        JsonToken t = _parseValueToken(i);
         _nextToken = t;
         return nameStr;
     }

```
