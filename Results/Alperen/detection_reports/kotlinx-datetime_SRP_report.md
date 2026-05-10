# SRP Violation Report: kotlinx-datetime

## Summary
- **Total unique issues**: 74
- **High severity**: 35
- **Medium severity**: 33
- **Low severity**: 6
- **Found by multiple scans**: 13/74

## Issues

### SRP-002 [MEDIUM] core/common/src/DateTimePeriod.kt — DateTimePeriod.Companion.parse
- **Confidence**: Found in 5 scan(s)
- **Lines**: 139–270
- **Type**: method
- **Description**: The parse method contains extensive string parsing logic, mixing data representation with complex deserialization.
- **Reasoning**: The `parse` method for DateTimePeriod is quite large and implements a detailed state machine for parsing ISO 8601 duration strings. While parsing is a necessary function for value types, the complexity and length of this method suggest that the parsing logic could be extracted into a dedicated parser class or utility, separating the concern of data representation from complex string deserialization.

### SRP-001 [HIGH] core/common/src/format/DateTimeComponents.kt — DateTimeComponents
- **Confidence**: Found in 4 scan(s)
- **Lines**: 30–339
- **Type**: class
- **Description**: The DateTimeComponents class mixes multiple responsibilities: data container, data conversion, and acting as a factory/registry for formatters.
- **Reasoning**: DateTimeComponents serves as a mutable data container for incomplete datetime fields. It also provides methods to populate these fields from complete datetime objects (`set*` methods) and to convert its fields back into complete datetime objects (`to*` methods), including complex arithmetic in `toInstantUsingOffset`. Furthermore, its companion object and nested `Formats` object are responsible for creating and providing `DateTimeFormat` instances, which is a distinct concern from being the data container itself. This violates SRP by having multiple reasons to change (e.g., changes to data structure, changes to conversion logic, changes to formatting API).

### SRP-003 [MEDIUM] core/common/src/LocalDate.kt — LocalDate
- **Confidence**: Found in 4 scan(s)
- **Lines**: 54–178
- **Type**: class
- **Description**: The LocalDate class mixes data representation with string serialization/deserialization and format definition.
- **Reasoning**: LocalDate is primarily responsible for representing a date. However, it also includes methods for converting itself to a string (`toString`), parsing strings into LocalDate instances (`parse` in companion object), and defining/providing formatting capabilities (`companion object Format`, `object Formats`). These formatting and parsing concerns are distinct from the core responsibility of representing a date, leading to multiple reasons for the class to change.

### SRP-004 [MEDIUM] core/common/src/LocalDateTime.kt — LocalDateTime
- **Confidence**: Found in 3 scan(s)
- **Lines**: 62–204
- **Type**: class
- **Description**: The LocalDateTime class mixes data representation with string serialization/deserialization and format definition.
- **Reasoning**: LocalDateTime is primarily responsible for representing a civil date and time. However, it also includes methods for converting itself to a string (`toString`), parsing strings into LocalDateTime instances (`parse` in companion object), and defining/providing formatting capabilities (`companion object Format`, `object Formats`). These formatting and parsing concerns are distinct from the core responsibility of representing a datetime, leading to multiple reasons for the class to change.

### SRP-013 [MEDIUM] core/common/src/YearMonth.kt — YearMonth
- **Confidence**: Found in 3 scan(s)
- **Lines**: 40–140
- **Type**: class
- **Description**: The YearMonth class mixes data representation with string serialization/deserialization and format definition.
- **Reasoning**: YearMonth is primarily responsible for representing a year and month. However, it also includes methods for converting itself to a string (`toString`), parsing strings into YearMonth instances (`parse` in companion object), and defining/providing formatting capabilities (`companion object Format`, `object Formats`). These formatting and parsing concerns are distinct from the core responsibility of representing a year-month, leading to multiple reasons for the class to change.

### SRP-015 [MEDIUM] core/common/src/UtcOffset.kt — UtcOffset
- **Confidence**: Found in 3 scan(s)
- **Lines**: 30–120
- **Type**: class
- **Description**: The UtcOffset class mixes data representation with string serialization/deserialization and format definition.
- **Reasoning**: UtcOffset is primarily responsible for representing a fixed offset from UTC. However, it also includes methods for converting itself to a string (`toString`), parsing strings into UtcOffset instances (`parse` in companion object), and defining/providing formatting capabilities (`companion object Format`, `object Formats`). These formatting and parsing concerns are distinct from the core responsibility of representing an offset, leading to multiple reasons for the class to change.

### SRP-034 [HIGH] core/common/src/DeprecatedInstant.kt — Instant.parse
- **Confidence**: Found in 3 scan(s)
- **Lines**: 142–145
- **Type**: method
- **Description**: The companion object method for Instant handles parsing a string, which is a separate responsibility from representing an instant in time.
- **Reasoning**: The core responsibility of an 'Instant' class is to represent a specific point in time. Parsing a string into an 'Instant' involves string manipulation, format interpretation, and error handling, which are distinct concerns. This method delegates to other parsing logic, but its very existence on the 'Instant' companion object indicates a violation.

### SRP-007 [HIGH] core/common/src/Instant.kt — Instant.periodUntil(other: Instant, timeZone: TimeZone)
- **Confidence**: Found in 2 scan(s)
- **Lines**: 68–85
- **Type**: method
- **Description**: The Instant.periodUntil extension function calculates a DateTimePeriod between two instants, involving complex calendar-based arithmetic and time zone rules.
- **Reasoning**: This extension function calculates the difference between two instants as a DateTimePeriod. This involves converting instants to LocalDateTime, performing date arithmetic on LocalDate, and handling time zone offsets. This is a complex piece of business logic that combines time interval calculation with calendar and time zone rules, violating SRP.

### SRP-008 [HIGH] core/common/src/Instant.kt — Instant.until(other: Instant, unit: DateTimeUnit, timeZone: TimeZone)
- **Confidence**: Found in 2 scan(s)
- **Lines**: 87–105
- **Type**: method
- **Description**: The Instant.until extension function calculates the number of units between instants, involving complex calendar-based arithmetic and time zone rules.
- **Reasoning**: This extension function calculates the number of DateTimeUnits between two instants. For `DateBased` units, it performs complex logic involving conversions to `LocalDateTime`, `LocalDate` arithmetic, and `TimeZone` considerations. This mixes simple time interval calculation with complex calendar and time zone rules, violating SRP.

