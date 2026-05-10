# Refactor OCP-002 (OCP): Extensive if-else if and switch statements for parsing logic violate OCP.

**Status:** `applied_unverified`  
**Branch:** `refactor/OCP-002` -> `main`  
**Head commit:** `d86482803f3f6a4fdd6cbb0bbd0e240415001d3a`  
**LLM finish:** `FinishReason.STOP` (prompt 5857, completion 605)  

## Detected issue

- **File**: `gson/src/main/java/com/google/gson/stream/JsonReader.java`
- **Entity**: `JsonReader.doPeek` (method)
- **Lines (at detection time)**: L298–L401
- **Severity**: high
- **Confidence**: detected by 5 scan(s)

**Description.** Extensive if-else if and switch statements for parsing logic violate OCP.

**Reasoning.** The `doPeek()` method contains multiple `if-else if` and `switch` statements that handle different `JsonScope` states and character parsing rules. Any addition of new JSON structures, parsing rules, or token types would necessitate modifying this method, making it closed for extension without modification.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files created** (1): `gson/src/main/java/com/google/gson/stream/PeekStrategy.java`

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. CREATE `gson/src/main/java/com/google/gson/stream/PeekStrategy.java` (7 line(s))

```java
package com.google.gson.stream;

import java.io.IOException;

interface PeekStrategy {
    int peek(JsonReader reader) throws IOException;
}
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `gson/src/main/java/com/google/gson/stream/JsonReader.java` | 1708 → - | 44 → - | 10.64 → - | 425 → - | 0 → - |
| `gson/src/main/java/com/google/gson/stream/PeekStrategy.java` | - → 5 | - → 0 | - → 1 | - → 1 | - → 0 |

## Diff

```diff
diff --git a/gson/src/main/java/com/google/gson/stream/PeekStrategy.java b/gson/src/main/java/com/google/gson/stream/PeekStrategy.java
new file mode 100644
index 0000000..0000000
--- /dev/null
+++ b/gson/src/main/java/com/google/gson/stream/PeekStrategy.java
@@ -0,0 +1,7 @@
+package com.google.gson.stream;
+
+import java.io.IOException;
+
+interface PeekStrategy {
+    int peek(JsonReader reader) throws IOException;
+}
\ No newline at end of file

```
