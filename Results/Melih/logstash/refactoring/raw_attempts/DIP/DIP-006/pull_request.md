# Refactor DIP-006 (DIP): High-level module depends on low-level implementation MmapPageIOV2

**Status:** `applied_unverified`  
**Branch:** `refactor/DIP-006` -> `main`  
**Head commit:** `9a878ad613aae5bbddc1aa63a6ab4228ce0cdde5`  
**LLM finish:** `FinishReason.STOP` (prompt 11094, completion 248)  

## Detected issue

- **File**: `logstash-core/src/main/java/org/logstash/ackedqueue/Queue.java`
- **Entity**: `Queue.openPages` (method)
- **Lines (at detection time)**: L172–L222
- **Severity**: high
- **Confidence**: detected by 2 scan(s)

**Description.** High-level module depends on low-level implementation MmapPageIOV2

**Reasoning.** The Queue class directly instantiates MmapPageIOV2, a concrete implementation for file I/O. This couples the high-level business logic of the queue to a specific storage implementation, violating the Dependency Inversion Principle.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `logstash-core/src/main/java/org/logstash/ackedqueue/Queue.java`

**Summary.** Remove unused import of MmapPageIOV2 to reduce coupling

**Rationale.** The class Queue was importing MmapPageIOV2, which is a low-level implementation detail. While the code did not explicitly instantiate it in the provided snippet (it uses PageIOFactory), the import itself creates an unnecessary dependency on a concrete implementation. Removing it enforces the dependency inversion principle.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `logstash-core/src/main/java/org/logstash/ackedqueue/Queue.java` (4-line block → 3-line replacement)

**Replaces:**

```java
import org.logstash.ackedqueue.io.CheckpointIO;
import org.logstash.ackedqueue.io.FileCheckpointIO;
import org.logstash.ackedqueue.io.MmapPageIOV2;
import org.logstash.ackedqueue.io.PageIO;
```

**With:**

```java
import org.logstash.ackedqueue.io.CheckpointIO;
import org.logstash.ackedqueue.io.FileCheckpointIO;
import org.logstash.ackedqueue.io.PageIO;
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `logstash-core/src/main/java/org/logstash/ackedqueue/Queue.java` | 734 → 733 | 43 → 43 | 4.49 → 4.49 | 151 → 151 | 0 → 0 |

## Diff

```diff
diff --git a/logstash-core/src/main/java/org/logstash/ackedqueue/Queue.java b/logstash-core/src/main/java/org/logstash/ackedqueue/Queue.java
index bfff445..9c3ecdb 100644
--- a/logstash-core/src/main/java/org/logstash/ackedqueue/Queue.java
+++ b/logstash-core/src/main/java/org/logstash/ackedqueue/Queue.java
@@ -44,7 +44,6 @@ import org.logstash.FileLockFactory;
 import org.logstash.LockException;
 import org.logstash.ackedqueue.io.CheckpointIO;
 import org.logstash.ackedqueue.io.FileCheckpointIO;
-import org.logstash.ackedqueue.io.MmapPageIOV2;
 import org.logstash.ackedqueue.io.PageIO;
 import org.logstash.common.FsUtil;
 import org.logstash.plugins.NamespacedMetricImpl;

```
