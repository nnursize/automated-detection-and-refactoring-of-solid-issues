# Refactor SRP-017 (SRP): Compiler class mixed with runtime dataset implementations.

**Status:** `applied_unverified`  
**Branch:** `refactor/SRP-017` -> `main`  
**Head commit:** `798764c82165d1a5dbd2a56e7f990faf0c269341`  
**LLM finish:** `FinishReason.STOP` (prompt 7427, completion 2241)  

## Detected issue

- **File**: `logstash-core/src/main/java/org/logstash/config/ir/compiler/DatasetCompiler.java`
- **Entity**: `DatasetCompiler` (class)
- **Lines (at detection time)**: L41–L574
- **Severity**: medium
- **Confidence**: detected by 1 scan(s)

**Description.** Compiler class mixed with runtime dataset implementations.

**Reasoning.** The class contains the logic to compile datasets but also defines internal runtime structures like 'Complement' (L486) and 'ComputeAndClear' (L547). The logic for generating/compiling execution code should be separated from the operational behavior of the resulting dataset objects.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 5
- **Files created** (2): `logstash-core/src/main/java/org/logstash/config/ir/compiler/Complement.java`, `logstash-core/src/main/java/org/logstash/config/ir/compiler/ComputeAndClear.java`
- **Files modified** (1): `logstash-core/src/main/java/org/logstash/config/ir/compiler/DatasetCompiler.java`

**Summary.** Extract DatasetCompiler internal classes to separate files

**Rationale.** The DatasetCompiler class was violating SRP by containing runtime dataset implementations (Complement) and internal helper structures (ComputeAndClear). Moving these to their own files improves maintainability and separation of concerns.

## Changes overview

_5 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `logstash-core/src/main/java/org/logstash/config/ir/compiler/DatasetCompiler.java` (17-line block → 17-line replacement)

**Replaces:**

```java
        final ValueSyntaxElement right = fields.add(DatasetCompiler.Complement.class);
        final VariableDefinition event =
            new VariableDefinition(JrubyEventExtLibrary.RubyEvent.class, "event");
        fields.addAfterInit(
            Closure.wrap(
                SyntaxFactory.assignment(
                    right,
                    SyntaxFactory.cast(
                        DatasetCompiler.Complement.class, SyntaxFactory.constant(
                            DatasetCompiler.class, DatasetCompiler.Complement.class.getSimpleName()
                        ).call("from", SyntaxFactory.identifier("this"), elseData)
                    )
                )
            )
        );
        final ValueSyntaxElement conditionField = fields.add("condition", condition);
        final DatasetCompiler.ComputeAndClear compute;
```

**With:**

```java
        final ValueSyntaxElement right = fields.add(Complement.class);
        final VariableDefinition event =
            new VariableDefinition(JrubyEventExtLibrary.RubyEvent.class, "event");
        fields.addAfterInit(
            Closure.wrap(
                SyntaxFactory.assignment(
                    right,
                    SyntaxFactory.cast(
                        Complement.class, SyntaxFactory.constant(
                            Complement.class, Complement.class.getSimpleName()
                        ).call("from", SyntaxFactory.identifier("this"), elseData)
                    )
                )
            )
        );
        final ValueSyntaxElement conditionField = fields.add("condition", condition);
        final ComputeAndClear compute;
```

### 2. EDIT `logstash-core/src/main/java/org/logstash/config/ir/compiler/DatasetCompiler.java` (19-line block → 19-line replacement)

**Replaces:**

```java
    private static DatasetCompiler.ComputeAndClear withOutputBuffering(final Closure compute,
        final Closure clear, final ValueSyntaxElement outputBuffer, final ClassFields fields) {
        final SyntaxFactory.MethodCallReturnValue done = new SyntaxFactory.MethodCallReturnValue(SyntaxFactory.value("this"), "isDone");
        return computeAndClear(
            Closure.wrap(
                SyntaxFactory.ifCondition(done, Closure.wrap(SyntaxFactory.ret(outputBuffer)))
            ).add(compute)
                .add(new SyntaxFactory.MethodCallReturnValue(SyntaxFactory.value("this"), "setDone"))
                .add(SyntaxFactory.ret(outputBuffer)),
            Closure.wrap(
                SyntaxFactory.ifCondition(
                    done, Closure.wrap(
                        clear.add(clear(outputBuffer)),
                        new SyntaxFactory.MethodCallReturnValue(SyntaxFactory.value("this"), "clearDone")
                    )
                )
            ), fields
        );
    }
```

**With:**

