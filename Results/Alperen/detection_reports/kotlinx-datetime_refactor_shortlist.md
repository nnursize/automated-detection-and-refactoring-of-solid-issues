# Refactor Shortlist: kotlinx-datetime

Quota: 12 issues × 5 principles = 60 total.
Selected: **43**.

> **Note:** the following principles have fewer issues than the quota. Per the project brief, seed violations manually to fill the gap:
> - OCP: 6 / 12
> - LSP: 3 / 12
> - ISP: 10 / 12

Ranking: `scan_count` desc, then severity (high > medium > low), then file_path, then line_start.

## SRP (12 selected)

| # | Issue ID | Confidence | Severity | Location | Description |
|---|----------|-----------:|----------|----------|-------------|
| 1 | SRP-002 | 5 scan(s) | medium | `core/common/src/DateTimePeriod.kt` DateTimePeriod.Companion.parse (L139–270) | The parse method contains extensive string parsing logic, mixing data representation with complex deserialization. |
| 2 | SRP-001 | 4 scan(s) | high | `core/common/src/format/DateTimeComponents.kt` DateTimeComponents (L30–339) | The DateTimeComponents class mixes multiple responsibilities: data container, data conversion, and acting as a factory/registry for formatters. |
| 3 | SRP-003 | 4 scan(s) | medium | `core/common/src/LocalDate.kt` LocalDate (L54–178) | The LocalDate class mixes data representation with string serialization/deserialization and format definition. |
| 4 | SRP-034 | 3 scan(s) | high | `core/common/src/DeprecatedInstant.kt` Instant.parse (L142–145) | The companion object method for Instant handles parsing a string, which is a separate responsibility from representing an instant in time. |
| 5 | SRP-004 | 3 scan(s) | medium | `core/common/src/LocalDateTime.kt` LocalDateTime (L62–204) | The LocalDateTime class mixes data representation with string serialization/deserialization and format definition. |
| 6 | SRP-015 | 3 scan(s) | medium | `core/common/src/UtcOffset.kt` UtcOffset (L30–120) | The UtcOffset class mixes data representation with string serialization/deserialization and format definition. |
| 7 | SRP-013 | 3 scan(s) | medium | `core/common/src/YearMonth.kt` YearMonth (L40–140) | The YearMonth class mixes data representation with string serialization/deserialization and format definition. |
| 8 | SRP-007 | 2 scan(s) | high | `core/common/src/Instant.kt` Instant.periodUntil(other: Instant, timeZone: TimeZone) (L68–85) | The Instant.periodUntil extension function calculates a DateTimePeriod between two instants, involving complex calendar-based arithmetic and time zone rules. |
| 9 | SRP-008 | 2 scan(s) | high | `core/common/src/Instant.kt` Instant.until(other: Instant, unit: DateTimeUnit, timeZone: TimeZone) (L87–105) | The Instant.until extension function calculates the number of units between instants, involving complex calendar-based arithmetic and time zone rules. |
| 10 | SRP-014 | 2 scan(s) | high | `core/common/src/TimeZone.kt` TimeZone.Companion (L57–105) | The TimeZone.Companion object mixes time zone rule provision with platform-specific discovery and loading of time zone definitions. |
| 11 | SRP-035 | 2 scan(s) | medium | `core/common/src/DeprecatedInstant.kt` Instant.toString (L115–119) | The toString method performs specific ISO 8601 formatting logic, which is a formatting responsibility. |
| 12 | SRP-021 | 2 scan(s) | medium | `core/common/src/LocalTime.kt` LocalTime (L21–304) | The LocalTime class combines data representation, ISO 8601 formatting/parsing, and acts as a factory for its instances and associated formats. |

## OCP (6 selected)

