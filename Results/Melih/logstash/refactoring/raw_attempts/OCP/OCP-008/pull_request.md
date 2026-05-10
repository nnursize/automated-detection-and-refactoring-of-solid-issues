# Refactor OCP-008 (OCP): Switch statement on pipeline state for health analysis

**Status:** `applied_unverified`  
**Branch:** `refactor/OCP-008` -> `main`  
**Head commit:** `9fbbeef031ab8f928678f367a07555b3ec710ac1`  
**LLM finish:** `FinishReason.STOP` (prompt 4704, completion 1621)  

## Detected issue

- **File**: `logstash-core/src/main/java/org/logstash/health/PipelineIndicator.java`
- **Entity**: `PipelineIndicator.StatusProbe.analyze` (method)
- **Lines (at detection time)**: L159–L198
- **Severity**: medium
- **Confidence**: detected by 2 scan(s)

**Description.** Switch statement on pipeline state for health analysis

**Reasoning.** The analyze method in StatusProbe uses a switch statement to generate health reports based on the pipeline's State enum. If a new pipeline state is introduced, this analysis logic must be modified. Encapsulating the analysis logic within state-specific objects would follow OCP.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `logstash-core/src/main/java/org/logstash/health/PipelineIndicator.java`

**Summary.** Refactor PipelineIndicator.StatusProbe to use a strategy pattern for pipeline state analysis

**Rationale.** Replaced the switch statement in StatusProbe.analyze with a map-based strategy lookup. This allows adding new pipeline states without modifying the core analysis logic, adhering to the Open/Closed Principle.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `logstash-core/src/main/java/org/logstash/health/PipelineIndicator.java` (69-line block → 60-line replacement)

**Replaces:**

```java
    static class StatusProbe implements Probe<Details> {
        static final Impact.Builder NOT_PROCESSING = Impact.builder()
                .withId(impactId("not_processing"))
                .withDescription("the pipeline is not currently processing")
                .withAdditionalImpactArea(ImpactArea.PIPELINE_EXECUTION);

        static final HelpUrl HELP_URL = new HelpUrl("health-report-pipeline-status");

        @Override
        public Analysis analyze(final Details details) {
            switch (details.getStatus().getState()) {
                case LOADING:
                    return Analysis.builder()
                            .withStatus(YELLOW)
                            .withDiagnosis(db -> db
                                    .withId(diagnosisId("loading"))
                                    .withCause("pipeline is loading")
                                    .withAction("if pipeline does not come up quickly, you may need to check the logs to see if it is stalled")
                                    .withHelpUrl(HELP_URL.withAnchor("loading").toString()))
                            .withImpact(NOT_PROCESSING.withSeverity(1).withDescription("pipeline is loading").build())
                            .build();
                case RUNNING:
                    return Analysis.builder()
                            .withStatus(GREEN)
                            .build();
                case FINISHED:
                    return Analysis.builder()
                            .withStatus(YELLOW)
                            .withDiagnosis(db -> db
                                    .withId(diagnosisId("finished"))
                                    .withCause("pipeline has finished running because its inputs have been closed and events have been processed")
                                    .withAction("if you expect this pipeline to run indefinitely, you will need to configure its inputs to continue receiving or fetching events")
                                    .withHelpUrl(HELP_URL.withAnchor("finished").toString()))
                            .withImpact(NOT_PROCESSING.withSeverity(10).withDescription("pipeline has finished running").build())
                            .build();
                case TERMINATED:
                    return Analysis.builder()
                            .withStatus(RED)
                            .withDiagnosis(db -> db
                                    .withId(diagnosisId("terminated"))
                                    .withCause("pipeline is not running, likely because it has encountered an error")
                                    .withAction("view logs to determine the cause of abnormal pipeline shutdown")
                                    .withHelpUrl(HELP_URL.withAnchor("terminated").toString()))
                            .withImpact(NOT_PROCESSING.withSeverity(1).build())
                            .build();
                case UNKNOWN:
                default:
                    return Analysis.builder()
                            .withStatus(UNKNOWN)
                            .withDiagnosis(db -> db
                                    .withId(diagnosisId("unknown"))
                                    .withCause("pipeline is not known; it may have been recently deleted or failed to start")
                                    .withAction("view logs to determine if the pipeline failed to start")
                                    .withHelpUrl(HELP_URL.withAnchor("unknown").toString()))
                            .withImpact(NOT_PROCESSING.withSeverity(2).build())
                            .build();
            }
        }

        static String diagnosisId(final String state) {
... (9 more line(s) truncated)
```

**With:**

