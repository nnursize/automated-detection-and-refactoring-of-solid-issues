# Refactor summary: fastjson2

- Total attempts: **56**
  - `applied_unverified`: 6
  - `obsolete`: 3
  - `llm_error`: 47

## All attempts

| Issue | Principle | Status | Tests passed/total | CC before -> after | MI before -> after | File |
|-------|-----------|--------|--------------------|--------------------|--------------------|------|
| DIP-001 | DIP | `llm_error` | - | - | - | `core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java` |
| DIP-002 | DIP | `llm_error` | - | - | - | `core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF8.java` |
| DIP-003 | DIP | `llm_error` | - | - | - | `core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF16.java` |
| DIP-004 | DIP | `llm_error` | - | - | - | `core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java` |
| DIP-006 | DIP | `llm_error` | - | - | - | `core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java` |
| DIP-007 | DIP | `llm_error` | - | - | - | `core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF8.java` |
| DIP-061 | DIP | `llm_error` | - | - | - | `core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java` |
| DIP-062 | DIP | `llm_error` | - | - | - | `core/src/main/java/com/alibaba/fastjson2/JSONReader.java` |
| DIP-076 | DIP | `llm_error` | - | - | - | `core/src/main/java/com/alibaba/fastjson2/JSONWriter.java` |
| DIP-077 | DIP | `obsolete` | - | - | - | `core/src/main/java/com/alibaba/fastjson2/JSON.java` |
| DIP-078 | DIP | `obsolete` | - | - | - | `core/src/main/java/com/alibaba/fastjson2/JSONB.java` |
| DIP-079 | DIP | `llm_error` | - | - | - | `core/src/main/java/com/alibaba/fastjson2/reader/ObjectReaderCreator.java` |
| ISP-001 | ISP | `llm_error` | - | - | - | `core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF8.java` |
| ISP-002 | ISP | `llm_error` | - | - | - | `core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF16.java` |
| ISP-003 | ISP | `llm_error` | - | - | - | `core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF8.java` |
| ISP-004 | ISP | `llm_error` | - | - | - | `core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF16.java` |
| ISP-005 | ISP | `llm_error` | - | - | - | `core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF16.java` |
| ISP-006 | ISP | `llm_error` | - | - | - | `core/src/main/java/com/alibaba/fastjson2/JSONReader.java` |
| ISP-007 | ISP | `llm_error` | - | - | - | `core/src/main/java/com/alibaba/fastjson2/JSONReaderJSONB.java` |
| ISP-008 | ISP | `llm_error` | - | - | - | `core/src/main/java/com/alibaba/fastjson2/JSONWriter.java` |
| LSP-002 | LSP | `llm_error` | - | - | - | `core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java` |
| LSP-006 | LSP | `llm_error` | - | - | - | `core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java` |
| LSP-009 | LSP | `llm_error` | - | - | - | `core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java` |
| LSP-017 | LSP | `llm_error` | - | - | - | `core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java` |
| LSP-018 | LSP | `llm_error` | - | - | - | `core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java` |
| LSP-019 | LSP | `llm_error` | - | - | - | `core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java` |
| LSP-022 | LSP | `llm_error` | - | - | - | `core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java` |
| LSP-023 | LSP | `llm_error` | - | - | - | `core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java` |
| LSP-026 | LSP | `llm_error` | - | - | - | `core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java` |
| LSP-027 | LSP | `llm_error` | - | - | - | `core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java` |
| LSP-029 | LSP | `llm_error` | - | - | - | `core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java` |
| LSP-030 | LSP | `llm_error` | - | - | - | `core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java` |
| OCP-001 | OCP | `llm_error` | - | - | - | `core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java` |
| OCP-003 | OCP | `llm_error` | - | - | - | `core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java` |
| OCP-004 | OCP | `applied_unverified` | - | 20.5 -> 20.35 | 0.0 -> 0.0 | `core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java` |
| OCP-005 | OCP | `applied_unverified` | - | 20.35 -> 20.07 | 0.0 -> 0.0 | `core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java` |
| OCP-006 | OCP | `applied_unverified` | - | 20.07 -> 20.09 | 0.0 -> 0.0 | `core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java` |
| OCP-007 | OCP | `llm_error` | - | - | - | `core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java` |
| OCP-010 | OCP | `llm_error` | - | - | - | `core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java` |
| OCP-011 | OCP | `llm_error` | - | - | - | `core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java` |
| OCP-013 | OCP | `llm_error` | - | - | - | `core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java` |
| OCP-014 | OCP | `llm_error` | - | - | - | `core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java` |
| OCP-015 | OCP | `llm_error` | - | - | - | `core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java` |
| OCP-020 | OCP | `llm_error` | - | - | - | `core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java` |
| SRP-001 | SRP | `applied_unverified` | - | 20.09 -> 14.12 | 0.0 -> 0.0 | `core/src/main/java/com/alibaba/fastjson2/util/DateUtils.java` |
| SRP-002 | SRP | `llm_error` | - | - | - | `core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF8.java` |
| SRP-006 | SRP | `llm_error` | - | - | - | `core/src/main/java/com/alibaba/fastjson2/JSONReaderUTF16.java` |
| SRP-010 | SRP | `applied_unverified` | - | 6.62 -> 5.52 | 0.0 -> 0.0 | `core/src/main/java/com/alibaba/fastjson2/JSONReader.java` |
| SRP-011 | SRP | `applied_unverified` | - | 4.91 -> 4.53 | 0.0 -> 0.0 | `core/src/main/java/com/alibaba/fastjson2/JSONWriter.java` |
| SRP-012 | SRP | `llm_error` | - | - | - | `core/src/main/java/com/alibaba/fastjson2/util/TypeUtils.java` |
| SRP-013 | SRP | `llm_error` | - | - | - | `core/src/main/java/com/alibaba/fastjson2/util/IOUtils.java` |
| SRP-015 | SRP | `llm_error` | - | - | - | `core/src/main/java/com/alibaba/fastjson2/writer/ObjectWriterCreatorASM.java` |
| SRP-016 | SRP | `llm_error` | - | - | - | `core/src/main/java/com/alibaba/fastjson2/reader/ObjectReaderCreatorASM.java` |
| SRP-017 | SRP | `llm_error` | - | - | - | `core/src/main/java/com/alibaba/fastjson2/introspect/PropertyAccessorFactory.java` |
| SRP-019 | SRP | `obsolete` | - | - | - | `core/src/main/java/com/alibaba/fastjson2/JSONB.java` |
| SRP-020 | SRP | `llm_error` | - | - | - | `core/src/main/java/com/alibaba/fastjson2/JSONReaderJSONB.java` |