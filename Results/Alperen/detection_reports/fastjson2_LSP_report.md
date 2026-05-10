# LSP Violation Report: fastjson2

## Summary
- **Total unique issues**: 160
- **High severity**: 12
- **Medium severity**: 147
- **Low severity**: 1
- **Found by multiple scans**: 62/160

## Issues

### LSP-002 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseDate
- **Confidence**: Found in 3 scan(s)
- **Lines**: 170–238
- **Type**: method
- **Description**: The parseDate method has multiple overloaded versions and a complex switch statement that handles various date formats, potentially leading to inconsistent behavior or unexpected exceptions for unsupported formats.
- **Reasoning**: The `parseDate` method has several overloaded versions and a large switch statement that attempts to parse dates in various formats. This complexity can lead to LSP violations if a subclass were to override this method and not handle all the formats or if the parsing logic for a specific format is subtly different from what a caller might expect based on the base class contract. The default case that falls through to `DateTimeFormatter.ofPattern(format)` and then `LocalDateTime.parse` might also introduce unexpected behavior or exceptions if the `format` string is not a valid pattern or if the `str` is not compatible with `LocalDateTime` parsing, which could break the substitutability contract.

### LSP-006 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseMillis
- **Confidence**: Found in 3 scan(s)
- **Lines**: 282–290
- **Type**: method
- **Description**: The parseMillis method returns milliseconds since epoch, which is a primitive long. While primitive types are immutable, the interpretation of '0' as a null or invalid date might be inconsistent with other parsing methods.
- **Reasoning**: Similar to the other `parseMillis` overload, returning `0` for null input can be problematic. `0` milliseconds since epoch is a valid date. If the intention is to signal an invalid or null date, returning `null` or throwing an exception would be more aligned with LSP, as it avoids ambiguity and potential misinterpretation by the caller.

### LSP-009 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTime
- **Confidence**: Found in 3 scan(s)
- **Lines**: 408–434
- **Type**: method
- **Description**: The parseLocalDateTime method has a large switch statement based on the length of the input, which can lead to unexpected behavior or exceptions if a length is not handled correctly.
- **Reasoning**: The `parseLocalDateTime` method uses a large switch statement based on the length of the input character array. If a length is not explicitly handled or falls into the `default` case, it might lead to incorrect parsing or exceptions. This violates LSP because a subclass overriding this method might not handle all lengths or might have a different interpretation of the default case, breaking the substitutability contract. The `default` case also throws a `DateTimeParseException` which might not be expected by all callers.

### LSP-017 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDate9
- **Confidence**: Found in 3 scan(s)
- **Lines**: 1375–1429
- **Type**: method
- **Description**: The parseLocalDate9 method handles multiple date formats with complex conditional logic, increasing the risk of inconsistent parsing or errors.
- **Reasoning**: This method, like `parseLocalDate8`, handles a variety of date formats (`yyyy-MM-d`, `yyyy-M-dd`, `dd-MMM-yy`, etc.) using extensive conditional logic. The complexity increases the likelihood of errors or inconsistent parsing behavior, especially if subclasses do not perfectly replicate the parsing logic for all supported formats. The reliance on `DateUtils.month` also adds another layer of potential inconsistency.

### LSP-018 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDate10
- **Confidence**: Found in 3 scan(s)
- **Lines**: 1445–1478
- **Type**: method
- **Description**: The parseLocalDate10 method handles multiple date formats with complex conditional logic, increasing the risk of inconsistent parsing or errors.
- **Reasoning**: This method parses several date formats (`yyyy-MM-dd`, `yyyy/MM/dd`, `MM/dd/yyyy`, `dd.MM.yyyy`, etc.) using a complex series of `if-else if` statements. This intricate logic can be a source of LSP violations if subclasses do not maintain the same parsing behavior or if the base implementation has subtle bugs. The handling of different separators and date component orders makes it prone to errors.

### LSP-019 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDate10
- **Confidence**: Found in 3 scan(s)
- **Lines**: 1480–1513
- **Type**: method
- **Description**: The parseLocalDate10 method handles multiple date formats with complex conditional logic, increasing the risk of inconsistent parsing or errors.
- **Reasoning**: Similar to the `byte[]` overload, this `char[]` version of `parseLocalDate10` handles multiple date formats with complex conditional logic. The variety of formats and the reliance on character checks can lead to LSP violations if subclasses do not implement the parsing logic identically or if the base implementation has subtle errors.

### LSP-022 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTime12
- **Confidence**: Found in 3 scan(s)
- **Lines**: 1613–1639
- **Type**: method
- **Description**: The parseLocalDateTime12 method parses a specific format ('yyyyMMddHHmm') and has complex validation logic that could lead to unexpected behavior.
- **Reasoning**: This method parses a fixed format ('yyyyMMddHHmm') but includes checks for year, month, day, hour, and minute values. The validation logic (`(year | month | dom | hour | minute) < 0`) and the special handling for `year == 0 && month == 0 && dom == 0 && hour == 0 && minute == 0` returning `null` might not be universally expected behavior for date parsing, potentially violating LSP if subclasses handle these edge cases differently.

### LSP-023 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTime12
- **Confidence**: Found in 3 scan(s)
- **Lines**: 1655–1681
- **Type**: method
- **Description**: The parseLocalDateTime12 method parses a specific format ('yyyyMMddHHmm') and has complex validation logic that could lead to unexpected behavior.
- **Reasoning**: This `byte[]` overload of `parseLocalDateTime12` also parses a fixed format ('yyyyMMddHHmm') with complex validation. The checks for negative values and the special handling for all-zero values returning `null` might not be consistent with LSP if subclasses handle these cases differently or if the expected behavior for invalid inputs is not clearly defined.

### LSP-026 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTime16
- **Confidence**: Found in 3 scan(s)
- **Lines**: 1767–1819
- **Type**: method
- **Description**: The parseLocalDateTime16 method handles multiple date/time formats with complex conditional logic, increasing the risk of inconsistent parsing or errors.
- **Reasoning**: This method handles several date/time formats (`yyyy-MM-ddTHH:mm`, `yyyy-MM-dd HH:mm`, `yyyyMMddTHHmmssZ`, etc.) using a complex series of `if-else if` statements. The variety of formats and the intricate character checks make it prone to LSP violations if subclasses do not implement the parsing logic identically or if the base implementation has subtle bugs. The handling of different separators and the specific checks for 'T' or ' ' as date/time separators, along with 'Z' for UTC, add to the complexity.

### LSP-027 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTime16
- **Confidence**: Found in 3 scan(s)
- **Lines**: 1821–1884
- **Type**: method
- **Description**: The parseLocalDateTime16 method handles multiple date/time formats with complex conditional logic, increasing the risk of inconsistent parsing or errors.
- **Reasoning**: This `byte[]` overload of `parseLocalDateTime16` also handles multiple date/time formats with complex conditional logic. The extensive checks for character positions, separators, and specific byte sequences for different formats can lead to LSP violations if subclasses do not replicate this logic precisely or if the base implementation contains errors. The handling of Chinese and Korean characters for month/day names adds further complexity.

### LSP-029 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTime17
- **Confidence**: Found in 3 scan(s)
- **Lines**: 1965–2038
- **Type**: method
- **Description**: The parseLocalDateTime17 method handles multiple date/time formats with complex conditional logic, increasing the risk of inconsistent parsing or errors.
- **Reasoning**: This `byte[]` overload of `parseLocalDateTime17` handles multiple date/time formats with complex conditional logic. The extensive checks for character positions, separators, and specific byte sequences for different formats can lead to LSP violations if subclasses do not replicate this logic precisely or if the base implementation contains errors. The handling of different date/time separators and the specific checks for 'Z' for UTC can lead to unexpected behavior.

### LSP-030 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTime18
- **Confidence**: Found in 3 scan(s)
- **Lines**: 2054–2117
- **Type**: method
- **Description**: The parseLocalDateTime18 method handles multiple date/time formats with complex conditional logic, increasing the risk of inconsistent parsing or errors.
- **Reasoning**: This method parses several date/time formats (`yyyy-M-ddTHH:mm:ss`, `yyyy-M-dd HH:mm:ss`, etc.) using a complex series of `if-else if` statements. The variety of formats and the intricate character checks make it prone to LSP violations if subclasses do not implement the parsing logic identically or if the base implementation has subtle bugs. The handling of single vs. double digit months/days and different separators contributes to this complexity.

### LSP-031 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTime18
- **Confidence**: Found in 3 scan(s)
- **Lines**: 2119–2192
- **Type**: method
- **Description**: The parseLocalDateTime18 method handles multiple date/time formats with complex conditional logic, increasing the risk of inconsistent parsing or errors.
- **Reasoning**: This `byte[]` overload of `parseLocalDateTime18` handles multiple date/time formats with complex conditional logic. The extensive checks for character positions, separators, and specific byte sequences for different formats can lead to LSP violations if subclasses do not replicate this logic precisely or if the base implementation contains errors. The handling of single vs. double digit months/days and different separators contributes to this complexity.

### LSP-032 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTime19
- **Confidence**: Found in 3 scan(s)
- **Lines**: 2208–2241
- **Type**: method
- **Description**: The parseLocalDateTime19 method handles multiple date/time formats with complex conditional logic, increasing the risk of inconsistent parsing or errors.
- **Reasoning**: This method parses several date/time formats (`yyyy-MM-ddTHH:mm:ss`, `yyyy/MM/ddTHH:mm:ss`, etc.) using a complex series of `if-else if` statements. The variety of formats and the intricate character checks make it prone to LSP violations if subclasses do not implement the parsing logic identically or if the base implementation has subtle bugs. The handling of different separators ('-' or '/') and date/time separators (' ' or 'T') adds to the complexity.

### LSP-035 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTime20
- **Confidence**: Found in 3 scan(s)
- **Lines**: 2313–2339
- **Type**: method
- **Description**: The parseLocalDateTime20 method parses a specific format and has complex validation logic that could lead to unexpected behavior.
- **Reasoning**: This method parses a specific format and includes validation logic like `hour > 24 || minute > 59 || second > 60`. The use of `hour > 24` is incorrect for a 24-hour clock (it should be `hour >= 24`). This kind of subtle bug or specific validation that might not be universally expected can lead to LSP violations if subclasses do not replicate this potentially flawed logic or if callers rely on standard time validation.

### LSP-037 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTime26
- **Confidence**: Found in 3 scan(s)
- **Lines**: 2383–2410
- **Type**: method
- **Description**: The parseLocalDateTime26 method parses a specific format and has complex validation logic that could lead to unexpected behavior.
- **Reasoning**: This method parses a specific format and includes validation logic like `hour > 24 || minute > 59 || second > 60`. The check `hour > 24` is incorrect for a 24-hour clock. This kind of subtle bug or specific validation that might not be universally expected can lead to LSP violations if subclasses do not replicate this potentially flawed logic or if callers rely on standard time validation.

### LSP-038 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTime26
- **Confidence**: Found in 3 scan(s)
- **Lines**: 2412–2439
- **Type**: method
- **Description**: The parseLocalDateTime26 method parses a specific format and has complex validation logic that could lead to unexpected behavior.
- **Reasoning**: This `byte[]` overload of `parseLocalDateTime26` parses a specific format and includes validation logic like `hour > 24 || minute > 59 || second > 60`. The check `hour > 24` is incorrect for a 24-hour clock. This kind of subtle bug or specific validation that might not be universally expected can lead to LSP violations if subclasses do not replicate this potentially flawed logic or if callers rely on standard time validation.

### LSP-039 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTime27
- **Confidence**: Found in 3 scan(s)
- **Lines**: 2455–2482
- **Type**: method
- **Description**: The parseLocalDateTime27 method parses a specific format and has complex validation logic that could lead to unexpected behavior.
- **Reasoning**: This method parses a specific format and includes validation logic like `hour > 24 || minute > 59 || second > 60`. The check `hour > 24` is incorrect for a 24-hour clock. This kind of subtle bug or specific validation that might not be universally expected can lead to LSP violations if subclasses do not replicate this potentially flawed logic or if callers rely on standard time validation.

