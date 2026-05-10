# Refactor LSP-075 (LSP): Swallows exceptions (including IOException) from critical cleanup steps, alte...

**Status:** `applied_unverified`  
**Branch:** `refactor/LSP-075` -> `main`  
**Head commit:** `655cccb6202745eddae652c0bb1211d1c2890468`  
**LLM finish:** `FinishReason.STOP` (prompt 8125, completion 592)  

## Detected issue

- **File**: `logstash-core/src/main/java/org/logstash/common/io/DeadLetterQueueWriter.java`
- **Entity**: `DeadLetterQueueWriter.close` (method)
- **Lines (at detection time)**: L407–L421
- **Severity**: high
- **Confidence**: detected by 2 scan(s)

**Description.** Swallows exceptions (including IOException) from critical cleanup steps, altering Closeable.close() contract.

**Reasoning.** The `DeadLetterQueueWriter.close()` method overrides `java.io.Closeable.close()`, which declares `throws IOException`. This implementation catches `Exception` (which includes `IOException`) from `finalizeSegment()` and `releaseFileLock()`, logs them as warnings, and then ignores them. This directly violates the `Closeable.close()` contract by preventing clients from catching and handling `IOException`s that occur during resource release, thus altering the expected error reporting behavior.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 2
- **Files modified** (1): `logstash-core/src/main/java/org/logstash/common/io/DeadLetterQueueWriter.java`

**Summary.** Propagate IOExceptions in DeadLetterQueueWriter.close() to satisfy Closeable contract

**Rationale.** The close() method was catching and swallowing IOExceptions, violating the Closeable contract. By allowing these exceptions to propagate, callers can properly handle resource cleanup failures. The internal helper methods were updated to throw IOException where appropriate, and the close() method now correctly declares the exception propagation.

## Changes overview

_2 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `logstash-core/src/main/java/org/logstash/common/io/DeadLetterQueueWriter.java` (18-line block → 15-line replacement)

**Replaces:**

```java
    @Override
    public void close() {
        if (open.compareAndSet(true, false)) {
            try {
                finalizeSegment(FinalizeWhen.ALWAYS, SealReason.DLQ_CLOSE);
            } catch (Exception e) {
                logger.warn("Unable to close dlq writer, ignoring", e);
            }
            try {
                releaseFileLock();
            } catch (Exception e) {
                logger.warn("Unable to release fileLock, ignoring", e);
            }

            flusherService.shutdown();
            closeConsumedSegmentsNotification();
        }
    }
```

**With:**

```java
    @Override
    public void close() throws IOException {
        if (open.compareAndSet(true, false)) {
            try {
                finalizeSegment(FinalizeWhen.ALWAYS, SealReason.DLQ_CLOSE);
            } finally {
                try {
                    releaseFileLock();
                } finally {
                    flusherService.shutdown();
                    closeConsumedSegmentsNotification();
                }
            }
        }
    }
```

### 2. EDIT `logstash-core/src/main/java/org/logstash/common/io/DeadLetterQueueWriter.java` (12-line block → 7-line replacement)

**Replaces:**

```java
    private void releaseFileLock() {
        try {
            FileLockFactory.releaseLock(fileLock);
        } catch (IOException e) {
            logger.debug("Unable to release fileLock", e);
        }
        try {
            Files.deleteIfExists(queuePath.resolve(LOCK_FILE));
        } catch (IOException e){
            logger.debug("Unable to delete fileLock file", e);
        }
    }
```

**With:**

```java
    private void releaseFileLock() throws IOException {
        try {
            FileLockFactory.releaseLock(fileLock);
        } finally {
            Files.deleteIfExists(queuePath.resolve(LOCK_FILE));
        }
    }
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `logstash-core/src/main/java/org/logstash/common/io/DeadLetterQueueWriter.java` | 593 → 586 | 44 → 44 | 2.5 → 2.41 | 67 → 63 | 0 → 0 |

## Diff

```diff
diff --git a/logstash-core/src/main/java/org/logstash/common/io/DeadLetterQueueWriter.java b/logstash-core/src/main/java/org/logstash/common/io/DeadLetterQueueWriter.java
index cfbd1b3..b56b78e 100644
--- a/logstash-core/src/main/java/org/logstash/common/io/DeadLetterQueueWriter.java
+++ b/logstash-core/src/main/java/org/logstash/common/io/DeadLetterQueueWriter.java
@@ -397,21 +397,18 @@ public final class DeadLetterQueueWriter implements Closeable {
     }
 
     @Override
-    public void close() {
+    public void close() throws IOException {
         if (open.compareAndSet(true, false)) {
             try {
                 finalizeSegment(FinalizeWhen.ALWAYS, SealReason.DLQ_CLOSE);
-            } catch (Exception e) {
-                logger.warn("Unable to close dlq writer, ignoring", e);
-            }
-            try {
-                releaseFileLock();
-            } catch (Exception e) {
-                logger.warn("Unable to release fileLock, ignoring", e);
+            } finally {
+                try {
+                    releaseFileLock();
+                } finally {
+                    flusherService.shutdown();
+                    closeConsumedSegmentsNotification();
+                }
             }
-
-            flusherService.shutdown();
-            closeConsumedSegmentsNotification();
         }
     }
 
@@ -610,16 +607,11 @@ public final class DeadLetterQueueWriter implements Closeable {
         }
     }
 
-    private void releaseFileLock() {
+    private void releaseFileLock() throws IOException {
         try {
             FileLockFactory.releaseLock(fileLock);
-        } catch (IOException e) {
-            logger.debug("Unable to release fileLock", e);
-        }
-        try {
+        } finally {
             Files.deleteIfExists(queuePath.resolve(LOCK_FILE));
-        } catch (IOException e){
-            logger.debug("Unable to delete fileLock file", e);
         }
     }
 

```
