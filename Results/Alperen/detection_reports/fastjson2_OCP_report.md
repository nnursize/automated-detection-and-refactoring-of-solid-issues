# OCP Violation Report: fastjson2

## Summary
- **Total unique issues**: 125
- **High severity**: 89
- **Medium severity**: 36
- **Low severity**: 0
- **Found by multiple scans**: 76/125

## Issues

### OCP-001 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseDate
- **Confidence**: Found in 9 scan(s)
- **Lines**: 109–155
- **Type**: method
- **Description**: The parseDate method uses a large switch statement to handle different date formats.
- **Reasoning**: The `parseDate` method in `DateUtils.java` contains a large `switch` statement based on the `format` string. To add support for a new date format, this `switch` statement would need to be modified by adding a new `case`. This violates the Open/Closed Principle because the existing code is being modified to extend its functionality. A better approach would be to use a strategy pattern or a registry of formatters that can be extended without modifying the core `parseDate` method.

### OCP-004 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDate
- **Confidence**: Found in 8 scan(s)
- **Lines**: 801–834
- **Type**: method
- **Description**: The parseLocalDate method uses a switch statement based on the length of the input.
- **Reasoning**: The `parseLocalDate` method, which takes a `String` as input, internally calls `parseLocalDate` with `char[]`. The `char[]` overload of `parseLocalDate` (lines 849-901) uses a `switch` statement on the length of the input. This switch statement needs to be modified to support new date formats or lengths, violating the OCP. The principle suggests that software entities should be open for extension but closed for modification.

### OCP-010 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTimeX
- **Confidence**: Found in 8 scan(s)
- **Lines**: 1429–1566
- **Type**: method
- **Description**: The parseLocalDateTimeX method (byte array overload) uses a large switch statement based on the length of the input and complex conditional logic.
- **Reasoning**: The `parseLocalDateTimeX` method, overloaded for byte arrays, also relies on a `switch` statement based on input length and extensive conditional logic. This design violates the Open/Closed Principle because extending the functionality to support new formats would require modifying the existing code. The principle promotes extensibility without modification.

### OCP-013 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseMillis19
- **Confidence**: Found in 8 scan(s)
- **Lines**: 1647–1877
- **Type**: method
- **Description**: The parseMillis19 method uses a large switch statement based on the DateTimeFormatPattern.
- **Reasoning**: The `parseMillis19` method uses a `switch` statement on the `DateTimeFormatPattern` enum to parse date-time strings. Adding a new format pattern would require modifying this `switch` statement, which violates the Open/Closed Principle. The principle suggests that software entities should be open for extension but closed for modification.

### OCP-014 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseMillis19
- **Confidence**: Found in 8 scan(s)
- **Lines**: 1892–2122
- **Type**: method
- **Description**: The parseMillis19 method (byte array overload) uses a large switch statement based on the DateTimeFormatPattern.
- **Reasoning**: Similar to the char array overload, the `parseMillis19` method that handles byte arrays also uses a `switch` statement based on `DateTimeFormatPattern`. This design violates the Open/Closed Principle because new date formats would require modifying the existing method. The principle promotes extending functionality without altering current code.

### OCP-005 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDate
- **Confidence**: Found in 7 scan(s)
- **Lines**: 916–971
- **Type**: method
- **Description**: The parseLocalDate method (byte array overload) uses a switch statement based on the length of the input.
- **Reasoning**: The `parseLocalDate` method that accepts a `byte[]` also relies on a `switch` statement based on the length of the input array. This design pattern requires modifying the existing method to add support for new date formats corresponding to different lengths, which is a violation of the Open/Closed Principle. New functionality should ideally be added through extension rather than modification.

### OCP-020 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTime
- **Confidence**: Found in 7 scan(s)
- **Lines**: 709–766
- **Type**: method
- **Description**: The `parseLocalDateTime` method (overload for byte array) uses a switch statement based on the length of the input.
- **Reasoning**: This method uses a switch statement on the length of the input byte array to parse LocalDateTime. Adding new date/time formats that have different lengths would require modifying this switch statement, which violates the Open/Closed Principle. A more extensible design is needed.

### OCP-003 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTime
- **Confidence**: Found in 6 scan(s)
- **Lines**: 670–736
- **Type**: method
- **Description**: The parseLocalDateTime method (byte array overload) uses a large switch statement based on the length of the input.
- **Reasoning**: Similar to the `char[]` overload, the `byte[]` version of `parseLocalDateTime` also uses a `switch` statement on the length of the input. This design forces modifications to the method whenever a new format length needs to be supported, violating the Open/Closed Principle. The principle advocates for extending functionality without altering existing code.

### OCP-006 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDate
- **Confidence**: Found in 6 scan(s)
- **Lines**: 986–1041
- **Type**: method
- **Description**: The parseLocalDate method (char array overload) uses a switch statement based on the length of the input.
- **Reasoning**: The `parseLocalDate` method that takes a `char[]` utilizes a `switch` statement based on the length of the input. This approach makes it difficult to add new date formats without altering the existing code, directly contradicting the Open/Closed Principle. The principle encourages designing classes that are open for extension but closed for modification.

### OCP-007 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseMillis
- **Confidence**: Found in 6 scan(s)
- **Lines**: 568–631
- **Type**: method
- **Description**: The parseMillis method (byte array overload) uses multiple conditional checks and a switch statement for parsing different date formats.
- **Reasoning**: The `parseMillis` method, which handles byte arrays, contains a series of `if-else if` statements and a `switch` statement based on the length of the input. This complex conditional logic is used to parse various date formats. Adding support for a new format would require modifying this method, violating the Open/Closed Principle. The principle suggests that new functionality should be added through extension, not modification of existing code.

### OCP-009 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTimeX
- **Confidence**: Found in 6 scan(s)
- **Lines**: 1277–1414
- **Type**: method
- **Description**: The parseLocalDateTimeX method uses a large switch statement based on the length of the input and complex conditional logic.
- **Reasoning**: The `parseLocalDateTimeX` method handles various date-time formats by checking the length of the input and employing complex conditional logic. This approach violates the Open/Closed Principle as adding support for new formats or variations would require modifying the existing method. The principle suggests that the method should be open for extension but closed for modification.

### OCP-011 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseZonedDateTime
- **Confidence**: Found in 6 scan(s)
- **Lines**: 1077–1118
- **Type**: method
- **Description**: The parseZonedDateTime method uses a switch statement based on the length of the input.
- **Reasoning**: The `parseZonedDateTime` method, which handles string input, delegates to an overload that uses a `switch` statement based on the length of the input. This `switch` statement contains logic for various date formats. Adding support for new formats would necessitate modifying this `switch` statement, violating the Open/Closed Principle. The principle states that software entities should be open for extension but closed for modification.

### OCP-012 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseZonedDateTime
- **Confidence**: Found in 6 scan(s)
- **Lines**: 1133–1259
- **Type**: method
- **Description**: The parseZonedDateTime method (byte array overload) uses a switch statement based on the length of the input.
- **Reasoning**: The `parseZonedDateTime` method, overloaded for byte arrays, also employs a `switch` statement based on the input length. This design makes it difficult to add new date formats without modifying the existing code, which violates the Open/Closed Principle. The principle encourages extending functionality through addition rather than alteration.

### OCP-015 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseMillis10
- **Confidence**: Found in 6 scan(s)
- **Lines**: 500–545
- **Type**: method
- **Description**: The parseMillis10 method uses a switch statement based on the DateTimeFormatPattern.
- **Reasoning**: The `parseMillis10` method uses a `switch` statement on `DateTimeFormatPattern` to parse date strings. Adding support for a new date format would require modifying this `switch` statement, which violates the Open/Closed Principle. The principle states that software entities should be open for extension but closed for modification.

### OCP-016 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.format
- **Confidence**: Found in 6 scan(s)
- **Lines**: 1557–1602
- **Type**: method
- **Description**: The format method (long timeMillis overload) uses a switch statement based on the DateTimeFormatPattern.
- **Reasoning**: The `format` method, overloaded to accept time in milliseconds, uses a `switch` statement based on `DateTimeFormatPattern`. This design violates the Open/Closed Principle because adding new formats requires modifying the existing `switch` statement. The principle promotes extensibility without modification of existing code.

