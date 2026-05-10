# Refactor DIP-033 (DIP): Reporter registry function `registerListener` directly uses `Detail::make_uni...

**Status:** `obsolete`  
**Branch:** `refactor/DIP-033` -> `main`  
**Head commit:** `83b3c825c2fcc66cc6ff817cbc5b149ac97eea55`  

## Detected issue

- **File**: `extras/catch_amalgamated.hpp`
- **Entity**: `Catch::ReporterRegistry::registerListener` (class)
- **Lines (at detection time)**: L317–L323
- **Severity**: high
- **Confidence**: detected by 3 scan(s)

**Description.** Reporter registry function `registerListener` directly uses `Detail::make_unique<EventListenerFactory>`.

**Reasoning.** The `Catch::ReporterRegistry::registerListener` function directly uses `Detail::make_unique<EventListenerFactory>` to create the listener factory. This creates a dependency on a specific factory function and the concrete `EventListenerFactory` type. DIP requires high-level modules to depend on abstractions. The registry should ideally accept an `EventListenerFactory` pointer or an interface, rather than directly instantiating it. This hardcodes the dependency on the `make_unique` usage and `EventListenerFactory`.

## Obsolete

entity `Catch::ReporterRegistry::registerListener` not found in current source of `extras/catch_amalgamated.hpp` — likely renamed/removed by an earlier refactor

## Diff

*(no diff — patch was not applied)*
