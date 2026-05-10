# Refactor DIP-004 (DIP): Function `getMutableRegistryHub` accesses a static global variable `RegistryH...

**Status:** `applied_unverified`  
**Branch:** `refactor/DIP-004` -> `main`  
**Head commit:** `c0e90c222f4f361304a843758cc8db4850cc978d`  
**LLM finish:** `FinishReason.STOP` (prompt 3084, completion 320)  

## Detected issue

- **File**: `extras/catch_amalgamated.hpp`
- **Entity**: `Catch::getMutableRegistryHub` (class)
- **Lines (at detection time)**: L670–L670
- **Severity**: high
- **Confidence**: detected by 3 scan(s)

**Description.** Function `getMutableRegistryHub` accesses a static global variable `RegistryHub::getRegistryHub()`.

**Reasoning.** The `Catch::getMutableRegistryHub` function accesses a static global variable via `RegistryHub::getRegistryHub()`. This creates a hardcoded dependency on a specific global instance, violating DIP. High-level modules should depend on abstractions, not concrete global implementations. This makes testing and substitution of dependencies challenging.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `extras/catch_amalgamated.hpp`

**Summary.** Introduce a RegistryHubProvider interface to decouple global registry access

**Rationale.** The current implementation of getMutableRegistryHub relies on a hardcoded global static instance. By introducing an IRegistryHubProvider interface and allowing for dependency injection of a provider, we can decouple the high-level components from the concrete global registry implementation, adhering to the Dependency Inversion Principle.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `extras/catch_amalgamated.hpp` (10-line block → 13-line replacement)

**Replaces:**

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
        virtual IMutableRegistryHub& getMutableRegistryHub() = 0;
    };

    void setRegistryHubProvider(IRegistryHubProvider* provider);
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `extras/catch_amalgamated.hpp` | 10519 → 10521 | 3 → 3 | 426 → 426 | 1276 → 1276 | 0 → 0 |

## Diff

```diff
diff --git a/extras/catch_amalgamated.hpp b/extras/catch_amalgamated.hpp
index 043baf9..7e42c6d 100644
--- a/extras/catch_amalgamated.hpp
+++ b/extras/catch_amalgamated.hpp
@@ -1384,8 +1384,11 @@ namespace Catch {
     public:
         virtual ~IRegistryHubProvider() = default;
         virtual IRegistryHub const& getRegistryHub() const = 0;
+        virtual IMutableRegistryHub& getMutableRegistryHub() = 0;
     };
 
+    void setRegistryHubProvider(IRegistryHubProvider* provider);
+
 }
 
 #endif // CATCH_INTERFACES_REGISTRY_HUB_HPP_INCLUDED

```
