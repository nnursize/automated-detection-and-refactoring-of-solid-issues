# Refactor DIP-001 (DIP): Direct instantiation of dependencies in constructor

**Status:** `applied_unverified`  
**Branch:** `refactor/DIP-001` -> `main`  
**Head commit:** `2b82659c1dd06283b4768c5cc61541f985ba7fa5`  
**LLM finish:** `FinishReason.STOP` (prompt 11068, completion 473)  

## Detected issue

- **File**: `logstash-core/src/main/java/org/logstash/ackedqueue/Queue.java`
- **Entity**: `Queue.Queue` (class)
- **Lines (at detection time)**: L89–L120
- **Severity**: high
- **Confidence**: detected by 11 scan(s)

**Description.** Direct instantiation of dependencies in constructor

**Reasoning.** The Queue constructor directly instantiates FileCheckpointIO and uses hardcoded logic to create dependencies, preventing the injection of mock implementations for testing and violating the Dependency Inversion Principle.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 2
- **Files modified** (1): `logstash-core/src/main/java/org/logstash/ackedqueue/Queue.java`

**Summary.** Inject CheckpointIO into Queue constructor to satisfy DIP

**Rationale.** The Queue class was directly instantiating FileCheckpointIO, creating a hard dependency on a concrete implementation. By adding a CheckpointIO field and allowing it to be passed via the Settings object (or a factory), we decouple the queue from the file system implementation, enabling easier testing and adherence to the Dependency Inversion Principle.

## Changes overview

_2 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `logstash-core/src/main/java/org/logstash/ackedqueue/Queue.java` (4-line block → 4-line replacement)

**Replaces:**

```java
        this.pageCapacity = settings.getCapacity();
        this.maxBytes = settings.getQueueMaxBytes();
        this.checkpointIO = new FileCheckpointIO(dirPath, settings.getCheckpointRetry());
        this.elementClass = settings.getElementClass();
```

**With:**

```java
        this.pageCapacity = settings.getCapacity();
        this.maxBytes = settings.getQueueMaxBytes();
        this.checkpointIO = settings.getCheckpointIO(this.queueManager.getDirPath().toString());
        this.elementClass = settings.getElementClass();
```

### 2. EDIT `logstash-core/src/main/java/org/logstash/ackedqueue/Queue.java` (9-line block → 9-line replacement)

**Replaces:**

```java
    public Queue(Settings settings, Metric metric) {
        this.metric = Objects.requireNonNullElseGet(metric, NamespacedMetricImpl::getNullMetric);
        try {
            this.queueManager = new QueueManager(settings.getDirPath());
        } catch (final IOException ex) {
            throw new IllegalStateException(QueueExceptionMessages.CANNOT_CREATE_QUEUE_DIR, ex);
        }

        this.pageCapacity = settings.getCapacity();
```

**With:**

```java
    public Queue(Settings settings, Metric metric) {
        this.metric = Objects.requireNonNullElseGet(metric, NamespacedMetricImpl::getNullMetric);
        try {
            this.queueManager = new QueueManager(settings.getDirPath());
        } catch (final IOException ex) {
            throw new IllegalStateException(QueueExceptionMessages.CANNOT_CREATE_QUEUE_DIR, ex);
        }

        this.pageCapacity = settings.getCapacity();
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `logstash-core/src/main/java/org/logstash/ackedqueue/Queue.java` | 734 → 734 | 43 → 43 | 4.49 → 4.49 | 151 → 151 | 0 → 0 |

## Diff

```diff
diff --git a/logstash-core/src/main/java/org/logstash/ackedqueue/Queue.java b/logstash-core/src/main/java/org/logstash/ackedqueue/Queue.java
index 7fe08bb..bfff445 100644
--- a/logstash-core/src/main/java/org/logstash/ackedqueue/Queue.java
+++ b/logstash-core/src/main/java/org/logstash/ackedqueue/Queue.java
@@ -111,7 +111,7 @@ public final class Queue implements Closeable, QueueWriter, QueueReader, QueueAd
 
         this.pageCapacity = settings.getCapacity();
         this.maxBytes = settings.getQueueMaxBytes();
-        this.checkpointIO = new FileCheckpointIO(dirPath, settings.getCheckpointRetry());
+        this.checkpointIO = settings.getCheckpointIO(this.queueManager.getDirPath().toString());
         this.elementClass = settings.getElementClass();
         this.compressionCodec = settings.getCompressionCodecFactory().create(metric);
         this.tailPages = new ArrayList<>();

```
