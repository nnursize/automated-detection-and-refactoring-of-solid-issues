# DIP Violation Report: fastjson2

## Summary
- **Total unique issues**: 81
- **High severity**: 20
- **Medium severity**: 60
- **Low severity**: 1
- **Found by multiple scans**: 11/81

## Issues

### DIP-002 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF8.java — JSONReaderUTF8.readBigDecimal
- **Confidence**: Found in 6 scan(s)
- **Lines**: 2068–2070
- **Type**: method
- **Description**: Direct instantiation of concrete JSONObject class.
- **Reasoning**: The method directly instantiates 'new JSONObject()' when encountering an object structure during BigDecimal parsing. This creates a tight coupling to a specific implementation of the Map interface, preventing users from providing custom object containers or using alternative Map implementations through dependency injection or a factory.

### DIP-003 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF16.java — JSONReaderUTF16.readBigDecimal
- **Confidence**: Found in 5 scan(s)
- **Lines**: 1011–1013
- **Type**: method
- **Description**: Direct instantiation of concrete JSONObject class.
- **Reasoning**: Similar to the UTF8 reader, this method hard-codes the dependency on the concrete JSONObject class, violating the principle that high-level parsing logic should depend on abstractions for data containers.

### DIP-062 [HIGH] core/src/main/java/com/alibaba/fastjson2/JSONReader.java — JSONReader.of
- **Confidence**: Found in 4 scan(s)
- **Lines**: 2110–2296
- **Type**: method
- **Description**: Static factory methods directly instantiate concrete subclasses of JSONReader.
- **Reasoning**: The static factory methods `JSONReader.of(...)` and `JSONReader.ofJSONB(...)` directly instantiate concrete implementations like `JSONReaderUTF8`, `JSONReaderUTF16`, `JSONReaderASCII`, and `JSONReaderJSONB`. This means the high-level abstraction `JSONReader` is coupled to its low-level concrete implementations, which is a direct violation of the Dependency Inversion Principle. New concrete implementations cannot be introduced without modifying the `JSONReader` class itself.

### DIP-001 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseMillis
- **Confidence**: Found in 3 scan(s)
- **Lines**: 559–565
- **Type**: method
- **Description**: Low-level utility depends on high-level implementation details and concrete reader instances.
- **Reasoning**: The parseMillis method directly instantiates a JSONReader and references a specific concrete implementation (ObjectReaderImplDate.INSTANCE). Utility classes should provide atomic logic and not depend on the high-level parsing subsystem or specific implementation details of the framework readers.

### DIP-006 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseMillis(char[], int, int, ZoneId)
- **Confidence**: Found in 3 scan(s)
- **Lines**: 435–490
- **Type**: method
- **Description**: Directly instantiates and uses a concrete ObjectReader implementation for date parsing.
- **Reasoning**: Similar to the byte array version, this method in 'DateUtils' directly invokes 'ObjectReaderImplDate.INSTANCE.readObject'. This couples the utility class to a specific concrete implementation of an object reader, violating DIP by depending on a detail rather than an abstraction.

### DIP-004 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseMillis
- **Confidence**: Found in 2 scan(s)
- **Lines**: 538–548
- **Type**: method
- **Description**: Low-level utility class depends on high-level parsing modules.
- **Reasoning**: The parseMillis method in DateUtils (a low-level utility) directly references and instantiates JSONReader and ObjectReaderImplDate. This creates a circular dependency between the utility package and the core parsing logic. According to DIP, low-level utilities should be independent and not depend on high-level implementation details like the JSON parsing engine.

### DIP-007 [HIGH] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF8.java — JSONReaderUTF8.readString(ValueConsumer, boolean)
- **Confidence**: Found in 2 scan(s)
- **Lines**: 1152–1269
- **Type**: method
- **Description**: Directly instantiates a concrete JSONWriter implementation within a JSONReader.
- **Reasoning**: The 'JSONReaderUTF8' class (a low-level module for parsing UTF8 JSON) directly creates an instance of 'JSONWriterUTF8' via 'JSONWriterUTF8.of()' to handle string formatting. This creates an unnecessary and tight coupling between a specific concrete reader implementation and a specific concrete writer implementation. Ideally, the reader should not depend on a concrete writer; if it needs writing capabilities, it should depend on an abstraction (e.g., a 'JSONWriter' interface) or receive it through injection, adhering to the 'details should depend on abstractions' part of DIP. This coupling makes it difficult to change or test the writing mechanism independently.

### DIP-061 [LOW] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseMillis(char[], int, int, ZoneId)
- **Confidence**: Found in 2 scan(s)
- **Lines**: 614–691
- **Type**: method
- **Description**: Direct dependency on a concrete JSON object reader implementation for date parsing.
- **Reasoning**: Similar to the byte-array version, this 'parseMillis' method directly instantiates and uses 'ObjectReaderImplDate.INSTANCE' (a concrete singleton) to parse date strings embedded in JSON. This represents a direct dependency of the 'DateUtils' utility (a detail) on a specific JSON deserialization implementation (another detail) without an abstraction, which is an 'Inappropriate Intimacy' smell and a low-severity DIP violation.

### DIP-076 [HIGH] core/src/main/java/com/alibaba/fastjson2/JSONWriter.java — JSONWriter.of
- **Confidence**: Found in 2 scan(s)
- **Lines**: 925–1153
- **Type**: class
- **Description**: The abstract JSONWriter class contains static factory methods that directly instantiate concrete writer implementations.
- **Reasoning**: Similar to `JSONReader`, the high-level abstraction `JSONWriter` should not depend on low-level concrete implementations like `JSONWriterUTF8`, `JSONWriterUTF16`, `JSONWriterJSONB`, or `JSONWriterPretty`. The factory methods `of(...)` hard-code the choice of concrete types, violating the principle that high-level modules should depend on abstractions, not details. This creates tight coupling and reduces flexibility.

