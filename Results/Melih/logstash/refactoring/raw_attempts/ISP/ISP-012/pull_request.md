# Refactor ISP-012 (ISP): The 'PageIO' interface is a fat interface mixing I/O, lifecycle, and state qu...

**Status:** `obsolete`  
**Branch:** `refactor/ISP-012` -> `main`  
**Head commit:** `c86960ad45d225a0604034d8f0b69a79cde0356a`  

## Detected issue

- **File**: `logstash-core/src/main/java/org/logstash/ackedqueue/io/MmapPageIOV2.java`
- **Entity**: `org.logstash.ackedqueue.io.PageIO` (class)
- **Lines (at detection time)**: L27–L27
- **Severity**: high
- **Confidence**: detected by 2 scan(s)

**Description.** The 'PageIO' interface is a fat interface mixing I/O, lifecycle, and state query methods.

**Reasoning.** The `PageIO` interface defines a very broad set of operations including opening/closing (`open`, `close`), reading/writing data (`read`, `write`), lifecycle management (`create`, `deactivate`, `activate`, `purge`, `recover`), persistence (`ensurePersisted`), and state queries (`getCapacity`, `getMinSeqNum`, `getElementCount`, `hasSpace`, `persistedByteCount`, `getHead`, `isCorruptedPage`). Clients interacting with a page might only need a subset of these methods (e.g., a reader client only needs read-related methods, a writer client only needs write-related methods). Forcing all clients to depend on all these methods violates ISP.

## Obsolete

entity `org.logstash.ackedqueue.io.PageIO` not found in current source of `logstash-core/src/main/java/org/logstash/ackedqueue/io/MmapPageIOV2.java` — likely renamed/removed by an earlier refactor

## Diff

*(no diff — patch was not applied)*
