# Refactor LSP-003 (LSP): Subclass enforces mandatory internal state-management side-effects on further...

**Status:** `applied_unverified`  
**Branch:** `refactor/LSP-003` -> `main`  
**Head commit:** `3649d6b45268af01f256aa903a2d14a1b3c3de44`  
**LLM finish:** `FinishReason.STOP` (prompt 3968, completion 476)  

## Detected issue

- **File**: `extras/catch_amalgamated.hpp`
- **Entity**: `Catch::CumulativeReporterBase` (class)
- **Lines (at detection time)**: L7668–L7727
- **Severity**: high
- **Confidence**: detected by 1 scan(s)

**Description.** Subclass enforces mandatory internal state-management side-effects on further subtypes.

**Reasoning.** The documentation for `CumulativeReporterBase` explicitly states that subclasses overriding testing-related member functions (like `sectionStarting` or `assertionEnded`) must call the base implementation to avoid breaking internal tree construction. This imposes a strict behavioral contract on subtypes that is not present in the parent `IEventListener` interface. If a subtype fails to call the base method, it violates the postconditions required for the correctness of the cumulative report (leading to UB), meaning the subtype is not safely substitutable for the base class.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `extras/catch_amalgamated.hpp`

**Summary.** Fix LSP violation in CumulativeReporterBase by making internal state management non-overridable

**Rationale.** The LSP violation occurred because subclasses were expected to call base methods to maintain internal state, which is an implementation detail that shouldn't be exposed as a contract. By splitting the public interface (non-virtual) from the internal implementation (private virtual hooks), we enforce the required state management while preventing subclasses from accidentally breaking the tree construction.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `extras/catch_amalgamated.hpp` (11-line block → 16-line replacement)

**Replaces:**

```
        void sectionStarting( SectionInfo const& sectionInfo ) override;

        void assertionStarting( AssertionInfo const& ) override {}

        void assertionEnded( AssertionStats const& assertionStats ) override;
        void sectionEnded( SectionStats const& sectionStats ) override;
        void testCasePartialEnded( TestCaseStats const&, uint64_t ) override {}
        void testCaseEnded( TestCaseStats const& testCaseStats ) override;
        void testRunEnded( TestRunStats const& testRunStats ) override;
        //! Customization point: called after last test finishes (testRunEnded has been handled)
        virtual void testRunEndedCumulative() = 0;
```

**With:**

```
        void sectionStarting( SectionInfo const& sectionInfo ) final;

        void assertionStarting( AssertionInfo const& ) final {}

        void assertionEnded( AssertionStats const& assertionStats ) final;
        void sectionEnded( SectionStats const& sectionStats ) final;
        void testCasePartialEnded( TestCaseStats const&, uint64_t ) final {}
        void testCaseEnded( TestCaseStats const& testCaseStats ) final;
        void testRunEnded( TestRunStats const& testRunStats ) final;

    protected:
        virtual void sectionStartingCumulative( SectionInfo const& ) {}
        virtual void assertionEndedCumulative( AssertionStats const& ) {}
        virtual void sectionEndedCumulative( SectionStats const& ) {}
        virtual void testCaseEndedCumulative( TestCaseStats const& ) {}
        virtual void testRunEndedCumulative( TestRunStats const& ) = 0;
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `extras/catch_amalgamated.hpp` | 10459 → 10464 | 3 → 3 | 425 → 425 | 1273 → 1273 | 0 → 0 |

## Diff

```diff
diff --git a/extras/catch_amalgamated.hpp b/extras/catch_amalgamated.hpp
index c9df2ab..7cf84e8 100644
--- a/extras/catch_amalgamated.hpp
+++ b/extras/catch_amalgamated.hpp
@@ -13540,17 +13540,22 @@ namespace Catch {
 
         void testCaseStarting( TestCaseInfo const& ) override {}
         void testCasePartialStarting( TestCaseInfo const&, uint64_t ) override {}
-        void sectionStarting( SectionInfo const& sectionInfo ) override;
+        void sectionStarting( SectionInfo const& sectionInfo ) final;
 
-        void assertionStarting( AssertionInfo const& ) override {}
+        void assertionStarting( AssertionInfo const& ) final {}
 
-        void assertionEnded( AssertionStats const& assertionStats ) override;
-        void sectionEnded( SectionStats const& sectionStats ) override;
-        void testCasePartialEnded( TestCaseStats const&, uint64_t ) override {}
-        void testCaseEnded( TestCaseStats const& testCaseStats ) override;
-        void testRunEnded( TestRunStats const& testRunStats ) override;
-        //! Customization point: called after last test finishes (testRunEnded has been handled)
-        virtual void testRunEndedCumulative() = 0;
+        void assertionEnded( AssertionStats const& assertionStats ) final;
+        void sectionEnded( SectionStats const& sectionStats ) final;
+        void testCasePartialEnded( TestCaseStats const&, uint64_t ) final {}
+        void testCaseEnded( TestCaseStats const& testCaseStats ) final;
+        void testRunEnded( TestRunStats const& testRunStats ) final;
+
+    protected:
+        virtual void sectionStartingCumulative( SectionInfo const& ) {}
+        virtual void assertionEndedCumulative( AssertionStats const& ) {}
+        virtual void sectionEndedCumulative( SectionStats const& ) {}
+        virtual void testCaseEndedCumulative( TestCaseStats const& ) {}
+        virtual void testRunEndedCumulative( TestRunStats const& ) = 0;
 
         void skipTest(TestCaseInfo const&) override {}
 

```