### LSP-044 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTime29
- **Confidence**: Found in 3 scan(s)
- **Lines**: 2628–2655
- **Type**: method
- **Description**: The parseLocalDateTime29 method parses a specific format and has complex validation logic that could lead to unexpected behavior.
- **Reasoning**: This `byte[]` overload of `parseLocalDateTime29` parses a specific format and includes validation logic like `hour > 24 || minute > 59 || second > 60`. The check `hour > 24` is incorrect for a 24-hour clock. This kind of subtle bug or specific validation that might not be universally expected can lead to LSP violations if subclasses do not replicate this potentially flawed logic or if callers rely on standard time validation.

### LSP-045 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTimeX
- **Confidence**: Found in 3 scan(s)
- **Lines**: 2671–2876
- **Type**: method
- **Description**: The parseLocalDateTimeX method handles a wide range of date/time formats with complex conditional logic, increasing the risk of inconsistent parsing or errors.
- **Reasoning**: This method handles a very broad range of date/time formats based on the length of the input and character checks. The extensive conditional logic and the use of `localDateTime` helper methods with many parameters make it highly complex and prone to LSP violations. If a subclass overrides this method, it would need to meticulously replicate all these parsing rules and validations, which is error-prone. The `localDateTime` helper itself also has validation checks that might not be universally expected.

### LSP-047 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseZonedDateTime16
- **Confidence**: Found in 3 scan(s)
- **Lines**: 3100–3154
- **Type**: method
- **Description**: The parseZonedDateTime16 method parses ISO Date with offset formats and relies on complex character checks and zone ID resolution, which can lead to inconsistent behavior.
- **Reasoning**: This method parses ISO Date with offset formats. The logic involves detailed character checks for separators ('-', '+', ':') and relies on `getZoneId` for zone resolution. This complexity increases the risk of LSP violations if subclasses do not handle these formats or zone resolutions identically. The direct throwing of `DateTimeParseException` for specific illegal inputs also indicates a potential for inconsistent error handling.

### LSP-001 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseDateYMDHMS19
- **Confidence**: Found in 2 scan(s)
- **Lines**: 144–148
- **Type**: method
- **Description**: Method parseDateYMDHMS19 returns a new Date object, which is mutable and can lead to unexpected behavior if modified after parsing.
- **Reasoning**: The Liskov Substitution Principle requires that subtypes be substitutable for their base types without altering the correctness of the program. While DateUtils.parseDateYMDHMS19 itself doesn't violate LSP directly, returning a mutable `java.util.Date` object from a utility method that is intended to parse and return a date representation can be problematic. If the caller modifies the returned `Date` object, it could lead to unexpected side effects in other parts of the program that might be using the same `Date` object or relying on its immutability. A more LSP-compliant approach would be to return an immutable date representation like `java.time.LocalDateTime` or `java.time.ZonedDateTime`.

### LSP-003 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseDate
- **Confidence**: Found in 2 scan(s)
- **Lines**: 240–244
- **Type**: method
- **Description**: The parseDate method returns a new Date object, which is mutable and can lead to unexpected behavior if modified after parsing.
- **Reasoning**: Similar to `parseDateYMDHMS19`, the `parseDate` method returns a mutable `java.util.Date` object. This violates the principle of substitutability if callers expect an immutable date object or if modifications to the returned `Date` object cause unintended side effects elsewhere in the program. Returning an immutable date type from `java.time` would be more robust.

### LSP-005 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseMillis
- **Confidence**: Found in 2 scan(s)
- **Lines**: 275–280
- **Type**: method
- **Description**: The parseMillis method returns milliseconds since epoch, which is a primitive long. While primitive types are immutable, the interpretation of '0' as a null or invalid date might be inconsistent with other parsing methods.
- **Reasoning**: The `parseMillis` method returns `0` if the input string is null. However, `0` milliseconds since epoch corresponds to January 1, 1970, 00:00:00 UTC. Returning `0` for a null input might be misleading and could be interpreted as a valid date by some callers, potentially violating the principle that subtypes (or in this case, return values representing states) should be substitutable without altering program correctness. A more explicit return value like `null` or throwing an exception for invalid/null input would be clearer.

### LSP-007 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTime
- **Confidence**: Found in 2 scan(s)
- **Lines**: 319–346
- **Type**: method
- **Description**: The parseLocalDateTime method has a complex conditional logic based on JVM version and internal flags, which can lead to inconsistent behavior across different environments.
- **Reasoning**: The `parseLocalDateTime` method contains conditional logic (`JVM_VERSION == 8 && !FIELD_STRING_VALUE_ERROR`) that might lead to different parsing behaviors depending on the JVM version and internal state. This violates LSP because a caller might expect consistent behavior regardless of the execution environment. If a subclass were to override this method, it might not be able to replicate this environment-specific behavior, breaking substitutability.

### LSP-008 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTime
- **Confidence**: Found in 2 scan(s)
- **Lines**: 348–367
- **Type**: method
- **Description**: The parseLocalDateTime method throws a DateTimeParseException for certain 'illegal input' strings, but also returns null for other specific 'illegal input' strings, creating inconsistent error handling.
- **Reasoning**: The method exhibits inconsistent error handling. For some invalid inputs (e.g., "null", "00000000"), it returns `null`. However, for other invalid inputs (e.g., "illegal input " + input), it throws a `DateTimeParseException`. This inconsistency violates LSP because a caller cannot reliably predict whether to expect a `null` return or an exception for invalid date strings. A consistent error handling strategy (e.g., always throwing an exception for invalid input) would be more robust.

### LSP-011 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDate
- **Confidence**: Found in 2 scan(s)
- **Lines**: 978–997
- **Type**: method
- **Description**: The parseLocalDate method has inconsistent error handling, returning null for some invalid inputs and throwing DateTimeParseException for others.
- **Reasoning**: The `parseLocalDate` method exhibits inconsistent error handling. It returns `null` for specific empty or zero-value date strings but throws `DateTimeParseException` for other invalid inputs. This violates LSP as callers cannot reliably predict the outcome of parsing an invalid date string. A consistent approach, such as always throwing an exception for invalid formats, would be more predictable and adhere better to LSP.

### LSP-012 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDate
- **Confidence**: Found in 2 scan(s)
- **Lines**: 1013–1032
- **Type**: method
- **Description**: The parseLocalDate method has inconsistent error handling, returning null for some invalid inputs and throwing DateTimeParseException for others.
- **Reasoning**: This overload of `parseLocalDate` also demonstrates inconsistent error handling. It returns `null` for specific invalid inputs (like "null" or "00000000") but throws `DateTimeParseException` for others. This inconsistency breaks the LSP, as callers cannot rely on a uniform way to handle invalid date formats.

### LSP-013 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDate
- **Confidence**: Found in 2 scan(s)
- **Lines**: 1048–1067
- **Type**: method
- **Description**: The parseLocalDate method has inconsistent error handling, returning null for some invalid inputs and throwing DateTimeParseException for others.
- **Reasoning**: This `char[]` overload of `parseLocalDate` also exhibits inconsistent error handling by returning `null` for certain invalid inputs while throwing `DateTimeParseException` for others. This violates LSP because the contract for handling invalid input is not uniform, making it difficult for subclasses or callers to substitute and expect consistent behavior.

### LSP-014 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseMillis
- **Confidence**: Found in 2 scan(s)
- **Lines**: 1128–1178
- **Type**: method
- **Description**: The parseMillis method contains complex conditional logic for parsing various date formats, including specific handling for numeric inputs and ISO 8601 formats, which can lead to unexpected behavior if not all cases are correctly handled or if the logic is not consistent.
- **Reasoning**: The `parseMillis` method attempts to parse dates from various formats, including numeric representations and ISO 8601. The logic for handling numeric inputs (e.g., `len == 8 && millis >= 19700101 && millis <= 21000101`) and the subsequent date validation might not cover all edge cases or might have subtle differences in interpretation compared to standard date parsing. This can lead to LSP violations if a subclass overrides this method and handles these cases differently, or if the base implementation itself has subtle bugs that break the expected contract.

### LSP-016 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDate8
- **Confidence**: Found in 2 scan(s)
- **Lines**: 1326–1359
- **Type**: method
- **Description**: The parseLocalDate8 method handles multiple date formats (yyyy-m-d, yyyyMMdd, d-MMM-yy) with complex conditional logic, which can lead to inconsistent parsing or errors.
- **Reasoning**: This method attempts to parse dates from several different formats using a series of `if-else if` conditions. The logic for determining the correct format and extracting year, month, and day is complex. If a subclass were to override this method, it might not correctly handle all these formats or might introduce subtle differences in parsing, violating LSP. The `d-MMM-yy` format parsing, in particular, relies on a `DateUtils.month` helper which could also be a source of inconsistency.

### LSP-020 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDate11
- **Confidence**: Found in 2 scan(s)
- **Lines**: 1529–1555
- **Type**: method
- **Description**: The parseLocalDate11 method handles multiple date formats with complex conditional logic, increasing the risk of inconsistent parsing or errors.
- **Reasoning**: This method parses specific date formats like `yyyy年MM月dd日` and `yyyy년MM월dd일`. The logic relies on checking specific character positions and values. This complexity can lead to LSP violations if subclasses do not correctly parse these formats or if the base implementation has subtle bugs. The handling of different character sets for year/month/day separators is also a potential source of inconsistency.

### LSP-021 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDate11
- **Confidence**: Found in 2 scan(s)
- **Lines**: 1571–1597
- **Type**: method
- **Description**: The parseLocalDate11 method handles multiple date formats with complex conditional logic, increasing the risk of inconsistent parsing or errors.
- **Reasoning**: This `byte[]` overload of `parseLocalDate11` also handles multiple date formats with complex conditional logic. The reliance on specific byte values and positions for parsing can lead to LSP violations if subclasses do not implement the parsing logic identically or if the base implementation has subtle errors.

### LSP-024 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTime14
- **Confidence**: Found in 2 scan(s)
- **Lines**: 1697–1723
- **Type**: method
- **Description**: The parseLocalDateTime14 method parses a specific format ('yyyyMMddHHmmss') and has complex validation logic that could lead to unexpected behavior.
- **Reasoning**: This method parses the 'yyyyMMddHHmmss' format. The validation logic `(year | month | dom | hour | minute | second) < 0` is used to check for invalid values. If a subclass were to override this and not perform the same validation or handle negative results differently, it could lead to LSP violations. The implicit assumption that all negative results from these checks indicate an invalid date might also be problematic.

### LSP-028 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTime17
- **Confidence**: Found in 2 scan(s)
- **Lines**: 1900–1963
- **Type**: method
- **Description**: The parseLocalDateTime17 method handles multiple date/time formats with complex conditional logic, increasing the risk of inconsistent parsing or errors.
- **Reasoning**: This method handles several date/time formats (`yyyy-MM-ddTHH:mmZ`, `yyyy-MM-dd HH:mmZ`, etc.) using a complex series of `if-else if` statements. The variety of formats, including those with 'Z' for UTC and different month/day representations, makes it prone to LSP violations if subclasses do not implement the parsing logic identically or if the base implementation has subtle bugs. The handling of different date/time separators and the specific checks for 'Z' can lead to unexpected behavior.

### LSP-033 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTime19
- **Confidence**: Found in 2 scan(s)
- **Lines**: 2243–2262
- **Type**: method
- **Description**: The parseLocalDateTime19 method relies on internal JVM version checks and potential field errors, which can lead to inconsistent behavior.
- **Reasoning**: This overload of `parseLocalDateTime19` relies on internal JVM version checks and potential field errors (`JVM_VERSION == 8 && !FIELD_STRING_VALUE_ERROR`). This dependency on the execution environment can lead to inconsistent behavior, violating LSP. If a subclass overrides this method, it might not be able to replicate this environment-specific behavior, breaking substitutability.

### LSP-034 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTime19
- **Confidence**: Found in 2 scan(s)
- **Lines**: 2264–2297
- **Type**: method
- **Description**: The parseLocalDateTime19 method handles multiple date/time formats with complex conditional logic, increasing the risk of inconsistent parsing or errors.
- **Reasoning**: This `byte[]` overload of `parseLocalDateTime19` handles multiple date/time formats with complex conditional logic. The extensive checks for character positions, separators, and specific byte sequences for different formats can lead to LSP violations if subclasses do not replicate this logic precisely or if the base implementation contains errors. The handling of different date/time separators and the specific checks for 'T' or ' ' contribute to this complexity.