```java
    private static ComputeAndClear withOutputBuffering(final Closure compute,
        final Closure clear, final ValueSyntaxElement outputBuffer, final ClassFields fields) {
        final SyntaxFactory.MethodCallReturnValue done = new SyntaxFactory.MethodCallReturnValue(SyntaxFactory.value("this"), "isDone");
        return computeAndClear(
            Closure.wrap(
                SyntaxFactory.ifCondition(done, Closure.wrap(SyntaxFactory.ret(outputBuffer)))
            ).add(compute)
                .add(new SyntaxFactory.MethodCallReturnValue(SyntaxFactory.value("this"), "setDone"))
                .add(SyntaxFactory.ret(outputBuffer)),
            Closure.wrap(
                SyntaxFactory.ifCondition(
                    done, Closure.wrap(
                        clear.add(clear(outputBuffer)),
                        new SyntaxFactory.MethodCallReturnValue(SyntaxFactory.value("this"), "clearDone")
                    )
                )
            ), fields
        );
    }
```

### 3. EDIT `logstash-core/src/main/java/org/logstash/config/ir/compiler/DatasetCompiler.java` (94-line block → 5-line replacement)

**Replaces:**

```java
    private static DatasetCompiler.ComputeAndClear computeAndClear(final Closure compute, final Closure clear,
        final ClassFields fields) {
        return new DatasetCompiler.ComputeAndClear(compute, clear, fields);
    }

    /**
     * Complementary {@link Dataset} to a {@link SplitDataset} representing the
     * negative branch of the {@code if} statement.
     */
    public static final class Complement implements Dataset {

        /**
         * Positive branch of underlying {@code if} statement.
         */
        private final Dataset parent;

        /**
         * This collection is shared with {@link DatasetCompiler.Complement#parent} and
         * mutated when calling its {@code compute} method. This class does not directly compute
         * it.
         */
        private final Collection<JrubyEventExtLibrary.RubyEvent> data;

        private boolean done;

        public static Dataset from(final Dataset parent,
            final Collection<JrubyEventExtLibrary.RubyEvent> complement) {
            return new DatasetCompiler.Complement(parent, complement);
        }

        /**
         * Ctor.
         * @param left Positive Branch {@link SplitDataset}
         * @param complement Collection of {@link JrubyEventExtLibrary.RubyEvent}s that did
         * not match {@code left}
         */
        private Complement(
            final Dataset left, final Collection<JrubyEventExtLibrary.RubyEvent> complement) {
            this.parent = left;
            data = complement;
        }

        @Override
        public Collection<JrubyEventExtLibrary.RubyEvent> compute(@SuppressWarnings("rawtypes") final RubyArray batch,
                                                                  final boolean flush, final boolean shutdown) {
            if (done) {
                return data;
            }
            parent.compute(batch, flush, shutdown);
            done = true;
            return data;
        }

        @Override
        public void clear() {
            if (done) {
                parent.clear();
                done = false;
            }
        }
... (34 more line(s) truncated)
```

**With:**

```java
    private static ComputeAndClear computeAndClear(final Closure compute, final Closure clear,
        final ClassFields fields) {
        return new ComputeAndClear(compute, clear, fields);
    }
}
```

### 4. CREATE `logstash-core/src/main/java/org/logstash/config/ir/compiler/Complement.java` (39 line(s))

```java
package org.logstash.config.ir.compiler;

import java.util.Collection;
import org.jruby.RubyArray;
import org.logstash.ext.JrubyEventExtLibrary;

public final class Complement implements Dataset {
    private final Dataset parent;
    private final Collection<JrubyEventExtLibrary.RubyEvent> data;
    private boolean done;

    public static Dataset from(final Dataset parent, final Collection<JrubyEventExtLibrary.RubyEvent> complement) {
        return new Complement(parent, complement);
    }

    private Complement(final Dataset left, final Collection<JrubyEventExtLibrary.RubyEvent> complement) {
        this.parent = left;
        this.data = complement;
    }

    @Override
    public Collection<JrubyEventExtLibrary.RubyEvent> compute(@SuppressWarnings("rawtypes") final RubyArray batch,
                                                              final boolean flush, final boolean shutdown) {
        if (done) {
            return data;
        }
        parent.compute(batch, flush, shutdown);
        done = true;
        return data;
    }

    @Override
    public void clear() {
        if (done) {
            parent.clear();
            done = false;
        }
    }
}
```

### 5. CREATE `logstash-core/src/main/java/org/logstash/config/ir/compiler/ComputeAndClear.java` (25 line(s))

