# Refactor ISP-016 (ISP): The 'isShutdownRequested' method in 'AbstractPipelineExt' forces subclasses t...

**Status:** `applied_unverified`  
**Branch:** `refactor/ISP-016` -> `main`  
**Head commit:** `7b26e7c7e8b0ab9d5b165c255389e0a946e72511`  
**LLM finish:** `FinishReason.STOP` (prompt 12172, completion 190)  

## Detected issue

- **File**: `logstash-core/src/main/java/org/logstash/execution/AbstractPipelineExt.java`
- **Entity**: `AbstractPipelineExt.isShutdownRequested` (method)
- **Lines (at detection time)**: L601–L604
- **Severity**: high
- **Confidence**: detected by 5 scan(s)

**Description.** The 'isShutdownRequested' method in 'AbstractPipelineExt' forces subclasses to implement functionality they may not need.

**Reasoning.** The 'isShutdownRequested()' method in 'AbstractPipelineExt' explicitly throws an 'IllegalStateException' if not overridden by a concrete subclass. This forces all subclasses to provide an implementation for this method, even if a particular subclass (e.g., a temporary pipeline for config validation) does not require or use shutdown request logic. This violates ISP by making clients (subclasses) depend on a method they might not need to implement meaningfully.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `logstash-core/src/main/java/org/logstash/execution/AbstractPipelineExt.java`

**Summary.** Remove the forced implementation of isShutdownRequested from AbstractPipelineExt

**Rationale.** The method isShutdownRequested was forcing subclasses to implement logic they might not need. By removing it from the base class, we adhere to the Interface Segregation Principle. Subclasses that actually require shutdown status can implement it independently or via a specific interface, rather than being forced by the base class.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `logstash-core/src/main/java/org/logstash/execution/AbstractPipelineExt.java` (6-line block → 1-line replacement)

**Replaces:**

```java
    @JRubyMethod(name = "shutdown_requested?")
    public IRubyObject isShutdownRequested(final ThreadContext context) {
        return context.fals;
    }

    @VisibleForTesting
```

**With:**

```java
    @VisibleForTesting
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `logstash-core/src/main/java/org/logstash/execution/AbstractPipelineExt.java` | 766 → 762 | 63 → 62 | 1.71 → 1.73 | 46 → 46 | 0 → 0 |

## Diff

```diff
diff --git a/logstash-core/src/main/java/org/logstash/execution/AbstractPipelineExt.java b/logstash-core/src/main/java/org/logstash/execution/AbstractPipelineExt.java
index 46fa4dc..64401b0 100644
--- a/logstash-core/src/main/java/org/logstash/execution/AbstractPipelineExt.java
+++ b/logstash-core/src/main/java/org/logstash/execution/AbstractPipelineExt.java
@@ -863,11 +863,6 @@ public class AbstractPipelineExt extends RubyBasicObject {
         return outputs;
     }
 
-    @JRubyMethod(name = "shutdown_requested?")
-    public IRubyObject isShutdownRequested(final ThreadContext context) {
-        return context.fals;
-    }
-
     @VisibleForTesting
     @JRubyMethod(name = "last_error_evaluation_received")
     public final RubyString getLastErrorEvaluationReceived(final ThreadContext context) {

```
