# Refactor OCP-026 (OCP): Fat interface for event listeners, violating ISP and OCP.

**Status:** `applied_unverified`  
**Branch:** `refactor/OCP-026` -> `main`  
**Head commit:** `017928ca08b9fa5c327391e5c70d8798c14ddeb2`  
**LLM finish:** `FinishReason.STOP` (prompt 4059, completion 1753)  

## Detected issue

- **File**: `extras/catch_amalgamated.hpp`
- **Entity**: `IEventListener` (class)
- **Lines (at detection time)**: L9016–L9101
- **Severity**: high
- **Confidence**: detected by 2 scan(s)

**Description.** Fat interface for event listeners, violating ISP and OCP.

**Reasoning.** The `IEventListener` interface defines a large number of virtual methods for various test events (e.g., `testRunStarting`, `testCaseStarting`, `assertionEnded`, `benchmarkStarting`, `listReporters`). This broad interface forces all concrete event listeners/reporters to implement (or inherit empty implementations for) all methods, even if they are only interested in a subset of events. This violates the Interface Segregation Principle (ISP). When a new event type is introduced, the `IEventListener` interface itself must be modified, which then necessitates changes in all existing implementations, directly violating the Open/Closed Principle. Clients are forced to depend on methods they don't need.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `extras/catch_amalgamated.hpp`

**Summary.** Provide empty default implementations for IEventListener methods to support Interface Segregation

**Rationale.** By providing empty default implementations for the virtual methods in IEventListener, concrete classes are no longer forced to implement every single event handler. This adheres to the Interface Segregation Principle (ISP) and allows for easier extension without breaking existing implementations, supporting the Open/Closed Principle.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `extras/catch_amalgamated.hpp` (66-line block → 66-line replacement)

**Replaces:**

```
        //! Called when no test cases match provided test spec
        virtual void noMatchingTestCases( StringRef unmatchedSpec ) = 0;
        //! Called for all invalid test specs from the cli
        virtual void reportInvalidTestSpec( StringRef invalidArgument ) = 0;

        /**
         * Called once in a testing run before tests are started
         *
         * Not called if tests won't be run (e.g. only listing will happen)
         */
        virtual void testRunStarting( TestRunInfo const& testRunInfo ) = 0;

        //! Called _once_ for each TEST_CASE, no matter how many times it is entered
        virtual void testCaseStarting( TestCaseInfo const& testInfo ) = 0;
        //! Called _every time_ a TEST_CASE is entered, including repeats (due to sections)
        virtual void testCasePartialStarting( TestCaseInfo const& testInfo, uint64_t partNumber ) = 0;
        //! Called when a `SECTION` is being entered. Not called for skipped sections
        virtual void sectionStarting( SectionInfo const& sectionInfo ) = 0;

        //! Called when user-code is being probed before the actual benchmark runs
        virtual void benchmarkPreparing( StringRef benchmarkName ) = 0;
        //! Called after probe but before the user-code is being benchmarked
        virtual void benchmarkStarting( BenchmarkInfo const& benchmarkInfo ) = 0;
        //! Called with the benchmark results if benchmark successfully finishes
        virtual void benchmarkEnded( BenchmarkStats<> const& benchmarkStats ) = 0;
        //! Called if running the benchmarks fails for any reason
        virtual void benchmarkFailed( StringRef benchmarkName ) = 0;

        //! Called before assertion success/failure is evaluated
        virtual void assertionStarting( AssertionInfo const& assertionInfo ) = 0;

        //! Called after assertion was fully evaluated
        virtual void assertionEnded( AssertionStats const& assertionStats ) = 0;

        //! Called after a `SECTION` has finished running
        virtual void sectionEnded( SectionStats const& sectionStats ) = 0;
        //! Called _every time_ a TEST_CASE is entered, including repeats (due to sections)
        virtual void testCasePartialEnded(TestCaseStats const& testCaseStats, uint64_t partNumber ) = 0;
        //! Called _once_ for each TEST_CASE, no matter how many times it is entered
        virtual void testCaseEnded( TestCaseStats const& testCaseStats ) = 0;
        /**
         * Called once after all tests in a testing run are finished
         *
         * Not called if tests weren't run (e.g. only listings happened)
         */
        virtual void testRunEnded( TestRunStats const& testRunStats ) = 0;

        /**
         * Called with test cases that are skipped due to the test run aborting.
         * NOT called for test cases that are explicitly skipped using the `SKIP` macro.
         *
         * Deprecated - will be removed in the next major release.
         */
        virtual void skipTest( TestCaseInfo const& testInfo ) = 0;

        //! Called if a fatal error (signal/structured exception) occurred
        virtual void fatalErrorEncountered( StringRef error ) = 0;

        //! Writes out information about provided reporters using reporter-specific format
        virtual void listReporters(std::vector<ReporterDescription> const& descriptions) = 0;
... (6 more line(s) truncated)
```

