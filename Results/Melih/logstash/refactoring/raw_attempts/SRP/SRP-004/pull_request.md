# Refactor SRP-004 (SRP): Mixes pipeline state management with low-level metric registration and DLQ in...

**Status:** `applied_unverified`  
**Branch:** `refactor/SRP-004` -> `main`  
**Head commit:** `760a3466dd57f852746b849db04782bab403b287`  
**LLM finish:** `FinishReason.STOP` (prompt 12791, completion 2401)  

## Detected issue

- **File**: `logstash-core/src/main/java/org/logstash/execution/AbstractPipelineExt.java`
- **Entity**: `AbstractPipelineExt` (class)
- **Lines (at detection time)**: L88–L650
- **Severity**: medium
- **Confidence**: detected by 10 scan(s)

**Description.** Mixes pipeline state management with low-level metric registration and DLQ instantiation.

**Reasoning.** This class manages the high-level execution state of a pipeline but also contains detailed logic for: 1) Instantiating specific DeadLetterQueueWriter implementations based on settings, 2) Manually registering a wide array of flow metrics into specific namespaces, and 3) Handling JRuby/Java bridge concerns. The metric registration logic is particularly verbose and unrelated to the core responsibility of pipeline execution.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 4
- **Files created** (1): `logstash-core/src/main/java/org/logstash/execution/DeadLetterQueueManager.java`
- **Files modified** (1): `logstash-core/src/main/java/org/logstash/execution/AbstractPipelineExt.java`

**Summary.** Extract DLQ management logic to a dedicated helper class

**Rationale.** The AbstractPipelineExt class was violating SRP by handling DLQ instantiation and management logic. Extracting this into a dedicated DeadLetterQueueManager class reduces the complexity of the pipeline class and isolates the DLQ-specific concerns.

## Changes overview

_4 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `logstash-core/src/main/java/org/logstash/execution/AbstractPipelineExt.java` (3-line block → 4-line replacement)

**Replaces:**

```java
    private transient DeadLetterQueueWriter javaDlqWriter;

    public AbstractPipelineExt(final Ruby runtime, final RubyClass metaClass) {
```

**With:**

```java
    private transient DeadLetterQueueWriter javaDlqWriter;
    private transient DeadLetterQueueManager dlqManager;

    public AbstractPipelineExt(final Ruby runtime, final RubyClass metaClass) {
```

### 2. EDIT `logstash-core/src/main/java/org/logstash/execution/AbstractPipelineExt.java` (51-line block → 15-line replacement)

**Replaces:**

