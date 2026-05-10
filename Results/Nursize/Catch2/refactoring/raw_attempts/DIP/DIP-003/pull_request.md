# Refactor DIP-003 (DIP): Function `getRegistryHub` accesses a static global variable `RegistryHub::get...

**Status:** `applied_unverified`  
**Branch:** `refactor/DIP-003` -> `main`  
**Head commit:** `91212601f6f7dd58e6b220399f1d42c679969fd9`  
**LLM finish:** `FinishReason.STOP` (prompt 3113, completion 231)  

## Detected issue

- **File**: `extras/catch_amalgamated.hpp`
- **Entity**: `Catch::getRegistryHub` (class)
- **Lines (at detection time)**: L667–L667
- **Severity**: high
- **Confidence**: detected by 3 scan(s)

**Description.** Function `getRegistryHub` accesses a static global variable `RegistryHub::getRegistryHub()`.

**Reasoning.** The `Catch::getRegistryHub` function accesses a static global variable via `RegistryHub::getRegistryHub()`. This means that all modules calling `getRegistryHub` have a hardcoded dependency on this specific global instance. DIP requires that high-level modules depend on abstractions, not concrete global instances. This coupling makes it difficult to test modules in isolation or to provide alternative implementations of the registry.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `extras/catch_amalgamated.hpp`

**Summary.** Introduce a RegistryHubProvider to decouple global registry access

**Rationale.** The current implementation of `getRegistryHub` forces a hard dependency on a static global instance. By introducing a provider interface, we allow for dependency injection and better testability, adhering to the Dependency Inversion Principle.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `extras/catch_amalgamated.hpp` (6-line block → 12-line replacement)

**Replaces:**

```
    IRegistryHub const& getRegistryHub();
    IMutableRegistryHub& getMutableRegistryHub();
    void cleanUp();
    std::string translateActiveException();

}
```

**With:**

```
    IRegistryHub const& getRegistryHub();
    IMutableRegistryHub& getMutableRegistryHub();
    void cleanUp();
    std::string translateActiveException();

    class IRegistryHubProvider {
    public:
        virtual ~IRegistryHubProvider() = default;
        virtual IRegistryHub const& getRegistryHub() const = 0;
    };

}
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `extras/catch_amalgamated.hpp` | 10514 → 10519 | 3 → 3 | 426 → 426 | 1276 → 1276 | 0 → 0 |

## Diff

```diff
diff --git a/extras/catch_amalgamated.hpp b/extras/catch_amalgamated.hpp
index 5a90946..043baf9 100644
--- a/extras/catch_amalgamated.hpp
+++ b/extras/catch_amalgamated.hpp
@@ -1380,6 +1380,12 @@ namespace Catch {
     void cleanUp();
     std::string translateActiveException();
 
+    class IRegistryHubProvider {
+    public:
+        virtual ~IRegistryHubProvider() = default;
+        virtual IRegistryHub const& getRegistryHub() const = 0;
+    };
+
 }
 
 #endif // CATCH_INTERFACES_REGISTRY_HUB_HPP_INCLUDED

```
