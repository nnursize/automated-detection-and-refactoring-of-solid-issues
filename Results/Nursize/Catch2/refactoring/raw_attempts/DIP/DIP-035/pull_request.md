# Refactor DIP-035 (DIP): Function `applyCommandLine` directly instantiates `Clara::Parser`.

**Status:** `obsolete`  
**Branch:** `refactor/DIP-035` -> `main`  
**Head commit:** `83b3c825c2fcc66cc6ff817cbc5b149ac97eea55`  

## Detected issue

- **File**: `extras/catch_amalgamated.hpp`
- **Entity**: `Catch::Session::applyCommandLine` (class)
- **Lines (at detection time)**: L175–L180
- **Severity**: high
- **Confidence**: detected by 3 scan(s)

**Description.** Function `applyCommandLine` directly instantiates `Clara::Parser`.

**Reasoning.** The `Catch::Session::applyCommandLine` function directly instantiates `Clara::Parser`. This means the session class depends directly on the concrete implementation of the command-line parser. DIP requires high-level modules to depend on abstractions. The command-line parsing functionality should be provided through an injected dependency (e.g., an `IParser` interface), allowing for different parsing strategies or mocks to be used, thus adhering to the Dependency Inversion Principle.

## Obsolete

entity `Catch::Session::applyCommandLine` not found in current source of `extras/catch_amalgamated.hpp` — likely renamed/removed by an earlier refactor

## Diff

*(no diff — patch was not applied)*