```java
    @JRubyMethod(name = "dlq_writer")
    public final IRubyObject dlqWriter(final ThreadContext context) {
        if (dlqWriter == null) {
            if (dlqEnabled(context).isTrue()) {
                javaDlqWriter = createDeadLetterQueueWriterFromSettings(context);
                dlqWriter = JavaUtil.convertJavaToUsableRubyObject(context.runtime, javaDlqWriter);
            } else {
                dlqWriter = RubyUtil.DUMMY_DLQ_WRITER_CLASS.callMethod(context, "new");
            }
        }
        return dlqWriter;
    }

    private DeadLetterQueueWriter createDeadLetterQueueWriterFromSettings(ThreadContext context) {
        final QueueStorageType storageType = QueueStorageType.parse(getSetting(context, "dead_letter_queue.storage_policy").asJavaString());

        String dlqPath = getSetting(context, "path.dead_letter_queue").asJavaString();
        long dlqMaxBytes = getSetting(context, "dead_letter_queue.max_bytes").convertToInteger().getLongValue();
        Duration dlqFlushInterval = Duration.ofMillis(getSetting(context, "dead_letter_queue.flush_interval").convertToInteger().getLongValue());

        if (hasSetting(context, "dead_letter_queue.retain.age") && !getSetting(context, "dead_letter_queue.retain.age").isNil()) {
            // convert to Duration
            final Duration age = parseToDuration(getSetting(context, "dead_letter_queue.retain.age").convertToString().toString());
            return DeadLetterQueueFactory.getWriter(pipelineId.asJavaString(), dlqPath, dlqMaxBytes,
                    dlqFlushInterval, storageType, age);
        }

        return DeadLetterQueueFactory.getWriter(pipelineId.asJavaString(), dlqPath, dlqMaxBytes, dlqFlushInterval, storageType);
    }

    /**
     * Convert time strings like 3d or 4h or 5m to a duration
     * */
    @VisibleForTesting
    static Duration parseToDuration(String timeStr) {
        final Matcher matcher = Pattern.compile("(?<value>\\d+)\\s*(?<time>[dhms])").matcher(timeStr);
        if (!matcher.matches()) {
            throw new IllegalArgumentException("Expected a time specification in the form <number>[d,h,m,s], e.g. 3m, but found [" + timeStr + "]");
        }
        final int value = Integer.parseInt(matcher.group("value"));
        final String timeSpecifier = matcher.group("time");
        final TemporalUnit unit;
        switch (timeSpecifier) {
            case "d": unit = ChronoUnit.DAYS; break;
            case "h": unit = ChronoUnit.HOURS; break;
            case "m": unit = ChronoUnit.MINUTES; break;
            case "s": unit = ChronoUnit.SECONDS; break;
            default: throw new IllegalStateException("Expected a time unit specification from d,h,m,s but found: [" + timeSpecifier + "]");
        }
        return Duration.of(value, unit);
    }
```

**With:**

```java
    @JRubyMethod(name = "dlq_writer")
    public final IRubyObject dlqWriter(final ThreadContext context) {
        if (dlqWriter == null) {
            if (dlqEnabled(context).isTrue()) {
                if (dlqManager == null) {
                    dlqManager = new DeadLetterQueueManager(pipelineId.asJavaString());
                }
                javaDlqWriter = dlqManager.createWriter(context, settings);
                dlqWriter = JavaUtil.convertJavaToUsableRubyObject(context.runtime, javaDlqWriter);
            } else {
                dlqWriter = RubyUtil.DUMMY_DLQ_WRITER_CLASS.callMethod(context, "new");
            }
        }
        return dlqWriter;
    }
```

### 3. EDIT `logstash-core/src/main/java/org/logstash/execution/AbstractPipelineExt.java` (8-line block → 8-line replacement)

**Replaces:**

```java
    @JRubyMethod(name = "close_dlq_writer")
    public final IRubyObject closeDlqWriter(final ThreadContext context) {
        dlqWriter.callMethod(context, "close");
        if (dlqEnabled(context).isTrue()) {
            DeadLetterQueueFactory.release(pipelineId.asJavaString());
        }
        return context.nil;
    }
```

**With:**

```java
    @JRubyMethod(name = "close_dlq_writer")
    public final IRubyObject closeDlqWriter(final ThreadContext context) {
        dlqWriter.callMethod(context, "close");
        if (dlqEnabled(context).isTrue() && dlqManager != null) {
            dlqManager.release();
        }
        return context.nil;
    }
```

### 4. CREATE `logstash-core/src/main/java/org/logstash/execution/DeadLetterQueueManager.java` (69 line(s))