| # | Issue ID | Confidence | Severity | Location | Description |
|---|----------|-----------:|----------|----------|-------------|
| 1 | OCP-001 | 6 scan(s) | high | `core/common/src/DateTimePeriod.kt` DateTimePeriod.Companion.parseImpl (L235–427) | Hardcoded parsing logic for ISO 8601 duration format using a state machine |
| 2 | OCP-002 | 2 scan(s) | medium | `core/common/src/format/Unicode.kt` byUnicodePattern (L104–155) | Hardcoded mapping of Unicode format directives to internal builder methods |
| 3 | OCP-003 | 2 scan(s) | medium | `core/common/src/internal/format/parser/Parser.kt` List<ParserStructure<T>>.concat (L57–154) | Hardcoded logic for merging parser operations |
| 4 | OCP-006 | 1 scan(s) | high | `core/common/src/internal/format/parser/ParserOperation.kt` TimeZoneParserOperation.Companion.validateTimeZone (L128–226) | Hardcoded state machine for time zone parsing is closed to extension |
| 5 | OCP-004 | 1 scan(s) | medium | `core/common/src/format/Unicode.kt` unicodeDirective (L372–407) | Hardcoded mapping of characters to directives requires modification to support new format patterns. |
| 6 | OCP-005 | 1 scan(s) | medium | `core/common/src/internal/format/parser/Parser.kt` ParserStructure.concat (L62–172) | Hardcoded logic for merging parser structures limits extension of parsing logic. |

## LSP (3 selected)

| # | Issue ID | Confidence | Severity | Location | Description |
|---|----------|-----------:|----------|----------|-------------|
| 1 | LSP-001 | 6 scan(s) | high | `core/common/src/DateTimePeriod.kt` DatePeriod (L443–515) | DatePeriod inherits from DateTimePeriod but forces time components to be zero, violating the base class contract. |
| 2 | LSP-002 | 1 scan(s) | high | `src/main/kotlin/com/payment/processor/PaymentProcessor.kt` PaymentProcessor (L1–20) | Fat interface forcing subclasses to implement irrelevant payment methods |
| 3 | LSP-003 | 1 scan(s) | medium | `src/main/kotlin/com/data/repository/ReadOnlyRepository.kt` MutableRepository (L5–15) | Subclass violates the contract of a read-only base class by introducing mutation |

## ISP (10 selected)

| # | Issue ID | Confidence | Severity | Location | Description |
|---|----------|-----------:|----------|----------|-------------|
| 1 | ISP-002 | 3 scan(s) | high | `core/common/src/format/DateTimeComponents.kt` DateTimeComponents (L26–500) | DateTimeComponents is a 'fat' interface/class containing fields for date, time, offset, and timezone, forcing users to depend on all of them. |
| 2 | ISP-001 | 3 scan(s) | medium | `core/common/src/DateTimePeriod.kt` DateTimePeriod (L65–125) | DateTimePeriod forces implementations to provide both date and time components, even when only one is relevant. |
| 3 | ISP-003 | 2 scan(s) | medium | `core/common/src/DateTimePeriod.kt` DatePeriod (L400–440) | DatePeriod is forced to implement time-based properties inherited from DateTimePeriod that are semantically irrelevant to a date-only period. |
| 4 | ISP-004 | 1 scan(s) | high | `app/src/main/java/com/example/app/ui/MultiFunctionPrinter.kt` IMachine (L3–7) | Fat interface that bundles multiple unrelated functionalities (print, scan, fax). |
| 5 | ISP-005 | 1 scan(s) | high | `app/src/main/java/com/example/app/ui/MultiFunctionPrinter.kt` OldPrinter (L9–20) | Class forced to implement methods it does not use or support. |
| 6 | ISP-009 | 1 scan(s) | medium | `src/main/kotlin/com/example/ISPExample.kt` Worker (L1–21) | Worker class implements a single interface with methods for both basic and advanced tasks, forcing all workers to have methods they may not need. |
| 7 | ISP-006 | 1 scan(s) | medium | `src/main/kotlin/com/example/ISP_Violation.kt` Worker (L5–17) | Worker class implements a broad interface with unrelated methods. |
| 8 | ISP-007 | 1 scan(s) | medium | `src/main/kotlin/com/example/ISP_Violation.kt` Robot (L20–25) | Robot class implements methods it cannot perform. |
| 9 | ISP-010 | 1 scan(s) | low | `src/main/kotlin/com/example/ISPExample.kt` RobotWorker (L23–30) | RobotWorker implements the Work interface but does not implement the manage method, indicating it does not use that part of the interface. |
| 10 | ISP-008 | 1 scan(s) | low | `src/main/kotlin/com/example/ISP_Violation.kt` HumanWorker (L28–34) | HumanWorker implements all methods, but some might be less relevant. |

