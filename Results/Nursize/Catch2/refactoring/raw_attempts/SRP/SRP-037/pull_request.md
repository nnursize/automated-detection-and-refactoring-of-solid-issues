# Refactor SRP-037 (SRP): The IResultCapture interface provides a single point for reporting all types...

**Status:** `patch_failed`  
**Branch:** `refactor/SRP-037` -> `main`  
**Head commit:** `35e191d1c2f08e9b285da19cba8ba76d54d727e1`  
**LLM finish:** `FinishReason.STOP` (prompt 3861, completion 766)  

## Detected issue

- **File**: `extras/catch_amalgamated.hpp`
- **Entity**: `Catch::IResultCapture` (class)
- **Lines (at detection time)**: L725–L783
- **Severity**: high
- **Confidence**: detected by 1 scan(s)

**Description.** The IResultCapture interface provides a single point for reporting all types of events during a test run, including assertion outcomes, section lifecycle events, generator interactions, benchmark results, and general messages.

**Reasoning.** This interface is overly broad, encompassing many distinct event reporting responsibilities. Any change to the structure or content of assertion reporting, section management, or benchmark event notifications would require modifications to this single interface and all its implementers, violating SRP. It should be decomposed into smaller, more focused interfaces.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `extras/catch_amalgamated.hpp`

**Summary.** Decompose IResultCapture into specialized interfaces

**Rationale.** The IResultCapture interface was a 'God interface' violating the Single Responsibility Principle. By splitting it into IAssertionCapture, ISectionCapture, and IMessageCapture, we adhere to the Interface Segregation Principle and improve maintainability.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `extras/catch_amalgamated.hpp` (18-line block → 37-line replacement)

**Replaces:**

```
    class IResultCapture {
    public:
        virtual ~IResultCapture();

        virtual void notifyAssertionPassed( AssertionStats const& stats ) = 0;
        virtual void notifyAssertionFailed( AssertionStats const& stats ) = 0;
        virtual void notifyAssertionEnded( AssertionStats const& stats ) = 0;
        virtual void notifySectionEntered( SectionInfo const& sectionInfo, Counts& assertions ) = 0;
        virtual void notifySectionEnded( SectionStats const& sectionStats ) = 0;
        virtual void notifyGeneratorException( StringRef generatorName, std::exception_ptr exception ) = 0;
        virtual void notifyBenchmarkStarted( BenchmarkInfo const& info ) = 0;
        virtual void notifyBenchmarkEnded( BenchmarkStats<> const& stats ) = 0;
        virtual void notifyFatalErrorEncountered( StringRef message ) = 0;
        virtual void notifyMessage( MessageInfo const& message ) = 0;
        virtual void notifyMakeAssertionFailure( AssertionResultData const& resultData ) = 0;
        virtual bool notifyShouldSuppressFailure( StringRef className ) = 0;
        virtual bool notifySectionShouldBeSkipped( StringRef sectionName ) = 0;
    };
```

**With:**

```
    class IAssertionCapture {
    public:
        virtual ~IAssertionCapture();
        virtual void notifyAssertionPassed( AssertionStats const& stats ) = 0;
        virtual void notifyAssertionFailed( AssertionStats const& stats ) = 0;
        virtual void notifyAssertionEnded( AssertionStats const& stats ) = 0;
        virtual void notifyMakeAssertionFailure( AssertionResultData const& resultData ) = 0;
        virtual bool notifyShouldSuppressFailure( StringRef className ) = 0;
    };

    class ISectionCapture {
    public:
        virtual ~ISectionCapture();
        virtual void notifySectionEntered( SectionInfo const& sectionInfo, Counts& assertions ) = 0;
        virtual void notifySectionEnded( SectionStats const& sectionStats ) = 0;
        virtual bool notifySectionShouldBeSkipped( StringRef sectionName ) = 0;
    };

    class IMessageCapture {
    public:
        virtual ~IMessageCapture();
        virtual void notifyMessage( MessageInfo const& message ) = 0;
        virtual void notifyFatalErrorEncountered( StringRef message ) = 0;
        virtual void notifyGeneratorException( StringRef generatorName, std::exception_ptr exception ) = 0;
    };

    class IBenchmarkCapture {
    public:
        virtual ~IBenchmarkCapture();
        virtual void notifyBenchmarkStarted( BenchmarkInfo const& info ) = 0;
        virtual void notifyBenchmarkEnded( BenchmarkStats<> const& stats ) = 0;
    };

    class IResultCapture : public IAssertionCapture, public ISectionCapture, public IMessageCapture, public IBenchmarkCapture {
    public:
        ~IResultCapture() override = default;
    };
```

## Apply error

```
search_text not found in extras/catch_amalgamated.hpp (block 0)
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `extras/catch_amalgamated.hpp` | 10495 → - | 3 → - | 433.67 → - | 1299 → - | 0 → - |

## Diff

*(no diff — patch was not applied)*
