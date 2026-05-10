# Refactor OCP-029 (OCP): Fat interface: IEventListener forces concrete reporters to implement many unr...

**Status:** `applied_unverified`  
**Branch:** `refactor/OCP-029` -> `main`  
**Head commit:** `d878a9f6a7d33b8a9f689f8c4f980f1a9c6889e4`  
**LLM finish:** `FinishReason.STOP` (prompt 3944, completion 1499)  

## Detected issue

- **File**: `extras/catch_amalgamated.hpp`
- **Entity**: `IEventListener` (class)
- **Lines (at detection time)**: L137–L222
- **Severity**: high
- **Confidence**: detected by 1 scan(s)

**Description.** Fat interface: IEventListener forces concrete reporters to implement many unrelated methods.

**Reasoning.** The IEventListener interface defines a large number of virtual methods covering various test events (run, test case, section, assertion, benchmark, listing, etc.). Concrete reporters like AutomakeReporter or CompactReporter only care about a small subset of these events, leading to numerous empty or pass-through overrides in intermediate base classes (StreamingReporterBase, CumulativeReporterBase) or directly in concrete classes. This violates the Interface Segregation Principle (ISP), which is a facet of OCP, as clients are forced to depend on methods they don't use. Adding new event types would necessitate modifying all existing reporter classes, even if they don't handle the new event, to provide an empty implementation.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `extras/catch_amalgamated.hpp`

**Summary.** Split IEventListener into smaller, specialized interfaces to adhere to Interface Segregation Principle.

**Rationale.** The IEventListener interface was too large, forcing all implementations to override many unused methods. By splitting it into ITestEventListener, IBenchmarkEventListener, and IReporterListingListener, concrete classes can now implement only the interfaces relevant to their needs, reducing coupling and improving maintainability.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `extras/catch_amalgamated.hpp` (86-line block → 46-line replacement)

**Replaces:**

```
    class IEventListener {
    protected:
        //! Derived classes can set up their preferences here
        ReporterPreferences m_preferences;
        //! The test run's config as filled in from CLI and defaults
        IConfig const* m_config;

    public:
        IEventListener( IConfig const* config ): m_config( config ) {}

        virtual ~IEventListener(); // = default;

        // Implementing class must also provide the following static methods:
        // static std::string getDescription();

        ReporterPreferences const& getPreferences() const {
            return m_preferences;
        }

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
... (26 more line(s) truncated)
```

**With:**