### OCP-031 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTimeX
- **Confidence**: Found in 6 scan(s)
- **Lines**: 2764–2935
- **Type**: method
- **Description**: The `parseLocalDateTimeX` method (overload for byte array) uses a large switch statement based on the length of the input.
- **Reasoning**: This overload for byte arrays also uses a switch statement based on input length. This violates OCP because new formats require modifying existing code. A design that decouples parsing logic, such as a strategy pattern, would be more compliant.

### OCP-002 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTime
- **Confidence**: Found in 5 scan(s)
- **Lines**: 242–308
- **Type**: method
- **Description**: The parseLocalDateTime method uses a large switch statement based on the length of the input.
- **Reasoning**: The `parseLocalDateTime` method in `DateUtils.java` uses a `switch` statement on the `len` (length) of the input character array. Each `case` handles a specific date/time format. Adding support for a new format length or a variation of an existing format would require modifying this `switch` statement, thus violating the Open/Closed Principle. This structure makes the method closed for extension but open for modification.

### OCP-008 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTime
- **Confidence**: Found in 5 scan(s)
- **Lines**: 311–377
- **Type**: method
- **Description**: The parseLocalDateTime method (char array overload) uses a large switch statement based on the length of the input.
- **Reasoning**: The `parseLocalDateTime` method that accepts a `char[]` uses a `switch` statement based on the length of the input. Each case handles a specific format. This design violates the Open/Closed Principle because adding support for new date/time formats would necessitate modifying this `switch` statement. The principle advocates for extending behavior without changing existing code.

### OCP-018 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDate
- **Confidence**: Found in 5 scan(s)
- **Lines**: 1035–1069
- **Type**: method
- **Description**: The `parseLocalDate` method (overload for char array) uses a switch statement based on the length of the input.
- **Reasoning**: Similar to the other `parseLocalDate` methods, this one for char arrays uses a switch statement on length. This makes it difficult to extend with new date formats without modifying existing code, thus breaking the Open/Closed Principle. A design that decouples parsing logic from the method itself is preferable.

### OCP-021 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTime20
- **Confidence**: Found in 5 scan(s)
- **Lines**: 2146–2172
- **Type**: method
- **Description**: The `parseLocalDateTime20` method (overload for byte array) uses multiple `if-else if` blocks to handle different string formats.
- **Reasoning**: This overload for byte arrays also uses a series of `if-else if` conditions for parsing different formats. This violates OCP because it requires modifying existing code to add new formats. A strategy pattern or a similar extensible mechanism would be more appropriate.

### OCP-030 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTimeX
- **Confidence**: Found in 5 scan(s)
- **Lines**: 2581–2752
- **Type**: method
- **Description**: The `parseLocalDateTimeX` method uses a large switch statement based on the length of the input.
- **Reasoning**: This method uses a switch statement on the length of the input string to determine parsing logic. Adding new formats with different lengths would require modifying this switch statement, violating the Open/Closed Principle. An extensible parsing mechanism is needed.

### OCP-032 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseZonedDateTime16
- **Confidence**: Found in 4 scan(s)
- **Lines**: 3091–3170
- **Type**: method
- **Description**: The `parseZonedDateTime16` method uses multiple `if-else if` blocks to handle different string formats.
- **Reasoning**: This method uses a chain of `if-else if` blocks to parse ISO date with offset formats. Adding support for new formats would require modifying this method, which violates the Open/Closed Principle. A more extensible design is needed.

### OCP-019 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseMillis
- **Confidence**: Found in 3 scan(s)
- **Lines**: 600–673
- **Type**: method
- **Description**: The `parseMillis` method (overload for char array) uses conditional logic to determine parsing strategy.
- **Reasoning**: This overload of `parseMillis` for char arrays also uses a series of conditional checks and a switch statement to parse different formats. This monolithic approach makes it hard to add new formats without modifying the existing code, which is a violation of OCP. A strategy-based approach would be more suitable.

### OCP-022 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTime26
- **Confidence**: Found in 3 scan(s)
- **Lines**: 2185–2222
- **Type**: method
- **Description**: The `parseLocalDateTime26` method uses multiple `if-else if` blocks to handle different string formats.
- **Reasoning**: This method uses a series of `if-else if` statements to parse various date-time formats. Adding new formats would require modifying this method, violating OCP. A design that separates parsing logic, like a strategy pattern, would be more extensible.

### OCP-023 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTime26
- **Confidence**: Found in 3 scan(s)
- **Lines**: 2234–2271
- **Type**: method
- **Description**: The `parseLocalDateTime26` method (overload for char array) uses multiple `if-else if` blocks to handle different string formats.
- **Reasoning**: This overload for char arrays also uses a series of `if-else if` conditions for parsing different formats. This violates OCP because it requires modifying existing code to add new formats. A strategy pattern or a similar extensible mechanism would be more appropriate.

### OCP-025 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTime27
- **Confidence**: Found in 3 scan(s)
- **Lines**: 2333–2370
- **Type**: method
- **Description**: The `parseLocalDateTime27` method (overload for char array) uses multiple `if-else if` blocks to handle different string formats.
- **Reasoning**: This overload for char arrays also uses a series of `if-else if` conditions for parsing different formats. This violates OCP because it requires modifying existing code to add new formats. A strategy pattern or a similar extensible mechanism would be more appropriate.

### OCP-026 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTime28
- **Confidence**: Found in 3 scan(s)
- **Lines**: 2383–2420
- **Type**: method
- **Description**: The `parseLocalDateTime28` method uses multiple `if-else if` blocks to handle different string formats.
- **Reasoning**: This method uses a series of `if-else if` statements to parse various date-time formats. Adding new formats would require modifying this method, violating OCP. A design that separates parsing logic, like a strategy pattern, would be more extensible.

### OCP-034 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseZonedDateTime
- **Confidence**: Found in 3 scan(s)
- **Lines**: 3480–3536
- **Type**: method
- **Description**: The `parseZonedDateTime` method (overload for byte array) uses conditional logic to determine parsing strategy.
- **Reasoning**: This method contains several `if-else if` blocks that handle different lengths and formats of date-time strings. Adding support for new formats would require modifying this method, violating the Open/Closed Principle. A design that decouples parsing logic would be more extensible.

### OCP-036 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseZonedDateTime
- **Confidence**: Found in 3 scan(s)
- **Lines**: 3616–3968
- **Type**: method
- **Description**: The `parseZonedDateTime` method contains a large `switch` statement based on string length and multiple `if-else if` blocks.
- **Reasoning**: This method has a `switch` statement based on the length of the input string, and within those cases, further `if-else if` blocks handle specific formats. This violates OCP because adding support for new date-time formats requires modifying this extensive conditional logic. A more extensible design is needed.

### OCP-037 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.getZoneId
- **Confidence**: Found in 3 scan(s)
- **Lines**: 4369–4407
- **Type**: method
- **Description**: The `getZoneId` method uses a switch statement to handle known zone IDs.
- **Reasoning**: The `getZoneId` method uses a switch statement to handle specific zone IDs like '000', '+08:00', and 'CST'. While this is not as extensive as some other switch statements, adding new specific zone ID mappings would require modifying this method, thus violating OCP. A more flexible approach, like a configuration or external mapping, could be considered.

### OCP-038 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseMillis19
- **Confidence**: Found in 3 scan(s)
- **Lines**: 4554–4831
- **Type**: method
- **Description**: The `parseMillis19` method uses a large switch statement based on `DateTimeFormatPattern` and multiple conditional checks.
- **Reasoning**: This method uses a switch statement on `DateTimeFormatPattern` and then proceeds with extensive conditional logic to parse different date-time formats. Adding new formats would require modifying this method, violating the Open/Closed Principle. A strategy pattern or a registry for formatters would be more appropriate.

### OCP-043 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.format
- **Confidence**: Found in 3 scan(s)
- **Lines**: 4184–4229
- **Type**: method
- **Description**: The `format` method uses a switch statement based on the format string.
- **Reasoning**: The `format` method uses a switch statement to handle different format strings. To add support for a new format, this switch statement must be modified, violating the Open/Closed Principle. A more extensible approach would involve using a registry or strategy pattern for formatters.

### OCP-044 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.format
- **Confidence**: Found in 3 scan(s)
- **Lines**: 4241–4288
- **Type**: method
- **Description**: The `format` method (overload for ZonedDateTime) uses a switch statement based on the format string.
- **Reasoning**: This overload of `format` for `ZonedDateTime` also uses a switch statement based on the format string. Adding new formats requires modifying this existing code, which violates OCP. A design that decouples format handling, such as a registry or strategy pattern, would be more extensible.

