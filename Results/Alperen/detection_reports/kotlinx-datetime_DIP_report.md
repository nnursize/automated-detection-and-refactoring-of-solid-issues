# DIP Violation Report: kotlinx-datetime

## Summary
- **Total unique issues**: 54
- **High severity**: 32
- **Medium severity**: 17
- **Low severity**: 5
- **Found by multiple scans**: 13/54

## Issues

### DIP-001 [HIGH] core/common/src/DeprecatedInstant.kt — Instant.now
- **Confidence**: Found in 6 scan(s)
- **Lines**: 199–199
- **Type**: class
- **Description**: Directly calls Clock.System.now() without abstraction.
- **Reasoning**: The `Instant.now()` function directly calls `Clock.System.now()`. This violates the Dependency Inversion Principle (DIP) because the high-level module (Instant) depends directly on a low-level module (Clock.System) instead of an abstraction. To adhere to DIP, `Instant.now()` should depend on an abstraction of a clock, and the concrete implementation (like `Clock.System`) should be injected.

### DIP-010 [MEDIUM] core/common/src/LocalDate.kt — LocalDate.Companion.parse
- **Confidence**: Found in 5 scan(s)
- **Lines**: 157–157
- **Type**: class
- **Description**: The `parse` function in `LocalDate.Companion` directly uses `getIsoDateFormat()` and `format.parse()`.
- **Reasoning**: The `LocalDate.Companion.parse` function has a default parameter `format: DateTimeFormat<LocalDate> = getIsoDateFormat()`. This default parameter directly calls `getIsoDateFormat()`, which in turn directly returns `LocalDate.Formats.ISO`. This means the `parse` function is tightly coupled to the concrete `LocalDate.Formats.ISO` implementation. If the way `ISO` format is obtained or defined were to change, this function would be affected. A more DIP-compliant approach would be to pass the `DateTimeFormat` as a parameter or inject a factory for obtaining formats.

### DIP-011 [MEDIUM] core/common/src/Instant.kt — Instant.parse
- **Confidence**: Found in 4 scan(s)
- **Lines**: 45–45
- **Type**: class
- **Description**: The `Instant.parse` function directly uses `DateTimeComponents.Formats.ISO_DATE_TIME_OFFSET` and `DateTimeComponents.toInstantUsingOffset()`.
- **Reasoning**: The `Instant.Companion.parse` function has a default parameter `format: DateTimeFormat<DateTimeComponents> = DateTimeComponents.Formats.ISO_DATE_TIME_OFFSET`. This default parameter directly references the concrete `DateTimeComponents.Formats.ISO_DATE_TIME_OFFSET`. Furthermore, it directly calls `DateTimeComponents.toInstantUsingOffset()`. This creates a tight coupling to the `DateTimeComponents` class and its specific format. A more DIP-compliant approach would be to inject or pass in the `DateTimeFormat` and potentially an abstraction for the conversion from `DateTimeComponents` to `Instant`.

### DIP-013 [HIGH] core/common/src/TimeZone.kt — TimeZone.currentSystemDefault
- **Confidence**: Found in 4 scan(s)
- **Lines**: 112–112
- **Type**: class
- **Description**: The `TimeZone.currentSystemDefault()` function directly accesses platform-specific APIs and concrete implementations for timezone retrieval.
- **Reasoning**: The `TimeZone.currentSystemDefault()` function directly interacts with platform-specific APIs (like `java.time.ZoneId.systemDefault()` on JVM, `NSTimeZone.systemTimeZone` on Darwin, or reading system files on Linux) and concrete implementations. This violates DIP because the high-level `TimeZone` concept is directly dependent on low-level, platform-specific details. Instead, it should depend on an abstraction that provides timezone information, and the concrete platform-specific logic should be encapsulated elsewhere, perhaps in a separate module or injected service.

### DIP-014 [MEDIUM] core/common/src/TimeZone.kt — Instant.toLocalDateTime
- **Confidence**: Found in 4 scan(s)
- **Lines**: 367–367
- **Type**: class
- **Description**: The `toLocalDateTime` extension function directly calls `toLocalDateTimeFailing`.
- **Reasoning**: The `toLocalDateTime` extension function directly calls `toLocalDateTimeFailing`. This creates a direct dependency on the implementation of `toLocalDateTimeFailing`. If its internal logic were to change, this extension function would need to be updated. A more DIP-compliant approach would be to abstract the conversion logic.

### DIP-015 [MEDIUM] core/common/src/TimeZone.kt — LocalDateTime.toInstant
- **Confidence**: Found in 4 scan(s)
- **Lines**: 426–426
- **Type**: class
- **Description**: The `toInstant` extension function directly calls `toLocalDateTimeFailing`, `localDateTimeToInstant`, and `toDeprecatedInstant()`.
- **Reasoning**: The `toInstant` extension function directly calls `toLocalDateTimeFailing`, `localDateTimeToInstant`, and `toDeprecatedInstant()`. These are concrete implementations of date/time conversion logic. This creates a tight coupling to these specific implementations. A more DIP-compliant approach would be to abstract these conversion steps, perhaps through interfaces or factories, allowing different strategies to be plugged in.