### SRP-014 [HIGH] core/common/src/TimeZone.kt — TimeZone.Companion
- **Confidence**: Found in 2 scan(s)
- **Lines**: 57–105
- **Type**: class
- **Description**: The TimeZone.Companion object mixes time zone rule provision with platform-specific discovery and loading of time zone definitions.
- **Reasoning**: The `TimeZone` class's core responsibility is to provide rules for converting between Instant and LocalDateTime. However, its companion object methods (`currentSystemDefault`, `of`, `availableZoneIds`) are heavily involved in platform-specific I/O and system interactions (e.g., reading system files, registry, using JS Intl API) to discover, load, and instantiate time zone definitions. This mixes the 'time zone rule provider' responsibility with a 'time zone registry/loader' responsibility, which are distinct concerns and give the companion object multiple reasons to change.

### SRP-021 [MEDIUM] core/common/src/LocalTime.kt — LocalTime
- **Confidence**: Found in 2 scan(s)
- **Lines**: 21–304
- **Type**: class
- **Description**: The LocalTime class combines data representation, ISO 8601 formatting/parsing, and acts as a factory for its instances and associated formats.
- **Reasoning**: Similar to `LocalDate`, this class has multiple reasons to change:
1. Its core responsibility is to represent a time (`hour`, `minute`, `second`, `nanosecond`).
2. It includes `toString()` for ISO 8601 formatting and `parse()` for parsing. Changes to ISO 8601 time formatting/parsing would require modifications.
3. The companion object's `orNull`, `fromSecondOfDay`, `fromMillisecondOfDay`, `fromNanosecondOfDay`, and `Format` methods, along with constructors, act as factories, a separate concern.
4. The `Formats` object defines predefined formats, also a distinct responsibility.
5. It provides conversion to `LocalDateTime` (`atDate`), which is a bridging responsibility.

### SRP-033 [LOW] core/common/src/internal/format/parser/ParserOperation.kt — TimeZoneParserOperation.Companion.validateTimeZone
- **Confidence**: Found in 2 scan(s)
- **Lines**: 139–204
- **Type**: method
- **Description**: The `validateTimeZone` method in `TimeZoneParserOperation.Companion` contains complex state machine logic for validating various time zone string formats, which could be extracted into a dedicated validator.
- **Reasoning**: The primary responsibility of `TimeZoneParserOperation` is to consume a time zone string and set it. The `validateTimeZone` method, however, contains a detailed state machine (`State` enum and `when` logic) to validate multiple complex time zone string formats (prefixes, signs, time components, IANA parts). This validation logic is quite extensive and could be considered a separate responsibility. If the rules for time zone string validation change, this method would need modification, independently of how the parsed string is then assigned.

### SRP-035 [MEDIUM] core/common/src/DeprecatedInstant.kt — Instant.toString
- **Confidence**: Found in 2 scan(s)
- **Lines**: 115–119
- **Type**: method
- **Description**: The toString method performs specific ISO 8601 formatting logic, which is a formatting responsibility.
- **Reasoning**: While a toString method is standard for debugging, when it implements a specific, standardized formatting (like ISO 8601 with details about UTC-SLS and trailing zeros) and is used as part of the public API for formatted output, it takes on a 'formatting' responsibility distinct from merely representing the data.

### SRP-005 [HIGH] core/common/src/Instant.kt — Instant.plus(period: DateTimePeriod, timeZone: TimeZone)
- **Confidence**: Found in 1 scan(s)
- **Lines**: 30–44
- **Type**: method
- **Description**: The Instant.plus extension function performs complex calendar-based arithmetic involving multiple datetime types and time zone rules.
- **Reasoning**: This extension function's responsibility is to add a DateTimePeriod to an Instant. However, it involves significant business logic by converting the Instant to LocalDateTime, performing date arithmetic on LocalDate, converting back to Instant, and handling nanosecond adjustments, all while considering TimeZone rules. This mixes simple time arithmetic with complex calendar-based arithmetic and time zone conversions, which are distinct responsibilities.

### SRP-006 [HIGH] core/common/src/Instant.kt — Instant.minus(period: DateTimePeriod, timeZone: TimeZone)
- **Confidence**: Found in 1 scan(s)
- **Lines**: 56–66
- **Type**: method
- **Description**: The Instant.minus extension function performs complex calendar-based arithmetic by delegating to Instant.plus, inheriting its SRP violation.
- **Reasoning**: This extension function delegates its complex calendar-based arithmetic to the `Instant.plus` function, which has been identified as an SRP violation. Therefore, it inherits the same violation by orchestrating complex date/time calculations across different datetime types and time zones.

### SRP-009 [HIGH] core/common/src/Instant.kt — Instant.plus(value: Long, unit: DateTimeUnit, timeZone: TimeZone)
- **Confidence**: Found in 1 scan(s)
- **Lines**: 204–218
- **Type**: method
- **Description**: The Instant.plus extension function (long value, DateTimeUnit, TimeZone) performs complex calendar-based arithmetic and time zone conversions.
- **Reasoning**: This is a core arithmetic method for Instant. When the `unit` is `DateBased`, it involves converting the Instant to LocalDateTime, performing date arithmetic on LocalDate, and converting back to Instant, all while respecting TimeZone rules. This is a complex orchestration of different domain concepts and business logic, violating SRP.

### SRP-010 [HIGH] core/common/src/Instant.kt — Instant.minus(value: Long, unit: DateTimeUnit, timeZone: TimeZone)
- **Confidence**: Found in 1 scan(s)
- **Lines**: 220–226
- **Type**: method
- **Description**: The Instant.minus extension function (long value, DateTimeUnit, TimeZone) delegates to Instant.plus, inheriting its SRP violation.
- **Reasoning**: This extension function delegates its complex calendar-based arithmetic to the `Instant.plus` function, which has been identified as an SRP violation. Therefore, it inherits the same violation by orchestrating complex date/time calculations across different datetime types and time zones.

### SRP-011 [MEDIUM] core/common/src/Instant.kt — Instant.format
- **Confidence**: Found in 1 scan(s)
- **Lines**: 260–265
- **Type**: method
- **Description**: The Instant.format extension function adds a formatting responsibility to the Instant type.
- **Reasoning**: While extension functions are a way to add functionality without modifying the core class, this function adds a specific formatting responsibility to the `Instant` type. A dedicated `InstantFormatter` class or a top-level utility function would better separate the concern of formatting from the core responsibility of representing a point in time.

### SRP-012 [MEDIUM] core/common/src/LocalIsoWeekDate.kt — LocalIsoWeekDate.Companion.parse
- **Confidence**: Found in 1 scan(s)
- **Lines**: 105–172
- **Type**: method
- **Description**: The parse method contains extensive string parsing logic, mixing data representation with complex deserialization.
- **Reasoning**: The `parse` method for LocalIsoWeekDate is quite large and implements a detailed state machine for parsing ISO 8601 week date strings, including specific validation for year length and format. While parsing is a necessary function for value types, the complexity and length of this method suggest that the parsing logic could be extracted into a dedicated parser class or utility, separating the concern of data representation from complex string deserialization.