### OCP-065 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.format
- **Confidence**: Found in 3 scan(s)
- **Lines**: 6472–6517
- **Type**: method
- **Description**: The `format` method (overload for int, int, int, int, int, int, DateTimeFormatPattern) uses a switch statement based on `DateTimeFormatPattern`.
- **Reasoning**: This method uses a switch statement on `DateTimeFormatPattern` to format dates and times. Adding new formats would require modifying this switch statement, violating the Open/Closed Principle. A registry or strategy pattern for formatters would be more extensible.

### OCP-069 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseMillis
- **Confidence**: Found in 3 scan(s)
- **Lines**: 537–596
- **Type**: method
- **Description**: The parseMillis method (char[] version) uses conditional logic (if-else if) to determine how to parse the date based on its characteristics.
- **Reasoning**: Similar to the byte array version, this `parseMillis` method also relies on `if-else if` statements to parse the date based on its length and content (`len`, `c0`, `c10`). Introducing support for new date formats would require modifying these conditional blocks, violating the Open/Closed Principle.

### OCP-070 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalTime11
- **Confidence**: Found in 3 scan(s)
- **Lines**: 838–857
- **Type**: method
- **Description**: The parseLocalTime11 method uses conditional logic (if-else if) to parse different time formats.
- **Reasoning**: The `parseLocalTime11` method uses `if-else if` statements to parse time strings based on separators (`:` and `.`) and digit positions. Adding support for new formats would require modifying these conditional branches, violating the Open/Closed Principle.

### OCP-071 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalTime12
- **Confidence**: Found in 3 scan(s)
- **Lines**: 865–888
- **Type**: method
- **Description**: The parseLocalTime12 method uses conditional logic (if-else if) to parse different time formats.
- **Reasoning**: The `parseLocalTime12` method employs `if-else if` statements to parse time strings based on separators (`:` and `.`) and digit positions. Supporting new formats would require modifying these conditional branches, violating the Open/Closed Principle.

### OCP-073 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTime26
- **Confidence**: Found in 3 scan(s)
- **Lines**: 1403–1427
- **Type**: method
- **Description**: The parseLocalDateTime26 method uses conditional logic to parse datetime formats.
- **Reasoning**: The `parseLocalDateTime26` method relies on conditional logic to parse datetime strings. Extending support to new formats would necessitate modifying these conditional checks, violating the Open/Closed Principle.

### OCP-076 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.format
- **Confidence**: Found in 3 scan(s)
- **Lines**: 3026–3070
- **Type**: method
- **Description**: The format method uses a switch statement on the DateTimeFormatPattern enum, violating the Open/Closed Principle.
- **Reasoning**: The `format(int year, int month, int dayOfMonth, DateTimeFormatPattern pattern)` method uses a switch statement on the `DateTimeFormatPattern` enum. Each case handles a specific format pattern. Adding support for new date formats would require modifying this switch statement, thus violating the Open/Closed Principle. The code is not open for extension without modification.

### OCP-114 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF8.java — JSONReaderUTF8
- **Confidence**: Found in 3 scan(s)
- **Lines**: 21–1957
- **Type**: class
- **Description**: Class contains numerous `nextIfName4MatchX` and `nextIfValue4MatchX` methods, suggesting a large conditional structure for parsing different token types.
- **Reasoning**: The `JSONReaderUTF8` class has a significant number of methods like `nextIfName4Match0` through `nextIfName4Match43` and `nextIfValue4Match2` through `nextIfValue4Match11`. These methods appear to be highly specific, likely implementing a large switch or if-else chain to identify and parse different JSON tokens based on their byte sequences. Adding support for new keywords or value types would require adding more such methods or modifying existing parsing logic within this class, violating the OCP. This suggests a violation where new functionality (handling different token types) requires modification of existing code rather than extension.

### OCP-115 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF16.java — JSONReaderUTF16
- **Confidence**: Found in 3 scan(s)
- **Lines**: 19–1608
- **Type**: class
- **Description**: Class contains numerous `nextIfName4MatchX` and `nextIfValue4MatchX` methods, suggesting a large conditional structure for parsing different token types.
- **Reasoning**: Similar to `JSONReaderUTF8`, the `JSONReaderUTF16` class exhibits a large number of methods like `nextIfName4Match0` through `nextIfName4Match43` and `nextIfValue4Match2` through `nextIfValue4Match11`. These methods are likely part of a large conditional parsing mechanism for different JSON tokens based on character sequences. Introducing new token types or parsing rules would necessitate adding more methods or modifying the existing conditional logic, which goes against the OCP's principle of being closed for modification but open for extension.

### OCP-116 [HIGH] core/src/main/java/com/alibaba/fastjson2/JSONReader.java — JSONReader
- **Confidence**: Found in 3 scan(s)
- **Lines**: 54–6887
- **Type**: class
- **Description**: Abstract class with a vast number of abstract methods for reading various data types and formats, indicating a monolithic design that is difficult to extend.
- **Reasoning**: The `JSONReader` abstract class defines an enormous number of abstract methods for reading different data types (`readInt32`, `readInt64`, `readDouble`, `readBigDecimal`, `readLocalDate`, `readLocalDateTime`, `readLocalTime`, `readZonedDateTime`, etc.) and for handling specific parsing scenarios (`nextIfName4MatchX`, `nextIfValue4MatchX`). This creates a very large and complex interface. Any new data type or parsing strategy would require adding a new abstract method or modifying the existing ones, violating the OCP. The sheer volume of these methods suggests that the responsibilities are not well-separated, making it hard to extend without modification. A more OCP-compliant design might involve a plugin architecture or a more granular set of interfaces for different reading capabilities.

### OCP-119 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/reader/ObjectReaderCreatorASM.java — ObjectReaderCreatorASM
- **Confidence**: Found in 3 scan(s)
- **Lines**: 31–4626
- **Type**: class
- **Description**: Class generates ASM code for ObjectReaders, with methods like `genMethodReadObject`, `genMethodReadJSONBObject`, `genMethodReadFieldValue` suggesting a large conditional structure for reading different types.
- **Reasoning**: Similar to `ObjectWriterCreatorASM`, this class generates ASM bytecode for `ObjectReader` implementations. Methods like `genMethodReadObject`, `genMethodReadJSONBObject`, `genMethodReadFieldValue`, and `genReadHashCode64ValueForNonDefaultConstructor` likely contain extensive conditional logic to handle the parsing of various data types and structures. Extending this class to support new types or parsing strategies would probably involve modifying these code generation methods, which violates the OCP. The ASM-based approach, while efficient, can make it difficult to extend without altering the core generation logic.

### OCP-120 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/BeanUtils.java — BeanUtils
- **Confidence**: Found in 3 scan(s)
- **Lines**: 31–3175
- **Type**: class
- **Description**: Class contains numerous methods for introspection (getters, setters, fields, constructors) and naming strategy conversions, indicating a lack of modularity.
- **Reasoning**: The `BeanUtils` class performs a wide range of reflection-based operations for bean introspection, including finding getters, setters, fields, constructors, and handling naming strategy conversions (`setterName`, `getterName`, `fieldName`). The sheer number of utility methods and the broad scope of responsibilities suggest that adding new introspection logic or supporting new naming strategies might require modifying this central utility class. A more OCP-compliant approach would involve separating these concerns into smaller, more specialized utility classes or using a strategy pattern for naming conventions.

### OCP-121 [HIGH] core/src/main/java/com/alibaba/fastjson2/JSONWriter.java — JSONWriter
- **Confidence**: Found in 3 scan(s)
- **Lines**: 68–5055
- **Type**: class
- **Description**: Abstract class with a vast number of abstract methods for writing various data types and formats, indicating a monolithic design that is difficult to extend.
- **Reasoning**: The `JSONWriter` abstract class defines a very large number of abstract methods for writing different data types (`writeInt8`, `writeInt16`, `writeInt32`, `writeInt64`, `writeFloat`, `writeDouble`, `writeString`, `writeLocalDate`, `writeLocalDateTime`, `writeLocalTime`, `writeZonedDateTime`, etc.) and for handling specific writing scenarios (e.g., `startArray`, `endArray`, `writeComma`, `writeNameRaw`). This creates a monolithic interface where adding support for new data types or writing formats would likely require adding new abstract methods or modifying existing ones, violating the OCP. The extensive set of methods suggests a lack of separation of concerns, making it difficult to extend without modification. A more OCP-compliant design might involve a more modular approach, perhaps using a visitor pattern or delegating writing logic to specific formatters.

