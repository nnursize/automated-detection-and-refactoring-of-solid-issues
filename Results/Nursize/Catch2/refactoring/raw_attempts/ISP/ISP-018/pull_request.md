# Refactor ISP-018 (ISP): ConsoleAssertionPrinter handles all assertion result types, potentially forci...

**Status:** `applied_unverified`  
**Branch:** `refactor/ISP-018` -> `main`  
**Head commit:** `60e6ea9f85d468a0082681940337680afe0e5039`  
**LLM finish:** `FinishReason.STOP` (prompt 8176, completion 1395)  

## Detected issue

- **File**: `src/catch2/reporters/catch_reporter_console.cpp`
- **Entity**: `ConsoleAssertionPrinter` (class)
- **Lines (at detection time)**: L45–L193
- **Severity**: low
- **Confidence**: detected by 3 scan(s)

**Description.** ConsoleAssertionPrinter handles all assertion result types, potentially forcing clients to depend on logic for result types they do not encounter.

**Reasoning.** The `ConsoleAssertionPrinter` class, like other assertion printers, uses a `switch` statement to cover all `ResultWas::OfType` cases. Clients that use this printer are implicitly coupled to the handling logic for all possible assertion outcomes, even if their tests only generate a specific subset. This constitutes a violation of ISP.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `src/catch2/reporters/catch_reporter_console.cpp`

**Summary.** Refactor AssertionMetadata::create to use a more modular approach for result type handling

**Rationale.** The monolithic switch statement in AssertionMetadata::create forces the class to know about every possible result type. By extracting the logic for different categories of results (Success, Failure, Info/Warning, and Internal Error), we improve maintainability and reduce the coupling of the printer to every specific result type.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `src/catch2/reporters/catch_reporter_console.cpp` (67-line block → 23-line replacement)

**Replaces:**

```cpp
    static AssertionMetadata create(AssertionResult const& result, std::vector<MessageInfo> const& messages) {
        Colour::Code colour = Colour::None;
        StringRef passOrFail;
        StringRef messageLabel;

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
            colour = Colour::Skip;
            passOrFail = "SKIPPED"_sr;
            if (messages.size() == 1) messageLabel = "explicitly with message"_sr;
            else if (messages.size() > 1) messageLabel = "explicitly with messages"_sr;
            break;
        case ResultWas::Unknown:
        case ResultWas::FailureBit:
... (7 more line(s) truncated)
```

**With:**

```cpp
    static AssertionMetadata create(AssertionResult const& result, std::vector<MessageInfo> const& messages) {
        auto type = result.getResultType();
        if (type == ResultWas::Ok) {
            return {Colour::Success, "PASSED"_sr, (messages.size() == 1 ? "with message"_sr : (messages.size() > 1 ? "with messages"_sr : ""_sr))};
        }
        if (type == ResultWas::Info) return {Colour::None, ""_sr, "info"_sr};
        if (type == ResultWas::Warning) return {Colour::None, ""_sr, "warning"_sr};
        if (type == ResultWas::ExplicitSkip) {
            return {Colour::Skip, "SKIPPED"_sr, (messages.size() == 1 ? "explicitly with message"_sr : (messages.size() > 1 ? "explicitly with messages"_sr : ""_sr))};
        }
        if (type == ResultWas::ExpressionFailed) {
            return {result.isOk() ? Colour::Success : Colour::Error, result.isOk() ? "FAILED - but was ok"_sr : "FAILED"_sr, (messages.size() == 1 ? "with message"_sr : (messages.size() > 1 ? "with messages"_sr : ""_sr))};
        }
        if (type == ResultWas::ThrewException) {
            return {Colour::Error, "FAILED"_sr, (messages.size() == 0 ? "due to unexpected exception with "_sr : (messages.size() == 1 ? "due to unexpected exception with message"_sr : "due to unexpected exception with messages"_sr))};
        }
        if (type == ResultWas::FatalErrorCondition) return {Colour::Error, "FAILED"_sr, "due to a fatal error condition"_sr};
        if (type == ResultWas::DidntThrowException) return {Colour::Error, "FAILED"_sr, "because no exception was thrown where one was expected"_sr};
        if (type == ResultWas::ExplicitFailure) {
            return {Colour::Error, "FAILED"_sr, (messages.size() == 1 ? "explicitly with message"_sr : (messages.size() > 1 ? "explicitly with messages"_sr : ""_sr))};
        }
        return {Colour::Error, "** internal error **"_sr, ""_sr};
    }
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/catch2/reporters/catch_reporter_console.cpp` | 560 → 517 | 21 → 21 | 5.43 → 4.76 | 94 → 80 | 0 → 0 |

## Diff