### SRP-016 [LOW] core/common/src/format/LocalTimeFormat.kt — IncompleteLocalTime.toLocalTime
- **Confidence**: Found in 1 scan(s)
- **Lines**: 53–70
- **Type**: method
- **Description**: The toLocalTime method performs validation logic in addition to converting incomplete data to a complete LocalTime object.
- **Reasoning**: The `IncompleteLocalTime` class is designed to be a mutable container for potentially incomplete or inconsistent time components during parsing. Its `toLocalTime` method is responsible for converting these components into a valid `LocalTime` object. However, it includes `require` calls for validation (e.g., checking consistency between `hour` and `hourOfAmPm`). While necessary for correctness, this mixes the responsibility of data conversion with explicit validation logic, which could be seen as a minor SRP violation for an internal helper class.

### SRP-017 [LOW] core/common/src/format/LocalDateFormat.kt — IncompleteLocalDate.toLocalDate
- **Confidence**: Found in 1 scan(s)
- **Lines**: 57–93
- **Type**: method
- **Description**: The toLocalDate method performs validation logic in addition to converting incomplete data to a complete LocalDate object.
- **Reasoning**: Similar to `IncompleteLocalTime.toLocalTime`, this method in `IncompleteLocalDate` is responsible for converting incomplete date components into a valid `LocalDate`. It includes `require` calls for validation (e.g., checking consistency between day of year, month, and day). This mixes data conversion with explicit validation logic, which is a minor SRP violation for an internal helper class.

### SRP-018 [LOW] core/common/src/format/YearMonthFormat.kt — IncompleteYearMonth.toYearMonth
- **Confidence**: Found in 1 scan(s)
- **Lines**: 53–57
- **Type**: method
- **Description**: The toYearMonth method performs validation logic in addition to converting incomplete data to a complete YearMonth object.
- **Reasoning**: Similar to other `Incomplete*` classes, `IncompleteYearMonth.toYearMonth` is responsible for converting incomplete year-month components into a valid `YearMonth`. It includes `require` calls for validation. This mixes data conversion with explicit validation logic, which is a minor SRP violation for an internal helper class.

### SRP-019 [LOW] core/common/src/format/UtcOffsetFormat.kt — IncompleteUtcOffset.toUtcOffset
- **Confidence**: Found in 1 scan(s)
- **Lines**: 62–66
- **Type**: method
- **Description**: The toUtcOffset method performs validation logic in addition to converting incomplete data to a complete UtcOffset object.
- **Reasoning**: Similar to other `Incomplete*` classes, `IncompleteUtcOffset.toUtcOffset` is responsible for converting incomplete UTC offset components into a valid `UtcOffset`. It implicitly relies on the `UtcOffset` constructor for validation. This mixes data conversion with explicit validation logic, which is a minor SRP violation for an internal helper class.

### SRP-020 [HIGH] core/common/src/DateTimeComponents.kt — DateTimeComponents
- **Confidence**: Found in 1 scan(s)
- **Lines**: 29–328
- **Type**: class
- **Description**: The DateTimeComponents class combines multiple responsibilities: acting as a generic data container for datetime fields, providing conversion logic to/from specific domain types, and defining/building datetime formats.
- **Reasoning**: The class has several distinct reasons to change: 
1. Its internal structure (fields like `year`, `monthNumber`, `day`, `hour`, `minute`, `offsetHours`, `timeZoneId`) could change if the representation of datetime components evolves.
2. Its conversion methods (`setDateTime`, `toLocalDate`, `toInstantUsingOffset`, etc.) could change if the rules for mapping between generic components and specific domain types (like `LocalDate`, `Instant`) are altered.
3. Its `Formats` object and `Format` builder methods (`companion object Format`) are responsible for defining and constructing formatters, which is a separate concern from data storage or conversion. Changes to formatting standards or the DSL for building formats would require modifying these parts.

### SRP-022 [MEDIUM] core/common/src/Instant.kt — Instant.Companion.parse
- **Confidence**: Found in 1 scan(s)
- **Lines**: 16–23
- **Type**: method
- **Description**: The Instant.Companion.parse extension function adds parsing logic to the Instant type, which should primarily represent a point in time.
- **Reasoning**: The core responsibility of `Instant` is to represent a point in time. Adding parsing logic, especially one that relies on `DateTimeComponents` and `DateTimeFormat`, introduces a new reason to change related to parsing standards and internal format structures. This externalizes a complex I/O and conversion responsibility onto a fundamental value type.

### SRP-023 [MEDIUM] core/common/src/Instant.kt — Instant.plus(period: DateTimePeriod, timeZone: TimeZone)
- **Confidence**: Found in 1 scan(s)
- **Lines**: 39–54
- **Type**: method
- **Description**: The Instant.plus extension function for DateTimePeriod and TimeZone mixes instant arithmetic with complex calendar-based calculations requiring time zone conversions.
- **Reasoning**: The `Instant` type inherently deals with linear time. Adding `plus` operations that involve `DateTimePeriod` and `TimeZone` introduces calendar-based arithmetic, which is a significantly different concern. This method performs multiple steps: converting to `LocalDateTime`, applying date/month arithmetic, converting back to `Instant`, and then applying nanosecond arithmetic. This complex logic for calendar-aware additions is a separate responsibility from basic instant manipulation.

### SRP-024 [MEDIUM] core/common/src/Instant.kt — Instant.until(other: Instant, unit: DateTimeUnit, timeZone: TimeZone)
- **Confidence**: Found in 1 scan(s)
- **Lines**: 124–142
- **Type**: method
- **Description**: The Instant.until extension function calculates the number of units between two instants, involving conditional logic based on DateTimeUnit type and time zone conversions for date-based units.
- **Reasoning**: This method has two distinct responsibilities based on the `DateTimeUnit` type: 
1. For `DateBased` units, it performs complex calendar-aware calculations requiring `LocalDateTime` conversions and date arithmetic.
2. For `TimeBased` units, it performs simpler time-based arithmetic. 
This conditional logic and the mixture of calendar-aware and time-based calculations, especially with `TimeZone` involvement, violate SRP by having multiple reasons to change (e.g., changes to calendar rules, changes to time zone handling, changes to time-based unit definitions).

