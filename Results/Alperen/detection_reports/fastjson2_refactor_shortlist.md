# Refactor Shortlist: fastjson2

Quota: 12 issues × 5 principles = 60 total.
Selected: **56**.

> **Note:** the following principles have fewer issues than the quota. Per the project brief, seed violations manually to fill the gap:
> - ISP: 8 / 12

Ranking: `scan_count` desc, then severity (high > medium > low), then file_path, then line_start.

## SRP (12 selected)

| # | Issue ID | Confidence | Severity | Location | Description |
|---|----------|-----------:|----------|----------|-------------|
| 1 | SRP-001 | 10 scan(s) | high | `core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java` DateUtils (L47–2130) | DateUtils acts as a God Class for all date-related operations, mixing high-level logic with low-level infrastructure concerns. |
| 2 | SRP-010 | 6 scan(s) | high | `core/src/main/java/com/alibaba/fastjson2/JSONReader.java` JSONReader (L54–6887) | The class acts as a 'God Class' by combining multiple distinct responsibilities: low-level JSON tokenization, high-level JSON structure navigation, type-specific deserialization, complex numeric parsing/coercion, polymorphic deserialization, reference resolution, configuration management, and factory creation. |
| 3 | SRP-002 | 6 scan(s) | medium | `core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF8.java` JSONReaderUTF8 (L21–2100) | Mixes JSON structural tokenization with specific business type parsing logic. |
| 4 | SRP-006 | 4 scan(s) | high | `core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF16.java` JSONReaderUTF16 (L20–2070) | The class mixes JSON lexical analysis, syntactic parsing, and direct Java type conversion for numerous data types, mirroring JSONReaderUTF8. |
| 5 | SRP-011 | 3 scan(s) | high | `core/src/main/java/com/alibaba/fastjson2/JSONWriter.java` JSONWriter (L68–5055) | Fat interface defining excessive abstract methods for all JSON writing operations and data types. |
| 6 | SRP-012 | 3 scan(s) | high | `core/src/main/java/com/alibaba/fastjson2/util/TypeUtils.java` TypeUtils (L29–3878) | God class combining unrelated utility functions for type conversion, reflection, number parsing, and validation. |
| 7 | SRP-016 | 2 scan(s) | high | `core/src/main/java/com/alibaba/fastjson2/reader/ObjectReaderCreatorASM.java` ObjectReaderCreatorASM (L31–4626) | God class responsible for generating bytecode for all ObjectReader deserialization logic. |
| 8 | SRP-013 | 2 scan(s) | high | `core/src/main/java/com/alibaba/fastjson2/util/IOUtils.java` IOUtils (L32–3110) | God class combining low-level I/O, number formatting, encoding, and byte/char array manipulation. |
| 9 | SRP-015 | 2 scan(s) | high | `core/src/main/java/com/alibaba/fastjson2/writer/ObjectWriterCreatorASM.java` ObjectWriterCreatorASM (L29–5305) | God class responsible for generating bytecode for all ObjectWriter serialization logic. |
| 10 | SRP-019 | 2 scan(s) | medium | `core/src/main/java/com/alibaba/fastjson2/JSONB.java` JSONB (L128–3209) | The JSONB utility class mixes high-level JSONB parsing/serialization with very low-level binary encoding/decoding primitives. |
| 11 | SRP-020 | 1 scan(s) | high | `core/src/main/java/com/alibaba/fastjson2/JSONReaderJSONB.java` JSONReaderJSONB (L25–6303) | Class handles reading and parsing of JSONB data, involving low-level byte processing and high-level type conversions. |
| 12 | SRP-017 | 1 scan(s) | high | `core/src/main/java/com/alibaba/fastjson2/introspect/PropertyAccessorFactory.java` PropertyAccessorFactory (L35–5114) | The PropertyAccessorFactory class acts as a factory but also contains numerous concrete implementations for various property accessors. |

## OCP (12 selected)

