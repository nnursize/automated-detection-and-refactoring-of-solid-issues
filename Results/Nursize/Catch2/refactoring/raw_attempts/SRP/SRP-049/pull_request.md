# Refactor SRP-049 (SRP): The ConsoleAssertionPrinter class is responsible for interpreting assertion r...

**Status:** `patch_failed`  
**Branch:** `refactor/SRP-049` -> `main`  
**Head commit:** `54a5882f307ef215f4ccad5da24858aad03b7fbc`  
**LLM finish:** `FinishReason.STOP` (prompt 4534, completion 2629)  

## Detected issue

- **File**: `extras/catch_amalgamated.cpp`
- **Entity**: `ConsoleAssertionPrinter` (class)
- **Lines (at detection time)**: L9278–L9426
- **Severity**: high
- **Confidence**: detected by 2 scan(s)

**Description.** The ConsoleAssertionPrinter class is responsible for interpreting assertion results, applying complex text layout, and rendering the output to a console stream.

**Reasoning.** The constructor contains extensive logic to categorize assertion results and determine presentation metadata (e.g., `passOrFail` string, `messageLabel`, `colour`). The `print` methods then use this metadata, along with `TextFlow::Column` for sophisticated text layout (indentation, line wrapping), to render the final output to `std::ostream`. This combines result interpretation, text formatting/layout, and output rendering, giving it multiple distinct reasons to change.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 3
- **Files modified** (1): `extras/catch_amalgamated.cpp`

**Summary.** Extract assertion result categorization logic from ConsoleAssertionPrinter

**Rationale.** The ConsoleAssertionPrinter was violating SRP by mixing result categorization logic (the constructor switch statement) with rendering logic. I extracted the categorization into a helper struct 'AssertionMetadata' to separate the 'what' (metadata) from the 'how' (rendering).

## Changes overview

_3 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `extras/catch_amalgamated.cpp` (94-line block → 86-line replacement)

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
... (34 more line(s) truncated)
```

**With:**

```cpp
// Formatter impl for ConsoleReporter
struct AssertionMetadata {
    Colour::Code colour = Colour::None;
    StringRef passOrFail;
    StringRef messageLabel;