### SRP-025 [MEDIUM] core/common/src/Instant.kt — Instant.format
- **Confidence**: Found in 1 scan(s)
- **Lines**: 269–274
- **Type**: method
- **Description**: The Instant.format extension function adds formatting logic to the Instant type, which should primarily represent a point in time.
- **Reasoning**: Similar to `Instant.Companion.parse`, this method introduces a formatting responsibility to `Instant`. It relies on `DateTimeComponents` and `DateTimeFormat` for its implementation, coupling `Instant` to specific formatting standards and internal format structures. This is a distinct concern from `Instant`'s core data representation.

### SRP-026 [MEDIUM] core/common/src/Instant.kt — Instant.Companion.parseOrNull
- **Confidence**: Found in 1 scan(s)
- **Lines**: 287–293
- **Type**: method
- **Description**: The Instant.Companion.parseOrNull extension function adds parsing logic to the Instant type, which should primarily represent a point in time.
- **Reasoning**: This method is the nullable version of `Instant.Companion.parse`, and shares the same SRP violation by adding parsing capabilities (an I/O and conversion responsibility) to the `Instant` type, coupling it to external formatting definitions.

### SRP-027 [MEDIUM] core/common/src/format/Unicode.kt — UnicodeFormat.Directive.YearMonthBased.addToFormat
- **Confidence**: Found in 1 scan(s)
- **Lines**: 136–138
- **Type**: method
- **Description**: The `addToFormat` methods in `UnicodeFormat.Directive` subclasses couple the representation of a Unicode format directive to the specific implementation details of `DateTimeFormatBuilder`.
- **Reasoning**: The `UnicodeFormat.Directive` hierarchy is responsible for representing the abstract syntax tree (AST) of a Unicode format string. However, each concrete directive (e.g., `Year`, `MonthOfYear`, `HourOfDay`) also contains logic (`addToFormat`) that directly calls methods on a `DateTimeFormatBuilder`. This means that if the `DateTimeFormatBuilder`'s API changes, or if a different builder implementation is introduced, these AST nodes would need to be modified. This couples the representation of the format string (what it *is*) with the logic for building a formatter (what it *does*), violating SRP.

### SRP-028 [MEDIUM] core/common/src/format/Unicode.kt — UnicodeFormat.Directive.DateBased.addToFormat
- **Confidence**: Found in 1 scan(s)
- **Lines**: 140–143
- **Type**: method
- **Description**: The `addToFormat` methods in `UnicodeFormat.Directive` subclasses couple the representation of a Unicode format directive to the specific implementation details of `DateTimeFormatBuilder`.
- **Reasoning**: The `UnicodeFormat.Directive` hierarchy is responsible for representing the abstract syntax tree (AST) of a Unicode format string. However, each concrete directive (e.g., `DayOfMonth`, `DayOfYear`) also contains logic (`addToFormat`) that directly calls methods on a `DateTimeFormatBuilder`. This means that if the `DateTimeFormatBuilder`'s API changes, or if a different builder implementation is introduced, these AST nodes would need to be modified. This couples the representation of the format string (what it *is*) with the logic for building a formatter (what it *does*), violating SRP.

### SRP-029 [MEDIUM] core/common/src/format/Unicode.kt — UnicodeFormat.Directive.TimeBased.addToFormat
- **Confidence**: Found in 1 scan(s)
- **Lines**: 218–220
- **Type**: method
- **Description**: The `addToFormat` methods in `UnicodeFormat.Directive` subclasses couple the representation of a Unicode format directive to the specific implementation details of `DateTimeFormatBuilder`.
- **Reasoning**: The `UnicodeFormat.Directive` hierarchy is responsible for representing the abstract syntax tree (AST) of a Unicode format string. However, each concrete directive (e.g., `HourOfDay`, `MinuteOfHour`, `SecondOfMinute`) also contains logic (`addToFormat`) that directly calls methods on a `DateTimeFormatBuilder`. This means that if the `DateTimeFormatBuilder`'s API changes, or if a different builder implementation is introduced, these AST nodes would need to be modified. This couples the representation of the format string (what it *is*) with the logic for building a formatter (what it *does*), violating SRP.

### SRP-030 [MEDIUM] core/common/src/format/Unicode.kt — UnicodeFormat.Directive.ZoneBased.addToFormat
- **Confidence**: Found in 1 scan(s)
- **Lines**: 279–281
- **Type**: method
- **Description**: The `addToFormat` methods in `UnicodeFormat.Directive` subclasses couple the representation of a Unicode format directive to the specific implementation details of `DateTimeFormatBuilder`.
- **Reasoning**: The `UnicodeFormat.Directive` hierarchy is responsible for representing the abstract syntax tree (AST) of a Unicode format string. However, each concrete directive (e.g., `TimeZoneId`) also contains logic (`addToFormat`) that directly calls methods on a `DateTimeFormatBuilder`. This means that if the `DateTimeFormatBuilder`'s API changes, or if a different builder implementation is introduced, these AST nodes would need to be modified. This couples the representation of the format string (what it *is*) with the logic for building a formatter (what it *does*), violating SRP.

### SRP-031 [MEDIUM] core/common/src/format/Unicode.kt — UnicodeFormat.Directive.OffsetBased.addToFormat
- **Confidence**: Found in 1 scan(s)
- **Lines**: 298–300
- **Type**: method
- **Description**: The `addToFormat` methods in `UnicodeFormat.Directive` subclasses couple the representation of a Unicode format directive to the specific implementation details of `DateTimeFormatBuilder`.
- **Reasoning**: The `UnicodeFormat.Directive` hierarchy is responsible for representing the abstract syntax tree (AST) of a Unicode format string. However, each concrete directive (e.g., `ZoneOffset1`, `ZoneOffset2`, `ZoneOffset3`) also contains logic (`addToFormat`) that directly calls methods on a `DateTimeFormatBuilder`. This means that if the `DateTimeFormatBuilder`'s API changes, or if a different builder implementation is introduced, these AST nodes would need to be modified. This couples the representation of the format string (what it *is*) with the logic for building a formatter (what it *does*), violating SRP.

### SRP-032 [MEDIUM] core/common/src/format/DateTimeFormat.kt — DateTimeFormat.Companion.formatAsKotlinBuilderDsl
- **Confidence**: Found in 1 scan(s)
- **Lines**: 62–74
- **Type**: method
- **Description**: The `formatAsKotlinBuilderDsl` method within the `DateTimeFormat.Companion` object is responsible for generating Kotlin code from a format structure, which is a code generation concern separate from defining, parsing, or formatting datetime values.
- **Reasoning**: The primary responsibility of `DateTimeFormat` and its companion object should be related to the definition, parsing, and formatting of datetime values. The `formatAsKotlinBuilderDsl` method, however, introduces a code generation or reflection-based transformation responsibility. This is a distinct concern, as changes to Kotlin's syntax or the desired output DSL would require modifying this method, while the core formatting/parsing logic might remain unchanged. This violates SRP by adding a tangential responsibility.