### DIP-004 [MEDIUM] core/common/src/format/DateTimeComponents.kt — DateTimeComponents.toInstantUsingOffset
- **Confidence**: Found in 3 scan(s)
- **Lines**: 340–356
- **Type**: class
- **Description**: The `toInstantUsingOffset` function directly calls `toLocalDateTime` and `toUtcOffset` on `this` `DateTimeComponents` instance.
- **Reasoning**: The `DateTimeComponents.toInstantUsingOffset` function directly calls `toLocalDateTime()` and `toUtcOffset()` on the `DateTimeComponents` instance itself. While `DateTimeComponents` is the source of truth for its own data, the methods `toLocalDateTime()` and `toUtcOffset()` are essentially converting internal details (`contents`) into higher-level abstractions. The violation is subtle: if the way `DateTimeComponents` exposes its data or the way these conversion methods are implemented were to change, this function would be directly affected. It's a dependency on the internal structure and conversion logic of `DateTimeComponents` rather than a pure abstraction.

### DIP-016 [MEDIUM] core/common/src/TimeZone.kt — LocalDate.atStartOfDayIn
- **Confidence**: Found in 3 scan(s)
- **Lines**: 473–473
- **Type**: class
- **Description**: The `atStartOfDayIn` extension function directly calls `toLocalDateTimeFailing`, `localDateTimeToInstant`, and `toDeprecatedInstant()`.
- **Reasoning**: The `atStartOfDayIn` extension function directly calls `toLocalDateTimeFailing`, `localDateTimeToInstant`, and `toDeprecatedInstant()`. These are concrete implementations of date/time conversion logic. This creates a tight coupling to these specific implementations. A more DIP-compliant approach would be to abstract these conversion steps, perhaps through interfaces or factories, allowing different strategies to be plugged in.

### DIP-017 [MEDIUM] core/common/src/TimeZone.kt — localDateTimeToInstant
- **Confidence**: Found in 3 scan(s)
- **Lines**: 493–493
- **Type**: class
- **Description**: The `localDateTimeToInstant` function directly calls `toLocalDateTimeFailing`, `localDateTimeToInstant`, and `check`.
- **Reasoning**: The `localDateTimeToInstant` function directly calls `toLocalDateTimeFailing`, `localDateTimeToInstant`, and `check`. These are concrete implementations of date/time conversion and validation logic. This creates a tight coupling to these specific implementations. A more DIP-compliant approach would be to abstract these conversion and validation steps, perhaps through interfaces or factories, allowing different strategies to be plugged in.

### DIP-012 [HIGH] core/common/src/Clock.kt — Clock.System.now
- **Confidence**: Found in 2 scan(s)
- **Lines**: 41–41
- **Type**: class
- **Description**: The `Clock.System.now()` function directly calls `kotlin.time.Clock.System.now()`.
- **Reasoning**: The `Clock.System.now()` function in the `kotlinx-datetime` library directly calls `kotlin.time.Clock.System.now()`. This violates the Dependency Inversion Principle because the high-level `kotlinx-datetime` module is depending directly on a concrete implementation (`kotlin.time.Clock.System`) from another module, rather than depending on an abstraction. While `kotlin.time.Clock` is an abstraction, the `kotlinx-datetime.Clock.System` is a specific wrapper around it, and the principle suggests that both high-level and low-level modules should depend on abstractions. Here, the `kotlinx-datetime`'s `Clock.System` is essentially a low-level detail if viewed from the perspective of a system that might want to use `kotlinx-datetime`'s abstractions without tying itself to `kotlin.time`'s specific implementation.

### DIP-018 [LOW] core/common/src/DateTimeUnit.kt — DateTimeUnit.TimeBased.times
- **Confidence**: Found in 2 scan(s)
- **Lines**: 86–86
- **Type**: class
- **Description**: The `times` function directly calls `safeMultiply` and the `TimeBased` constructor.
- **Reasoning**: The `times` function directly calls `safeMultiply` and the `TimeBased` constructor. While `safeMultiply` is an internal utility, the direct instantiation of `TimeBased` couples this function to that specific implementation. If there were different ways to represent time-based units, this would need to be updated. However, given the simplicity and directness of the operation, this is a minor violation.

### DIP-020 [HIGH] core/common/src/format/DateTimeComponents.kt — DateTimeComponents.Formats.ISO_DATE_TIME_OFFSET
- **Confidence**: Found in 2 scan(s)
- **Lines**: 175–215
- **Type**: class
- **Description**: Exposes a concrete format implementation directly.
- **Reasoning**: The `ISO_DATE_TIME_OFFSET` property directly exposes a concrete `DateTimeFormat<DateTimeComponents>` instance. This violates DIP because high-level modules (that might use this format) are depending on a specific low-level detail (the implementation of `ISO_DATE_TIME_OFFSET`). If this format's implementation changes, any code using it directly will be affected. An abstraction for date-time formats would be more appropriate.