### LSP-036 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTime20
- **Confidence**: Found in 2 scan(s)
- **Lines**: 2341–2367
- **Type**: method
- **Description**: The parseLocalDateTime20 method parses a specific format and has complex validation logic that could lead to unexpected behavior.
- **Reasoning**: This `byte[]` overload of `parseLocalDateTime20` parses a specific format and includes validation logic like `hour > 24 || minute > 59 || second > 60`. The check `hour > 24` is incorrect for a 24-hour clock. This kind of subtle bug or specific validation that might not be universally expected can lead to LSP violations if subclasses do not replicate this potentially flawed logic or if callers rely on standard time validation.

### LSP-040 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTime27
- **Confidence**: Found in 2 scan(s)
- **Lines**: 2484–2511
- **Type**: method
- **Description**: The parseLocalDateTime27 method parses a specific format and has complex validation logic that could lead to unexpected behavior.
- **Reasoning**: This `byte[]` overload of `parseLocalDateTime27` parses a specific format and includes validation logic like `hour > 24 || minute > 59 || second > 60`. The check `hour > 24` is incorrect for a 24-hour clock. This kind of subtle bug or specific validation that might not be universally expected can lead to LSP violations if subclasses do not replicate this potentially flawed logic or if callers rely on standard time validation.

### LSP-041 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTime28
- **Confidence**: Found in 2 scan(s)
- **Lines**: 2527–2554
- **Type**: method
- **Description**: The parseLocalDateTime28 method parses a specific format and has complex validation logic that could lead to unexpected behavior.
- **Reasoning**: This method parses a specific format and includes validation logic like `hour > 24 || minute > 59 || second > 60`. The check `hour > 24` is incorrect for a 24-hour clock. This kind of subtle bug or specific validation that might not be universally expected can lead to LSP violations if subclasses do not replicate this potentially flawed logic or if callers rely on standard time validation.

### LSP-043 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTime29
- **Confidence**: Found in 2 scan(s)
- **Lines**: 2599–2626
- **Type**: method
- **Description**: The parseLocalDateTime29 method parses a specific format and has complex validation logic that could lead to unexpected behavior.
- **Reasoning**: This method parses a specific format and includes validation logic like `hour > 24 || minute > 59 || second > 60`. The check `hour > 24` is incorrect for a 24-hour clock. This kind of subtle bug or specific validation that might not be universally expected can lead to LSP violations if subclasses do not replicate this potentially flawed logic or if callers rely on standard time validation.

### LSP-046 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTimeX
- **Confidence**: Found in 2 scan(s)
- **Lines**: 2878–3083
- **Type**: method
- **Description**: The parseLocalDateTimeX method handles a wide range of date/time formats with complex conditional logic, increasing the risk of inconsistent parsing or errors.
- **Reasoning**: This `byte[]` overload of `parseLocalDateTimeX` handles a very broad range of date/time formats with complex conditional logic. The extensive checks for character positions, separators, and the reliance on helper methods with many parameters increase the risk of LSP violations. If a subclass overrides this method, it must perfectly replicate the parsing logic for all supported formats, which is difficult and error-prone.

### LSP-049 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseZonedDateTime
- **Confidence**: Found in 2 scan(s)
- **Lines**: 3226–3230
- **Type**: method
- **Description**: The parseZonedDateTime method returns a ZonedDateTime object, which is mutable, potentially leading to unexpected behavior if modified.
- **Reasoning**: The `parseZonedDateTime` method returns a `ZonedDateTime` object. While `ZonedDateTime` itself is immutable, the method's contract might be violated if callers expect a specific behavior related to time zones or immutability that is not fully guaranteed or if the parsing logic itself has subtle issues. Returning an immutable and clearly defined type is generally preferred.

### LSP-051 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseZonedDateTime
- **Confidence**: Found in 2 scan(s)
- **Lines**: 3277–3296
- **Type**: method
- **Description**: The parseZonedDateTime method has inconsistent error handling, returning null for some invalid inputs and throwing DateTimeParseException for others.
- **Reasoning**: This `byte[]` overload of `parseZonedDateTime` exhibits inconsistent error handling. It returns `null` for specific inputs like "null", "0", or "0000-00-00", but throws `DateTimeParseException` for other invalid inputs. This violates LSP because callers cannot rely on a uniform way to handle invalid date strings.

### LSP-054 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseZonedDateTime
- **Confidence**: Found in 2 scan(s)
- **Lines**: 3375–3579
- **Type**: method
- **Description**: The parseZonedDateTime method handles a wide range of date/time formats with complex conditional logic, increasing the risk of inconsistent parsing or errors.
- **Reasoning**: This `char[]` overload of `parseZonedDateTime` handles a very broad range of date/time formats with complex conditional logic. The extensive checks for character positions, separators, time zone representations, and the reliance on helper methods with many parameters increase the risk of LSP violations. Subclasses must perfectly replicate this logic, which is difficult and error-prone. The handling of various date formats, including those with AM/PM and different separators, adds significant complexity.

### LSP-055 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.getZoneId
- **Confidence**: Found in 2 scan(s)
- **Lines**: 3601–3629
- **Type**: method
- **Description**: The getZoneId method uses a switch statement with hardcoded zone IDs and relies on ZoneId.of for others, which can lead to inconsistent behavior or exceptions for unrecognized zone IDs.
- **Reasoning**: The `getZoneId` method has a switch statement that handles specific hardcoded zone IDs ('000', '+08:00', 'CST') and then falls back to `ZoneId.of(zoneIdStr)`. This approach can lead to LSP violations if a subclass expects different handling for these specific IDs or if `ZoneId.of` throws an exception for an unrecognized zone ID that the base class does not handle consistently. The parsing of bracketed zone IDs (`[zoneId]`) is also a specific implementation detail that might not be universally expected.

### LSP-073 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalTime5
- **Confidence**: Found in 2 scan(s)
- **Lines**: 450–465
- **Type**: method
- **Description**: The parseLocalTime5(byte[] str, int off) method returns null for certain invalid inputs, which might not be the expected behavior for a method that parses time.
- **Reasoning**: The `parseLocalTime5(byte[] str, int off)` method returns `null` if the input format is not recognized or if the length is insufficient. While returning null is a valid way to indicate failure, if the base contract implies that parsing should either succeed or throw a specific exception (like `DateTimeParseException`), returning `null` could violate LSP. Callers might not be prepared to handle `null` if the base class contract doesn't specify it.

### LSP-075 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalTime6
- **Confidence**: Found in 2 scan(s)
- **Lines**: 507–524
- **Type**: method
- **Description**: The parseLocalTime6(byte[] str, int off) method returns null for unrecognized formats, potentially violating LSP if the base contract expects exceptions.
- **Reasoning**: This method returns `null` for invalid or unrecognized time formats. If the superclass or base contract implies that parsing errors should result in exceptions rather than null returns, this violates LSP. Callers might not be prepared to handle `null` if the base class doesn't specify this return value for errors.

### LSP-079 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalTime8
- **Confidence**: Found in 2 scan(s)
- **Lines**: 625–630
- **Type**: method
- **Description**: The parseLocalTime8(byte[] bytes, int off) method returns null for invalid inputs, which might violate LSP if exceptions are expected.
- **Reasoning**: Returning `null` from `parseLocalTime8(byte[] bytes, int off)` for invalid inputs can break LSP if the base contract implies throwing an exception. This can lead to unexpected `NullPointerException`s if callers are not prepared for `null` returns.

### LSP-081 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTime
- **Confidence**: Found in 2 scan(s)
- **Lines**: 837–879
- **Type**: method
- **Description**: The parseLocalDateTime(byte[] str, int off, int len) method has a large switch statement based on length and throws DateTimeParseException, which might violate LSP.
- **Reasoning**: This method uses a switch statement on `len` to parse dates. The large number of cases and reliance on internal helper methods make it specific. If a subclass were to override this method expecting a different set of supported lengths or a different error-handling strategy (e.g., returning null instead of throwing `DateTimeParseException`), it would violate LSP. The explicit throwing of `DateTimeParseException` might also be a violation if the base contract implies a different exception type or error handling.

### LSP-083 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDate
- **Confidence**: Found in 2 scan(s)
- **Lines**: 926–959
- **Type**: method
- **Description**: The parseLocalDate(byte[] str, int off, int len) method has a switch statement based on length and throws DateTimeParseException, potentially violating LSP.
- **Reasoning**: This method uses a switch statement on `len` to parse dates and throws `DateTimeParseException` for invalid inputs or lengths. This specific implementation might not be substitutable for a base contract that expects a different behavior for invalid formats (e.g., returning null or a different exception). The reliance on specific lengths also makes it less flexible.

### LSP-125 [LOW] core/src/main/java/com/alibaba/fastjson2/JSONReader.java — JSONReader.nextIfName4Match2
- **Confidence**: Found in 2 scan(s)
- **Lines**: 345–345
- **Type**: method
- **Description**: Abstract method 'nextIfName4Match2' is not implemented by all concrete subclasses.
- **Reasoning**: The method 'nextIfName4Match2' is declared as abstract in the base class 'JSONReader'. However, the provided skeleton does not show any concrete subclasses implementing this method. If a subclass does not implement this method, it violates LSP because a client expecting an implementation would encounter a runtime error or unexpected behavior.

### LSP-126 [HIGH] core/src/main/java/com/alibaba/fastjson2/JSONReaderJSONB.java — JSONReaderJSONB.nextIfMatch(char)
- **Confidence**: Found in 2 scan(s)
- **Lines**: 260–261
- **Type**: method
- **Description**: Subtype JSONReaderJSONB throws UnsupportedOperationException for an abstract method defined in its base type JSONReader.
- **Reasoning**: The JSONReader base class defines `nextIfMatch(char ch)` as an abstract method, implying that all concrete subclasses should provide a meaningful implementation. JSONReaderJSONB, being a binary reader, throws `JSONException("UnsupportedOperation")` for this method. This directly violates LSP because a client expecting a JSONReader should be able to call `nextIfMatch(char ch)` without encountering an UnsupportedOperationException, as it breaks the expected contract of the base type.

### LSP-127 [HIGH] core/src/main/java/com/alibaba/fastjson2/JSONReaderJSONB.java — JSONReaderJSONB.nextIfArrayStart()
- **Confidence**: Found in 2 scan(s)
- **Lines**: 265–266
- **Type**: method
- **Description**: Subtype JSONReaderJSONB throws UnsupportedOperationException for an abstract method defined in its base type JSONReader.
- **Reasoning**: Similar to `nextIfMatch`, `nextIfArrayStart()` is an abstract method in JSONReader. JSONReaderJSONB throws `JSONException("UnsupportedOperation")`, indicating it cannot fulfill the contract. This violates LSP as a subtype should be substitutable for its base type without altering correctness.

### LSP-128 [HIGH] core/src/main/java/com/alibaba/fastjson2/JSONReaderJSONB.java — JSONReaderJSONB.nextIfComma()
- **Confidence**: Found in 2 scan(s)
- **Lines**: 270–271
- **Type**: method
- **Description**: Subtype JSONReaderJSONB throws UnsupportedOperationException for an abstract method defined in its base type JSONReader.
- **Reasoning**: Similar to `nextIfMatch`, `nextIfComma()` is an abstract method in JSONReader. JSONReaderJSONB throws `JSONException("UnsupportedOperation")`, indicating it cannot fulfill the contract. This violates LSP as a subtype should be substitutable for its base type without altering correctness.

### LSP-129 [HIGH] core/src/main/java/com/alibaba/fastjson2/JSONReaderJSONB.java — JSONReaderJSONB.nextIfArrayEnd()
- **Confidence**: Found in 2 scan(s)
- **Lines**: 275–276
- **Type**: method
- **Description**: Subtype JSONReaderJSONB throws UnsupportedOperationException for an abstract method defined in its base type JSONReader.
- **Reasoning**: Similar to `nextIfMatch`, `nextIfArrayEnd()` is an abstract method in JSONReader. JSONReaderJSONB throws `JSONException("UnsupportedOperation")`, indicating it cannot fulfill the contract. This violates LSP as a subtype should be substitutable for its base type without altering correctness.