### SRP-036 [HIGH] core/common/src/DeprecatedInstant.kt — Instant.plus(period: DateTimePeriod, timeZone: TimeZone)
- **Confidence**: Found in 1 scan(s)
- **Lines**: 191–198
- **Type**: method
- **Description**: This method performs complex calendar arithmetic and timezone conversions, mixing 'point in time' representation with 'calendar-aware calculations'.
- **Reasoning**: The core responsibility of 'Instant' is to represent an immutable point in time and handle basic duration arithmetic. Operations involving 'DateTimePeriod' and 'TimeZone' require complex calendar logic and timezone rules (e.g., DST, leap seconds), which are separate domains of responsibility. This method pulls in those distinct concerns.

### SRP-037 [HIGH] core/common/src/DeprecatedInstant.kt — Instant.minus(period: DateTimePeriod, timeZone: TimeZone)
- **Confidence**: Found in 1 scan(s)
- **Lines**: 200–209
- **Type**: method
- **Description**: This method performs complex calendar arithmetic and timezone conversions, mixing 'point in time' representation with 'calendar-aware calculations'.
- **Reasoning**: Similar to 'plus', this method introduces complex calendar arithmetic and timezone conversion logic, which is a different responsibility than the core 'Instant' data representation and simple duration arithmetic.

### SRP-038 [HIGH] core/common/src/DeprecatedInstant.kt — Instant.periodUntil(other: Instant, timeZone: TimeZone)
- **Confidence**: Found in 1 scan(s)
- **Lines**: 211–227
- **Type**: method
- **Description**: This method calculates a DateTimePeriod between two instants, involving complex calendar and timezone logic.
- **Reasoning**: Calculating a 'DateTimePeriod' between two 'Instant's in a specific 'TimeZone' requires intricate calendar and timezone-aware computations, which extends beyond the fundamental role of an 'Instant' as a time point.

### SRP-039 [HIGH] core/common/src/DeprecatedInstant.kt — Instant.until(other: Instant, unit: DateTimeUnit, timeZone: TimeZone)
- **Confidence**: Found in 1 scan(s)
- **Lines**: 229–245
- **Type**: method
- **Description**: This method calculates the number of units between two instants, involving complex calendar and timezone logic.
- **Reasoning**: Similar to 'periodUntil', this method applies complex calendar and timezone logic to compute the difference in specific units, which is a distinct responsibility from the core 'Instant' functionality.

### SRP-040 [HIGH] core/common/src/DeprecatedInstant.kt — Instant.daysUntil(other: Instant, timeZone: TimeZone)
- **Confidence**: Found in 1 scan(s)
- **Lines**: 257–258
- **Type**: method
- **Description**: This method calculates days between instants, involving calendar and timezone logic.
- **Reasoning**: This is a specialized form of 'until' that still brings in the complex calendar and timezone calculations, violating SRP.

### SRP-041 [HIGH] core/common/src/DeprecatedInstant.kt — Instant.monthsUntil(other: Instant, timeZone: TimeZone)
- **Confidence**: Found in 1 scan(s)
- **Lines**: 266–267
- **Type**: method
- **Description**: This method calculates months between instants, involving calendar and timezone logic.
- **Reasoning**: This is a specialized form of 'until' that still brings in the complex calendar and timezone calculations, violating SRP.

### SRP-042 [HIGH] core/common/src/DeprecatedInstant.kt — Instant.yearsUntil(other: Instant, timeZone: TimeZone)
- **Confidence**: Found in 1 scan(s)
- **Lines**: 275–276
- **Type**: method
- **Description**: This method calculates years between instants, involving calendar and timezone logic.
- **Reasoning**: This is a specialized form of 'until' that still brings in the complex calendar and timezone calculations, violating SRP.

### SRP-043 [HIGH] core/common/src/DeprecatedInstant.kt — Instant.minus(other: Instant, timeZone: TimeZone)
- **Confidence**: Found in 1 scan(s)
- **Lines**: 284–285
- **Type**: method
- **Description**: This method calculates a DateTimePeriod between two instants, involving complex calendar and timezone logic.
- **Reasoning**: This is a specialized form of 'periodUntil' that still brings in the complex calendar and timezone calculations, violating SRP.

### SRP-044 [HIGH] core/common/src/DeprecatedInstant.kt — Instant.plus(unit: DateTimeUnit, timeZone: TimeZone)
- **Confidence**: Found in 1 scan(s)
- **Lines**: 296–298
- **Type**: method
- **Description**: This method adds a date/time unit to an instant, involving complex calendar and timezone logic.
- **Reasoning**: This method introduces complex calendar arithmetic and timezone conversion logic, which is a different responsibility than the core 'Instant' data representation and simple duration arithmetic.

### SRP-045 [HIGH] core/common/src/DeprecatedInstant.kt — Instant.minus(unit: DateTimeUnit, timeZone: TimeZone)
- **Confidence**: Found in 1 scan(s)
- **Lines**: 306–308
- **Type**: method
- **Description**: This method subtracts a date/time unit from an instant, involving complex calendar and timezone logic.
- **Reasoning**: This method introduces complex calendar arithmetic and timezone conversion logic, which is a different responsibility than the core 'Instant' data representation and simple duration arithmetic.

### SRP-046 [HIGH] core/common/src/DeprecatedInstant.kt — Instant.plus(value: Int, unit: DateTimeUnit, timeZone: TimeZone)
- **Confidence**: Found in 1 scan(s)
- **Lines**: 339–341
- **Type**: method
- **Description**: This method adds a value of date/time unit to an instant, involving complex calendar and timezone logic.
- **Reasoning**: This method introduces complex calendar arithmetic and timezone conversion logic, which is a different responsibility than the core 'Instant' data representation and simple duration arithmetic.

### SRP-047 [HIGH] core/common/src/DeprecatedInstant.kt — Instant.minus(value: Int, unit: DateTimeUnit, timeZone: TimeZone)
- **Confidence**: Found in 1 scan(s)
- **Lines**: 357–359
- **Type**: method
- **Description**: This method subtracts a value of date/time unit from an instant, involving complex calendar and timezone logic.
- **Reasoning**: This method introduces complex calendar arithmetic and timezone conversion logic, which is a different responsibility than the core 'Instant' data representation and simple duration arithmetic.

