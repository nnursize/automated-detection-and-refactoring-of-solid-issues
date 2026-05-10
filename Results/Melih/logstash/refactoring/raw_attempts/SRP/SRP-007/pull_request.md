# Refactor SRP-007 (SRP): Queue class manages logical queue operations alongside physical file system c...

**Status:** `applied_unverified`  
**Branch:** `refactor/SRP-007` -> `main`  
**Head commit:** `1c876b4b4de952ca93cb22874807365b68658b60`  
**LLM finish:** `FinishReason.STOP` (prompt 11151, completion 3956)  

## Detected issue

- **File**: `logstash-core/src/main/java/org/logstash/ackedqueue/Queue.java`
- **Entity**: `Queue` (class)
- **Lines (at detection time)**: L58–L740
- **Severity**: medium
- **Confidence**: detected by 9 scan(s)

**Description.** Queue class manages logical queue operations alongside physical file system concerns.

**Reasoning.** The Queue class handles the high-level logic of a persistent queue (read/write/ack) but is also responsible for low-level file system tasks like disk space availability checks, file locking, and directory-level upgrades (QueueUpgrade). These infrastructure concerns should be separated from the queue's behavioral logic.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 10
- **Files created** (1): `logstash-core/src/main/java/org/logstash/ackedqueue/QueueManager.java`
- **Files modified** (1): `logstash-core/src/main/java/org/logstash/ackedqueue/Queue.java`

**Summary.** Extract Queue infrastructure concerns into a dedicated QueueManager class

**Rationale.** The Queue class was violating SRP by managing both high-level queue logic and low-level infrastructure concerns (file locking, disk space checks, directory upgrades). I extracted these infrastructure responsibilities into a new QueueManager class to improve maintainability and separation of concerns.

## Changes overview

_10 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `logstash-core/src/main/java/org/logstash/ackedqueue/Queue.java` (45-line block → 35-line replacement)

**Replaces:**

```java
    private final Path dirPath;
    private final int maxUnread;
    private final int checkpointMaxAcks;
    private final int checkpointMaxWrites;

    private final AtomicBoolean closed;

    // deserialization
    private final Class<? extends Queueable> elementClass;
    private final Method deserializeMethod;
    private final CompressionCodec compressionCodec;

    // thread safety
    private final ReentrantLock lock = new ReentrantLock();
    private final Condition notFull  = lock.newCondition();
    private final Condition notEmpty = lock.newCondition();

    // exclusive dir access
    private FileLock dirLock;
    private final static String LOCK_NAME = ".lock";

    private static final Logger logger = LogManager.getLogger(Queue.class);

    private final Metric metric;


    public Queue(Settings settings) {
        this(settings, null);
    }

    public Queue(Settings settings, Metric metric) {
        this.metric = Objects.requireNonNullElseGet(metric, NamespacedMetricImpl::getNullMetric);
        try {
            final Path queueDir = Paths.get(settings.getDirPath());
            // Files.createDirectories raises a FileAlreadyExistsException
            // if queue dir is symlinked, so worth checking against Files.exists
            if (Files.exists(queueDir) == false) {
                Files.createDirectories(queueDir);
            }
            this.dirPath = queueDir.toRealPath();
        } catch (final IOException ex) {
            throw new IllegalStateException(QueueExceptionMessages.CANNOT_CREATE_QUEUE_DIR, ex);
        }

        this.pageCapacity = settings.getCapacity();
```

**With:**

```java
    private final QueueManager queueManager;
    private final int maxUnread;
    private final int checkpointMaxAcks;
    private final int checkpointMaxWrites;

    private final AtomicBoolean closed;

    // deserialization
    private final Class<? extends Queueable> elementClass;
    private final Method deserializeMethod;
    private final CompressionCodec compressionCodec;

    // thread safety
    private final ReentrantLock lock = new ReentrantLock();
    private final Condition notFull  = lock.newCondition();
    private final Condition notEmpty = lock.newCondition();

    private static final Logger logger = LogManager.getLogger(Queue.class);

    private final Metric metric;


    public Queue(Settings settings) {
        this(settings, null);
    }

    public Queue(Settings settings, Metric metric) {
        this.metric = Objects.requireNonNullElseGet(metric, NamespacedMetricImpl::getNullMetric);
        try {
            this.queueManager = new QueueManager(settings.getDirPath());
        } catch (final IOException ex) {
            throw new IllegalStateException(QueueExceptionMessages.CANNOT_CREATE_QUEUE_DIR, ex);
        }

        this.pageCapacity = settings.getCapacity();
```