### LSP-130 [HIGH] core/src/main/java/com/alibaba/fastjson2/JSONReaderJSONB.java — JSONReaderJSONB.readNullOrNewDate()
- **Confidence**: Found in 2 scan(s)
- **Lines**: 1646–1647
- **Type**: method
- **Description**: Subtype JSONReaderJSONB throws UnsupportedOperationException for an abstract method defined in its base type JSONReader.
- **Reasoning**: The abstract method `readNullOrNewDate()` in JSONReader implies that all concrete readers should be able to read a date or null. JSONReaderJSONB throws `JSONException("UnsupportedOperation")`, indicating it cannot provide a meaningful implementation for this part of the contract, violating LSP.

### LSP-131 [HIGH] core/src/main/java/com/alibaba/fastjson2/JSONReaderJSONB.java — JSONReaderJSONB.skipComment()
- **Confidence**: Found in 2 scan(s)
- **Lines**: 4825–4826
- **Type**: method
- **Description**: Subtype JSONReaderJSONB throws UnsupportedOperationException for an abstract method defined in its base type JSONReader.
- **Reasoning**: The abstract method `skipComment()` in JSONReader implies comment skipping functionality. JSONReaderJSONB throws `JSONException("UnsupportedOperation")`, indicating it cannot fulfill this contract, which violates LSP. If comments are not applicable to JSONB, the base interface should not mandate this method for all subtypes.

### LSP-133 [HIGH] core/src/main/java/com/alibaba/fastjson2/JSONReaderJSONB.java — JSONReaderJSONB.readPattern()
- **Confidence**: Found in 2 scan(s)
- **Lines**: 5562–5563
- **Type**: method
- **Description**: Subtype JSONReaderJSONB throws UnsupportedOperationException for an abstract method defined in its base type JSONReader.
- **Reasoning**: The abstract method `readPattern()` in JSONReader implies pattern reading functionality. JSONReaderJSONB throws `JSONException("UnsupportedOperation")`, indicating it cannot fulfill this contract, which violates LSP. This suggests the method is not universally applicable across all JSONReader subtypes.

### LSP-134 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderJSONB.java — JSONReaderJSONB.readLocalDate8()
- **Confidence**: Found in 2 scan(s)
- **Lines**: 5340–5345
- **Type**: method
- **Description**: Subtype JSONReaderJSONB alters the contract by throwing an exception indicating a specific input format requirement ('date only support string input') for a general date parsing method.
- **Reasoning**: The abstract method `readLocalDate8()` in JSONReader implies a general capability to read a date. However, JSONReaderJSONB throws `JSONException("date only support string input")`. This alters the expected contract: a client using a JSONReader should expect to read a date regardless of its internal representation (binary or string), not be constrained by the subtype's internal parsing logic. This changes the post-condition and violates LSP.

### LSP-135 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderJSONB.java — JSONReaderJSONB.readLocalDateTime12()
- **Confidence**: Found in 2 scan(s)
- **Lines**: 4735–4740
- **Type**: method
- **Description**: Subtype JSONReaderJSONB alters the contract by throwing an exception indicating a specific input format requirement ('date only support string input') for a general datetime parsing method.
- **Reasoning**: Similar to `readLocalDate8()`, the `readLocalDateTime12()` method in JSONReaderJSONB throws `JSONException("date only support string input")`. This changes the expected behavior of a general datetime parsing method, implying a textual representation constraint that is not part of the abstract base class's contract. This violates LSP.

### LSP-136 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderJSONB.java — JSONReaderJSONB.readLocalTime10()
- **Confidence**: Found in 2 scan(s)
- **Lines**: 4783–4788
- **Type**: method
- **Description**: Subtype JSONReaderJSONB alters the contract by throwing an exception indicating a specific input format requirement ('date only support string input') for a general time parsing method.
- **Reasoning**: Similar to other date/time parsing methods, `readLocalTime10()` in JSONReaderJSONB throws `JSONException("date only support string input")`. This alters the expected contract by imposing a textual representation requirement for a method that should abstractly read a time value, violating LSP.

### LSP-004 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseDate
- **Confidence**: Found in 1 scan(s)
- **Lines**: 246–250
- **Type**: method
- **Description**: The parseDate method returns a new Date object, which is mutable and can lead to unexpected behavior if modified after parsing.
- **Reasoning**: The `parseDate(String str, ZoneId zoneId)` method, like other `parseDate` overloads, returns a mutable `java.util.Date`. This can lead to LSP violations if the caller modifies the returned object, potentially breaking the contract expected by the base type or other parts of the system that rely on the state of the `Date` object.

### LSP-010 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTime
- **Confidence**: Found in 1 scan(s)
- **Lines**: 776–802
- **Type**: method
- **Description**: The parseLocalDateTime method has a large switch statement based on the length of the input, which can lead to unexpected behavior or exceptions if a length is not handled correctly.
- **Reasoning**: Similar to the `char[]` overload, this `byte[]` version of `parseLocalDateTime` relies on a large switch statement based on input length. Unhandled lengths or incorrect parsing in the `default` case can lead to `DateTimeParseException` or `null` returns, violating LSP if subclasses do not maintain this behavior or if callers expect a consistent outcome.

### LSP-015 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseMillis
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1180–1199
- **Type**: method
- **Description**: The parseMillis method contains complex conditional logic for parsing various date formats, including specific handling for numeric inputs and ISO 8601 formats, which can lead to unexpected behavior if not all cases are correctly handled or if the logic is not consistent.
- **Reasoning**: Similar to the `byte[]` overload, this `char[]` version of `parseMillis` also has complex logic for parsing different date formats. The handling of numeric inputs and the fallback to `DateUtils.parseLocalDateTime` can lead to inconsistencies or unexpected exceptions, potentially violating LSP if a subclass does not replicate this behavior or if the parsing logic itself is flawed.

### LSP-025 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTime14
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1725–1751
- **Type**: method
- **Description**: The parseLocalDateTime14 method parses a specific format ('yyyyMMddHHmmss') and has complex validation logic that could lead to unexpected behavior.
- **Reasoning**: This `byte[]` overload of `parseLocalDateTime14` parses the 'yyyyMMddHHmmss' format. The validation `(year | month | dom | hour | minute | second) < 0` is used. If a subclass overrides this method and does not apply the same validation or handles invalid values differently, it would violate LSP. The check for negative results from these bitwise OR operations is a specific implementation detail that might not be universally understood or expected.

### LSP-042 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTime28
- **Confidence**: Found in 1 scan(s)
- **Lines**: 2556–2583
- **Type**: method
- **Description**: The parseLocalDateTime28 method parses a specific format and has complex validation logic that could lead to unexpected behavior.
- **Reasoning**: This `byte[]` overload of `parseLocalDateTime28` parses a specific format and includes validation logic like `hour > 24 || minute > 59 || second > 60`. The check `hour > 24` is incorrect for a 24-hour clock. This kind of subtle bug or specific validation that might not be universally expected can lead to LSP violations if subclasses do not replicate this potentially flawed logic or if callers rely on standard time validation.

### LSP-048 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseZonedDateTime16
- **Confidence**: Found in 1 scan(s)
- **Lines**: 3156–3210
- **Type**: method
- **Description**: The parseZonedDateTime16 method parses ISO Date with offset formats and relies on complex character checks and zone ID resolution, which can lead to inconsistent behavior.
- **Reasoning**: This `byte[]` overload of `parseZonedDateTime16` parses ISO Date with offset formats. The detailed checks for byte values, separators, and the reliance on `getZoneId` for zone resolution introduce complexity that can lead to LSP violations. If subclasses do not replicate this logic precisely, or if the base implementation has subtle bugs, substitutability can be broken.

### LSP-050 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseZonedDateTime
- **Confidence**: Found in 1 scan(s)
- **Lines**: 3232–3261
- **Type**: method
- **Description**: The parseZonedDateTime method has complex logic involving JVM version checks and internal flags, potentially leading to inconsistent behavior.
- **Reasoning**: This overload of `parseZonedDateTime` uses internal JVM version checks and flags (`JVM_VERSION == 8 && !FIELD_STRING_VALUE_ERROR`). This dependency on the execution environment can lead to inconsistent behavior across different JVMs or configurations, violating LSP. Subclasses might not be able to replicate this environment-specific behavior.

### LSP-052 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseZonedDateTime
- **Confidence**: Found in 1 scan(s)
- **Lines**: 3298–3317
- **Type**: method
- **Description**: The parseZonedDateTime method has inconsistent error handling, returning null for some invalid inputs and throwing DateTimeParseException for others.
- **Reasoning**: This `char[]` overload of `parseZonedDateTime` also exhibits inconsistent error handling. It returns `null` for specific invalid inputs but throws `DateTimeParseException` for others. This violates LSP as callers cannot predict whether to expect a `null` return or an exception for invalid date strings.

### LSP-053 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseZonedDateTime
- **Confidence**: Found in 1 scan(s)
- **Lines**: 3319–3373
- **Type**: method
- **Description**: The parseZonedDateTime method handles a wide range of date/time formats with complex conditional logic, increasing the risk of inconsistent parsing or errors.
- **Reasoning**: This method handles a wide variety of date/time formats, including ISO-like formats with offsets and various string representations of time zones. The extensive conditional logic, including checks for JVM version and specific string patterns, makes it complex and prone to LSP violations. Subclasses might struggle to replicate this behavior consistently, especially with the nuanced handling of time zones and escape characters.

### LSP-056 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseMillisYMDHMS19
- **Confidence**: Found in 1 scan(s)
- **Lines**: 3645–3887
- **Type**: method
- **Description**: The parseMillisYMDHMS19 method handles multiple date/time formats with complex conditional logic and direct character/byte checks, increasing the risk of inconsistent parsing or errors.
- **Reasoning**: This method parses date-time strings in the 'yyyy-MM-dd HH:mm:ss' format and its variations ('yyyy-MM-ddTHH:mm:ss', 'yyyy/MM/dd HH:mm:ss', etc.). It uses extensive character and byte checks, along with complex conditional logic for different patterns. This complexity makes it prone to LSP violations if subclasses do not replicate the parsing logic precisely or if the base implementation contains subtle bugs. The direct calculation of `year`, `month`, `dom`, `hour`, `minute`, `second` based on character positions can be brittle.

### LSP-057 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseMillis19
- **Confidence**: Found in 1 scan(s)
- **Lines**: 3903–4145
- **Type**: method
- **Description**: The parseMillis19 method handles multiple date/time formats with complex conditional logic and direct character/byte checks, increasing the risk of inconsistent parsing or errors.
- **Reasoning**: This `byte[]` overload of `parseMillis19` handles multiple date/time formats with complex conditional logic. The extensive checks for character positions, separators, and the reliance on specific patterns (`DATE_TIME_FORMAT_19_DASH`, `DATE_TIME_FORMAT_19_DASH_T`, etc.) can lead to LSP violations if subclasses do not replicate this logic precisely or if the base implementation contains errors. The direct calculation of date and time components based on character positions is fragile.

### LSP-058 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseMillis10
- **Confidence**: Found in 1 scan(s)
- **Lines**: 4161–4205
- **Type**: method
- **Description**: The parseMillis10 method handles multiple date formats ('yyyy-MM-dd', 'yyyy/MM/dd') with complex conditional logic, increasing the risk of inconsistent parsing or errors.
- **Reasoning**: This method parses date formats like 'yyyy-MM-dd' and 'yyyy/MM/dd'. The logic relies on checking specific character positions and separators. This complexity can lead to LSP violations if subclasses do not correctly parse these formats or if the base implementation has subtle bugs. The handling of different separators ('-' or '/') increases the risk of errors.

