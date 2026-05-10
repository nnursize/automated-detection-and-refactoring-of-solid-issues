# Refactor summary: Catch2

- Total attempts: **60**
  - `applied_unverified`: 26
  - `patch_failed`: 18
  - `detection_rejected`: 9
  - `obsolete`: 5
  - `llm_error`: 2

## All attempts

| Issue | Principle | Status | Tests passed/total | CC before -> after | MI before -> after | File |
|-------|-----------|--------|--------------------|--------------------|--------------------|------|
| DIP-001 | DIP | `obsolete` | - | - | - | `extras/catch_amalgamated.hpp` |
| DIP-003 | DIP | `applied_unverified` | - | 426.0 -> 426.0 | 0.0 -> 0.0 | `extras/catch_amalgamated.hpp` |
| DIP-004 | DIP | `applied_unverified` | - | 426.0 -> 426.0 | 0.0 -> 0.0 | `extras/catch_amalgamated.hpp` |
| DIP-032 | DIP | `obsolete` | - | - | - | `extras/catch_amalgamated.hpp` |
| DIP-033 | DIP | `obsolete` | - | - | - | `extras/catch_amalgamated.hpp` |
| DIP-035 | DIP | `obsolete` | - | - | - | `extras/catch_amalgamated.hpp` |
| DIP-046 | DIP | `detection_rejected` | - | - | - | `extras/catch_amalgamated.hpp` |
| DIP-053 | DIP | `obsolete` | - | - | - | `extras/catch_amalgamated.hpp` |
| DIP-054 | DIP | `applied_unverified` | - | 426.0 -> 426.0 | 0.0 -> 0.0 | `extras/catch_amalgamated.hpp` |
| DIP-055 | DIP | `applied_unverified` | - | 426.0 -> 426.33 | 0.0 -> 0.0 | `extras/catch_amalgamated.hpp` |
| DIP-102 | DIP | `applied_unverified` | - | 426.0 -> 426.0 | 0.0 -> 0.0 | `extras/catch_amalgamated.hpp` |
| DIP-110 | DIP | `applied_unverified` | - | 426.33 -> 426.33 | 0.0 -> 0.0 | `extras/catch_amalgamated.hpp` |
| ISP-001 | ISP | `applied_unverified` | - | 425.0 -> 425.0 | 0.0 -> 0.0 | `extras/catch_amalgamated.hpp` |
| ISP-002 | ISP | `patch_failed` | - | - | - | `src/catch2/internal/catch_run_context.hpp` |
| ISP-003 | ISP | `applied_unverified` | - | 425.0 -> 425.0 | 0.0 -> 0.0 | `extras/catch_amalgamated.hpp` |
| ISP-004 | ISP | `patch_failed` | - | - | - | `src/catch2/internal/catch_run_context.hpp` |
| ISP-005 | ISP | `patch_failed` | - | - | - | `extras/catch_amalgamated.hpp` |
| ISP-007 | ISP | `applied_unverified` | - | 425.0 -> 426.0 | 0.0 -> 0.0 | `extras/catch_amalgamated.hpp` |
| ISP-010 | ISP | `detection_rejected` | - | - | - | `extras/catch_amalgamated.hpp` |
| ISP-011 | ISP | `detection_rejected` | - | - | - | `src/catch2/internal/catch_decomposer.hpp` |
| ISP-018 | ISP | `applied_unverified` | - | 5.43 -> 4.76 | 0.0 -> 0.0 | `src/catch2/reporters/catch_reporter_console.cpp` |
| ISP-022 | ISP | `applied_unverified` | - | 425.0 -> 425.0 | 0.0 -> 0.0 | `extras/catch_amalgamated.hpp` |
| ISP-023 | ISP | `patch_failed` | - | - | - | `extras/catch_amalgamated.hpp` |
| ISP-043 | ISP | `applied_unverified` | - | 55.0 -> 55.0 | 0.0 -> 0.0 | `src/catch2/internal/catch_clara.hpp` |
| LSP-001 | LSP | `applied_unverified` | - | 425.0 -> 425.0 | 0.0 -> 0.0 | `extras/catch_amalgamated.hpp` |
| LSP-002 | LSP | `patch_failed` | - | - | - | `extras/catch_amalgamated.hpp` |
| LSP-003 | LSP | `applied_unverified` | - | 425.0 -> 425.0 | 0.0 -> 0.0 | `extras/catch_amalgamated.hpp` |
| LSP-004 | LSP | `patch_failed` | - | - | - | `extras/catch_amalgamated.hpp` |
| LSP-005 | LSP | `patch_failed` | - | - | - | `extras/catch_amalgamated.hpp` |
| LSP-006 | LSP | `applied_unverified` | - | 428.33 -> 426.33 | 0.0 -> 0.0 | `extras/catch_amalgamated.hpp` |
| LSP-007 | LSP | `patch_failed` | - | - | - | `extras/catch_amalgamated.hpp` |
| LSP-008 | LSP | `applied_unverified` | - | 425.0 -> 425.0 | 0.0 -> 0.0 | `extras/catch_amalgamated.hpp` |
| LSP-009 | LSP | `patch_failed` | - | - | - | `extras/catch_amalgamated.hpp` |
| LSP-010 | LSP | `patch_failed` | - | - | - | `extras/catch_amalgamated.hpp` |
| LSP-012 | LSP | `applied_unverified` | - | 426.33 -> 425.0 | 0.0 -> 0.0 | `extras/catch_amalgamated.hpp` |
| LSP-014 | LSP | `detection_rejected` | - | - | - | `third_party/clara.hpp` |
| OCP-004 | OCP | `patch_failed` | - | - | - | `extras/catch_amalgamated.hpp` |
| OCP-011 | OCP | `patch_failed` | - | - | - | `extras/catch_amalgamated.cpp` |
| OCP-012 | OCP | `applied_unverified` | - | 8.0 -> 7.0 | 0.0 -> 0.0 | `src/catch2/reporters/catch_reporter_tap.cpp` |
| OCP-013 | OCP | `patch_failed` | - | - | - | `extras/catch_amalgamated.cpp` |
| OCP-014 | OCP | `applied_unverified` | - | 6.5 -> 4.83 | 0.0 -> 0.0 | `src/catch2/reporters/catch_reporter_compact.cpp` |
| OCP-015 | OCP | `patch_failed` | - | - | - | `extras/catch_amalgamated.cpp` |
| OCP-016 | OCP | `applied_unverified` | - | 5.43 -> 5.43 | 0.0 -> 0.0 | `src/catch2/reporters/catch_reporter_console.cpp` |
| OCP-026 | OCP | `applied_unverified` | - | 433.0 -> 433.0 | 0.0 -> 0.0 | `extras/catch_amalgamated.hpp` |
| OCP-027 | OCP | `detection_rejected` | - | - | - | `extras/catch_amalgamated.cpp` |
| OCP-029 | OCP | `applied_unverified` | - | 433.0 -> 428.33 | 0.0 -> 0.0 | `extras/catch_amalgamated.hpp` |
| OCP-030 | OCP | `detection_rejected` | - | - | - | `extras/catch_amalgamated.cpp` |
| OCP-037 | OCP | `detection_rejected` | - | - | - | `extras/catch_amalgamated.cpp` |
| SRP-001 | SRP | `applied_unverified` | - | 433.67 -> 433.67 | 0.0 -> 0.0 | `extras/catch_amalgamated.hpp` |
| SRP-004 | SRP | `patch_failed` | - | - | - | `extras/catch_amalgamated.hpp` |
| SRP-006 | SRP | `applied_unverified` | - | 433.67 -> 433.0 | 0.0 -> 0.0 | `extras/catch_amalgamated.hpp` |
| SRP-037 | SRP | `patch_failed` | - | - | - | `extras/catch_amalgamated.hpp` |
| SRP-039 | SRP | `patch_failed` | - | - | - | `extras/catch_amalgamated.hpp` |
| SRP-046 | SRP | `applied_unverified` | - | 145.0 -> 145.0 | 0.0 -> 0.0 | `third_party/clara.hpp` |
| SRP-047 | SRP | `detection_rejected` | - | - | - | `extras/catch_amalgamated.hpp` |
| SRP-048 | SRP | `detection_rejected` | - | - | - | `src/catch2/internal/catch_decomposer.hpp` |
| SRP-049 | SRP | `patch_failed` | - | - | - | `extras/catch_amalgamated.cpp` |
| SRP-050 | SRP | `applied_unverified` | - | 5.48 -> 5.43 | 0.0 -> 0.0 | `src/catch2/reporters/catch_reporter_console.cpp` |
| SRP-051 | SRP | `llm_error` | - | - | - | `extras/catch_amalgamated.hpp` |
| SRP-052 | SRP | `llm_error` | - | - | - | `src/catch2/internal/catch_run_context.hpp` |