### DIP-077 [HIGH] core/src/main/java/com/alibaba/fastjson2/JSON.java — JSON.parse / JSON.toJSONString / JSON.toJSONBytes / JSON.writeTo
- **Confidence**: Found in 2 scan(s)
- **Lines**: 121–3834
- **Type**: class
- **Description**: The high-level JSON utility class directly depends on concrete factory methods of JSONReader and JSONWriter.
- **Reasoning**: The `JSON` class, serving as a high-level entry point for parsing and serialization, directly calls static factory methods like `JSONReader.of(...)` and `JSONWriter.of(...)`. This creates a direct dependency on the concrete factory implementations, which in turn instantiate concrete reader/writer types. This violates the Dependency Inversion Principle, as a high-level module should depend on abstractions (e.g., an injectable `JSONFactory` interface) rather than concrete low-level details.

### DIP-079 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/reader/ObjectReaderCreator.java — ObjectReaderCreator.createObjectReader
- **Confidence**: Found in 2 scan(s)
- **Lines**: 134–3570
- **Type**: class
- **Description**: The abstract ObjectReaderCreator class directly instantiates various concrete ObjectReader implementations.
- **Reasoning**: An abstract factory class (`ObjectReaderCreator`) should define the interface for creating objects but should not be responsible for directly instantiating concrete implementations (e.g., `ObjectReaderNoneDefaultConstructor`, `ObjectReaderSeeAlso`, `ObjectReaderImplValue`, `ObjectReaderAdapter`, etc.) within its own methods. This responsibility should be delegated to its concrete subclasses (like `ObjectReaderCreatorASM`) or an external factory, ensuring that the abstraction does not depend on details.

### DIP-005 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseMillis(byte[], int, int, Charset, ZoneId)
- **Confidence**: Found in 1 scan(s)
- **Lines**: 387–431
- **Type**: method
- **Description**: Directly instantiates and uses a concrete ObjectReader implementation for date parsing.
- **Reasoning**: The 'DateUtils' utility class, which is a low-level module, directly invokes 'ObjectReaderImplDate.INSTANCE.readObject'. This creates a tight coupling to a specific concrete implementation ('ObjectReaderImplDate') rather than relying on an abstraction (e.g., an 'ObjectReader' interface). This violates the Dependency Inversion Principle, as a detail ('DateUtils') is depending on another concrete detail ('ObjectReaderImplDate'), hindering flexibility and testability.

### DIP-008 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF16.java — JSONReaderUTF16.readBigDecimal()
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1370–1520
- **Type**: method
- **Description**: Directly instantiates concrete JSON data structure classes (JSONObject, implicitly ArrayList).
- **Reasoning**: Similar to 'JSONReaderUTF8', 'JSONReaderUTF16' (a low-level parsing component) directly instantiates 'new JSONObject()' and implicitly relies on 'ArrayList' (returned by 'readArray()') when parsing complex values within 'readBigDecimal'. This tightly couples the reader to specific concrete data structures of the Fastjson2 library, making it less adaptable to alternative data models or custom implementations. This is a violation of the Dependency Inversion Principle, as a detail (the reader) is depending on other concrete details (the specific object/array types).

### DIP-009 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseMillis(byte[], int, int, Charset, ZoneId)
- **Confidence**: Found in 1 scan(s)
- **Lines**: 725–798
- **Type**: method
- **Description**: Directly instantiates and uses a concrete low-level object reader for date parsing.
- **Reasoning**: The `DateUtils.parseMillis` method directly instantiates and uses `ObjectReaderImplDate.INSTANCE`. `ObjectReaderImplDate` is a concrete, low-level implementation detail of how `Date` objects are read within the `fastjson2` framework. A utility class like `DateUtils`, which provides date parsing functionality, should ideally depend on an abstraction (e.g., an `ObjectReader` interface) for such parsing, allowing different implementations to be plugged in without modifying `DateUtils` itself. This violates the Dependency Inversion Principle by depending on a concrete detail rather than an abstraction.

### DIP-010 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseMillis(char[], int, int, ZoneId)
- **Confidence**: Found in 1 scan(s)
- **Lines**: 801–874
- **Type**: method
- **Description**: Directly instantiates and uses a concrete low-level object reader for date parsing.
- **Reasoning**: Similar to its byte array counterpart, the `DateUtils.parseMillis` method directly instantiates and uses `ObjectReaderImplDate.INSTANCE`. This creates a tight coupling to a specific, concrete implementation of date object reading. Adhering to DIP would involve depending on an abstraction for `ObjectReader`, allowing for more flexible and testable date parsing strategies.

### DIP-011 [HIGH] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF8.java — JSONReaderUTF8.readString(ValueConsumer, boolean)
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1022–1130
- **Type**: method
- **Description**: Direct instantiation of a concrete JSONWriter implementation within a JSONReader.
- **Reasoning**: The 'JSONReaderUTF8' class, a low-level module responsible for reading JSON, directly instantiates 'JSONWriterUTF8' via 'JSONWriterUTF8.of()'. This creates a tight coupling between reading and writing concerns. A reader should not directly depend on a concrete writer implementation; instead, it should depend on an abstraction (e.g., an interface) if it needs to interact with a writing component, or the writing logic should be externalized.