### LSP-059 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseMillis10
- **Confidence**: Found in 1 scan(s)
- **Lines**: 4207–4251
- **Type**: method
- **Description**: The parseMillis10 method handles multiple date formats ('yyyy-MM-dd', 'yyyy/MM/dd') with complex conditional logic, increasing the risk of inconsistent parsing or errors.
- **Reasoning**: This `char[]` overload of `parseMillis10` handles date formats like 'yyyy-MM-dd' and 'yyyy/MM/dd' with complex conditional logic. The reliance on specific character positions and separators makes it prone to LSP violations if subclasses do not replicate the parsing logic precisely or if the base implementation contains errors.

### LSP-060 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.formatYMDHMS19
- **Confidence**: Found in 1 scan(s)
- **Lines**: 4659–4737
- **Type**: method
- **Description**: The formatYMDHMS19 method performs complex date calculations based on epoch second and zone offset, which might have subtle issues or inconsistencies.
- **Reasoning**: This method formats a `Date` object into 'yyyy-MM-dd HH:mm:ss' string. It involves complex calculations for epoch second, zone offset, and then deriving year, month, day, hour, minute, and second. The logic for calculating these components, especially the year and day of month based on `localEpochDay` and `secsOfDay`, is intricate and could be a source of LSP violations if subclasses do not replicate it accurately or if there are edge cases not handled correctly.

### LSP-061 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.formatYMD8
- **Confidence**: Found in 1 scan(s)
- **Lines**: 4753–4772
- **Type**: method
- **Description**: The formatYMD8 method returns a mutable Date object, which can lead to unexpected behavior if modified.
- **Reasoning**: The `formatYMD8` method, when called with a `Date` object, implicitly uses `date.getTime()`. While the method itself doesn't return a `Date` object, the underlying `Date` object passed to it is mutable. If the caller modifies the `Date` object after passing it to this method, it could lead to unexpected behavior, potentially violating LSP if the formatting logic relies on the `Date` object's state remaining constant.

### LSP-062 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.formatYMD8
- **Confidence**: Found in 1 scan(s)
- **Lines**: 4774–4805
- **Type**: method
- **Description**: The formatYMD8 method performs complex date calculations based on epoch second and zone offset, which might have subtle issues or inconsistencies.
- **Reasoning**: This method formats a timestamp into 'yyyyMMdd' string. It involves complex calculations for epoch second, zone offset, and then deriving year, month, and day. The logic for calculating these components, especially the year and day of month based on `localEpochDay`, is intricate and could be a source of LSP violations if subclasses do not replicate it accurately or if there are edge cases not handled correctly. The caching mechanism also adds a layer of complexity.

### LSP-063 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.formatYMD10
- **Confidence**: Found in 1 scan(s)
- **Lines**: 4877–4896
- **Type**: method
- **Description**: The formatYMD10 method returns a string representation of a LocalDate, but the underlying parsing logic for various formats might be inconsistent.
- **Reasoning**: The `formatYMD10` method formats year, month, and day into a string. While the formatting itself is straightforward, the underlying parsing methods (`parseLocalDate8`, `parseLocalDate9`, etc.) that this class relies on have complex and potentially inconsistent logic. If a subclass were to override `formatYMD10` and implicitly rely on these parsing methods for some internal validation or behavior, it could lead to LSP violations.

### LSP-064 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.formatYMD10
- **Confidence**: Found in 1 scan(s)
- **Lines**: 4898–4917
- **Type**: method
- **Description**: The formatYMD10 method returns a string representation of a LocalDate, but the underlying parsing logic for various formats might be inconsistent.
- **Reasoning**: Similar to the overload taking `int` parameters, this `formatYMD10` overload taking `LocalDate` might implicitly rely on the complex and potentially inconsistent parsing logic of other `parseLocalDate` methods within the class. If a subclass overrides this method and its behavior is influenced by these underlying parsing methods, it could lead to LSP violations.

### LSP-065 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.formatYMD10
- **Confidence**: Found in 1 scan(s)
- **Lines**: 4919–4938
- **Type**: method
- **Description**: The formatYMD10 method returns a string representation of a Date, but the underlying parsing logic for various formats might be inconsistent.
- **Reasoning**: This overload of `formatYMD10` takes a `Date` object. The method uses `date.getTime()` and then formats it based on `DEFAULT_ZONE_ID`. The potential LSP violations stem from the same complex and potentially inconsistent date parsing logic used elsewhere in the class, which might indirectly affect the formatting if the `Date` object's interpretation is influenced by these parsing methods.

### LSP-066 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.formatYMD8
- **Confidence**: Found in 1 scan(s)
- **Lines**: 4940–4977
- **Type**: method
- **Description**: The formatYMD8 method performs complex date calculations based on epoch second and zone offset, which might have subtle issues or inconsistencies.
- **Reasoning**: This method formats a `LocalDate` into a 'yyyyMMdd' string. It involves complex calculations for year, month, and day based on `localEpochDay`. The logic for deriving these components is intricate and could lead to LSP violations if subclasses do not replicate it accurately or if there are edge cases not handled correctly. The caching mechanism also adds complexity.

### LSP-067 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.formatYMD10
- **Confidence**: Found in 1 scan(s)
- **Lines**: 4979–5005
- **Type**: method
- **Description**: The formatYMD10 method formats a timestamp into a 'yyyy-MM-dd' string, but the underlying date calculations might have subtle issues or inconsistencies.
- **Reasoning**: This method formats a timestamp into a 'yyyy-MM-dd' string. It involves complex calculations for epoch second, zone offset, and then deriving year, month, and day. The logic for calculating these components, especially the year and day of month based on `localEpochDay`, is intricate and could be a source of LSP violations if subclasses do not replicate it accurately or if there are edge cases not handled correctly. The caching mechanism also adds complexity.

### LSP-068 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.format
- **Confidence**: Found in 1 scan(s)
- **Lines**: 5021–5041
- **Type**: method
- **Description**: The format method handles multiple date formats with complex conditional logic, increasing the risk of inconsistent parsing or errors.
- **Reasoning**: This method formats a `Date` object into a string based on a provided format pattern. It uses a switch statement for common patterns and falls back to `DateTimeFormatter.ofPattern(format)`. The switch statement handles several specific formats, and the fallback might lead to unexpected behavior or exceptions if the provided `format` string is not a valid pattern or if the `DateTimeFormatter` cannot parse it correctly. This can violate LSP if a subclass provides a different default behavior or if the fallback logic is not robust.

### LSP-069 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.formatYMDHMS19
- **Confidence**: Found in 1 scan(s)
- **Lines**: 4740–4751
- **Type**: method
- **Description**: The formatYMDHMS19 method returns a mutable Date object, which can lead to unexpected behavior if modified.
- **Reasoning**: The `formatYMDHMS19` method, when called with a `Date` object, implicitly uses `date.getTime()`. While the method itself doesn't return a `Date` object, the mutable nature of the input `Date` object can lead to LSP violations if the caller modifies it after passing it, potentially affecting the formatting logic or other parts of the system relying on the `Date` object's state.

### LSP-070 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseDateYMDHMS19
- **Confidence**: Found in 1 scan(s)
- **Lines**: 108–112
- **Type**: method
- **Description**: parseDateYMDHMS19 returns a new Date object, which might have different behavior than expected by a caller expecting a Date object created with a specific timezone.
- **Reasoning**: The method `parseDateYMDHMS19(String str)` calls `parseMillisYMDHMS19(str, DEFAULT_ZONE_ID)`. The `DEFAULT_ZONE_ID` is determined by `ZoneId.systemDefault()`. If a caller expects a `Date` object to be parsed using a specific timezone that is not the system default, this method violates LSP because the resulting `Date` object's interpretation (due to its internal millisecond representation) will be tied to the system's default timezone, not necessarily the timezone the caller might have intended or that a base type might imply.

### LSP-071 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseDate
- **Confidence**: Found in 1 scan(s)
- **Lines**: 127–131
- **Type**: method
- **Description**: parseDate(String str, String format) uses DEFAULT_ZONE_ID, which might not be the expected timezone for parsing.
- **Reasoning**: The method `parseDate(String str, String format)` defaults to using `DEFAULT_ZONE_ID` for parsing. If a caller passes a `format` string that implies a specific timezone or if the base `Date` type contract expects timezone awareness that differs from the system default, this method's behavior might not be substitutable. A more flexible design would allow specifying the ZoneId explicitly or inferring it from the format if possible.

### LSP-072 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTime
- **Confidence**: Found in 1 scan(s)
- **Lines**: 297–330
- **Type**: method
- **Description**: The parseLocalDateTime(String str, int off, int len) method has complex internal logic and throws DateTimeParseException, which might not be expected by a base contract.
- **Reasoning**: This method handles parsing based on string length and uses internal helper methods like `parseLocalDateTime(bytes, off, len)` or `parseLocalDateTime(chars, off, len)`. The extensive switch statement on `len` and the potential `DateTimeParseException` throw indicate a highly specific implementation. If a subclass were to override `parseLocalDateTime` expecting a different set of supported lengths or a different error handling strategy (e.g., returning null instead of throwing an exception for certain formats), it would violate LSP. The direct use of `JVM_VERSION` and `FIELD_STRING_VALUE_ERROR` also suggests implementation details that might not be substitutable.

### LSP-074 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalTime5
- **Confidence**: Found in 1 scan(s)
- **Lines**: 471–486
- **Type**: method
- **Description**: The parseLocalTime5(char[] str, int off) method returns null for certain invalid inputs, which might not be the expected behavior for a method that parses time.
- **Reasoning**: Similar to the byte array version, `parseLocalTime5(char[] str, int off)` returns `null` for unrecognized formats or insufficient length. This deviates from a potential base contract that might expect exceptions for invalid inputs, thus violating LSP if substitutability is expected based on a different error-handling strategy.

### LSP-076 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalTime6
- **Confidence**: Found in 1 scan(s)
- **Lines**: 530–547
- **Type**: method
- **Description**: The parseLocalTime6(char[] str, int off) method returns null for unrecognized formats, potentially violating LSP if the base contract expects exceptions.
- **Reasoning**: Similar to the byte array version, `parseLocalTime6(char[] str, int off)` returns `null` for invalid formats. This could violate LSP if the base contract mandates throwing exceptions for parsing failures, as callers might not anticipate or handle `null` returns.

### LSP-077 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalTime7
- **Confidence**: Found in 1 scan(s)
- **Lines**: 567–583
- **Type**: method
- **Description**: The parseLocalTime7(byte[] str, int off) method returns null for unrecognized formats, potentially violating LSP if the base contract expects exceptions.
- **Reasoning**: Returning `null` for parsing errors in `parseLocalTime7(byte[] str, int off)` might violate LSP if the base method's contract implies throwing an exception for such cases. Callers might be designed to catch specific exceptions and not handle `null` returns gracefully.

### LSP-078 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalTime7
- **Confidence**: Found in 1 scan(s)
- **Lines**: 589–605
- **Type**: method
- **Description**: The parseLocalTime7(char[] str, int off) method returns null for unrecognized formats, potentially violating LSP if the base contract expects exceptions.
- **Reasoning**: Similar to the byte array version, `parseLocalTime7(char[] str, int off)` returning `null` for invalid inputs can violate LSP if the base contract expects exceptions. This can lead to `NullPointerException`s if not handled correctly by callers expecting a different error signaling mechanism.

### LSP-080 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalTime8
- **Confidence**: Found in 1 scan(s)
- **Lines**: 632–637
- **Type**: method
- **Description**: The parseLocalTime8(char[] bytes, int off) method returns null for invalid inputs, which might violate LSP if exceptions are expected.
- **Reasoning**: The `parseLocalTime8(char[] bytes, int off)` method returns `null` for invalid inputs. This can violate LSP if the base contract expects exceptions for such cases, leading to potential `NullPointerException`s for callers not expecting `null`.

### LSP-082 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDate
- **Confidence**: Found in 1 scan(s)
- **Lines**: 900–915
- **Type**: method
- **Description**: parseLocalDate(String str) throws DateTimeParseException for certain invalid inputs, which might not be consistent with a base contract expecting null or a different exception.
- **Reasoning**: The `parseLocalDate(String str)` method throws `DateTimeParseException` for unrecognized inputs like '00000000'. If the base contract for `parseLocalDate` implies returning `null` or a different exception type for invalid formats, this method violates LSP. Callers might not be prepared to catch `DateTimeParseException` if the base class contract doesn't specify it.