### DIP-032 [MEDIUM] core/common/src/format/DateTimeComponents.kt — DateTimeComponents.Formats.ISO_DATE_TIME_OFFSET
- **Confidence**: Found in 2 scan(s)
- **Lines**: 153–167
- **Type**: class
- **Description**: The `DateTimeComponents.Formats.ISO_DATE_TIME_OFFSET` format directly uses `UtcOffset.Formats.ISO` and `DateTimeComponents.Formats.ISO_DATE` without depending on abstractions for these formats.
- **Reasoning**: The `DateTimeComponents.Formats.ISO_DATE_TIME_OFFSET` is defined using a builder pattern that directly references concrete format objects like `ISO_DATE` and `UtcOffset.Formats.ISO`. This creates a direct dependency on these concrete format implementations rather than depending on abstractions for formatting. While the builder pattern itself is an abstraction, the specific formats used within the builder configuration are concrete dependencies. To adhere to DIP, these dependencies should be injected or passed as abstractions (e.g., through constructor parameters or factory methods that accept `DateTimeFormat` instances).

### DIP-002 [MEDIUM] core/common/src/format/DateTimeComponents.kt — DateTimeComponents.Formats.ISO_DATE_TIME_OFFSET
- **Confidence**: Found in 1 scan(s)
- **Lines**: 130–156
- **Type**: class
- **Description**: The `ISO_DATE_TIME_OFFSET` format directly uses concrete formatters for date, time, and offset.
- **Reasoning**: The `DateTimeComponents.Formats.ISO_DATE_TIME_OFFSET` property is defined using a builder pattern that directly instantiates and configures concrete formatters for date (`ISO_DATE`), time (`hour`, `minute`, `second`, etc.), and offset (`UtcOffset.Formats.ISO`). While the builder pattern itself is an abstraction, the specific formatters used within the builder (`ISO_DATE`, `UtcOffset.Formats.ISO`) are concrete implementations. If these underlying formats were to change or if a different strategy for formatting these components was desired, this definition would need to be modified. A more DIP-compliant approach might involve injecting or depending on abstractions for these sub-formats rather than directly referencing them.

### DIP-003 [MEDIUM] core/common/src/format/DateTimeComponents.kt — DateTimeComponents.Format
- **Confidence**: Found in 1 scan(s)
- **Lines**: 61–65
- **Type**: class
- **Description**: The `DateTimeComponents.Format` function directly creates and configures a `DateTimeComponentsFormat.Builder`.
- **Reasoning**: The `DateTimeComponents.Format` function creates a `DateTimeComponentsFormat.Builder` and directly configures it via a lambda. While this is a common and often acceptable pattern for DSLs, it still represents a direct dependency on the concrete `DateTimeComponentsFormat.Builder`. If the internal implementation of how `DateTimeComponents` formats are built were to change, this function would need to be updated. A more abstract approach might involve a factory that provides `DateTimeFormatBuilder.WithDateTimeComponents` instances, allowing for different builder implementations to be injected.

### DIP-005 [MEDIUM] core/common/src/format/Unicode.kt — DateTimeFormatBuilder.byUnicodePattern
- **Confidence**: Found in 1 scan(s)
- **Lines**: 128–252
- **Type**: class
- **Description**: The `byUnicodePattern` extension function directly instantiates and uses concrete `UnicodeFormat` directives.
- **Reasoning**: The `byUnicodePattern` function, which extends `DateTimeFormatBuilder`, parses a Unicode pattern string and then directly instantiates and configures concrete `UnicodeFormat.Directive` implementations (e.g., `UnicodeFormat.Directive.YearMonthBased.Year`, `UnicodeFormat.Directive.TimeBased.HourOfDay`). This creates a tight coupling between the pattern parsing logic and the specific implementations of format directives. If the internal representation or hierarchy of `UnicodeFormat` directives were to change, this function would need to be updated. A more DIP-compliant approach might involve a factory or a registry that provides formatters based on parsed directive types, abstracting away the concrete directive classes.

### DIP-006 [MEDIUM] core/common/src/format/DateTimeFormatBuilder.kt — DateTimeFormatBuilder.alternativeParsing
- **Confidence**: Found in 1 scan(s)
- **Lines**: 302–329
- **Type**: class
- **Description**: The `alternativeParsing` function directly uses `AbstractDateTimeFormatBuilder` and `AppendableFormatStructure`.
- **Reasoning**: The `alternativeParsing` function, when implemented for `AbstractDateTimeFormatBuilder`, directly creates new instances of `Builder` (which extends `AbstractDateTimeFormatBuilder`) and `AppendableFormatStructure`. This creates a direct dependency on these concrete implementation classes. If the internal structure of how formats are built were to change (e.g., if `Builder` or `AppendableFormatStructure` were refactored or replaced), this function would need to be updated. A more abstract approach might involve injecting factories for creating builders or format structures.