| # | Issue ID | Confidence | Severity | Location | Description |
|---|----------|-----------:|----------|----------|-------------|
| 1 | OCP-001 | 9 scan(s) | high | `core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java` DateUtils.parseDate (L109–155) | The parseDate method uses a large switch statement to handle different date formats. |
| 2 | OCP-004 | 8 scan(s) | high | `core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java` DateUtils.parseLocalDate (L801–834) | The parseLocalDate method uses a switch statement based on the length of the input. |
| 3 | OCP-010 | 8 scan(s) | high | `core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java` DateUtils.parseLocalDateTimeX (L1429–1566) | The parseLocalDateTimeX method (byte array overload) uses a large switch statement based on the length of the input and complex conditional logic. |
| 4 | OCP-013 | 8 scan(s) | high | `core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java` DateUtils.parseMillis19 (L1647–1877) | The parseMillis19 method uses a large switch statement based on the DateTimeFormatPattern. |
| 5 | OCP-014 | 8 scan(s) | high | `core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java` DateUtils.parseMillis19 (L1892–2122) | The parseMillis19 method (byte array overload) uses a large switch statement based on the DateTimeFormatPattern. |
| 6 | OCP-020 | 7 scan(s) | high | `core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java` DateUtils.parseLocalDateTime (L709–766) | The `parseLocalDateTime` method (overload for byte array) uses a switch statement based on the length of the input. |
| 7 | OCP-005 | 7 scan(s) | high | `core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java` DateUtils.parseLocalDate (L916–971) | The parseLocalDate method (byte array overload) uses a switch statement based on the length of the input. |
| 8 | OCP-015 | 6 scan(s) | high | `core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java` DateUtils.parseMillis10 (L500–545) | The parseMillis10 method uses a switch statement based on the DateTimeFormatPattern. |
| 9 | OCP-007 | 6 scan(s) | high | `core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java` DateUtils.parseMillis (L568–631) | The parseMillis method (byte array overload) uses multiple conditional checks and a switch statement for parsing different date formats. |
| 10 | OCP-003 | 6 scan(s) | high | `core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java` DateUtils.parseLocalDateTime (L670–736) | The parseLocalDateTime method (byte array overload) uses a large switch statement based on the length of the input. |
| 11 | OCP-006 | 6 scan(s) | high | `core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java` DateUtils.parseLocalDate (L986–1041) | The parseLocalDate method (char array overload) uses a switch statement based on the length of the input. |
| 12 | OCP-011 | 6 scan(s) | high | `core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java` DateUtils.parseZonedDateTime (L1077–1118) | The parseZonedDateTime method uses a switch statement based on the length of the input. |

## LSP (12 selected)

| # | Issue ID | Confidence | Severity | Location | Description |
|---|----------|-----------:|----------|----------|-------------|
| 1 | LSP-002 | 3 scan(s) | medium | `core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java` DateUtils.parseDate (L170–238) | The parseDate method has multiple overloaded versions and a complex switch statement that handles various date formats, potentially leading to inconsistent behavior or unexpected exceptions for unsupported formats. |
| 2 | LSP-006 | 3 scan(s) | medium | `core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java` DateUtils.parseMillis (L282–290) | The parseMillis method returns milliseconds since epoch, which is a primitive long. While primitive types are immutable, the interpretation of '0' as a null or invalid date might be inconsistent with other parsing methods. |
| 3 | LSP-009 | 3 scan(s) | medium | `core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java` DateUtils.parseLocalDateTime (L408–434) | The parseLocalDateTime method has a large switch statement based on the length of the input, which can lead to unexpected behavior or exceptions if a length is not handled correctly. |
| 4 | LSP-017 | 3 scan(s) | medium | `core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java` DateUtils.parseLocalDate9 (L1375–1429) | The parseLocalDate9 method handles multiple date formats with complex conditional logic, increasing the risk of inconsistent parsing or errors. |
| 5 | LSP-018 | 3 scan(s) | medium | `core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java` DateUtils.parseLocalDate10 (L1445–1478) | The parseLocalDate10 method handles multiple date formats with complex conditional logic, increasing the risk of inconsistent parsing or errors. |
| 6 | LSP-019 | 3 scan(s) | medium | `core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java` DateUtils.parseLocalDate10 (L1480–1513) | The parseLocalDate10 method handles multiple date formats with complex conditional logic, increasing the risk of inconsistent parsing or errors. |
| 7 | LSP-022 | 3 scan(s) | medium | `core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java` DateUtils.parseLocalDateTime12 (L1613–1639) | The parseLocalDateTime12 method parses a specific format ('yyyyMMddHHmm') and has complex validation logic that could lead to unexpected behavior. |
| 8 | LSP-023 | 3 scan(s) | medium | `core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java` DateUtils.parseLocalDateTime12 (L1655–1681) | The parseLocalDateTime12 method parses a specific format ('yyyyMMddHHmm') and has complex validation logic that could lead to unexpected behavior. |
| 9 | LSP-026 | 3 scan(s) | medium | `core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java` DateUtils.parseLocalDateTime16 (L1767–1819) | The parseLocalDateTime16 method handles multiple date/time formats with complex conditional logic, increasing the risk of inconsistent parsing or errors. |
| 10 | LSP-027 | 3 scan(s) | medium | `core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java` DateUtils.parseLocalDateTime16 (L1821–1884) | The parseLocalDateTime16 method handles multiple date/time formats with complex conditional logic, increasing the risk of inconsistent parsing or errors. |
| 11 | LSP-029 | 3 scan(s) | medium | `core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java` DateUtils.parseLocalDateTime17 (L1965–2038) | The parseLocalDateTime17 method handles multiple date/time formats with complex conditional logic, increasing the risk of inconsistent parsing or errors. |
| 12 | LSP-030 | 3 scan(s) | medium | `core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java` DateUtils.parseLocalDateTime18 (L2054–2117) | The parseLocalDateTime18 method handles multiple date/time formats with complex conditional logic, increasing the risk of inconsistent parsing or errors. |

## ISP (8 selected)

