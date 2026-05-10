# Refactor OCP-013 (OCP): The 'print' method contains a large switch statement dispatching on 'result.g...

**Status:** `patch_failed`  
**Branch:** `refactor/OCP-013` -> `main`  
**Head commit:** `9d2cba195b4200e785630e88fbdb6c70d42f83ef`  
**LLM finish:** `FinishReason.STOP` (prompt 3013, completion 1393)  

## Detected issue

- **File**: `extras/catch_amalgamated.cpp`
- **Entity**: `AssertionPrinter.print` (method)
- **Lines (at detection time)**: L9053–L9118
- **Severity**: high
- **Confidence**: detected by 4 scan(s)

**Description.** The 'print' method contains a large switch statement dispatching on 'result.getResultType()'.

**Reasoning.** Adding a new type of assertion result (new 'ResultWas::OfType' enum value) would require modifying this switch statement to add a new case, violating the Open/Closed Principle. This behavior should ideally be extended through polymorphism or a strategy pattern, where each result type knows how to print itself or has a dedicated printer strategy.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `extras/catch_amalgamated.cpp`

**Summary.** Refactor AssertionPrinter to use a dispatch table for result printing

**Rationale.** Replaced the large switch statement in AssertionPrinter::print with a static dispatch table mapping ResultWas types to handler functions. This allows adding new result types by updating the table rather than modifying the core logic, adhering to the Open/Closed Principle.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `extras/catch_amalgamated.cpp` (72-line block → 81-line replacement)

**Replaces:**

```cpp
    void print() {
        printSourceInfo();

        itMessage = messages.begin();

        switch (result.getResultType()) {
        case ResultWas::Ok:
            printResultType(Colour::ResultSuccess, compactPassedString);
            printOriginalExpression();
            printReconstructedExpression();
            if (!result.hasExpression())
                printRemainingMessages(Colour::None);
            else
                printRemainingMessages();
            break;
        case ResultWas::ExpressionFailed:
            if (result.isOk())
                printResultType(Colour::ResultSuccess, compactFailedString + " - but was ok"_sr);
            else
                printResultType(Colour::Error, compactFailedString);
            printOriginalExpression();
            printReconstructedExpression();
            printRemainingMessages();
            break;
        case ResultWas::ThrewException:
            printResultType(Colour::Error, compactFailedString);
            printIssue("unexpected exception with message:");
            printMessage();
            printExpressionWas();
            printRemainingMessages();
            break;
        case ResultWas::FatalErrorCondition:
            printResultType(Colour::Error, compactFailedString);
            printIssue("fatal error condition with message:");
            printMessage();
            printExpressionWas();
            printRemainingMessages();
            break;
        case ResultWas::DidntThrowException:
            printResultType(Colour::Error, compactFailedString);
            printIssue("expected exception, got none");
            printExpressionWas();
            printRemainingMessages();
            break;
        case ResultWas::Info:
            printResultType(Colour::None, "info"_sr);
            printMessage();
            printRemainingMessages();
            break;
        case ResultWas::Warning:
            printResultType(Colour::None, "warning"_sr);
            printMessage();
            printRemainingMessages();
            break;
        case ResultWas::ExplicitFailure:
            printResultType(Colour::Error, compactFailedString);
            printIssue("explicitly");
            printRemainingMessages(Colour::None);
            break;
        case ResultWas::ExplicitSkip:
... (12 more line(s) truncated)
```

**With:**