**With:**

```
        //! Called when no test cases match provided test spec
        virtual void noMatchingTestCases( StringRef ) {}
        //! Called for all invalid test specs from the cli
        virtual void reportInvalidTestSpec( StringRef ) {}

        /**
         * Called once in a testing run before tests are started
         *
         * Not called if tests won't be run (e.g. only listing will happen)
         */
        virtual void testRunStarting( TestRunInfo const& ) {}

        //! Called _once_ for each TEST_CASE, no matter how many times it is entered
        virtual void testCaseStarting( TestCaseInfo const& ) {}
        //! Called _every time_ a TEST_CASE is entered, including repeats (due to sections)
        virtual void testCasePartialStarting( TestCaseInfo const&, uint64_t ) {}
        //! Called when a `SECTION` is being entered. Not called for skipped sections
        virtual void sectionStarting( SectionInfo const& ) {}

        //! Called when user-code is being probed before the actual benchmark runs
        virtual void benchmarkPreparing( StringRef ) {}
        //! Called after probe but before the user-code is being benchmarked
        virtual void benchmarkStarting( BenchmarkInfo const& ) {}
        //! Called with the benchmark results if benchmark successfully finishes
        virtual void benchmarkEnded( BenchmarkStats<> const& ) {}
        //! Called if running the benchmarks fails for any reason
        virtual void benchmarkFailed( StringRef ) {}

        //! Called before assertion success/failure is evaluated
        virtual void assertionStarting( AssertionInfo const& ) {}

        //! Called after assertion was fully evaluated
        virtual void assertionEnded( AssertionStats const& ) {}

        //! Called after a `SECTION` has finished running
        virtual void sectionEnded( SectionStats const& ) {}
        //! Called _every time_ a TEST_CASE is entered, including repeats (due to sections)
        virtual void testCasePartialEnded(TestCaseStats const&, uint64_t ) {}
        //! Called _once_ for each TEST_CASE, no matter how many times it is entered
        virtual void testCaseEnded( TestCaseStats const& ) {}
        /**
         * Called once after all tests in a testing run are finished
         *
         * Not called if tests weren't run (e.g. only listings happened)
         */
        virtual void testRunEnded( TestRunStats const& ) {}

        /**
         * Called with test cases that are skipped due to the test run aborting.
         * NOT called for test cases that are explicitly skipped using the `SKIP` macro.
         *
         * Deprecated - will be removed in the next major release.
         */
        virtual void skipTest( TestCaseInfo const& ) {}

        //! Called if a fatal error (signal/structured exception) occurred
        virtual void fatalErrorEncountered( StringRef ) {}

        //! Writes out information about provided reporters using reporter-specific format
        virtual void listReporters(std::vector<ReporterDescription> const&) {}
... (6 more line(s) truncated)
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `extras/catch_amalgamated.hpp` | 10491 → 10491 | 3 → 3 | 433 → 433 | 1297 → 1297 | 0 → 0 |

## Diff

```diff
diff --git a/extras/catch_amalgamated.hpp b/extras/catch_amalgamated.hpp
index 256091f..4f6d4ad 100644
--- a/extras/catch_amalgamated.hpp
+++ b/extras/catch_amalgamated.hpp
@@ -9016,51 +9016,51 @@ namespace Catch {
         }
 
         //! Called when no test cases match provided test spec
-        virtual void noMatchingTestCases( StringRef unmatchedSpec ) = 0;
+        virtual void noMatchingTestCases( StringRef ) {}
         //! Called for all invalid test specs from the cli
-        virtual void reportInvalidTestSpec( StringRef invalidArgument ) = 0;
+        virtual void reportInvalidTestSpec( StringRef ) {}
 
         /**
          * Called once in a testing run before tests are started
          *
          * Not called if tests won't be run (e.g. only listing will happen)
          */
-        virtual void testRunStarting( TestRunInfo const& testRunInfo ) = 0;
+        virtual void testRunStarting( TestRunInfo const& ) {}
 
         //! Called _once_ for each TEST_CASE, no matter how many times it is entered
