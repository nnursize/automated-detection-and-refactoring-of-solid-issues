# Refactor SRP-002 (SRP): Class mixes low-level I/O, retention policy logic, and inter-process synchron...

**Status:** `applied_unverified`  
**Branch:** `refactor/SRP-002` -> `main`  
**Head commit:** `b3160c587eab2fd87e9b4a51ea14534f1c44b3db`  
**LLM finish:** `FinishReason.STOP` (prompt 9096, completion 3950)  

## Detected issue

- **File**: `logstash-core/src/main/java/org/logstash/common/io/DeadLetterQueueWriter.java`
- **Entity**: `DeadLetterQueueWriter` (class)
- **Lines (at detection time)**: L88–L605
- **Severity**: high
- **Confidence**: detected by 10 scan(s)

**Description.** Class mixes low-level I/O, retention policy logic, and inter-process synchronization.

**Reasoning.** This class is responsible for: 1) Writing entries to the DLQ, 2) Managing file segment lifecycle (rollover and sealing), 3) Implementing business logic for retention policies (age-based and size-based deletion), and 4) Monitoring the filesystem for external notifications from the reader process using a WatchService. The policy logic (when to delete) should be separated from the mechanism (how to write/delete files).

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 7
- **Files created** (1): `logstash-core/src/main/java/org/logstash/common/io/RetentionPolicyManager.java`
- **Files modified** (1): `logstash-core/src/main/java/org/logstash/common/io/DeadLetterQueueWriter.java`

**Summary.** Extract DLQ retention policy logic into a dedicated RetentionPolicyManager class

**Rationale.** The DeadLetterQueueWriter was violating SRP by managing both I/O operations and complex retention policies (age/size). Extracting the policy logic into a separate class improves maintainability and testability.

## Changes overview

_7 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `logstash-core/src/main/java/org/logstash/common/io/DeadLetterQueueWriter.java` (4-line block → 2-line replacement)

**Replaces:**

```java
    private volatile Optional<Timestamp> oldestSegmentTimestamp;
    private volatile Optional<Path> oldestSegmentPath = Optional.empty();
    private final TemporalAmount retentionTime;
    private final SchedulerService flusherService;
```

**With:**

```java
    private final RetentionPolicyManager retentionPolicyManager;
    private final SchedulerService flusherService;
```

### 2. EDIT `logstash-core/src/main/java/org/logstash/common/io/DeadLetterQueueWriter.java` (16-line block → 16-line replacement)

**Replaces:**

```java
        this.currentQueueSize = new AtomicLong(computeQueueSize());
        this.retentionTime = retentionTime;

        cleanupTempFiles();
        updateOldestSegmentReference();
        currentSegmentIndex = listSegmentPaths(queuePath)
                .map(s -> s.getFileName().toString().split("\\.")[0])
                .mapToInt(Integer::parseInt)
                .max().orElse(0);
        nextWriter();
        this.lastEntryTimestamp = Timestamp.now();
        this.flusherService = flusherService;
        this.flusherService.repeatedAction(this::scheduledFlushCheck);

        setupConsumedSegmentsNotificationWatcher();
    }
```

**With:**

```java
        this.currentQueueSize = new AtomicLong(computeQueueSize());
        this.retentionPolicyManager = new RetentionPolicyManager(queuePath, maxQueueSize, storageType, retentionTime, clock, currentQueueSize, expiredEvents);

        cleanupTempFiles();
        retentionPolicyManager.updateOldestSegmentReference();
        currentSegmentIndex = listSegmentPaths(queuePath)
                .map(s -> s.getFileName().toString().split("\\.")[0])
                .mapToInt(Integer::parseInt)
                .max().orElse(0);
        nextWriter();
        this.lastEntryTimestamp = Timestamp.now();
        this.flusherService = flusherService;
        this.flusherService.repeatedAction(this::scheduledFlushCheck);

        setupConsumedSegmentsNotificationWatcher();
    }
```

### 3. EDIT `logstash-core/src/main/java/org/logstash/common/io/DeadLetterQueueWriter.java` (6-line block → 11-line replacement)

**Replaces:**