### OCP-017 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.format
- **Confidence**: Found in 2 scan(s)
- **Lines**: 1617–1654
- **Type**: method
- **Description**: The format method (Date overload) uses a switch statement based on the format string.
- **Reasoning**: The `format` method, overloaded to accept a `Date` object, uses a `switch` statement based on the `format` string. This violates the Open/Closed Principle because adding new formats requires modifying the existing `switch` statement. The principle states that software entities should be open for extension but closed for modification.

### OCP-024 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTime27
- **Confidence**: Found in 2 scan(s)
- **Lines**: 2284–2321
- **Type**: method
- **Description**: The `parseLocalDateTime27` method uses multiple `if-else if` blocks to handle different string formats.
- **Reasoning**: This method handles various date-time formats using a chain of `if-else if` statements. This violates OCP because adding new formats requires modifying the existing code. A design that decouples format handling, such as a registry or strategy pattern, would be more compliant.

### OCP-027 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTime28
- **Confidence**: Found in 2 scan(s)
- **Lines**: 2432–2469
- **Type**: method
- **Description**: The `parseLocalDateTime28` method (overload for byte array) uses multiple `if-else if` blocks to handle different string formats.
- **Reasoning**: This overload for byte arrays also uses a series of `if-else if` conditions for parsing different formats. This violates OCP because it requires modifying existing code to add new formats. A strategy pattern or a similar extensible mechanism would be more appropriate.

### OCP-029 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTime29
- **Confidence**: Found in 2 scan(s)
- **Lines**: 2531–2568
- **Type**: method
- **Description**: The `parseLocalDateTime29` method (overload for char array) uses multiple `if-else if` blocks to handle different string formats.
- **Reasoning**: This overload for char arrays also uses a series of `if-else if` conditions for parsing different formats. This violates OCP because it requires modifying existing code to add new formats. A strategy pattern or a similar extensible mechanism would be more appropriate.

### OCP-033 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseZonedDateTime16
- **Confidence**: Found in 2 scan(s)
- **Lines**: 3182–3261
- **Type**: method
- **Description**: The `parseZonedDateTime16` method (overload for byte array) uses multiple `if-else if` blocks to handle different string formats.
- **Reasoning**: This overload for byte arrays also uses a series of `if-else if` conditions for parsing different formats. This violates OCP because it requires modifying existing code to add new formats. A strategy pattern or a similar extensible mechanism would be more appropriate.

### OCP-035 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseZonedDateTime
- **Confidence**: Found in 2 scan(s)
- **Lines**: 3548–3604
- **Type**: method
- **Description**: The `parseZonedDateTime` method (overload for char array) uses conditional logic to determine parsing strategy.
- **Reasoning**: This overload for char arrays also uses `if-else if` blocks to handle different date-time formats. This violates OCP because new formats require modifications to existing code. A strategy pattern or a registry for parsers would improve extensibility.

### OCP-040 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseMillis19
- **Confidence**: Found in 2 scan(s)
- **Lines**: 5132–5409
- **Type**: method
- **Description**: The `parseMillis19` method (overload for char array) uses a large switch statement based on `DateTimeFormatPattern` and multiple conditional checks.
- **Reasoning**: This overload for char arrays also uses a switch statement on `DateTimeFormatPattern` and extensive conditional logic. This violates OCP because adding new formats requires modifying this method. A design that decouples parsing logic, such as a strategy pattern, would be more compliant.

### OCP-045 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.format
- **Confidence**: Found in 2 scan(s)
- **Lines**: 4300–4347
- **Type**: method
- **Description**: The `format` method (overload for LocalDateTime) uses a switch statement based on the format string.
- **Reasoning**: This overload of `format` for `LocalDateTime` uses a switch statement on the format string. Supporting new formats necessitates modifying this method, violating OCP. A design that uses a registry or strategy pattern for formatters would be more compliant.

### OCP-046 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.format
- **Confidence**: Found in 2 scan(s)
- **Lines**: 4418–4475
- **Type**: method
- **Description**: The `format` method (overload for int, int, int) uses a switch statement based on `DateTimeFormatPattern`.
- **Reasoning**: This method uses a switch statement on `DateTimeFormatPattern` to format dates. Adding new formats would require modifying this switch statement, violating the Open/Closed Principle. A registry or strategy pattern for formatters would be more extensible.

### OCP-047 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.format
- **Confidence**: Found in 2 scan(s)
- **Lines**: 4487–4544
- **Type**: method
- **Description**: The `format` method (overload for int, int, int, DateTimeFormatPattern) uses a switch statement based on `DateTimeFormatPattern`.
- **Reasoning**: This method uses a switch statement on `DateTimeFormatPattern` to format dates. Adding new formats would require modifying this switch statement, violating the Open/Closed Principle. A registry or strategy pattern for formatters would be more extensible.

### OCP-051 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.format
- **Confidence**: Found in 2 scan(s)
- **Lines**: 5674–5719
- **Type**: method
- **Description**: The `format` method (overload for int, int, int, int, int, int, DateTimeFormatPattern) uses a switch statement based on `DateTimeFormatPattern`.
- **Reasoning**: This method uses a switch statement on `DateTimeFormatPattern` to format dates and times. Adding new formats would require modifying this switch statement, violating the Open/Closed Principle. A registry or strategy pattern for formatters would be more extensible.

### OCP-054 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.format
- **Confidence**: Found in 2 scan(s)
- **Lines**: 5845–5890
- **Type**: method
- **Description**: The `format` method (overload for int, int, int, int, int, int, DateTimeFormatPattern) uses a switch statement based on `DateTimeFormatPattern`.
- **Reasoning**: This method uses a switch statement on `DateTimeFormatPattern` to format dates and times. Adding new formats would require modifying this switch statement, violating the Open/Closed Principle. A registry or strategy pattern for formatters would be more extensible.

### OCP-064 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.format
- **Confidence**: Found in 2 scan(s)
- **Lines**: 6415–6460
- **Type**: method
- **Description**: The `format` method (overload for int, int, int, int, int, int, DateTimeFormatPattern) uses a switch statement based on `DateTimeFormatPattern`.
- **Reasoning**: This method uses a switch statement on `DateTimeFormatPattern` to format dates and times. Adding new formats would require modifying this switch statement, violating the Open/Closed Principle. A registry or strategy pattern for formatters would be more extensible.

### OCP-066 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.format
- **Confidence**: Found in 2 scan(s)
- **Lines**: 6529–6574
- **Type**: method
- **Description**: The `format` method (overload for int, int, int, int, int, int, DateTimeFormatPattern) uses a switch statement based on `DateTimeFormatPattern`.
- **Reasoning**: This method uses a switch statement on `DateTimeFormatPattern` to format dates and times. Adding new formats would require modifying this switch statement, violating the Open/Closed Principle. A registry or strategy pattern for formatters would be more extensible.

### OCP-067 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.format
- **Confidence**: Found in 2 scan(s)
- **Lines**: 6586–6631
- **Type**: method
- **Description**: The `format` method (overload for int, int, int, int, int, int, DateTimeFormatPattern) uses a switch statement based on `DateTimeFormatPattern`.
- **Reasoning**: This method uses a switch statement on `DateTimeFormatPattern` to format dates and times. Adding new formats would require modifying this switch statement, violating the Open/Closed Principle. A registry or strategy pattern for formatters would be more extensible.

### OCP-072 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTime18
- **Confidence**: Found in 2 scan(s)
- **Lines**: 1224–1319
- **Type**: method
- **Description**: The parseLocalDateTime18 method uses a large if-else if chain to handle various datetime formats.
- **Reasoning**: This method contains a significant `if-else if` chain to parse LocalDateTime strings based on their length and format (e.g., 'yyyy-M-ddTHH:mm:ss', 'yyyy-MM-ddTH:mm:ss'). Adding support for new datetime formats necessitates modifying this existing conditional chain, violating the Open/Closed Principle.

### OCP-074 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.format
- **Confidence**: Found in 2 scan(s)
- **Lines**: 2928–2964
- **Type**: method
- **Description**: The format method uses a switch statement on the format string, violating the Open/Closed Principle.
- **Reasoning**: The `format(ZonedDateTime zdt, String format)` method contains a switch statement that handles different date format strings. To add support for a new date format, this method would need to be modified, thus violating the Open/Closed Principle. This indicates a lack of extensibility without modification. A better approach would be to use a strategy pattern or a registry for formatters.

