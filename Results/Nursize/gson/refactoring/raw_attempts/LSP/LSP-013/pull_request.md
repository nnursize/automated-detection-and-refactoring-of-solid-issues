# Refactor LSP-013 (LSP): The 'read' method for BitSet adapter accepts NUMBER or STRING tokens but thro...

**Status:** `applied_unverified`  
**Branch:** `refactor/LSP-013` -> `main`  
**Head commit:** `6a784c03dad4439d32b512048ede11a11c920f70`  
**LLM finish:** `FinishReason.STOP` (prompt 10035, completion 281)  

## Detected issue

- **File**: `gson/src/main/java/com/google/gson/internal/bind/TypeAdapters.java`
- **Entity**: `TypeAdapters.BIT_SET.read` (method)
- **Lines (at detection time)**: L71–L96
- **Severity**: medium
- **Confidence**: detected by 3 scan(s)

**Description.** The 'read' method for BitSet adapter accepts NUMBER or STRING tokens but throws JsonSyntaxException for values other than 0 or 1, narrowing accepted input.

**Reasoning.** The `BitSet` `TypeAdapter`'s `read` method uses `in.nextInt()` or `in.nextString()` to read JSON tokens that are of type `NUMBER` or `STRING`. It then imposes an additional constraint, requiring these numeric or string values to be either `0` or `1`. If any other numeric or string value is encountered, it throws a `JsonSyntaxException`. While a `TypeAdapter`'s role is to convert, this behavior narrows the acceptable range of values for what `JsonReader` reports as `NUMBER` or `STRING`. A generic `TypeAdapter<Collection<Boolean>>` (conceptually similar) would likely accept any valid number or string and convert it, whereas this specialized adapter rejects valid input for its underlying primitive types, violating substitutability for a broader `Number` or `String` type adapter.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `gson/src/main/java/com/google/gson/internal/bind/TypeAdapters.java`

**Summary.** Relax BitSet deserialization to accept any non-zero value as true

**Rationale.** The BitSet adapter previously strictly enforced 0 or 1, which is overly restrictive for a general-purpose type adapter. By treating any non-zero value as true (consistent with common programming conventions for boolean-like integers), we improve substitutability and robustness without breaking existing valid 0/1 inputs.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `gson/src/main/java/com/google/gson/internal/bind/TypeAdapters.java` (12-line block → 2-line replacement)

**Replaces:**

```java
                int intValue = in.nextInt();
                if (intValue == 0) {
                  set = false;
                } else if (intValue == 1) {
                  set = true;
                } else {
                  throw new JsonSyntaxException(
                      "Invalid bitset value "
                          + intValue
                          + ", expected 0 or 1; at path "
                          + in.getPreviousPath());
                }
```

**With:**

```java
                int intValue = in.nextInt();
                set = intValue != 0;
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `gson/src/main/java/com/google/gson/internal/bind/TypeAdapters.java` | 861 → 851 | 73 → 73 | 2.08 → 2.05 | 80 → 78 | 0 → 0 |

## Diff

```diff
diff --git a/gson/src/main/java/com/google/gson/internal/bind/TypeAdapters.java b/gson/src/main/java/com/google/gson/internal/bind/TypeAdapters.java
index 605afdb..93ddc40 100644
--- a/gson/src/main/java/com/google/gson/internal/bind/TypeAdapters.java
+++ b/gson/src/main/java/com/google/gson/internal/bind/TypeAdapters.java
@@ -100,17 +100,7 @@ public final class TypeAdapters {
               case NUMBER:
               case STRING:
                 int intValue = in.nextInt();
-                if (intValue == 0) {
-                  set = false;
-                } else if (intValue == 1) {
-                  set = true;
-                } else {
-                  throw new JsonSyntaxException(
-                      "Invalid bitset value "
-                          + intValue
-                          + ", expected 0 or 1; at path "
-                          + in.getPreviousPath());
-                }
+                set = intValue != 0;
                 break;
               case BOOLEAN:
                 set = in.nextBoolean();

```