### DIP-007 [MEDIUM] core/common/src/format/DateTimeFormatBuilder.kt — DateTimeFormatBuilder.optional
- **Confidence**: Found in 1 scan(s)
- **Lines**: 354–382
- **Type**: class
- **Description**: The `optional` function directly uses `AbstractDateTimeFormatBuilder` and `AppendableFormatStructure`.
- **Reasoning**: Similar to `alternativeParsing`, the `optional` function directly creates new instances of `Builder` and `AppendableFormatStructure`. This creates a direct dependency on these concrete implementation classes. If the internal structure of how formats are built were to change, this function would need to be updated. A more abstract approach might involve injecting factories for creating builders or format structures.

### DIP-008 [MEDIUM] core/common/src/format/DateTimeFormatBuilder.kt — AbstractDateTimeFormatBuilder.appendAlternativeParsingImpl
- **Confidence**: Found in 1 scan(s)
- **Lines**: 413–430
- **Type**: class
- **Description**: The `appendAlternativeParsingImpl` function directly creates and uses concrete `AppendableFormatStructure` instances.
- **Reasoning**: The `appendAlternativeParsingImpl` function, which is an internal implementation detail of the builder pattern, directly creates new `AppendableFormatStructure` instances. This creates a direct dependency on this concrete class. If the internal structure of how formats are built were to change, this function would need to be updated. A more abstract approach might involve injecting factories for creating format structures.

### DIP-009 [MEDIUM] core/common/src/format/DateTimeFormatBuilder.kt — AbstractDateTimeFormatBuilder.appendOptionalImpl
- **Confidence**: Found in 1 scan(s)
- **Lines**: 432–443
- **Type**: class
- **Description**: The `appendOptionalImpl` function directly creates and uses concrete `AppendableFormatStructure` instances.
- **Reasoning**: The `appendOptionalImpl` function, similar to `appendAlternativeParsingImpl`, directly creates new `AppendableFormatStructure` instances. This creates a direct dependency on this concrete class. If the internal structure of how formats are built were to change, this function would need to be updated. A more abstract approach might involve injecting factories for creating format structures.

### DIP-019 [LOW] core/common/src/DeprecatedInstant.kt — kotlin.time.Instant.toDeprecatedInstant
- **Confidence**: Found in 1 scan(s)
- **Lines**: 37–39
- **Type**: class
- **Description**: Directly accesses epochSeconds and nanosecondsOfSecond.
- **Reasoning**: The `toDeprecatedInstant` extension function directly accesses `epochSeconds` and `nanosecondsOfSecond` properties of the standard library's `kotlin.time.Instant` to construct a `kotlinx-datetime.Instant`. This is an implementation detail of the interop layer and not a violation of DIP, as it correctly bridges between two distinct types.

### DIP-021 [HIGH] core/common/src/format/DateTimeComponents.kt — DateTimeComponents.setDateTimeOffset
- **Confidence**: Found in 1 scan(s)
- **Lines**: 391–399
- **Type**: class
- **Description**: Directly calls toLocalDateTime() and Instant.fromEpochSeconds().
- **Reasoning**: The `setDateTimeOffset` function directly depends on `toLocalDateTime()` and `Instant.fromEpochSeconds()` (via `toStdlibInstant()`). This couples the `DateTimeComponents` class to the concrete implementations of date-time conversions. According to DIP, it should depend on abstractions. For instance, if the way `Instant` or `LocalDateTime` are constructed changes, this method would need modification.

### DIP-022 [HIGH] core/common/src/format/DateTimeComponents.kt — DateTimeComponents.toInstantUsingOffset
- **Confidence**: Found in 1 scan(s)
- **Lines**: 511–523
- **Type**: class
- **Description**: Directly uses internal helper functions and constants for calculations.
- **Reasoning**: The `toInstantUsingOffset` function directly uses internal helper functions like `requireParsedField`, `safeMultiply`, `safeAdd`, and constants like `SECONDS_PER_10000_YEARS`. This creates a tight coupling to the internal implementation details of date-time calculations, violating DIP. These operations should ideally be exposed through a more abstract interface or service if they are intended to be swappable or tested independently.

### DIP-023 [HIGH] core/common/src/format/DateTimeComponents.kt — DateTimeComponents.toInstantUsingOffset
- **Confidence**: Found in 1 scan(s)
- **Lines**: 525–528
- **Type**: class
- **Description**: Directly calls toStdlibInstant() for replacement.
- **Reasoning**: The `replaceWith` argument for the `toInstantUsingOffset` function directly calls `instant.toStdlibInstant()`. This couples the `kotlinx-datetime` `toInstantUsingOffset` operation to the standard library's `Instant` and the `toStdlibInstant` conversion. If the standard library's behavior or the conversion were to change, this would directly impact the `kotlinx-datetime` version.

