# Refactor ISP-007 (ISP): MmapPageIOV1 implements PageIO but throws UnsupportedOperationException for s...

**Status:** `obsolete`  
**Branch:** `refactor/ISP-007` -> `main`  
**Head commit:** `c86960ad45d225a0604034d8f0b69a79cde0356a`  

## Detected issue

- **File**: `logstash-core/src/main/java/org/logstash/ackedqueue/io/MmapPageIOV1.java`
- **Entity**: `org.logstash.ackedqueue.io.MmapPageIOV1` (class)
- **Lines (at detection time)**: L29–L222
- **Severity**: high
- **Confidence**: detected by 3 scan(s)

**Description.** MmapPageIOV1 implements PageIO but throws UnsupportedOperationException for several methods.

**Reasoning.** The `MmapPageIOV1` class implements the `PageIO` interface but throws `UnsupportedOperationException` for `recover()`, `create()`, `ensurePersisted()`, `purge()`, and `write()`. This is a textbook violation of the Interface Segregation Principle. It indicates that the `PageIO` interface is 'fat' and groups together responsibilities (reading, writing, lifecycle management, recovery) that are not universally applicable to all its implementations. `MmapPageIOV1` only supports reading, but is forced to provide implementations for writing, creating, and other operations it does not support. The `PageIO` interface should be segregated into smaller, more focused interfaces (e.g., `ReadablePageIO`, `WritablePageIO`, `RecoverablePageIO`, `LifecyclePageIO`) so that clients are only forced to depend on methods relevant to their specific needs.

## Obsolete

entity `org.logstash.ackedqueue.io.MmapPageIOV1` not found in current source of `logstash-core/src/main/java/org/logstash/ackedqueue/io/MmapPageIOV1.java` — likely renamed/removed by an earlier refactor

## Diff

*(no diff — patch was not applied)*
