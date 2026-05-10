# Refactor ISP-005 (ISP): IGeneratorTracker interface has too many methods, potentially forcing impleme...

**Status:** `patch_failed`  
**Branch:** `refactor/ISP-005` -> `main`  
**Head commit:** `8c45ea2ed7ab55827fab32c5593ad112e5115d5d`  
**LLM finish:** `FinishReason.STOP` (prompt 2916, completion 572)  

## Detected issue

- **File**: `extras/catch_amalgamated.hpp`
- **Entity**: `IGeneratorTracker` (class)
- **Lines (at detection time)**: L10653–L10786
- **Severity**: medium
- **Confidence**: detected by 2 scan(s)

**Description.** IGeneratorTracker interface has too many methods, potentially forcing implementations to provide unused functionality.

**Reasoning.** The IGeneratorTracker interface appears to have a significant number of methods related to managing generators within the test framework. If a specific use case only requires a subset of these tracking functionalities, implementing the full interface would be unnecessary. This violates ISP by forcing clients to depend on methods they do not use. It could potentially be refactored into smaller interfaces for different aspects of generator tracking.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 2
- **Files modified** (1): `extras/catch_amalgamated.hpp`

**Summary.** Refactor IGeneratorTracker into smaller, focused interfaces to adhere to ISP.

**Rationale.** The IGeneratorTracker interface was monolithic. By splitting it into IGeneratorTracker (for lifecycle) and IGenerator (for value retrieval), clients only depend on the functionality they actually require.

## Changes overview

_2 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `extras/catch_amalgamated.hpp` (6-line block → 7-line replacement)

**Replaces:**

```
    class IGeneratorTracker;

    namespace Generators {
        class GeneratorUntypedBase;
        using GeneratorBasePtr = Catch::Detail::unique_ptr<GeneratorUntypedBase>;
    }
```

**With:**

```
    class IGeneratorTracker;
    class IGenerator;

    namespace Generators {
        class GeneratorUntypedBase;
        using GeneratorBasePtr = Catch::Detail::unique_ptr<GeneratorUntypedBase>;
    }
```

### 2. EDIT `extras/catch_amalgamated.hpp` (18-line block → 18-line replacement)

**Replaces:**

```
    class IResultCapture {
    public:
        virtual ~IResultCapture();

        virtual void notifyAssertionStarted( AssertionInfo const& info ) = 0;
        virtual bool sectionStarted( StringRef sectionName,
                                     SourceLineInfo const& sectionLineInfo,
                                     Counts& assertions ) = 0;
        virtual void sectionEnded( SectionEndInfo&& endInfo ) = 0;
        virtual void sectionEndedEarly( SectionEndInfo&& endInfo ) = 0;

        virtual IGeneratorTracker*
        acquireGeneratorTracker( StringRef generatorName,
                                 SourceLineInfo const& lineInfo ) = 0;
        virtual IGeneratorTracker*
        createGeneratorTracker( StringRef generatorName,
                                SourceLineInfo lineInfo,
                                Generators::GeneratorBasePtr&& generator ) = 0;
```

**With:**

```
    class IResultCapture {
    public:
        virtual ~IResultCapture();

        virtual void notifyAssertionStarted( AssertionInfo const& info ) = 0;
        virtual bool sectionStarted( StringRef sectionName,
                                     SourceLineInfo const& sectionLineInfo,
                                     Counts& assertions ) = 0;
        virtual void sectionEnded( SectionEndInfo&& endInfo ) = 0;
        virtual void sectionEndedEarly( SectionEndInfo&& endInfo ) = 0;

        virtual IGeneratorTracker*
        acquireGeneratorTracker( StringRef generatorName,
                                 SourceLineInfo const& lineInfo ) = 0;
        virtual IGeneratorTracker*
        createGeneratorTracker( StringRef generatorName,
                                SourceLineInfo lineInfo,
                                Generators::GeneratorBasePtr&& generator ) = 0;
```

## Apply error

```
search_text not found in extras/catch_amalgamated.hpp (block 0)
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `extras/catch_amalgamated.hpp` | 10515 → - | 3 → - | 426 → - | 1276 → - | 0 → - |

## Diff

*(no diff — patch was not applied)*
