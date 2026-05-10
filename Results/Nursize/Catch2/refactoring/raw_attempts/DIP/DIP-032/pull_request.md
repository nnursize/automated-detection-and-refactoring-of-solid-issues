# Refactor DIP-032 (DIP): Reporter registry function `registerReporter` directly uses `Detail::make_uni...

**Status:** `obsolete`  
**Branch:** `refactor/DIP-032` -> `main`  
**Head commit:** `83b3c825c2fcc66cc6ff817cbc5b149ac97eea55`  

## Detected issue

- **File**: `extras/catch_amalgamated.hpp`
- **Entity**: `Catch::ReporterRegistry::registerReporter` (class)
- **Lines (at detection time)**: L309–L315
- **Severity**: high
- **Confidence**: detected by 3 scan(s)

**Description.** Reporter registry function `registerReporter` directly uses `Detail::make_unique<IReporterFactory>`.

**Reasoning.** The `Catch::ReporterRegistry::registerReporter` function directly uses `Detail::make_unique<IReporterFactory>` to create the reporter factory. This creates a dependency on a specific factory function and the concrete `IReporterFactory` type. DIP requires high-level modules to depend on abstractions. The registry should ideally accept an `IReporterFactory` pointer or a factory interface, rather than directly instantiating it. This hardcodes the dependency on the `make_unique` usage and `IReporterFactory`.

## Obsolete

entity `Catch::ReporterRegistry::registerReporter` not found in current source of `extras/catch_amalgamated.hpp` — likely renamed/removed by an earlier refactor

## Diff

*(no diff — patch was not applied)*
