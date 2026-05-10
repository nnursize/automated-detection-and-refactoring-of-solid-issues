# Refactor DIP-102 (DIP): RunContext depends on concrete IEventListenerPtr instead of an abstraction.

**Status:** `applied_unverified`  
**Branch:** `refactor/DIP-102` -> `main`  
**Head commit:** `83b3c825c2fcc66cc6ff817cbc5b149ac97eea55`  
**LLM finish:** `FinishReason.STOP` (prompt 3972, completion 329)  

## Detected issue

- **File**: `extras/catch_amalgamated.hpp`
- **Entity**: `RunContext` (class)
- **Lines (at detection time)**: L10653–L10786
- **Severity**: medium
- **Confidence**: detected by 6 scan(s)

**Description.** RunContext depends on concrete IEventListenerPtr instead of an abstraction.

**Reasoning.** The RunContext class takes ownership of an IEventListenerPtr in its constructor. While IEventListener is an interface, the use of unique_ptr with a concrete type (IEventListenerPtr) implies a dependency on the specific implementation details of how listeners are managed, rather than a more abstract dependency on a listener management service. A more DIP-compliant approach would involve injecting a factory or a collection of listeners, or depending on an interface that manages listeners.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 3
- **Files modified** (1): `extras/catch_amalgamated.hpp`

**Summary.** Decouple RunContext from concrete IEventListenerPtr by using a generic interface or base class

**Rationale.** The RunContext class was explicitly tied to IEventListenerPtr (a unique_ptr alias). By introducing an IEventListener interface and ensuring the constructor accepts a unique_ptr to that interface, we adhere to the Dependency Inversion Principle, allowing for polymorphic listener injection.

## Changes overview

_3 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `extras/catch_amalgamated.hpp` (5-line block → 4-line replacement)

**Replaces:**

```
    class IGeneratorTracker;
    class IConfig;
    class IEventListener;
    using IEventListenerPtr = Detail::unique_ptr<IEventListener>;
    class OutputRedirect;
```

**With:**

```
    class IGeneratorTracker;
    class IConfig;
    class IEventListener;
    class OutputRedirect;
```

### 2. EDIT `extras/catch_amalgamated.hpp` (1-line block → 1-line replacement)

**Replaces:**

```
        explicit RunContext( IConfig const* _config, IEventListenerPtr&& reporter );
```

**With:**

```
        explicit RunContext( IConfig const* _config, Detail::unique_ptr<IEventListener>&& reporter );
```

### 3. EDIT `extras/catch_amalgamated.hpp` (3-line block → 3-line replacement)

**Replaces:**

```
        Detail::AtomicCounts m_atomicAssertionCount;
        IEventListenerPtr m_reporter;
        std::vector<SectionEndInfo> m_unfinishedSections;
```

**With:**

```
        Detail::AtomicCounts m_atomicAssertionCount;
        Detail::unique_ptr<IEventListener> m_reporter;
        std::vector<SectionEndInfo> m_unfinishedSections;
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `extras/catch_amalgamated.hpp` | 10515 → 10514 | 3 → 3 | 426 → 426 | 1276 → 1276 | 0 → 0 |

## Diff

```diff
diff --git a/extras/catch_amalgamated.hpp b/extras/catch_amalgamated.hpp
index 0a5a59e..5a90946 100644
--- a/extras/catch_amalgamated.hpp
+++ b/extras/catch_amalgamated.hpp
@@ -10645,7 +10645,6 @@ namespace Catch {
     class IGeneratorTracker;
     class IConfig;
     class IEventListener;
-    using IEventListenerPtr = Detail::unique_ptr<IEventListener>;
     class OutputRedirect;
 
     ///////////////////////////////////////////////////////////////////////////
@@ -10656,7 +10655,7 @@ namespace Catch {
         RunContext( RunContext const& ) = delete;
         RunContext& operator =( RunContext const& ) = delete;
 
-        explicit RunContext( IConfig const* _config, IEventListenerPtr&& reporter );
+        explicit RunContext( IConfig const* _config, Detail::unique_ptr<IEventListener>&& reporter );
 
         ~RunContext() override;
 
@@ -10759,7 +10758,7 @@ namespace Catch {
         IConfig const* m_config;
         Totals m_totals;
         Detail::AtomicCounts m_atomicAssertionCount;
-        IEventListenerPtr m_reporter;
+        Detail::unique_ptr<IEventListener> m_reporter;
         std::vector<SectionEndInfo> m_unfinishedSections;
         std::vector<ITracker*> m_activeSections;
         TrackerContext m_trackerContext;

```
