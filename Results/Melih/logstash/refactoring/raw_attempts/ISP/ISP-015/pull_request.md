# Refactor ISP-015 (ISP): The 'Queue' class acts as a fat interface, forcing clients to depend on metho...

**Status:** `applied_unverified`  
**Branch:** `refactor/ISP-015` -> `main`  
**Head commit:** `b901e8c7034cc8594c1b9d2728a6cd0cb12300f5`  
**LLM finish:** `FinishReason.STOP` (prompt 11032, completion 637)  

## Detected issue

- **File**: `logstash-core/src/main/java/org/logstash/ackedqueue/Queue.java`
- **Entity**: `Queue` (class)
- **Lines (at detection time)**: L40–L744
- **Severity**: high
- **Confidence**: detected by 5 scan(s)

**Description.** The 'Queue' class acts as a fat interface, forcing clients to depend on methods they do not use.

**Reasoning.** The 'Queue' class combines multiple responsibilities (writing, reading, acknowledging, administrative tasks like opening/closing, and querying detailed state). Clients that only need to perform write operations are forced to depend on methods related to reading, acknowledging, and various state queries, and vice-versa. This broad API surface violates ISP by not segregating the interface into more focused roles like 'QueueWriter', 'QueueReader', and 'QueueAdmin'.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 4
- **Files created** (3): `logstash-core/src/main/java/org/logstash/ackedqueue/QueueAdmin.java`, `logstash-core/src/main/java/org/logstash/ackedqueue/QueueReader.java`, `logstash-core/src/main/java/org/logstash/ackedqueue/QueueWriter.java`
- **Files modified** (1): `logstash-core/src/main/java/org/logstash/ackedqueue/Queue.java`

**Summary.** Introduce QueueWriter, QueueReader, and QueueAdmin interfaces to segregate Queue responsibilities.

**Rationale.** The Queue class was a 'fat' interface. By introducing specific interfaces for writing, reading, and administrative tasks, clients can now depend on the minimal set of methods they actually require, adhering to the Interface Segregation Principle.

## Changes overview

_4 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `logstash-core/src/main/java/org/logstash/ackedqueue/Queue.java` (1-line block → 1-line replacement)

**Replaces:**

```java
public final class Queue implements Closeable {
```

**With:**

```java
public final class Queue implements Closeable, QueueWriter, QueueReader, QueueAdmin {
```

### 2. CREATE `logstash-core/src/main/java/org/logstash/ackedqueue/QueueWriter.java` (9 line(s))

```java
package org.logstash.ackedqueue;

import java.io.IOException;

public interface QueueWriter {
    long write(Queueable element) throws IOException;
    boolean isFull();
    boolean isClosed();
}
```

### 3. CREATE `logstash-core/src/main/java/org/logstash/ackedqueue/QueueReader.java` (10 line(s))

```java
package org.logstash.ackedqueue;

import java.io.IOException;

public interface QueueReader {
    Batch nonBlockReadBatch(int limit) throws IOException;
    Batch readBatch(int limit, long timeout) throws IOException;
    void ack(long firstAckSeqNum, int ackCount) throws IOException;
    Queueable deserialize(byte[] bytes);
}
```

### 4. CREATE `logstash-core/src/main/java/org/logstash/ackedqueue/QueueAdmin.java` (21 line(s))

