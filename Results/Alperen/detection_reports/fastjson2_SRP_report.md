# SRP Violation Report: fastjson2

## Summary
- **Total unique issues**: 21
- **High severity**: 12
- **Medium severity**: 7
- **Low severity**: 2
- **Found by multiple scans**: 10/21

## Issues

### SRP-001 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils
- **Confidence**: Found in 10 scan(s)
- **Lines**: 47–2130
- **Type**: class
- **Description**: DateUtils acts as a God Class for all date-related operations, mixing high-level logic with low-level infrastructure concerns.
- **Reasoning**: The class encapsulates at least four distinct responsibilities: 1) High-level date parsing and formatting logic for multiple standards (ISO, RFC, etc.), 2) Low-level memory management and performance optimization using 'Unsafe' to read raw bytes/shorts/longs (e.g., methods like 'hms' and 'localDateYMD'), 3) Timezone database management, including hardcoded historical offset tables for specific regions like Shanghai, and 4) Internal caching mechanisms for formatted strings (CacheDate8/10). A change in performance requirements, timezone laws, or supported date formats would all require modifying this single class.

### SRP-002 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF8.java — JSONReaderUTF8
- **Confidence**: Found in 6 scan(s)
- **Lines**: 21–2100
- **Type**: class
- **Description**: Mixes JSON structural tokenization with specific business type parsing logic.
- **Reasoning**: The class is responsible for structural JSON parsing (handling braces, brackets, commas) but also contains specialized logic for parsing complex types like UUID (readUUID), BigDecimal (readBigDecimal), and various Date types. According to SRP, the reader should focus on JSON grammar, while the logic for interpreting specific data types should be delegated to separate TypeReaders or ValueConsumers. This mixing makes the class extremely large and difficult to maintain.

### SRP-010 [HIGH] core/src/main/java/com/alibaba/fastjson2/JSONReader.java — JSONReader
- **Confidence**: Found in 6 scan(s)
- **Lines**: 54–6887
- **Type**: class
- **Description**: The class acts as a 'God Class' by combining multiple distinct responsibilities: low-level JSON tokenization, high-level JSON structure navigation, type-specific deserialization, complex numeric parsing/coercion, polymorphic deserialization, reference resolution, configuration management, and factory creation.
- **Reasoning**: The `JSONReader` class is responsible for too many unrelated concerns. It handles the fundamental task of reading JSON tokens (lexer/parser), but also includes extensive logic for converting these tokens into various Java types (deserializer), managing complex numeric representations (arbitrary-precision number handler), resolving object references, and dynamically loading classes for polymorphic types (auto-type handler). Each of these areas represents a distinct reason for the class to change. For instance, a change in JSON tokenization rules, a new date format, an update to numeric precision handling, or a modification to auto-type security would all necessitate changes to this single class, indicating a severe violation of SRP.

### SRP-006 [HIGH] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF16.java — JSONReaderUTF16
- **Confidence**: Found in 4 scan(s)
- **Lines**: 20–2070
- **Type**: class
- **Description**: The class mixes JSON lexical analysis, syntactic parsing, and direct Java type conversion for numerous data types, mirroring JSONReaderUTF8.
- **Reasoning**: This class exhibits the same SRP violations as `JSONReaderUTF8`, but for UTF-16 character input. It is responsible for: (1) tokenizing JSON input (lexical analysis), (2) parsing JSON structure (syntactic analysis), (3) handling character-level escape sequences, (4) performing Java type conversion from JSON tokens (e.g., `readInt32Value()`, `readDoubleValue()`, `readLocalDate()`, `readUUID()`, `readBigDecimal()`), and (5) managing caching and resource management. This conflates multiple responsibilities, making it a 'God class'. Changes in JSON format, character encoding, or Java type conversion logic would all require modifications to this single class.

### SRP-011 [HIGH] core/src/main/java/com/alibaba/fastjson2/JSONWriter.java — JSONWriter
- **Confidence**: Found in 3 scan(s)
- **Lines**: 68–5055
- **Type**: class
- **Description**: Fat interface defining excessive abstract methods for all JSON writing operations and data types.
- **Reasoning**: Similar to `JSONReader`, the `JSONWriter` abstract class defines a huge number of abstract methods for token writing, raw value writing, and type-specific serialization (primitives, wrappers, dates, times, UUIDs, BigDecimals, arrays, etc.). This forces concrete implementations to be 'god writers' and leads to `UnsupportedOperationException` for methods not applicable to a specific format (e.g., JSONB). This violates SRP by having too many reasons to change and forcing clients to implement methods they don't need.