```java
        int eventPayloadSize = RECORD_HEADER_SIZE + record.length;
        executeAgeRetentionPolicy();
        boolean skipWrite = executeStoragePolicy(eventPayloadSize);
        if (skipWrite) {
            return;
        }
```

**With:**

```java
        int eventPayloadSize = RECORD_HEADER_SIZE + record.length;
        retentionPolicyManager.executeAgeRetentionPolicy();
        boolean skipWrite = retentionPolicyManager.executeStoragePolicy(eventPayloadSize, () -> {
            try { this.currentQueueSize.set(computeQueueSize()); } catch (IOException e) { logger.warn("Size refresh failed", e); }
        });
        if (skipWrite) {
            lastError = String.format("Cannot write event to DLQ(path: %s): reached maxQueueSize of %d", queuePath, maxQueueSize);
            logger.error(lastError);
            droppedEvents.add(1L);
            return;
        }
```

### 4. EDIT `logstash-core/src/main/java/org/logstash/common/io/DeadLetterQueueWriter.java` (134-line block → 6-line replacement)

**Replaces:**

```java
    private void executeAgeRetentionPolicy() {
        if (isOldestSegmentExpired()) {
            try {
                deleteExpiredSegments();
            } catch (IOException ex) {
                logger.error("Can't remove some DLQ files while cleaning expired segments", ex);
            }
        }
    }

    /**
     * @param eventPayloadSize payload size in bytes.
     * @return boolean true if event write has to be skipped.
     * */
    private boolean executeStoragePolicy(int eventPayloadSize) {
        if (!exceedMaxQueueSize(eventPayloadSize)) {
            return false;
        }

        // load currentQueueSize from filesystem because there could be a consumer
        // that's already cleaning
        try {
            this.currentQueueSize.set(computeQueueSize());
        } catch (IOException ex) {
            logger.warn("Unable to determine DLQ size, skipping storage policy check", ex);
            return false;
        }

        // after reload verify the condition is still valid
        if (!exceedMaxQueueSize(eventPayloadSize)) {
            return false;
        }

        if (storageType == QueueStorageType.DROP_NEWER) {
            lastError = String.format("Cannot write event to DLQ(path: %s): reached maxQueueSize of %d", queuePath, maxQueueSize);
            logger.error(lastError);
            droppedEvents.add(1L);
            return true;
        } else {
            try {
                do {
                    dropTailSegment();
                } while (exceedMaxQueueSize(eventPayloadSize));
            } catch (IOException ex) {
                logger.error("Can't remove some DLQ files while removing older segments", ex);
            }
            return false;
        }
    }

    private boolean exceedMaxQueueSize(int eventPayloadSize) {
        return currentQueueSize.longValue() + eventPayloadSize > maxQueueSize;
    }

    private boolean isOldestSegmentExpired() {
        if (retentionTime == null) {
            return false;
        }
        final Instant now = clock.instant();
        return oldestSegmentTimestamp
... (74 more line(s) truncated)
```

**With:**

```java
>>>>>>> REPLACE

<<<<<<< SEARCH logstash-core/src/main/java/org/logstash/common/io/DeadLetterQueueWriter.java
    static Optional<Timestamp> readTimestampOfLastEventInSegment(Path segmentPath) throws IOException {
=======
    public static Optional<Timestamp> readTimestampOfLastEventInSegment(Path segmentPath) throws IOException {
```

### 5. EDIT `logstash-core/src/main/java/org/logstash/common/io/DeadLetterQueueWriter.java` (12-line block → 18-line replacement)

**Replaces:**

```java
    // package-private for testing
    void dropTailSegment() throws IOException {
        // remove oldest segment
        final Optional<Path> oldestSegment = listSegmentPathsSortedBySegmentId(queuePath).findFirst();
        if (oldestSegment.isPresent()) {
            final Path beheadedSegment = oldestSegment.get();
            deleteTailSegment(beheadedSegment, "dead letter queue size exceeded dead_letter_queue.max_bytes size(" + maxQueueSize + ")");
        } else {
            logger.info("Queue size {} exceeded, but no complete DLQ segments found", maxQueueSize);
        }
        this.currentQueueSize.set(computeQueueSize());
    }
```