```java
package org.logstash.execution;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.jruby.runtime.ThreadContext;
import org.jruby.runtime.builtin.IRubyObject;
import org.logstash.RubyUtil;
import org.logstash.common.DeadLetterQueueFactory;
import org.logstash.common.io.DeadLetterQueueWriter;
import org.logstash.common.io.QueueStorageType;
import org.jruby.javasupport.JavaUtil;

import java.time.Duration;
import java.time.temporal.ChronoUnit;
import java.time.temporal.TemporalUnit;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class DeadLetterQueueManager {
    private static final Logger LOGGER = LogManager.getLogger(DeadLetterQueueManager.class);
    private final String pipelineId;

    public DeadLetterQueueManager(String pipelineId) {
        this.pipelineId = pipelineId;
    }

    public DeadLetterQueueWriter createWriter(ThreadContext context, IRubyObject settings) {
        final QueueStorageType storageType = QueueStorageType.parse(getSetting(context, settings, "dead_letter_queue.storage_policy").asJavaString());
        String dlqPath = getSetting(context, settings, "path.dead_letter_queue").asJavaString();
        long dlqMaxBytes = getSetting(context, settings, "dead_letter_queue.max_bytes").convertToInteger().getLongValue();
        Duration dlqFlushInterval = Duration.ofMillis(getSetting(context, settings, "dead_letter_queue.flush_interval").convertToInteger().getLongValue());

        if (hasSetting(context, settings, "dead_letter_queue.retain.age") && !getSetting(context, settings, "dead_letter_queue.retain.age").isNil()) {
            final Duration age = parseToDuration(getSetting(context, settings, "dead_letter_queue.retain.age").convertToString().toString());
            return DeadLetterQueueFactory.getWriter(pipelineId, dlqPath, dlqMaxBytes, dlqFlushInterval, storageType, age);
        }
        return DeadLetterQueueFactory.getWriter(pipelineId, dlqPath, dlqMaxBytes, dlqFlushInterval, storageType);
    }

    public void release() {
        DeadLetterQueueFactory.release(pipelineId);
    }

    private IRubyObject getSetting(ThreadContext context, IRubyObject settings, String name) {
        return settings.callMethod(context, "get_value", context.runtime.newString(name));
    }

    private boolean hasSetting(ThreadContext context, IRubyObject settings, String name) {
        return settings.callMethod(context, "registered?", context.runtime.newString(name)) == context.tru;
    }

    public static Duration parseToDuration(String timeStr) {
        final Matcher matcher = Pattern.compile("(?<value>\\d+)\\s*(?<time>[dhms])").matcher(timeStr);
        if (!matcher.matches()) {
            throw new IllegalArgumentException("Expected a time specification in the form <number>[d,h,m,s], e.g. 3m, but found [" + timeStr + "]");
        }
        final int value = Integer.parseInt(matcher.group("value"));
        final String timeSpecifier = matcher.group("time");
        final TemporalUnit unit;
        switch (timeSpecifier) {
... (9 more line(s) truncated)
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `logstash-core/src/main/java/org/logstash/execution/AbstractPipelineExt.java` | 806 → 777 | 63 → 61 | 1.87 → 1.82 | 56 → 51 | 0 → 0 |
| `logstash-core/src/main/java/org/logstash/execution/DeadLetterQueueManager.java` | - → 59 | - → 5 | - → 2.4 | - → 8 | - → 0 |

## Diff

```diff
diff --git a/logstash-core/src/main/java/org/logstash/execution/AbstractPipelineExt.java b/logstash-core/src/main/java/org/logstash/execution/AbstractPipelineExt.java
index b90b77d..9573eff 100644
--- a/logstash-core/src/main/java/org/logstash/execution/AbstractPipelineExt.java
+++ b/logstash-core/src/main/java/org/logstash/execution/AbstractPipelineExt.java
@@ -170,6 +170,7 @@ public class AbstractPipelineExt extends RubyBasicObject {
 
     private String lastErrorEvaluationReceived = "";
     private transient DeadLetterQueueWriter javaDlqWriter;
+    private transient DeadLetterQueueManager dlqManager;
 
     public AbstractPipelineExt(final Ruby runtime, final RubyClass metaClass) {
         super(runtime, metaClass);
@@ -387,7 +388,10 @@ public class AbstractPipelineExt extends RubyBasicObject {
     public final IRubyObject dlqWriter(final ThreadContext context) {
         if (dlqWriter == null) {
             if (dlqEnabled(context).isTrue()) {
-                javaDlqWriter = createDeadLetterQueueWriterFromSettings(context);
+                if (dlqManager == null) {
+                    dlqManager = new DeadLetterQueueManager(pipelineId.asJavaString());
+                }
+                javaDlqWriter = dlqManager.createWriter(context, settings);
                 dlqWriter = JavaUtil.convertJavaToUsableRubyObject(context.runtime, javaDlqWriter);
             } else {
                 dlqWriter = RubyUtil.DUMMY_DLQ_WRITER_CLASS.callMethod(context, "new");
@@ -396,45 +400,6 @@ public class AbstractPipelineExt extends RubyBasicObject {
         return dlqWriter;
     }
 
-    private DeadLetterQueueWriter createDeadLetterQueueWriterFromSettings(ThreadContext context) {
-        final QueueStorageType storageType = QueueStorageType.parse(getSetting(context, "dead_letter_queue.storage_policy").asJavaString());
-
-        String dlqPath = getSetting(context, "path.dead_letter_queue").asJavaString();
-        long dlqMaxBytes = getSetting(context, "dead_letter_queue.max_bytes").convertToInteger().getLongValue();
-        Duration dlqFlushInterval = Duration.ofMillis(getSetting(context, "dead_letter_queue.flush_interval").convertToInteger().getLongValue());
-
-        if (hasSetting(context, "dead_letter_queue.retain.age") && !getSetting(context, "dead_letter_queue.retain.age").isNil()) {
-            // convert to Duration
-            final Duration age = parseToDuration(getSetting(context, "dead_letter_queue.retain.age").convertToString().toString());
-            return DeadLetterQueueFactory.getWriter(pipelineId.asJavaString(), dlqPath, dlqMaxBytes,
-                    dlqFlushInterval, storageType, age);
-        }
-
-        return DeadLetterQueueFactory.getWriter(pipelineId.asJavaString(), dlqPath, dlqMaxBytes, dlqFlushInterval, storageType);
-    }
-
-    /**
-     * Convert time strings like 3d or 4h or 5m to a duration
-     * */
-    @VisibleForTesting
-    static Duration parseToDuration(String timeStr) {
-        final Matcher matcher = Pattern.compile("(?<value>\\d+)\\s*(?<time>[dhms])").matcher(timeStr);
-        if (!matcher.matches()) {
-            throw new IllegalArgumentException("Expected a time specification in the form <number>[d,h,m,s], e.g. 3m, but found [" + timeStr + "]");
-        }
-        final int value = Integer.parseInt(matcher.group("value"));
-        final String timeSpecifier = matcher.group("time");
-        final TemporalUnit unit;
-        switch (timeSpecifier) {
-            case "d": unit = ChronoUnit.DAYS; break;
-            case "h": unit = ChronoUnit.HOURS; break;
-            case "m": unit = ChronoUnit.MINUTES; break;
-            case "s": unit = ChronoUnit.SECONDS; break;
-            default: throw new IllegalStateException("Expected a time unit specification from d,h,m,s but found: [" + timeSpecifier + "]");
-        }
-        return Duration.of(value, unit);
-    }
-
     @JRubyMethod(name = "dlq_enabled?")
     public final IRubyObject dlqEnabled(final ThreadContext context) {
         return getSetting(context, "dead_letter_queue.enable");
@@ -443,8 +408,8 @@ public class AbstractPipelineExt extends RubyBasicObject {
     @JRubyMethod(name = "close_dlq_writer")
     public final IRubyObject closeDlqWriter(final ThreadContext context) {
         dlqWriter.callMethod(context, "close");
-        if (dlqEnabled(context).isTrue()) {
-            DeadLetterQueueFactory.release(pipelineId.asJavaString());
+        if (dlqEnabled(context).isTrue() && dlqManager != null) {
+            dlqManager.release();
         }
         return context.nil;
     }
diff --git a/logstash-core/src/main/java/org/logstash/execution/DeadLetterQueueManager.java b/logstash-core/src/main/java/org/logstash/execution/DeadLetterQueueManager.java
new file mode 100644
index 0000000..0000000
--- /dev/null
+++ b/logstash-core/src/main/java/org/logstash/execution/DeadLetterQueueManager.java
@@ -0,0 +1,69 @@
+package org.logstash.execution;
+
+import org.apache.logging.log4j.LogManager;
+import org.apache.logging.log4j.Logger;
+import org.jruby.runtime.ThreadContext;
+import org.jruby.runtime.builtin.IRubyObject;
+import org.logstash.RubyUtil;
+import org.logstash.common.DeadLetterQueueFactory;
+import org.logstash.common.io.DeadLetterQueueWriter;
+import org.logstash.common.io.QueueStorageType;
+import org.jruby.javasupport.JavaUtil;
+
+import java.time.Duration;
+import java.time.temporal.ChronoUnit;
+import java.time.temporal.TemporalUnit;
+import java.util.regex.Matcher;
+import java.util.regex.Pattern;
+
+public class DeadLetterQueueManager {
+    private static final Logger LOGGER = LogManager.getLogger(DeadLetterQueueManager.class);
+    private final String pipelineId;
+
+    public DeadLetterQueueManager(String pipelineId) {
+        this.pipelineId = pipelineId;
+    }
+
+    public DeadLetterQueueWriter createWriter(ThreadContext context, IRubyObject settings) {
+        final QueueStorageType storageType = QueueStorageType.parse(getSetting(context, settings, "dead_letter_queue.storage_policy").asJavaString());
+        String dlqPath = getSetting(context, settings, "path.dead_letter_queue").asJavaString();
+        long dlqMaxBytes = getSetting(context, settings, "dead_letter_queue.max_bytes").convertToInteger().getLongValue();
+        Duration dlqFlushInterval = Duration.ofMillis(getSetting(context, settings, "dead_letter_queue.flush_interval").convertToInteger().getLongValue());
+
+        if (hasSetting(context, settings, "dead_letter_queue.retain.age") && !getSetting(context, settings, "dead_letter_queue.retain.age").isNil()) {
+            final Duration age = parseToDuration(getSetting(context, settings, "dead_letter_queue.retain.age").convertToString().toString());
+            return DeadLetterQueueFactory.getWriter(pipelineId, dlqPath, dlqMaxBytes, dlqFlushInterval, storageType, age);
+        }
+        return DeadLetterQueueFactory.getWriter(pipelineId, dlqPath, dlqMaxBytes, dlqFlushInterval, storageType);
+    }
+
+    public void release() {
+        DeadLetterQueueFactory.release(pipelineId);
+    }
+
+    private IRubyObject getSetting(ThreadContext context, IRubyObject settings, String name) {
+        return settings.callMethod(context, "get_value", context.runtime.newString(name));
+    }
+
+    private boolean hasSetting(ThreadContext context, IRubyObject settings, String name) {
+        return settings.callMethod(context, "registered?", context.runtime.newString(name)) == context.tru;
+    }
+
+    public static Duration parseToDuration(String timeStr) {
+        final Matcher matcher = Pattern.compile("(?<value>\\d+)\\s*(?<time>[dhms])").matcher(timeStr);
+        if (!matcher.matches()) {
+            throw new IllegalArgumentException("Expected a time specification in the form <number>[d,h,m,s], e.g. 3m, but found [" + timeStr + "]");
+        }
+        final int value = Integer.parseInt(matcher.group("value"));
+        final String timeSpecifier = matcher.group("time");
+        final TemporalUnit unit;
+        switch (timeSpecifier) {
+            case "d": unit = ChronoUnit.DAYS; break;
+            case "h": unit = ChronoUnit.HOURS; break;
+            case "m": unit = ChronoUnit.MINUTES; break;
+            case "s": unit = ChronoUnit.SECONDS; break;
+            default: throw new IllegalStateException("Expected a time unit specification from d,h,m,s but found: [" + timeSpecifier + "]");
+        }
+        return Duration.of(value, unit);
+    }
+}
\ No newline at end of file

```