### SRP-012 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/TypeUtils.java — TypeUtils
- **Confidence**: Found in 3 scan(s)
- **Lines**: 29–3878
- **Type**: class
- **Description**: God class combining unrelated utility functions for type conversion, reflection, number parsing, and validation.
- **Reasoning**: The `TypeUtils` class is a classic 'God Object' that aggregates a wide array of disparate responsibilities. It handles proxy creation, string/byte array conversions, type interning, number parsing (double, float, int, long, BigDecimal), type casting, type mapping/resolution, type comparison, reflection utilities (generic types, annotations), and various validation methods (isInteger, isNumber, isUUID, validateIPv4/IPv6). This class has numerous reasons to change, violating SRP. It should be decomposed into several smaller, more focused utility classes.

### SRP-013 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/IOUtils.java — IOUtils
- **Confidence**: Found in 2 scan(s)
- **Lines**: 32–3110
- **Type**: class
- **Description**: God class combining low-level I/O, number formatting, encoding, and byte/char array manipulation.
- **Reasoning**: The `IOUtils` class is another severe 'God Object' violation. It mixes responsibilities for digit/number formatting (e.g., `writeDigitPair`, `getChars`, `writeDecimal`, `writeIntX`), UTF-8 encoding/decoding, basic file/stream operations (`close`, `lines`), date/time formatting into buffers (`writeLocalDate`, `writeLocalTime`, `writeNano`), and extensive low-level byte/char array manipulation (put/get primitives, unaligned operations, searching, validation). This class has many unrelated reasons to change and should be broken down into more cohesive utility classes.

### SRP-015 [HIGH] core/src/main/java/com/alibaba/fastjson2/writer/ObjectWriterCreatorASM.java — ObjectWriterCreatorASM
- **Confidence**: Found in 2 scan(s)
- **Lines**: 29–5305
- **Type**: class
- **Description**: God class responsible for generating bytecode for all ObjectWriter serialization logic.
- **Reasoning**: This class is a 'god generator' for `ObjectWriter` bytecode. It contains an immense amount of logic for generating serialization code for virtually every possible Java type and serialization strategy (JSON, JSONB, array mapping, direct field access, null handling, date/time, collections, objects, enums, primitives, numbers, type info, references, filters, field names, field values, different field lengths/types). This single class has too many reasons to change, as any change in serialization logic for any type or format would require modification here, violating SRP.

### SRP-016 [HIGH] core/src/main/java/com/alibaba/fastjson2/reader/ObjectReaderCreatorASM.java — ObjectReaderCreatorASM
- **Confidence**: Found in 2 scan(s)
- **Lines**: 31–4626
- **Type**: class
- **Description**: God class responsible for generating bytecode for all ObjectReader deserialization logic.
- **Reasoning**: Similar to `ObjectWriterCreatorASM`, this class is a 'god generator' for `ObjectReader` bytecode. It handles the generation of deserialization logic for various constructors, builder patterns, field types, JSON/JSONB formats, auto-type mechanisms, field name matching, value parsing, error handling, and more. This class has too many distinct responsibilities, making it highly susceptible to changes and difficult to maintain, which is a clear violation of SRP.

### SRP-019 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONB.java — JSONB
- **Confidence**: Found in 2 scan(s)
- **Lines**: 128–3209
- **Type**: class
- **Description**: The JSONB utility class mixes high-level JSONB parsing/serialization with very low-level binary encoding/decoding primitives.
- **Reasoning**: This class provides high-level API entry points for JSONB serialization and deserialization (parse, toBytes, writeTo). However, it also exposes and implements numerous extremely low-level binary encoding and decoding primitives (e.g., toBytes(boolean), toBytes(int), writeEnum, writeBoolean, writeFloat, writeDouble, writeInt8, writeInt16, writeInt32, writeSymbol, writeUUID, writeInstant, writeLocalDate, stringCapacity, putStringSizeSmall/Large). These low-level details should be encapsulated within the specific JSONReaderJSONB and JSONWriterJSONB implementations or dedicated internal binary codec utilities, not exposed directly in a top-level facade, violating separation of concerns.

