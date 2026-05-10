# Refactor ISP-003 (ISP): MmapPageIOV1 implements PageIO but throws UnsupportedOperationException for s...

**Status:** `obsolete`  
**Branch:** `refactor/ISP-003` -> `main`  
**Head commit:** `22b093a1453fbe4f3f30563aa4cab10cf4907391`  

## Detected issue

- **File**: `logstash-core/src/main/java/org/logstash/ackedqueue/io/MmapPageIOV1.java`
- **Entity**: `PageIO` (class)
- **Lines (at detection time)**: L30–L240
- **Severity**: high
- **Confidence**: detected by 1 scan(s)

**Description.** MmapPageIOV1 implements PageIO but throws UnsupportedOperationException for several methods.

**Reasoning.** The `PageIO` interface defines a broad set of operations for page management (reading, writing, creating, recovering, persisting, purging, checking space, activating, deactivating, closing). The `MmapPageIOV1` class, which represents an older version of page I/O, explicitly throws `UnsupportedOperationException` for several methods (`recover()`, `create()`, `ensurePersisted()`, `purge()`, `write()`, `hasSpace()`). This is a textbook violation of ISP, as `MmapPageIOV1` is forced to implement methods that are not relevant to its specific functionality (read-only for an older format). This indicates that `PageIO` is too broad and should be segregated into smaller, more specific interfaces, such as `ReadablePageIO`, `WritablePageIO`, `RecoverablePageIO`, `CreatablePageIO`, `PersistablePageIO`, `PurgeablePageIO`, and `SpaceCheckablePageIO`.

## Obsolete

entity `PageIO` not found in current source of `logstash-core/src/main/java/org/logstash/ackedqueue/io/MmapPageIOV1.java` — likely renamed/removed by an earlier refactor

## Diff

*(no diff — patch was not applied)*
