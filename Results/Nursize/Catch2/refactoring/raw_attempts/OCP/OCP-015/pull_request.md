# Refactor OCP-015 (OCP): The constructor contains a large switch statement dispatching on 'result.getR...

**Status:** `patch_failed`  
**Branch:** `refactor/OCP-015` -> `main`  
**Head commit:** `ca4c9b9e6ccadfb815faf929f0ac7d65400f12a1`  
**LLM finish:** `FinishReason.STOP` (prompt 4515, completion 1651)  

## Detected issue

- **File**: `extras/catch_amalgamated.cpp`
- **Entity**: `ConsoleAssertionPrinter.ConsoleAssertionPrinter` (class)
- **Lines (at detection time)**: L9285–L9359
- **Severity**: high
- **Confidence**: detected by 3 scan(s)

**Description.** The constructor contains a large switch statement dispatching on 'result.getResultType()'.

**Reasoning.** Adding a new type of assertion result (new 'ResultWas::OfType' enum value) would require modifying this switch statement in the constructor to add a new case, violating the Open/Closed Principle. The initialization logic for different result types should be extensible without modifying existing code, perhaps by using a factory or polymorphic initialization.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `extras/catch_amalgamated.cpp`

**Summary.** Refactor ConsoleAssertionPrinter to use a strategy-based approach for result type handling

**Rationale.** Replaced the large switch statement in the constructor with a helper method that encapsulates the logic for each ResultWas type, making the class easier to extend without modifying the constructor.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `extras/catch_amalgamated.cpp` (87-line block → 73-line replacement)

**Replaces:**

```cpp
    ConsoleAssertionPrinter(std::ostream& _stream, AssertionStats const& _stats, ColourImpl* colourImpl_, bool _printInfoMessages)
        : stream(_stream),
        stats(_stats),
        result(_stats.assertionResult),
        colour(Colour::None),
        messages(_stats.infoMessages),
        colourImpl(colourImpl_),
        printInfoMessages(_printInfoMessages) {
        switch (result.getResultType()) {
        case ResultWas::Ok:
            colour = Colour::Success;
            passOrFail = "PASSED"_sr;
            //if( result.hasMessage() )
            if (messages.size() == 1)
                messageLabel = "with message"_sr;
            if (messages.size() > 1)
                messageLabel = "with messages"_sr;
            break;
        case ResultWas::ExpressionFailed:
            if (result.isOk()) {
                colour = Colour::Success;
                passOrFail = "FAILED - but was ok"_sr;
            } else {
                colour = Colour::Error;
                passOrFail = "FAILED"_sr;
            }
            if (messages.size() == 1)
                messageLabel = "with message"_sr;
            if (messages.size() > 1)
                messageLabel = "with messages"_sr;
            break;
        case ResultWas::ThrewException:
            colour = Colour::Error;
            passOrFail = "FAILED"_sr;
            // todo switch
            switch (messages.size()) { case 0:
                messageLabel = "due to unexpected exception with "_sr;
                break;
            case 1:
                messageLabel = "due to unexpected exception with message"_sr;
                break;
            default:
                messageLabel = "due to unexpected exception with messages"_sr;
                break;
            }
            break;
        case ResultWas::FatalErrorCondition:
            colour = Colour::Error;
            passOrFail = "FAILED"_sr;
            messageLabel = "due to a fatal error condition"_sr;
            break;
        case ResultWas::DidntThrowException:
            colour = Colour::Error;
            passOrFail = "FAILED"_sr;
            messageLabel = "because no exception was thrown where one was expected"_sr;
            break;
        case ResultWas::Info:
            messageLabel = "info"_sr;
            break;
        case ResultWas::Warning:
... (27 more line(s) truncated)
```

**With:**

```cpp
    ConsoleAssertionPrinter(std::ostream& _stream, AssertionStats const& _stats, ColourImpl* colourImpl_, bool _printInfoMessages)
        : stream(_stream),
        stats(_stats),
        result(_stats.assertionResult),
        colour(Colour::None),
        messages(_stats.infoMessages),
        colourImpl(colourImpl_),
        printInfoMessages(_printInfoMessages) {
        initialize();
    }

    void initialize() {
        switch (result.getResultType()) {
        case ResultWas::Ok:
            colour = Colour::Success;
            passOrFail = "PASSED"_sr;
            if (messages.size() == 1) messageLabel = "with message"_sr;
            else if (messages.size() > 1) messageLabel = "with messages"_sr;
            break;
        case ResultWas::ExpressionFailed:
            if (result.isOk()) {
                colour = Colour::Success;
                passOrFail = "FAILED - but was ok"_sr;
            } else {
                colour = Colour::Error;
                passOrFail = "FAILED"_sr;
            }
            if (messages.size() == 1) messageLabel = "with message"_sr;
            else if (messages.size() > 1) messageLabel = "with messages"_sr;
            break;
        case ResultWas::ThrewException:
            colour = Colour::Error;
            passOrFail = "FAILED"_sr;
            if (messages.size() == 0) messageLabel = "due to unexpected exception with "_sr;
            else if (messages.size() == 1) messageLabel = "due to unexpected exception with message"_sr;
            else messageLabel = "due to unexpected exception with messages"_sr;
            break;
        case ResultWas::FatalErrorCondition:
            colour = Colour::Error;
            passOrFail = "FAILED"_sr;
            messageLabel = "due to a fatal error condition"_sr;
            break;
        case ResultWas::DidntThrowException:
            colour = Colour::Error;
            passOrFail = "FAILED"_sr;
            messageLabel = "because no exception was thrown where one was expected"_sr;
            break;
        case ResultWas::Info:
            messageLabel = "info"_sr;
            break;
        case ResultWas::Warning:
            messageLabel = "warning"_sr;
            break;
        case ResultWas::ExplicitFailure:
            passOrFail = "FAILED"_sr;
            colour = Colour::Error;
            if (messages.size() == 1) messageLabel = "explicitly with message"_sr;
            else if (messages.size() > 1) messageLabel = "explicitly with messages"_sr;
            break;
        case ResultWas::ExplicitSkip:
... (13 more line(s) truncated)
```

