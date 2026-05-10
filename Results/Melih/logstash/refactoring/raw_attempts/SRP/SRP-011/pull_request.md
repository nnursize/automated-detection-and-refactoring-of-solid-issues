# Refactor SRP-011 (SRP): The DLQ Writer handles low-level I/O, high-level retention policies, and file...

**Status:** `obsolete`  
**Branch:** `refactor/SRP-011` -> `main`  
**Head commit:** `c58cd163a1d9291fd2141008659d58fc19a62e21`  

## Detected issue

- **File**: `logstash-core/src/main/java/org/logstash/common/io/DeadLetterQueueWriter.java`
- **Entity**: `org.logstash.common.io.DeadLetterQueueWriter` (class)
- **Lines (at detection time)**: L85–L645
- **Severity**: medium
- **Confidence**: detected by 1 scan(s)

**Description.** The DLQ Writer handles low-level I/O, high-level retention policies, and filesystem monitoring.

**Reasoning.** The class manages the creation and sealing of data segments (I/O), implements business logic for age and size-based retention policies, and includes a WatchService to monitor the filesystem for notifications from the reader. Policy enforcement and filesystem monitoring are distinct responsibilities from the actual writing of data records.

## Obsolete

entity `org.logstash.common.io.DeadLetterQueueWriter` not found in current source of `logstash-core/src/main/java/org/logstash/common/io/DeadLetterQueueWriter.java` — likely renamed/removed by an earlier refactor

## Diff

*(no diff — patch was not applied)*