### 2. EDIT `logstash-core/src/main/java/org/logstash/ackedqueue/Queue.java` (3-line block → 3-line replacement)

**Replaces:**

```java
    public String getDirPath() {
        return this.dirPath.toString();
    }
```

**With:**

```java
    public String getDirPath() {
        return this.queueManager.getDirPath().toString();
    }
```

### 3. EDIT `logstash-core/src/main/java/org/logstash/ackedqueue/Queue.java` (23-line block → 14-line replacement)

**Replaces:**

```java
        lock.lock();
        try {
            try {
                // verify exclusive access to the dirPath
                this.dirLock = FileLockFactory.obtainLock(this.dirPath, LOCK_NAME);
            } catch (LockException e) {
                throw new LockException("The queue failed to obtain exclusive access, cause: " + e.getMessage());
            }

            try {
                openPages();
                this.closed.set(false);
            } catch (IOException e) {
                // upon any exception while opening the queue and after dirlock has been obtained
                // we need to make sure to release the dirlock. Calling the close method on a partially
                // open queue has no effect because the closed flag is still true.
                releaseLockAndSwallow();
                throw(e);
            }
        } finally {
            lock.unlock();
        }
    }
```

**With:**

```java
        lock.lock();
        try {
            this.queueManager.acquireLock();
            try {
                openPages();
                this.closed.set(false);
            } catch (IOException e) {
                releaseLockAndSwallow();
                throw(e);
            }
        } finally {
            lock.unlock();
        }
    }
```

### 4. EDIT `logstash-core/src/main/java/org/logstash/ackedqueue/Queue.java` (24-line block → 24-line replacement)

**Replaces:**

```java
    private void openPages() throws IOException {
        final int headPageNum;

        // Upgrade to serialization format V2
        QueueUpgrade.upgradeQueueDirectoryToV2(dirPath);

        Checkpoint headCheckpoint;
        try {
            headCheckpoint = this.checkpointIO.read(checkpointIO.headFileName());
        } catch (NoSuchFileException e) {
            // if there is no head checkpoint, create a new headpage and checkpoint it and exit method

            logger.debug("No head checkpoint found at: {}, creating new head page", checkpointIO.headFileName());

            this.ensureDiskAvailable(this.maxBytes, 0);

            this.seqNum = 0;
            headPageNum = 0;

            newCheckpointedHeadpage(headPageNum);
            this.closed.set(false);

            return;
        }
```

**With:**

```java
    private void openPages() throws IOException {
        final int headPageNum;

        // Upgrade to serialization format V2
        this.queueManager.upgrade();

        Checkpoint headCheckpoint;
        try {
            headCheckpoint = this.checkpointIO.read(checkpointIO.headFileName());
        } catch (NoSuchFileException e) {
            // if there is no head checkpoint, create a new headpage and checkpoint it and exit method

            logger.debug("No head checkpoint found at: {}, creating new head page", checkpointIO.headFileName());

            this.queueManager.ensureDiskAvailable(this.maxBytes, 0);

            this.seqNum = 0;
            headPageNum = 0;

            newCheckpointedHeadpage(headPageNum);
            this.closed.set(false);

            return;
        }
```

### 5. EDIT `logstash-core/src/main/java/org/logstash/ackedqueue/Queue.java` (14-line block → 14-line replacement)

**Replaces:**

