# Refactor DIP-008 (DIP): High-level module directly instantiates RecordIOWriter

**Status:** `applied_unverified`  
**Branch:** `refactor/DIP-008` -> `main`  
**Head commit:** `976f844ddb91d13914b7732d9991cf5258f2e23f`  
**LLM finish:** `FinishReason.STOP` (prompt 7971, completion 1535)  

## Detected issue

- **File**: `logstash-core/src/main/java/org/logstash/common/io/DeadLetterQueueWriter.java`
- **Entity**: `DeadLetterQueueWriter.nextWriter` (method)
- **Lines (at detection time)**: L579–L583
- **Severity**: high
- **Confidence**: detected by 7 scan(s)

**Description.** High-level module directly instantiates RecordIOWriter

**Reasoning.** The DeadLetterQueueWriter directly instantiates the concrete class RecordIOWriter. This creates a hard-coded dependency on a low-level detail, preventing the use of alternative writers and complicating unit testing.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 4
- **Files created** (1): `logstash-core/src/main/java/org/logstash/common/io/RecordIOWriterFactory.java`
- **Files modified** (1): `logstash-core/src/main/java/org/logstash/common/io/DeadLetterQueueWriter.java`

**Summary.** Introduce a factory interface for RecordIOWriter to decouple DeadLetterQueueWriter from concrete implementation.

**Rationale.** The DeadLetterQueueWriter was directly instantiating RecordIOWriter. By introducing a RecordIOWriterFactory, we allow the writer to depend on an abstraction, enabling better testability and adherence to the Dependency Inversion Principle.

## Changes overview

_4 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `logstash-core/src/main/java/org/logstash/common/io/DeadLetterQueueWriter.java` (3-line block → 4-line replacement)

**Replaces:**

```java
    private final Clock clock;
    private final RetentionPolicyManager retentionPolicyManager;
    private final SchedulerService flusherService;
```

**With:**

```java
    private final Clock clock;
    private final RetentionPolicyManager retentionPolicyManager;
    private final SchedulerService flusherService;
    private final RecordIOWriterFactory writerFactory;
```

### 2. EDIT `logstash-core/src/main/java/org/logstash/common/io/DeadLetterQueueWriter.java` (27-line block → 34-line replacement)

**Replaces:**