### DIP-024 [HIGH] core/common/src/DateTimePeriod.kt — DateTimePeriod.parse
- **Confidence**: Found in 1 scan(s)
- **Lines**: 429–433
- **Type**: class
- **Description**: Directly calls parseImpl with a lambda that throws DateTimeFormatException.
- **Reasoning**: The `parse` function directly calls `parseImpl` and provides a lambda that throws a `DateTimeFormatException`. This means that the error handling strategy for parsing is hardcoded within this function. According to DIP, high-level modules should not depend on low-level modules; both should depend on abstractions. The error reporting mechanism could be abstracted.

### DIP-025 [HIGH] core/common/src/DateTimePeriod.kt — DateTimePeriod.parseOrNull
- **Confidence**: Found in 1 scan(s)
- **Lines**: 479–485
- **Type**: class
- **Description**: Directly calls parseImpl with a lambda that returns null.
- **Reasoning**: The `parseOrNull` function directly calls `parseImpl` and provides a lambda that returns `null` on failure. This hardcodes the null-returning behavior for parsing errors. DIP suggests depending on abstractions; the error handling strategy (returning null vs. throwing) could be abstracted or passed in as a parameter.

### DIP-026 [HIGH] core/common/src/DateTimePeriod.kt — DatePeriod.parse
- **Confidence**: Found in 1 scan(s)
- **Lines**: 609–613
- **Type**: class
- **Description**: Directly calls DateTimePeriod.parse and checks the type.
- **Reasoning**: The `DatePeriod.parse` function directly calls `DateTimePeriod.parse` and then checks the returned type. This creates a dependency on the concrete implementation of `DateTimePeriod.parse`. A more DIP-compliant approach would be to have an abstraction for parsing date-based periods, or to inject the parsing logic.

### DIP-027 [HIGH] core/common/src/DateTimePeriod.kt — DatePeriod.parseOrNull
- **Confidence**: Found in 1 scan(s)
- **Lines**: 631–634
- **Type**: class
- **Description**: Directly calls DateTimePeriod.parseOrNull and casts the result.
- **Reasoning**: The `DatePeriod.parseOrNull` function directly calls `DateTimePeriod.parseOrNull` and then casts the result. This creates a dependency on the concrete implementation of `DateTimePeriod.parseOrNull`. A more DIP-compliant approach would be to have an abstraction for parsing date-based periods, or to inject the parsing logic.

### DIP-028 [LOW] core/common/src/DateTimePeriod.kt — DateTimePeriod.plus
- **Confidence**: Found in 1 scan(s)
- **Lines**: 704–708
- **Type**: class
- **Description**: Directly calls safeAdd for arithmetic operations.
- **Reasoning**: The `plus` operator function directly calls `safeAdd` for arithmetic operations on its components. While `safeAdd` is an internal utility, direct calls like this create a dependency on its specific implementation. If the arithmetic logic were to be provided by a more abstract service, this would be more aligned with DIP.

### DIP-029 [LOW] core/common/src/DateTimePeriod.kt — DatePeriod.plus
- **Confidence**: Found in 1 scan(s)
- **Lines**: 678–682
- **Type**: class
- **Description**: Directly calls safeAdd for arithmetic operations.
- **Reasoning**: The `plus` operator function directly calls `safeAdd` for arithmetic operations on its components. While `safeAdd` is an internal utility, direct calls like this create a dependency on its specific implementation. If the arithmetic logic were to be provided by a more abstract service, this would be more aligned with DIP.

### DIP-030 [HIGH] core/common/src/format/DateTimeComponents.kt — DateTimeComponents.toInstantUsingOffset
- **Confidence**: Found in 1 scan(s)
- **Lines**: 320–341
- **Type**: class
- **Description**: The `toInstantUsingOffset` function in `DateTimeComponents` depends on `kotlin.time.Instant`.
- **Reasoning**: The `DateTimeComponents.toInstantUsingOffset` function directly uses `kotlin.time.Instant.fromEpochSeconds` and `kotlin.time.Instant.fromEpochSeconds` to construct an `Instant`. This creates a dependency on a concrete low-level implementation (`kotlin.time.Instant`) from a higher-level module (`DateTimeComponents`), violating the Dependency Inversion Principle. Abstractions should not depend on details; details should depend on abstractions. Here, the `DateTimeComponents` module is depending on the concrete `kotlin.time.Instant` class.

### DIP-031 [HIGH] core/common/src/Clock.kt — TimeSource.asClock
- **Confidence**: Found in 1 scan(s)
- **Lines**: 127–134
- **Type**: class
- **Description**: The `asClock` function depends on `origin.toStdlibInstant` and `kotlin.time.Clock`.
- **Reasoning**: The `TimeSource.asClock` function calls `origin.toStdlibInstant()`, which depends on `kotlin.time.Instant`, and then creates a `kotlinx.datetime.Clock` that delegates to a `kotlin.time.Clock`. This creates a dependency on concrete low-level implementations (`kotlin.time.Instant` and `kotlin.time.Clock`) from a higher-level abstraction (`TimeSource`), violating the Dependency Inversion Principle. Abstractions should not depend on details; details should depend on abstractions. Here, the `TimeSource` abstraction is depending on concrete `kotlin.time.Instant` and `kotlin.time.Clock` implementations.

