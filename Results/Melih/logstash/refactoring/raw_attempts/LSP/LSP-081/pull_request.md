# Refactor LSP-081 (LSP): Final method in an abstract class throws IllegalStateException, effectively n...

**Status:** `applied_unverified`  
**Branch:** `refactor/LSP-081` -> `main`  
**Head commit:** `2a11b71ed196ba2e15f5d972c37073f243040146`  
**LLM finish:** `FinishReason.STOP` (prompt 12187, completion 306)  

## Detected issue

- **File**: `logstash-core/src/main/java/org/logstash/execution/AbstractPipelineExt.java`
- **Entity**: `AbstractPipelineExt.isShutdownRequested` (method)
- **Lines (at detection time)**: L909–L912
- **Severity**: high
- **Confidence**: detected by 2 scan(s)

**Description.** Final method in an abstract class throws IllegalStateException, effectively nullifying its intended functionality.

**Reasoning.** The `isShutdownRequested` method is declared `final` in an abstract class `AbstractPipelineExt`, yet its implementation always throws an `IllegalStateException` with a message indicating that concrete implementations *should* provide it. This violates LSP because `AbstractPipelineExt` cannot be substituted for a concrete pipeline without altering the program's correctness; any call to this method will result in an unexpected runtime exception. This effectively nullifies the method's contract in the abstract class, forcing clients to handle an exception or rely on subclasses that paradoxically override a final method (a contradiction in Java).

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `logstash-core/src/main/java/org/logstash/execution/AbstractPipelineExt.java`

**Summary.** Change isShutdownRequested to return false by default instead of throwing an exception

**Rationale.** The method was throwing an IllegalStateException, which violates the Liskov Substitution Principle by breaking the contract of the base class. Changing the default implementation to return 'false' (a safe default for a pipeline that hasn't explicitly been told to shut down) allows subclasses to function without being forced to override the method if they don't need custom shutdown logic, while still allowing them to override it if they do.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `logstash-core/src/main/java/org/logstash/execution/AbstractPipelineExt.java` (5-line block → 4-line replacement)

**Replaces:**

```java
    @JRubyMethod(name = "shutdown_requested?")
    public IRubyObject isShutdownRequested(final ThreadContext context) {
        // shutdown_requested? MUST be implemented in the concrete implementation of this class.
        throw new IllegalStateException("Pipeline implementation does not provide `shutdown_requested?`, which is a Logstash internal error.");
    }
```

**With:**

```java
    @JRubyMethod(name = "shutdown_requested?")
    public IRubyObject isShutdownRequested(final ThreadContext context) {
        return context.fals;
    }
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `logstash-core/src/main/java/org/logstash/execution/AbstractPipelineExt.java` | 763 → 763 | 62 → 62 | 1.73 → 1.73 | 46 → 46 | 0 → 0 |

## Diff

```diff
diff --git a/logstash-core/src/main/java/org/logstash/execution/AbstractPipelineExt.java b/logstash-core/src/main/java/org/logstash/execution/AbstractPipelineExt.java
index 545a302..2bc72f6 100644
--- a/logstash-core/src/main/java/org/logstash/execution/AbstractPipelineExt.java
+++ b/logstash-core/src/main/java/org/logstash/execution/AbstractPipelineExt.java
@@ -861,8 +861,7 @@ public class AbstractPipelineExt extends RubyBasicObject {
 
     @JRubyMethod(name = "shutdown_requested?")
     public IRubyObject isShutdownRequested(final ThreadContext context) {
-        // shutdown_requested? MUST be implemented in the concrete implementation of this class.
-        throw new IllegalStateException("Pipeline implementation does not provide `shutdown_requested?`, which is a Logstash internal error.");
+        return context.fals;
     }
 
     @VisibleForTesting

```
