# Refactor DIP-012 (DIP): The Compiler class is responsible for instantiating various concrete EventCon...

**Status:** `applied_unverified`  
**Branch:** `refactor/DIP-012` -> `main`  
**Head commit:** `da101acd4e72813575d0b2ff5ca8d93280a63d71`  
**LLM finish:** `FinishReason.STOP` (prompt 8849, completion 2669)  

## Detected issue

- **File**: `logstash-core/src/main/java/org/logstash/config/ir/compiler/EventCondition.java`
- **Entity**: `Compiler` (class)
- **Lines (at detection time)**: L82–L721
- **Severity**: high
- **Confidence**: detected by 1 scan(s)

**Description.** The Compiler class is responsible for instantiating various concrete EventCondition implementations.

**Reasoning.** The Compiler class directly creates concrete instances of EventCondition subclasses (e.g., FieldMatches, ConstantMatches). This creates a dependency on concrete implementations for every condition type. A factory pattern or dependency injection should be used to decouple the compiler from specific condition logic.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 6
- **Files created** (1): `logstash-core/src/main/java/org/logstash/config/ir/compiler/ConditionFactory.java`
- **Files modified** (1): `logstash-core/src/main/java/org/logstash/config/ir/compiler/EventCondition.java`

**Summary.** Introduce ConditionFactory to decouple Compiler from concrete EventCondition implementations

**Rationale.** The Compiler class was directly instantiating concrete EventCondition implementations (e.g., FieldMatches, FieldInField). By introducing a ConditionFactory, we move the instantiation logic out of the Compiler, adhering to the Dependency Inversion Principle and improving maintainability.

## Changes overview

_6 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `logstash-core/src/main/java/org/logstash/config/ir/compiler/EventCondition.java` (19-line block → 20-line replacement)

**Replaces:**

```java
        private static EventCondition regex(final RegexEq regex) {
            final EventCondition condition;
            final Expression uleft = regex.getLeft();
            final Expression uright = regex.getRight();
            if (eAndV(regex)) {
                condition = new EventCondition.Compiler.FieldMatches(
                        ((EventValueExpression) uleft).getFieldName(),
                        ((ValueExpression) uright).get().toString()
                );
            } else if (vAndR(regex)) {
                condition = new EventCondition.Compiler.ConstantMatches(
                        ((ValueExpression) uleft).get(),
                        ((RegexValueExpression) uright).get().toString()
                );
            } else {
                throw new EventCondition.Compiler.UnexpectedTypeException(uleft, uright);
            }
            return condition;
        }
```

**With:**

```java
        private static EventCondition regex(final RegexEq regex) {
            final EventCondition condition;
            final Expression uleft = regex.getLeft();
            final Expression uright = regex.getRight();
            final ConditionFactory factory = new DefaultConditionFactory();
            if (eAndV(regex)) {
                condition = factory.createFieldMatches(
                        ((EventValueExpression) uleft).getFieldName(),
                        ((ValueExpression) uright).get().toString()
                );
            } else if (vAndR(regex)) {
                condition = factory.createConstantMatches(
                        ((ValueExpression) uleft).get(),
                        ((RegexValueExpression) uright).get().toString()
                );
            } else {
                throw new EventCondition.Compiler.UnexpectedTypeException(uleft, uright);
            }
            return condition;
        }
```

### 2. EDIT `logstash-core/src/main/java/org/logstash/config/ir/compiler/EventCondition.java` (39-line block → 34-line replacement)

**Replaces:**

```java
        private static EventCondition in(final In in) {
            final Expression left = in.getLeft();
            final Expression right = in.getRight();
            final EventCondition condition;
            if (eAndV(in) && isScalar((ValueExpression) in.getRight())) {
                condition = new EventCondition.Compiler.FieldInConstantScalar(
                        FieldReference.from(((EventValueExpression) left).getFieldName()),
                        ((ValueExpression) right).get().toString()
                );
            } else if (vAndE(in) && isScalar((ValueExpression) in.getLeft())) {
                final Object leftv = ((ValueExpression) left).get();
                final FieldReference rfield =
                        FieldReference.from(((EventValueExpression) right).getFieldName());
                if (leftv instanceof String) {
                    condition = new EventCondition.Compiler.ConstantStringInField(
                            rfield, (String) leftv
                    );
                } else {
                    condition = new EventCondition.Compiler.ConstantScalarInField(rfield, leftv);
                }
            } else if (eAndV(in) && listValueRight(in)) {
                condition = in(
                        (EventValueExpression) left, (List<?>) ((ValueExpression) right).get()
                );
            } else if (eAndE(in)) {
                condition = in((EventValueExpression) left, (EventValueExpression) right);
            } else if (vAndV(in)) {
                condition = in((ValueExpression) left, (ValueExpression) right);
            } else {
                throw new EventCondition.Compiler.UnexpectedTypeException(left, right);
            }
            return condition;
        }

        private static EventCondition in(final EventValueExpression left, final List<?> right) {
            return new EventCondition.Compiler.FieldInConstantList(
                    FieldReference.from(left.getFieldName()), right
            );
        }
```