### DIP-033 [MEDIUM] core/common/src/Instant.kt — LocalDateTime.plus
- **Confidence**: Found in 1 scan(s)
- **Lines**: 718–719
- **Type**: class
- **Description**: The `LocalDateTime.plus` function directly calls `date.plus(value, unit).atTime(time)`, creating dependencies on concrete implementations of date addition and time combination.
- **Reasoning**: The `LocalDateTime.plus` function directly calls `date.plus(value, unit).atTime(time)`. This creates a direct dependency on the concrete `plus` function for `LocalDate` and the `atTime` function for combining date and time. According to DIP, these operations should depend on abstractions, allowing for different date arithmetic or date-time combination strategies to be used.

### DIP-034 [MEDIUM] core/common/src/Instant.kt — LocalDateTime.plus
- **Confidence**: Found in 1 scan(s)
- **Lines**: 722–723
- **Type**: class
- **Description**: The `LocalDateTime.plus` function directly calls `date.plus(value, unit).atTime(time)`, creating dependencies on concrete implementations of date addition and time combination.
- **Reasoning**: The `LocalDateTime.plus` function directly calls `date.plus(value, unit).atTime(time)`. This creates a direct dependency on the concrete `plus` function for `LocalDate` and the `atTime` function for combining date and time. According to DIP, these operations should depend on abstractions, allowing for different date arithmetic or date-time combination strategies to be used.

### DIP-035 [HIGH] core/common/src/format/DateTimeComponents.kt — DateTimeComponents.toInstantUsingOffset
- **Confidence**: Found in 1 scan(s)
- **Lines**: 349–370
- **Type**: class
- **Description**: The `toInstantUsingOffset` function directly instantiates `Instant`.
- **Reasoning**: The `toInstantUsingOffset` function directly calls `Instant.fromEpochSeconds()` to create a new `Instant`. This violates DIP because it depends on the concrete `Instant` class. Instead, it should depend on an abstraction that can create instants, or receive an `Instant` instance via dependency injection.

### DIP-036 [HIGH] core/common/src/format/DateTimeComponents.kt — DateTimeComponents.toInstantUsingOffset
- **Confidence**: Found in 1 scan(s)
- **Lines**: 373–375
- **Type**: class
- **Description**: The deprecated overload of `toInstantUsingOffset` directly depends on concrete `kotlinx.datetime.Instant` and `kotlin.time.Instant`.
- **Reasoning**: The deprecated overload of `toInstantUsingOffset` directly calls `instant.toStdlibInstant()` and `this.toStdlibInstant().toDeprecatedInstant()`. This indicates a direct dependency on concrete implementations of `Instant` from both `kotlinx.datetime` and `kotlin.time`, violating DIP. It should depend on abstractions or receive these as injected dependencies.

### DIP-037 [HIGH] core/common/src/Instant.kt — localDateTimeToInstant
- **Confidence**: Found in 1 scan(s)
- **Lines**: 608–610
- **Type**: class
- **Description**: The `localDateTimeToInstant` function directly depends on `LocalDateTime.toInstant` and `TimeZone`.
- **Reasoning**: The `localDateTimeToInstant` function directly calls `LocalDateTime.toInstant` and uses a concrete `TimeZone` object. To adhere to DIP, it should depend on an abstraction of the time zone and the conversion process, allowing for different time zone implementations or conversion strategies to be injected.

### DIP-038 [HIGH] core/common/src/Instant.kt — check
- **Confidence**: Found in 1 scan(s)
- **Lines**: 614–615
- **Type**: class
- **Description**: The `check` extension function directly depends on `toLocalDateTimeFailing` and `TimeZone`.
- **Reasoning**: The `check` extension function directly depends on `toLocalDateTimeFailing` and a concrete `TimeZone` object. To adhere to DIP, it should depend on an abstraction of the time zone and the validation/conversion process, allowing for different time zone implementations or validation strategies to be injected.

### DIP-039 [HIGH] core/common/src/Instant.kt — LocalDateTime.plus
- **Confidence**: Found in 1 scan(s)
- **Lines**: 618–619
- **Type**: class
- **Description**: The `plus` extension function directly depends on `LocalDate.plus` and `DateTimeUnit.DateBased`.
- **Reasoning**: The `plus` extension function directly depends on `LocalDate.plus` and a concrete `DateTimeUnit.DateBased`. Since `LocalDate.plus` violates DIP, this method also inherits that violation. It should ideally depend on an abstraction of the date arithmetic operations.