| # | Issue ID | Confidence | Severity | Location | Description |
|---|----------|-----------:|----------|----------|-------------|
| 1 | ISP-006 | 6 scan(s) | high | `core/src/main/java/com/alibaba/fastjson2/JSONReader.java` JSONReader (L54–6887) | JSONReader is a fat interface that forces subclasses to implement a massive number of highly specialized methods. |
| 2 | ISP-001 | 6 scan(s) | high | `core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF8.java` JSONReaderUTF8 (L774–1215) | Implementation of a 'Fat Interface' containing dozens of specialized optimization methods. |
| 3 | ISP-002 | 4 scan(s) | high | `core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF16.java` JSONReaderUTF16 (L1500–1950) | Implementation of a 'Fat Interface' containing dozens of specialized optimization methods. |
| 4 | ISP-007 | 3 scan(s) | high | `core/src/main/java/com/alibaba/fastjson2/JSONReaderJSONB.java` JSONReaderJSONB (L25–6303) | JSONReaderJSONB is forced to implement numerous text-specific methods from JSONReader that are not applicable to binary JSON. |
| 5 | ISP-008 | 3 scan(s) | high | `core/src/main/java/com/alibaba/fastjson2/JSONWriter.java` JSONWriter (L68–5055) | JSONWriter is a fat interface that forces implementations to depend on a broad range of unrelated output methods. |
| 6 | ISP-005 | 1 scan(s) | high | `core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF16.java` JSONReaderUTF16 (L16–1450) | JSONReaderUTF16 is forced to implement a bloated contract that includes specialized parsing for non-core JSON types. |
| 7 | ISP-004 | 1 scan(s) | medium | `core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF16.java` JSONReaderUTF16 (L1860–2330) | Inheritance of a fat interface requiring dozens of specialized matching methods. |
| 8 | ISP-003 | 1 scan(s) | medium | `core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF8.java` JSONReaderUTF8 (L1968–2230) | Reader interface is polluted with specific date format parsing methods. |

## DIP (12 selected)

| # | Issue ID | Confidence | Severity | Location | Description |
|---|----------|-----------:|----------|----------|-------------|
| 1 | DIP-002 | 6 scan(s) | medium | `core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF8.java` JSONReaderUTF8.readBigDecimal (L2068–2070) | Direct instantiation of concrete JSONObject class. |
| 2 | DIP-003 | 5 scan(s) | medium | `core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF16.java` JSONReaderUTF16.readBigDecimal (L1011–1013) | Direct instantiation of concrete JSONObject class. |
| 3 | DIP-062 | 4 scan(s) | high | `core/src/main/java/com/alibaba/fastjson2/JSONReader.java` JSONReader.of (L2110–2296) | Static factory methods directly instantiate concrete subclasses of JSONReader. |
| 4 | DIP-001 | 3 scan(s) | high | `core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java` DateUtils.parseMillis (L559–565) | Low-level utility depends on high-level implementation details and concrete reader instances. |
| 5 | DIP-006 | 3 scan(s) | medium | `core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java` DateUtils.parseMillis(char[], int, int, ZoneId) (L435–490) | Directly instantiates and uses a concrete ObjectReader implementation for date parsing. |
| 6 | DIP-077 | 2 scan(s) | high | `core/src/main/java/com/alibaba/fastjson2/JSON.java` JSON.parse / JSON.toJSONString / JSON.toJSONBytes / JSON.writeTo (L121–3834) | The high-level JSON utility class directly depends on concrete factory methods of JSONReader and JSONWriter. |
| 7 | DIP-007 | 2 scan(s) | high | `core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF8.java` JSONReaderUTF8.readString(ValueConsumer, boolean) (L1152–1269) | Directly instantiates a concrete JSONWriter implementation within a JSONReader. |
| 8 | DIP-076 | 2 scan(s) | high | `core/src/main/java/com/alibaba/fastjson2/JSONWriter.java` JSONWriter.of (L925–1153) | The abstract JSONWriter class contains static factory methods that directly instantiate concrete writer implementations. |
| 9 | DIP-004 | 2 scan(s) | high | `core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java` DateUtils.parseMillis (L538–548) | Low-level utility class depends on high-level parsing modules. |
| 10 | DIP-079 | 2 scan(s) | medium | `core/src/main/java/com/alibaba/fastjson2/reader/ObjectReaderCreator.java` ObjectReaderCreator.createObjectReader (L134–3570) | The abstract ObjectReaderCreator class directly instantiates various concrete ObjectReader implementations. |
| 11 | DIP-061 | 2 scan(s) | low | `core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java` DateUtils.parseMillis(char[], int, int, ZoneId) (L614–691) | Direct dependency on a concrete JSON object reader implementation for date parsing. |
| 12 | DIP-078 | 1 scan(s) | high | `core/src/main/java/com/alibaba/fastjson2/JSONB.java` JSONB.parse / JSONB.toBytes / JSONB.writeTo (L418–1932) | The high-level JSONB utility class directly depends on concrete factory methods of JSONReader and JSONWriter for JSONB format. |