```java
    static class StatusProbe implements Probe<Details> {
        static final Impact.Builder NOT_PROCESSING = Impact.builder()
                .withId(impactId("not_processing"))
                .withDescription("the pipeline is not currently processing")
                .withAdditionalImpactArea(ImpactArea.PIPELINE_EXECUTION);

        static final HelpUrl HELP_URL = new HelpUrl("health-report-pipeline-status");

        private static final Map<Status.State, java.util.function.Supplier<Analysis>> STRATEGIES = Map.of(
            Status.State.LOADING, () -> Analysis.builder()
                .withStatus(YELLOW)
                .withDiagnosis(db -> db
                    .withId(diagnosisId("loading"))
                    .withCause("pipeline is loading")
                    .withAction("if pipeline does not come up quickly, you may need to check the logs to see if it is stalled")
                    .withHelpUrl(HELP_URL.withAnchor("loading").toString()))
                .withImpact(NOT_PROCESSING.withSeverity(1).withDescription("pipeline is loading").build())
                .build(),
            Status.State.RUNNING, () -> Analysis.builder().withStatus(GREEN).build(),
            Status.State.FINISHED, () -> Analysis.builder()
                .withStatus(YELLOW)
                .withDiagnosis(db -> db
                    .withId(diagnosisId("finished"))
                    .withCause("pipeline has finished running because its inputs have been closed and events have been processed")
                    .withAction("if you expect this pipeline to run indefinitely, you will need to configure its inputs to continue receiving or fetching events")
                    .withHelpUrl(HELP_URL.withAnchor("finished").toString()))
                .withImpact(NOT_PROCESSING.withSeverity(10).withDescription("pipeline has finished running").build())
                .build(),
            Status.State.TERMINATED, () -> Analysis.builder()
                .withStatus(RED)
                .withDiagnosis(db -> db
                    .withId(diagnosisId("terminated"))
                    .withCause("pipeline is not running, likely because it has encountered an error")
                    .withAction("view logs to determine the cause of abnormal pipeline shutdown")
                    .withHelpUrl(HELP_URL.withAnchor("terminated").toString()))
                .withImpact(NOT_PROCESSING.withSeverity(1).build())
                .build()
        );

        @Override
        public Analysis analyze(final Details details) {
            return STRATEGIES.getOrDefault(details.getStatus().getState(), () -> Analysis.builder()
                .withStatus(UNKNOWN)
                .withDiagnosis(db -> db
                    .withId(diagnosisId("unknown"))
                    .withCause("pipeline is not known; it may have been recently deleted or failed to start")
                    .withAction("view logs to determine if the pipeline failed to start")
                    .withHelpUrl(HELP_URL.withAnchor("unknown").toString()))
                .withImpact(NOT_PROCESSING.withSeverity(2).build())
                .build()).get();
        }

        static String diagnosisId(final String state) {
            return String.format("logstash:health:pipeline:status:diagnosis:%s", state);
        }

        static String impactId(final String state) {
            return String.format("logstash:health:pipeline:status:impact:%s", state);
        }
    }
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `logstash-core/src/main/java/org/logstash/health/PipelineIndicator.java` | 292 → 284 | 17 → 17 | 2.53 → 2.24 | 27 → 22 | 0 → 0 |

## Diff

```diff
diff --git a/logstash-core/src/main/java/org/logstash/health/PipelineIndicator.java b/logstash-core/src/main/java/org/logstash/health/PipelineIndicator.java
index ce6a5ed..1f8d3a7 100644
--- a/logstash-core/src/main/java/org/logstash/health/PipelineIndicator.java
+++ b/logstash-core/src/main/java/org/logstash/health/PipelineIndicator.java
@@ -185,55 +185,48 @@ public class PipelineIndicator extends ProbeIndicator<PipelineIndicator.Details>
 
         static final HelpUrl HELP_URL = new HelpUrl("health-report-pipeline-status");
 