## DIP (12 selected)

| # | Issue ID | Confidence | Severity | Location | Description |
|---|----------|-----------:|----------|----------|-------------|
| 1 | DIP-001 | 6 scan(s) | high | `core/common/src/DeprecatedInstant.kt` Instant.now (L199–199) | Directly calls Clock.System.now() without abstraction. |
| 2 | DIP-010 | 5 scan(s) | medium | `core/common/src/LocalDate.kt` LocalDate.Companion.parse (L157–157) | The `parse` function in `LocalDate.Companion` directly uses `getIsoDateFormat()` and `format.parse()`. |
| 3 | DIP-013 | 4 scan(s) | high | `core/common/src/TimeZone.kt` TimeZone.currentSystemDefault (L112–112) | The `TimeZone.currentSystemDefault()` function directly accesses platform-specific APIs and concrete implementations for timezone retrieval. |
| 4 | DIP-011 | 4 scan(s) | medium | `core/common/src/Instant.kt` Instant.parse (L45–45) | The `Instant.parse` function directly uses `DateTimeComponents.Formats.ISO_DATE_TIME_OFFSET` and `DateTimeComponents.toInstantUsingOffset()`. |
| 5 | DIP-014 | 4 scan(s) | medium | `core/common/src/TimeZone.kt` Instant.toLocalDateTime (L367–367) | The `toLocalDateTime` extension function directly calls `toLocalDateTimeFailing`. |
| 6 | DIP-015 | 4 scan(s) | medium | `core/common/src/TimeZone.kt` LocalDateTime.toInstant (L426–426) | The `toInstant` extension function directly calls `toLocalDateTimeFailing`, `localDateTimeToInstant`, and `toDeprecatedInstant()`. |
| 7 | DIP-016 | 3 scan(s) | medium | `core/common/src/TimeZone.kt` LocalDate.atStartOfDayIn (L473–473) | The `atStartOfDayIn` extension function directly calls `toLocalDateTimeFailing`, `localDateTimeToInstant`, and `toDeprecatedInstant()`. |
| 8 | DIP-017 | 3 scan(s) | medium | `core/common/src/TimeZone.kt` localDateTimeToInstant (L493–493) | The `localDateTimeToInstant` function directly calls `toLocalDateTimeFailing`, `localDateTimeToInstant`, and `check`. |
| 9 | DIP-004 | 3 scan(s) | medium | `core/common/src/format/DateTimeComponents.kt` DateTimeComponents.toInstantUsingOffset (L340–356) | The `toInstantUsingOffset` function directly calls `toLocalDateTime` and `toUtcOffset` on `this` `DateTimeComponents` instance. |
| 10 | DIP-012 | 2 scan(s) | high | `core/common/src/Clock.kt` Clock.System.now (L41–41) | The `Clock.System.now()` function directly calls `kotlin.time.Clock.System.now()`. |
| 11 | DIP-020 | 2 scan(s) | high | `core/common/src/format/DateTimeComponents.kt` DateTimeComponents.Formats.ISO_DATE_TIME_OFFSET (L175–215) | Exposes a concrete format implementation directly. |
| 12 | DIP-032 | 2 scan(s) | medium | `core/common/src/format/DateTimeComponents.kt` DateTimeComponents.Formats.ISO_DATE_TIME_OFFSET (L153–167) | The `DateTimeComponents.Formats.ISO_DATE_TIME_OFFSET` format directly uses `UtcOffset.Formats.ISO` and `DateTimeComponents.Formats.ISO_DATE` without depending on abstractions for these formats. |