### OCP-075 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.format
- **Confidence**: Found in 2 scan(s)
- **Lines**: 2977–3013
- **Type**: method
- **Description**: The format method uses a switch statement on the format string, violating the Open/Closed Principle.
- **Reasoning**: The `format(LocalDateTime ldt, String format)` method contains a switch statement that handles different date format strings. To add support for a new date format, this method would need to be modified, thus violating the Open/Closed Principle. This indicates a lack of extensibility without modification. A better approach would be to use a strategy pattern or a registry for formatters.

### OCP-080 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTime19(byte[] str, int off)
- **Confidence**: Found in 2 scan(s)
- **Lines**: 2502–2539
- **Type**: method
- **Description**: Multiple conditional branches for parsing different date formats violate OCP.
- **Reasoning**: This method, similar to its char array overload, uses multiple `if-else if` statements to parse different LocalDateTime formats. This violates the Open/Closed Principle because adding new formats requires modifying the existing method. The design lacks extensibility for new date formats without altering existing code.

### OCP-083 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTimeX(byte[] str, int offset, int len)
- **Confidence**: Found in 2 scan(s)
- **Lines**: 3312–3475
- **Type**: method
- **Description**: Switch statement on length for LocalDateTime parsing violates OCP.
- **Reasoning**: Similar to the char array overload, this method uses a switch statement based on the `len` of the byte array to parse LocalDateTime. Adding support for new date formats with different lengths would require modifying this method, violating the Open/Closed Principle. An extension mechanism like a strategy pattern or a map of length to parser would be more appropriate.

### OCP-084 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseZonedDateTime(char[] str, int off, int len, ZoneId defaultZoneId)
- **Confidence**: Found in 2 scan(s)
- **Lines**: 3997–4194
- **Type**: method
- **Description**: Multiple conditional branches based on length for parsing ZonedDateTime violate OCP.
- **Reasoning**: Similar to the byte array overload, this method uses a `switch` statement on `len` to parse ZonedDateTime strings. Each `case` handles a specific format. Extending this to support new formats necessitates modifying the method, thus violating the Open/Closed Principle. The design should allow for adding new parsers without altering existing code.

### OCP-087 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.format(int year, int month, int dayOfMonth, DateTimeFormatPattern pattern)
- **Confidence**: Found in 2 scan(s)
- **Lines**: 6622–6672
- **Type**: method
- **Description**: Conditional logic based on DateTimeFormatPattern violates OCP.
- **Reasoning**: This method uses conditional logic based on the `DateTimeFormatPattern` enum to format dates. Adding a new pattern would require modifying this method, violating the Open/Closed Principle. A design that allows for extending formatting logic without modifying existing code is preferable.

### OCP-088 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.format(long timeMillis, DateTimeFormatPattern pattern)
- **Confidence**: Found in 2 scan(s)
- **Lines**: 6835–6978
- **Type**: method
- **Description**: Multiple conditional branches for formatting dates violate OCP.
- **Reasoning**: The `format` method uses a `switch` statement on `DateTimeFormatPattern` and contains extensive conditional logic within each case to format dates. Adding support for a new format would require modifying this method, violating the Open/Closed Principle. This is a clear violation of OCP due to the extensive conditional logic based on input characteristics.

### OCP-089 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.format(int year, int month, int dayOfMonth, int hour, int minute, int second, DateTimeFormatPattern pattern)
- **Confidence**: Found in 2 scan(s)
- **Lines**: 6997–7057
- **Type**: method
- **Description**: Conditional logic based on DateTimeFormatPattern violates OCP.
- **Reasoning**: This method uses conditional logic based on the `DateTimeFormatPattern` enum to format date-time values. Adding a new pattern would require modifying this method, violating the Open/Closed Principle. A design that allows for extending formatting logic without modifying existing code is preferable.

### OCP-091 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDate(char[] str, int off, int len)
- **Confidence**: Found in 2 scan(s)
- **Lines**: 887–923
- **Type**: method
- **Description**: Switch statement on length for LocalDate parsing violates OCP.
- **Reasoning**: This method, similar to its byte array counterpart, uses a switch statement based on the `len` parameter to parse LocalDate from character arrays. This approach makes the code closed for extension but open for modification. To support new date formats or lengths, this method must be changed. An alternative would be to employ a more flexible parsing strategy, such as a map of handlers or a visitor pattern.

### OCP-092 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTime20(byte[] str, int off)
- **Confidence**: Found in 2 scan(s)
- **Lines**: 1113–1143
- **Type**: method
- **Description**: Conditional logic for parsing various date formats violates OCP.
- **Reasoning**: This method parses LocalDateTime from byte arrays and employs an if-else if structure to handle different formats. This design violates the Open/Closed Principle because adding new formats necessitates modifying this method. A more extensible solution would involve separating parsing logic into different classes or using a registry.

### OCP-093 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.format(Date date, String format)
- **Confidence**: Found in 2 scan(s)
- **Lines**: 2464–2499
- **Type**: method
- **Description**: Switch statement on format string for date formatting violates OCP.
- **Reasoning**: The `format` method uses a switch statement based on the `format` string to determine how to format a Date. Adding new formatting patterns requires modifying this existing method, which violates the Open/Closed Principle. This can be refactored using a map of formatters or a strategy pattern to allow for extensions without modifying the core method.

### OCP-118 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/writer/ObjectWriterCreatorASM.java — ObjectWriterCreatorASM
- **Confidence**: Found in 2 scan(s)
- **Lines**: 29–5305
- **Type**: class
- **Description**: Class generates ASM code for ObjectWriters, with methods like `genMethodWrite`, `genMethodWriteJSONB`, `genMethodWriteArrayMapping` suggesting a large conditional structure for writing different types.
- **Reasoning**: The `ObjectWriterCreatorASM` class is responsible for generating ASM bytecode for `ObjectWriter` implementations. It contains methods like `genMethodWrite`, `genMethodWriteJSONB`, and `genMethodWriteArrayMapping`, which likely involve complex conditional logic (e.g., switch statements or extensive if-else chains) to handle the writing of different data types and formats. Adding support for new types or writing strategies would likely require modifying these core generation methods, thus violating the OCP. The class is designed to be extensible through ASM code generation, but the underlying generation logic itself might not be easily extendable without modification.

### OCP-122 [HIGH] core/src/main/java/com/alibaba/fastjson2/JSON.java — JSON
- **Confidence**: Found in 2 scan(s)
- **Lines**: 1–4643
- **Type**: class
- **Description**: Top-level class with a massive number of static methods for parsing and writing JSON, indicating a lack of separation of concerns and potential for modification when adding new features.
- **Reasoning**: The `JSON` class acts as a central entry point for JSON parsing and serialization. It contains an overwhelming number of static methods for `parse`, `parseObject`, `parseArray`, `toJSONString`, `toJSONBytes`, `writeTo`, `isValid`, `to`, etc., with numerous overloads for different input types (String, byte[], char[], InputStream, URL, ByteBuffer), output formats (JSON, JSONB), and features. This monolithic design violates the OCP because adding new parsing or serialization capabilities (e.g., support for a new data format or a new feature) would likely require modifying this already massive class. The principle of separation of concerns is not evident here, as this single class handles a vast array of functionalities. A more OCP-compliant design would involve delegating these responsibilities to specialized reader and writer implementations, potentially managed through a factory or provider pattern.

### OCP-123 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/TypeUtils.java — TypeUtils
- **Confidence**: Found in 2 scan(s)
- **Lines**: 29–3878
- **Type**: class
- **Description**: Class contains a large number of utility methods for type conversion, casting, and reflection, suggesting a lack of modularity.
- **Reasoning**: The `TypeUtils` class provides a wide array of static utility methods for type conversions (e.g., `toDate`, `toInstant`, `toBigDecimal`, `toBigInteger`, `toLong`, `toInt`, `toBoolean`, `toFloat`, `toDouble`), casting, parsing primitives, and reflection-related operations. The sheer volume and diversity of these methods indicate that the class is handling too many distinct responsibilities. Adding new type conversion logic or supporting new data types would likely require modifying this central utility class, violating the OCP. A more modular design would involve breaking down these utilities into smaller, more focused classes, perhaps based on the type of conversion or the target data type.