+        private static final Map<Status.State, java.util.function.Supplier<Analysis>> STRATEGIES = Map.of(
+            Status.State.LOADING, () -> Analysis.builder()
+                .withStatus(YELLOW)
+                .withDiagnosis(db -> db
+                    .withId(diagnosisId("loading"))
+                    .withCause("pipeline is loading")
+                    .withAction("if pipeline does not come up quickly, you may need to check the logs to see if it is stalled")
+                    .withHelpUrl(HELP_URL.withAnchor("loading").toString()))
+                .withImpact(NOT_PROCESSING.withSeverity(1).withDescription("pipeline is loading").build())
+                .build(),
+            Status.State.RUNNING, () -> Analysis.builder().withStatus(GREEN).build(),
+            Status.State.FINISHED, () -> Analysis.builder()
+                .withStatus(YELLOW)
+                .withDiagnosis(db -> db
+                    .withId(diagnosisId("finished"))
+                    .withCause("pipeline has finished running because its inputs have been closed and events have been processed")
+                    .withAction("if you expect this pipeline to run indefinitely, you will need to configure its inputs to continue receiving or fetching events")
+                    .withHelpUrl(HELP_URL.withAnchor("finished").toString()))
+                .withImpact(NOT_PROCESSING.withSeverity(10).withDescription("pipeline has finished running").build())
+                .build(),
+            Status.State.TERMINATED, () -> Analysis.builder()
+                .withStatus(RED)
+                .withDiagnosis(db -> db
+                    .withId(diagnosisId("terminated"))
+                    .withCause("pipeline is not running, likely because it has encountered an error")
+                    .withAction("view logs to determine the cause of abnormal pipeline shutdown")
+                    .withHelpUrl(HELP_URL.withAnchor("terminated").toString()))
+                .withImpact(NOT_PROCESSING.withSeverity(1).build())
+                .build()
+        );
+
         @Override
         public Analysis analyze(final Details details) {
-            switch (details.getStatus().getState()) {
-                case LOADING:
-                    return Analysis.builder()
-                            .withStatus(YELLOW)
-                            .withDiagnosis(db -> db
-                                    .withId(diagnosisId("loading"))
-                                    .withCause("pipeline is loading")
-                                    .withAction("if pipeline does not come up quickly, you may need to check the logs to see if it is stalled")
-                                    .withHelpUrl(HELP_URL.withAnchor("loading").toString()))
-                            .withImpact(NOT_PROCESSING.withSeverity(1).withDescription("pipeline is loading").build())
-                            .build();
-                case RUNNING:
-                    return Analysis.builder()
-                            .withStatus(GREEN)
-                            .build();
-                case FINISHED:
-                    return Analysis.builder()
-                            .withStatus(YELLOW)
-                            .withDiagnosis(db -> db
-                                    .withId(diagnosisId("finished"))
-                                    .withCause("pipeline has finished running because its inputs have been closed and events have been processed")
-                                    .withAction("if you expect this pipeline to run indefinitely, you will need to configure its inputs to continue receiving or fetching events")
-                                    .withHelpUrl(HELP_URL.withAnchor("finished").toString()))
-                            .withImpact(NOT_PROCESSING.withSeverity(10).withDescription("pipeline has finished running").build())
-                            .build();
-                case TERMINATED:
-                    return Analysis.builder()
-                            .withStatus(RED)
-                            .withDiagnosis(db -> db
-                                    .withId(diagnosisId("terminated"))
-                                    .withCause("pipeline is not running, likely because it has encountered an error")
-                                    .withAction("view logs to determine the cause of abnormal pipeline shutdown")
-                                    .withHelpUrl(HELP_URL.withAnchor("terminated").toString()))
-                            .withImpact(NOT_PROCESSING.withSeverity(1).build())
-                            .build();
-                case UNKNOWN:
-                default:
-                    return Analysis.builder()
-                            .withStatus(UNKNOWN)
-                            .withDiagnosis(db -> db
-                                    .withId(diagnosisId("unknown"))
-                                    .withCause("pipeline is not known; it may have been recently deleted or failed to start")
-                                    .withAction("view logs to determine if the pipeline failed to start")
-                                    .withHelpUrl(HELP_URL.withAnchor("unknown").toString()))
-                            .withImpact(NOT_PROCESSING.withSeverity(2).build())
-                            .build();
-            }
+            return STRATEGIES.getOrDefault(details.getStatus().getState(), () -> Analysis.builder()
+                .withStatus(UNKNOWN)
+                .withDiagnosis(db -> db
+                    .withId(diagnosisId("unknown"))
+                    .withCause("pipeline is not known; it may have been recently deleted or failed to start")
+                    .withAction("view logs to determine if the pipeline failed to start")
+                    .withHelpUrl(HELP_URL.withAnchor("unknown").toString()))
+                .withImpact(NOT_PROCESSING.withSeverity(2).build())
+                .build()).get();
         }
 
         static String diagnosisId(final String state) {
@@ -243,8 +236,6 @@ public class PipelineIndicator extends ProbeIndicator<PipelineIndicator.Details>
         static String impactId(final String state) {
             return String.format("logstash:health:pipeline:status:impact:%s", state);
         }
-
-
     }
 
     static class FlowWorkerUtilizationProbe implements Probe<Details> {

```