```cpp
    void print() {
        printSourceInfo();
        itMessage = messages.begin();

        using Handler = void (AssertionPrinter::*)();
        static const std::pair<ResultWas::OfType, Handler> handlers[] = {
            {ResultWas::Ok, &AssertionPrinter::printOk},
            {ResultWas::ExpressionFailed, &AssertionPrinter::printExpressionFailed},
            {ResultWas::ThrewException, &AssertionPrinter::printThrewException},
            {ResultWas::FatalErrorCondition, &AssertionPrinter::printFatalError},
            {ResultWas::DidntThrowException, &AssertionPrinter::printDidntThrow},
            {ResultWas::Info, &AssertionPrinter::printInfo},
            {ResultWas::Warning, &AssertionPrinter::printWarning},
            {ResultWas::ExplicitFailure, &AssertionPrinter::printExplicitFailure},
            {ResultWas::ExplicitSkip, &AssertionPrinter::printExplicitSkip}
        };

        for (auto const& h : handlers) {
            if (h.first == result.getResultType()) {
                (this->*h.second)();
                return;
            }
        }
        printResultType(Colour::Error, "** internal error **");
    }

    void printOk() {
        printResultType(Colour::ResultSuccess, compactPassedString);
        printOriginalExpression();
        printReconstructedExpression();
        printRemainingMessages(!result.hasExpression() ? Colour::None : Colour::None);
    }
    void printExpressionFailed() {
        if (result.isOk())
            printResultType(Colour::ResultSuccess, compactFailedString + " - but was ok"_sr);
        else
            printResultType(Colour::Error, compactFailedString);
        printOriginalExpression();
        printReconstructedExpression();
        printRemainingMessages();
    }
    void printThrewException() {
        printResultType(Colour::Error, compactFailedString);
        printIssue("unexpected exception with message:");
        printMessage();
        printExpressionWas();
        printRemainingMessages();
    }
    void printFatalError() {
        printResultType(Colour::Error, compactFailedString);
        printIssue("fatal error condition with message:");
        printMessage();
        printExpressionWas();
        printRemainingMessages();
    }
    void printDidntThrow() {
        printResultType(Colour::Error, compactFailedString);
        printIssue("expected exception, got none");
        printExpressionWas();
        printRemainingMessages();
... (21 more line(s) truncated)
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
index a4406d0..54221fc 100644
--- a/extras/catch_amalgamated.cpp
+++ b/extras/catch_amalgamated.cpp
@@ -9045,75 +9045,84 @@ public:
 
     void print() {
         printSourceInfo();
-
         itMessage = messages.begin();
 
-        switch (result.getResultType()) {
-        case ResultWas::Ok:
-            printResultType(Colour::ResultSuccess, compactPassedString);
-            printOriginalExpression();
-            printReconstructedExpression();
-            if (!result.hasExpression())
-                printRemainingMessages(Colour::None);
-            else
-                printRemainingMessages();
-            break;
-        case ResultWas::ExpressionFailed:
-            if (result.isOk())
-                printResultType(Colour::ResultSuccess, compactFailedString + " - but was ok"_sr);
-            else
-                printResultType(Colour::Error, compactFailedString);
-            printOriginalExpression();
-            printReconstructedExpression();
-            printRemainingMessages();
-            break;
-        case ResultWas::ThrewException:
-            printResultType(Colour::Error, compactFailedString);
-            printIssue("unexpected exception with message:");
-            printMessage();
-            printExpressionWas();
-            printRemainingMessages();
-            break;
-        case ResultWas::FatalErrorCondition:
-            printResultType(Colour::Error, compactFailedString);
-            printIssue("fatal error condition with message:");
-            printMessage();
-            printExpressionWas();
-            printRemainingMessages();
-            break;
-        case ResultWas::DidntThrowException:
-            printResultType(Colour::Error, compactFailedString);
-            printIssue("expected exception, got none");
-            printExpressionWas();
-            printRemainingMessages();
-            break;
-        case ResultWas::Info:
-            printResultType(Colour::None, "info"_sr);
-            printMessage();
-            printRemainingMessages();
-            break;
-        case ResultWas::Warning:
-            printResultType(Colour::None, "warning"_sr);
-            printMessage();
-            printRemainingMessages();
-            break;
-        case ResultWas::ExplicitFailure:
-            printResultType(Colour::Error, compactFailedString);
-            printIssue("explicitly");
-            printRemainingMessages(Colour::None);
-            break;
-        case ResultWas::ExplicitSkip:
-            printResultType(Colour::Skip, "skipped"_sr);
-            printMessage();
-            printRemainingMessages();
-            break;
-            // These cases are here to prevent compiler warnings
-        case ResultWas::Unknown:
-        case ResultWas::FailureBit:
-        case ResultWas::Exception:
-            printResultType(Colour::Error, "** internal error **");
-            break;
+        using Handler = void (AssertionPrinter::*)();
+        static const std::pair<ResultWas::OfType, Handler> handlers[] = {
+            {ResultWas::Ok, &AssertionPrinter::printOk},
+            {ResultWas::ExpressionFailed, &AssertionPrinter::printExpressionFailed},
+            {ResultWas::ThrewException, &AssertionPrinter::printThrewException},
+            {ResultWas::FatalErrorCondition, &AssertionPrinter::printFatalError},
+            {ResultWas::DidntThrowException, &AssertionPrinter::printDidntThrow},
+            {ResultWas::Info, &AssertionPrinter::printInfo},
+            {ResultWas::Warning, &AssertionPrinter::printWarning},
+            {ResultWas::ExplicitFailure, &AssertionPrinter::printExplicitFailure},
+            {ResultWas::ExplicitSkip, &AssertionPrinter::printExplicitSkip}
+        };
+
+        for (auto const& h : handlers) {
+            if (h.first == result.getResultType()) {
+                (this->*h.second)();
+                return;
+            }
         }
+        printResultType(Colour::Error, "** internal error **");
+    }
+
+    void printOk() {
+        printResultType(Colour::ResultSuccess, compactPassedString);
+        printOriginalExpression();
+        printReconstructedExpression();
+        printRemainingMessages(!result.hasExpression() ? Colour::None : Colour::None);
+    }
+    void printExpressionFailed() {
+        if (result.isOk())
+            printResultType(Colour::ResultSuccess, compactFailedString + " - but was ok"_sr);
+        else
+            printResultType(Colour::Error, compactFailedString);
+        printOriginalExpression();
+        printReconstructedExpression();
+        printRemainingMessages();
+    }
+    void printThrewException() {
+        printResultType(Colour::Error, compactFailedString);
+        printIssue("unexpected exception with message:");
+        printMessage();
+        printExpressionWas();
+        printRemainingMessages();
+    }
+    void printFatalError() {
+        printResultType(Colour::Error, compactFailedString);
+        printIssue("fatal error condition with message:");
+        printMessage();
+        printExpressionWas();
+        printRemainingMessages();
+    }
+    void printDidntThrow() {
+        printResultType(Colour::Error, compactFailedString);
+        printIssue("expected exception, got none");
+        printExpressionWas();
+        printRemainingMessages();
+    }
+    void printInfo() {
+        printResultType(Colour::None, "info"_sr);
+        printMessage();
+        printRemainingMessages();
+    }
+    void printWarning() {
+        printResultType(Colour::None, "warning"_sr);
+        printMessage();
+        printRemainingMessages();
+    }
+    void printExplicitFailure() {
+        printResultType(Colour::Error, compactFailedString);
+        printIssue("explicitly");
+        printRemainingMessages(Colour::None);
+    }
+    void printExplicitSkip() {
+        printResultType(Colour::Skip, "skipped"_sr);
+        printMessage();
+        printRemainingMessages();
     }
 
 private:

```