### OCP-124 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONB.java — JSONB
- **Confidence**: Found in 2 scan(s)
- **Lines**: 1–3209
- **Type**: class
- **Description**: The class provides static methods for parsing and writing JSONB, with many overloaded methods for different input types and features.
- **Reasoning**: Similar to the `JSON` class, `JSONB` offers a broad set of static methods for handling JSONB data, including `parse`, `parseObject`, `parseArray`, `toBytes`, `toJSONString`, `writeTo`. These methods are overloaded to support different input sources (byte[], InputStream), contexts, features, and symbol tables. The static and overloaded nature means that extending functionality, such as adding support for new JSONB types or features, would likely involve adding more static methods or modifying existing ones, which is a common indicator of potential OCP violations. A more extensible design might involve factory patterns or strategy patterns for JSONB serialization/deserialization.

### OCP-028 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTime29
- **Confidence**: Found in 1 scan(s)
- **Lines**: 2482–2519
- **Type**: method
- **Description**: The `parseLocalDateTime29` method uses multiple `if-else if` blocks to handle different string formats.
- **Reasoning**: This method handles various date-time formats using a chain of `if-else if` statements. This violates OCP because adding new formats requires modifying the existing code. A design that decouples format handling, such as a registry or strategy pattern, would be more compliant.

### OCP-039 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseMillis19
- **Confidence**: Found in 1 scan(s)
- **Lines**: 4843–5120
- **Type**: method
- **Description**: The `parseMillis19` method (overload for byte array) uses a large switch statement based on `DateTimeFormatPattern` and multiple conditional checks.
- **Reasoning**: This overload for byte arrays also uses a switch statement on `DateTimeFormatPattern` and extensive conditional logic. This violates OCP because adding new formats requires modifying this method. A design that decouples parsing logic, such as a strategy pattern, would be more compliant.

### OCP-041 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseMillis10
- **Confidence**: Found in 1 scan(s)
- **Lines**: 5422–5553
- **Type**: method
- **Description**: The `parseMillis10` method uses a switch statement based on `DateTimeFormatPattern`.
- **Reasoning**: This method uses a switch statement on `DateTimeFormatPattern` to handle different date formats. Adding new formats would require modifying this switch statement, violating the Open/Closed Principle. A more extensible design, like a registry or strategy pattern, would be preferable.

### OCP-042 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseMillis10
- **Confidence**: Found in 1 scan(s)
- **Lines**: 5565–5696
- **Type**: method
- **Description**: The `parseMillis10` method (overload for char array) uses a switch statement based on `DateTimeFormatPattern`.
- **Reasoning**: This overload for char arrays also uses a switch statement on `DateTimeFormatPattern`. This violates OCP because adding new formats requires modifying the existing code. A design that decouples format handling, such as a strategy pattern, would be more compliant.

### OCP-048 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.format
- **Confidence**: Found in 1 scan(s)
- **Lines**: 4819–4864
- **Type**: method
- **Description**: The `format` method (overload for int, int, int, DateTimeFormatPattern) uses a switch statement based on `DateTimeFormatPattern`.
- **Reasoning**: This method uses a switch statement on `DateTimeFormatPattern` to format dates based on year, month, and day. Adding new formats would require modifying this switch statement, violating the Open/Closed Principle. A registry or strategy pattern for formatters would be more extensible.

### OCP-049 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.format
- **Confidence**: Found in 1 scan(s)
- **Lines**: 5104–5149
- **Type**: method
- **Description**: The `format` method (overload for int, int, int, int, int, int, DateTimeFormatPattern) uses a switch statement based on `DateTimeFormatPattern`.
- **Reasoning**: This method uses a switch statement on `DateTimeFormatPattern` to format dates and times. Adding new formats would require modifying this switch statement, violating the Open/Closed Principle. A registry or strategy pattern for formatters would be more extensible.

### OCP-050 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.format
- **Confidence**: Found in 1 scan(s)
- **Lines**: 5389–5434
- **Type**: method
- **Description**: The `format` method (overload for int, int, int, int, int, int, DateTimeFormatPattern) uses a switch statement based on `DateTimeFormatPattern`.
- **Reasoning**: This method uses a switch statement on `DateTimeFormatPattern` to format dates and times. Adding new formats would require modifying this switch statement, violating the Open/Closed Principle. A registry or strategy pattern for formatters would be more extensible.

### OCP-052 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.format
- **Confidence**: Found in 1 scan(s)
- **Lines**: 5731–5776
- **Type**: method
- **Description**: The `format` method (overload for int, int, int, int, int, int, DateTimeFormatPattern) uses a switch statement based on `DateTimeFormatPattern`.
- **Reasoning**: This method uses a switch statement on `DateTimeFormatPattern` to format dates and times. Adding new formats would require modifying this switch statement, violating the Open/Closed Principle. A registry or strategy pattern for formatters would be more extensible.

### OCP-053 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.format
- **Confidence**: Found in 1 scan(s)
- **Lines**: 5788–5833
- **Type**: method
- **Description**: The `format` method (overload for int, int, int, int, int, int, DateTimeFormatPattern) uses a switch statement based on `DateTimeFormatPattern`.
- **Reasoning**: This method uses a switch statement on `DateTimeFormatPattern` to format dates and times. Adding new formats would require modifying this switch statement, violating the Open/Closed Principle. A registry or strategy pattern for formatters would be more extensible.

### OCP-055 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.format
- **Confidence**: Found in 1 scan(s)
- **Lines**: 5902–5947
- **Type**: method
- **Description**: The `format` method (overload for int, int, int, int, int, int, DateTimeFormatPattern) uses a switch statement based on `DateTimeFormatPattern`.
- **Reasoning**: This method uses a switch statement on `DateTimeFormatPattern` to format dates and times. Adding new formats would require modifying this switch statement, violating the Open/Closed Principle. A registry or strategy pattern for formatters would be more extensible.

### OCP-056 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.format
- **Confidence**: Found in 1 scan(s)
- **Lines**: 5959–6004
- **Type**: method
- **Description**: The `format` method (overload for int, int, int, int, int, int, DateTimeFormatPattern) uses a switch statement based on `DateTimeFormatPattern`.
- **Reasoning**: This method uses a switch statement on `DateTimeFormatPattern` to format dates and times. Adding new formats would require modifying this switch statement, violating the Open/Closed Principle. A registry or strategy pattern for formatters would be more extensible.

### OCP-057 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.format
- **Confidence**: Found in 1 scan(s)
- **Lines**: 6016–6061
- **Type**: method
- **Description**: The `format` method (overload for int, int, int, int, int, int, DateTimeFormatPattern) uses a switch statement based on `DateTimeFormatPattern`.
- **Reasoning**: This method uses a switch statement on `DateTimeFormatPattern` to format dates and times. Adding new formats would require modifying this switch statement, violating the Open/Closed Principle. A registry or strategy pattern for formatters would be more extensible.

### OCP-058 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.format
- **Confidence**: Found in 1 scan(s)
- **Lines**: 6073–6118
- **Type**: method
- **Description**: The `format` method (overload for int, int, int, int, int, int, DateTimeFormatPattern) uses a switch statement based on `DateTimeFormatPattern`.
- **Reasoning**: This method uses a switch statement on `DateTimeFormatPattern` to format dates and times. Adding new formats would require modifying this switch statement, violating the Open/Closed Principle. A registry or strategy pattern for formatters would be more extensible.

### OCP-059 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.format
- **Confidence**: Found in 1 scan(s)
- **Lines**: 6130–6175
- **Type**: method
- **Description**: The `format` method (overload for int, int, int, int, int, int, DateTimeFormatPattern) uses a switch statement based on `DateTimeFormatPattern`.
- **Reasoning**: This method uses a switch statement on `DateTimeFormatPattern` to format dates and times. Adding new formats would require modifying this switch statement, violating the Open/Closed Principle. A registry or strategy pattern for formatters would be more extensible.

### OCP-060 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.format
- **Confidence**: Found in 1 scan(s)
- **Lines**: 6187–6232
- **Type**: method
- **Description**: The `format` method (overload for int, int, int, int, int, int, DateTimeFormatPattern) uses a switch statement based on `DateTimeFormatPattern`.
- **Reasoning**: This method uses a switch statement on `DateTimeFormatPattern` to format dates and times. Adding new formats would require modifying this switch statement, violating the Open/Closed Principle. A registry or strategy pattern for formatters would be more extensible.

