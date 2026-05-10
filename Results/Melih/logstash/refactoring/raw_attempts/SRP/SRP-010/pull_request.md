# Refactor SRP-010 (SRP): The Pipeline JRuby extension manages execution, metrics, security, and DLQ lo...

**Status:** `obsolete`  
**Branch:** `refactor/SRP-010` -> `main`  
**Head commit:** `1c876b4b4de952ca93cb22874807365b68658b60`  

## Detected issue

- **File**: `logstash-core/src/main/java/org/logstash/execution/AbstractPipelineExt.java`
- **Entity**: `org.logstash.execution.AbstractPipelineExt` (class)
- **Lines (at detection time)**: L105–L644
- **Severity**: high
- **Confidence**: detected by 1 scan(s)

**Description.** The Pipeline JRuby extension manages execution, metrics, security, and DLQ logic.

**Reasoning.** This class is responsible for compiling the Pipeline IR, initializing complex flow metrics, managing the lifecycle of the Dead Letter Queue (DLQ) writer, handling secret store integration, and providing health status details. It mixes high-level execution logic with specific infrastructural concerns like security (SecretStore) and diagnostics (Metrics/Health).

## Obsolete

entity `org.logstash.execution.AbstractPipelineExt` not found in current source of `logstash-core/src/main/java/org/logstash/execution/AbstractPipelineExt.java` — likely renamed/removed by an earlier refactor

## Diff

*(no diff — patch was not applied)*