### DIP-012 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF8.java — JSONReaderUTF8.readOffsetDateTime()
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1599–1662
- **Type**: method
- **Description**: Direct dependency on concrete utility methods for date/time parsing.
- **Reasoning**: The 'JSONReaderUTF8' class, a low-level JSON parsing module, directly calls numerous static concrete methods from 'DateUtils' (e.g., 'localDateYMD', 'nanos', 'zoneOffset'). This tightly couples the reader's date/time parsing logic to the specific implementation details within 'DateUtils', violating DIP. Ideally, the reader should depend on an abstraction for date/time parsing.

### DIP-013 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF8.java — JSONReaderUTF8.readOffsetTime()
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1664–1725
- **Type**: method
- **Description**: Direct dependency on concrete utility methods for date/time parsing.
- **Reasoning**: The 'JSONReaderUTF8' class directly calls static concrete methods from 'DateUtils' (e.g., 'readNanos'). This tightly couples the reader's date/time parsing logic to the specific implementation details within 'DateUtils', violating DIP. Ideally, the reader should depend on an abstraction for date/time parsing.

### DIP-014 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF8.java — JSONReaderUTF8.readZonedDateTimeX(int)
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1727–1756
- **Type**: method
- **Description**: Direct dependency on concrete utility methods for date/time parsing.
- **Reasoning**: The 'JSONReaderUTF8' class directly calls numerous static concrete methods from 'DateUtils' (e.g., 'parseLocalDateTime29', 'parseZonedDateTime'). This tightly couples the reader's date/time parsing logic to the specific implementation details within 'DateUtils', violating DIP.

### DIP-015 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF8.java — JSONReaderUTF8.readLocalDate8()
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1758–1772
- **Type**: method
- **Description**: Direct dependency on concrete utility methods for date parsing.
- **Reasoning**: The 'JSONReaderUTF8' class directly calls 'DateUtils.parseLocalDate8()'. This creates a tight coupling to the specific implementation details within 'DateUtils', violating DIP.

### DIP-016 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF8.java — JSONReaderUTF8.readLocalDate9()
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1774–1788
- **Type**: method
- **Description**: Direct dependency on concrete utility methods for date parsing.
- **Reasoning**: The 'JSONReaderUTF8' class directly calls 'DateUtils.parseLocalDate9()'. This creates a tight coupling to the specific implementation details within 'DateUtils', violating DIP.

### DIP-017 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF8.java — JSONReaderUTF8.readLocalDate10()
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1790–1802
- **Type**: method
- **Description**: Direct dependency on concrete utility methods for date parsing.
- **Reasoning**: The 'JSONReaderUTF8' class directly calls 'DateUtils.parseLocalDate10()'. This creates a tight coupling to the specific implementation details within 'DateUtils', violating DIP.

### DIP-018 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF8.java — JSONReaderUTF8.readLocalDate11()
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1804–1818
- **Type**: method
- **Description**: Direct dependency on concrete utility methods for date parsing.
- **Reasoning**: The 'JSONReaderUTF8' class directly calls 'DateUtils.parseLocalDate11()'. This creates a tight coupling to the specific implementation details within 'DateUtils', violating DIP.

### DIP-019 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF8.java — JSONReaderUTF8.readLocalDateTime17()
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1820–1834
- **Type**: method
- **Description**: Direct dependency on concrete utility methods for date/time parsing.
- **Reasoning**: The 'JSONReaderUTF8' class directly calls 'DateUtils.parseLocalDateTime17()'. This creates a tight coupling to the specific implementation details within 'DateUtils', violating DIP.

### DIP-020 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF8.java — JSONReaderUTF8.readLocalTime5()
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1836–1850
- **Type**: method
- **Description**: Direct dependency on concrete utility methods for time parsing.
- **Reasoning**: The 'JSONReaderUTF8' class directly calls 'DateUtils.parseLocalTime5()'. This creates a tight coupling to the specific implementation details within 'DateUtils', violating DIP.

### DIP-021 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF8.java — JSONReaderUTF8.readLocalTime6()
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1852–1866
- **Type**: method
- **Description**: Direct dependency on concrete utility methods for time parsing.
- **Reasoning**: The 'JSONReaderUTF8' class directly calls 'DateUtils.parseLocalTime6()'. This creates a tight coupling to the specific implementation details within 'DateUtils', violating DIP.

### DIP-022 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF8.java — JSONReaderUTF8.readLocalTime7()
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1868–1882
- **Type**: method
- **Description**: Direct dependency on concrete utility methods for time parsing.
- **Reasoning**: The 'JSONReaderUTF8' class directly calls 'DateUtils.parseLocalTime7()'. This creates a tight coupling to the specific implementation details within 'DateUtils', violating DIP.

### DIP-023 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF8.java — JSONReaderUTF8.readLocalTime8()
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1884–1898
- **Type**: method
- **Description**: Direct dependency on concrete utility methods for time parsing.
- **Reasoning**: The 'JSONReaderUTF8' class directly calls 'DateUtils.parseLocalTime8()'. This creates a tight coupling to the specific implementation details within 'DateUtils', violating DIP.

### DIP-024 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF8.java — JSONReaderUTF8.readLocalTime9()
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1900–1914
- **Type**: method
- **Description**: Direct dependency on concrete utility methods for time parsing.
- **Reasoning**: The 'JSONReaderUTF8' class directly calls 'DateUtils.parseLocalTime8()'. This creates a tight coupling to the specific implementation details within 'DateUtils', violating DIP.

