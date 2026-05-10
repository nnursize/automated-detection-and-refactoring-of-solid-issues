# Refactor DIP-001 (DIP): Static global variable 'currentContext' in Catch::Context class.

**Status:** `obsolete`  
**Branch:** `refactor/DIP-001` -> `main`  
**Head commit:** `83b3c825c2fcc66cc6ff817cbc5b149ac97eea55`  

## Detected issue

- **File**: `extras/catch_amalgamated.hpp`
- **Entity**: `Catch::Context::currentContext` (class)
- **Lines (at detection time)**: L279–L279
- **Severity**: high
- **Confidence**: detected by 3 scan(s)

**Description.** Static global variable 'currentContext' in Catch::Context class.

**Reasoning.** The `Catch::Context::currentContext` is a static global variable. High-level modules (like tests or any code that uses `getCurrentContext`) depend directly on this concrete global state. This violates DIP because it hardcodes a dependency on a specific implementation detail (the global context instance) rather than depending on an abstraction. It makes it difficult to replace or mock the context for testing or to manage multiple contexts. Ideally, the context should be passed through dependency injection or managed through a more flexible mechanism.

## Obsolete

entity `Catch::Context::currentContext` not found in current source of `extras/catch_amalgamated.hpp` — likely renamed/removed by an earlier refactor

## Diff

*(no diff — patch was not applied)*