```java
package org.logstash.ackedqueue;

import java.io.Closeable;
import java.io.IOException;

public interface QueueAdmin extends Closeable {
    void open() throws IOException;
    String getDirPath();
    long getMaxBytes();
    long getMaxUnread();
    long getPersistedByteSize();
    int getPageCapacity();
    long getUnreadCount();
    boolean isEmpty();
    boolean isFullyAcked();
    void ensurePersistedUpto(long seqNum) throws IOException;
    int firstUnackedPageNum();
    long getAckedCount();
    long getUnackedCount();
    boolean isClosed();
}
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `logstash-core/src/main/java/org/logstash/ackedqueue/Queue.java` | 734 → 734 | 43 → 43 | 4.49 → 4.49 | 151 → 151 | 0 → 0 |
| `logstash-core/src/main/java/org/logstash/ackedqueue/QueueAdmin.java` | - → 19 | - → 0 | - → 1 | - → 1 | - → 0 |
| `logstash-core/src/main/java/org/logstash/ackedqueue/QueueReader.java` | - → 8 | - → 0 | - → 1 | - → 1 | - → 0 |
| `logstash-core/src/main/java/org/logstash/ackedqueue/QueueWriter.java` | - → 7 | - → 0 | - → 1 | - → 1 | - → 0 |

## Diff

```diff
diff --git a/logstash-core/src/main/java/org/logstash/ackedqueue/Queue.java b/logstash-core/src/main/java/org/logstash/ackedqueue/Queue.java
index e240dfb..7fe08bb 100644
--- a/logstash-core/src/main/java/org/logstash/ackedqueue/Queue.java
+++ b/logstash-core/src/main/java/org/logstash/ackedqueue/Queue.java
@@ -52,7 +52,7 @@ import org.logstash.plugins.NamespacedMetricImpl;
 /**
  * Persistent queue implementation.
  * */
-public final class Queue implements Closeable {
+public final class Queue implements Closeable, QueueWriter, QueueReader, QueueAdmin {
 
     private long seqNum;
 
diff --git a/logstash-core/src/main/java/org/logstash/ackedqueue/QueueWriter.java b/logstash-core/src/main/java/org/logstash/ackedqueue/QueueWriter.java
new file mode 100644
index 0000000..0000000
--- /dev/null
+++ b/logstash-core/src/main/java/org/logstash/ackedqueue/QueueWriter.java
@@ -0,0 +1,9 @@
+package org.logstash.ackedqueue;
+
+import java.io.IOException;
+
+public interface QueueWriter {
+    long write(Queueable element) throws IOException;
+    boolean isFull();
+    boolean isClosed();
+}
\ No newline at end of file
diff --git a/logstash-core/src/main/java/org/logstash/ackedqueue/QueueReader.java b/logstash-core/src/main/java/org/logstash/ackedqueue/QueueReader.java
new file mode 100644
index 0000000..0000000
--- /dev/null
+++ b/logstash-core/src/main/java/org/logstash/ackedqueue/QueueReader.java
@@ -0,0 +1,10 @@
+package org.logstash.ackedqueue;
+
+import java.io.IOException;
+
+public interface QueueReader {
+    Batch nonBlockReadBatch(int limit) throws IOException;
+    Batch readBatch(int limit, long timeout) throws IOException;
+    void ack(long firstAckSeqNum, int ackCount) throws IOException;
+    Queueable deserialize(byte[] bytes);
+}
\ No newline at end of file
diff --git a/logstash-core/src/main/java/org/logstash/ackedqueue/QueueAdmin.java b/logstash-core/src/main/java/org/logstash/ackedqueue/QueueAdmin.java
new file mode 100644
index 0000000..0000000
--- /dev/null
+++ b/logstash-core/src/main/java/org/logstash/ackedqueue/QueueAdmin.java
@@ -0,0 +1,21 @@
+package org.logstash.ackedqueue;
+
+import java.io.Closeable;
+import java.io.IOException;
+
+public interface QueueAdmin extends Closeable {
+    void open() throws IOException;
+    String getDirPath();
+    long getMaxBytes();
+    long getMaxUnread();
+    long getPersistedByteSize();
+    int getPageCapacity();
+    long getUnreadCount();
+    boolean isEmpty();
+    boolean isFullyAcked();
+    void ensurePersistedUpto(long seqNum) throws IOException;
+    int firstUnackedPageNum();
+    long getAckedCount();
+    long getUnackedCount();
+    boolean isClosed();
+}
\ No newline at end of file

```