### DIP-040 [HIGH] core/common/src/LocalTime.kt — LocalTime.Companion.orNull
- **Confidence**: Found in 1 scan(s)
- **Lines**: 128–137
- **Type**: class
- **Description**: The `orNull` function directly calls the `LocalTime` constructor.
- **Reasoning**: The `LocalTime.orNull` function directly calls the `LocalTime` constructor (`LocalTime(hour, minute, second, nanosecond)`). This violates DIP because it depends on the concrete `LocalTime` class instead of an abstraction. A more DIP-compliant approach would be to have a factory or dependency injection mechanism that provides `LocalTime` instances.

### DIP-041 [HIGH] core/common/src/LocalTime.kt — LocalTime.Companion.parse
- **Confidence**: Found in 1 scan(s)
- **Lines**: 161–164
- **Type**: class
- **Description**: The `LocalTime.parse()` function directly depends on concrete `DateTimeFormat` and `LocalTime` classes.
- **Reasoning**: The `LocalTime.parse()` function directly instantiates and uses a concrete implementation of `DateTimeFormat` (`getIsoTimeFormat()`). To adhere to DIP, it should depend on an abstraction of `DateTimeFormat`, allowing for different formatting strategies to be plugged in. This direct dependency on a concrete formatting implementation violates DIP.

### DIP-042 [HIGH] core/common/src/LocalTime.kt — LocalTime.fromSecondOfDay
- **Confidence**: Found in 1 scan(s)
- **Lines**: 194–214
- **Type**: class
- **Description**: The `fromSecondOfDay` function directly depends on the concrete `LocalTime` class.
- **Reasoning**: The `fromSecondOfDay` function is a factory method that directly creates an instance of the concrete `LocalTime` class. Instead, it should depend on an abstraction, such as an interface or an abstract class that represents a time, and receive its dependencies through dependency injection. This direct instantiation violates the Dependency Inversion Principle by tightly coupling the factory method to the concrete implementation.

### DIP-043 [HIGH] core/common/src/LocalTime.kt — LocalTime.fromMillisecondOfDay
- **Confidence**: Found in 1 scan(s)
- **Lines**: 238–258
- **Type**: class
- **Description**: The `fromMillisecondOfDay` function directly depends on the concrete `LocalTime` class.
- **Reasoning**: The `fromMillisecondOfDay` function is a factory method that directly creates an instance of the concrete `LocalTime` class. Instead, it should depend on an abstraction, such as an interface or an abstract class that represents a time, and receive its dependencies through dependency injection. This direct instantiation violates the Dependency Inversion Principle by tightly coupling the factory method to the concrete implementation.

### DIP-044 [HIGH] core/common/src/LocalTime.kt — LocalTime.fromNanosecondOfDay
- **Confidence**: Found in 1 scan(s)
- **Lines**: 282–302
- **Type**: class
- **Description**: The `fromNanosecondOfDay` function directly depends on the concrete `LocalTime` class.
- **Reasoning**: The `fromNanosecondOfDay` function is a factory method that directly creates an instance of the concrete `LocalTime` class. Instead, it should depend on an abstraction, such as an interface or an abstract class that represents a time, and receive its dependencies through dependency injection. This direct instantiation violates the Dependency Inversion Principle by tightly coupling the factory method to the concrete implementation.

### DIP-045 [HIGH] core/common/src/LocalTime.kt — LocalTime.Format
- **Confidence**: Found in 1 scan(s)
- **Lines**: 314–319
- **Type**: class
- **Description**: The `LocalTime.Format` function directly calls concrete formatting builder methods.
- **Reasoning**: The `LocalTime.Format` function uses a builder API (`DateTimeFormatBuilder.WithTime.() -> Unit`). Inside this builder, methods like `hour()`, `char(':')`, `minute()`, etc., are called directly. These methods are concrete implementations of formatting logic. To adhere to DIP, the builder should ideally operate on abstractions of these formatting components, allowing for different formatting strategies to be plugged in. This direct usage of concrete formatting methods violates DIP.

### DIP-046 [LOW] core/common/src/LocalTime.kt — LocalTime.nanosecond
- **Confidence**: Found in 1 scan(s)
- **Lines**: 500–504
- **Type**: class
- **Description**: The getter/setter for `nanosecond` directly accesses `contents.time.nanosecond`.
- **Reasoning**: The getter and setter for the `nanosecond` property directly access `contents.time.nanosecond`. While `contents.time` might be an abstraction, the direct access to a specific field like `nanosecond` without going through a more abstract interface for time components could be seen as a minor violation of DIP if `contents.time` is a concrete implementation. However, given that `contents.time` itself is likely an internal detail, this is a low-severity issue. The principle is more about depending on abstractions of *services* or *dependencies*, not necessarily every internal field.

### DIP-047 [HIGH] core/common/src/LocalTime.kt — LocalTime.atDate
- **Confidence**: Found in 1 scan(s)
- **Lines**: 624–626
- **Type**: class
- **Description**: The `atDate` function directly calls `LocalDateTime` constructor with components.
- **Reasoning**: The `atDate` function directly calls the `LocalDateTime` constructor with extracted components (`year`, `month`, `day`, `hour`, `minute`, `second`, `nanosecond`). This violates DIP because it depends on the concrete `LocalDateTime` class. It should ideally rely on an abstraction or factory for creating `LocalDateTime` objects.