    static AssertionMetadata create(AssertionResult const& result, std::vector<MessageInfo> const& messages) {
        AssertionMetadata meta;
        switch (result.getResultType()) {
        case ResultWas::Ok:
            meta.colour = Colour::Success;
            meta.passOrFail = "PASSED"_sr;
            if (messages.size() == 1) meta.messageLabel = "with message"_sr;
            else if (messages.size() > 1) meta.messageLabel = "with messages"_sr;
            break;
        case ResultWas::ExpressionFailed:
            if (result.isOk()) {
                meta.colour = Colour::Success;
                meta.passOrFail = "FAILED - but was ok"_sr;
            } else {
                meta.colour = Colour::Error;
                meta.passOrFail = "FAILED"_sr;
            }
            if (messages.size() == 1) meta.messageLabel = "with message"_sr;
            else if (messages.size() > 1) meta.messageLabel = "with messages"_sr;
            break;
        case ResultWas::ThrewException:
            meta.colour = Colour::Error;
            meta.passOrFail = "FAILED"_sr;
            if (messages.size() == 0) meta.messageLabel = "due to unexpected exception with "_sr;
            else if (messages.size() == 1) meta.messageLabel = "due to unexpected exception with message"_sr;
            else meta.messageLabel = "due to unexpected exception with messages"_sr;
            break;
        case ResultWas::FatalErrorCondition:
            meta.colour = Colour::Error;
            meta.passOrFail = "FAILED"_sr;
            meta.messageLabel = "due to a fatal error condition"_sr;
            break;
        case ResultWas::DidntThrowException:
            meta.colour = Colour::Error;
            meta.passOrFail = "FAILED"_sr;
            meta.messageLabel = "because no exception was thrown where one was expected"_sr;
            break;
        case ResultWas::Info:
            meta.messageLabel = "info"_sr;
            break;
        case ResultWas::Warning:
            meta.messageLabel = "warning"_sr;
            break;
        case ResultWas::ExplicitFailure:
            meta.passOrFail = "FAILED"_sr;
            meta.colour = Colour::Error;
            if (messages.size() == 1) meta.messageLabel = "explicitly with message"_sr;
            else if (messages.size() > 1) meta.messageLabel = "explicitly with messages"_sr;
            break;
        case ResultWas::ExplicitSkip:
            meta.colour = Colour::Skip;
            meta.passOrFail = "SKIPPED"_sr;
            if (messages.size() == 1) meta.messageLabel = "explicitly with message"_sr;
            else if (messages.size() > 1) meta.messageLabel = "explicitly with messages"_sr;
... (26 more line(s) truncated)
```

### 2. EDIT `extras/catch_amalgamated.cpp` (10-line block → 8-line replacement)

**Replaces:**

```cpp
    std::ostream& stream;
    AssertionStats const& stats;
    AssertionResult const& result;
    Colour::Code colour;
    StringRef passOrFail;
    StringRef messageLabel;
    std::vector<MessageInfo> const& messages;
    ColourImpl* colourImpl;
    bool printInfoMessages;
};
```

**With:**

```cpp
    std::ostream& stream;
    AssertionStats const& stats;
    AssertionResult const& result;
    std::vector<MessageInfo> const& messages;
    ColourImpl* colourImpl;
    bool printInfoMessages;
    AssertionMetadata meta;
};
```

### 3. EDIT `extras/catch_amalgamated.cpp` (29-line block → 29-line replacement)

**Replaces:**

```cpp
    void printResultType() const {
        if (!passOrFail.empty()) {
            stream << colourImpl->guardColour(colour) << passOrFail << ":\n";
        }
    }
    void printOriginalExpression() const {
        if (result.hasExpression()) {
            stream << colourImpl->guardColour( Colour::OriginalExpression )
                   << "  " << result.getExpressionInMacro() << '\n';
        }
    }
    void printReconstructedExpression() const {
        if (result.hasExpandedExpression()) {
            stream << "with expansion:\n";
            stream << colourImpl->guardColour( Colour::ReconstructedExpression )
                   << TextFlow::Column( result.getExpandedExpression() )
                          .indent( 2 )
                   << '\n';
        }
    }
    void printMessage() const {
        if (!messageLabel.empty())
            stream << messageLabel << ':' << '\n';
        for (auto const& msg : messages) {
            // If this assertion is a warning ignore any INFO messages
            if (printInfoMessages || msg.type != ResultWas::Info)
                stream << TextFlow::Column(msg.message).indent(2) << '\n';
        }
    }
```

**With:**

```cpp
    void printResultType() const {
        if (!meta.passOrFail.empty()) {
            stream << colourImpl->guardColour(meta.colour) << meta.passOrFail << ":\n";
        }
    }
    void printOriginalExpression() const {
        if (result.hasExpression()) {
            stream << colourImpl->guardColour( Colour::OriginalExpression )
                   << "  " << result.getExpressionInMacro() << '\n';
        }
    }
    void printReconstructedExpression() const {
        if (result.hasExpandedExpression()) {
            stream << "with expansion:\n";
            stream << colourImpl->guardColour( Colour::ReconstructedExpression )
                   << TextFlow::Column( result.getExpandedExpression() )
                          .indent( 2 )
                   << '\n';
        }
    }
    void printMessage() const {
        if (!meta.messageLabel.empty())
            stream << meta.messageLabel << ':' << '\n';
        for (auto const& msg : messages) {
            // If this assertion is a warning ignore any INFO messages
            if (printInfoMessages || msg.type != ResultWas::Info)
                stream << TextFlow::Column(msg.message).indent(2) << '\n';
        }
    }
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
index a4406d0..5ee50f8 100644
--- a/extras/catch_amalgamated.cpp
+++ b/extras/catch_amalgamated.cpp
@@ -9275,97 +9275,89 @@ namespace Catch {
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
+    static AssertionMetadata create(AssertionResult const& result, std::vector<MessageInfo> const& messages) {
+        AssertionMetadata meta;
         switch (result.getResultType()) {
         case ResultWas::Ok:
-            colour = Colour::Success;
-            passOrFail = "PASSED"_sr;
-            //if( result.hasMessage() )
-            if (messages.size() == 1)
-                messageLabel = "with message"_sr;
-            if (messages.size() > 1)
-                messageLabel = "with messages"_sr;
+            meta.colour = Colour::Success;
+            meta.passOrFail = "PASSED"_sr;
+            if (messages.size() == 1) meta.messageLabel = "with message"_sr;
+            else if (messages.size() > 1) meta.messageLabel = "with messages"_sr;
             break;
         case ResultWas::ExpressionFailed:
             if (result.isOk()) {
-                colour = Colour::Success;
-                passOrFail = "FAILED - but was ok"_sr;
+                meta.colour = Colour::Success;
+                meta.passOrFail = "FAILED - but was ok"_sr;
             } else {
-                colour = Colour::Error;
-                passOrFail = "FAILED"_sr;
+                meta.colour = Colour::Error;
+                meta.passOrFail = "FAILED"_sr;
             }
-            if (messages.size() == 1)
-                messageLabel = "with message"_sr;
-            if (messages.size() > 1)
-                messageLabel = "with messages"_sr;
+            if (messages.size() == 1) meta.messageLabel = "with message"_sr;
+            else if (messages.size() > 1) meta.messageLabel = "with messages"_sr;
             break;
         case ResultWas::ThrewException:
-            colour = Colour::Error;
-            passOrFail = "FAILED"_sr;
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
+            meta.colour = Colour::Error;
+            meta.passOrFail = "FAILED"_sr;
+            if (messages.size() == 0) meta.messageLabel = "due to unexpected exception with "_sr;
+            else if (messages.size() == 1) meta.messageLabel = "due to unexpected exception with message"_sr;
+            else meta.messageLabel = "due to unexpected exception with messages"_sr;
             break;
         case ResultWas::FatalErrorCondition:
-            colour = Colour::Error;
-            passOrFail = "FAILED"_sr;
-            messageLabel = "due to a fatal error condition"_sr;
+            meta.colour = Colour::Error;
+            meta.passOrFail = "FAILED"_sr;
+            meta.messageLabel = "due to a fatal error condition"_sr;
             break;
         case ResultWas::DidntThrowException:
-            colour = Colour::Error;
-            passOrFail = "FAILED"_sr;
-            messageLabel = "because no exception was thrown where one was expected"_sr;
+            meta.colour = Colour::Error;
+            meta.passOrFail = "FAILED"_sr;
+            meta.messageLabel = "because no exception was thrown where one was expected"_sr;
             break;
         case ResultWas::Info:
-            messageLabel = "info"_sr;
+            meta.messageLabel = "info"_sr;
             break;
         case ResultWas::Warning:
-            messageLabel = "warning"_sr;
+            meta.messageLabel = "warning"_sr;
             break;
         case ResultWas::ExplicitFailure:
-            passOrFail = "FAILED"_sr;
-            colour = Colour::Error;
-            if (messages.size() == 1)
-                messageLabel = "explicitly with message"_sr;
-            if (messages.size() > 1)
-                messageLabel = "explicitly with messages"_sr;
+            meta.passOrFail = "FAILED"_sr;
+            meta.colour = Colour::Error;
+            if (messages.size() == 1) meta.messageLabel = "explicitly with message"_sr;
+            else if (messages.size() > 1) meta.messageLabel = "explicitly with messages"_sr;
             break;
         case ResultWas::ExplicitSkip:
-            colour = Colour::Skip;
-            passOrFail = "SKIPPED"_sr;
-            if (messages.size() == 1)
-                messageLabel = "explicitly with message"_sr;
-            if (messages.size() > 1)
-                messageLabel = "explicitly with messages"_sr;
+            meta.colour = Colour::Skip;
+            meta.passOrFail = "SKIPPED"_sr;
+            if (messages.size() == 1) meta.messageLabel = "explicitly with message"_sr;
+            else if (messages.size() > 1) meta.messageLabel = "explicitly with messages"_sr;
             break;
-            // These cases are here to prevent compiler warnings
         case ResultWas::Unknown:
         case ResultWas::FailureBit:
         case ResultWas::Exception:
-            passOrFail = "** internal error **"_sr;
-            colour = Colour::Error;
+            meta.passOrFail = "** internal error **"_sr;
+            meta.colour = Colour::Error;
             break;
         }
+        return meta;
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
+        messages(_stats.infoMessages),
+        colourImpl(colourImpl_),
+        printInfoMessages(_printInfoMessages),
+        meta(AssertionMetadata::create(result, messages)) {}
 
     void print() const {
         printSourceInfo();
@@ -9381,8 +9373,8 @@ public:
 
 private:
     void printResultType() const {
-        if (!passOrFail.empty()) {
-            stream << colourImpl->guardColour(colour) << passOrFail << ":\n";
+        if (!meta.passOrFail.empty()) {
+            stream << colourImpl->guardColour(meta.colour) << meta.passOrFail << ":\n";
         }
     }
     void printOriginalExpression() const {
@@ -9401,8 +9393,8 @@ private:
         }
     }
     void printMessage() const {
-        if (!messageLabel.empty())
-            stream << messageLabel << ':' << '\n';
+        if (!meta.messageLabel.empty())
+            stream << meta.messageLabel << ':' << '\n';
         for (auto const& msg : messages) {
             // If this assertion is a warning ignore any INFO messages
             if (printInfoMessages || msg.type != ResultWas::Info)
@@ -9417,12 +9409,10 @@ private:
     std::ostream& stream;
     AssertionStats const& stats;
     AssertionResult const& result;
-    Colour::Code colour;
-    StringRef passOrFail;
-    StringRef messageLabel;
     std::vector<MessageInfo> const& messages;
     ColourImpl* colourImpl;
     bool printInfoMessages;
+    AssertionMetadata meta;
 };
 
 std::size_t makeRatio( std::uint64_t number, std::uint64_t total ) {

```