### OCP-061 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.format
- **Confidence**: Found in 1 scan(s)
- **Lines**: 6244–6289
- **Type**: method
- **Description**: The `format` method (overload for int, int, int, int, int, int, DateTimeFormatPattern) uses a switch statement based on `DateTimeFormatPattern`.
- **Reasoning**: This method uses a switch statement on `DateTimeFormatPattern` to format dates and times. Adding new formats would require modifying this switch statement, violating the Open/Closed Principle. A registry or strategy pattern for formatters would be more extensible.

### OCP-062 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.format
- **Confidence**: Found in 1 scan(s)
- **Lines**: 6301–6346
- **Type**: method
- **Description**: The `format` method (overload for int, int, int, int, int, int, DateTimeFormatPattern) uses a switch statement based on `DateTimeFormatPattern`.
- **Reasoning**: This method uses a switch statement on `DateTimeFormatPattern` to format dates and times. Adding new formats would require modifying this switch statement, violating the Open/Closed Principle. A registry or strategy pattern for formatters would be more extensible.

### OCP-063 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.format
- **Confidence**: Found in 1 scan(s)
- **Lines**: 6358–6403
- **Type**: method
- **Description**: The `format` method (overload for int, int, int, int, int, int, DateTimeFormatPattern) uses a switch statement based on `DateTimeFormatPattern`.
- **Reasoning**: This method uses a switch statement on `DateTimeFormatPattern` to format dates and times. Adding new formats would require modifying this switch statement, violating the Open/Closed Principle. A registry or strategy pattern for formatters would be more extensible.

### OCP-068 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDate
- **Confidence**: Found in 1 scan(s)
- **Lines**: 763–799
- **Type**: method
- **Description**: The parseLocalDate method (byte[] version) uses a switch statement based on the length of the input.
- **Reasoning**: This `parseLocalDate` method, which operates on byte arrays, also includes a `switch` statement based on the `len` parameter. Adding support for new date formats with different lengths requires modifying this existing `switch` statement, which is a violation of the Open/Closed Principle.

### OCP-077 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.format
- **Confidence**: Found in 1 scan(s)
- **Lines**: 3160–3196
- **Type**: method
- **Description**: The format method uses a switch statement on the DateTimeFormatPattern enum, violating the Open/Closed Principle.
- **Reasoning**: The `format(long timeMillis, DateTimeFormatPattern pattern)` method uses a switch statement on the `DateTimeFormatPattern` enum. Each case handles a specific format pattern. Adding support for new date-time formats would require modifying this switch statement, thus violating the Open/Closed Principle. The code is not open for extension without modification.

### OCP-078 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTime(char[] str, int off, int len)
- **Confidence**: Found in 1 scan(s)
- **Lines**: 385–431
- **Type**: method
- **Description**: Switch statement on length for LocalDateTime parsing violates OCP.
- **Reasoning**: The `parseLocalDateTime` method uses a switch statement on the `len` (length) of the character array to determine the parsing logic. This means that to support a new LocalDateTime format (which would likely correspond to a different length), this method would need to be modified. This violates the Open/Closed Principle. An extension mechanism like a strategy pattern or a map of length to parser would be more appropriate.

### OCP-079 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTime12(char[] str, int off)
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1586–1624
- **Type**: method
- **Description**: Multiple conditional branches for parsing different date formats violate OCP.
- **Reasoning**: The `parseLocalDateTime12` method uses multiple `if-else if` conditions to handle different date formats. This violates the Open/Closed Principle because adding new formats requires modifying this method. The code is not open for extension without modification.

### OCP-081 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTime20(char[] str, int off)
- **Confidence**: Found in 1 scan(s)
- **Lines**: 2558–2592
- **Type**: method
- **Description**: Multiple conditional branches for parsing different date formats violate OCP.
- **Reasoning**: The `parseLocalDateTime20` method uses multiple `if-else if` conditions to parse different date formats. Adding support for a new format would require modifying this method, violating the Open/Closed Principle. This indicates a 'switch on type' smell (specifically, 'switch on length/format').

### OCP-082 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTime28(byte[] str, int off)
- **Confidence**: Found in 1 scan(s)
- **Lines**: 2956–2995
- **Type**: method
- **Description**: Multiple conditional branches for parsing different date formats violate OCP.
- **Reasoning**: This method, similar to its char array overload, uses multiple `if-else if` statements to parse different LocalDateTime formats. This violates the Open/Closed Principle because adding new formats requires modifying the existing method. The design lacks extensibility for new date formats without altering existing code.

### OCP-085 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.format(LocalDateTime ldt, String format)
- **Confidence**: Found in 1 scan(s)
- **Lines**: 6510–6547
- **Type**: method
- **Description**: Switch statement for date formatting violates OCP.
- **Reasoning**: The `format` method uses a `switch` statement on the `format` string to determine how to format the LocalDateTime. Adding support for a new date format would require modifying this existing method, thus violating the Open/Closed Principle. A more OCP-compliant approach would involve a strategy pattern or a registry for different date formatters.

### OCP-086 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.format(LocalDate localDate, String format)
- **Confidence**: Found in 1 scan(s)
- **Lines**: 6566–6603
- **Type**: method
- **Description**: Switch statement for date formatting violates OCP.
- **Reasoning**: The `format` method uses a `switch` statement on the `format` string to determine how to format the LocalDate. Adding support for a new date format would require modifying this existing method, thus violating the Open/Closed Principle. A more OCP-compliant approach would involve a strategy pattern or a registry for different date formatters.

### OCP-090 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseDate(String str, String format, ZoneId zoneId)
- **Confidence**: Found in 1 scan(s)
- **Lines**: 87–127
- **Type**: method
- **Description**: Switch statement on format string for date parsing violates OCP.
- **Reasoning**: The `parseDate` method contains a large switch statement based on the `format` string. Adding support for a new date format requires modifying this existing method, thus violating the Open/Closed Principle. This switch statement can be replaced with a more extensible strategy, like a map of formatters or a plugin system.

### OCP-094 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseDate
- **Confidence**: Found in 1 scan(s)
- **Lines**: 168–226
- **Type**: method
- **Description**: The `parseDate` method uses a switch statement on the format string, requiring modification to support new date formats.
- **Reasoning**: The `parseDate` method in `DateUtils` contains a `switch` statement that handles various date format strings. To add support for a new date format, this `switch` statement would need to be modified by adding a new `case`. This violates the Open/Closed Principle because the method is not closed for modification when new behaviors (handling new formats) are needed. A more OCP-compliant approach would involve a strategy pattern or a registry of format handlers that can be extended without modifying the existing `parseDate` method.

### OCP-095 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTime
- **Confidence**: Found in 1 scan(s)
- **Lines**: 953–1011
- **Type**: method
- **Description**: The `parseLocalDateTime` method uses a switch statement on the length of the input, requiring modification to support new date/time formats.
- **Reasoning**: The `parseLocalDateTime` method in `DateUtils` uses a `switch` statement based on the `len` (length) of the input byte array. Each `case` handles a specific length, implying a specific format. To support new date/time formats that might have different lengths or structures, this `switch` statement would need to be modified. This violates the Open/Closed Principle as the method is not closed for modification when new parsing logic is required. An extension-based approach, such as using a map of length-to-parser or a more flexible parsing strategy, would be more compliant with OCP.

### OCP-096 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.format
- **Confidence**: Found in 1 scan(s)
- **Lines**: 3270–3302
- **Type**: method
- **Description**: The `format` method uses a switch statement on the format string, requiring modification to support new date formats.
- **Reasoning**: The `format` method in `DateUtils` uses a `switch` statement to handle different format strings. To add support for a new date format, this `switch` statement would need to be modified by adding a new `case`. This violates the Open/Closed Principle because the method is not closed for modification when new behaviors (handling new formats) are needed. A more OCP-compliant approach would involve a strategy pattern or a registry of formatters that can be extended without modifying the existing `format` method.

### OCP-097 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.format
- **Confidence**: Found in 1 scan(s)
- **Lines**: 3974–4006
- **Type**: method
- **Description**: The `format` method uses a switch statement on the format string, requiring modification to support new date formats.
- **Reasoning**: The `format` method in `DateUtils` uses a `switch` statement to handle different format strings. To add support for a new date format, this `switch` statement would need to be modified by adding a new `case`. This violates the Open/Closed Principle because the method is not closed for modification when new behaviors (handling new formats) are needed. A more OCP-compliant approach would involve a strategy pattern or a registry of formatters that can be extended without modifying the existing `format` method.