```java
package org.logstash.config.ir.compiler;

public final class ComputeAndClear {
    private final MethodSyntaxElement compute;
    private final MethodSyntaxElement clear;
    private final ClassFields fields;

    public ComputeAndClear(final Closure compute, final Closure clear, final ClassFields fields) {
        this.compute = MethodSyntaxElement.compute(compute);
        this.clear = MethodSyntaxElement.clear(clear);
        this.fields = fields;
    }

    public MethodSyntaxElement compute() {
        return compute;
    }

    public MethodSyntaxElement clear() {
        return clear;
    }

    public ClassFields fields() {
        return fields;
    }
}
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `logstash-core/src/main/java/org/logstash/config/ir/compiler/Complement.java` | - → 33 | - → 2 | - → 2 | - → 3 | - → 0 |
| `logstash-core/src/main/java/org/logstash/config/ir/compiler/ComputeAndClear.java` | - → 20 | - → 3 | - → 1 | - → 1 | - → 0 |
| `logstash-core/src/main/java/org/logstash/config/ir/compiler/DatasetCompiler.java` | 504 → 431 | 27 → 24 | 2.33 → 2.29 | 37 → 32 | 0 → 0 |

## Diff

```diff
diff --git a/logstash-core/src/main/java/org/logstash/config/ir/compiler/DatasetCompiler.java b/logstash-core/src/main/java/org/logstash/config/ir/compiler/DatasetCompiler.java
index cd21019..4a2cecb 100644
--- a/logstash-core/src/main/java/org/logstash/config/ir/compiler/DatasetCompiler.java
+++ b/logstash-core/src/main/java/org/logstash/config/ir/compiler/DatasetCompiler.java
@@ -63,7 +63,7 @@ public final class DatasetCompiler {
         final ClassFields fields = new ClassFields();
         final ValueSyntaxElement ifData = fields.add("ifData", new ArrayList<>());
         final ValueSyntaxElement elseData = fields.add("elseData", new ArrayList<>());
-        final ValueSyntaxElement right = fields.add(DatasetCompiler.Complement.class);
+        final ValueSyntaxElement right = fields.add(Complement.class);
         final VariableDefinition event =
             new VariableDefinition(JrubyEventExtLibrary.RubyEvent.class, "event");
         fields.addAfterInit(
@@ -71,15 +71,15 @@ public final class DatasetCompiler {
                 SyntaxFactory.assignment(
                     right,
                     SyntaxFactory.cast(
-                        DatasetCompiler.Complement.class, SyntaxFactory.constant(
-                            DatasetCompiler.class, DatasetCompiler.Complement.class.getSimpleName()
+                        Complement.class, SyntaxFactory.constant(
+                            Complement.class, Complement.class.getSimpleName()
                         ).call("from", SyntaxFactory.identifier("this"), elseData)
                     )
                 )
             )
         );
         final ValueSyntaxElement conditionField = fields.add("condition", condition);
-        final DatasetCompiler.ComputeAndClear compute;
+        final ComputeAndClear compute;
 
         final ValueSyntaxElement errorNotifier = fields.add(conditionalErrListener);
         Closure exceptionHandlerBlock = Closure.wrap(
@@ -385,7 +385,7 @@ public final class DatasetCompiler {
      * @param fields Class fields
      * @return ComputeAndClear with adjusted methods and {@code done} flag added to fields
      */
-    private static DatasetCompiler.ComputeAndClear withOutputBuffering(final Closure compute,
+    private static ComputeAndClear withOutputBuffering(final Closure compute,
         final Closure clear, final ValueSyntaxElement outputBuffer, final ClassFields fields) {
         final SyntaxFactory.MethodCallReturnValue done = new SyntaxFactory.MethodCallReturnValue(SyntaxFactory.value("this"), "isDone");
         return computeAndClear(
@@ -474,97 +474,8 @@ public final class DatasetCompiler {
         );
     }
 
-    private static DatasetCompiler.ComputeAndClear computeAndClear(final Closure compute, final Closure clear,
+    private static ComputeAndClear computeAndClear(final Closure compute, final Closure clear,
         final ClassFields fields) {
-        return new DatasetCompiler.ComputeAndClear(compute, clear, fields);
-    }
-
-    /**
-     * Complementary {@link Dataset} to a {@link SplitDataset} representing the
-     * negative branch of the {@code if} statement.
-     */
-    public static final class Complement implements Dataset {
-
-        /**
-         * Positive branch of underlying {@code if} statement.
-         */
-        private final Dataset parent;
-
-        /**
-         * This collection is shared with {@link DatasetCompiler.Complement#parent} and
-         * mutated when calling its {@code compute} method. This class does not directly compute
-         * it.
-         */
-        private final Collection<JrubyEventExtLibrary.RubyEvent> data;
-
-        private boolean done;
-
-        public static Dataset from(final Dataset parent,
-            final Collection<JrubyEventExtLibrary.RubyEvent> complement) {
-            return new DatasetCompiler.Complement(parent, complement);
-        }
-
-        /**
-         * Ctor.
-         * @param left Positive Branch {@link SplitDataset}
-         * @param complement Collection of {@link JrubyEventExtLibrary.RubyEvent}s that did
-         * not match {@code left}
-         */
-        private Complement(
-            final Dataset left, final Collection<JrubyEventExtLibrary.RubyEvent> complement) {
-            this.parent = left;
-            data = complement;
-        }
-
-        @Override
-        public Collection<JrubyEventExtLibrary.RubyEvent> compute(@SuppressWarnings("rawtypes") final RubyArray batch,
-                                                                  final boolean flush, final boolean shutdown) {
-            if (done) {
-                return data;
-            }
-            parent.compute(batch, flush, shutdown);
-            done = true;
-            return data;
-        }
-
-        @Override
-        public void clear() {
-            if (done) {
-                parent.clear();
-                done = false;
-            }
-        }
-    }
-
-    /**
-     * Represents the 3-tuple of {@code compute} method, {@code clear} method and
-     * {@link ClassFields} used by both methods.
-     */
-    private static final class ComputeAndClear {
-
-        private final MethodSyntaxElement compute;
-
-        private final MethodSyntaxElement clear;
-
-        private final ClassFields fields;
-
-        private ComputeAndClear(final Closure compute, final Closure clear,
-            final ClassFields fields) {
-            this.compute = MethodSyntaxElement.compute(compute);
-            this.clear = MethodSyntaxElement.clear(clear);
-            this.fields = fields;
-        }
-
-        public MethodSyntaxElement compute() {
-            return compute;
-        }
-
-        public MethodSyntaxElement clear() {
-            return clear;
-        }
-
-        public ClassFields fields() {
-            return fields;
-        }
+        return new ComputeAndClear(compute, clear, fields);
     }
 }
diff --git a/logstash-core/src/main/java/org/logstash/config/ir/compiler/Complement.java b/logstash-core/src/main/java/org/logstash/config/ir/compiler/Complement.java
new file mode 100644
index 0000000..0000000
--- /dev/null
+++ b/logstash-core/src/main/java/org/logstash/config/ir/compiler/Complement.java
@@ -0,0 +1,39 @@
+package org.logstash.config.ir.compiler;
+
+import java.util.Collection;
+import org.jruby.RubyArray;
+import org.logstash.ext.JrubyEventExtLibrary;
+
+public final class Complement implements Dataset {
+    private final Dataset parent;
+    private final Collection<JrubyEventExtLibrary.RubyEvent> data;
+    private boolean done;
+
+    public static Dataset from(final Dataset parent, final Collection<JrubyEventExtLibrary.RubyEvent> complement) {
+        return new Complement(parent, complement);
+    }
+
+    private Complement(final Dataset left, final Collection<JrubyEventExtLibrary.RubyEvent> complement) {
+        this.parent = left;
+        this.data = complement;
+    }
+
+    @Override
+    public Collection<JrubyEventExtLibrary.RubyEvent> compute(@SuppressWarnings("rawtypes") final RubyArray batch,
+                                                              final boolean flush, final boolean shutdown) {
+        if (done) {
+            return data;
+        }
+        parent.compute(batch, flush, shutdown);
+        done = true;
+        return data;
+    }
+
+    @Override
+    public void clear() {
+        if (done) {
+            parent.clear();
+            done = false;
+        }
+    }
+}
\ No newline at end of file
diff --git a/logstash-core/src/main/java/org/logstash/config/ir/compiler/ComputeAndClear.java b/logstash-core/src/main/java/org/logstash/config/ir/compiler/ComputeAndClear.java
new file mode 100644
index 0000000..0000000
--- /dev/null
+++ b/logstash-core/src/main/java/org/logstash/config/ir/compiler/ComputeAndClear.java
@@ -0,0 +1,25 @@
+package org.logstash.config.ir.compiler;
+
+public final class ComputeAndClear {
+    private final MethodSyntaxElement compute;
+    private final MethodSyntaxElement clear;
+    private final ClassFields fields;
+
+    public ComputeAndClear(final Closure compute, final Closure clear, final ClassFields fields) {
+        this.compute = MethodSyntaxElement.compute(compute);
+        this.clear = MethodSyntaxElement.clear(clear);
+        this.fields = fields;
+    }
+
+    public MethodSyntaxElement compute() {
+        return compute;
+    }
+
+    public MethodSyntaxElement clear() {
+        return clear;
+    }
+
+    public ClassFields fields() {
+        return fields;
+    }
+}
\ No newline at end of file

```