### SRP-048 [HIGH] core/common/src/DeprecatedInstant.kt — Instant.plus(value: Long, unit: DateTimeUnit, timeZone: TimeZone)
- **Confidence**: Found in 1 scan(s)
- **Lines**: 375–377
- **Type**: method
- **Description**: This method adds a value of date/time unit to an instant, involving complex calendar and timezone logic.
- **Reasoning**: This method introduces complex calendar arithmetic and timezone conversion logic, which is a different responsibility than the core 'Instant' data representation and simple duration arithmetic.

### SRP-049 [HIGH] core/common/src/DeprecatedInstant.kt — Instant.minus(value: Long, unit: DateTimeUnit, timeZone: TimeZone)
- **Confidence**: Found in 1 scan(s)
- **Lines**: 393–398
- **Type**: method
- **Description**: This method subtracts a value of date/time unit from an instant, involving complex calendar and timezone logic.
- **Reasoning**: This method introduces complex calendar arithmetic and timezone conversion logic, which is a different responsibility than the core 'Instant' data representation and simple duration arithmetic.

### SRP-050 [HIGH] core/common/src/DeprecatedInstant.kt — Instant.minus(other: Instant, unit: DateTimeUnit, timeZone: TimeZone)
- **Confidence**: Found in 1 scan(s)
- **Lines**: 414–415
- **Type**: method
- **Description**: This method calculates the difference between two instants in terms of a date/time unit, involving calendar and timezone logic.
- **Reasoning**: This is a specialized form of 'until' that still brings in the complex calendar and timezone calculations, violating SRP.

### SRP-051 [MEDIUM] core/common/src/DeprecatedInstant.kt — Instant.format
- **Confidence**: Found in 1 scan(s)
- **Lines**: 431–434
- **Type**: method
- **Description**: This extension function provides a formatting capability for 'Instant' values using arbitrary 'DateTimeFormat' instances.
- **Reasoning**: While an extension function is less intrusive than a class method, having 'Instant' as the receiver for a general formatting operation means the 'Instant' concept is implicitly taking on the responsibility of 'being format-able by arbitrary formats'. The core responsibility is data representation, not presentation.

### SRP-052 [MEDIUM] core/common/src/format/DateTimeComponents.kt — DateTimeComponents.toInstantUsingOffset
- **Confidence**: Found in 1 scan(s)
- **Lines**: 351–370
- **Type**: method
- **Description**: This method performs complex conversion and validation logic from flexible components to a canonical 'Instant' value.
- **Reasoning**: 'DateTimeComponents' is primarily a flexible container for various date-time fields used during parsing/formatting. The 'toInstantUsingOffset' method, however, involves significant logic for interpreting these fields, handling potential out-of-bounds values, applying UTC offsets, and performing boundary checks before creating an 'Instant'. This conversion and validation logic is a distinct responsibility from merely holding the components.

### SRP-053 [MEDIUM] core/common/src/DateTimePeriod.kt — DateTimePeriod.toString
- **Confidence**: Found in 1 scan(s)
- **Lines**: 80–99
- **Type**: method
- **Description**: The toString method formats the period into a specific ISO 8601 string representation.
- **Reasoning**: While a toString method is standard, when it implements a specific, standardized formatting (like ISO 8601 with details about units and signs) and is used as part of the public API for formatted output, it takes on a 'formatting' responsibility distinct from merely representing the difference between two instants.

### SRP-054 [MEDIUM] core/common/src/DateTimePeriod.kt — DatePeriod.Companion.parse
- **Confidence**: Found in 1 scan(s)
- **Lines**: 255–261
- **Type**: method
- **Description**: This method adds validation logic specific to 'DatePeriod' (ensuring time components are zero) on top of general parsing.
- **Reasoning**: While 'DatePeriod' is a specialized type, its 'parse' method not only delegates to 'DateTimePeriod.parse' but also includes additional validation to enforce that no time components are present. This adds a 'validation' responsibility beyond its primary role as a specialized data structure.

### SRP-055 [MEDIUM] core/common/src/DateTimePeriod.kt — DatePeriod.Companion.parseOrNull
- **Confidence**: Found in 1 scan(s)
- **Lines**: 269–270
- **Type**: method
- **Description**: This method adds validation logic specific to 'DatePeriod' (ensuring time components are zero) on top of general parsing.
- **Reasoning**: Similar to 'parse', this method is responsible for validating that parsed 'DateTimePeriod' is indeed a 'DatePeriod', which is a validation concern.

### SRP-056 [MEDIUM] core/common/src/format/Unicode.kt — DateTimeFormatBuilder.byUnicodePattern
- **Confidence**: Found in 1 scan(s)
- **Lines**: 105–169
- **Type**: method
- **Description**: The byUnicodePattern function is responsible for parsing a Unicode pattern string, interpreting directives, and building the format structure.
- **Reasoning**: The `byUnicodePattern` extension function combines several distinct responsibilities: parsing a complex Unicode pattern string into an internal `UnicodeFormat` representation, interpreting the various directives (e.g., 'u' for year, 'M' for month, 'H' for hour, 'V' for timezone), and then building the corresponding `DateTimeFormat` structure by calling methods on the `DateTimeFormatBuilder`. It also includes validation logic for directive compatibility. This mixes parsing, interpretation, and construction concerns, violating SRP. A change to the Unicode pattern syntax, the interpretation of a directive, or the `DateTimeFormatBuilder` DSL would all require modifying this single function.

### SRP-057 [MEDIUM] core/common/src/internal/format/parser/ParserOperation.kt — TimeZoneParserOperation.Companion.validateTimeZone
- **Confidence**: Found in 1 scan(s)
- **Lines**: 102–170
- **Type**: method
- **Description**: The validateTimeZone function is a 'God Function' responsible for parsing all types of time zone identifiers using a single state machine.
- **Reasoning**: The `validateTimeZone` companion function within `TimeZoneParserOperation` is overly complex. It uses a large state machine (`when (state)`) to handle the parsing and validation of diverse time zone identifier formats, including UTC/GMT prefixes, fixed offsets, and IANA region IDs. Each of these formats has distinct parsing rules. This function has too many reasons to change; for example, adding support for a new time zone prefix or modifying the rules for IANA IDs would require changes to this single, monolithic function. This violates SRP by combining multiple distinct parsing responsibilities.

### SRP-058 [LOW] core/common/src/internal/format/FormatStructure.kt — ConstantFormatStructure.parser
- **Confidence**: Found in 1 scan(s)
- **Lines**: 40–66
- **Type**: method
- **Description**: The parser() method of ConstantFormatStructure not only matches a literal string but also intelligently breaks it down into numeric and non-numeric parts.
- **Reasoning**: The primary responsibility of `ConstantFormatStructure` is to represent and match a fixed literal string. However, its `parser()` method goes beyond simple literal matching by attempting to intelligently break down the constant string into sequences of digits (handled by `NumberSpanParserOperation`) and non-digit characters (handled by `PlainStringParserOperation`). This introduces a secondary responsibility of numeric interpretation within a literal, which is a subtle violation of SRP. A change in how numbers embedded within constant strings are parsed would require modifying this method, separate from changes to how literal strings are generally handled.