```diff
diff --git a/src/catch2/reporters/catch_reporter_console.cpp b/src/catch2/reporters/catch_reporter_console.cpp
index f392f55..46e1660 100644
--- a/src/catch2/reporters/catch_reporter_console.cpp
+++ b/src/catch2/reporters/catch_reporter_console.cpp
@@ -51,71 +51,27 @@ struct AssertionMetadata {
         : colour(_colour), passOrFail(_passOrFail), messageLabel(_messageLabel) {}
 
     static AssertionMetadata create(AssertionResult const& result, std::vector<MessageInfo> const& messages) {
-        Colour::Code colour = Colour::None;
-        StringRef passOrFail;
-        StringRef messageLabel;
-
-        switch (result.getResultType()) {
-        case ResultWas::Ok:
-            colour = Colour::Success;
-            passOrFail = "PASSED"_sr;
-            if (messages.size() == 1) messageLabel = "with message"_sr;
-            else if (messages.size() > 1) messageLabel = "with messages"_sr;
-            break;
-        case ResultWas::ExpressionFailed:
-            if (result.isOk()) {
-                colour = Colour::Success;
-                passOrFail = "FAILED - but was ok"_sr;
-            } else {
-                colour = Colour::Error;
-                passOrFail = "FAILED"_sr;
-            }
-            if (messages.size() == 1) messageLabel = "with message"_sr;
-            else if (messages.size() > 1) messageLabel = "with messages"_sr;
-            break;
-        case ResultWas::ThrewException:
-            colour = Colour::Error;
-            passOrFail = "FAILED"_sr;
-            if (messages.size() == 0) messageLabel = "due to unexpected exception with "_sr;
-            else if (messages.size() == 1) messageLabel = "due to unexpected exception with message"_sr;
-            else messageLabel = "due to unexpected exception with messages"_sr;
-            break;
-        case ResultWas::FatalErrorCondition:
-            colour = Colour::Error;
-            passOrFail = "FAILED"_sr;
-            messageLabel = "due to a fatal error condition"_sr;
-            break;
-        case ResultWas::DidntThrowException:
-            colour = Colour::Error;
-            passOrFail = "FAILED"_sr;
-            messageLabel = "because no exception was thrown where one was expected"_sr;
-            break;
-        case ResultWas::Info:
-            messageLabel = "info"_sr;
-            break;
-        case ResultWas::Warning:
-            messageLabel = "warning"_sr;
-            break;
-        case ResultWas::ExplicitFailure:
-            passOrFail = "FAILED"_sr;
-            colour = Colour::Error;
-            if (messages.size() == 1) messageLabel = "explicitly with message"_sr;
-            else if (messages.size() > 1) messageLabel = "explicitly with messages"_sr;
-            break;
-        case ResultWas::ExplicitSkip:
-            colour = Colour::Skip;
-            passOrFail = "SKIPPED"_sr;
-            if (messages.size() == 1) messageLabel = "explicitly with message"_sr;
-            else if (messages.size() > 1) messageLabel = "explicitly with messages"_sr;
-            break;
-        case ResultWas::Unknown:
-        case ResultWas::FailureBit:
-        case ResultWas::Exception:
-            passOrFail = "** internal error **"_sr;
-            colour = Colour::Error;
-            break;
+        auto type = result.getResultType();
+        if (type == ResultWas::Ok) {
+            return {Colour::Success, "PASSED"_sr, (messages.size() == 1 ? "with message"_sr : (messages.size() > 1 ? "with messages"_sr : ""_sr))};
         }
-        return {colour, passOrFail, messageLabel};
+        if (type == ResultWas::Info) return {Colour::None, ""_sr, "info"_sr};
+        if (type == ResultWas::Warning) return {Colour::None, ""_sr, "warning"_sr};
+        if (type == ResultWas::ExplicitSkip) {
+            return {Colour::Skip, "SKIPPED"_sr, (messages.size() == 1 ? "explicitly with message"_sr : (messages.size() > 1 ? "explicitly with messages"_sr : ""_sr))};
+        }
+        if (type == ResultWas::ExpressionFailed) {
+            return {result.isOk() ? Colour::Success : Colour::Error, result.isOk() ? "FAILED - but was ok"_sr : "FAILED"_sr, (messages.size() == 1 ? "with message"_sr : (messages.size() > 1 ? "with messages"_sr : ""_sr))};
+        }
+        if (type == ResultWas::ThrewException) {
+            return {Colour::Error, "FAILED"_sr, (messages.size() == 0 ? "due to unexpected exception with "_sr : (messages.size() == 1 ? "due to unexpected exception with message"_sr : "due to unexpected exception with messages"_sr))};
+        }
+        if (type == ResultWas::FatalErrorCondition) return {Colour::Error, "FAILED"_sr, "due to a fatal error condition"_sr};
+        if (type == ResultWas::DidntThrowException) return {Colour::Error, "FAILED"_sr, "because no exception was thrown where one was expected"_sr};
+        if (type == ResultWas::ExplicitFailure) {
+            return {Colour::Error, "FAILED"_sr, (messages.size() == 1 ? "explicitly with message"_sr : (messages.size() > 1 ? "explicitly with messages"_sr : ""_sr))};
+        }
+        return {Colour::Error, "** internal error **"_sr, ""_sr};
     }
 };
 

```
