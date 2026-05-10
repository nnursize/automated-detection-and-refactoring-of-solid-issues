# Refactor SRP-013 (SRP): FieldReference combines data representation with complex string parsing logic.

**Status:** `applied_unverified`  
**Branch:** `refactor/SRP-013` -> `main`  
**Head commit:** `c58cd163a1d9291fd2141008659d58fc19a62e21`  
**LLM finish:** `FinishReason.STOP` (prompt 4640, completion 2459)  

## Detected issue

- **File**: `logstash-core/src/main/java/org/logstash/FieldReference.java`
- **Entity**: `FieldReference` (class)
- **Lines (at detection time)**: L40–L250
- **Severity**: medium
- **Confidence**: detected by 1 scan(s)

**Description.** FieldReference combines data representation with complex string parsing logic.

**Reasoning.** Large Class smell -> SRP violation because it encapsulates both the identity of a field path (the data structure) and the complex logic required to parse that path from a string (StrictTokenizer). The parsing logic is a separate responsibility from the representation of the parsed result.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files created** (1): `logstash-core/src/main/java/org/logstash/FieldReferenceParser.java`

**Summary.** Extract FieldReference parsing logic into a dedicated FieldReferenceParser class

**Rationale.** The FieldReference class was violating the Single Responsibility Principle by handling both the data structure of a field reference and the complex string parsing logic. Moving the parsing logic to a separate class improves maintainability and adheres to SRP.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. CREATE `logstash-core/src/main/java/org/logstash/FieldReferenceParser.java` (117 line(s))