### SRP-059 [MEDIUM] core/common/src/internal/format/parser/Parser.kt — List<ParserStructure<T>>.concat
- **Confidence**: Found in 1 scan(s)
- **Lines**: 29–120
- **Type**: method
- **Description**: The concat extension function performs multiple distinct optimization and merging strategies for parser structures.
- **Reasoning**: The `concat` extension function is responsible for combining a list of `ParserStructure` instances into a single, optimized structure. This involves several distinct sub-responsibilities: merging consecutive `NumberSpanParserOperation` instances, collecting and applying `UnconditionalModification`s, and flattening alternative parsing paths. Each of these is a separate concern related to parser optimization. A change to any one of these optimization strategies would necessitate modifying this single function, indicating a violation of SRP by combining too many distinct responsibilities into one method.

### SRP-060 [HIGH] core/common/src/format/Unicode.kt — DateTimeFormatBuilder.byUnicodePattern
- **Confidence**: Found in 1 scan(s)
- **Lines**: 70–131
- **Type**: method
- **Description**: The 'byUnicodePattern' function mixes parsing a Unicode pattern string with building a DateTimeFormat structure.
- **Reasoning**: This function is responsible for two distinct concerns: first, parsing the input `pattern` string into an abstract `UnicodeFormat` representation (`UnicodeFormat.parse(pattern)`), and second, translating this parsed structure into a series of `DateTimeFormatBuilder` DSL calls (`rec` function). Changes to the Unicode pattern syntax or the `DateTimeFormatBuilder` DSL would both require modifications to this single function, indicating a Divergent Change smell and a clear SRP violation.

### SRP-061 [MEDIUM] core/common/src/format/Unicode.kt — UnicodeFormat.Directive.YearMonthBased.Year.addToFormat
- **Confidence**: Found in 1 scan(s)
- **Lines**: 168–175
- **Type**: method
- **Description**: Subclasses of 'UnicodeFormat.Directive' contain logic for translating themselves into 'DateTimeFormatBuilder' calls.
- **Reasoning**: Classes like `UnicodeFormat.Directive.Year` (and other `Directive` subclasses) are designed to represent a parsed Unicode directive. However, they also include methods like `addToFormat(builder: ...)` that embed the logic for *how* to translate this directive into specific `DateTimeFormatBuilder` DSL calls. This couples the representation of a directive with its translation strategy, meaning changes to the `DateTimeFormatBuilder` API or the mapping logic would force changes to these directive classes, which should ideally only focus on their descriptive role. This is a Feature Envy smell.

### SRP-062 [HIGH] core/common/src/format/DateTimeFormatBuilder.kt — FormatStructure<T>.builderString
- **Confidence**: Found in 1 scan(s)
- **Lines**: 105–171
- **Type**: method
- **Description**: The 'builderString' extension function mixes traversing a format AST with generating Kotlin code.
- **Reasoning**: This function is responsible for iterating through the `FormatStructure` (an Abstract Syntax Tree of a format) and, concurrently, generating a string of Kotlin code that represents that structure using the `DateTimeFormatBuilder` DSL. This mixes the concern of AST traversal with the distinct concern of code generation. Any change to the `FormatStructure` or the desired Kotlin DSL output would require modifying this method, indicating a Divergent Change smell and a violation of SRP.

### SRP-063 [MEDIUM] core/common/src/internal/format/parser/TimeZoneParserOperation.kt — TimeZoneParserOperation
- **Confidence**: Found in 1 scan(s)
- **Lines**: 121–200
- **Type**: class
- **Description**: The 'TimeZoneParserOperation' class mixes parsing a timezone string with complex validation logic.
- **Reasoning**: This class's `consume` method relies heavily on the nested `validateTimeZone` function, which contains substantial logic for validating the format of a timezone string according to RFC 9557 grammar. This couples the core responsibility of parsing with a significant validation concern. The validation logic could be extracted into a separate utility or validator class, making `TimeZoneParserOperation` solely responsible for consuming the input based on a given validation rule.

### SRP-064 [MEDIUM] core/common/src/internal/format/parser/Parser.kt — Parser
- **Confidence**: Found in 1 scan(s)
- **Lines**: 29–84
- **Type**: class
- **Description**: The 'Parser' class mixes parsing orchestration with detailed error handling and formatting.
- **Reasoning**: The `Parser` class is primarily responsible for orchestrating the parsing process by managing alternative parsing paths and input consumption. However, its `match` method also includes logic for collecting, sorting, and formatting detailed error messages into a `ParseException`. The responsibility of generating user-friendly, sorted error reports is distinct from the core parsing execution logic. This indicates a violation of SRP, as changes to error reporting requirements would impact the `Parser` class.

### SRP-065 [HIGH] core/common/src/internal/format/FormatStructure.kt — OptionalFormatStructure
- **Confidence**: Found in 1 scan(s)
- **Lines**: 102–167
- **Type**: class
- **Description**: The 'OptionalFormatStructure' class combines structural representation, default value management, and parsing/formatting logic for optional sections.
- **Reasoning**: This class represents an optional section within a format. It is responsible for determining and managing default values for fields within its optional block (via `PropertyWithDefault`), and it contains the logic for *how* to parse the optional string (including assigning defaults if the optional part is missing) and *how* to conditionally format based on whether values are default. This mixes structural description with default value handling and the concrete parsing/formatting strategies, leading to a God Class smell and multiple reasons for change.

### SRP-066 [HIGH] core/common/src/internal/format/FieldFormatDirective.kt — UnsignedIntFieldFormatDirective
- **Confidence**: Found in 1 scan(s)
- **Lines**: 19–48
- **Type**: class
- **Description**: Abstract 'FieldFormatDirective' subclasses couple field description with formatting and parsing strategies.
- **Reasoning**: Abstract classes like `UnsignedIntFieldFormatDirective` (and its siblings `NamedUnsignedIntFieldFormatDirective`, `SignedIntFieldFormatDirective`, etc.) define *what* a field is (its properties and constraints) and *how* it should be formatted and parsed by providing concrete implementations for `formatter()` and `parser()`. This tightly couples the declarative description of a field with the imperative implementation of its formatting and parsing logic. A change in the strategy for formatting/parsing an unsigned integer (e.g., a new padding rule) would require modifying this class, which should ideally only describe the field itself. This is a Divergent Change smell.