**With:**

```java
>>>>>>> REPLACE

<<<<<<< SEARCH logstash-core/src/main/java/org/logstash/common/io/DeadLetterQueueWriter.java
        lock.lock();
        try {
            finalizeSegment(FinalizeWhen.ONLY_IF_STALE, SealReason.SCHEDULED_FLUSH);

            updateOldestSegmentReference();
            executeAgeRetentionPolicy();
        } catch (Exception e) {
=======
        lock.lock();
        try {
            finalizeSegment(FinalizeWhen.ONLY_IF_STALE, SealReason.SCHEDULED_FLUSH);

            retentionPolicyManager.updateOldestSegmentReference();
            retentionPolicyManager.executeAgeRetentionPolicy();
        } catch (Exception e) {
```

### 6. EDIT `logstash-core/src/main/java/org/logstash/common/io/DeadLetterQueueWriter.java` (11-line block → 11-line replacement)

**Replaces:**

```java
                if (currentWriter.hasWritten()) {
                    currentWriter.close();
                    sealSegment(currentSegmentIndex, sealReason);
                } else {
                    logger.debug("Current head segment {} is untouched", currentWriter.getPath().getFileName());
                }
                updateOldestSegmentReference();
                executeAgeRetentionPolicy();
                if (isOpen() && currentWriter.hasWritten()) {
                    nextWriter();
                }
```

**With:**

```java
                if (currentWriter.hasWritten()) {
                    currentWriter.close();
                    sealSegment(currentSegmentIndex, sealReason);
                } else {
                    logger.debug("Current head segment {} is untouched", currentWriter.getPath().getFileName());
                }
                retentionPolicyManager.updateOldestSegmentReference();
                retentionPolicyManager.executeAgeRetentionPolicy();
                if (isOpen() && currentWriter.hasWritten()) {
                    nextWriter();
                }
```

### 7. CREATE `logstash-core/src/main/java/org/logstash/common/io/RetentionPolicyManager.java` (112 line(s))

