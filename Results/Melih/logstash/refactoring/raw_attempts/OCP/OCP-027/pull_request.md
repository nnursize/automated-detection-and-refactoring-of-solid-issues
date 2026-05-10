# Refactor OCP-027 (OCP): The Queue class is tightly coupled to the concrete MmapPageIOV2 implementation.

**Status:** `applied_unverified`  
**Branch:** `refactor/OCP-027` -> `main`  
**Head commit:** `705051ab73604540c6a9008bdafefcf491c9fc04`  
**LLM finish:** `FinishReason.STOP` (prompt 11015, completion 1222)  

## Detected issue

- **File**: `logstash-core/src/main/java/org/logstash/ackedqueue/Queue.java`
- **Entity**: `Queue.openPages` (method)
- **Lines (at detection time)**: L165–L260
- **Severity**: medium
- **Confidence**: detected by 3 scan(s)

**Description.** The Queue class is tightly coupled to the concrete MmapPageIOV2 implementation.

**Reasoning.** The method openPages (and others like newCheckpointedHeadpage) explicitly instantiates MmapPageIOV2. If a new storage format or a V3 version of the page IO is introduced, the core Queue class must be modified. This should be abstracted behind a PageIO factory or injected via settings.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 5
- **Files created** (1): `logstash-core/src/main/java/org/logstash/ackedqueue/io/PageIOFactory.java`
- **Files modified** (1): `logstash-core/src/main/java/org/logstash/ackedqueue/Queue.java`

**Summary.** Introduce PageIOFactory to decouple Queue from MmapPageIOV2

**Rationale.** The Queue class was directly instantiating MmapPageIOV2. By introducing a PageIOFactory, we abstract the creation of PageIO implementations, allowing for future storage format extensions without modifying the Queue class.

## Changes overview

_5 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `logstash-core/src/main/java/org/logstash/ackedqueue/Queue.java` (7-line block → 7-line replacement)

**Replaces:**

```java
            final Checkpoint cp = this.checkpointIO.read(cpFileName);

            logger.debug("opening tail page: {}, in: {}, with checkpoint: {}", pageNum, this.queueManager.getDirPath(), cp);

            PageIO pageIO = new MmapPageIOV2(pageNum, this.pageCapacity, this.queueManager.getDirPath());
            // important to NOT pageIO.open() just yet, we must first verify if it is fully acked in which case
            // we can purge it and we don't care about its integrity for example if it is of zero-byte file size.
```

**With:**

```java
            final Checkpoint cp = this.checkpointIO.read(cpFileName);

            logger.debug("opening tail page: {}, in: {}, with checkpoint: {}", pageNum, this.queueManager.getDirPath(), cp);

            PageIO pageIO = PageIOFactory.create(pageNum, this.pageCapacity, this.queueManager.getDirPath());
            // important to NOT pageIO.open() just yet, we must first verify if it is fully acked in which case
            // we can purge it and we don't care about its integrity for example if it is of zero-byte file size.
```

### 2. EDIT `logstash-core/src/main/java/org/logstash/ackedqueue/Queue.java` (4-line block → 4-line replacement)

**Replaces:**

```java
        logger.debug("opening head page: {}, in: {}, with checkpoint: {}", headCheckpoint.getPageNum(), this.queueManager.getDirPath(), headCheckpoint);

        PageIO pageIO = new MmapPageIOV2(headCheckpoint.getPageNum(), this.pageCapacity, this.queueManager.getDirPath());
        pageIO.recover(); // optimistically recovers the head page data file and set minSeqNum and elementCount to the actual read/recovered data
```

**With:**

```java
        logger.debug("opening head page: {}, in: {}, with checkpoint: {}", headCheckpoint.getPageNum(), this.queueManager.getDirPath(), headCheckpoint);

        PageIO pageIO = PageIOFactory.create(headCheckpoint.getPageNum(), this.pageCapacity, this.queueManager.getDirPath());
        pageIO.recover(); // optimistically recovers the head page data file and set minSeqNum and elementCount to the actual read/recovered data
```

### 3. EDIT `logstash-core/src/main/java/org/logstash/ackedqueue/Queue.java` (5-line block → 5-line replacement)

**Replaces:**

```java
    private boolean cleanedUpFullyAckedCorruptedPage(Checkpoint headCheckpoint, long pqSizeBytes) throws IOException {
        if (headCheckpoint.isFullyAcked()) {
            PageIO pageIO = new MmapPageIOV2(headCheckpoint.getPageNum(), this.pageCapacity, this.queueManager.getDirPath());
            if (pageIO.isCorruptedPage()) {
                logger.debug("Queue is fully acked. Found zero byte page.{}. Recreate checkpoint.head and delete corrupted page", headCheckpoint.getPageNum());
```

**With:**

```java
    private boolean cleanedUpFullyAckedCorruptedPage(Checkpoint headCheckpoint, long pqSizeBytes) throws IOException {
        if (headCheckpoint.isFullyAcked()) {
            PageIO pageIO = PageIOFactory.create(headCheckpoint.getPageNum(), this.pageCapacity, this.queueManager.getDirPath());
            if (pageIO.isCorruptedPage()) {
                logger.debug("Queue is fully acked. Found zero byte page.{}. Recreate checkpoint.head and delete corrupted page", headCheckpoint.getPageNum());
```

### 4. EDIT `logstash-core/src/main/java/org/logstash/ackedqueue/Queue.java` (4-line block → 4-line replacement)

