# OCP Violation Report: kotlinx-datetime

## Summary
- **Total unique issues**: 6
- **High severity**: 2
- **Medium severity**: 4
- **Low severity**: 0
- **Found by multiple scans**: 3/6

## Issues

### OCP-001 [HIGH] core/common/src/DateTimePeriod.kt — DateTimePeriod.Companion.parseImpl
- **Confidence**: Found in 6 scan(s)
- **Lines**: 235–427
- **Type**: method
- **Description**: Hardcoded parsing logic for ISO 8601 duration format using a state machine
- **Reasoning**: The parsing logic is implemented as a monolithic state machine with hardcoded character checks ('Y', 'M', 'W', 'D', 'T', 'H', 'S'). Adding support for new duration components or alternative formats requires modifying this complex, tightly coupled state machine, violating the Open/Closed Principle.

### OCP-002 [MEDIUM] core/common/src/format/Unicode.kt — byUnicodePattern
- **Confidence**: Found in 2 scan(s)
- **Lines**: 104–155
- **Type**: method
- **Description**: Hardcoded mapping of Unicode format directives to internal builder methods
- **Reasoning**: The `byUnicodePattern` function uses a large `when` block to map specific Unicode characters to builder methods. Adding support for new format directives requires modifying this central `when` block, which is a classic violation of OCP.

### OCP-003 [MEDIUM] core/common/src/internal/format/parser/Parser.kt — List<ParserStructure<T>>.concat
- **Confidence**: Found in 2 scan(s)
- **Lines**: 57–154
- **Type**: method
- **Description**: Hardcoded logic for merging parser operations
- **Reasoning**: The `concat` function uses a complex `when` block to handle different types of `ParserOperation` (NumberSpan, UnconditionalModification, etc.). Adding new types of parser operations requires modifying this central logic, making the system closed to extension for new parser operation types.

### OCP-004 [MEDIUM] core/common/src/format/Unicode.kt — unicodeDirective
- **Confidence**: Found in 1 scan(s)
- **Lines**: 372–407
- **Type**: class
- **Description**: Hardcoded mapping of characters to directives requires modification to support new format patterns.
- **Reasoning**: The function `unicodeDirective` acts as a central switch for mapping Unicode format characters to internal directives. Adding support for new format directives requires modifying this function, which is a classic OCP violation.

### OCP-005 [MEDIUM] core/common/src/internal/format/parser/Parser.kt — ParserStructure.concat
- **Confidence**: Found in 1 scan(s)
- **Lines**: 62–172
- **Type**: class
- **Description**: Hardcoded logic for merging parser structures limits extension of parsing logic.
- **Reasoning**: The concat function performs complex, hardcoded logic to merge parser structures and number spans. Adding new types of parser operations or complex parsing requirements requires modifying this logic, which is tightly coupled to current implementation details.

### OCP-006 [HIGH] core/common/src/internal/format/parser/ParserOperation.kt — TimeZoneParserOperation.Companion.validateTimeZone
- **Confidence**: Found in 1 scan(s)
- **Lines**: 128–226
- **Type**: class
- **Description**: Hardcoded state machine for time zone parsing is closed to extension
- **Reasoning**: The validateTimeZone function implements a rigid state machine using hardcoded rules for specific time zone ID components. Supporting new time zone identifier formats requires modifying the existing state machine logic, which is a clear violation of OCP.