### SRP-003 [LOW] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — getShanghaiZoneOffsetTotalSeconds
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1932–1994
- **Type**: method
- **Description**: Encapsulates specific, historical time zone rules for a single region within a general date utility class.
- **Reasoning**: While time zone handling is related to dates, implementing a detailed historical rule set for a specific time zone (Shanghai) is a very specialized responsibility. This logic could ideally reside in a dedicated time zone rule provider or a more abstract mechanism, rather than being hardcoded in a general-purpose `DateUtils`.

### SRP-004 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF8.java — readString
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1269–1403
- **Type**: method
- **Description**: The method is responsible for reading a string, handling escape sequences, UTF-8 decoding, and applying string post-processing features like trimming and null-on-empty.
- **Reasoning**: The `readString` method not only reads the raw string content and handles escape sequences and multi-byte UTF-8 characters but also applies `MASK_TRIM_STRING` and `MASK_EMPTY_STRING_AS_NULL` features. These post-processing/business logic concerns are distinct from the primary responsibility of correctly parsing the raw string value as defined by JSON. This could be delegated to a separate string processor.

### SRP-005 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF8.java — readNumber0
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1420–1618
- **Type**: method
- **Description**: The method combines numeric parsing logic with handling of special values (null, true, false, NaN) and complex JSON objects/arrays.
- **Reasoning**: While its primary role is to parse numbers, `readNumber0` also contains logic to detect and handle `null`, `true`, `false`, `NaN`, and even recursively calls `readObject()` or `readArray()` if the token is an object or array. This extends its responsibility beyond mere numeric parsing, intertwining it with boolean parsing, null handling, and structural parsing of complex types, blurring its single responsibility.

### SRP-007 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF16.java — readString
- **Confidence**: Found in 1 scan(s)
- **Lines**: 986–1083
- **Type**: method
- **Description**: The method is responsible for reading a string, handling escape sequences, and applying string post-processing features like trimming and null-on-empty.
- **Reasoning**: Similar to `JSONReaderUTF8.readString`, this method handles the raw parsing of string content, escape sequences, and then applies `MASK_TRIM_STRING` and `MASK_EMPTY_STRING_AS_NULL` features. These post-processing/business logic concerns are distinct from the core responsibility of correctly parsing the raw string value as defined by JSON. This could be delegated to a separate string processor.

### SRP-008 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF16.java — readNumber0
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1541–1730
- **Type**: method
- **Description**: The method combines numeric parsing logic with handling of special values (null, true, false, NaN) and complex JSON objects/arrays.
- **Reasoning**: Similar to `JSONReaderUTF8.readNumber0`, this method, intended for parsing numbers, also contains logic to detect and handle `null`, `true`, `false`, `NaN`, and recursively calls `readObject()` or `readArray()` if the token is an object or array. This extends its responsibility beyond mere numeric parsing, intertwining it with boolean parsing, null handling, and structural parsing of complex types, blurring its single responsibility.

### SRP-009 [LOW] core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java — DateUtils.getShanghaiZoneOffsetTotalSeconds
- **Confidence**: Found in 1 scan(s)
- **Lines**: 9109–9208
- **Type**: method
- **Description**: The method contains extensive hardcoded historical time zone offset rules specific to the Shanghai time zone.
- **Reasoning**: The responsibility of managing and providing historical time zone offset data for a specific region (Shanghai) is a specialized data management and rule-based logic. This is distinct from the general utility of parsing and formatting dates. If China's time zone rules change again, or if similar historical data for other regions needs to be supported, this method would require modification, representing a separate reason to change from the core date/time manipulation logic.

### SRP-014 [HIGH] core/src/main/java/com/alibaba/fastjson2/reader/ObjectReaderCreator.java — ObjectReaderCreator
- **Confidence**: Found in 1 scan(s)
- **Lines**: 101–4094
- **Type**: class
- **Description**: God class responsible for creating all types of ObjectReader and FieldReader instances under various conditions.
- **Reasoning**: This class is responsible for creating `ObjectReader` and `FieldReader` instances, but it contains an overwhelming number of overloaded `createObjectReader` and `createFieldReader` methods. These methods handle different creation strategies (constructors, factory methods, builders, 'see also' types), various configurations (features, formats, locales, default values, schemas), and different member types (fields, methods, parameters). This indicates it's performing too much analysis and creation logic itself, rather than delegating to more specialized factories or builders, violating SRP.