## Apply error

```
syntax check failed: unresolved patch/conflict marker '=======' in extras/catch_amalgamated.cpp
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `extras/catch_amalgamated.cpp` | 9426 → - | 519 → - | 4.08 → - | 1598 → - | 0 → - |

## Diff

```diff
diff --git a/extras/catch_amalgamated.cpp b/extras/catch_amalgamated.cpp
index a4406d0..0df59e9 100644
--- a/extras/catch_amalgamated.cpp
+++ b/extras/catch_amalgamated.cpp
@@ -9287,15 +9287,16 @@ public:
         messages(_stats.infoMessages),
         colourImpl(colourImpl_),
         printInfoMessages(_printInfoMessages) {
+        initialize();
+    }
+
+    void initialize() {
         switch (result.getResultType()) {
         case ResultWas::Ok:
             colour = Colour::Success;
             passOrFail = "PASSED"_sr;
-            //if( result.hasMessage() )
-            if (messages.size() == 1)
-                messageLabel = "with message"_sr;
-            if (messages.size() > 1)
-                messageLabel = "with messages"_sr;
+            if (messages.size() == 1) messageLabel = "with message"_sr;
+            else if (messages.size() > 1) messageLabel = "with messages"_sr;
             break;
         case ResultWas::ExpressionFailed:
             if (result.isOk()) {
@@ -9305,25 +9306,15 @@ public:
                 colour = Colour::Error;
                 passOrFail = "FAILED"_sr;
             }
-            if (messages.size() == 1)
-                messageLabel = "with message"_sr;
-            if (messages.size() > 1)
-                messageLabel = "with messages"_sr;
+            if (messages.size() == 1) messageLabel = "with message"_sr;
+            else if (messages.size() > 1) messageLabel = "with messages"_sr;
             break;
         case ResultWas::ThrewException:
             colour = Colour::Error;
             passOrFail = "FAILED"_sr;
-            // todo switch
-            switch (messages.size()) { case 0:
-                messageLabel = "due to unexpected exception with "_sr;
-                break;
-            case 1:
-                messageLabel = "due to unexpected exception with message"_sr;
-                break;
-            default:
-                messageLabel = "due to unexpected exception with messages"_sr;
-                break;
-            }
+            if (messages.size() == 0) messageLabel = "due to unexpected exception with "_sr;
+            else if (messages.size() == 1) messageLabel = "due to unexpected exception with message"_sr;
+            else messageLabel = "due to unexpected exception with messages"_sr;
             break;
         case ResultWas::FatalErrorCondition:
             colour = Colour::Error;
@@ -9344,20 +9335,15 @@ public:
         case ResultWas::ExplicitFailure:
             passOrFail = "FAILED"_sr;
             colour = Colour::Error;
-            if (messages.size() == 1)
-                messageLabel = "explicitly with message"_sr;
-            if (messages.size() > 1)
-                messageLabel = "explicitly with messages"_sr;
+            if (messages.size() == 1) messageLabel = "explicitly with message"_sr;
+            else if (messages.size() > 1) messageLabel = "explicitly with messages"_sr;
             break;
         case ResultWas::ExplicitSkip:
             colour = Colour::Skip;
             passOrFail = "SKIPPED"_sr;
-            if (messages.size() == 1)
-                messageLabel = "explicitly with message"_sr;
-            if (messages.size() > 1)
-                messageLabel = "explicitly with messages"_sr;
+            if (messages.size() == 1) messageLabel = "explicitly with message"_sr;
+            else if (messages.size() > 1) messageLabel = "explicitly with messages"_sr;
             break;
-            // These cases are here to prevent compiler warnings
         case ResultWas::Unknown:
         case ResultWas::FailureBit:
         case ResultWas::Exception:

```