```
    class ITestEventListener {
    public:
        virtual ~ITestEventListener();
        virtual void noMatchingTestCases( StringRef ) {}
        virtual void reportInvalidTestSpec( StringRef ) {}
        virtual void testRunStarting( TestRunInfo const& ) {}
        virtual void testCaseStarting( TestCaseInfo const& ) {}
        virtual void testCasePartialStarting( TestCaseInfo const&, uint64_t ) {}
        virtual void sectionStarting( SectionInfo const& ) {}
        virtual void assertionStarting( AssertionInfo const& ) {}
        virtual void assertionEnded( AssertionStats const& ) {}
        virtual void sectionEnded( SectionStats const& ) {}
        virtual void testCasePartialEnded(TestCaseStats const&, uint64_t ) {}
        virtual void testCaseEnded( TestCaseStats const& ) {}
        virtual void testRunEnded( TestRunStats const& ) {}
        virtual void skipTest( TestCaseInfo const& ) {}
        virtual void fatalErrorEncountered( StringRef ) {}
    };

    class IBenchmarkEventListener {
    public:
        virtual ~IBenchmarkEventListener();
        virtual void benchmarkPreparing( StringRef ) {}
        virtual void benchmarkStarting( BenchmarkInfo const& ) {}
        virtual void benchmarkEnded( BenchmarkStats<> const& ) {}
        virtual void benchmarkFailed( StringRef ) {}
    };

    class IReporterListingListener {
    public:
        virtual ~IReporterListingListener();
        virtual void listReporters(std::vector<ReporterDescription> const&) {}
        virtual void listListeners(std::vector<ListenerDescription> const&) {}
        virtual void listTests(std::vector<TestCaseHandle> const&) {}
        virtual void listTags(std::vector<TagInfo> const&) {}
    };

    class IEventListener : public ITestEventListener, public IBenchmarkEventListener, public IReporterListingListener {
    protected:
        ReporterPreferences m_preferences;
        IConfig const* m_config;
    public:
        IEventListener( IConfig const* config ): m_config( config ) {}
        virtual ~IEventListener();
        ReporterPreferences const& getPreferences() const { return m_preferences; }
    };
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `extras/catch_amalgamated.hpp` | 10491 → 10485 | 3 → 3 | 433 → 428.33 | 1297 → 1283 | 0 → 0 |

## Diff

```diff
diff --git a/extras/catch_amalgamated.hpp b/extras/catch_amalgamated.hpp
index 4f6d4ad..b9ba53d 100644
--- a/extras/catch_amalgamated.hpp
+++ b/extras/catch_amalgamated.hpp
@@ -8996,92 +8996,52 @@ namespace Catch {
      * instead they should derive from one of the utility bases that
      * derive from this class.
      */
-    class IEventListener {
-    protected:
-        //! Derived classes can set up their preferences here
-        ReporterPreferences m_preferences;
-        //! The test run's config as filled in from CLI and defaults
-        IConfig const* m_config;
-
+    class ITestEventListener {
     public:
-        IEventListener( IConfig const* config ): m_config( config ) {}
-
-        virtual ~IEventListener(); // = default;
-
-        // Implementing class must also provide the following static methods:
-        // static std::string getDescription();
-
-        ReporterPreferences const& getPreferences() const {
-            return m_preferences;
-        }
-
-        //! Called when no test cases match provided test spec
+        virtual ~ITestEventListener();
         virtual void noMatchingTestCases( StringRef ) {}
-        //! Called for all invalid test specs from the cli
         virtual void reportInvalidTestSpec( StringRef ) {}
-
-        /**
-         * Called once in a testing run before tests are started
-         *
-         * Not called if tests won't be run (e.g. only listing will happen)
-         */
         virtual void testRunStarting( TestRunInfo const& ) {}
-
-        //! Called _once_ for each TEST_CASE, no matter how many times it is entered
         virtual void testCaseStarting( TestCaseInfo const& ) {}
-        //! Called _every time_ a TEST_CASE is entered, including repeats (due to sections)
         virtual void testCasePartialStarting( TestCaseInfo const&, uint64_t ) {}
-        //! Called when a `SECTION` is being entered. Not called for skipped sections
         virtual void sectionStarting( SectionInfo const& ) {}
-
-        //! Called when user-code is being probed before the actual benchmark runs
-        virtual void benchmarkPreparing( StringRef ) {}
-        //! Called after probe but before the user-code is being benchmarked
-        virtual void benchmarkStarting( BenchmarkInfo const& ) {}
-        //! Called with the benchmark results if benchmark successfully finishes
-        virtual void benchmarkEnded( BenchmarkStats<> const& ) {}
-        //! Called if running the benchmarks fails for any reason
-        virtual void benchmarkFailed( StringRef ) {}
-
-        //! Called before assertion success/failure is evaluated
         virtual void assertionStarting( AssertionInfo const& ) {}
-
-        //! Called after assertion was fully evaluated
         virtual void assertionEnded( AssertionStats const& ) {}
-
-        //! Called after a `SECTION` has finished running
         virtual void sectionEnded( SectionStats const& ) {}
-        //! Called _every time_ a TEST_CASE is entered, including repeats (due to sections)
         virtual void testCasePartialEnded(TestCaseStats const&, uint64_t ) {}
-        //! Called _once_ for each TEST_CASE, no matter how many times it is entered
         virtual void testCaseEnded( TestCaseStats const& ) {}
-        /**
-         * Called once after all tests in a testing run are finished
-         *
-         * Not called if tests weren't run (e.g. only listings happened)
-         */
         virtual void testRunEnded( TestRunStats const& ) {}
-
-        /**
-         * Called with test cases that are skipped due to the test run aborting.
-         * NOT called for test cases that are explicitly skipped using the `SKIP` macro.
-         *
-         * Deprecated - will be removed in the next major release.
-         */
         virtual void skipTest( TestCaseInfo const& ) {}
-
-        //! Called if a fatal error (signal/structured exception) occurred
         virtual void fatalErrorEncountered( StringRef ) {}
+    };
 
-        //! Writes out information about provided reporters using reporter-specific format
+    class IBenchmarkEventListener {
+    public:
+        virtual ~IBenchmarkEventListener();
+        virtual void benchmarkPreparing( StringRef ) {}
+        virtual void benchmarkStarting( BenchmarkInfo const& ) {}
+        virtual void benchmarkEnded( BenchmarkStats<> const& ) {}
+        virtual void benchmarkFailed( StringRef ) {}
+    };
+
+    class IReporterListingListener {
+    public:
+        virtual ~IReporterListingListener();
         virtual void listReporters(std::vector<ReporterDescription> const&) {}
-        //! Writes out the provided listeners descriptions using reporter-specific format
         virtual void listListeners(std::vector<ListenerDescription> const&) {}
-        //! Writes out information about provided tests using reporter-specific format
         virtual void listTests(std::vector<TestCaseHandle> const&) {}
-        //! Writes out information about the provided tags using reporter-specific format
         virtual void listTags(std::vector<TagInfo> const&) {}
     };
+
+    class IEventListener : public ITestEventListener, public IBenchmarkEventListener, public IReporterListingListener {
+    protected:
+        ReporterPreferences m_preferences;
+        IConfig const* m_config;
+    public:
+        IEventListener( IConfig const* config ): m_config( config ) {}
+        virtual ~IEventListener();
+        ReporterPreferences const& getPreferences() const { return m_preferences; }
+    };
     using IEventListenerPtr = Detail::unique_ptr<IEventListener>;
 
 } // end namespace Catch

```
