# Refactor LSP-006 (LSP): The ITracker interface uses explicit methods to identify specific subtypes (i...

**Status:** `applied_unverified`  
**Branch:** `refactor/LSP-006` -> `main`  
**Head commit:** `c4fb8fdc2847e98069506246b6cf6bdb5e597f83`  
**LLM finish:** `FinishReason.STOP` (prompt 3640, completion 551)  

## Detected issue

- **File**: `extras/catch_amalgamated.hpp`
- **Entity**: `Catch::TestCaseTracking::ITracker` (class)
- **Lines (at detection time)**: L4712–L4762
- **Severity**: medium
- **Confidence**: detected by 2 scan(s)

**Description.** The ITracker interface uses explicit methods to identify specific subtypes (isSectionTracker, isGeneratorTracker).

**Reasoning.** By including isSectionTracker() and isGeneratorTracker() in the ITracker interface, the design forces the base class to be aware of its potential specializations. Callers are encouraged to use these methods to downcast or change behavior depending on the concrete subtype, which breaks the polymorphic contract where the base type should be sufficient for all interactions.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 2
- **Files modified** (1): `extras/catch_amalgamated.hpp`

**Summary.** Remove type-checking methods from ITracker interface to satisfy LSP

**Rationale.** The ITracker interface was leaking implementation details by providing methods to identify specific subtypes (isSectionTracker, isGeneratorTracker). Removing these methods forces the design to rely on polymorphism rather than downcasting or type-checking, adhering to the Liskov Substitution Principle.

## Changes overview

_2 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `extras/catch_amalgamated.hpp` (15-line block → 1-line replacement)

**Replaces:**

```
        /**
         * Returns true if the instance is a section tracker
         *
         * Subclasses should override to true if they are, replaces RTTI
         * for internal debug checks.
         */
        virtual bool isSectionTracker() const;
        /**
         * Returns true if the instance is a generator tracker
         *
         * Subclasses should override to true if they are, replaces RTTI
         * for internal debug checks.
         */
        virtual bool isGeneratorTracker() const;
    };
```

**With:**

```
    };
```

### 2. EDIT `extras/catch_amalgamated.hpp` (13-line block → 11-line replacement)

**Replaces:**

```
    class SectionTracker : public TrackerBase {
        std::vector<StringRef> m_filters;
        // Note that lifetime-wise we piggy back off the name stored in the `ITracker` parent`.
        // Currently it allocates owns the name, so this is safe. If it is later refactored
        // to not own the name, the name still has to outlive the `ITracker` parent, so
        // this should still be safe.
        StringRef m_trimmed_name;
    public:
        SectionTracker( NameAndLocation&& nameAndLocation, TrackerContext& ctx, ITracker* parent );

        bool isSectionTracker() const override;

        bool isComplete() const override;
```

**With:**

```
    class SectionTracker : public TrackerBase {
        std::vector<StringRef> m_filters;
        // Note that lifetime-wise we piggy back off the name stored in the `ITracker` parent`.
        // Currently it allocates owns the name, so this is safe. If it is later refactored
        // to not own the name, the name still has to outlive the `ITracker` parent, so
        // this should still be safe.
        StringRef m_trimmed_name;
    public:
        SectionTracker( NameAndLocation&& nameAndLocation, TrackerContext& ctx, ITracker* parent );

        bool isComplete() const override;
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `extras/catch_amalgamated.hpp` | 10485 → 10470 | 3 → 3 | 428.33 → 426.33 | 1283 → 1277 | 0 → 0 |

## Diff

```diff
diff --git a/extras/catch_amalgamated.hpp b/extras/catch_amalgamated.hpp
index b9ba53d..b589142 100644
--- a/extras/catch_amalgamated.hpp
+++ b/extras/catch_amalgamated.hpp
@@ -10449,20 +10449,6 @@ namespace TestCaseTracking {
         //! Marks tracker as executing a child, doing se recursively up the tree
         void openChild();
 
-        /**
-         * Returns true if the instance is a section tracker
-         *
-         * Subclasses should override to true if they are, replaces RTTI
-         * for internal debug checks.
-         */
-        virtual bool isSectionTracker() const;
-        /**
-         * Returns true if the instance is a generator tracker
-         *
-         * Subclasses should override to true if they are, replaces RTTI
-         * for internal debug checks.
-         */
-        virtual bool isGeneratorTracker() const;
     };
 
     class TrackerContext {
@@ -10522,8 +10508,6 @@ namespace TestCaseTracking {
     public:
         SectionTracker( NameAndLocation&& nameAndLocation, TrackerContext& ctx, ITracker* parent );
 
-        bool isSectionTracker() const override;
-
         bool isComplete() const override;
 
         static SectionTracker& acquire( TrackerContext& ctx, NameAndLocationRef const& nameAndLocation );

```
