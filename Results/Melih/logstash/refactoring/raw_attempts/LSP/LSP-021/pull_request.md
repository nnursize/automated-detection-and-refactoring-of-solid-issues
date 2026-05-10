# Refactor LSP-021 (LSP): Subtype catches a specific RuntimeException and alters propagation behavior.

**Status:** `applied_unverified`  
**Branch:** `refactor/LSP-021` -> `main`  
**Head commit:** `f94c16851eaf546ac12fb395e0d57ebf2d1a6901`  
**LLM finish:** `FinishReason.STOP` (prompt 7466, completion 204)  

## Detected issue

- **File**: `logstash-core/src/main/java/org/logstash/config/ir/compiler/DatasetCompiler.java`
- **Entity**: `DatasetCompiler.Complement.compute` (method)
- **Lines (at detection time)**: L506–L515
- **Severity**: medium
- **Confidence**: detected by 2 scan(s)

**Description.** Subtype catches a specific RuntimeException and alters propagation behavior.

**Reasoning.** The `DatasetCompiler.Complement#compute` method catches `ConditionalEvaluationError` (a `RuntimeException`). If the `Dataset` interface's contract for `compute` implies that all `RuntimeException`s should propagate, then catching this specific exception and returning `data` (a behavioral change) violates LSP. A client might expect certain exceptions to propagate, but `Complement` handles it differently.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `logstash-core/src/main/java/org/logstash/config/ir/compiler/DatasetCompiler.java`

**Summary.** Remove catch block for ConditionalEvaluationError in DatasetCompiler.Complement to preserve exception propagation

**Rationale.** The catch block in DatasetCompiler.Complement#compute was suppressing ConditionalEvaluationError, which violates the Liskov Substitution Principle by altering the expected exception propagation behavior of the Dataset interface. Removing the catch block ensures that the exception propagates as expected by the contract.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `logstash-core/src/main/java/org/logstash/config/ir/compiler/DatasetCompiler.java` (7-line block → 3-line replacement)

**Replaces:**

```java
            try {
                parent.compute(batch, flush, shutdown);
                done = true;
                return data;
            } catch (ConditionalEvaluationError ex) {
                return data;
            }
```

**With:**

```java
            parent.compute(batch, flush, shutdown);
            done = true;
            return data;
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `logstash-core/src/main/java/org/logstash/config/ir/compiler/DatasetCompiler.java` | 508 → 504 | 27 → 27 | 2.37 → 2.33 | 38 → 37 | 0 → 0 |

## Diff

```diff
diff --git a/logstash-core/src/main/java/org/logstash/config/ir/compiler/DatasetCompiler.java b/logstash-core/src/main/java/org/logstash/config/ir/compiler/DatasetCompiler.java
index 956bbe1..cd21019 100644
--- a/logstash-core/src/main/java/org/logstash/config/ir/compiler/DatasetCompiler.java
+++ b/logstash-core/src/main/java/org/logstash/config/ir/compiler/DatasetCompiler.java
@@ -522,13 +522,9 @@ public final class DatasetCompiler {
             if (done) {
                 return data;
             }
-            try {
-                parent.compute(batch, flush, shutdown);
-                done = true;
-                return data;
-            } catch (ConditionalEvaluationError ex) {
-                return data;
-            }
+            parent.compute(batch, flush, shutdown);
+            done = true;
+            return data;
         }
 
         @Override

```