### DIP-025 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF8.java — JSONReaderUTF8.readLocalTime10()
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1916–1930
- **Type**: method
- **Description**: Direct dependency on concrete utility methods for time parsing.
- **Reasoning**: The 'JSONReaderUTF8' class directly calls 'DateUtils.parseLocalTime10()'. This creates a tight coupling to the specific implementation details within 'DateUtils', violating DIP.

### DIP-026 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF8.java — JSONReaderUTF8.readLocalTime11()
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1932–1946
- **Type**: method
- **Description**: Direct dependency on concrete utility methods for time parsing.
- **Reasoning**: The 'JSONReaderUTF8' class directly calls 'DateUtils.parseLocalTime11()'. This creates a tight coupling to the specific implementation details within 'DateUtils', violating DIP.

### DIP-027 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF8.java — JSONReaderUTF8.readLocalTime12()
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1948–1962
- **Type**: method
- **Description**: Direct dependency on concrete utility methods for time parsing.
- **Reasoning**: The 'JSONReaderUTF8' class directly calls 'DateUtils.parseLocalTime12()'. This creates a tight coupling to the specific implementation details within 'DateUtils', violating DIP.

### DIP-028 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF8.java — JSONReaderUTF8.readLocalTime15()
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1964–1978
- **Type**: method
- **Description**: Direct dependency on concrete utility methods for time parsing.
- **Reasoning**: The 'JSONReaderUTF8' class directly calls 'DateUtils.parseLocalTime15()'. This creates a tight coupling to the specific implementation details within 'DateUtils', violating DIP.

### DIP-029 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF8.java — JSONReaderUTF8.readLocalTime18()
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1980–1994
- **Type**: method
- **Description**: Direct dependency on concrete utility methods for time parsing.
- **Reasoning**: The 'JSONReaderUTF8' class directly calls 'DateUtils.parseLocalTime18()'. This creates a tight coupling to the specific implementation details within 'DateUtils', violating DIP.

### DIP-030 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF8.java — JSONReaderUTF8.readLocalDateTime12()
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1996–2010
- **Type**: method
- **Description**: Direct dependency on concrete utility methods for date/time parsing.
- **Reasoning**: The 'JSONReaderUTF8' class directly calls 'DateUtils.parseLocalDateTime12()'. This creates a tight coupling to the specific implementation details within 'DateUtils', violating DIP.

### DIP-031 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF8.java — JSONReaderUTF8.readLocalDateTime14()
- **Confidence**: Found in 1 scan(s)
- **Lines**: 2012–2026
- **Type**: method
- **Description**: Direct dependency on concrete utility methods for date/time parsing.
- **Reasoning**: The 'JSONReaderUTF8' class directly calls 'DateUtils.parseLocalDateTime14()'. This creates a tight coupling to the specific implementation details within 'DateUtils', violating DIP.

### DIP-032 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF8.java — JSONReaderUTF8.readLocalDateTime16()
- **Confidence**: Found in 1 scan(s)
- **Lines**: 2028–2042
- **Type**: method
- **Description**: Direct dependency on concrete utility methods for date/time parsing.
- **Reasoning**: The 'JSONReaderUTF8' class directly calls 'DateUtils.parseLocalDateTime16()'. This creates a tight coupling to the specific implementation details within 'DateUtils', violating DIP.

### DIP-033 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF8.java — JSONReaderUTF8.readLocalDateTime18()
- **Confidence**: Found in 1 scan(s)
- **Lines**: 2044–2058
- **Type**: method
- **Description**: Direct dependency on concrete utility methods for date/time parsing.
- **Reasoning**: The 'JSONReaderUTF8' class directly calls 'DateUtils.parseLocalDateTime18()'. This creates a tight coupling to the specific implementation details within 'DateUtils', violating DIP.

### DIP-034 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF8.java — JSONReaderUTF8.readLocalDateTime20()
- **Confidence**: Found in 1 scan(s)
- **Lines**: 2076–2090
- **Type**: method
- **Description**: Direct dependency on concrete utility methods for date/time parsing.
- **Reasoning**: The 'JSONReaderUTF8' class directly calls 'DateUtils.parseLocalDateTime20()'. This creates a tight coupling to the specific implementation details within 'DateUtils', violating DIP.

### DIP-035 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF8.java — JSONReaderUTF8.readMillis19()
- **Confidence**: Found in 1 scan(s)
- **Lines**: 2092–2109
- **Type**: method
- **Description**: Direct dependency on concrete utility methods for millisecond parsing.
- **Reasoning**: The 'JSONReaderUTF8' class directly calls 'DateUtils.parseMillis19()'. This creates a tight coupling to the specific implementation details within 'DateUtils', violating DIP.

### DIP-036 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF8.java — JSONReaderUTF8.readLocalDateTimeX(int)
- **Confidence**: Found in 1 scan(s)
- **Lines**: 2111–2134
- **Type**: method
- **Description**: Direct dependency on concrete utility methods for date/time parsing.
- **Reasoning**: The 'JSONReaderUTF8' class directly calls 'DateUtils.parseZonedDateTime()' and 'DateUtils.parseLocalDateTimeX()'. This creates a tight coupling to the specific implementation details within 'DateUtils', violating DIP.