```java
        // reconstruct all tail pages state upto but excluding the head page
        for (int pageNum = headCheckpoint.getFirstUnackedPageNum(); pageNum < headCheckpoint.getPageNum(); pageNum++) {
            final String cpFileName = checkpointIO.tailFileName(pageNum);
            if (!dirPath.resolve(cpFileName).toFile().exists()) {
                continue;
            }
            final Checkpoint cp = this.checkpointIO.read(cpFileName);

            logger.debug("opening tail page: {}, in: {}, with checkpoint: {}", pageNum, this.dirPath, cp);

            PageIO pageIO = new MmapPageIOV2(pageNum, this.pageCapacity, this.dirPath);
            // important to NOT pageIO.open() just yet, we must first verify if it is fully acked in which case
            // we can purge it and we don't care about its integrity for example if it is of zero-byte file size.
            if (cp.isFullyAcked()) {
```

**With:**

```java
        // reconstruct all tail pages state upto but excluding the head page
        for (int pageNum = headCheckpoint.getFirstUnackedPageNum(); pageNum < headCheckpoint.getPageNum(); pageNum++) {
            final String cpFileName = checkpointIO.tailFileName(pageNum);
            if (!this.queueManager.getDirPath().resolve(cpFileName).toFile().exists()) {
                continue;
            }
            final Checkpoint cp = this.checkpointIO.read(cpFileName);

            logger.debug("opening tail page: {}, in: {}, with checkpoint: {}", pageNum, this.queueManager.getDirPath(), cp);

            PageIO pageIO = new MmapPageIOV2(pageNum, this.pageCapacity, this.queueManager.getDirPath());
            // important to NOT pageIO.open() just yet, we must first verify if it is fully acked in which case
            // we can purge it and we don't care about its integrity for example if it is of zero-byte file size.
            if (cp.isFullyAcked()) {
```

### 6. EDIT `logstash-core/src/main/java/org/logstash/ackedqueue/Queue.java` (7-line block → 7-line replacement)

**Replaces:**

```java
        logger.debug("opening head page: {}, in: {}, with checkpoint: {}", headCheckpoint.getPageNum(), this.dirPath, headCheckpoint);

        PageIO pageIO = new MmapPageIOV2(headCheckpoint.getPageNum(), this.pageCapacity, this.dirPath);
        pageIO.recover(); // optimistically recovers the head page data file and set minSeqNum and elementCount to the actual read/recovered data

        pqSizeBytes += (long) pageIO.getHead();
        ensureDiskAvailable(this.maxBytes, pqSizeBytes);
```

**With:**

```java
        logger.debug("opening head page: {}, in: {}, with checkpoint: {}", headCheckpoint.getPageNum(), this.queueManager.getDirPath(), headCheckpoint);

        PageIO pageIO = new MmapPageIOV2(headCheckpoint.getPageNum(), this.pageCapacity, this.queueManager.getDirPath());
        pageIO.recover(); // optimistically recovers the head page data file and set minSeqNum and elementCount to the actual read/recovered data

        pqSizeBytes += (long) pageIO.getHead();
        this.queueManager.ensureDiskAvailable(this.maxBytes, pqSizeBytes);
```

### 7. EDIT `logstash-core/src/main/java/org/logstash/ackedqueue/Queue.java` (22-line block → 22-line replacement)

**Replaces:**

```java
    private boolean cleanedUpFullyAckedCorruptedPage(Checkpoint headCheckpoint, long pqSizeBytes) throws IOException {
        if (headCheckpoint.isFullyAcked()) {
            PageIO pageIO = new MmapPageIOV2(headCheckpoint.getPageNum(), this.pageCapacity, this.dirPath);
            if (pageIO.isCorruptedPage()) {
                logger.debug("Queue is fully acked. Found zero byte page.{}. Recreate checkpoint.head and delete corrupted page", headCheckpoint.getPageNum());

                this.checkpointIO.purge(checkpointIO.headFileName());
                pageIO.purge();

                if (headCheckpoint.maxSeqNum() > this.seqNum) {
                    this.seqNum = headCheckpoint.maxSeqNum();
                }

                newCheckpointedHeadpage(headCheckpoint.getPageNum() + 1);

                pqSizeBytes += (long) pageIO.getHead();
                ensureDiskAvailable(this.maxBytes, pqSizeBytes);
                return true;
            }
        }
        return false;
    }
```

