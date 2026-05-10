# Refactor OCP-025 (OCP): The method uses a switch statement on hardcoded protocol strings to determine...

**Status:** `applied_unverified`  
**Branch:** `refactor/OCP-025` -> `main`  
**Head commit:** `afbe603f8be25cc855a929d53fdd8774bf2cd5b7`  
**LLM finish:** `FinishReason.STOP` (prompt 12199, completion 254)  

## Detected issue

- **File**: `logstash-core/src/main/java/org/logstash/execution/AbstractPipelineExt.java`
- **Entity**: `AbstractPipelineExt.getPipelineSourceDetails` (method)
- **Lines (at detection time)**: L868–L887
- **Severity**: medium
- **Confidence**: detected by 2 scan(s)

**Description.** The method uses a switch statement on hardcoded protocol strings to determine source details.

**Reasoning.** Adding a new configuration source protocol (e.g., 'http' or 's3') requires modifying this method to add a new case to the switch statement. This logic should be encapsulated within the SourceWithMetadata implementations or a registry of detail providers.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `logstash-core/src/main/java/org/logstash/execution/AbstractPipelineExt.java`

**Summary.** Refactor pipeline source description logic to use polymorphism

**Rationale.** The switch statement in AbstractPipelineExt violates the Open/Closed Principle. By moving the responsibility of providing a description to the SourceWithMetadata interface (or a default method/implementation), we allow new protocols to be added without modifying the core pipeline execution logic.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `logstash-core/src/main/java/org/logstash/execution/AbstractPipelineExt.java` (10-line block → 3-line replacement)

**Replaces:**

```java
    private String getSourceDescription(SourceWithMetadata source) {
        switch (source.getProtocol()) {
            case "string": return "config string";
            case "file": return source.getId();
            case "x-pack-metrics": return "monitoring pipeline";
            case "x-pack-config-management": return "central pipeline management";
            case "module": return "module";
            default: return source.getProtocol();
        }
    }
```

**With:**

```java
    private String getSourceDescription(SourceWithMetadata source) {
        return source.getDescription();
    }
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `logstash-core/src/main/java/org/logstash/execution/AbstractPipelineExt.java` | 770 → 763 | 62 → 62 | 1.81 → 1.73 | 51 → 46 | 0 → 0 |

## Diff

```diff
diff --git a/logstash-core/src/main/java/org/logstash/execution/AbstractPipelineExt.java b/logstash-core/src/main/java/org/logstash/execution/AbstractPipelineExt.java
index 7b2e452..545a302 100644
--- a/logstash-core/src/main/java/org/logstash/execution/AbstractPipelineExt.java
+++ b/logstash-core/src/main/java/org/logstash/execution/AbstractPipelineExt.java
@@ -811,14 +811,7 @@ public class AbstractPipelineExt extends RubyBasicObject {
     }
 
     private String getSourceDescription(SourceWithMetadata source) {
-        switch (source.getProtocol()) {
-            case "string": return "config string";
-            case "file": return source.getId();
-            case "x-pack-metrics": return "monitoring pipeline";
-            case "x-pack-config-management": return "central pipeline management";
-            case "module": return "module";
-            default: return source.getProtocol();
-        }
+        return source.getDescription();
     }
 
     protected final IRubyObject getSetting(final ThreadContext context, final String name) {

```