### DIP-037 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF8.java — JSONReaderUTF8.of(byte[], int, int, JSONReader.Context)
- **Confidence**: Found in 1 scan(s)
- **Lines**: 2280–2292
- **Type**: method
- **Description**: Direct instantiation of a concrete JSONReader implementation in a factory method.
- **Reasoning**: The static factory method 'JSONReaderUTF8.of()' makes a decision based on input characteristics (ASCII vs. UTF8) and then directly instantiates 'JSONReaderASCII' (a concrete low-level reader). This violates DIP because the factory, which acts as a high-level component for creating readers, depends on a concrete implementation rather than an abstraction for reader creation or selection.

### DIP-038 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF16.java — JSONReaderUTF16.readLocalDate()
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1591–1634
- **Type**: method
- **Description**: Direct dependency on concrete utility methods for date parsing.
- **Reasoning**: The 'JSONReaderUTF16' class directly calls static concrete methods from 'IOUtils' (e.g., 'digit4', 'digit2'). This tightly couples the reader's date parsing logic to the specific implementation details within 'IOUtils', violating DIP.

### DIP-039 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF16.java — JSONReaderUTF16.readLocalDate0(int, char[], char)
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1636–1658
- **Type**: method
- **Description**: Direct dependency on concrete utility methods for date parsing.
- **Reasoning**: The 'JSONReaderUTF16' class directly calls static concrete methods from 'IOUtils' (e.g., 'indexOfChar', 'digit2') and 'TypeUtils' ('parseInt'). This tightly couples the reader's date parsing logic to the specific implementation details within these utilities, violating DIP.

### DIP-040 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF16.java — JSONReaderUTF16.readOffsetDateTime()
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1660–1738
- **Type**: method
- **Description**: Direct dependency on concrete utility methods for date/time parsing.
- **Reasoning**: The 'JSONReaderUTF16' class directly calls numerous static concrete methods from 'IOUtils' (e.g., 'digit4', 'digit2') and 'DateUtils' (e.g., 'nanos', 'zoneOffset'). This tightly couples the reader's date/time parsing logic to the specific implementation details within these utilities, violating DIP.

### DIP-041 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF16.java — JSONReaderUTF16.readOffsetTime()
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1740–1815
- **Type**: method
- **Description**: Direct dependency on concrete utility methods for time parsing.
- **Reasoning**: The 'JSONReaderUTF16' class directly calls static concrete methods from 'IOUtils' (e.g., 'digit2') and 'DateUtils' (e.g., 'readNanos', 'zoneOffset'). This tightly couples the reader's time parsing logic to the specific implementation details within these utilities, violating DIP.

### DIP-042 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF16.java — JSONReaderUTF16.readZonedDateTimeX(int)
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1817–1846
- **Type**: method
- **Description**: Direct dependency on concrete utility methods for date/time parsing.
- **Reasoning**: The 'JSONReaderUTF16' class directly calls numerous static concrete methods from 'DateUtils' (e.g., 'parseLocalDateTime29', 'parseZonedDateTime'). This tightly couples the reader's date/time parsing logic to the specific implementation details within 'DateUtils', violating DIP.

### DIP-043 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF16.java — JSONReaderUTF16.readLocalDateTime19()
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1848–1862
- **Type**: method
- **Description**: Direct dependency on concrete utility methods for date/time parsing.
- **Reasoning**: The 'JSONReaderUTF16' class directly calls 'DateUtils.parseLocalDateTime19()'. This creates a tight coupling to the specific implementation details within 'DateUtils', violating DIP.

### DIP-044 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF16.java — JSONReaderUTF16.readLocalDateTime20()
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1864–1878
- **Type**: method
- **Description**: Direct dependency on concrete utility methods for date/time parsing.
- **Reasoning**: The 'JSONReaderUTF16' class directly calls 'DateUtils.parseLocalDateTime20()'. This creates a tight coupling to the specific implementation details within 'DateUtils', violating DIP.

### DIP-045 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF16.java — JSONReaderUTF16.readMillis19()
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1880–1897
- **Type**: method
- **Description**: Direct dependency on concrete utility methods for millisecond parsing.
- **Reasoning**: The 'JSONReaderUTF16' class directly calls 'DateUtils.parseMillis19()'. This creates a tight coupling to the specific implementation details within 'DateUtils', violating DIP.

### DIP-046 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF16.java — JSONReaderUTF16.readLocalDateTimeX(int)
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1902–1925
- **Type**: method
- **Description**: Direct dependency on concrete utility methods for date/time parsing.
- **Reasoning**: The 'JSONReaderUTF16' class directly calls 'DateUtils.parseZonedDateTime()' and 'DateUtils.parseLocalDateTimeX()'. This creates a tight coupling to the specific implementation details within 'DateUtils', violating DIP.

### DIP-047 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF16.java — JSONReaderUTF16.readLocalTime10()
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1927–1941
- **Type**: method
- **Description**: Direct dependency on concrete utility methods for time parsing.
- **Reasoning**: The 'JSONReaderUTF16' class directly calls 'DateUtils.parseLocalTime10()'. This creates a tight coupling to the specific implementation details within 'DateUtils', violating DIP.

### DIP-048 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF16.java — JSONReaderUTF16.readLocalTime11()
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1943–1957
- **Type**: method
- **Description**: Direct dependency on concrete utility methods for time parsing.
- **Reasoning**: The 'JSONReaderUTF16' class directly calls 'DateUtils.parseLocalTime11()'. This creates a tight coupling to the specific implementation details within 'DateUtils', violating DIP.