**With:**

```java
    private boolean cleanedUpFullyAckedCorruptedPage(Checkpoint headCheckpoint, long pqSizeBytes) throws IOException {
        if (headCheckpoint.isFullyAcked()) {
            PageIO pageIO = new MmapPageIOV2(headCheckpoint.getPageNum(), this.pageCapacity, this.queueManager.getDirPath());
            if (pageIO.isCorruptedPage()) {
                logger.debug("Queue is fully acked. Found zero byte page.{}. Recreate checkpoint.head and delete corrupted page", headCheckpoint.getPageNum());

                this.checkpointIO.purge(checkpointIO.headFileName());
                pageIO.purge();

                if (headCheckpoint.maxSeqNum() > this.seqNum) {
                    this.seqNum = headCheckpoint.maxSeqNum();
                }

                newCheckpointedHeadpage(headCheckpoint.getPageNum() + 1);

                pqSizeBytes += (long) pageIO.getHead();
                this.queueManager.ensureDiskAvailable(this.maxBytes, pqSizeBytes);
                return true;
            }
        }
        return false;
    }
```

### 8. EDIT `logstash-core/src/main/java/org/logstash/ackedqueue/Queue.java` (7-line block → 7-line replacement)

**Replaces:**

```java
    private void newCheckpointedHeadpage(int pageNum) throws IOException {
        PageIO headPageIO = new MmapPageIOV2(pageNum, this.pageCapacity, this.dirPath);
        headPageIO.create();
        logger.debug("created new head page: {}", headPageIO);
        this.headPage = PageFactory.newHeadPage(pageNum, this, headPageIO);
        this.headPage.forceCheckpoint();
    }
```

**With:**

```java
    private void newCheckpointedHeadpage(int pageNum) throws IOException {
        PageIO headPageIO = new MmapPageIOV2(pageNum, this.pageCapacity, this.queueManager.getDirPath());
        headPageIO.create();
        logger.debug("created new head page: {}", headPageIO);
        this.headPage = PageFactory.newHeadPage(pageNum, this, headPageIO);
        this.headPage.forceCheckpoint();
    }
```

### 9. EDIT `logstash-core/src/main/java/org/logstash/ackedqueue/Queue.java` (8-line block → 8-line replacement)

**Replaces:**

```java
    private void releaseLockAndSwallow() {
        try {
            FileLockFactory.releaseLock(this.dirLock);
        } catch (IOException e) {
            // log error and ignore
            logger.error("Queue close releaseLock failed, error={}", e.getMessage());
        }
    }
```

**With:**

```java
    private void releaseLockAndSwallow() {
        try {
            this.queueManager.releaseLock();
        } catch (IOException e) {
            // log error and ignore
            logger.error("Queue close releaseLock failed, error={}", e.getMessage());
        }
    }
```

### 10. CREATE `logstash-core/src/main/java/org/logstash/ackedqueue/QueueManager.java` (54 line(s))

