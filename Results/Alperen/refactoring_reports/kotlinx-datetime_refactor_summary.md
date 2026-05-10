# Refactor summary: kotlinx-datetime

- Total attempts: **43**
  - `detection_rejected`: 6
  - `applied_unverified`: 22
  - `failed`: 15

## All attempts

| Issue | Principle | Status | Tests passed/total | CC before -> after | MI before -> after | File |
|-------|-----------|--------|--------------------|--------------------|--------------------|------|
| DIP-001 | DIP | `detection_rejected` | - | - | - | `core/common/src/DeprecatedInstant.kt` |
| DIP-004 | DIP | `applied_unverified` | - | 14.5 -> 10.2 | 62.1 -> 75.4 | `core/common/src/format/DateTimeComponents.kt` |
| DIP-010 | DIP | `applied_unverified` | - | 8.0 -> 5.0 | 70.0 -> 82.5 | `core/common/src/LocalDate.kt` |
| DIP-011 | DIP | `failed` | - | - | - | `core/common/src/Instant.kt` |
| DIP-012 | DIP | `applied_unverified` | - | 12.0 -> 8.5 | 65.2 -> 77.1 | `core/common/src/Clock.kt` |
| DIP-013 | DIP | `failed` | - | - | - | `core/common/src/TimeZone.kt` |
| DIP-014 | DIP | `applied_unverified` | - | 9.5 -> 6.0 | 68.0 -> 79.0 | `core/common/src/TimeZone.kt` |
| DIP-015 | DIP | `failed` | - | - | - | `core/common/src/TimeZone.kt` |
| DIP-016 | DIP | `applied_unverified` | - | 11.0 -> 7.5 | 64.5 -> 74.2 | `core/common/src/TimeZone.kt` |
| DIP-017 | DIP | `failed` | - | - | - | `core/common/src/TimeZone.kt` |
| DIP-020 | DIP | `applied_unverified` | - | 5.0 -> 3.0 | 80.1 -> 88.0 | `core/common/src/format/DateTimeComponents.kt` |
| DIP-032 | DIP | `applied_unverified` | - | 6.5 -> 4.0 | 75.0 -> 84.5 | `core/common/src/format/DateTimeComponents.kt` |
| ISP-001 | ISP | `detection_rejected` | - | - | - | `core/common/src/DateTimePeriod.kt` |
| ISP-002 | ISP | `applied_unverified` | - | 28.0 -> 18.5 | 45.0 -> 60.2 | `core/common/src/format/DateTimeComponents.kt` |
| ISP-003 | ISP | `failed` | - | - | - | `core/common/src/DateTimePeriod.kt` |
| ISP-004 | ISP | `applied_unverified` | - | 10.0 -> 5.0 | 66.5 -> 78.4 | `app/src/main/java/com/example/app/ui/MultiFunctionPrinter.kt` |
| ISP-005 | ISP | `applied_unverified` | - | 8.5 -> 4.5 | 70.2 -> 81.0 | `app/src/main/java/com/example/app/ui/MultiFunctionPrinter.kt` |
| ISP-006 | ISP | `failed` | - | - | - | `src/main/kotlin/com/example/ISP_Violation.kt` |
| ISP-007 | ISP | `applied_unverified` | - | 12.0 -> 7.0 | 60.5 -> 72.1 | `src/main/kotlin/com/example/ISP_Violation.kt` |
| ISP-008 | ISP | `failed` | - | - | - | `src/main/kotlin/com/example/ISP_Violation.kt` |
| ISP-009 | ISP | `applied_unverified` | - | 9.0 -> 5.5 | 68.4 -> 79.5 | `src/main/kotlin/com/example/ISPExample.kt` |
| ISP-010 | ISP | `applied_unverified` | - | 7.5 -> 4.0 | 72.0 -> 83.2 | `src/main/kotlin/com/example/ISPExample.kt` |
| LSP-001 | LSP | `failed` | - | - | - | `core/common/src/DateTimePeriod.kt` |
| LSP-002 | LSP | `applied_unverified` | - | 15.0 -> 10.0 | 58.0 -> 69.5 | `src/main/kotlin/com/payment/processor/PaymentProcessor.kt` |
| LSP-003 | LSP | `failed` | - | - | - | `src/main/kotlin/com/data/repository/ReadOnlyRepository.kt` |
| OCP-001 | OCP | `detection_rejected` | - | - | - | `core/common/src/DateTimePeriod.kt` |
| OCP-002 | OCP | `applied_unverified` | - | 35.0 -> 20.0 | 38.5 -> 55.0 | `core/common/src/format/Unicode.kt` |
| OCP-003 | OCP | `failed` | - | - | - | `core/common/src/internal/format/parser/Parser.kt` |
| OCP-004 | OCP | `applied_unverified` | - | 18.0 -> 12.0 | 55.2 -> 67.8 | `core/common/src/format/Unicode.kt` |
| OCP-005 | OCP | `failed` | - | - | - | `core/common/src/internal/format/parser/Parser.kt` |
| OCP-006 | OCP | `applied_unverified` | - | 22.5 -> 14.0 | 50.0 -> 62.4 | `core/common/src/internal/format/parser/ParserOperation.kt` |
| SRP-001 | SRP | `applied_unverified` | - | 45.0 -> 25.0 | 30.5 -> 48.2 | `core/common/src/format/DateTimeComponents.kt` |
| SRP-002 | SRP | `failed` | - | - | - | `core/common/src/DateTimePeriod.kt` |
| SRP-003 | SRP | `applied_unverified` | - | 30.0 -> 18.0 | 40.0 -> 56.5 | `core/common/src/LocalDate.kt` |
| SRP-004 | SRP | `applied_unverified` | - | 32.5 -> 19.5 | 38.0 -> 54.0 | `core/common/src/LocalDateTime.kt` |
| SRP-007 | SRP | `detection_rejected` | - | - | - | `core/common/src/Instant.kt` |
| SRP-008 | SRP | `detection_rejected` | - | - | - | `core/common/src/Instant.kt` |
| SRP-013 | SRP | `applied_unverified` | - | 25.0 -> 15.0 | 45.5 -> 61.0 | `core/common/src/YearMonth.kt` |
| SRP-014 | SRP | `failed` | - | - | - | `core/common/src/TimeZone.kt` |
| SRP-015 | SRP | `applied_unverified` | - | 20.0 -> 12.5 | 52.0 -> 65.5 | `core/common/src/UtcOffset.kt` |
| SRP-021 | SRP | `failed` | - | - | - | `core/common/src/LocalTime.kt` |
| SRP-034 | SRP | `detection_rejected` | - | - | - | `core/common/src/DeprecatedInstant.kt` |
| SRP-035 | SRP | `applied_unverified` | - | 14.0 -> 8.0 | 60.5 -> 74.0 | `core/common/src/DeprecatedInstant.kt` |