### DIP-049 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF16.java — JSONReaderUTF16.readLocalTime12()
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1959–1973
- **Type**: method
- **Description**: Direct dependency on concrete utility methods for time parsing.
- **Reasoning**: The 'JSONReaderUTF16' class directly calls 'DateUtils.parseLocalTime12()'. This creates a tight coupling to the specific implementation details within 'DateUtils', violating DIP.

### DIP-050 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF16.java — JSONReaderUTF16.readLocalTime15()
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1975–1989
- **Type**: method
- **Description**: Direct dependency on concrete utility methods for time parsing.
- **Reasoning**: The 'JSONReaderUTF16' class directly calls 'DateUtils.parseLocalTime15()'. This creates a tight coupling to the specific implementation details within 'DateUtils', violating DIP.

### DIP-051 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF16.java — JSONReaderUTF16.readLocalTime18()
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1991–2005
- **Type**: method
- **Description**: Direct dependency on concrete utility methods for time parsing.
- **Reasoning**: The 'JSONReaderUTF16' class directly calls 'DateUtils.parseLocalTime18()'. This creates a tight coupling to the specific implementation details within 'DateUtils', violating DIP.

### DIP-052 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF16.java — JSONReaderUTF16.readLocalDate8()
- **Confidence**: Found in 1 scan(s)
- **Lines**: 2011–2025
- **Type**: method
- **Description**: Direct dependency on concrete utility methods for date parsing.
- **Reasoning**: The 'JSONReaderUTF16' class directly calls 'DateUtils.parseLocalDate8()'. This creates a tight coupling to the specific implementation details within 'DateUtils', violating DIP.

### DIP-053 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF16.java — JSONReaderUTF16.readLocalDate9()
- **Confidence**: Found in 1 scan(s)
- **Lines**: 2027–2041
- **Type**: method
- **Description**: Direct dependency on concrete utility methods for date parsing.
- **Reasoning**: The 'JSONReaderUTF16' class directly calls 'DateUtils.parseLocalDate9()'. This creates a tight coupling to the specific implementation details within 'DateUtils', violating DIP.

### DIP-054 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF16.java — JSONReaderUTF16.readLocalDate10()
- **Confidence**: Found in 1 scan(s)
- **Lines**: 2043–2057
- **Type**: method
- **Description**: Direct dependency on concrete utility methods for date parsing.
- **Reasoning**: The 'JSONReaderUTF16' class directly calls 'DateUtils.parseLocalDate10()'. This creates a tight coupling to the specific implementation details within 'DateUtils', violating DIP.

### DIP-055 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF16.java — JSONReaderUTF16.readLocalDate11()
- **Confidence**: Found in 1 scan(s)
- **Lines**: 2059–2073
- **Type**: method
- **Description**: Direct dependency on concrete utility methods for date parsing.
- **Reasoning**: The 'JSONReaderUTF16' class directly calls 'DateUtils.parseLocalDate11()'. This creates a tight coupling to the specific implementation details within 'DateUtils', violating DIP.

### DIP-056 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF16.java — JSONReaderUTF16.readLocalDateTime14()
- **Confidence**: Found in 1 scan(s)
- **Lines**: 2075–2089
- **Type**: method
- **Description**: Direct dependency on concrete utility methods for date/time parsing.
- **Reasoning**: The 'JSONReaderUTF16' class directly calls 'DateUtils.parseLocalDateTime14()'. This creates a tight coupling to the specific implementation details within 'DateUtils', violating DIP.

### DIP-057 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF16.java — JSONReaderUTF16.readLocalDateTime12()
- **Confidence**: Found in 1 scan(s)
- **Lines**: 2091–2105
- **Type**: method
- **Description**: Direct dependency on concrete utility methods for date/time parsing.
- **Reasoning**: The 'JSONReaderUTF16' class directly calls 'DateUtils.parseLocalDateTime12()'. This creates a tight coupling to the specific implementation details within 'DateUtils', violating DIP.

### DIP-058 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF16.java — JSONReaderUTF16.readLocalDateTime16()
- **Confidence**: Found in 1 scan(s)
- **Lines**: 2107–2121
- **Type**: method
- **Description**: Direct dependency on concrete utility methods for date/time parsing.
- **Reasoning**: The 'JSONReaderUTF16' class directly calls 'DateUtils.parseLocalDateTime16()'. This creates a tight coupling to the specific implementation details within 'DateUtils', violating DIP.

### DIP-059 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF16.java — JSONReaderUTF16.readLocalDateTime17()
- **Confidence**: Found in 1 scan(s)
- **Lines**: 2123–2137
- **Type**: method
- **Description**: Direct dependency on concrete utility methods for date/time parsing.
- **Reasoning**: The 'JSONReaderUTF16' class directly calls 'DateUtils.parseLocalDateTime17()'. This creates a tight coupling to the specific implementation details within 'DateUtils', violating DIP.

### DIP-060 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF16.java — JSONReaderUTF16.readLocalDateTime18()
- **Confidence**: Found in 1 scan(s)
- **Lines**: 2139–2153
- **Type**: method
- **Description**: Direct dependency on concrete utility methods for date/time parsing.
- **Reasoning**: The 'JSONReaderUTF16' class directly calls 'DateUtils.parseLocalDateTime18()'. This creates a tight coupling to the specific implementation details within 'DateUtils', violating DIP.