**With:**

```java
        private static EventCondition in(final In in) {
            final Expression left = in.getLeft();
            final Expression right = in.getRight();
            final EventCondition condition;
            final ConditionFactory factory = new DefaultConditionFactory();
            if (eAndV(in) && isScalar((ValueExpression) in.getRight())) {
                condition = factory.createFieldInConstantScalar(
                        FieldReference.from(((EventValueExpression) left).getFieldName()),
                        ((ValueExpression) right).get().toString()
                );
            } else if (vAndE(in) && isScalar((ValueExpression) in.getLeft())) {
                final Object leftv = ((ValueExpression) left).get();
                final FieldReference rfield =
                        FieldReference.from(((EventValueExpression) right).getFieldName());
                if (leftv instanceof String) {
                    condition = factory.createConstantStringInField(
                            rfield, (String) leftv
                    );
                } else {
                    condition = factory.createConstantScalarInField(rfield, leftv);
                }
            } else if (eAndV(in) && listValueRight(in)) {
                condition = factory.createFieldInConstantList(
                        FieldReference.from(((EventValueExpression) left).getFieldName()), (List<?>) ((ValueExpression) right).get()
                );
            } else if (eAndE(in)) {
                condition = in((EventValueExpression) left, (EventValueExpression) right);
            } else if (vAndV(in)) {
                condition = in((ValueExpression) left, (ValueExpression) right);
            } else {
                throw new EventCondition.Compiler.UnexpectedTypeException(left, right);
            }
            return condition;
        }
```

### 3. EDIT `logstash-core/src/main/java/org/logstash/config/ir/compiler/EventCondition.java` (6-line block → 6-line replacement)

**Replaces:**

```java
        private static EventCondition in(final EventValueExpression left,
                                         final EventValueExpression right) {
            return new EventCondition.Compiler.FieldInField(
                    FieldReference.from(left.getFieldName()), FieldReference.from(right.getFieldName())
            );
        }
```

**With:**

```java
        private static EventCondition in(final EventValueExpression left,
                                         final EventValueExpression right) {
            return new DefaultConditionFactory().createFieldInField(
                    FieldReference.from(left.getFieldName()), FieldReference.from(right.getFieldName())
            );
        }
```

### 4. EDIT `logstash-core/src/main/java/org/logstash/config/ir/compiler/EventCondition.java` (3-line block → 3-line replacement)

**Replaces:**

```java
        private static EventCondition truthy(final EventValueExpression evalE) {
            return new EventCondition.Compiler.FieldTruthy(FieldReference.from(evalE.getFieldName()));
        }
```

**With:**

```java
        private static EventCondition truthy(final EventValueExpression evalE) {
            return new DefaultConditionFactory().createFieldTruthy(FieldReference.from(evalE.getFieldName()));
        }
```

### 5. EDIT `logstash-core/src/main/java/org/logstash/config/ir/compiler/EventCondition.java` (10-line block → 21-line replacement)

**Replaces:**

```java
        private static RubyRegexp newRegexp(String pattern) {
            final Ruby runtime = RubyUtil.RUBY;
            return RubyRegexp.newRegexpFromStr(runtime, runtime.newString(pattern), 0);
        }

        private static boolean matches(RubyString str, RubyRegexp regexp) {
            return regexp.match_p(RubyUtil.RUBY.getCurrentContext(), str).isTrue(); // match? returns true/false
        }

        private static final class FieldMatches implements EventCondition {
```

**With:**

