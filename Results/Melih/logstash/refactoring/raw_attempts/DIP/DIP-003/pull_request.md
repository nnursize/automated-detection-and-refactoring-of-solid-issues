# Refactor DIP-003 (DIP): Direct instantiation of internal components

**Status:** `applied_unverified`  
**Branch:** `refactor/DIP-003` -> `main`  
**Head commit:** `6ab463252ad389786239b27ff8cb0b5fed663ad9`  
**LLM finish:** `FinishReason.STOP` (prompt 6908, completion 545)  

## Detected issue

- **File**: `logstash-core/src/main/java/org/logstash/config/ir/CompiledPipeline.java`
- **Entity**: `CompiledPipeline.CompiledPipeline` (class)
- **Lines (at detection time)**: L96–L113
- **Severity**: medium
- **Confidence**: detected by 3 scan(s)

**Description.** Direct instantiation of internal components

**Reasoning.** The constructor directly instantiates ConfigVariableExpander and other internal components, making it difficult to swap these dependencies for testing or alternative configurations.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `logstash-core/src/main/java/org/logstash/config/ir/CompiledPipeline.java`

**Summary.** Inject ConfigVariableExpander into CompiledPipeline constructor

**Rationale.** The CompiledPipeline class was directly instantiating ConfigVariableExpander, which couples it to specific implementation details and makes testing difficult. By injecting the ConfigVariableExpander (or a factory/provider for it) into the constructor, we adhere to the Dependency Inversion Principle.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `logstash-core/src/main/java/org/logstash/config/ir/CompiledPipeline.java` (19-line block → 26-line replacement)

**Replaces:**

```java
    public CompiledPipeline(
            final PipelineIR pipelineIR,
            final RubyIntegration.PluginFactory pluginFactory,
            final SecretStore secretStore,
            final AbstractPipelineExt.ConditionalEvaluationListener conditionalErrListener)
    {
        this.pipelineIR = pipelineIR;
        this.pluginFactory = pluginFactory;
        this.conditionalErrListener = conditionalErrListener;
        try (ConfigVariableExpander cve = new ConfigVariableExpander(
                secretStore,
                EnvironmentVariableProvider.defaultProvider())) {
            inputs = setupInputs(cve);
            filters = setupFilters(cve);
            outputs = setupOutputs(cve);
        } catch (Exception e) {
            throw new IllegalStateException("Unable to configure plugins: " + e.getMessage(), e);
        }
    }
```

**With:**

```java
    public CompiledPipeline(
            final PipelineIR pipelineIR,
            final RubyIntegration.PluginFactory pluginFactory,
            final SecretStore secretStore,
            final AbstractPipelineExt.ConditionalEvaluationListener conditionalErrListener)
    {
        this(pipelineIR, pluginFactory, new ConfigVariableExpander(secretStore, EnvironmentVariableProvider.defaultProvider()), conditionalErrListener);
    }

    public CompiledPipeline(
            final PipelineIR pipelineIR,
            final RubyIntegration.PluginFactory pluginFactory,
            final ConfigVariableExpander cve,
            final AbstractPipelineExt.ConditionalEvaluationListener conditionalErrListener)
    {
        this.pipelineIR = pipelineIR;
        this.pluginFactory = pluginFactory;
        this.conditionalErrListener = conditionalErrListener;
        try {
            inputs = setupInputs(cve);
            filters = setupFilters(cve);
            outputs = setupOutputs(cve);
        } catch (Exception e) {
            throw new IllegalStateException("Unable to configure plugins: " + e.getMessage(), e);
        }
    }
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `logstash-core/src/main/java/org/logstash/config/ir/CompiledPipeline.java` | 502 → 508 | 27 → 27 | 2.52 → 2.52 | 42 → 42 | 0 → 0 |

## Diff

```diff
diff --git a/logstash-core/src/main/java/org/logstash/config/ir/CompiledPipeline.java b/logstash-core/src/main/java/org/logstash/config/ir/CompiledPipeline.java
index e851e0f..d150cc3 100644
--- a/logstash-core/src/main/java/org/logstash/config/ir/CompiledPipeline.java
+++ b/logstash-core/src/main/java/org/logstash/config/ir/CompiledPipeline.java
@@ -123,13 +123,20 @@ public final class CompiledPipeline {
             final RubyIntegration.PluginFactory pluginFactory,
             final SecretStore secretStore,
             final AbstractPipelineExt.ConditionalEvaluationListener conditionalErrListener)
+    {
+        this(pipelineIR, pluginFactory, new ConfigVariableExpander(secretStore, EnvironmentVariableProvider.defaultProvider()), conditionalErrListener);
+    }
+
+    public CompiledPipeline(
+            final PipelineIR pipelineIR,
+            final RubyIntegration.PluginFactory pluginFactory,
+            final ConfigVariableExpander cve,
+            final AbstractPipelineExt.ConditionalEvaluationListener conditionalErrListener)
     {
         this.pipelineIR = pipelineIR;
         this.pluginFactory = pluginFactory;
         this.conditionalErrListener = conditionalErrListener;
-        try (ConfigVariableExpander cve = new ConfigVariableExpander(
-                secretStore,
-                EnvironmentVariableProvider.defaultProvider())) {
+        try {
             inputs = setupInputs(cve);
             filters = setupFilters(cve);
             outputs = setupOutputs(cve);

```