**Replaces:**

```java
    private void newCheckpointedHeadpage(int pageNum) throws IOException {
        PageIO headPageIO = new MmapPageIOV2(pageNum, this.pageCapacity, this.queueManager.getDirPath());
        headPageIO.create();
        logger.debug("created new head page: {}", headPageIO);
```

**With:**

```java
    private void newCheckpointedHeadpage(int pageNum) throws IOException {
        PageIO headPageIO = PageIOFactory.create(pageNum, this.pageCapacity, this.queueManager.getDirPath());
        headPageIO.create();
        logger.debug("created new head page: {}", headPageIO);
```

### 5. CREATE `logstash-core/src/main/java/org/logstash/ackedqueue/io/PageIOFactory.java` (9 line(s))

```java
package org.logstash.ackedqueue.io;

import java.nio.file.Path;

public final class PageIOFactory {
    public static PageIO create(int pageNum, int pageCapacity, Path dirPath) {
        return new MmapPageIOV2(pageNum, pageCapacity, dirPath);
    }
}
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `logstash-core/src/main/java/org/logstash/ackedqueue/Queue.java` | 734 → 734 | 43 → 43 | 4.49 → 4.49 | 151 → 151 | 0 → 0 |
| `logstash-core/src/main/java/org/logstash/ackedqueue/io/PageIOFactory.java` | - → 7 | - → 1 | - → 1 | - → 1 | - → 0 |

## Diff

```diff
diff --git a/logstash-core/src/main/java/org/logstash/ackedqueue/Queue.java b/logstash-core/src/main/java/org/logstash/ackedqueue/Queue.java
index 2a80b79..e240dfb 100644
--- a/logstash-core/src/main/java/org/logstash/ackedqueue/Queue.java
+++ b/logstash-core/src/main/java/org/logstash/ackedqueue/Queue.java
@@ -230,7 +230,7 @@ public final class Queue implements Closeable {
 
             logger.debug("opening tail page: {}, in: {}, with checkpoint: {}", pageNum, this.queueManager.getDirPath(), cp);
 
-            PageIO pageIO = new MmapPageIOV2(pageNum, this.pageCapacity, this.queueManager.getDirPath());
+            PageIO pageIO = PageIOFactory.create(pageNum, this.pageCapacity, this.queueManager.getDirPath());
             // important to NOT pageIO.open() just yet, we must first verify if it is fully acked in which case
             // we can purge it and we don't care about its integrity for example if it is of zero-byte file size.
             if (cp.isFullyAcked()) {
@@ -255,7 +255,7 @@ public final class Queue implements Closeable {
 
         logger.debug("opening head page: {}, in: {}, with checkpoint: {}", headCheckpoint.getPageNum(), this.queueManager.getDirPath(), headCheckpoint);
 
-        PageIO pageIO = new MmapPageIOV2(headCheckpoint.getPageNum(), this.pageCapacity, this.queueManager.getDirPath());
+        PageIO pageIO = PageIOFactory.create(headCheckpoint.getPageNum(), this.pageCapacity, this.queueManager.getDirPath());
         pageIO.recover(); // optimistically recovers the head page data file and set minSeqNum and elementCount to the actual read/recovered data
 
         pqSizeBytes += (long) pageIO.getHead();
@@ -317,7 +317,7 @@ public final class Queue implements Closeable {
      */
     private boolean cleanedUpFullyAckedCorruptedPage(Checkpoint headCheckpoint, long pqSizeBytes) throws IOException {
         if (headCheckpoint.isFullyAcked()) {
-            PageIO pageIO = new MmapPageIOV2(headCheckpoint.getPageNum(), this.pageCapacity, this.queueManager.getDirPath());
+            PageIO pageIO = PageIOFactory.create(headCheckpoint.getPageNum(), this.pageCapacity, this.queueManager.getDirPath());
             if (pageIO.isCorruptedPage()) {
                 logger.debug("Queue is fully acked. Found zero byte page.{}. Recreate checkpoint.head and delete corrupted page", headCheckpoint.getPageNum());
 
@@ -385,7 +385,7 @@ public final class Queue implements Closeable {
      * @throws IOException
      */
     private void newCheckpointedHeadpage(int pageNum) throws IOException {
-        PageIO headPageIO = new MmapPageIOV2(pageNum, this.pageCapacity, this.queueManager.getDirPath());
+        PageIO headPageIO = PageIOFactory.create(pageNum, this.pageCapacity, this.queueManager.getDirPath());
         headPageIO.create();
         logger.debug("created new head page: {}", headPageIO);
         this.headPage = PageFactory.newHeadPage(pageNum, this, headPageIO);
diff --git a/logstash-core/src/main/java/org/logstash/ackedqueue/io/PageIOFactory.java b/logstash-core/src/main/java/org/logstash/ackedqueue/io/PageIOFactory.java
new file mode 100644
index 0000000..0000000
--- /dev/null
+++ b/logstash-core/src/main/java/org/logstash/ackedqueue/io/PageIOFactory.java
@@ -0,0 +1,9 @@
+package org.logstash.ackedqueue.io;
+
+import java.nio.file.Path;
+
+public final class PageIOFactory {
+    public static PageIO create(int pageNum, int pageCapacity, Path dirPath) {
+        return new MmapPageIOV2(pageNum, pageCapacity, dirPath);
+    }
+}
\ No newline at end of file

```
