# Refactor summary: jackson-core

- Total attempts: **60**
  - `applied_unverified`: 19
  - `patch_failed`: 38
  - `detection_rejected`: 3

## All attempts

| Issue | Principle | Status | Tests passed/total | CC before -> after | MI before -> after | File |
|-------|-----------|--------|--------------------|--------------------|--------------------|------|
| DIP-001 | DIP | `patch_failed` | - | - | - | `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java` |
| DIP-003 | DIP | `patch_failed` | - | - | - | `src/main/java/tools/jackson/core/JsonGenerator.java` |
| DIP-004 | DIP | `applied_unverified` | - | 9.62 -> 5.81 | 0.0 -> 0.0 | `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java` |
| DIP-008 | DIP | `applied_unverified` | - | 9.92 -> 5.72 | 0.0 -> 0.0 | `src/main/java/tools/jackson/core/json/ReaderBasedJsonParser.java` |
| DIP-011 | DIP | `applied_unverified` | - | 4.41 -> 2.14 | 0.0 -> 0.0 | `src/main/java/tools/jackson/core/TokenStreamFactory.java` |
| DIP-016 | DIP | `patch_failed` | - | - | - | `src/main/java/tools/jackson/core/json/JsonParserBase.java` |
| DIP-018 | DIP | `patch_failed` | - | - | - | `src/main/java/tools/jackson/core/TokenStreamFactory.java` |
| DIP-019 | DIP | `patch_failed` | - | - | - | `src/main/java/tools/jackson/core/TokenStreamFactory.java` |
| DIP-021 | DIP | `patch_failed` | - | - | - | `src/main/java/tools/jackson/core/json/ByteSourceJsonBootstrapper.java` |
| DIP-022 | DIP | `applied_unverified` | - | 2.66 -> 2.08 | 0.0 -> 0.0 | `src/main/java/tools/jackson/core/io/IOContext.java` |
| DIP-023 | DIP | `patch_failed` | - | - | - | `src/main/java/tools/jackson/core/base/TextualTSFactory.java` |
| DIP-024 | DIP | `patch_failed` | - | - | - | `src/main/java/tools/jackson/core/base/GeneratorBase.java` |
| ISP-001 | ISP | `applied_unverified` | - | 8.52 -> 5.22 | 0.0 -> 0.0 | `src/main/java/tools/jackson/core/JsonGenerator.java` |
| ISP-002 | ISP | `patch_failed` | - | - | - | `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java` |
| ISP-004 | ISP | `patch_failed` | - | - | - | `src/main/java/tools/jackson/core/json/ReaderBasedJsonParser.java` |
| ISP-006 | ISP | `patch_failed` | - | - | - | `src/main/java/tools/jackson/core/json/WriterBasedJsonGenerator.java` |
| ISP-007 | ISP | `applied_unverified` | - | 10.77 -> 6.38 | 0.0 -> 0.0 | `src/main/java/tools/jackson/core/JsonParser.java` |
| ISP-008 | ISP | `patch_failed` | - | - | - | `src/main/java/tools/jackson/core/base/BinaryTSFactory.java` |
| ISP-010 | ISP | `applied_unverified` | - | 5.14 -> 4.11 | 0.0 -> 0.0 | `src/main/java/tools/jackson/core/base/ParserBase.java` |
| ISP-011 | ISP | `patch_failed` | - | - | - | `src/main/java/tools/jackson/core/filter/FilteringParserDelegate.java` |
| ISP-012 | ISP | `patch_failed` | - | - | - | `src/main/java/tools/jackson/core/base/GeneratorBase.java` |
| ISP-013 | ISP | `patch_failed` | - | - | - | `src/main/java/tools/jackson/core/base/GeneratorBase.java` |
| ISP-014 | ISP | `patch_failed` | - | - | - | `src/main/java/tools/jackson/core/json/WriterBasedJsonGenerator.java` |
| ISP-015 | ISP | `patch_failed` | - | - | - | `src/main/java/tools/jackson/core/json/WriterBasedJsonGenerator.java` |
| LSP-001 | LSP | `patch_failed` | - | - | - | `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java` |
| LSP-002 | LSP | `detection_rejected` | - | - | - | `src/main/java/tools/jackson/core/json/UTF8DataInputJsonParser.java` |
| LSP-003 | LSP | `patch_failed` | - | - | - | `src/main/java/tools/jackson/core/json/async/NonBlockingUtf8JsonParserBase.java` |
| LSP-004 | LSP | `detection_rejected` | - | - | - | `src/main/java/tools/jackson/core/json/ReaderBasedJsonParser.java` |
| LSP-005 | LSP | `patch_failed` | - | - | - | `src/main/java/tools/jackson/core/json/async/NonBlockingUtf8JsonParserBase.java` |
| LSP-006 | LSP | `patch_failed` | - | - | - | `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java` |
| LSP-007 | LSP | `patch_failed` | - | - | - | `src/main/java/tools/jackson/core/json/WriterBasedJsonGenerator.java` |
| LSP-008 | LSP | `patch_failed` | - | - | - | `src/main/java/tools/jackson/core/json/WriterBasedJsonGenerator.java` |
| LSP-010 | LSP | `patch_failed` | - | - | - | `src/main/java/tools/jackson/core/json/UTF8JsonGenerator.java` |
| LSP-011 | LSP | `patch_failed` | - | - | - | `src/main/java/tools/jackson/core/json/WriterBasedJsonGenerator.java` |
| LSP-012 | LSP | `detection_rejected` | - | - | - | `src/main/java/tools/jackson/core/json/async/NonBlockingJsonParserBase.java` |
| LSP-013 | LSP | `patch_failed` | - | - | - | `src/main/java/tools/jackson/core/base/GeneratorBase.java` |
| OCP-001 | OCP | `patch_failed` | - | - | - | `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java` |
| OCP-002 | OCP | `patch_failed` | - | - | - | `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java` |
| OCP-003 | OCP | `applied_unverified` | - | 9.72 -> 9.62 | 0.0 -> 0.0 | `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java` |
| OCP-005 | OCP | `patch_failed` | - | - | - | `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java` |
| OCP-006 | OCP | `patch_failed` | - | - | - | `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java` |
| OCP-007 | OCP | `applied_unverified` | - | 9.88 -> 9.81 | 0.0 -> 0.0 | `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java` |
| OCP-008 | OCP | `patch_failed` | - | - | - | `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java` |
| OCP-010 | OCP | `patch_failed` | - | - | - | `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java` |
| OCP-012 | OCP | `patch_failed` | - | - | - | `src/main/java/tools/jackson/core/json/async/NonBlockingUtf8JsonParserBase.java` |
| OCP-018 | OCP | `patch_failed` | - | - | - | `src/main/java/tools/jackson/core/JsonGenerator.java` |
| OCP-032 | OCP | `applied_unverified` | - | 9.81 -> 9.72 | 0.0 -> 0.0 | `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java` |
| OCP-033 | OCP | `patch_failed` | - | - | - | `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java` |
| SRP-001 | SRP | `applied_unverified` | - | 10.22 -> 10.54 | 0.0 -> 0.0 | `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java` |
| SRP-002 | SRP | `applied_unverified` | - | 12.2 -> 10.62 | 0.0 -> 0.0 | `src/main/java/tools/jackson/core/json/async/NonBlockingUtf8JsonParserBase.java` |
| SRP-003 | SRP | `applied_unverified` | - | 8.71 -> 7.87 | 0.0 -> 0.0 | `src/main/java/tools/jackson/core/json/UTF8DataInputJsonParser.java` |
| SRP-004 | SRP | `applied_unverified` | - | 11.21 -> 14.64 | 0.0 -> 0.0 | `src/main/java/tools/jackson/core/json/ReaderBasedJsonParser.java` |
| SRP-005 | SRP | `applied_unverified` | - | 9.29 -> 8.97 | 0.0 -> 0.0 | `src/main/java/tools/jackson/core/JsonGenerator.java` |
| SRP-006 | SRP | `patch_failed` | - | - | - | `src/main/java/tools/jackson/core/json/UTF8JsonGenerator.java` |
| SRP-007 | SRP | `applied_unverified` | - | 5.76 -> 8.68 | 0.0 -> 0.0 | `src/main/java/tools/jackson/core/json/WriterBasedJsonGenerator.java` |
| SRP-022 | SRP | `applied_unverified` | - | 4.59 -> 9.71 | 0.0 -> 0.0 | `src/main/java/tools/jackson/core/TokenStreamFactory.java` |
| SRP-023 | SRP | `applied_unverified` | - | 4.41 -> 3.83 | 0.0 -> 0.0 | `src/main/java/tools/jackson/core/TokenStreamFactory.java` |
| SRP-027 | SRP | `patch_failed` | - | - | - | `src/main/java/tools/jackson/core/JsonGenerator.java` |
| SRP-028 | SRP | `applied_unverified` | - | 8.97 -> 13.6 | 0.0 -> 0.0 | `src/main/java/tools/jackson/core/JsonGenerator.java` |
| SRP-032 | SRP | `patch_failed` | - | - | - | `src/main/java/tools/jackson/core/json/UTF8JsonGenerator.java` |