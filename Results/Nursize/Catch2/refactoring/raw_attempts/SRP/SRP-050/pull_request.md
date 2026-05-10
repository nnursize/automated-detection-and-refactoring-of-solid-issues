# Refactor SRP-050 (SRP): The ConsoleAssertionPrinter class is responsible for interpreting assertion r...

**Status:** `applied_unverified`  
**Branch:** `refactor/SRP-050` -> `main`  
**Head commit:** `35e191d1c2f08e9b285da19cba8ba76d54d727e1`  
**LLM finish:** `FinishReason.STOP` (prompt 8115, completion 2737)  

## Detected issue

- **File**: `src/catch2/reporters/catch_reporter_console.cpp`
- **Entity**: `ConsoleAssertionPrinter` (class)
- **Lines (at detection time)**: L45–L193
- **Severity**: high
- **Confidence**: detected by 2 scan(s)

**Description.** The ConsoleAssertionPrinter class is responsible for interpreting assertion results, applying complex text layout, and rendering the output to a console stream.

**Reasoning.** The constructor contains extensive logic to categorize assertion results and determine presentation metadata (e.g., `passOrFail` string, `messageLabel`, `colour`). The `print` methods then use this metadata, along with `TextFlow::Column` for sophisticated text layout (indentation, line wrapping), to render the final output to `std::ostream`. This combines result interpretation, text formatting/layout, and output rendering, giving it multiple distinct reasons to change.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `src/catch2/reporters/catch_reporter_console.cpp`

**Summary.** Extract assertion result categorization logic from ConsoleAssertionPrinter

**Rationale.** The ConsoleAssertionPrinter class was violating SRP by mixing result categorization logic (determining labels and colours) with rendering logic. I extracted the categorization into a separate helper struct 'AssertionMetadata' to separate the 'what' (metadata) from the 'how' (rendering).

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `src/catch2/reporters/catch_reporter_console.cpp` (150-line block → 137-line replacement)

**Replaces:**

```cpp
// Formatter impl for ConsoleReporter
class ConsoleAssertionPrinter {
public:
    ConsoleAssertionPrinter& operator= (ConsoleAssertionPrinter const&) = delete;
    ConsoleAssertionPrinter(ConsoleAssertionPrinter const&) = delete;
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
... (90 more line(s) truncated)
```

**With:**

```cpp
// Formatter impl for ConsoleReporter
struct AssertionMetadata {
    Colour::Code colour = Colour::None;
    StringRef passOrFail;
    StringRef messageLabel;

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
... (77 more line(s) truncated)
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/catch2/reporters/catch_reporter_console.cpp` | 565 → 554 | 21 → 21 | 5.48 → 5.43 | 95 → 94 | 0 → 0 |

## Diff

```diff
diff --git a/src/catch2/reporters/catch_reporter_console.cpp b/src/catch2/reporters/catch_reporter_console.cpp
index acb4ae8..1768bc7 100644
--- a/src/catch2/reporters/catch_reporter_console.cpp
+++ b/src/catch2/reporters/catch_reporter_console.cpp
@@ -42,27 +42,18 @@ namespace Catch {
 namespace {
 
 // Formatter impl for ConsoleReporter
-class ConsoleAssertionPrinter {
-public:
-    ConsoleAssertionPrinter& operator= (ConsoleAssertionPrinter const&) = delete;
-    ConsoleAssertionPrinter(ConsoleAssertionPrinter const&) = delete;
-    ConsoleAssertionPrinter(std::ostream& _stream, AssertionStats const& _stats, ColourImpl* colourImpl_, bool _printInfoMessages)
-        : stream(_stream),
-        stats(_stats),
-        result(_stats.assertionResult),
-        colour(Colour::None),
-        messages(_stats.infoMessages),
-        colourImpl(colourImpl_),
-        printInfoMessages(_printInfoMessages) {
+struct AssertionMetadata {
+    Colour::Code colour = Colour::None;
+    StringRef passOrFail;
+    StringRef messageLabel;
+
+    AssertionMetadata(AssertionResult const& result, std::vector<MessageInfo> const& messages) {
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
@@ -72,25 +63,15 @@ public:
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
@@ -111,20 +92,15 @@ public:
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
@@ -133,6 +109,20 @@ public:
             break;
         }
     }
+};
+
+class ConsoleAssertionPrinter {
+public:
+    ConsoleAssertionPrinter& operator= (ConsoleAssertionPrinter const&) = delete;
+    ConsoleAssertionPrinter(ConsoleAssertionPrinter const&) = delete;
+    ConsoleAssertionPrinter(std::ostream& _stream, AssertionStats const& _stats, ColourImpl* colourImpl_, bool _printInfoMessages)
+        : stream(_stream),
+        stats(_stats),
+        result(_stats.assertionResult),
+        metadata(_stats.assertionResult, _stats.infoMessages),
+        messages(_stats.infoMessages),
+        colourImpl(colourImpl_),
+        printInfoMessages(_printInfoMessages) {}
 
     void print() const {
         printSourceInfo();
@@ -148,8 +138,8 @@ public:
 
 private:
     void printResultType() const {
-        if (!passOrFail.empty()) {
-            stream << colourImpl->guardColour(colour) << passOrFail << ":\n";
+        if (!metadata.passOrFail.empty()) {
+            stream << colourImpl->guardColour(metadata.colour) << metadata.passOrFail << ":\n";
         }
     }
     void printOriginalExpression() const {
@@ -168,10 +158,9 @@ private:
         }
     }
     void printMessage() const {
-        if (!messageLabel.empty())
-            stream << messageLabel << ':' << '\n';
+        if (!metadata.messageLabel.empty())
+            stream << metadata.messageLabel << ':' << '\n';
         for (auto const& msg : messages) {
-            // If this assertion is a warning ignore any INFO messages
             if (printInfoMessages || msg.type != ResultWas::Info)
                 stream << TextFlow::Column(msg.message).indent(2) << '\n';
         }
@@ -184,9 +173,7 @@ private:
     std::ostream& stream;
     AssertionStats const& stats;
     AssertionResult const& result;
-    Colour::Code colour;
-    StringRef passOrFail;
-    StringRef messageLabel;
+    AssertionMetadata metadata;
     std::vector<MessageInfo> const& messages;
     ColourImpl* colourImpl;
     bool printInfoMessages;

```