### SRP-017 [HIGH] core/src/main/java/com/alibaba/fastjson2/introspect/PropertyAccessorFactory.java — PropertyAccessorFactory
- **Confidence**: Found in 1 scan(s)
- **Lines**: 35–5114
- **Type**: class
- **Description**: The PropertyAccessorFactory class acts as a factory but also contains numerous concrete implementations for various property accessors.
- **Reasoning**: While its primary role is to create PropertyAccessor instances, this class directly houses dozens of concrete PropertyAccessor implementations (e.g., FieldAccessorReflectBooleanValue, MethodAccessorCharValue, FunctionAccessorByteValue, PropertyAccessorWrapperBooleanValue) for different data types and access patterns (fields, methods, functional interfaces, wrappers). It also includes factories for constructor functions and accessor decorators. This violates SRP by combining the factory responsibility with the responsibility of *implementing* the products it creates, leading to a massive and highly coupled class with many reasons to change.

### SRP-018 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSON.java — JSON
- **Confidence**: Found in 1 scan(s)
- **Lines**: 121–4643
- **Type**: class
- **Description**: The JSON utility class serves as a God facade, combining parsing, serialization, validation, and global configuration responsibilities.
- **Reasoning**: This class, acting as the main entry point for the Fastjson2 library, aggregates a wide range of functionalities: comprehensive parsing methods (parse, parseObject, parseArray), serialization methods (toJSONString, toJSONBytes, writeTo), utility/conversion methods (isValid, toJSON, toJavaObject), and global configuration/registration methods (mixIn, register, config, isEnabled, configReaderDateFormat, etc.). While a facade often aggregates, the inclusion of global configuration and validation logic alongside core parsing/serialization makes it overly broad and gives it too many reasons to change.

### SRP-020 [HIGH] core/src/main/java/com/alibaba/fastjson2/JSONReaderJSONB.java — JSONReaderJSONB
- **Confidence**: Found in 1 scan(s)
- **Lines**: 25–6303
- **Type**: class
- **Description**: Class handles reading and parsing of JSONB data, involving low-level byte processing and high-level type conversions.
- **Reasoning**: The `JSONReaderJSONB` class is responsible for parsing the JSONB binary format. This includes reading from `InputStream` and `byte[]`, handling various JSONB data types and structures (e.g., `readLength`, `readTimestampWithTimeZone`, `readLocalTime`, `readLocalDateTime`, `readZonedDateTime`, `readUUID`, `readBigInteger`, `readBigDecimal`), and managing internal state like `offset` and `type`. The extensive range of parsing methods for different data types and formats, combined with the low-level byte processing specific to JSONB, indicates a violation of SRP.

### SRP-021 [HIGH] core/src/main/java/com/alibaba/fastjson2/util/BeanUtils.java — BeanUtils
- **Confidence**: Found in 1 scan(s)
- **Lines**: 31–3175
- **Type**: class
- **Description**: Class provides utility methods for introspection of Java Beans, including finding fields, methods, constructors, and applying naming strategies and annotations.
- **Reasoning**: The `BeanUtils` class offers a wide range of functionalities related to introspection and metadata processing. It includes methods for finding fields (`fields`, `declaredFields`), methods (`getMethod`, `getSetter`, `getters`, `setters`, `annotationMethods`), constructors (`constructor`, `getDefaultConstructor`), and handling naming strategies (`setterName`, `getterName`, `fieldName`). Additionally, it processes annotations (`processJacksonJsonFormat`, `processGsonSerializedName`, `processJacksonJsonInclude`, `processJacksonJsonUnwrapped`, `processJacksonJsonTypeName`, `processJacksonJsonSubTypesType`) and manages type resolution (`resolveCollectionItemType`, `getGenericSupertype`, `resolve`, `findAnnotation`). This broad set of responsibilities, spanning reflection, annotation processing, and naming strategy application, suggests that the class is doing too many things and could be broken down into smaller, more focused utilities.
