# ISP Violation Report: fastjson2

## Summary
- **Total unique issues**: 8
- **High severity**: 6
- **Medium severity**: 2
- **Low severity**: 0
- **Found by multiple scans**: 5/8

## Issues

### ISP-001 [HIGH] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF8.java — JSONReaderUTF8
- **Confidence**: Found in 6 scan(s)
- **Lines**: 774–1215
- **Type**: class
- **Description**: Implementation of a 'Fat Interface' containing dozens of specialized optimization methods.
- **Reasoning**: The JSONReader hierarchy (as seen in JSONReaderUTF8) defines a massive set of methods for matching field names and values of specific lengths (e.g., nextIfName4Match1 through nextIfName4Match43). This 'Fat Interface' forces every subclass to implement these highly specific optimization hooks, regardless of whether the implementation strategy or data source benefits from them. This violates ISP by bloating the core reader contract with implementation-specific optimization details that should be segregated from the general parsing interface.

### ISP-006 [HIGH] core/src/main/java/com/alibaba/fastjson2/JSONReader.java — JSONReader
- **Confidence**: Found in 6 scan(s)
- **Lines**: 54–6887
- **Type**: class
- **Description**: JSONReader is a fat interface that forces subclasses to implement a massive number of highly specialized methods.
- **Reasoning**: The abstract class JSONReader defines hundreds of abstract methods that every subclass must implement. This includes a massive series of optimization methods like nextIfName4Match2 through nextIfName4Match43 (lines 480-1000+), which are highly specific to binary format (JSONB) optimizations. Additionally, it defines numerous format-specific parsing methods (e.g., readLocalTime8, readLocalDate10) as abstract. This forces subclasses for standard text formats (like JSONReaderUTF8 or JSONReaderASCII) to provide implementations for dozens of methods that are irrelevant to their specific format or encoding. Furthermore, methods like nextIfMatch(byte type) and nextIfMatchTypedAny() (lines 2049-2060) throw 'UnsupportedOperation' exceptions in the base class, indicating that the interface is forcing a contract that is not universally applicable to its implementations.

### ISP-002 [HIGH] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF16.java — JSONReaderUTF16
- **Confidence**: Found in 4 scan(s)
- **Lines**: 1500–1950
- **Type**: class
- **Description**: Implementation of a 'Fat Interface' containing dozens of specialized optimization methods.
- **Reasoning**: Similar to the UTF8 implementation, JSONReaderUTF16 is forced to satisfy a bloated contract in the JSONReader base class. It implements a vast array of specialized 'Match' methods (nextIfName8Match0, nextIfName4Match2, etc.) that are coupled to specific char patterns and lengths. This forces the class to provide logic for a large number of methods that should be segregated into specialized optimization interfaces rather than being part of the primary JSON parsing contract.

### ISP-007 [HIGH] core/src/main/java/com/alibaba/fastjson2/JSONReaderJSONB.java — JSONReaderJSONB
- **Confidence**: Found in 3 scan(s)
- **Lines**: 25–6303
- **Type**: class
- **Description**: JSONReaderJSONB is forced to implement numerous text-specific methods from JSONReader that are not applicable to binary JSON.
- **Reasoning**: As a subclass of JSONReader, JSONReaderJSONB is forced to provide implementations for methods like nextIfMatch(char), nextIfArrayStart(), nextIfComma(), and skipComment(). Because these operations are specific to text-based JSON and have no meaning in the binary JSONB format, the class is forced to throw 'UnsupportedOperationException' or 'JSONException("UnsupportedOperation")' (e.g., L261, L266, L271, L4826), which is a clear violation of ISP.

### ISP-008 [HIGH] core/src/main/java/com/alibaba/fastjson2/JSONWriter.java — JSONWriter
- **Confidence**: Found in 3 scan(s)
- **Lines**: 68–5055
- **Type**: class
- **Description**: JSONWriter is a fat interface that forces implementations to depend on a broad range of unrelated output methods.
- **Reasoning**: JSONWriter contains a vast number of abstract methods for writing every possible data type and handling different output formats (text vs binary). The base class itself contains several methods that throw 'UnsupportedOperationException' (e.g., writeRaw at L1230, writeSymbol at L1463, writeTypeName at L2416), indicating that the interface is too broad and forces subclasses to inherit or implement methods they do not support or use.

### ISP-003 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF8.java — JSONReaderUTF8
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1968–2230
- **Type**: class
- **Description**: Reader interface is polluted with specific date format parsing methods.
- **Reasoning**: The reader hierarchy includes methods like readLocalDate8, readLocalDate9, readLocalDate10, and readLocalDate11. These methods represent specific string-length optimizations for date parsing. Including them in the primary reader interface forces all implementations to support these specific formats, violating ISP by not segregating general JSON parsing from specialized, format-specific optimizations.

### ISP-004 [MEDIUM] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF16.java — JSONReaderUTF16
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1860–2330
- **Type**: class
- **Description**: Inheritance of a fat interface requiring dozens of specialized matching methods.
- **Reasoning**: Similar to the UTF8 implementation, JSONReaderUTF16 is forced to implement the full suite of optimization methods (nextIfName8Match0, nextIfName4Match1...43, etc.) defined in the JSONReader base. This forces the class to depend on and implement a large number of methods that are only relevant to specific internal performance optimizations of the library's codec generator. This violates ISP by forcing implementations to satisfy a massive, non-segregated interface containing nearly 100 methods, many of which serve distinct, specialized purposes.

### ISP-005 [HIGH] core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF16.java — JSONReaderUTF16
- **Confidence**: Found in 1 scan(s)
- **Lines**: 16–1450
- **Type**: class
- **Description**: JSONReaderUTF16 is forced to implement a bloated contract that includes specialized parsing for non-core JSON types.
- **Reasoning**: God Class smell -> ISP violation. Similar to the UTF8 implementation, JSONReaderUTF16 is forced to implement the entire JSONReader contract, which is a 'fat interface'. It includes dozens of methods for specialized Java 8 date/time types (readLocalDate8, readLocalDate9, etc.), UUIDs, and regular expression patterns. This forces the class to carry significant implementation baggage that should be segregated into separate, more focused interfaces or external handlers, ensuring that a basic JSON reader implementation isn't forced to support every possible data type supported by the library.