### DIP-048 [HIGH] core/common/src/LocalTime.kt — LocalTime.atDate
- **Confidence**: Found in 1 scan(s)
- **Lines**: 641–645
- **Type**: class
- **Description**: The `atDate` function directly calls `LocalDateTime` constructor with components.
- **Reasoning**: The `atDate` function directly calls the `LocalDateTime` constructor with extracted components (`year`, `month`, `day`, `hour`, `minute`, `second`, `nanosecond`). This violates DIP because it depends on the concrete `LocalDateTime` class. It should ideally rely on an abstraction or factory for creating `LocalDateTime` objects.

### DIP-049 [HIGH] core/common/src/LocalTime.kt — LocalTime.atDate
- **Confidence**: Found in 1 scan(s)
- **Lines**: 659–660
- **Type**: class
- **Description**: The `atDate` function directly calls `LocalDateTime` constructor with `date` and `this`.
- **Reasoning**: The `atDate` function directly calls the `LocalDateTime` constructor with a `LocalDate` and `this` (the `LocalTime` itself). This violates DIP because it depends on the concrete `LocalDateTime` class. It should ideally rely on an abstraction or factory for creating `LocalDateTime` objects.

### DIP-050 [HIGH] src/main/kotlin/com/example/example/ExampleService.kt — ExampleService
- **Confidence**: Found in 1 scan(s)
- **Lines**: 5–17
- **Type**: class
- **Description**: ExampleService directly instantiates a concrete implementation of Repository.
- **Reasoning**: The ExampleService class directly instantiates `DatabaseRepository()` within its constructor. This creates a tight coupling to the concrete `DatabaseRepository` implementation. According to DIP, high-level modules (like ExampleService) should depend on abstractions (interfaces or abstract classes) rather than concrete low-level implementations. The `Repository` interface exists, but it is not being used for dependency injection. This violates DIP because ExampleService is dependent on a detail (DatabaseRepository) rather than an abstraction.

### DIP-051 [HIGH] com/example/di/problem/HighLevelModule.kt — HighLevelModule
- **Confidence**: Found in 1 scan(s)
- **Lines**: 5–14
- **Type**: class
- **Description**: HighLevelModule directly instantiates a concrete low-level module.
- **Reasoning**: The HighLevelModule class directly instantiates `LowLevelModuleImpl` within its constructor. This creates a tight coupling between the high-level module and the concrete implementation of the low-level module. According to DIP, both high-level and low-level modules should depend on abstractions. The HighLevelModule should depend on an abstraction (e.g., an interface like `LowLevelModule`) and receive an instance of a concrete implementation through dependency injection, rather than creating it directly.

### DIP-052 [HIGH] app/src/main/java/com/example/app/data/repository/UserRepository.kt — UserRepository
- **Confidence**: Found in 1 scan(s)
- **Lines**: 7–20
- **Type**: class
- **Description**: Depends on concrete implementation of UserLocalDataSource instead of an abstraction.
- **Reasoning**: The UserRepository class directly instantiates UserLocalDataSource, which is a concrete implementation of a low-level data source. According to DIP, high-level modules (like repositories often are in terms of business logic) should depend on abstractions, not concrete implementations. This tight coupling makes it difficult to swap out the data source implementation (e.g., for testing with a mock or for using a different database) without modifying the UserRepository.

### DIP-053 [HIGH] app/src/main/java/com/example/app/domain/usecase/GetUserProfileUseCase.kt — GetUserProfileUseCase
- **Confidence**: Found in 1 scan(s)
- **Lines**: 8–15
- **Type**: class
- **Description**: Depends on concrete implementation of UserRepository instead of an abstraction.
- **Reasoning**: The GetUserProfileUseCase class directly instantiates UserRepository. Repositories often encapsulate data access logic and can be considered lower-level modules compared to use cases which orchestrate business logic. DIP dictates that both should depend on abstractions. By depending on the concrete UserRepository, the use case is tightly coupled to this specific implementation, hindering testability and the ability to swap repository implementations.

### DIP-054 [HIGH] app/src/main/java/com/example/app/presentation/viewmodel/UserViewModel.kt — UserViewModel
- **Confidence**: Found in 1 scan(s)
- **Lines**: 10–24
- **Type**: class
- **Description**: Depends on concrete implementation of GetUserProfileUseCase instead of an abstraction.
- **Reasoning**: The UserViewModel class directly instantiates GetUserProfileUseCase. ViewModels often represent the presentation layer and should depend on abstractions of business logic (use cases). By depending on the concrete GetUserProfileUseCase, the ViewModel is tightly coupled to this specific use case implementation, making it difficult to substitute for testing or to introduce alternative business logic flows.