### LSP-084 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseMillis
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1059–1125
- **Type**: method
- **Description**: The parseMillis(byte[] chars, int off, int len, Charset charset, ZoneId zoneId) method has complex logic and throws DateTimeParseException, which might violate LSP.
- **Reasoning**: This method contains a large amount of conditional logic for parsing dates from byte arrays, including checks for JSONReader context, specific formats, and potential exceptions. The complexity and specific handling of formats (e.g., `YYYYMMDD` parsing with date validation) might not be consistent with a base contract that implies a simpler or different parsing approach. The throwing of `DateTimeParseException` could also be an LSP violation if the base contract expects different error handling.

### LSP-085 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDate11
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1711–1738
- **Type**: method
- **Description**: The parseLocalDate11(char[] str, int off) method handles specific date formats and returns null for invalid inputs, potentially violating LSP.
- **Reasoning**: This method parses dates from character arrays supporting specific formats and returns `null` for invalid inputs. This might violate LSP if the base contract expects exceptions for parsing errors, as callers might not be prepared for `null` returns.

### LSP-086 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDate11
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1744–1771
- **Type**: method
- **Description**: The parseLocalDate11(byte[] str, int off) method handles specific date formats and returns null for invalid inputs, potentially violating LSP.
- **Reasoning**: Similar to the char array version, `parseLocalDate11(byte[] str, int off)` handles specific formats and returns `null` for invalid inputs. This can violate LSP if the base contract expects exceptions for parsing failures, leading to potential `NullPointerException`s.

### LSP-087 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTime14
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1890–1905
- **Type**: method
- **Description**: The parseLocalDateTime14(byte[] str, int off) method returns null for invalid inputs, potentially violating LSP if exceptions are expected.
- **Reasoning**: Similar to the char array version, `parseLocalDateTime14(byte[] str, int off)` returns `null` for invalid inputs. This can violate LSP if the base contract expects exceptions for parsing failures, leading to potential `NullPointerException`s.

### LSP-088 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTime26
- **Confidence**: Found in 1 scan(s)
- **Lines**: 2514–2534
- **Type**: method
- **Description**: The parseLocalDateTime26(byte[] str, int off) method returns null for invalid inputs, potentially violating LSP if exceptions are expected.
- **Reasoning**: Returning `null` from `parseLocalDateTime26(byte[] str, int off)` for invalid inputs might violate LSP if the base contract implies throwing an exception for such cases. Callers might not be prepared to handle `null` returns.

### LSP-089 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTime27
- **Confidence**: Found in 1 scan(s)
- **Lines**: 2579–2599
- **Type**: method
- **Description**: The parseLocalDateTime27(byte[] str, int off) method returns null for invalid inputs, potentially violating LSP if exceptions are expected.
- **Reasoning**: Returning `null` from `parseLocalDateTime27(byte[] str, int off)` for invalid inputs might violate LSP if the base contract implies throwing an exception for such cases. Callers might not be prepared to handle `null` returns.

### LSP-090 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTimeX
- **Confidence**: Found in 1 scan(s)
- **Lines**: 2774–2979
- **Type**: method
- **Description**: The parseLocalDateTimeX(char[] str, int offset, int len) method handles a wide range of formats and returns null for invalid inputs, potentially violating LSP.
- **Reasoning**: This method attempts to parse a very broad range of date-time formats based on length and character checks. Returning `null` for invalid inputs might violate LSP if the base contract expects exceptions. The extensive conditional logic makes it hard to guarantee consistent behavior across potential subclasses.

### LSP-091 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseZonedDateTime
- **Confidence**: Found in 1 scan(s)
- **Lines**: 3577–3581
- **Type**: method
- **Description**: parseZonedDateTime(byte[] str, int off, int len) uses a default ZoneId, which might violate LSP.
- **Reasoning**: This method uses `DEFAULT_ZONE_ID` if `defaultZoneId` is null. This reliance on a default value can violate LSP if a subclass or caller expects a different default or if the base contract implies that the timezone should always be explicitly handled or derived differently.

### LSP-092 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseZonedDateTime
- **Confidence**: Found in 1 scan(s)
- **Lines**: 3592–3596
- **Type**: method
- **Description**: parseZonedDateTime(char[] str, int off, int len) uses a default ZoneId, which might violate LSP.
- **Reasoning**: Similar to the byte array version, `parseZonedDateTime(char[] str, int off, int len)` uses `DEFAULT_ZONE_ID` if the provided `zoneId` is null. This reliance on a default timezone can violate LSP if the base contract expects explicit timezone handling or a different default.

### LSP-093 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseZonedDateTime
- **Confidence**: Found in 1 scan(s)
- **Lines**: 5800–6313
- **Type**: method
- **Description**: The parseZonedDateTime(char[] str, int off, int len, ZoneId defaultZoneId) method contains extensive logic for parsing various date-time formats and throws DateTimeParseException, potentially violating LSP.
- **Reasoning**: Similar to the byte array version, `parseZonedDateTime(char[] str, int off, int len, ZoneId defaultZoneId)` handles numerous date-time formats and throws `DateTimeParseException` for invalid inputs. This violates LSP if the base contract expects a different error handling mechanism or a more generalized parsing approach. The reliance on specific length checks and internal parsing logic makes it non-substitutable.

### LSP-094 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseZonedDateTimeCookie
- **Confidence**: Found in 1 scan(s)
- **Lines**: 6325–6342
- **Type**: method
- **Description**: The parseZonedDateTimeCookie(String str) method has conditional logic based on the string ending, which might violate LSP if the base contract implies a single, consistent parsing mechanism.
- **Reasoning**: This method handles cookie date formats with conditional logic based on the string ending (' CST'). This specific handling might not be substitutable if the base contract for parsing zoned date times implies a more uniform approach or if subclasses need to support different cookie formats or timezone handling. The hardcoded `SHANGHAI_ZONE_ID` is also a potential LSP violation if a different zone is expected.

### LSP-095 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.getZoneId
- **Confidence**: Found in 1 scan(s)
- **Lines**: 6353–6388
- **Type**: method
- **Description**: The getZoneId(String zoneIdStr, ZoneId defaultZoneId) method has specific hardcoded zone IDs and parsing logic, which might violate LSP.
- **Reasoning**: This method has hardcoded handling for specific zone ID strings like '000', '+08:00', and 'CST'. It also includes logic for parsing zone IDs enclosed in brackets. This specialized behavior might not be substitutable if a base contract expects a more generic or configurable way to obtain ZoneIds, or if it relies on a different lookup mechanism. The direct use of `ZoneId.of()` could also throw exceptions not anticipated by a base contract.

### LSP-096 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseMillisYMDHMS19
- **Confidence**: Found in 1 scan(s)
- **Lines**: 6400–6793
- **Type**: method
- **Description**: The parseMillisYMDHMS19(String str, ZoneId zoneId) method contains extensive logic for parsing specific date formats and throws DateTimeParseException, which might violate LSP.
- **Reasoning**: This method parses dates in 'yyyy-MM-dd HH:mm:ss' format and variations, with extensive checks for character positions and digit validity. It also throws `DateTimeParseException` for invalid inputs. This violates LSP if the base contract implies a different error handling strategy or a more flexible parsing approach. The reliance on specific character positions and the JVM version checks are implementation details that might not be substitutable.

### LSP-097 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseMillis19
- **Confidence**: Found in 1 scan(s)
- **Lines**: 6812–7194
- **Type**: method
- **Description**: The parseMillis19(String str, ZoneId zoneId, DateTimeFormatPattern pattern) method has complex logic, throws DateTimeParseException, and relies on specific patterns, potentially violating LSP.
- **Reasoning**: This method parses dates based on specific `DateTimeFormatPattern`s and throws `DateTimeParseException` for invalid inputs. This violates LSP if the base contract implies a different error handling strategy or a more generic parsing mechanism. The explicit reliance on predefined patterns makes it less flexible for substitution.

### LSP-098 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseMillis19
- **Confidence**: Found in 1 scan(s)
- **Lines**: 7196–7578
- **Type**: method
- **Description**: The parseMillis19(byte[] bytes, int off, ZoneId zoneId) method contains extensive logic for parsing specific date formats and throws DateTimeParseException, which might violate LSP.
- **Reasoning**: This method parses dates from byte arrays in specific formats ('yyyy-MM-dd HH:mm:ss' and variations) and throws `DateTimeParseException` for invalid inputs. This violates LSP if the base contract implies a different error handling strategy or a more flexible parsing approach. The specific character checks and reliance on internal `calcEpochDay` method are implementation details that might not be substitutable.

### LSP-099 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseMillis19
- **Confidence**: Found in 1 scan(s)
- **Lines**: 7580–7962
- **Type**: method
- **Description**: The parseMillis19(char[] bytes, int off, ZoneId zoneId) method contains extensive logic for parsing specific date formats and throws DateTimeParseException, which might violate LSP.
- **Reasoning**: Similar to the byte array version, `parseMillis19(char[] bytes, int off, ZoneId zoneId)` parses specific date formats and throws `DateTimeParseException` for invalid inputs. This violates LSP if the base contract implies a different error handling strategy or a more flexible parsing approach. The reliance on specific character checks and internal methods like `calcEpochDay` makes it non-substitutable.

### LSP-100 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseMillis10
- **Confidence**: Found in 1 scan(s)
- **Lines**: 7980–8110
- **Type**: method
- **Description**: The parseMillis10(String str, ZoneId zoneId, DateTimeFormatPattern pattern) method has complex logic and throws DateTimeParseException, which might violate LSP.
- **Reasoning**: This method parses dates based on specific `DateTimeFormatPattern`s and throws `DateTimeParseException` for invalid inputs. This violates LSP if the base contract implies a different error handling strategy or a more generic parsing mechanism. The reliance on specific patterns makes it less flexible for substitution.

### LSP-101 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.formatYMDHMS19
- **Confidence**: Found in 1 scan(s)
- **Lines**: 8519–8523
- **Type**: method
- **Description**: formatYMDHMS19(Date date) uses DEFAULT_ZONE_ID, which might violate LSP if a different timezone is expected.
- **Reasoning**: The `formatYMDHMS19(Date date)` method uses `DEFAULT_ZONE_ID` for formatting. This violates LSP if a subclass or caller expects the formatting to occur in a timezone other than the system default. The `Date` object itself doesn't inherently carry timezone information, so the interpretation of the formatted string depends on the assumed timezone.

### LSP-102 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.formatYMDHMS19
- **Confidence**: Found in 1 scan(s)
- **Lines**: 8534–8795
- **Type**: method
- **Description**: The formatYMDHMS19(Date date, ZoneId zoneId) method has complex logic for timezone handling and date formatting, potentially violating LSP.
- **Reasoning**: This method involves complex logic for calculating local time based on the provided `zoneId`, including specific handling for Shanghai's timezone rules. This intricate implementation might not be substitutable if a subclass expects a simpler or different timezone conversion logic. The calculation of `localEpochDay` and `secsOfDay` based on timezone offsets is a detailed implementation that could break LSP if the base contract implies a more abstract or less timezone-sensitive formatting.

### LSP-103 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.formatYMD8
- **Confidence**: Found in 1 scan(s)
- **Lines**: 8814–8818
- **Type**: method
- **Description**: formatYMD8(Date date) uses DEFAULT_ZONE_ID, which might violate LSP if a different timezone is expected.
- **Reasoning**: The `formatYMD8(Date date)` method uses `DEFAULT_ZONE_ID` for formatting. This violates LSP if a subclass or caller expects the formatting to occur in a timezone other than the system default. The `Date` object's millisecond representation is timezone-agnostic, so the interpretation of the formatted string depends on the assumed timezone.

### LSP-104 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseDateYMDHMS19
- **Confidence**: Found in 1 scan(s)
- **Lines**: 148–152
- **Type**: method
- **Description**: Method returns a new Date object, potentially violating LSP if Date's internal state is expected to be immutable or if subclasses alter date behavior.
- **Reasoning**: The `parseDateYMDHMS19` method creates and returns a `new Date(millis)`. While `java.util.Date` is mutable, this method itself does not violate LSP by itself. However, if `Date` objects are treated as immutable by the caller or other parts of the system, and a subclass of `Date` (or a wrapper) were to be used with this parser, the caller might expect certain behaviors from `Date` that a subclass might alter. This is a potential for LSP violation depending on how `Date` is used elsewhere. The severity is high because `java.util.Date` is notoriously problematic for immutability expectations.