### DIP-063 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReader.java — JSONReader.readObject
- **Confidence**: Found in 1 scan(s)
- **Lines**: 2577–2724
- **Type**: method
- **Description**: Falls back to direct instantiation of concrete collection types (HashMap, JSONObject, ArrayList, JSONArray) if no supplier is provided.
- **Reasoning**: The `readObject()` and `readArray()` methods, which are part of the high-level `JSONReader` abstraction, directly instantiate concrete collection types (`new HashMap()`, `new JSONObject()`, `new ArrayList()`, `new JSONArray()`) if custom suppliers (`context.objectSupplier`, `context.arraySupplier`) are not provided. While dependency injection is supported via suppliers, the fallback to concrete types creates a hard-coded dependency on low-level implementations, violating DIP.

### DIP-064 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReader.java — JSONReader.readMillisFromString
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1850–2095
- **Type**: method
- **Description**: Directly instantiates SimpleDateFormat when a specific date format is used and DateTimeFormatter is not configured.
- **Reasoning**: The `readMillisFromString()` method, a high-level parsing logic, directly instantiates `java.text.SimpleDateFormat` if the `context.dateFormat` is set to a pattern that doesn't match predefined fast paths and `DateTimeFormatter` is not already configured. This couples the `JSONReader` to a concrete, low-level date formatting utility, violating DIP. Ideally, it should rely solely on an abstraction (like `DateTimeFormatter` or a custom interface) provided through configuration.

### DIP-065 [HIGH] core/src/main/java/com/alibaba/fastjson2/JSONReader.java — JSONReader.of
- **Confidence**: Found in 1 scan(s)
- **Lines**: 2399–2600
- **Type**: method
- **Description**: Abstract class contains static factory methods that directly instantiate its concrete implementations.
- **Reasoning**: The `JSONReader` is an abstract class designed to serve as a high-level abstraction for reading JSON. However, it contains static factory methods (e.g., `of(byte[]...)`, `of(char[]...)`, `of(String...)`, `ofJSONB(...)`) that directly instantiate its concrete, low-level implementations such as `JSONReaderUTF8`, `JSONReaderUTF16`, `JSONReaderASCII`, and `JSONReaderJSONB`. This is a fundamental violation of the Dependency Inversion Principle, which states that high-level modules should not depend on low-level modules; both should depend on abstractions. By directly creating concrete instances, the `JSONReader` abstraction is coupled to its implementation details, reducing flexibility and making it harder to introduce new implementations or mock them for testing without modifying the abstraction itself. A separate, external factory or a dependency injection mechanism would be more appropriate for managing the creation of concrete `JSONReader` instances.

### DIP-066 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.parseMillis
- **Confidence**: Found in 1 scan(s)
- **Lines**: 579–643
- **Type**: method
- **Description**: Directly instantiates JSONReader and depends on a concrete ObjectReader implementation for date parsing.
- **Reasoning**: The 'parseMillis' method directly calls `JSONReader.of()` which, despite being a factory, returns a concrete implementation of `JSONReader` (a low-level detail). More critically, it directly accesses `ObjectReaderImplDate.INSTANCE.readObject()`, tying this high-level date utility to a specific, concrete JSON object reader. This violates DIP by having the high-level module (general date utility) depend on low-level concrete JSON parsing details rather than abstractions.

### DIP-067 [HIGH] core/src/main/java/com/alibaba/fastjson2/JSONReader.java — JSONReader.of
- **Confidence**: Found in 1 scan(s)
- **Lines**: 3317–3328
- **Type**: method
- **Description**: The static factory method directly instantiates a concrete subclass, 'JSONReaderUTF8'.
- **Reasoning**: The abstract `JSONReader` class's static factory method `of()` directly creates and returns an instance of `JSONReaderUTF8`. This means the high-level abstraction (`JSONReader`) depends on its low-level concrete implementation (`JSONReaderUTF8`), which is a direct violation of the Dependency Inversion Principle. Changes to concrete implementations will necessitate changes in the abstract factory method.

### DIP-068 [HIGH] core/src/main/java/com/alibaba/fastjson2/JSONReader.java — JSONReader.of
- **Confidence**: Found in 1 scan(s)
- **Lines**: 3335–3342
- **Type**: method
- **Description**: The static factory method directly instantiates a concrete subclass, 'JSONReaderUTF16'.
- **Reasoning**: The abstract `JSONReader` class's static factory method `of()` directly creates and returns an instance of `JSONReaderUTF16` (via `ofUTF16`). This means the high-level abstraction (`JSONReader`) depends on its low-level concrete implementation (`JSONReaderUTF16`), which is a direct violation of the Dependency Inversion Principle. Changes to concrete implementations will necessitate changes in the abstract factory method.

### DIP-069 [HIGH] core/src/main/java/com/alibaba/fastjson2/JSONReader.java — JSONReader.ofJSONB
- **Confidence**: Found in 1 scan(s)
- **Lines**: 3350–3356
- **Type**: method
- **Description**: The static factory method directly instantiates a concrete subclass, 'JSONReaderJSONB'.
- **Reasoning**: The abstract `JSONReader` class's static factory method `ofJSONB()` directly creates and returns an instance of `JSONReaderJSONB`. This means the high-level abstraction (`JSONReader`) depends on its low-level concrete implementation (`JSONReaderJSONB`), which is a direct violation of the Dependency Inversion Principle. Changes to concrete implementations will necessitate changes in the abstract factory method.

### DIP-070 [HIGH] core/src/main/java/com/alibaba/fastjson2/JSONReader.java — JSONReader.of
- **Confidence**: Found in 1 scan(s)
- **Lines**: 3381–3400
- **Type**: method
- **Description**: The static factory method directly instantiates various concrete subclasses based on charset.
- **Reasoning**: The abstract `JSONReader` class's static factory method `of()` contains logic to create different concrete `JSONReader` implementations (`JSONReaderUTF8`, `JSONReaderUTF16`, `JSONReaderASCII`) based on the provided `Charset`. This makes the high-level `JSONReader` abstraction directly dependent on multiple low-level concrete implementations and their specific factory/constructor calls, violating the Dependency Inversion Principle.

