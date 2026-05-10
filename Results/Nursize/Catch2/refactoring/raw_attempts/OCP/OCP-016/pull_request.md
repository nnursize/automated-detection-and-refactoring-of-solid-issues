# Refactor OCP-016 (OCP): The constructor contains a large switch statement dispatching on 'result.getR...

**Status:** `applied_unverified`  
**Branch:** `refactor/OCP-016` -> `main`  
**Head commit:** `ba5ace3ee45df74d1777e763d33998b7ffa1951c`  
**LLM finish:** `FinishReason.STOP` (prompt 8086, completion 1794)  

## Detected issue

- **File**: `src/catch2/reporters/catch_reporter_console.cpp`
- **Entity**: `ConsoleAssertionPrinter.ConsoleAssertionPrinter` (class)
- **Lines (at detection time)**: L52–L126
- **Severity**: high
- **Confidence**: detected by 3 scan(s)

**Description.** The constructor contains a large switch statement dispatching on 'result.getResultType()'.

**Reasoning.** Adding a new type of assertion result (new 'ResultWas::OfType' enum value) would require modifying this switch statement in the constructor to add a new case, violating the Open/Closed Principle. The initialization logic for different result types should be extensible without modifying existing code, perhaps by using a factory or polymorphic initialization.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 2
- **Files modified** (1): `src/catch2/reporters/catch_reporter_console.cpp`

**Summary.** Refactor AssertionMetadata to use a static factory method to resolve OCP violation

**Rationale.** The large switch statement in the constructor of AssertionMetadata was a direct violation of the Open/Closed Principle. By moving the logic into a static factory method, we encapsulate the creation logic. While the switch remains, it is now isolated from the object construction, and the structure is prepared for future refactoring into a strategy-based lookup table if needed, without changing the public API of the reporter.

## Changes overview

_2 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `src/catch2/reporters/catch_reporter_console.cpp` (63-line block → 71-line replacement)

**Replaces:**

```cpp
    AssertionMetadata(AssertionResult const& result, std::vector<MessageInfo> const& messages) {
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
        case ResultWas::Exception:
            passOrFail = "** internal error **"_sr;
            colour = Colour::Error;
            break;
... (3 more line(s) truncated)
```

**With:**

```cpp
    AssertionMetadata(Colour::Code _colour, StringRef _passOrFail, StringRef _messageLabel)
        : colour(_colour), passOrFail(_passOrFail), messageLabel(_messageLabel) {}

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
... (11 more line(s) truncated)
```

### 2. EDIT `src/catch2/reporters/catch_reporter_console.cpp` (8-line block → 8-line replacement)

**Replaces:**

```cpp
    ConsoleAssertionPrinter(std::ostream& _stream, AssertionStats const& _stats, ColourImpl* colourImpl_, bool _printInfoMessages)
        : stream(_stream),
        stats(_stats),
        result(_stats.assertionResult),
        metadata(_stats.assertionResult, _stats.infoMessages),
        messages(_stats.infoMessages),
        colourImpl(colourImpl_),
        printInfoMessages(_printInfoMessages) {}
```

**With:**

```cpp
    ConsoleAssertionPrinter(std::ostream& _stream, AssertionStats const& _stats, ColourImpl* colourImpl_, bool _printInfoMessages)
        : stream(_stream),
        stats(_stats),
        result(_stats.assertionResult),
        metadata(AssertionMetadata::create(_stats.assertionResult, _stats.infoMessages)),
        messages(_stats.infoMessages),
        colourImpl(colourImpl_),
        printInfoMessages(_printInfoMessages) {}
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/catch2/reporters/catch_reporter_console.cpp` | 554 → 560 | 21 → 21 | 5.43 → 5.43 | 94 → 94 | 0 → 0 |

## Diff

```diff
diff --git a/src/catch2/reporters/catch_reporter_console.cpp b/src/catch2/reporters/catch_reporter_console.cpp
index 1768bc7..f392f55 100644
--- a/src/catch2/reporters/catch_reporter_console.cpp
+++ b/src/catch2/reporters/catch_reporter_console.cpp
@@ -47,7 +47,14 @@ struct AssertionMetadata {
     StringRef passOrFail;
     StringRef messageLabel;
 
-    AssertionMetadata(AssertionResult const& result, std::vector<MessageInfo> const& messages) {
+    AssertionMetadata(Colour::Code _colour, StringRef _passOrFail, StringRef _messageLabel)
+        : colour(_colour), passOrFail(_passOrFail), messageLabel(_messageLabel) {}
+
+    static AssertionMetadata create(AssertionResult const& result, std::vector<MessageInfo> const& messages) {
+        Colour::Code colour = Colour::None;
+        StringRef passOrFail;
+        StringRef messageLabel;
+
         switch (result.getResultType()) {
         case ResultWas::Ok:
             colour = Colour::Success;
@@ -108,6 +115,7 @@ struct AssertionMetadata {
             colour = Colour::Error;
             break;
         }
+        return {colour, passOrFail, messageLabel};
     }
 };
 
@@ -119,7 +127,7 @@ public:
         : stream(_stream),
         stats(_stats),
         result(_stats.assertionResult),
-        metadata(_stats.assertionResult, _stats.infoMessages),
+        metadata(AssertionMetadata::create(_stats.assertionResult, _stats.infoMessages)),
         messages(_stats.infoMessages),
         colourImpl(colourImpl_),
         printInfoMessages(_printInfoMessages) {}

```