### LSP-105 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseDate
- **Confidence**: Found in 1 scan(s)
- **Lines**: 261–270
- **Type**: method
- **Description**: The method returns a `java.util.Date` object, which is mutable and can lead to LSP violations if callers expect immutability.
- **Reasoning**: Similar to the `parseDate(String str, String format, ZoneId zoneId)` method, this overload also returns `java.util.Date`. As `java.util.Date` is mutable, its returned instances can be modified after they are obtained, potentially breaking the LSP if the calling code relies on the date's state remaining unchanged. This can happen if the caller modifies the `Date` object and other parts of the system are still using the original reference, leading to unexpected behavior.

### LSP-106 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseMillis
- **Confidence**: Found in 1 scan(s)
- **Lines**: 370–381
- **Type**: method
- **Description**: The method returns milliseconds as a `long`, which is a primitive type and inherently immutable. However, the parsing logic might be considered a contract that could be violated by subclasses.
- **Reasoning**: This method returns a primitive `long`, which is immutable. Therefore, the direct return type does not violate LSP. The potential LSP violation lies in the parsing logic itself. If this method were to be overridden by a subclass, and that subclass changed the parsing behavior (e.g., how it handles time zones, specific formats, or errors), it could lead to LSP violations if the calling code relied on the original parsing contract established by this method.

### LSP-107 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalTime5
- **Confidence**: Found in 1 scan(s)
- **Lines**: 560–574
- **Type**: method
- **Description**: The method returns `LocalTime` objects, which are immutable and thus do not violate LSP directly through their return type.
- **Reasoning**: This method returns `java.time.LocalTime` objects, which are immutable. Therefore, the return type does not violate LSP. However, the parsing logic for different time formats is complex. If a subclass were to override this method and alter the parsing behavior (e.g., how it handles separators or digit extraction), it could lead to an LSP violation if callers expect the original, specific parsing logic.

### LSP-108 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalTime5
- **Confidence**: Found in 1 scan(s)
- **Lines**: 577–591
- **Type**: method
- **Description**: The method returns `LocalTime` objects, which are immutable and thus do not violate LSP directly through their return type.
- **Reasoning**: This method returns `java.time.LocalTime`, which is an immutable object. This means the return type itself does not violate LSP. However, the method's parsing logic handles multiple formats for `LocalTime`. If a subclass were to override this method and change how it parses these formats, or how it handles invalid inputs (e.g., returning null instead of throwing an exception), it could violate the LSP for callers expecting the original contract.

### LSP-109 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalTime6
- **Confidence**: Found in 1 scan(s)
- **Lines**: 605–622
- **Type**: method
- **Description**: The method returns `LocalTime` objects, which are immutable and thus do not violate LSP directly through their return type.
- **Reasoning**: This method returns `java.time.LocalTime`, an immutable class, so the return type itself does not cause an LSP violation. However, the method's parsing logic is complex, handling various formats. If a subclass overrides this method and alters the parsing behavior or error handling (e.g., changing how invalid formats are treated), it could violate the LSP for consumers expecting the original contract.

### LSP-110 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalTime7
- **Confidence**: Found in 1 scan(s)
- **Lines**: 657–672
- **Type**: method
- **Description**: The method returns `LocalTime` objects, which are immutable and thus do not violate LSP directly through their return type.
- **Reasoning**: This method returns `java.time.LocalTime`, an immutable type, so the return type itself does not violate LSP. However, the method's parsing logic is extensive, covering various `LocalTime` formats. If a subclass overrides this method and changes the parsing behavior or error handling (e.g., how it deals with malformed input), it could break the LSP for callers expecting the original contract.

### LSP-111 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalTime7
- **Confidence**: Found in 1 scan(s)
- **Lines**: 675–690
- **Type**: method
- **Description**: The method returns `LocalTime` objects, which are immutable and thus do not violate LSP directly through their return type.
- **Reasoning**: This method returns `java.time.LocalTime`, an immutable class, meaning the return type itself does not cause an LSP violation. However, the parsing logic is complex and handles various `LocalTime` formats. If a subclass overrides this method and alters the parsing logic or error handling (e.g., how it treats malformed input), it could violate the LSP for consumers expecting the original behavior.