### OCP-098 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.format
- **Confidence**: Found in 1 scan(s)
- **Lines**: 4282–4314
- **Type**: method
- **Description**: The `format` method uses a switch statement on the format string, requiring modification to support new date formats.
- **Reasoning**: The `format` method in `DateUtils` uses a `switch` statement to handle different format strings. To add support for a new date format, this `switch` statement would need to be modified by adding a new `case`. This violates the Open/Closed Principle because the method is not closed for modification when new behaviors (handling new formats) are needed. A more OCP-compliant approach would involve a strategy pattern or a registry of formatters that can be extended without modifying the existing `format` method.

### OCP-099 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTime
- **Confidence**: Found in 1 scan(s)
- **Lines**: 419–468
- **Type**: method
- **Description**: The `parseLocalDateTime` method has a switch statement that handles different date string lengths.
- **Reasoning**: This `parseLocalDateTime` method uses a `switch` statement on the `len` parameter to parse dates based on their string length. Adding support for new date formats with different lengths would require modifying this `switch` statement, which is a violation of the Open/Closed Principle.

### OCP-100 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTime26
- **Confidence**: Found in 1 scan(s)
- **Lines**: 2352–2390
- **Type**: method
- **Description**: The `parseLocalDateTime26` method for character arrays uses direct parsing logic for a specific format.
- **Reasoning**: This overload of `parseLocalDateTime26` for character arrays also directly parses a date-time string assuming a specific format. Extending it to support new formats would require modifying this method, thus violating the Open/Closed Principle.

### OCP-101 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTime27
- **Confidence**: Found in 1 scan(s)
- **Lines**: 2405–2443
- **Type**: method
- **Description**: The `parseLocalDateTime27` method uses direct parsing logic for a specific format.
- **Reasoning**: The `parseLocalDateTime27` method directly parses a date-time string assuming a specific format. Supporting new formats would require modifying this method, violating the Open/Closed Principle.

### OCP-102 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.format
- **Confidence**: Found in 1 scan(s)
- **Lines**: 7586–7634
- **Type**: method
- **Description**: The `format` method has a switch statement that handles specific format strings.
- **Reasoning**: The `format` method uses a `switch` statement to handle predefined date format strings like "yyyy-MM-dd HH:mm:ss" and "yyyyMMdd". Adding support for new formats would require modifying this `switch` statement, violating the Open/Closed Principle.

### OCP-103 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.format
- **Confidence**: Found in 1 scan(s)
- **Lines**: 7479–7536
- **Type**: method
- **Description**: The `format` method has a switch statement that handles specific format strings.
- **Reasoning**: This `format` method also uses a `switch` statement to handle predefined date format strings. Adding new formats necessitates modification of this `switch` statement, violating the Open/Closed Principle.

### OCP-104 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.format
- **Confidence**: Found in 1 scan(s)
- **Lines**: 7404–7461
- **Type**: method
- **Description**: The `format` method has a switch statement that handles specific format strings.
- **Reasoning**: This `format` method uses a `switch` statement to handle predefined date format strings. Extending it to support new formats requires modification of this `switch` statement, violating the Open/Closed Principle.

### OCP-105 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.format
- **Confidence**: Found in 1 scan(s)
- **Lines**: 7329–7386
- **Type**: method
- **Description**: The `format` method has a switch statement that handles specific format strings.
- **Reasoning**: This `format` method utilizes a `switch` statement to manage predefined date format strings. Adding new formats requires modifying this `switch` statement, which violates the Open/Closed Principle.

### OCP-106 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.format
- **Confidence**: Found in 1 scan(s)
- **Lines**: 7254–7311
- **Type**: method
- **Description**: The `format` method has a switch statement that handles specific format strings.
- **Reasoning**: This `format` method uses a `switch` statement to process predefined date format strings. Any extension to support new formats would necessitate modification of this `switch` statement, violating the Open/Closed Principle.

### OCP-107 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.format
- **Confidence**: Found in 1 scan(s)
- **Lines**: 7197–7251
- **Type**: method
- **Description**: The `format` method has a switch statement that handles specific format strings.
- **Reasoning**: This `format` method uses a `switch` statement to handle predefined date format strings. Adding new formats would require modifying this `switch` statement, violating the Open/Closed Principle.

### OCP-108 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.format
- **Confidence**: Found in 1 scan(s)
- **Lines**: 7140–7194
- **Type**: method
- **Description**: The `format` method has a switch statement that handles specific format strings.
- **Reasoning**: This `format` method uses a `switch` statement to manage predefined date format strings. Extending it to support new formats requires modification of this `switch` statement, violating the Open/Closed Principle.

### OCP-109 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.format
- **Confidence**: Found in 1 scan(s)
- **Lines**: 7083–7137
- **Type**: method
- **Description**: The `format` method has a switch statement that handles specific format strings.
- **Reasoning**: This `format` method utilizes a `switch` statement to process predefined date format strings. Any extension to support new formats would necessitate modification of this `switch` statement, violating the Open/Closed Principle.

### OCP-110 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.format
- **Confidence**: Found in 1 scan(s)
- **Lines**: 6969–7022
- **Type**: method
- **Description**: The `format` method has a switch statement that handles specific format strings.
- **Reasoning**: This `format` method utilizes a `switch` statement to process predefined date format strings. Any extension to support new formats would necessitate modification of this `switch` statement, violating the Open/Closed Principle.

### OCP-111 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.format
- **Confidence**: Found in 1 scan(s)
- **Lines**: 6798–6851
- **Type**: method
- **Description**: The `format` method has a switch statement that handles specific format strings.
- **Reasoning**: This `format` method uses a `switch` statement to handle predefined date format strings. Adding new formats would require modifying this `switch` statement, violating the Open/Closed Principle.

### OCP-112 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.format
- **Confidence**: Found in 1 scan(s)
- **Lines**: 6741–6794
- **Type**: method
- **Description**: The `format` method has a switch statement that handles specific format strings.
- **Reasoning**: This `format` method utilizes a `switch` statement to process predefined date format strings. Any extension to support new formats would necessitate modification of this `switch` statement, violating the Open/Closed Principle.

### OCP-113 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.format
- **Confidence**: Found in 1 scan(s)
- **Lines**: 6684–6737
- **Type**: method
- **Description**: The `format` method has a switch statement that handles specific format strings.
- **Reasoning**: This `format` method uses a `switch` statement to handle predefined date format strings. Adding new formats would require modifying this `switch` statement, violating the Open/Closed Principle.

### OCP-117 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderJSONB.java — JSONReaderJSONB
- **Confidence**: Found in 1 scan(s)
- **Lines**: 25–6303
- **Type**: class
- **Description**: Class contains numerous `nextIfName4MatchX` and `nextIfValue4MatchX` methods, similar to UTF readers, indicating a large conditional structure for parsing JSONB tokens.
- **Reasoning**: The `JSONReaderJSONB` class also features a large set of `nextIfName4MatchX` and `nextIfValue4MatchX` methods. These are likely used to parse specific byte patterns representing JSONB tokens. The extensive use of such methods suggests a monolithic parsing logic that would need modification to support new JSONB types or variations, thus violating the Open/Closed Principle. The class is open for extension by adding more such methods, but this approach leads to a large, hard-to-maintain class.

### OCP-125 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/reader/ObjectReaderCreator.java — ObjectReaderCreator
- **Confidence**: Found in 1 scan(s)
- **Lines**: 101–4094
- **Type**: class
- **Description**: The abstract class defines methods for creating `ObjectReader` instances, with many create methods for different scenarios and types.
- **Reasoning**: As an abstract creator class, `ObjectReaderCreator` defines numerous abstract methods and concrete factory methods for creating `ObjectReader` instances. Methods like `createObjectReader`, `createFieldReaders`, `createFieldReader`, `createSupplier`, `createFunction`, `createEnumReader`, `createObjectReaderSeeAlso`, `createObjectReaderWithBuilder`, `createObjectReaderWithCreator`, and the extensive `FieldReader` creation methods (`FieldReaderInt32`, `FieldReaderLocalDate`, etc.) indicate a design where adding support for new types or complex bean structures might require adding new concrete implementations or extending the logic within these factory methods. The sheer number of specialized `createFieldReader` methods suggests that new field types might lead to modifications here.