```java
    private DeadLetterQueueWriter(final Path queuePath, final long maxSegmentSize, final long maxQueueSize,
                                  final Duration flushInterval, final QueueStorageType storageType, final Duration retentionTime,
                                  final Clock clock, SchedulerService flusherService) throws IOException {
        this.clock = clock;

        this.fileLock = FileLockFactory.obtainLock(queuePath, LOCK_FILE);
        this.queuePath = queuePath;
        this.maxSegmentSize = maxSegmentSize;
        this.maxQueueSize = maxQueueSize;
        this.storageType = storageType;
        this.flushInterval = flushInterval;
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

**With:**

```java
    private DeadLetterQueueWriter(final Path queuePath, final long maxSegmentSize, final long maxQueueSize,
                                  final Duration flushInterval, final QueueStorageType storageType, final Duration retentionTime,
                                  final Clock clock, SchedulerService flusherService) throws IOException {
        this(queuePath, maxSegmentSize, maxQueueSize, flushInterval, storageType, retentionTime, clock, flusherService, RecordIOWriter::new);
    }

    private DeadLetterQueueWriter(final Path queuePath, final long maxSegmentSize, final long maxQueueSize,
                                  final Duration flushInterval, final QueueStorageType storageType, final Duration retentionTime,
                                  final Clock clock, SchedulerService flusherService, RecordIOWriterFactory writerFactory) throws IOException {
        this.clock = clock;
        this.writerFactory = writerFactory;

        this.fileLock = FileLockFactory.obtainLock(queuePath, LOCK_FILE);
        this.queuePath = queuePath;
        this.maxSegmentSize = maxSegmentSize;
        this.maxQueueSize = maxQueueSize;
        this.storageType = storageType;
        this.flushInterval = flushInterval;
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

### 3. EDIT `logstash-core/src/main/java/org/logstash/common/io/DeadLetterQueueWriter.java` (6-line block → 6-line replacement)

**Replaces:**

```java
    private void nextWriter() throws IOException {
        Path nextSegmentPath = queuePath.resolve(String.format(TEMP_FILE_PATTERN, ++currentSegmentIndex));
        currentWriter = new RecordIOWriter(nextSegmentPath);
        currentQueueSize.incrementAndGet();
        logger.debug("Created new head segment {}", nextSegmentPath);
    }
```

**With:**

```java
    private void nextWriter() throws IOException {
        Path nextSegmentPath = queuePath.resolve(String.format(TEMP_FILE_PATTERN, ++currentSegmentIndex));
        currentWriter = writerFactory.create(nextSegmentPath);
        currentQueueSize.incrementAndGet();
        logger.debug("Created new head segment {}", nextSegmentPath);
    }
```

### 4. CREATE `logstash-core/src/main/java/org/logstash/common/io/RecordIOWriterFactory.java` (26 line(s))

```java
/*
 * Licensed to Elasticsearch B.V. under one or more contributor
 * license agreements. See the NOTICE file distributed with
 * this work for additional information regarding copyright
 * ownership. Elasticsearch B.V. licenses this file to you under
 * the Apache License, Version 2.0 (the "License"); you may
 * not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *	http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */
package org.logstash.common.io;

import java.io.IOException;
import java.nio.file.Path;

public interface RecordIOWriterFactory {
    RecordIOWriter create(Path path) throws IOException;
}
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `logstash-core/src/main/java/org/logstash/common/io/DeadLetterQueueWriter.java` | 584 → 591 | 44 → 44 | 2.41 → 2.41 | 63 → 63 | 0 → 0 |
| `logstash-core/src/main/java/org/logstash/common/io/RecordIOWriterFactory.java` | - → 24 | - → 0 | - → 3 | - → 3 | - → 0 |

## Diff

```diff
diff --git a/logstash-core/src/main/java/org/logstash/common/io/DeadLetterQueueWriter.java b/logstash-core/src/main/java/org/logstash/common/io/DeadLetterQueueWriter.java
index abfa460..52ef30c 100644
--- a/logstash-core/src/main/java/org/logstash/common/io/DeadLetterQueueWriter.java
+++ b/logstash-core/src/main/java/org/logstash/common/io/DeadLetterQueueWriter.java
@@ -152,6 +152,7 @@ public final class DeadLetterQueueWriter implements Closeable {
     private final Clock clock;
     private final RetentionPolicyManager retentionPolicyManager;
     private final SchedulerService flusherService;
+    private final RecordIOWriterFactory writerFactory;
     private ScheduledExecutorService scheduledFSWatcher = Executors.newScheduledThreadPool(1, r -> {
         Thread t = new Thread(r);
         //Allow this thread to die when the JVM dies
@@ -288,7 +289,14 @@ public final class DeadLetterQueueWriter implements Closeable {
     private DeadLetterQueueWriter(final Path queuePath, final long maxSegmentSize, final long maxQueueSize,
                                   final Duration flushInterval, final QueueStorageType storageType, final Duration retentionTime,
                                   final Clock clock, SchedulerService flusherService) throws IOException {
+        this(queuePath, maxSegmentSize, maxQueueSize, flushInterval, storageType, retentionTime, clock, flusherService, RecordIOWriter::new);
+    }
+
+    private DeadLetterQueueWriter(final Path queuePath, final long maxSegmentSize, final long maxQueueSize,
+                                  final Duration flushInterval, final QueueStorageType storageType, final Duration retentionTime,
+                                  final Clock clock, SchedulerService flusherService, RecordIOWriterFactory writerFactory) throws IOException {
         this.clock = clock;
+        this.writerFactory = writerFactory;
 
         this.fileLock = FileLockFactory.obtainLock(queuePath, LOCK_FILE);
         this.queuePath = queuePath;
@@ -614,7 +622,7 @@ public final class DeadLetterQueueWriter implements Closeable {
 
     private void nextWriter() throws IOException {
         Path nextSegmentPath = queuePath.resolve(String.format(TEMP_FILE_PATTERN, ++currentSegmentIndex));
-        currentWriter = new RecordIOWriter(nextSegmentPath);
+        currentWriter = writerFactory.create(nextSegmentPath);
         currentQueueSize.incrementAndGet();
         logger.debug("Created new head segment {}", nextSegmentPath);
     }
diff --git a/logstash-core/src/main/java/org/logstash/common/io/RecordIOWriterFactory.java b/logstash-core/src/main/java/org/logstash/common/io/RecordIOWriterFactory.java
new file mode 100644
index 0000000..0000000
--- /dev/null
+++ b/logstash-core/src/main/java/org/logstash/common/io/RecordIOWriterFactory.java
@@ -0,0 +1,26 @@
+/*
+ * Licensed to Elasticsearch B.V. under one or more contributor
+ * license agreements. See the NOTICE file distributed with
+ * this work for additional information regarding copyright
+ * ownership. Elasticsearch B.V. licenses this file to you under
+ * the Apache License, Version 2.0 (the "License"); you may
+ * not use this file except in compliance with the License.
+ * You may obtain a copy of the License at
+ *
+ *	http://www.apache.org/licenses/LICENSE-2.0
+ *
+ * Unless required by applicable law or agreed to in writing,
+ * software distributed under the License is distributed on an
+ * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
+ * KIND, either express or implied.  See the License for the
+ * specific language governing permissions and limitations
+ * under the License.
+ */
+package org.logstash.common.io;
+
+import java.io.IOException;
+import java.nio.file.Path;
+
+public interface RecordIOWriterFactory {
+    RecordIOWriter create(Path path) throws IOException;
+}
\ No newline at end of file

```
