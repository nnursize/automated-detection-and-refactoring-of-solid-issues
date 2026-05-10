# Refactor ISP-002 (ISP): The co.elastic.logstash.api.Event interface is a 'fat' interface combining ma...

**Status:** `obsolete`  
**Branch:** `refactor/ISP-002` -> `main`  
**Head commit:** `b901e8c7034cc8594c1b9d2728a6cd0cb12300f5`  

## Detected issue

- **File**: `logstash-core/src/main/java/org/logstash/Event.java`
- **Entity**: `co.elastic.logstash.api.Event` (class)
- **Lines (at detection time)**: L39–L400
- **Severity**: high
- **Confidence**: detected by 4 scan(s)

**Description.** The co.elastic.logstash.api.Event interface is a 'fat' interface combining many responsibilities.

**Reasoning.** The `co.elastic.logstash.api.Event` interface defines a large number of methods covering various aspects of an event (reading, writing, cancelling, tagging, cloning, serialization, etc.). Clients that only need a subset of these functionalities (e.g., a component that only reads event fields, or one that only tags events) are forced to depend on the entire interface, including methods they do not use. This increases coupling and makes it harder to create specialized event processors. The interface could be segregated into smaller, more focused interfaces such as `ReadableEvent`, `WritableEvent`, `CancellableEvent`, `TaggingEvent`, etc.

## Obsolete

entity `co.elastic.logstash.api.Event` not found in current source of `logstash-core/src/main/java/org/logstash/Event.java` — likely renamed/removed by an earlier refactor

## Diff

*(no diff — patch was not applied)*