### DIP-071 [HIGH] core/src/main/java/com/alibaba/fastjson2/JSONReader.java — JSONReader.of
- **Confidence**: Found in 1 scan(s)
- **Lines**: 3442–3462
- **Type**: method
- **Description**: The static factory method directly instantiates various concrete subclasses based on charset for InputStream.
- **Reasoning**: The abstract `JSONReader` class's static factory method `of()` for `InputStream` directly creates and returns instances of concrete `JSONReader` implementations (`JSONReaderUTF8`, `JSONReaderUTF16`, `JSONReaderASCII`). This tightly couples the abstract class to its concrete details, violating DIP.

### DIP-072 [HIGH] core/src/main/java/com/alibaba/fastjson2/JSONReader.java — JSONReader.of
- **Confidence**: Found in 1 scan(s)
- **Lines**: 3469–3474
- **Type**: method
- **Description**: The static factory method directly instantiates a concrete subclass, 'JSONReaderUTF16'.
- **Reasoning**: The abstract `JSONReader` class's static factory method `of()` for `Reader` directly creates and returns an instance of `JSONReaderUTF16`. This tightly couples the abstract class to its concrete implementation, violating DIP.

### DIP-073 [HIGH] core/src/main/java/com/alibaba/fastjson2/JSONReader.java — JSONReader.of
- **Confidence**: Found in 1 scan(s)
- **Lines**: 3491–3495
- **Type**: method
- **Description**: The static factory method directly instantiates a concrete subclass, 'JSONReaderUTF8'.
- **Reasoning**: The abstract `JSONReader` class's static factory method `of()` for `ByteBuffer` directly creates and returns an instance of `JSONReaderUTF8`. This tightly couples the abstract class to its concrete implementation, violating DIP.

### DIP-074 [HIGH] core/src/main/java/com/alibaba/fastjson2/JSONReader.java — JSONReader.of
- **Confidence**: Found in 1 scan(s)
- **Lines**: 3508–3527
- **Type**: method
- **Description**: The static factory method directly instantiates concrete subclasses, 'JSONReaderASCII' or 'JSONReaderUTF16', based on string encoding.
- **Reasoning**: The abstract `JSONReader` class's static factory method `of()` for `String` directly creates and returns instances of concrete `JSONReader` implementations (`JSONReaderASCII`, `JSONReaderUTF16`) based on internal string encoding checks. This makes the high-level abstraction `JSONReader` dependent on low-level concrete implementations, violating DIP.

### DIP-075 [HIGH] core/src/main/java/com/alibaba/fastjson2/JSONReader.java — JSONReader.of
- **Confidence**: Found in 1 scan(s)
- **Lines**: 3538–3557
- **Type**: method
- **Description**: The static factory method directly instantiates concrete subclasses, 'JSONReaderASCII' or 'JSONReaderUTF16', based on string encoding for substrings.
- **Reasoning**: Similar to the `JSONReader.of(String)` method, this factory method for substrings also directly creates concrete `JSONReader` implementations. This maintains the violation of DIP where the abstract `JSONReader` depends on its concrete subclasses.

### DIP-078 [HIGH] core/src/main/java/com/alibaba/fastjson2/JSONB.java — JSONB.parse / JSONB.toBytes / JSONB.writeTo
- **Confidence**: Found in 1 scan(s)
- **Lines**: 418–1932
- **Type**: class
- **Description**: The high-level JSONB utility class directly depends on concrete factory methods of JSONReader and JSONWriter for JSONB format.
- **Reasoning**: Similar to the `JSON` class, the `JSONB` utility class directly calls static factory methods like `JSONReader.ofJSONB(...)` and `JSONWriter.ofJSONB(...)`. This creates a direct dependency on the concrete factory implementations for JSONB, which instantiate concrete reader/writer types. This violates the Dependency Inversion Principle, as a high-level module should depend on abstractions rather than concrete low-level details.

### DIP-080 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReader.java — JSONReader.of
- **Confidence**: Found in 1 scan(s)
- **Lines**: 4646–4961
- **Type**: method
- **Description**: Static factory methods in abstract JSONReader directly instantiate concrete implementations.
- **Reasoning**: The abstract `JSONReader` class contains static factory methods (`of(...)`) that directly instantiate its concrete implementations (`JSONReaderUTF8`, `JSONReaderUTF16`, `JSONReaderJSONB`). This means the abstraction is aware of and directly depends on its concrete details, violating DIP. Ideally, the creation of concrete implementations should be externalized (e.g., to a separate factory class or an Inversion of Control container) to maintain the separation of concerns.

### DIP-081 [HIGH] core/src/main/java/com/alibaba/fastjson2/JSONReaderJSONB.java — JSONReaderJSONB
- **Confidence**: Found in 1 scan(s)
- **Lines**: 25–6303
- **Type**: class
- **Description**: High-level module `JSONReaderJSONB` directly depends on the concrete low-level utility `DateUtils`.
- **Reasoning**: `JSONReaderJSONB`, a concrete implementation of the `JSONReader` abstraction (a high-level module for parsing JSON), directly imports and utilizes static methods from the concrete utility class `DateUtils`. This violates DIP as high-level modules should depend on abstractions, not concrete low-level implementations.
