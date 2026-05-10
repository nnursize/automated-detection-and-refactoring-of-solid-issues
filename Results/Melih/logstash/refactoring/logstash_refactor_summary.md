# Refactor summary: logstash

- Total attempts: **60**
  - `applied_unverified`: 42
  - `patch_failed`: 5
  - `obsolete`: 13

## All attempts

| Issue | Principle | Status | Tests passed/total | CC before -> after | MI before -> after | File |
|-------|-----------|--------|--------------------|--------------------|--------------------|------|
| DIP-001 | DIP | `applied_unverified` | - | 4.49 -> 4.49 | 0.0 -> 0.0 | `logstash-core/src/main/java/org/logstash/ackedqueue/Queue.java` |
| DIP-002 | DIP | `patch_failed` | - | - | - | `logstash-core/src/main/java/org/logstash/ackedqueue/Queue.java` |
| DIP-003 | DIP | `applied_unverified` | - | 2.52 -> 2.52 | 0.0 -> 0.0 | `logstash-core/src/main/java/org/logstash/config/ir/CompiledPipeline.java` |
| DIP-004 | DIP | `applied_unverified` | - | 1.9 -> 1.82 | 0.0 -> 0.0 | `logstash-core/src/main/java/org/logstash/plugins/factory/PluginFactoryExt.java` |
| DIP-005 | DIP | `applied_unverified` | - | 4.49 -> 4.49 | 0.0 -> 0.0 | `logstash-core/src/main/java/org/logstash/ackedqueue/Queue.java` |
| DIP-006 | DIP | `applied_unverified` | - | 4.49 -> 4.49 | 0.0 -> 0.0 | `logstash-core/src/main/java/org/logstash/ackedqueue/Queue.java` |
| DIP-007 | DIP | `applied_unverified` | - | 4.49 -> 4.49 | 0.0 -> 0.0 | `logstash-core/src/main/java/org/logstash/ackedqueue/Queue.java` |
| DIP-008 | DIP | `applied_unverified` | - | 2.41 -> 2.71 | 0.0 -> 0.0 | `logstash-core/src/main/java/org/logstash/common/io/DeadLetterQueueWriter.java` |
| DIP-009 | DIP | `applied_unverified` | - | 1.73 -> 1.71 | 0.0 -> 0.0 | `logstash-core/src/main/java/org/logstash/execution/AbstractPipelineExt.java` |
| DIP-010 | DIP | `applied_unverified` | - | 2.41 -> 1.67 | 0.0 -> 0.0 | `logstash-core/src/main/java/org/logstash/common/io/DeadLetterQueueWriter.java` |
| DIP-012 | DIP | `applied_unverified` | - | 3.05 -> 3.05 | 0.0 -> 0.0 | `logstash-core/src/main/java/org/logstash/config/ir/compiler/EventCondition.java` |
| DIP-014 | DIP | `applied_unverified` | - | 1.82 -> 2.0 | 0.0 -> 0.0 | `logstash-core/src/main/java/org/logstash/plugins/factory/PluginFactoryExt.java` |
| ISP-002 | ISP | `obsolete` | - | - | - | `logstash-core/src/main/java/org/logstash/Event.java` |
| ISP-003 | ISP | `obsolete` | - | - | - | `logstash-core/src/main/java/org/logstash/ackedqueue/io/MmapPageIOV1.java` |
| ISP-005 | ISP | `obsolete` | - | - | - | `logstash-core/src/main/java/org/logstash/plugins/factory/PluginFactoryExt.java` |
| ISP-007 | ISP | `obsolete` | - | - | - | `logstash-core/src/main/java/org/logstash/ackedqueue/io/MmapPageIOV1.java` |
| ISP-011 | ISP | `obsolete` | - | - | - | `logstash-core/src/main/java/org/logstash/secret/store/backend/JavaKeyStore.java` |
| ISP-012 | ISP | `obsolete` | - | - | - | `logstash-core/src/main/java/org/logstash/ackedqueue/io/MmapPageIOV2.java` |
| ISP-014 | ISP | `applied_unverified` | - | 2.48 -> 1.0 | 0.0 -> 0.0 | `logstash-core/src/main/java/org/logstash/ackedqueue/io/MmapPageIOV1.java` |
| ISP-015 | ISP | `applied_unverified` | - | 4.49 -> 1.87 | 0.0 -> 0.0 | `logstash-core/src/main/java/org/logstash/ackedqueue/Queue.java` |
| ISP-016 | ISP | `applied_unverified` | - | 1.71 -> 1.73 | 0.0 -> 0.0 | `logstash-core/src/main/java/org/logstash/execution/AbstractPipelineExt.java` |
| ISP-017 | ISP | `obsolete` | - | - | - | `logstash-core/src/main/java/org/logstash/Event.java` |
| ISP-018 | ISP | `obsolete` | - | - | - | `logstash-core/src/main/java/org/logstash/ackedqueue/io/MmapPageIOV2.java` |
| ISP-024 | ISP | `applied_unverified` | - | 2.41 -> 2.41 | 0.0 -> 0.0 | `logstash-core/src/main/java/org/logstash/common/io/DeadLetterQueueWriter.java` |
| LSP-001 | LSP | `applied_unverified` | - | 2.3 -> 2.52 | 0.0 -> 0.0 | `logstash-core/src/main/java/org/logstash/ackedqueue/io/MmapPageIOV1.java` |
| LSP-021 | LSP | `applied_unverified` | - | 2.37 -> 2.33 | 0.0 -> 0.0 | `logstash-core/src/main/java/org/logstash/config/ir/compiler/DatasetCompiler.java` |
| LSP-022 | LSP | `applied_unverified` | - | 5.44 -> 5.44 | 0.0 -> 0.0 | `logstash-core/src/main/java/org/logstash/secret/store/backend/JavaKeyStore.java` |
| LSP-023 | LSP | `applied_unverified` | - | 5.44 -> 5.44 | 0.0 -> 0.0 | `logstash-core/src/main/java/org/logstash/secret/store/backend/JavaKeyStore.java` |
| LSP-046 | LSP | `applied_unverified` | - | 2.38 -> 2.33 | 0.0 -> 0.0 | `logstash-core/src/main/java/org/logstash/Event.java` |
| LSP-075 | LSP | `applied_unverified` | - | 2.5 -> 2.41 | 0.0 -> 0.0 | `logstash-core/src/main/java/org/logstash/common/io/DeadLetterQueueWriter.java` |
| LSP-081 | LSP | `applied_unverified` | - | 1.73 -> 1.73 | 0.0 -> 0.0 | `logstash-core/src/main/java/org/logstash/execution/AbstractPipelineExt.java` |
| LSP-090 | LSP | `applied_unverified` | - | 2.52 -> 2.52 | 0.0 -> 0.0 | `logstash-core/src/main/java/org/logstash/ackedqueue/io/MmapPageIOV1.java` |
| LSP-091 | LSP | `patch_failed` | - | - | - | `logstash-core/src/main/java/org/logstash/ackedqueue/io/MmapPageIOV1.java` |
| LSP-092 | LSP | `patch_failed` | - | - | - | `logstash-core/src/main/java/org/logstash/ackedqueue/io/MmapPageIOV1.java` |
| LSP-093 | LSP | `patch_failed` | - | - | - | `logstash-core/src/main/java/org/logstash/ackedqueue/io/MmapPageIOV1.java` |
| LSP-094 | LSP | `applied_unverified` | - | 2.52 -> 2.48 | 0.0 -> 0.0 | `logstash-core/src/main/java/org/logstash/ackedqueue/io/MmapPageIOV1.java` |
| OCP-001 | OCP | `obsolete` | - | - | - | `logstash-core/src/main/java/org/logstash/config/ir/compiler/EventCondition.java` |
| OCP-003 | OCP | `applied_unverified` | - | 1.82 -> 1.81 | 0.0 -> 0.0 | `logstash-core/src/main/java/org/logstash/execution/AbstractPipelineExt.java` |
| OCP-006 | OCP | `applied_unverified` | - | 2.0 -> 1.9 | 0.0 -> 0.0 | `logstash-core/src/main/java/org/logstash/plugins/factory/PluginFactoryExt.java` |
| OCP-007 | OCP | `applied_unverified` | - | 5.9 -> 5.5 | 0.0 -> 0.0 | `logstash-core/src/main/java/org/logstash/secret/cli/SecretStoreCli.java` |
| OCP-008 | OCP | `applied_unverified` | - | 2.53 -> 2.24 | 0.0 -> 0.0 | `logstash-core/src/main/java/org/logstash/health/PipelineIndicator.java` |
| OCP-020 | OCP | `patch_failed` | - | - | - | `logstash-core/src/main/java/org/logstash/execution/AbstractPipelineExt.java` |
| OCP-024 | OCP | `applied_unverified` | - | 3.33 -> 3.05 | 0.0 -> 0.0 | `logstash-core/src/main/java/org/logstash/config/ir/compiler/EventCondition.java` |
| OCP-025 | OCP | `applied_unverified` | - | 1.81 -> 1.73 | 0.0 -> 0.0 | `logstash-core/src/main/java/org/logstash/execution/AbstractPipelineExt.java` |
| OCP-027 | OCP | `applied_unverified` | - | 4.49 -> 2.75 | 0.0 -> 0.0 | `logstash-core/src/main/java/org/logstash/ackedqueue/Queue.java` |
| OCP-035 | OCP | `applied_unverified` | - | 2.43 -> 2.3 | 0.0 -> 0.0 | `logstash-core/src/main/java/org/logstash/ackedqueue/io/MmapPageIOV1.java` |
| OCP-040 | OCP | `applied_unverified` | - | 5.0 -> 6.5 | 0.0 -> 0.0 | `logstash-core/src/main/java/org/logstash/Javafier.java` |
| OCP-046 | OCP | `applied_unverified` | - | 1.8 -> 1.65 | 0.0 -> 0.0 | `logstash-core/src/main/java/org/logstash/RubyUtil.java` |
| SRP-002 | SRP | `applied_unverified` | - | 2.9 -> 3.55 | 0.0 -> 0.0 | `logstash-core/src/main/java/org/logstash/common/io/DeadLetterQueueWriter.java` |
| SRP-003 | SRP | `applied_unverified` | - | 2.38 -> 1.83 | 0.0 -> 0.0 | `logstash-core/src/main/java/org/logstash/Event.java` |
| SRP-004 | SRP | `applied_unverified` | - | 1.87 -> 2.11 | 0.0 -> 0.0 | `logstash-core/src/main/java/org/logstash/execution/AbstractPipelineExt.java` |
| SRP-006 | SRP | `applied_unverified` | - | 2.12 -> 2.17 | 0.0 -> 0.0 | `logstash-core/src/main/java/org/logstash/plugins/factory/PluginFactoryExt.java` |
| SRP-007 | SRP | `applied_unverified` | - | 4.58 -> 3.25 | 0.0 -> 0.0 | `logstash-core/src/main/java/org/logstash/ackedqueue/Queue.java` |
| SRP-009 | SRP | `obsolete` | - | - | - | `logstash-core/src/main/java/org/logstash/Event.java` |
| SRP-010 | SRP | `obsolete` | - | - | - | `logstash-core/src/main/java/org/logstash/execution/AbstractPipelineExt.java` |
| SRP-011 | SRP | `obsolete` | - | - | - | `logstash-core/src/main/java/org/logstash/common/io/DeadLetterQueueWriter.java` |
| SRP-012 | SRP | `obsolete` | - | - | - | `logstash-core/src/main/java/org/logstash/FieldReference.java` |
| SRP-013 | SRP | `applied_unverified` | - | 4.2 -> 7.33 | 0.0 -> 0.0 | `logstash-core/src/main/java/org/logstash/FieldReference.java` |
| SRP-014 | SRP | `applied_unverified` | - | 5.44 -> 3.33 | 0.0 -> 0.0 | `logstash-core/src/main/java/org/logstash/secret/store/backend/JavaKeyStore.java` |
| SRP-017 | SRP | `applied_unverified` | - | 2.33 -> 1.76 | 0.0 -> 0.0 | `logstash-core/src/main/java/org/logstash/config/ir/compiler/DatasetCompiler.java` |