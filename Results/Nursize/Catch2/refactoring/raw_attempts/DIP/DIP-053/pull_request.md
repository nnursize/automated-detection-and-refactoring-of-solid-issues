# Refactor DIP-053 (DIP): Generator factory `makeGenerators` directly uses `value` and `Generators` con...

**Status:** `obsolete`  
**Branch:** `refactor/DIP-053` -> `main`  
**Head commit:** `83b3c825c2fcc66cc6ff817cbc5b149ac97eea55`  

## Detected issue

- **File**: `extras/catch_amalgamated.hpp`
- **Entity**: `Catch::Generators::makeGenerators` (class)
- **Lines (at detection time)**: L649–L677
- **Severity**: high
- **Confidence**: detected by 3 scan(s)

**Description.** Generator factory `makeGenerators` directly uses `value` and `Generators` constructor.

**Reasoning.** The `Catch::Generators::makeGenerators` function directly calls `value()` and the `Generators<T>` constructor. This tightly couples the generator creation to specific generator implementations (`SingleValueGenerator`, `Generators`). DIP requires high-level modules to depend on abstractions. The generator creation should ideally accept an `IGenerator` or an abstract factory for generators, rather than directly instantiating these concrete types.

## Obsolete

entity `Catch::Generators::makeGenerators` not found in current source of `extras/catch_amalgamated.hpp` — likely renamed/removed by an earlier refactor

## Diff

*(no diff — patch was not applied)*