```java
        private static RubyRegexp newRegexp(String pattern) {
            final Ruby runtime = RubyUtil.RUBY;
            return RubyRegexp.newRegexpFromStr(runtime, runtime.newString(pattern), 0);
        }

        private static boolean matches(RubyString str, RubyRegexp regexp) {
            return regexp.match_p(RubyUtil.RUBY.getCurrentContext(), str).isTrue(); // match? returns true/false
        }

        private static final class DefaultConditionFactory implements ConditionFactory {
            @Override public EventCondition createFieldMatches(String field, String pattern) { return new FieldMatches(field, pattern); }
            @Override public EventCondition createConstantMatches(Object constant, String pattern) { return new ConstantMatches(constant, pattern); }
            @Override public EventCondition createConstantStringInField(FieldReference field, String value) { return new ConstantStringInField(field, value); }
            @Override public EventCondition createConstantScalarInField(FieldReference field, Object value) { return new ConstantScalarInField(field, value); }
            @Override public EventCondition createFieldInConstantScalar(FieldReference field, String value) { return new FieldInConstantScalar(field, value); }
            @Override public EventCondition createFieldInField(FieldReference left, FieldReference right) { return new FieldInField(left, right); }
            @Override public EventCondition createFieldInConstantList(FieldReference field, List<?> value) { return new FieldInConstantList(field, value); }
            @Override public EventCondition createFieldTruthy(FieldReference field) { return new FieldTruthy(field); }
        }

        private static final class FieldMatches implements EventCondition {
```

### 6. CREATE `logstash-core/src/main/java/org/logstash/config/ir/compiler/ConditionFactory.java` (35 line(s))

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

package org.logstash.config.ir.compiler;

import org.logstash.FieldReference;
import org.logstash.ext.JrubyEventExtLibrary;
import java.util.List;

public interface ConditionFactory {
    EventCondition createFieldMatches(String field, String pattern);
    EventCondition createConstantMatches(Object constant, String pattern);
    EventCondition createConstantStringInField(FieldReference field, String value);
    EventCondition createConstantScalarInField(FieldReference field, Object value);
    EventCondition createFieldInConstantScalar(FieldReference field, String value);
    EventCondition createFieldInField(FieldReference left, FieldReference right);
    EventCondition createFieldInConstantList(FieldReference field, List<?> value);
    EventCondition createFieldTruthy(FieldReference field);
}
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `logstash-core/src/main/java/org/logstash/config/ir/compiler/ConditionFactory.java` | - → 32 | - → 0 | - → 3 | - → 3 | - → 0 |
| `logstash-core/src/main/java/org/logstash/config/ir/compiler/EventCondition.java` | 624 → 631 | 42 → 41 | 3.05 → 3.1 | 87 → 87 | 0 → 0 |

## Diff