```java
package org.logstash.ackedqueue;

import java.io.IOException;
import java.nio.channels.FileLock;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import org.logstash.FileLockFactory;
import org.logstash.LockException;
import org.logstash.common.FsUtil;

public final class QueueManager {
    private final Path dirPath;
    private FileLock dirLock;
    private final static String LOCK_NAME = ".lock";

    public QueueManager(String path) throws IOException {
        final Path queueDir = Paths.get(path);
        if (Files.exists(queueDir) == false) {
            Files.createDirectories(queueDir);
        }
        this.dirPath = queueDir.toRealPath();
    }

    public void upgrade() throws IOException {
        QueueUpgrade.upgradeQueueDirectoryToV2(dirPath);
    }

    public void acquireLock() throws IOException {
        try {
            this.dirLock = FileLockFactory.obtainLock(this.dirPath, LOCK_NAME);
        } catch (LockException e) {
            throw new LockException("The queue failed to obtain exclusive access, cause: " + e.getMessage());
        }
    }

    public void releaseLock() throws IOException {
        if (this.dirLock != null) {
            FileLockFactory.releaseLock(this.dirLock);
        }
    }

    public void ensureDiskAvailable(final long maxPqSize, long currentPqSize) throws IOException {
        if (!FsUtil.hasFreeSpace(this.dirPath, maxPqSize - currentPqSize)) {
            throw new IOException(
                    String.format("Unable to allocate %d more bytes for persisted queue on top of its current usage of %d bytes",
                            maxPqSize - currentPqSize, currentPqSize));
        }
    }

    public Path getDirPath() {
        return dirPath;
    }
}
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `logstash-core/src/main/java/org/logstash/ackedqueue/Queue.java` | 744 → 734 | 43 → 43 | 4.58 → 4.49 | 155 → 151 | 0 → 0 |
| `logstash-core/src/main/java/org/logstash/ackedqueue/QueueManager.java` | - → 46 | - → 5 | - → 2 | - → 6 | - → 0 |

## Diff

```diff
diff --git a/logstash-core/src/main/java/org/logstash/ackedqueue/Queue.java b/logstash-core/src/main/java/org/logstash/ackedqueue/Queue.java
index 42771a1..2a80b79 100644
--- a/logstash-core/src/main/java/org/logstash/ackedqueue/Queue.java
+++ b/logstash-core/src/main/java/org/logstash/ackedqueue/Queue.java
@@ -75,7 +75,7 @@ public final class Queue implements Closeable {
     private final CheckpointIO checkpointIO;
     private final int pageCapacity;
     private final long maxBytes;
-    private final Path dirPath;
+    private final QueueManager queueManager;
     private final int maxUnread;
     private final int checkpointMaxAcks;
     private final int checkpointMaxWrites;
@@ -92,10 +92,6 @@ public final class Queue implements Closeable {
     private final Condition notFull  = lock.newCondition();
     private final Condition notEmpty = lock.newCondition();
 
-    // exclusive dir access
-    private FileLock dirLock;
-    private final static String LOCK_NAME = ".lock";
-
     private static final Logger logger = LogManager.getLogger(Queue.class);
 
     private final Metric metric;
@@ -108,13 +104,7 @@ public final class Queue implements Closeable {
     public Queue(Settings settings, Metric metric) {
         this.metric = Objects.requireNonNullElseGet(metric, NamespacedMetricImpl::getNullMetric);
         try {
-            final Path queueDir = Paths.get(settings.getDirPath());
-            // Files.createDirectories raises a FileAlreadyExistsException
-            // if queue dir is symlinked, so worth checking against Files.exists
-            if (Files.exists(queueDir) == false) {
-                Files.createDirectories(queueDir);
-            }
-            this.dirPath = queueDir.toRealPath();
+            this.queueManager = new QueueManager(settings.getDirPath());
         } catch (final IOException ex) {
             throw new IllegalStateException(QueueExceptionMessages.CANNOT_CREATE_QUEUE_DIR, ex);
         }
@@ -143,7 +133,7 @@ public final class Queue implements Closeable {
     }
 
     public String getDirPath() {
-        return this.dirPath.toString();
+        return this.queueManager.getDirPath().toString();
     }
 
     public long getMaxBytes() {
@@ -187,20 +177,11 @@ public final class Queue implements Closeable {
 
         lock.lock();
         try {
-            try {
-                // verify exclusive access to the dirPath
-                this.dirLock = FileLockFactory.obtainLock(this.dirPath, LOCK_NAME);
-            } catch (LockException e) {
-                throw new LockException("The queue failed to obtain exclusive access, cause: " + e.getMessage());
-            }
-
+            this.queueManager.acquireLock();
             try {
                 openPages();
                 this.closed.set(false);
             } catch (IOException e) {
-                // upon any exception while opening the queue and after dirlock has been obtained
-                // we need to make sure to release the dirlock. Calling the close method on a partially
-                // open queue has no effect because the closed flag is still true.
                 releaseLockAndSwallow();
                 throw(e);
             }
@@ -213,7 +194,7 @@ public final class Queue implements Closeable {
         final int headPageNum;
 
         // Upgrade to serialization format V2
-        QueueUpgrade.upgradeQueueDirectoryToV2(dirPath);
+        this.queueManager.upgrade();
 
         Checkpoint headCheckpoint;
         try {
@@ -223,7 +204,7 @@ public final class Queue implements Closeable {
 
             logger.debug("No head checkpoint found at: {}, creating new head page", checkpointIO.headFileName());
 
-            this.ensureDiskAvailable(this.maxBytes, 0);
+            this.queueManager.ensureDiskAvailable(this.maxBytes, 0);
 
             this.seqNum = 0;
             headPageNum = 0;
@@ -242,14 +223,14 @@ public final class Queue implements Closeable {
         // reconstruct all tail pages state upto but excluding the head page
         for (int pageNum = headCheckpoint.getFirstUnackedPageNum(); pageNum < headCheckpoint.getPageNum(); pageNum++) {
             final String cpFileName = checkpointIO.tailFileName(pageNum);
-            if (!dirPath.resolve(cpFileName).toFile().exists()) {
+            if (!this.queueManager.getDirPath().resolve(cpFileName).toFile().exists()) {
                 continue;
             }
             final Checkpoint cp = this.checkpointIO.read(cpFileName);
 
-            logger.debug("opening tail page: {}, in: {}, with checkpoint: {}", pageNum, this.dirPath, cp);
+            logger.debug("opening tail page: {}, in: {}, with checkpoint: {}", pageNum, this.queueManager.getDirPath(), cp);
 
-            PageIO pageIO = new MmapPageIOV2(pageNum, this.pageCapacity, this.dirPath);
+            PageIO pageIO = new MmapPageIOV2(pageNum, this.pageCapacity, this.queueManager.getDirPath());
             // important to NOT pageIO.open() just yet, we must first verify if it is fully acked in which case
             // we can purge it and we don't care about its integrity for example if it is of zero-byte file size.
             if (cp.isFullyAcked()) {
@@ -272,13 +253,13 @@ public final class Queue implements Closeable {
         // transform the head page into a tail page only if the headpage is non-empty
         // in both cases it will be checkpointed to track any changes in the firstUnackedPageNum when reconstructing the tail pages
 
-        logger.debug("opening head page: {}, in: {}, with checkpoint: {}", headCheckpoint.getPageNum(), this.dirPath, headCheckpoint);
+        logger.debug("opening head page: {}, in: {}, with checkpoint: {}", headCheckpoint.getPageNum(), this.queueManager.getDirPath(), headCheckpoint);
 
-        PageIO pageIO = new MmapPageIOV2(headCheckpoint.getPageNum(), this.pageCapacity, this.dirPath);
+        PageIO pageIO = new MmapPageIOV2(headCheckpoint.getPageNum(), this.pageCapacity, this.queueManager.getDirPath());
         pageIO.recover(); // optimistically recovers the head page data file and set minSeqNum and elementCount to the actual read/recovered data
 
         pqSizeBytes += (long) pageIO.getHead();
-        ensureDiskAvailable(this.maxBytes, pqSizeBytes);
+        this.queueManager.ensureDiskAvailable(this.maxBytes, pqSizeBytes);
 
         if (pageIO.getMinSeqNum() != headCheckpoint.getMinSeqNum() || pageIO.getElementCount() != headCheckpoint.getElementCount()) {
             // the recovered page IO shows different minSeqNum or elementCount than the checkpoint, use the page IO attributes
@@ -336,7 +317,7 @@ public final class Queue implements Closeable {
      */
     private boolean cleanedUpFullyAckedCorruptedPage(Checkpoint headCheckpoint, long pqSizeBytes) throws IOException {
         if (headCheckpoint.isFullyAcked()) {
-            PageIO pageIO = new MmapPageIOV2(headCheckpoint.getPageNum(), this.pageCapacity, this.dirPath);
+            PageIO pageIO = new MmapPageIOV2(headCheckpoint.getPageNum(), this.pageCapacity, this.queueManager.getDirPath());
             if (pageIO.isCorruptedPage()) {
                 logger.debug("Queue is fully acked. Found zero byte page.{}. Recreate checkpoint.head and delete corrupted page", headCheckpoint.getPageNum());
 
@@ -350,7 +331,7 @@ public final class Queue implements Closeable {
                 newCheckpointedHeadpage(headCheckpoint.getPageNum() + 1);
 
                 pqSizeBytes += (long) pageIO.getHead();
-                ensureDiskAvailable(this.maxBytes, pqSizeBytes);
+                this.queueManager.ensureDiskAvailable(this.maxBytes, pqSizeBytes);
                 return true;
             }
         }
@@ -404,7 +385,7 @@ public final class Queue implements Closeable {
      * @throws IOException
      */
     private void newCheckpointedHeadpage(int pageNum) throws IOException {
-        PageIO headPageIO = new MmapPageIOV2(pageNum, this.pageCapacity, this.dirPath);
+        PageIO headPageIO = new MmapPageIOV2(pageNum, this.pageCapacity, this.queueManager.getDirPath());
         headPageIO.create();
         logger.debug("created new head page: {}", headPageIO);
         this.headPage = PageFactory.newHeadPage(pageNum, this, headPageIO);
@@ -823,7 +804,7 @@ public final class Queue implements Closeable {
 
     private void releaseLockAndSwallow() {
         try {
-            FileLockFactory.releaseLock(this.dirLock);
+            this.queueManager.releaseLock();
         } catch (IOException e) {
             // log error and ignore
             logger.error("Queue close releaseLock failed, error={}", e.getMessage());
diff --git a/logstash-core/src/main/java/org/logstash/ackedqueue/QueueManager.java b/logstash-core/src/main/java/org/logstash/ackedqueue/QueueManager.java
new file mode 100644
index 0000000..0000000
--- /dev/null
+++ b/logstash-core/src/main/java/org/logstash/ackedqueue/QueueManager.java
@@ -0,0 +1,54 @@
+package org.logstash.ackedqueue;
+
+import java.io.IOException;
+import java.nio.channels.FileLock;
+import java.nio.file.Files;
+import java.nio.file.Path;
+import java.nio.file.Paths;
+import org.logstash.FileLockFactory;
+import org.logstash.LockException;
+import org.logstash.common.FsUtil;
+
+public final class QueueManager {
+    private final Path dirPath;
+    private FileLock dirLock;
+    private final static String LOCK_NAME = ".lock";
+
+    public QueueManager(String path) throws IOException {
+        final Path queueDir = Paths.get(path);
+        if (Files.exists(queueDir) == false) {
+            Files.createDirectories(queueDir);
+        }
+        this.dirPath = queueDir.toRealPath();
+    }
+
+    public void upgrade() throws IOException {
+        QueueUpgrade.upgradeQueueDirectoryToV2(dirPath);
+    }
+
+    public void acquireLock() throws IOException {
+        try {
+            this.dirLock = FileLockFactory.obtainLock(this.dirPath, LOCK_NAME);
+        } catch (LockException e) {
+            throw new LockException("The queue failed to obtain exclusive access, cause: " + e.getMessage());
+        }
+    }
+
+    public void releaseLock() throws IOException {
+        if (this.dirLock != null) {
+            FileLockFactory.releaseLock(this.dirLock);
+        }
+    }
+
+    public void ensureDiskAvailable(final long maxPqSize, long currentPqSize) throws IOException {
+        if (!FsUtil.hasFreeSpace(this.dirPath, maxPqSize - currentPqSize)) {
+            throw new IOException(
+                    String.format("Unable to allocate %d more bytes for persisted queue on top of its current usage of %d bytes",
+                            maxPqSize - currentPqSize, currentPqSize));
+        }
+    }
+
+    public Path getDirPath() {
+        return dirPath;
+    }
+}
\ No newline at end of file

```