```java
/*
 * Licensed to Elasticsearch B.V. under one or more contributor
 * license agreements. See the NOTICE file distributed with
 * this work for additional information regarding copyright
 * ownership. Elasticsearch B.V. licenses this file to you under
 * the Apache License, Version 2.0 (the "License"); you may
 * not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *	http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */

package org.logstash;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;
import org.logstash.util.EscapeHandler;

public final class FieldReferenceParser {

    private static final String[] EMPTY_STRING_ARRAY = new String[0];

    public static FieldReference parse(final CharSequence reference, final EscapeHandler escapeHandler) {
        final List<String> path = tokenize(reference).stream()
                .map(escapeHandler::unescape)
                .collect(Collectors.toList());

        return fromTokens(path);
    }

    private static FieldReference fromTokens(final List<String> path) {
        final String key = path.remove(path.size() - 1);
        final boolean empty = path.isEmpty();
        if (empty && key.equals(Event.METADATA)) {
            return new FieldReference(EMPTY_STRING_ARRAY, key, FieldReference.META_PARENT);
        } else if (!empty && path.get(0).equals(Event.METADATA)) {
            return new FieldReference(
                    path.subList(1, path.size()).toArray(EMPTY_STRING_ARRAY), key, FieldReference.META_CHILD
            );
        } else {
            return new FieldReference(path.toArray(EMPTY_STRING_ARRAY), key, -1); // DATA_CHILD is -1
        }
    }

    private static List<String> tokenize(final CharSequence reference) {
        ArrayList<String> path = new ArrayList<>();
        final int length = reference.length();

        boolean potentiallyAmbiguousSyntaxDetected = false;
        boolean seenBracket = false;
        int depth = 0;
        int splitPoint = 0;
... (57 more line(s) truncated)
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `logstash-core/src/main/java/org/logstash/FieldReference.java` | 292 → - | 15 → - | 4.2 → - | 49 → - | 0 → - |
| `logstash-core/src/main/java/org/logstash/FieldReferenceParser.java` | - → 104 | - → 3 | - → 7.33 | - → 20 | - → 0 |

## Diff

```diff
diff --git a/logstash-core/src/main/java/org/logstash/FieldReferenceParser.java b/logstash-core/src/main/java/org/logstash/FieldReferenceParser.java
new file mode 100644
index 0000000..0000000
--- /dev/null
+++ b/logstash-core/src/main/java/org/logstash/FieldReferenceParser.java
@@ -0,0 +1,117 @@
+/*
+ * Licensed to Elasticsearch B.V. under one or more contributor
+ * license agreements. See the NOTICE file distributed with
+ * this work for additional information regarding copyright
+ * ownership. Elasticsearch B.V. licenses this file to you under
+ * the Apache License, Version 2.0 (the "License"); you may
+ * not use this file except in compliance with the License.
+ * You may obtain a copy of the License at
+ *
+ *	http://www.apache.org/licenses/LICENSE-2.0
+ *
+ * Unless required by applicable law or agreed to in writing,
+ * software distributed under the License is distributed on an
+ * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
+ * KIND, either express or implied.  See the License for the
+ * specific language governing permissions and limitations
+ * under the License.
+ */
+
+package org.logstash;
+
+import java.util.ArrayList;
+import java.util.List;
+import java.util.stream.Collectors;
+import org.logstash.util.EscapeHandler;
+
+public final class FieldReferenceParser {
+
+    private static final String[] EMPTY_STRING_ARRAY = new String[0];
+
+    public static FieldReference parse(final CharSequence reference, final EscapeHandler escapeHandler) {
+        final List<String> path = tokenize(reference).stream()
+                .map(escapeHandler::unescape)
+                .collect(Collectors.toList());
+
+        return fromTokens(path);
+    }
+
+    private static FieldReference fromTokens(final List<String> path) {
+        final String key = path.remove(path.size() - 1);
+        final boolean empty = path.isEmpty();
+        if (empty && key.equals(Event.METADATA)) {
+            return new FieldReference(EMPTY_STRING_ARRAY, key, FieldReference.META_PARENT);
+        } else if (!empty && path.get(0).equals(Event.METADATA)) {
+            return new FieldReference(
+                    path.subList(1, path.size()).toArray(EMPTY_STRING_ARRAY), key, FieldReference.META_CHILD
+            );
+        } else {
+            return new FieldReference(path.toArray(EMPTY_STRING_ARRAY), key, -1); // DATA_CHILD is -1
+        }
+    }
+
+    private static List<String> tokenize(final CharSequence reference) {
+        ArrayList<String> path = new ArrayList<>();
+        final int length = reference.length();
+
+        boolean potentiallyAmbiguousSyntaxDetected = false;
+        boolean seenBracket = false;
+        int depth = 0;
+        int splitPoint = 0;
+        char current = 0;
+        char previous = 0;
+        scan: for (int i = 0; i < length; i++) {
+            previous = current;
+            current = reference.charAt(i);
+            switch (current) {
+                case '[':
+                    seenBracket = true;
+                    if (splitPoint != i) {
+                        potentiallyAmbiguousSyntaxDetected = true;
+                        break scan;
+                    }
+                    depth++;
+                    splitPoint = i + 1;
+                    continue scan;
+                case ']':
+                    seenBracket = true;
+                    if (depth <= 0) {
+                        potentiallyAmbiguousSyntaxDetected = true;
+                        break scan;
+                    }
+                    if (splitPoint == i && previous != ']') {
+                        potentiallyAmbiguousSyntaxDetected = true;
+                        break scan;
+                    }
+                    if (splitPoint < i) {
+                        path.add(reference.subSequence(splitPoint, i).toString());
+                    }
+                    depth--;
+                    splitPoint = i + 1;
+                    continue scan;
+                default:
+                    if (seenBracket && previous == ']') {
+                        potentiallyAmbiguousSyntaxDetected = true;
+                        break scan;
+                    }
+                    continue scan;
+            }
+        }
+
+        if (!seenBracket) {
+            path.add(reference.toString());
+            return path;
+        } else if (depth > 0) {
+            potentiallyAmbiguousSyntaxDetected = true;
+        }
+
+        if (potentiallyAmbiguousSyntaxDetected) {
+            throw new FieldReference.IllegalSyntaxException(String.format("Invalid FieldReference: `%s`", reference.toString()));
+        }
+
+        path.trimToSize();
+        return path;
+    }
+
+    private FieldReferenceParser() {}
+}
\ No newline at end of file

```