### SRP-067 [MEDIUM] core/common/src/Clock.kt — Clock.asTimeSource
- **Confidence**: Found in 1 scan(s)
- **Lines**: 39–67
- **Type**: method
- **Description**: The 'asTimeSource' extension function mixes conversion with the detailed implementation logic of the target interface.
- **Reasoning**: This extension function is responsible for converting a `Clock` instance into a `TimeSource.WithComparableMarks`. However, it also fully implements the complex behavior of the `ComparableTimeMark` interface (via the `InstantTimeMark` anonymous object), including methods like `elapsedNow`, `plus`, `minus`, `equals`, `hashCode`, `toString`, and internal helper functions like `isSaturated`, `saturatingAdd`, and `saturatingDiff`. This means the function is responsible for both the conversion mechanism and the substantial, distinct logic of the new time mark type. This is a Long Method smell, as the implementation of `ComparableTimeMark` could be a separate, dedicated class.

### SRP-068 [HIGH] src/main/kotlin/com/example/app/service/UserService.kt — UserService.sendWelcomeEmail
- **Confidence**: Found in 1 scan(s)
- **Lines**: 40–45
- **Type**: method
- **Description**: The method 'sendWelcomeEmail' handles email sending, which is a separate responsibility from user business logic.
- **Reasoning**: The UserService should focus solely on business logic related to user management (e.g., registration, profile updates, deletion). Sending emails involves concerns like email templating, SMTP configuration, network communication, and error handling for email delivery, which are distinct and should be delegated to a dedicated EmailService.

### SRP-069 [HIGH] src/main/kotlin/com/example/app/service/UserService.kt — UserService.generateUserReport
- **Confidence**: Found in 1 scan(s)
- **Lines**: 47–62
- **Type**: method
- **Description**: The method 'generateUserReport' handles report generation, which is a separate responsibility from user business logic.
- **Reasoning**: The UserService should focus solely on business logic related to user management. Generating reports involves concerns like data aggregation, formatting, potentially complex layout, and outputting to specific formats (e.g., PDF, HTML, plain text), which are distinct and should be delegated to a dedicated ReportService or UserReportGenerator class.

### SRP-070 [MEDIUM] src/main/kotlin/com/example/app/util/DatabaseConnector.kt — DatabaseConnector.initializeDatabaseSchema
- **Confidence**: Found in 1 scan(s)
- **Lines**: 29–49
- **Type**: method
- **Description**: The method 'initializeDatabaseSchema' handles database schema management, which is a separate responsibility from providing database connections.
- **Reasoning**: The DatabaseConnector's primary responsibility should be to provide and manage database connections. Schema initialization or migration (DDL operations) is a distinct concern, typically handled by dedicated migration tools (like Flyway or Liquibase) or a separate SchemaInitializer component. Mixing these responsibilities means the class has two reasons to change: changes in connection logic or changes in schema definition.

### SRP-071 [HIGH] src/main/kotlin/com/example/demo/service/OrderService.kt — OrderService
- **Confidence**: Found in 1 scan(s)
- **Lines**: 9–59
- **Type**: class
- **Description**: The OrderService class handles order management (CRUD), payment processing, invoice generation, and email notification.
- **Reasoning**: This class has multiple distinct reasons to change. For example, changes to payment gateway integration, invoice formatting rules, or email notification logic would all necessitate modifications to `OrderService`, even though these concerns are separate from the core responsibility of managing the order lifecycle. The methods `processOrderPayment` and `generateInvoice` clearly demonstrate responsibilities beyond just order management, and the `createOrder` method mixes core logic with email notification.

### SRP-072 [HIGH] src/main/kotlin/com/example/app/data/UserRepository.kt — UserRepository
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1–26
- **Type**: class
- **Description**: The UserRepository interface has too many unrelated responsibilities, acting as a 'God Interface'.
- **Reasoning**: This interface combines data persistence (save, find, delete, update), logging (logUserActivity), communication (sendWelcomeEmail, notifyAdminOfSuspiciousActivity), security (generateAuthToken, auditUserAccess, getUserPermissions), validation (validateUserData), data management (export, import, backup, restore, cache), business logic (calculateUserScore, applyUserDiscount), and integration (syncUserWithExternalSystem). These are distinct reasons for change and should be segregated into separate interfaces or classes (e.g., `UserPersistenceRepository`, `UserActivityLogger`, `UserNotifier`, `UserSecurityService`, `UserDataValidator`, `UserDataExporter`, `UserCacheManager`, `UserBackupService`, `UserBusinessService`, `UserIntegrationService`).

### SRP-073 [HIGH] src/main/kotlin/com/example/app/service/UserService.kt — UserService
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1–26
- **Type**: class
- **Description**: The UserService class is a 'God Class' handling an excessive number of unrelated business concerns.
- **Reasoning**: This class is responsible for core user management (create, get, update, delete), but also handles password management (changeUserPassword, sendPasswordResetEmail), order processing (processUserOrder), financial operations (generateInvoice, integrateWithPaymentGateway), marketing (sendMarketingEmail), analytics (trackUserBehavior), security (performSecurityCheck), notifications (notifyUserOfUpdates), backup/restore (backupUserAccount, restoreUserAccount), loyalty/promotions (calculateLoyaltyPoints, applyPromotionalCode), CRM synchronization (syncUserWithCRM), activity logging (getUserActivityLog), and subscription management (manageUserSubscriptions). Each of these represents a distinct responsibility and a separate reason for the class to change. This class should be broken down into smaller, more focused services (e.g., `UserManagementService`, `UserSecurityService`, `OrderProcessingService`, `MarketingService`, `NotificationService`, `UserAccountService`, `LoyaltyService`, `SubscriptionService`).

### SRP-074 [HIGH] src/main/kotlin/com/example/app/api/UserApi.kt — UserApi
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1–26
- **Type**: class
- **Description**: The UserApi interface exposes an overly broad set of API endpoints, violating the principle of interface segregation and single responsibility.
- **Reasoning**: This interface defines endpoints for basic user CRUD, but also for password resets, order placement, invoice retrieval, marketing opt-in, security scans, payment processing, notifications, backup initiation, loyalty point redemption, promotions, activity logs, and subscription management. An API interface should ideally be segregated by resource or domain area. Forcing clients to depend on this large interface means they are exposed to methods they don't need, and any change to an unrelated domain (e.g., loyalty points vs. security scans) would require changes or recompilation of this single interface and its implementations. This should be split into more granular API interfaces like `UserManagementApi`, `UserOrderApi`, `UserSecurityApi`, `UserAccountApi`, etc.