```diff
diff --git a/logstash-core/src/main/java/org/logstash/config/ir/compiler/EventCondition.java b/logstash-core/src/main/java/org/logstash/config/ir/compiler/EventCondition.java
index 111f98a..56be81c 100644
--- a/logstash-core/src/main/java/org/logstash/config/ir/compiler/EventCondition.java
+++ b/logstash-core/src/main/java/org/logstash/config/ir/compiler/EventCondition.java
@@ -230,13 +230,14 @@ public interface EventCondition {
             final EventCondition condition;
             final Expression uleft = regex.getLeft();
             final Expression uright = regex.getRight();
+            final ConditionFactory factory = new DefaultConditionFactory();
             if (eAndV(regex)) {
-                condition = new EventCondition.Compiler.FieldMatches(
+                condition = factory.createFieldMatches(
                         ((EventValueExpression) uleft).getFieldName(),
                         ((ValueExpression) uright).get().toString()
                 );
             } else if (vAndR(regex)) {
-                condition = new EventCondition.Compiler.ConstantMatches(
+                condition = factory.createConstantMatches(
                         ((ValueExpression) uleft).get(),
                         ((RegexValueExpression) uright).get().toString()
                 );
@@ -291,8 +292,9 @@ public interface EventCondition {
             final Expression left = in.getLeft();
             final Expression right = in.getRight();
             final EventCondition condition;
+            final ConditionFactory factory = new DefaultConditionFactory();
             if (eAndV(in) && isScalar((ValueExpression) in.getRight())) {
-                condition = new EventCondition.Compiler.FieldInConstantScalar(
+                condition = factory.createFieldInConstantScalar(
                         FieldReference.from(((EventValueExpression) left).getFieldName()),
                         ((ValueExpression) right).get().toString()
                 );
@@ -301,15 +303,15 @@ public interface EventCondition {
                 final FieldReference rfield =
                         FieldReference.from(((EventValueExpression) right).getFieldName());
                 if (leftv instanceof String) {
-                    condition = new EventCondition.Compiler.ConstantStringInField(
+                    condition = factory.createConstantStringInField(
                             rfield, (String) leftv
                     );
                 } else {
-                    condition = new EventCondition.Compiler.ConstantScalarInField(rfield, leftv);
+                    condition = factory.createConstantScalarInField(rfield, leftv);
                 }
             } else if (eAndV(in) && listValueRight(in)) {
-                condition = in(
-                        (EventValueExpression) left, (List<?>) ((ValueExpression) right).get()
+                condition = factory.createFieldInConstantList(
+                        FieldReference.from(((EventValueExpression) left).getFieldName()), (List<?>) ((ValueExpression) right).get()
                 );
             } else if (eAndE(in)) {
                 condition = in((EventValueExpression) left, (EventValueExpression) right);
@@ -321,12 +323,6 @@ public interface EventCondition {
             return condition;
         }
 
-        private static EventCondition in(final EventValueExpression left, final List<?> right) {
-            return new EventCondition.Compiler.FieldInConstantList(
-                    FieldReference.from(left.getFieldName()), right
-            );
-        }
-
         /**
          * Compiles a constant (due to both of its sides being constant {@link ValueExpression})
          * conditional.
@@ -364,7 +360,7 @@ public interface EventCondition {
 
         private static EventCondition in(final EventValueExpression left,
                                          final EventValueExpression right) {
-            return new EventCondition.Compiler.FieldInField(
+            return new DefaultConditionFactory().createFieldInField(
                     FieldReference.from(left.getFieldName()), FieldReference.from(right.getFieldName())
             );
         }
@@ -409,7 +405,7 @@ public interface EventCondition {
         }
 
         private static EventCondition truthy(final EventValueExpression evalE) {
-            return new EventCondition.Compiler.FieldTruthy(FieldReference.from(evalE.getFieldName()));
+            return new DefaultConditionFactory().createFieldTruthy(FieldReference.from(evalE.getFieldName()));
         }
 
         private static EventCondition not(final EventCondition condition) {
@@ -513,6 +509,17 @@ public interface EventCondition {
             return regexp.match_p(RubyUtil.RUBY.getCurrentContext(), str).isTrue(); // match? returns true/false
         }
 
+        private static final class DefaultConditionFactory implements ConditionFactory {
+            @Override public EventCondition createFieldMatches(String field, String pattern) { return new FieldMatches(field, pattern); }
+            @Override public EventCondition createConstantMatches(Object constant, String pattern) { return new ConstantMatches(constant, pattern); }
+            @Override public EventCondition createConstantStringInField(FieldReference field, String value) { return new ConstantStringInField(field, value); }
+            @Override public EventCondition createConstantScalarInField(FieldReference field, Object value) { return new ConstantScalarInField(field, value); }
+            @Override public EventCondition createFieldInConstantScalar(FieldReference field, String value) { return new FieldInConstantScalar(field, value); }
+            @Override public EventCondition createFieldInField(FieldReference left, FieldReference right) { return new FieldInField(left, right); }
+            @Override public EventCondition createFieldInConstantList(FieldReference field, List<?> value) { return new FieldInConstantList(field, value); }
+            @Override public EventCondition createFieldTruthy(FieldReference field) { return new FieldTruthy(field); }
+        }
+
         private static final class FieldMatches implements EventCondition {
 
             private final FieldReference field;
diff --git a/logstash-core/src/main/java/org/logstash/config/ir/compiler/ConditionFactory.java b/logstash-core/src/main/java/org/logstash/config/ir/compiler/ConditionFactory.java
new file mode 100644
index 0000000..0000000
--- /dev/null
+++ b/logstash-core/src/main/java/org/logstash/config/ir/compiler/ConditionFactory.java
@@ -0,0 +1,35 @@
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
+package org.logstash.config.ir.compiler;
+
+import org.logstash.FieldReference;
+import org.logstash.ext.JrubyEventExtLibrary;
+import java.util.List;
+
+public interface ConditionFactory {
+    EventCondition createFieldMatches(String field, String pattern);
+    EventCondition createConstantMatches(Object constant, String pattern);
+    EventCondition createConstantStringInField(FieldReference field, String value);
+    EventCondition createConstantScalarInField(FieldReference field, Object value);
+    EventCondition createFieldInConstantScalar(FieldReference field, String value);
+    EventCondition createFieldInField(FieldReference left, FieldReference right);
+    EventCondition createFieldInConstantList(FieldReference field, List<?> value);
+    EventCondition createFieldTruthy(FieldReference field);
+}
\ No newline at end of file

```
