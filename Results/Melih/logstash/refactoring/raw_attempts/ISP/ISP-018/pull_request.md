# Refactor ISP-018 (ISP): The 'PageIO' interface is a fat interface, bundling too many responsibilities.

**Status:** `obsolete`  
**Branch:** `refactor/ISP-018` -> `main`  
**Head commit:** `22b093a1453fbe4f3f30563aa4cab10cf4907391`  

## Detected issue

- **File**: `logstash-core/src/main/java/org/logstash/ackedqueue/io/MmapPageIOV2.java`
- **Entity**: `PageIO` (class)
- **Lines (at detection time)**: L30–L31
- **Severity**: high
- **Confidence**: detected by 1 scan(s)

**Description.** The 'PageIO' interface is a fat interface, bundling too many responsibilities.

**Reasoning.** The 'PageIO' interface defines a broad set of methods related to various aspects of page management, including opening, reading, recovering, creating, activating/deactivating, persisting, purging, writing, and querying page properties. Implementations are forced to provide all these methods. Clients that only require a subset of these functionalities (e.g., only reading from a page or only writing to a page) are forced to depend on the entire broad interface, including methods they do not use. This violates ISP.

## Obsolete

entity `PageIO` not found in current source of `logstash-core/src/main/java/org/logstash/ackedqueue/io/MmapPageIOV2.java` — likely renamed/removed by an earlier refactor

## Diff

*(no diff — patch was not applied)*
