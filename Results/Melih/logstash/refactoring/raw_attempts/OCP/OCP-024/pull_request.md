# Refactor OCP-024 (OCP): The buildCondition method uses a long instanceof chain to dispatch compilatio...

**Status:** `applied_unverified`  
**Branch:** `refactor/OCP-024` -> `main`  
**Head commit:** `ebdec654880841571bcef5c4cdda9dcc09686534`  
**LLM finish:** `FinishReason.STOP` (prompt 8769, completion 850)  

## Detected issue

- **File**: `logstash-core/src/main/java/org/logstash/config/ir/compiler/EventCondition.java`
- **Entity**: `Compiler.buildCondition` (method)
- **Lines (at detection time)**: L115–L143
- **Severity**: high
- **Confidence**: detected by 3 scan(s)

**Description.** The buildCondition method uses a long instanceof chain to dispatch compilation logic based on expression types.

**Reasoning.** Adding a new type of BooleanExpression requires modifying this central compiler method to add a new branch. This violates OCP as the class is not closed for modification when extending the language's expression set. A better approach would be a visitor pattern or polymorphic dispatch on the expression objects themselves.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `logstash-core/src/main/java/org/logstash/config/ir/compiler/EventCondition.java`

**Summary.** Refactor EventCondition.Compiler to use a visitor pattern for expression compilation

**Rationale.** The long instanceof chain in buildCondition violates the Open/Closed Principle. By introducing a visitor interface (ConditionCompilerVisitor) and implementing it in the Compiler class, we delegate the dispatch logic to the expression types, allowing for easier extension without modifying the core compiler method.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `logstash-core/src/main/java/org/logstash/config/ir/compiler/EventCondition.java` (32-line block → 29-line replacement)

**Replaces:**

```java
        public EventCondition buildCondition(final BooleanExpression expression) {
            synchronized (cache) {
                final String cachekey = expression.toRubyString();
                final EventCondition cached = cache.get(cachekey);
                if (cached != null) {
                    return cached;
                }
                final EventCondition condition;
                if (expression instanceof Eq) {
                    condition = eq((Eq) expression);
                } else if (expression instanceof RegexEq) {
                    condition = regex((RegexEq) expression);
                } else if (expression instanceof In) {
                    condition = in((In) expression);
                } else if (expression instanceof Or || expression instanceof And) {
                    condition = booleanCondition((BinaryBooleanExpression) expression);
                } else if (expression instanceof Truthy) {
                    condition = truthy((Truthy) expression);
                } else if (expression instanceof Not) {
                    condition = not((Not) expression);
                } else if (expression instanceof Gt || expression instanceof Gte
                        || expression instanceof Lt || expression instanceof Lte) {
                    condition = comparison((BinaryBooleanExpression) expression);
                } else if (expression instanceof Neq) {
                    condition = not(eq((BinaryBooleanExpression) expression));
                } else {
                    throw new EventCondition.Compiler.UnexpectedTypeException(expression);
                }
                cache.put(cachekey, condition);
                return condition;
            }
        }
```

**With:**