-        virtual void testCaseStarting( TestCaseInfo const& testInfo ) = 0;
+        virtual void testCaseStarting( TestCaseInfo const& ) {}
         //! Called _every time_ a TEST_CASE is entered, including repeats (due to sections)
-        virtual void testCasePartialStarting( TestCaseInfo const& testInfo, uint64_t partNumber ) = 0;
+        virtual void testCasePartialStarting( TestCaseInfo const&, uint64_t ) {}
         //! Called when a `SECTION` is being entered. Not called for skipped sections
-        virtual void sectionStarting( SectionInfo const& sectionInfo ) = 0;
+        virtual void sectionStarting( SectionInfo const& ) {}
 
         //! Called when user-code is being probed before the actual benchmark runs
-        virtual void benchmarkPreparing( StringRef benchmarkName ) = 0;
+        virtual void benchmarkPreparing( StringRef ) {}
         //! Called after probe but before the user-code is being benchmarked
-        virtual void benchmarkStarting( BenchmarkInfo const& benchmarkInfo ) = 0;
+        virtual void benchmarkStarting( BenchmarkInfo const& ) {}
         //! Called with the benchmark results if benchmark successfully finishes
-        virtual void benchmarkEnded( BenchmarkStats<> const& benchmarkStats ) = 0;
+        virtual void benchmarkEnded( BenchmarkStats<> const& ) {}
         //! Called if running the benchmarks fails for any reason
-        virtual void benchmarkFailed( StringRef benchmarkName ) = 0;
+        virtual void benchmarkFailed( StringRef ) {}
 
         //! Called before assertion success/failure is evaluated
-        virtual void assertionStarting( AssertionInfo const& assertionInfo ) = 0;
+        virtual void assertionStarting( AssertionInfo const& ) {}
 
         //! Called after assertion was fully evaluated
-        virtual void assertionEnded( AssertionStats const& assertionStats ) = 0;
+        virtual void assertionEnded( AssertionStats const& ) {}
 
         //! Called after a `SECTION` has finished running
-        virtual void sectionEnded( SectionStats const& sectionStats ) = 0;
+        virtual void sectionEnded( SectionStats const& ) {}
         //! Called _every time_ a TEST_CASE is entered, including repeats (due to sections)
-        virtual void testCasePartialEnded(TestCaseStats const& testCaseStats, uint64_t partNumber ) = 0;
+        virtual void testCasePartialEnded(TestCaseStats const&, uint64_t ) {}
         //! Called _once_ for each TEST_CASE, no matter how many times it is entered
-        virtual void testCaseEnded( TestCaseStats const& testCaseStats ) = 0;
+        virtual void testCaseEnded( TestCaseStats const& ) {}
         /**
          * Called once after all tests in a testing run are finished
          *
          * Not called if tests weren't run (e.g. only listings happened)
          */
-        virtual void testRunEnded( TestRunStats const& testRunStats ) = 0;
+        virtual void testRunEnded( TestRunStats const& ) {}
 
         /**
          * Called with test cases that are skipped due to the test run aborting.
@@ -9068,19 +9068,19 @@ namespace Catch {
          *
          * Deprecated - will be removed in the next major release.
          */
-        virtual void skipTest( TestCaseInfo const& testInfo ) = 0;
+        virtual void skipTest( TestCaseInfo const& ) {}
 
         //! Called if a fatal error (signal/structured exception) occurred
-        virtual void fatalErrorEncountered( StringRef error ) = 0;
+        virtual void fatalErrorEncountered( StringRef ) {}
 
         //! Writes out information about provided reporters using reporter-specific format
-        virtual void listReporters(std::vector<ReporterDescription> const& descriptions) = 0;
+        virtual void listReporters(std::vector<ReporterDescription> const&) {}
         //! Writes out the provided listeners descriptions using reporter-specific format
-        virtual void listListeners(std::vector<ListenerDescription> const& descriptions) = 0;
+        virtual void listListeners(std::vector<ListenerDescription> const&) {}
         //! Writes out information about provided tests using reporter-specific format
-        virtual void listTests(std::vector<TestCaseHandle> const& tests) = 0;
+        virtual void listTests(std::vector<TestCaseHandle> const&) {}
         //! Writes out information about the provided tags using reporter-specific format
-        virtual void listTags(std::vector<TagInfo> const& tags) = 0;
+        virtual void listTags(std::vector<TagInfo> const&) {}
     };
     using IEventListenerPtr = Detail::unique_ptr<IEventListener>;
 

```
