# Refactor ISP-017 (ISP): The 'co.elastic.logstash.api.Event' interface is a fat interface, bundling to...

**Status:** `obsolete`  
**Branch:** `refactor/ISP-017` -> `main`  
**Head commit:** `22b093a1453fbe4f3f30563aa4cab10cf4907391`  

## Detected issue

- **File**: `logstash-core/src/main/java/org/logstash/Event.java`
- **Entity**: `co.elastic.logstash.api.Event` (class)
- **Lines (at detection time)**: L36–L37
- **Severity**: high
- **Confidence**: detected by 1 scan(s)

**Description.** The 'co.elastic.logstash.api.Event' interface is a fat interface, bundling too many responsibilities.

**Reasoning.** The 'co.elastic.logstash.api.Event' interface defines a large number of methods covering diverse functionalities such as field access, modification, cancellation, timestamp management, tagging, cloning, and merging. Clients (e.g., plugins) that only need a subset of these functionalities (e.g., only reading fields or only tagging) are forced to depend on the entire broad interface, including methods they do not use. This violates ISP by not segregating the interface into more focused roles like 'ReadableEvent', 'WritableEvent', 'CloneableEvent', etc.

## Obsolete

entity `co.elastic.logstash.api.Event` not found in current source of `logstash-core/src/main/java/org/logstash/Event.java` — likely renamed/removed by an earlier refactor

## Diff

*(no diff — patch was not applied)*