### LSP-112 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalTime8
- **Confidence**: Found in 1 scan(s)
- **Lines**: 704–709
- **Type**: method
- **Description**: The method returns `LocalTime` objects, which are immutable and thus do not violate LSP directly through their return type.
- **Reasoning**: This method returns `java.time.LocalTime`, an immutable type, so the return type itself does not violate LSP. However, the parsing logic depends on helper methods (`hms`) and checks for valid input. If a subclass overrides this method and changes the parsing logic or the conditions under which it returns null (e.g., by altering the `hms` method's behavior or the input validation), it could violate the LSP for callers expecting the original contract.

### LSP-113 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalTime8
- **Confidence**: Found in 1 scan(s)
- **Lines**: 712–717
- **Type**: method
- **Description**: The method returns `LocalTime` objects, which are immutable and thus do not violate LSP directly through their return type.
- **Reasoning**: This method returns `java.time.LocalTime`, an immutable object, so the return type itself does not cause an LSP violation. However, the parsing logic for `LocalTime` relies on specific character checks (`bytes[off + 2] != ':' || bytes[off + 5] != ':'`) and digit extraction. If a subclass overrides this method and alters these checks or the `localTime` creation logic, it could violate the LSP for consumers expecting the original parsing behavior.

### LSP-114 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTime
- **Confidence**: Found in 1 scan(s)
- **Lines**: 868–907
- **Type**: method
- **Description**: The method returns `LocalDateTime` objects, which are immutable and thus do not violate LSP directly through their return type.
- **Reasoning**: This method returns `java.time.LocalDateTime`, which is immutable, so the return type itself does not violate LSP. However, the method's parsing logic handles many specific length cases for `LocalDateTime` from character arrays. If a subclass overrides this method and alters the length checks, the parsing logic for any of these cases, or the error handling (e.g., returning null vs. throwing `DateTimeParseException`), it could violate the LSP for callers expecting the original contract.

### LSP-115 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDate
- **Confidence**: Found in 1 scan(s)
- **Lines**: 917–934
- **Type**: method
- **Description**: The method returns `LocalDate` objects, which are immutable and thus do not violate LSP directly through their return type.
- **Reasoning**: This method returns `java.time.LocalDate`, which is immutable, so the return type itself does not violate LSP. However, the parsing logic handles different string representations of dates. If a subclass overrides this method and changes the parsing logic or error handling (e.g., what constitutes an invalid input and how it's reported), it could violate the LSP for callers expecting the original contract.

### LSP-116 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDate
- **Confidence**: Found in 1 scan(s)
- **Lines**: 960–980
- **Type**: method
- **Description**: The method returns `LocalDate` objects, which are immutable and thus do not violate LSP directly through their return type.
- **Reasoning**: This method returns `java.time.LocalDate`, which is immutable, so the return type itself does not cause an LSP violation. However, the parsing logic handles various character array representations of dates. If a subclass overrides this method and alters the parsing logic or error handling (e.g., changing how invalid inputs are treated), it could violate the LSP for callers expecting the original contract.

### LSP-117 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDate8
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1209–1234
- **Type**: method
- **Description**: The method returns `LocalDate` objects, which are immutable and thus do not violate LSP directly through their return type.
- **Reasoning**: This method returns `java.time.LocalDate`, which is immutable, meaning the return type itself does not violate LSP. However, the parsing logic is quite intricate, handling multiple date formats within an 8-character input. If a subclass were to override this method and change how it interprets these formats or handles invalid inputs (e.g., returning null instead of throwing an exception for malformed dates), it could violate the LSP for callers expecting the original parsing contract.

### LSP-118 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDate8
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1237–1262
- **Type**: method
- **Description**: The method returns `LocalDate` objects, which are immutable and thus do not violate LSP directly through their return type.
- **Reasoning**: This method returns `java.time.LocalDate`, an immutable object, so the return type itself does not cause an LSP violation. However, the parsing logic is complex, handling multiple date formats within an 8-character input. If a subclass overrides this method and alters the parsing logic or error handling (e.g., changing how invalid formats are treated), it could violate the LSP for callers expecting the original behavior.

### LSP-119 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDate9
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1277–1328
- **Type**: method
- **Description**: The method returns `LocalDate` objects, which are immutable and thus do not violate LSP directly through their return type.
- **Reasoning**: This method returns `java.time.LocalDate`, which is immutable, thus the return type does not violate LSP. However, the parsing logic is extensive, handling various date formats within a 9-character input. If a subclass overrides this method and alters the parsing logic or error handling (e.g., changing how invalid inputs are managed or which formats are supported), it could violate the LSP for callers expecting the original contract.

### LSP-120 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDate11
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1503–1523
- **Type**: method
- **Description**: The method returns `LocalDate` objects, which are immutable and thus do not violate LSP directly through their return type.
- **Reasoning**: This method returns `java.time.LocalDate`, an immutable object, so the return type itself does not cause an LSP violation. However, the parsing logic is complex, handling specific formats within an 11-character input. If a subclass overrides this method and alters the parsing logic or error handling (e.g., how it treats malformed inputs or unsupported formats), it could violate the LSP for consumers expecting the original behavior.

### LSP-121 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTime12
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1560–1580
- **Type**: method
- **Description**: The method returns `LocalDateTime` objects, which are immutable and thus do not violate LSP directly through their return type.
- **Reasoning**: This method returns `java.time.LocalDateTime`, an immutable object, so the return type itself does not cause an LSP violation. However, the parsing logic is specific to a 12-character format. If a subclass overrides this method and alters the parsing logic or error handling (e.g., changing how invalid inputs are treated or extending support to other formats), it could violate the LSP for consumers expecting the original behavior.

### LSP-122 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTime14
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1594–1610
- **Type**: method
- **Description**: The method returns `LocalDateTime` objects, which are immutable and thus do not violate LSP directly through their return type.
- **Reasoning**: This method returns `java.time.LocalDateTime`, which is immutable, so the return type does not violate LSP. However, the parsing logic is specific to a 14-character format. If a subclass overrides this method and changes the parsing logic or error handling (e.g., how it treats malformed inputs or unsupported formats), it could violate the LSP for callers expecting the original contract.

### LSP-123 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTime20
- **Confidence**: Found in 1 scan(s)
- **Lines**: 2187–2204
- **Type**: method
- **Description**: The method returns `LocalDateTime` objects, which are immutable and thus do not violate LSP directly through their return type.
- **Reasoning**: This method returns `java.time.LocalDateTime`, an immutable object, so the return type itself does not cause an LSP violation. However, the parsing logic is specific to a 20-character format and includes checks for hour, minute, and second ranges. If a subclass overrides this method and alters the parsing logic or error handling (e.g., changing how invalid inputs are treated or the range checks), it could violate the LSP for consumers expecting the original behavior.

### LSP-124 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseLocalDateTime27
- **Confidence**: Found in 1 scan(s)
- **Lines**: 2295–2314
- **Type**: method
- **Description**: The method returns `LocalDateTime` objects, which are immutable and thus do not violate LSP directly through their return type.
- **Reasoning**: This method returns `java.time.LocalDateTime`, an immutable object, so the return type itself does not cause an LSP violation. However, the parsing logic is complex, handling a specific 27-character format and including range checks for time components. If a subclass overrides this method and alters the parsing logic or error handling (e.g., changing how invalid inputs are treated or the range checks), it could violate the LSP for consumers expecting the original behavior.

### LSP-132 [HIGH] core/src/main/java/com/alibaba/fastjson2/JSONReaderJSONB.java — JSONReaderJSONB.getStringLength()
- **Confidence**: Found in 1 scan(s)
- **Lines**: 5255–5260
- **Type**: method
- **Description**: Subtype JSONReaderJSONB throws UnsupportedOperationException for an abstract method defined in its base type JSONReader.
- **Reasoning**: The abstract method `getStringLength()` in JSONReader implies that all concrete readers should be able to determine string length. JSONReaderJSONB throws `UnsupportedOperationException`, indicating it cannot fulfill this contract, which violates LSP. This suggests the method is not universally applicable across all JSONReader subtypes.

### LSP-137 [HIGH] core/src/main/java/com/alibaba/fastjson2/JSONReaderJSONB.java — JSONReaderJSONB.readNumber0
- **Confidence**: Found in 1 scan(s)
- **Lines**: 4112–4113
- **Type**: method
- **Description**: Subtype alters base class contract by throwing UnsupportedOperationException for an abstract method.
- **Reasoning**: The abstract method `JSONReader.readNumber0()` implies a contract that all concrete subtypes should provide a functional implementation. `JSONReaderJSONB` violates this by explicitly throwing `JSONException("UnsupportedOperation")`, which breaks substitutability.

### LSP-138 [HIGH] core/src/main/java/com/alibaba/fastjson2/JSONReaderJSONB.java — JSONReaderJSONB.nextIfMatchIdent
- **Confidence**: Found in 1 scan(s)
- **Lines**: 5567–5568
- **Type**: method
- **Description**: Subtype alters base class contract by throwing UnsupportedOperationException for an abstract method.
- **Reasoning**: The abstract method `JSONReader.nextIfMatchIdent(char c0, char c1)` implies a contract that all concrete subtypes should provide a functional implementation. `JSONReaderJSONB` violates this by explicitly throwing `JSONException("UnsupportedOperation")`, which breaks substitutability. This applies to all `nextIfMatchIdent` overloads (L5572, L5592, L5597, L5602).

### LSP-139 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderJSONB.java — JSONReaderJSONB.readLocalDateTime14
- **Confidence**: Found in 1 scan(s)
- **Lines**: 4747–4752
- **Type**: method
- **Description**: Subtype alters base class contract by throwing JSONException for an abstract date parsing method.
- **Reasoning**: Similar to `readLocalDateTime12`, this method throws `JSONException("date only support string input")`, violating the implied contract of the abstract `JSONReader.readLocalDateTime14()` method.

### LSP-140 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderJSONB.java — JSONReaderJSONB.readLocalDateTime16
- **Confidence**: Found in 1 scan(s)
- **Lines**: 4759–4764
- **Type**: method
- **Description**: Subtype alters base class contract by throwing JSONException for an abstract date parsing method.
- **Reasoning**: Similar to `readLocalDateTime12`, this method throws `JSONException("date only support string input")`, violating the implied contract of the abstract `JSONReader.readLocalDateTime16()` method.

### LSP-141 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderJSONB.java — JSONReaderJSONB.readLocalDateTime17
- **Confidence**: Found in 1 scan(s)
- **Lines**: 4771–4776
- **Type**: method
- **Description**: Subtype alters base class contract by throwing JSONException for an abstract date parsing method.
- **Reasoning**: Similar to `readLocalDateTime12`, this method throws `JSONException("date only support string input")`, violating the implied contract of the abstract `JSONReader.readLocalDateTime17()` method.

### LSP-142 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderJSONB.java — JSONReaderJSONB.readLocalTime11
- **Confidence**: Found in 1 scan(s)
- **Lines**: 4795–4800
- **Type**: method
- **Description**: Subtype alters base class contract by throwing JSONException for an abstract date parsing method.
- **Reasoning**: Similar to `readLocalDateTime12`, this method throws `JSONException("date only support string input")`, violating the implied contract of the abstract `JSONReader.readLocalTime11()` method.

### LSP-143 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderJSONB.java — JSONReaderJSONB.readZonedDateTimeX
- **Confidence**: Found in 1 scan(s)
- **Lines**: 4807–4810
- **Type**: method
- **Description**: Subtype alters base class contract by throwing JSONException for an abstract date parsing method.
- **Reasoning**: Similar to `readLocalDateTime12`, this method throws `JSONException("date only support string input")`, violating the implied contract of the abstract `JSONReader.readZonedDateTimeX(int len)` method.

### LSP-144 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderJSONB.java — JSONReaderJSONB.readLocalDate9
- **Confidence**: Found in 1 scan(s)
- **Lines**: 5353–5358
- **Type**: method
- **Description**: Subtype alters base class contract by throwing JSONException for an abstract date parsing method.
- **Reasoning**: Similar to `readLocalDateTime12`, this method throws `JSONException("date only support string input")`, violating the implied contract of the abstract `JSONReader.readLocalDate9()` method.

### LSP-145 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderJSONB.java — JSONReaderJSONB.readLocalDate10
- **Confidence**: Found in 1 scan(s)
- **Lines**: 5366–5373
- **Type**: method
- **Description**: Subtype alters base class contract by throwing JSONException for an abstract date parsing method.
- **Reasoning**: Similar to `readLocalDateTime12`, this method throws `JSONException("date only support string input")`, violating the implied contract of the abstract `JSONReader.readLocalDate10()` method.

### LSP-146 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderJSONB.java — JSONReaderJSONB.readLocalDate11
- **Confidence**: Found in 1 scan(s)
- **Lines**: 5381–5388
- **Type**: method
- **Description**: Subtype alters base class contract by throwing JSONException for an abstract date parsing method.
- **Reasoning**: Similar to `readLocalDateTime12`, this method throws `JSONException("date only support string input")`, violating the implied contract of the abstract `JSONReader.readLocalDate11()` method.

### LSP-147 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderJSONB.java — JSONReaderJSONB.readLocalTime5
- **Confidence**: Found in 1 scan(s)
- **Lines**: 5396–5401
- **Type**: method
- **Description**: Subtype alters base class contract by throwing JSONException for an abstract date parsing method.
- **Reasoning**: Similar to `readLocalDateTime12`, this method throws `JSONException("date only support string input")`, violating the implied contract of the abstract `JSONReader.readLocalTime5()` method. This is a duplicate of the earlier `readLocalTime5` entry, highlighting the pervasive nature of the issue.

### LSP-148 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderJSONB.java — JSONReaderJSONB.readLocalTime6
- **Confidence**: Found in 1 scan(s)
- **Lines**: 5408–5413
- **Type**: method
- **Description**: Subtype alters base class contract by throwing JSONException for an abstract date parsing method.
- **Reasoning**: Similar to `readLocalDateTime12`, this method throws `JSONException("date only support string input")`, violating the implied contract of the abstract `JSONReader.readLocalTime6()` method.

### LSP-149 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderJSONB.java — JSONReaderJSONB.readLocalTime7
- **Confidence**: Found in 1 scan(s)
- **Lines**: 5420–5425
- **Type**: method
- **Description**: Subtype alters base class contract by throwing JSONException for an abstract date parsing method.
- **Reasoning**: Similar to `readLocalDateTime12`, this method throws `JSONException("date only support string input")`, violating the implied contract of the abstract `JSONReader.readLocalTime7()` method.

### LSP-150 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderJSONB.java — JSONReaderJSONB.readLocalTime8
- **Confidence**: Found in 1 scan(s)
- **Lines**: 5432–5437
- **Type**: method
- **Description**: Subtype alters base class contract by throwing JSONException for an abstract date parsing method.
- **Reasoning**: Similar to `readLocalDateTime12`, this method throws `JSONException("date only support string input")`, violating the implied contract of the abstract `JSONReader.readLocalTime8()` method.

### LSP-151 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderJSONB.java — JSONReaderJSONB.readLocalTime9
- **Confidence**: Found in 1 scan(s)
- **Lines**: 5444–5449
- **Type**: method
- **Description**: Subtype alters base class contract by throwing JSONException for an abstract date parsing method.
- **Reasoning**: Similar to `readLocalDateTime12`, this method throws `JSONException("date only support string input")`, violating the implied contract of the abstract `JSONReader.readLocalTime9()` method.

### LSP-152 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderJSONB.java — JSONReaderJSONB.readLocalTime12
- **Confidence**: Found in 1 scan(s)
- **Lines**: 5456–5461
- **Type**: method
- **Description**: Subtype alters base class contract by throwing JSONException for an abstract date parsing method.
- **Reasoning**: Similar to `readLocalDateTime12`, this method throws `JSONException("date only support string input")`, violating the implied contract of the abstract `JSONReader.readLocalTime12()` method.

### LSP-153 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderJSONB.java — JSONReaderJSONB.readLocalTime15
- **Confidence**: Found in 1 scan(s)
- **Lines**: 5468–5473
- **Type**: method
- **Description**: Subtype alters base class contract by throwing JSONException for an abstract date parsing method.
- **Reasoning**: Similar to `readLocalDateTime12`, this method throws `JSONException("date only support string input")`, violating the implied contract of the abstract `JSONReader.readLocalTime15()` method.

### LSP-154 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderJSONB.java — JSONReaderJSONB.readLocalTime18
- **Confidence**: Found in 1 scan(s)
- **Lines**: 5480–5485
- **Type**: method
- **Description**: Subtype alters base class contract by throwing JSONException for an abstract date parsing method.
- **Reasoning**: Similar to `readLocalDateTime12`, this method throws `JSONException("date only support string input")`, violating the implied contract of the abstract `JSONReader.readLocalTime18()` method.

### LSP-155 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderJSONB.java — JSONReaderJSONB.readLocalDateTime18
- **Confidence**: Found in 1 scan(s)
- **Lines**: 5492–5497
- **Type**: method
- **Description**: Subtype alters base class contract by throwing JSONException for an abstract date parsing method.
- **Reasoning**: Similar to `readLocalDateTime12`, this method throws `JSONException("date only support string input")`, violating the implied contract of the abstract `JSONReader.readLocalDateTime18()` method.

### LSP-156 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderJSONB.java — JSONReaderJSONB.readLocalDateTime20
- **Confidence**: Found in 1 scan(s)
- **Lines**: 5504–5509
- **Type**: method
- **Description**: Subtype alters base class contract by throwing JSONException for an abstract date parsing method.
- **Reasoning**: Similar to `readLocalDateTime12`, this method throws `JSONException("date only support string input")`, violating the implied contract of the abstract `JSONReader.readLocalDateTime20()` method.

### LSP-157 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderJSONB.java — JSONReaderJSONB.readMillis19
- **Confidence**: Found in 1 scan(s)
- **Lines**: 5516–5518
- **Type**: method
- **Description**: Subtype alters base class contract by throwing JSONException for an abstract date parsing method.
- **Reasoning**: Similar to `readLocalDateTime12`, this method throws `JSONException("date only support string input")`, violating the implied contract of the abstract `JSONReader.readMillis19()` method.

### LSP-158 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderJSONB.java — JSONReaderJSONB.readLocalDateTime19
- **Confidence**: Found in 1 scan(s)
- **Lines**: 5527–5535
- **Type**: method
- **Description**: Subtype alters base class contract by throwing JSONException for an abstract date parsing method.
- **Reasoning**: Similar to `readLocalDateTime12`, this method throws `JSONException("date only support string input")`, violating the implied contract of the abstract `JSONReader.readLocalDateTime19()` method.

### LSP-159 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderJSONB.java — JSONReaderJSONB.readLocalDateTimeX
- **Confidence**: Found in 1 scan(s)
- **Lines**: 5543–5546
- **Type**: method
- **Description**: Subtype alters base class contract by throwing JSONException for an abstract date parsing method.
- **Reasoning**: Similar to `readLocalDateTime12`, this method throws `JSONException("date only support string input")`, violating the implied contract of the abstract `JSONReader.readLocalDateTimeX(int len)` method.

### LSP-160 [HIGH] core/src/main/java/com/alibaba/fastjson2/JSONWriter.java — JSONWriter.writeRaw
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1229–1230
- **Type**: method
- **Description**: Concrete method in abstract class throws UnsupportedOperationException.
- **Reasoning**: The method `JSONWriter.writeRaw(byte b)` is a concrete (non-abstract) method in an abstract class. Its implementation throws `JSONException("UnsupportedOperation")`. This means any client using a `JSONWriter` instance, if that instance does not override this method (or inherits this default throwing behavior), will encounter a runtime error. This violates LSP as the base type's method contract is broken by its own default implementation.
