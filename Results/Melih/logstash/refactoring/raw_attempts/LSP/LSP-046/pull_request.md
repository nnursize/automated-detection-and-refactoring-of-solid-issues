# Refactor LSP-046 (LSP): Method uses instanceof check to conditionally skip core functionality.

**Status:** `applied_unverified`  
**Branch:** `refactor/LSP-046` -> `main`  
**Head commit:** `7f6b8ce5dbbac4b7b1d079fac8b36aec0fcd7434`  
**LLM finish:** `FinishReason.STOP` (prompt 6925, completion 437)  

## Detected issue

- **File**: `logstash-core/src/main/java/org/logstash/Event.java`
- **Entity**: `Event.append` (method)
- **Lines (at detection time)**: L306–L311
- **Severity**: high
- **Confidence**: detected by 2 scan(s)

**Description.** Method uses instanceof check to conditionally skip core functionality.

**Reasoning.** The `append` method checks if the input `e` is an instance of `Event`. If `e` is not an `Event` (but is a `co.elastic.logstash.api.Event` subtype), the method simply returns `this` without performing any append operation. This violates LSP because a subtype of `co.elastic.logstash.api.Event` that is not `Event` cannot be substituted for `Event` without altering the correctness of the program, as the expected behavior of appending the event's data is skipped.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `logstash-core/src/main/java/org/logstash/Event.java`

**Summary.** Remove type-checking in overwrite and append methods to satisfy LSP

**Rationale.** The `overwrite` and `append` methods were using `instanceof` to conditionally skip logic for non-`Event` implementations of `co.elastic.logstash.api.Event`. By using the public `getData()` and `getTimestamp()` methods defined in the interface, we can perform the operations on any valid `co.elastic.logstash.api.Event` implementation, ensuring substitutability.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `logstash-core/src/main/java/org/logstash/Event.java` (15-line block → 14-line replacement)

**Replaces:**

```java
    @Override
    public co.elastic.logstash.api.Event overwrite(co.elastic.logstash.api.Event e) {
        if (e instanceof Event) {
            return overwrite((Event)e);
        }
        return e;
    }

    @Override
    public co.elastic.logstash.api.Event append(co.elastic.logstash.api.Event e) {
        if (e instanceof Event) {
            return append((Event)e);
        }
        return e;
    }
```

**With:**

```java
    @Override
    public co.elastic.logstash.api.Event overwrite(co.elastic.logstash.api.Event e) {
        this.data = ConvertedMap.newFromMap(e.toMap());
        this.cancelled = e.isCancelled();
        Instant t = e.getEventTimestamp();
        setTimestamp(t == null ? new Timestamp() : new Timestamp(t.toEpochMilli()));
        return this;
    }

    @Override
    public co.elastic.logstash.api.Event append(co.elastic.logstash.api.Event e) {
        Util.mapMerge(this.data, e.toMap());
        return this;
    }
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `logstash-core/src/main/java/org/logstash/Event.java` | 499 → 498 | 45 → 45 | 2.38 → 2.33 | 63 → 61 | 0 → 0 |

## Diff

```diff
diff --git a/logstash-core/src/main/java/org/logstash/Event.java b/logstash-core/src/main/java/org/logstash/Event.java
index 2a9f79a..7ad7e3a 100644
--- a/logstash-core/src/main/java/org/logstash/Event.java
+++ b/logstash-core/src/main/java/org/logstash/Event.java
@@ -346,18 +346,17 @@ public final class Event implements Cloneable, Queueable, co.elastic.logstash.ap
 
     @Override
     public co.elastic.logstash.api.Event overwrite(co.elastic.logstash.api.Event e) {
-        if (e instanceof Event) {
-            return overwrite((Event)e);
-        }
-        return e;
+        this.data = ConvertedMap.newFromMap(e.toMap());
+        this.cancelled = e.isCancelled();
+        Instant t = e.getEventTimestamp();
+        setTimestamp(t == null ? new Timestamp() : new Timestamp(t.toEpochMilli()));
+        return this;
     }
 
     @Override
     public co.elastic.logstash.api.Event append(co.elastic.logstash.api.Event e) {
-        if (e instanceof Event) {
-            return append((Event)e);
-        }
-        return e;
+        Util.mapMerge(this.data, e.toMap());
+        return this;
     }
 
     public Event overwrite(Event e) {

```