```java
package org.logstash.common.io;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.logstash.DLQEntry;
import org.logstash.Timestamp;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.NoSuchFileException;
import java.nio.file.Path;
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.atomic.LongAdder;

import static org.logstash.common.io.DeadLetterQueueUtils.listSegmentPathsSortedBySegmentId;

public final class RetentionPolicyManager {
    private static final Logger logger = LogManager.getLogger(RetentionPolicyManager.class);
    private final Path queuePath;
    private final long maxQueueSize;
    private final QueueStorageType storageType;
    private final Duration retentionTime;
    private final Clock clock;
    private final AtomicLong currentQueueSize;
    private final LongAdder expiredEvents;
    private volatile Optional<Timestamp> oldestSegmentTimestamp = Optional.empty();
    private volatile Optional<Path> oldestSegmentPath = Optional.empty();

    public RetentionPolicyManager(Path queuePath, long maxQueueSize, QueueStorageType storageType, 
                                  Duration retentionTime, Clock clock, AtomicLong currentQueueSize, LongAdder expiredEvents) {
        this.queuePath = queuePath;
        this.maxQueueSize = maxQueueSize;
        this.storageType = storageType;
        this.retentionTime = retentionTime;
        this.clock = clock;
        this.currentQueueSize = currentQueueSize;
        this.expiredEvents = expiredEvents;
    }

    public void updateOldestSegmentReference() throws IOException {
        oldestSegmentPath = listSegmentPathsSortedBySegmentId(this.queuePath)
                .filter(p -> p.toFile().length() > 1)
                .findFirst();
        if (!oldestSegmentPath.isPresent()) {
            oldestSegmentTimestamp = Optional.empty();
            return;
        }
        oldestSegmentTimestamp = DeadLetterQueueWriter.readTimestampOfLastEventInSegment(oldestSegmentPath.get());
        if (!oldestSegmentTimestamp.isPresent()) {
            oldestSegmentPath = Optional.empty();
        }
    }

    public void executeAgeRetentionPolicy() {
        if (retentionTime == null) return;
        final Instant now = clock.instant();
        boolean expired = oldestSegmentTimestamp.map(t -> t.toInstant().isBefore(now.minus(retentionTime))).orElse(false);
... (52 more line(s) truncated)
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `logstash-core/src/main/java/org/logstash/common/io/DeadLetterQueueWriter.java` | 690 → 593 | 48 → 44 | 2.9 → 2.5 | 92 → 67 | 0 → 0 |
| `logstash-core/src/main/java/org/logstash/common/io/RetentionPolicyManager.java` | - → 102 | - → 5 | - → 4.6 | - → 19 | - → 0 |

## Diff

```diff
diff --git a/logstash-core/src/main/java/org/logstash/common/io/DeadLetterQueueWriter.java b/logstash-core/src/main/java/org/logstash/common/io/DeadLetterQueueWriter.java
index 94a25ad..cfbd1b3 100644
--- a/logstash-core/src/main/java/org/logstash/common/io/DeadLetterQueueWriter.java
+++ b/logstash-core/src/main/java/org/logstash/common/io/DeadLetterQueueWriter.java
@@ -150,9 +150,7 @@ public final class DeadLetterQueueWriter implements Closeable {
     private final LongAdder expiredEvents = new LongAdder();
     private volatile String lastError = "no errors";
     private final Clock clock;
-    private volatile Optional<Timestamp> oldestSegmentTimestamp;
-    private volatile Optional<Path> oldestSegmentPath = Optional.empty();
-    private final TemporalAmount retentionTime;
+    private final RetentionPolicyManager retentionPolicyManager;
     private final SchedulerService flusherService;
     private ScheduledExecutorService scheduledFSWatcher = Executors.newScheduledThreadPool(1, r -> {
         Thread t = new Thread(r);
@@ -299,10 +297,10 @@ public final class DeadLetterQueueWriter implements Closeable {
         this.storageType = storageType;
         this.flushInterval = flushInterval;
         this.currentQueueSize = new AtomicLong(computeQueueSize());
-        this.retentionTime = retentionTime;
+        this.retentionPolicyManager = new RetentionPolicyManager(queuePath, maxQueueSize, storageType, retentionTime, clock, currentQueueSize, expiredEvents);
 
         cleanupTempFiles();
-        updateOldestSegmentReference();
+        retentionPolicyManager.updateOldestSegmentReference();
         currentSegmentIndex = listSegmentPaths(queuePath)
                 .map(s -> s.getFileName().toString().split("\\.")[0])
                 .mapToInt(Integer::parseInt)
@@ -455,9 +453,14 @@ public final class DeadLetterQueueWriter implements Closeable {
         }
         byte[] record = entry.serialize();
         int eventPayloadSize = RECORD_HEADER_SIZE + record.length;
-        executeAgeRetentionPolicy();
-        boolean skipWrite = executeStoragePolicy(eventPayloadSize);
+        retentionPolicyManager.executeAgeRetentionPolicy();
+        boolean skipWrite = retentionPolicyManager.executeStoragePolicy(eventPayloadSize, () -> {
+            try { this.currentQueueSize.set(computeQueueSize()); } catch (IOException e) { logger.warn("Size refresh failed", e); }
+        });
         if (skipWrite) {
+            lastError = String.format("Cannot write event to DLQ(path: %s): reached maxQueueSize of %d", queuePath, maxQueueSize);
+            logger.error(lastError);
+            droppedEvents.add(1L);
             return;
         }
 
@@ -472,140 +475,12 @@ public final class DeadLetterQueueWriter implements Closeable {
         return currentWriter.getPosition() + eventPayloadSize > maxSegmentSize;
     }
 
-    private void executeAgeRetentionPolicy() {
-        if (isOldestSegmentExpired()) {
-            try {
-                deleteExpiredSegments();
-            } catch (IOException ex) {
-                logger.error("Can't remove some DLQ files while cleaning expired segments", ex);
-            }
-        }
-    }
-
-    /**
-     * @param eventPayloadSize payload size in bytes.
-     * @return boolean true if event write has to be skipped.
-     * */
-    private boolean executeStoragePolicy(int eventPayloadSize) {
-        if (!exceedMaxQueueSize(eventPayloadSize)) {
-            return false;
-        }
-
-        // load currentQueueSize from filesystem because there could be a consumer
-        // that's already cleaning
-        try {
-            this.currentQueueSize.set(computeQueueSize());
-        } catch (IOException ex) {
-            logger.warn("Unable to determine DLQ size, skipping storage policy check", ex);
-            return false;
-        }
-
-        // after reload verify the condition is still valid
-        if (!exceedMaxQueueSize(eventPayloadSize)) {
-            return false;
-        }
-
-        if (storageType == QueueStorageType.DROP_NEWER) {
-            lastError = String.format("Cannot write event to DLQ(path: %s): reached maxQueueSize of %d", queuePath, maxQueueSize);
-            logger.error(lastError);
-            droppedEvents.add(1L);
-            return true;
-        } else {
-            try {
-                do {
-                    dropTailSegment();
-                } while (exceedMaxQueueSize(eventPayloadSize));
-            } catch (IOException ex) {
-                logger.error("Can't remove some DLQ files while removing older segments", ex);
-            }
-            return false;
-        }
-    }
-
-    private boolean exceedMaxQueueSize(int eventPayloadSize) {
-        return currentQueueSize.longValue() + eventPayloadSize > maxQueueSize;
-    }
-
-    private boolean isOldestSegmentExpired() {
-        if (retentionTime == null) {
-            return false;
-        }
-        final Instant now = clock.instant();
-        return oldestSegmentTimestamp
-                .map(t -> t.toInstant().isBefore(now.minus(retentionTime)))
-                .orElse(false);
-    }
-
-    private void deleteExpiredSegments() throws IOException {
-        // remove all the old segments that verifies the age retention condition
-        boolean cleanNextSegment;
-        do {
-            if (oldestSegmentPath.isPresent()) {
-                Path beheadedSegment = oldestSegmentPath.get();
-                expiredEvents.add(deleteTailSegment(beheadedSegment, "age retention policy"));
-            }
-            updateOldestSegmentReference();
-            cleanNextSegment = isOldestSegmentExpired();
-        } while (cleanNextSegment);
-
-        this.currentQueueSize.set(computeQueueSize());
-    }
+>>>>>>> REPLACE
 
-    /**
-     * Deletes the segment path, if present. Also return the number of events it contains.
-     *
-     * @param segment
-     *      The segment file to delete.
-     * @param motivation
-     *      Description of delete motivation.
-     * @return the number of events contained in the segment or 0 if the segment was already removed.
-     * @throws IOException if any other IO related error happens during deletion of the segment.
-     * */
-    private long deleteTailSegment(Path segment, String motivation) throws IOException {
-        try {
-            long eventsInSegment = DeadLetterQueueUtils.countEventsInSegment(segment);
-            Files.delete(segment);
-            logger.debug("Removed segment file {} due to {}", segment, motivation);
-            return eventsInSegment;
-        } catch (NoSuchFileException nsfex) {
-            // the last segment was deleted by another process, maybe the reader that's cleaning consumed segments
-            logger.debug("File not found {}, maybe removed by the reader pipeline", segment);
-            return 0;
-        }
-    }
-
-    // package-private for testing
-    void updateOldestSegmentReference() throws IOException {
-        final Optional<Path> previousOldestSegmentPath = oldestSegmentPath;
-        oldestSegmentPath = listSegmentPathsSortedBySegmentId(this.queuePath)
-                .filter(p -> p.toFile().length() > 1) // take the files that have content to process
-                .findFirst();
-        if (!oldestSegmentPath.isPresent()) {
-            oldestSegmentTimestamp = Optional.empty();
-            return;
-        }
-
-        boolean previousPathEqualsToCurrent = previousOldestSegmentPath.isPresent() && // contains a value
-                previousOldestSegmentPath.get().equals(oldestSegmentPath.get()); // and the value is the same as the current
-        if (!previousPathEqualsToCurrent) {
-            // oldest segment path has changed
-            logger.debug("Oldest segment is {}", oldestSegmentPath.get());
-        }
-
-        // extract the newest timestamp from the oldest segment
-        Optional<Timestamp> foundTimestamp = readTimestampOfLastEventInSegment(oldestSegmentPath.get());
-        if (!foundTimestamp.isPresent()) {
-            // clean also the last segment, because doesn't contain a timestamp (corrupted maybe)
-            // or is not present anymore
-            oldestSegmentPath = Optional.empty();
-        }
-        oldestSegmentTimestamp = foundTimestamp;
-    }
-
-    // package-private for testing
-    Optional<Path> getOldestSegmentPath() {
-        return oldestSegmentPath;
-    }
+<<<<<<< SEARCH logstash-core/src/main/java/org/logstash/common/io/DeadLetterQueueWriter.java
+    static Optional<Timestamp> readTimestampOfLastEventInSegment(Path segmentPath) throws IOException {
+=======
+    public static Optional<Timestamp> readTimestampOfLastEventInSegment(Path segmentPath) throws IOException {
 
     /**
      * Extract the timestamp from the last DLQEntry it finds in the given segment.
@@ -631,18 +506,24 @@ public final class DeadLetterQueueWriter implements Closeable {
         return Optional.of(DLQEntry.deserialize(eventBytes).getEntryTime());
     }
 
-    // package-private for testing
-    void dropTailSegment() throws IOException {
-        // remove oldest segment
-        final Optional<Path> oldestSegment = listSegmentPathsSortedBySegmentId(queuePath).findFirst();
-        if (oldestSegment.isPresent()) {
-            final Path beheadedSegment = oldestSegment.get();
-            deleteTailSegment(beheadedSegment, "dead letter queue size exceeded dead_letter_queue.max_bytes size(" + maxQueueSize + ")");
-        } else {
-            logger.info("Queue size {} exceeded, but no complete DLQ segments found", maxQueueSize);
-        }
-        this.currentQueueSize.set(computeQueueSize());
-    }
+>>>>>>> REPLACE
+
+<<<<<<< SEARCH logstash-core/src/main/java/org/logstash/common/io/DeadLetterQueueWriter.java
+        lock.lock();
+        try {
+            finalizeSegment(FinalizeWhen.ONLY_IF_STALE, SealReason.SCHEDULED_FLUSH);
+
+            updateOldestSegmentReference();
+            executeAgeRetentionPolicy();
+        } catch (Exception e) {
+=======
+        lock.lock();
+        try {
+            finalizeSegment(FinalizeWhen.ONLY_IF_STALE, SealReason.SCHEDULED_FLUSH);
+
+            retentionPolicyManager.updateOldestSegmentReference();
+            retentionPolicyManager.executeAgeRetentionPolicy();
+        } catch (Exception e) {
 
     /**
      * Method to determine whether the event has already been processed by the DLQ - currently this
@@ -695,8 +576,8 @@ public final class DeadLetterQueueWriter implements Closeable {
                 } else {
                     logger.debug("Current head segment {} is untouched", currentWriter.getPath().getFileName());
                 }
-                updateOldestSegmentReference();
-                executeAgeRetentionPolicy();
+                retentionPolicyManager.updateOldestSegmentReference();
+                retentionPolicyManager.executeAgeRetentionPolicy();
                 if (isOpen() && currentWriter.hasWritten()) {
                     nextWriter();
                 }
diff --git a/logstash-core/src/main/java/org/logstash/common/io/RetentionPolicyManager.java b/logstash-core/src/main/java/org/logstash/common/io/RetentionPolicyManager.java
new file mode 100644
index 0000000..0000000
--- /dev/null
+++ b/logstash-core/src/main/java/org/logstash/common/io/RetentionPolicyManager.java
@@ -0,0 +1,112 @@
+package org.logstash.common.io;
+
+import org.apache.logging.log4j.LogManager;
+import org.apache.logging.log4j.Logger;
+import org.logstash.DLQEntry;
+import org.logstash.Timestamp;
+import java.io.IOException;
+import java.nio.file.Files;
+import java.nio.file.NoSuchFileException;
+import java.nio.file.Path;
+import java.time.Clock;
+import java.time.Duration;
+import java.time.Instant;
+import java.util.Optional;
+import java.util.concurrent.atomic.AtomicLong;
+import java.util.concurrent.atomic.LongAdder;
+
+import static org.logstash.common.io.DeadLetterQueueUtils.listSegmentPathsSortedBySegmentId;
+
+public final class RetentionPolicyManager {
+    private static final Logger logger = LogManager.getLogger(RetentionPolicyManager.class);
+    private final Path queuePath;
+    private final long maxQueueSize;
+    private final QueueStorageType storageType;
+    private final Duration retentionTime;
+    private final Clock clock;
+    private final AtomicLong currentQueueSize;
+    private final LongAdder expiredEvents;
+    private volatile Optional<Timestamp> oldestSegmentTimestamp = Optional.empty();
+    private volatile Optional<Path> oldestSegmentPath = Optional.empty();
+
+    public RetentionPolicyManager(Path queuePath, long maxQueueSize, QueueStorageType storageType, 
+                                  Duration retentionTime, Clock clock, AtomicLong currentQueueSize, LongAdder expiredEvents) {
+        this.queuePath = queuePath;
+        this.maxQueueSize = maxQueueSize;
+        this.storageType = storageType;
+        this.retentionTime = retentionTime;
+        this.clock = clock;
+        this.currentQueueSize = currentQueueSize;
+        this.expiredEvents = expiredEvents;
+    }
+
+    public void updateOldestSegmentReference() throws IOException {
+        oldestSegmentPath = listSegmentPathsSortedBySegmentId(this.queuePath)
+                .filter(p -> p.toFile().length() > 1)
+                .findFirst();
+        if (!oldestSegmentPath.isPresent()) {
+            oldestSegmentTimestamp = Optional.empty();
+            return;
+        }
+        oldestSegmentTimestamp = DeadLetterQueueWriter.readTimestampOfLastEventInSegment(oldestSegmentPath.get());
+        if (!oldestSegmentTimestamp.isPresent()) {
+            oldestSegmentPath = Optional.empty();
+        }
+    }
+
+    public void executeAgeRetentionPolicy() {
+        if (retentionTime == null) return;
+        final Instant now = clock.instant();
+        boolean expired = oldestSegmentTimestamp.map(t -> t.toInstant().isBefore(now.minus(retentionTime))).orElse(false);
+        if (expired) {
+            try {
+                boolean cleanNext;
+                do {
+                    if (oldestSegmentPath.isPresent()) {
+                        expiredEvents.add(deleteTailSegment(oldestSegmentPath.get(), "age retention policy"));
+                    }
+                    updateOldestSegmentReference();
+                    cleanNext = oldestSegmentTimestamp.map(t -> t.toInstant().isBefore(now.minus(retentionTime))).orElse(false);
+                } while (cleanNext);
+            } catch (IOException ex) {
+                logger.error("Can't remove some DLQ files while cleaning expired segments", ex);
+            }
+        }
+    }
+
+    public boolean executeStoragePolicy(int eventPayloadSize, Runnable refreshSize) {
+        if (currentQueueSize.longValue() + eventPayloadSize <= maxQueueSize) return false;
+        refreshSize.run();
+        if (currentQueueSize.longValue() + eventPayloadSize <= maxQueueSize) return false;
+
+        if (storageType == QueueStorageType.DROP_NEWER) return true;
+        try {
+            do {
+                dropTailSegment();
+            } while (currentQueueSize.longValue() + eventPayloadSize > maxQueueSize);
+        } catch (IOException ex) {
+            logger.error("Can't remove some DLQ files while removing older segments", ex);
+        }
+        return false;
+    }
+
+    private void dropTailSegment() throws IOException {
+        listSegmentPathsSortedBySegmentId(queuePath).findFirst().ifPresent(p -> {
+            try {
+                deleteTailSegment(p, "dead letter queue size exceeded max_bytes");
+            } catch (IOException e) {
+                logger.error("Error dropping tail segment", e);
+            }
+        });
+    }
+
+    private long deleteTailSegment(Path segment, String motivation) throws IOException {
+        try {
+            long events = DeadLetterQueueUtils.countEventsInSegment(segment);
+            Files.delete(segment);
+            return events;
+        } catch (NoSuchFileException nsfex) {
+            return 0;
+        }
+    }
+}
\ No newline at end of file

```