```java
        public EventCondition buildCondition(final BooleanExpression expression) {
            synchronized (cache) {
                final String cachekey = expression.toRubyString();
                final EventCondition cached = cache.get(cachekey);
                if (cached != null) {
                    return cached;
                }
                final EventCondition condition = expression.accept(new ConditionCompilerVisitor(this));
                cache.put(cachekey, condition);
                return condition;
            }
        }

        private final class ConditionCompilerVisitor implements org.logstash.config.ir.expression.BooleanExpressionVisitor<EventCondition> {
            private final Compiler compiler;
            ConditionCompilerVisitor(Compiler compiler) { this.compiler = compiler; }
            @Override public EventCondition visit(Eq e) { return eq(e); }
            @Override public EventCondition visit(RegexEq e) { return regex(e); }
            @Override public EventCondition visit(In e) { return in(e); }
            @Override public EventCondition visit(And e) { return booleanCondition(e); }
            @Override public EventCondition visit(Or e) { return booleanCondition(e); }
            @Override public EventCondition visit(Truthy e) { return truthy(e); }
            @Override public EventCondition visit(Not e) { return not(e); }
            @Override public EventCondition visit(Gt e) { return comparison(e); }
            @Override public EventCondition visit(Gte e) { return comparison(e); }
            @Override public EventCondition visit(Lt e) { return comparison(e); }
            @Override public EventCondition visit(Lte e) { return comparison(e); }
            @Override public EventCondition visit(Neq e) { return not(eq(e)); }
        }
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `logstash-core/src/main/java/org/logstash/config/ir/compiler/EventCondition.java` | 628 → 624 | 42 → 42 | 3.33 → 3.05 | 99 → 87 | 0 → 0 |

## Diff

```diff
diff --git a/logstash-core/src/main/java/org/logstash/config/ir/compiler/EventCondition.java b/logstash-core/src/main/java/org/logstash/config/ir/compiler/EventCondition.java
index 62e3a3e..111f98a 100644
--- a/logstash-core/src/main/java/org/logstash/config/ir/compiler/EventCondition.java
+++ b/logstash-core/src/main/java/org/logstash/config/ir/compiler/EventCondition.java
@@ -114,32 +114,29 @@ public interface EventCondition {
                 if (cached != null) {
                     return cached;
                 }
-                final EventCondition condition;
-                if (expression instanceof Eq) {
-                    condition = eq((Eq) expression);
-                } else if (expression instanceof RegexEq) {
-                    condition = regex((RegexEq) expression);
-                } else if (expression instanceof In) {
-                    condition = in((In) expression);
-                } else if (expression instanceof Or || expression instanceof And) {
-                    condition = booleanCondition((BinaryBooleanExpression) expression);
-                } else if (expression instanceof Truthy) {
-                    condition = truthy((Truthy) expression);
-                } else if (expression instanceof Not) {
-                    condition = not((Not) expression);
-                } else if (expression instanceof Gt || expression instanceof Gte
-                        || expression instanceof Lt || expression instanceof Lte) {
-                    condition = comparison((BinaryBooleanExpression) expression);
-                } else if (expression instanceof Neq) {
-                    condition = not(eq((BinaryBooleanExpression) expression));
-                } else {
-                    throw new EventCondition.Compiler.UnexpectedTypeException(expression);
-                }
+                final EventCondition condition = expression.accept(new ConditionCompilerVisitor(this));
                 cache.put(cachekey, condition);
                 return condition;
             }
         }
 
+        private final class ConditionCompilerVisitor implements org.logstash.config.ir.expression.BooleanExpressionVisitor<EventCondition> {
+            private final Compiler compiler;
+            ConditionCompilerVisitor(Compiler compiler) { this.compiler = compiler; }
+            @Override public EventCondition visit(Eq e) { return eq(e); }
+            @Override public EventCondition visit(RegexEq e) { return regex(e); }
+            @Override public EventCondition visit(In e) { return in(e); }
+            @Override public EventCondition visit(And e) { return booleanCondition(e); }
+            @Override public EventCondition visit(Or e) { return booleanCondition(e); }
+            @Override public EventCondition visit(Truthy e) { return truthy(e); }
+            @Override public EventCondition visit(Not e) { return not(e); }
+            @Override public EventCondition visit(Gt e) { return comparison(e); }
+            @Override public EventCondition visit(Gte e) { return comparison(e); }
+            @Override public EventCondition visit(Lt e) { return comparison(e); }
+            @Override public EventCondition visit(Lte e) { return comparison(e); }
+            @Override public EventCondition visit(Neq e) { return not(eq(e)); }
+        }
+
         private EventCondition booleanCondition(final BinaryBooleanExpression expression) {
             final Expression left = expression.getLeft();
             final Expression right = expression.getRight();

```
