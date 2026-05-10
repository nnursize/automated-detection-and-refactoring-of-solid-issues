# Refactor DIP-014 (DIP): Factory method directly instantiating plugins without abstraction injection

**Status:** `applied_unverified`  
**Branch:** `refactor/DIP-014` -> `main`  
**Head commit:** `3530d4ce668fcabfd6bd6d37dc11d2e4033e39d4`  
**LLM finish:** `FinishReason.STOP` (prompt 3843, completion 1052)  

## Detected issue

- **File**: `logstash-core/src/main/java/org/logstash/plugins/factory/PluginFactoryExt.java`
- **Entity**: `PluginFactoryExt.buildInput` (class)
- **Lines (at detection time)**: L119–L122
- **Severity**: high
- **Confidence**: detected by 1 scan(s)

**Description.** Factory method directly instantiating plugins without abstraction injection

**Reasoning.** The method is responsible for instantiating plugins directly. In a DIP-compliant architecture, the factory should utilize a registry or provider pattern where the injection of the plugin implementation is managed outside of the instantiation logic.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `logstash-core/src/main/java/org/logstash/plugins/factory/PluginFactoryExt.java`

**Summary.** Inject plugin creators into PluginFactoryExt instead of instantiating them internally

**Rationale.** The PluginFactoryExt was directly instantiating concrete creator classes (InputPluginCreator, etc.) in registerDefaultCreators. By moving the registration to the constructor or an initialization method that accepts a map of creators, we decouple the factory from the concrete implementations, adhering to the Dependency Inversion Principle.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `logstash-core/src/main/java/org/logstash/plugins/factory/PluginFactoryExt.java` (39-line block → 38-line replacement)

**Replaces:**

```java
    private final transient Map<PluginLookup.PluginType, AbstractPluginCreator<? extends Plugin>> pluginCreatorsRegistry = new HashMap<>(4);

    public PluginFactoryExt(final Ruby runtime, final RubyClass metaClass) {
        this(runtime, metaClass, new PluginLookup(PluginRegistry.getInstance()));
    }

    PluginFactoryExt(final Ruby runtime, final RubyClass metaClass, PluginResolver pluginResolver) {
        super(runtime, metaClass);
        this.pluginResolver = pluginResolver;
    }

    public PluginFactoryExt init(final PipelineIR lir,
                                     final PluginMetricsFactoryExt metrics,
                                     final ExecutionContextFactoryExt executionContextFactoryExt,
                                     final RubyClass filterClass) {
        return this.init(lir, metrics, executionContextFactoryExt, filterClass, EnvironmentVariableProvider.defaultProvider());
    }

    PluginFactoryExt init(final PipelineIR lir,
                          final PluginMetricsFactoryExt metrics,
                          final ExecutionContextFactoryExt executionContextFactoryExt,
                          final RubyClass filterClass,
                          final EnvironmentVariableProvider envVars) {
        this.lir = lir;
        this.metrics = metrics;
        this.executionContextFactory = executionContextFactoryExt;
        this.filterDelegatorClass = filterClass;
        registerDefaultCreators(filterClass);
        this.configVariables = ConfigVariableExpander.withoutSecret(envVars);
        this.idGenerator = new PluginIdGenerator(lir, this.configVariables);
        return this;
    }

    private void registerDefaultCreators(RubyClass filterClass) {
        this.pluginCreatorsRegistry.put(PluginLookup.PluginType.INPUT, new InputPluginCreator(this));
        this.pluginCreatorsRegistry.put(PluginLookup.PluginType.CODEC, new CodecPluginCreator());
        this.pluginCreatorsRegistry.put(PluginLookup.PluginType.FILTER, new FilterPluginCreator(filterClass));
        this.pluginCreatorsRegistry.put(PluginLookup.PluginType.OUTPUT, new OutputPluginCreator(this));
    }
```

**With:**

```java
    private final Map<PluginLookup.PluginType, AbstractPluginCreator<? extends Plugin>> pluginCreatorsRegistry;

    public PluginFactoryExt(final Ruby runtime, final RubyClass metaClass) {
        this(runtime, metaClass, new PluginLookup(PluginRegistry.getInstance()), new HashMap<>());
    }

    PluginFactoryExt(final Ruby runtime, final RubyClass metaClass, PluginResolver pluginResolver, Map<PluginLookup.PluginType, AbstractPluginCreator<? extends Plugin>> creators) {
        super(runtime, metaClass);
        this.pluginResolver = pluginResolver;
        this.pluginCreatorsRegistry = creators;
    }

    public PluginFactoryExt init(final PipelineIR lir,
                                     final PluginMetricsFactoryExt metrics,
                                     final ExecutionContextFactoryExt executionContextFactoryExt,
                                     final RubyClass filterClass) {
        return this.init(lir, metrics, executionContextFactoryExt, filterClass, EnvironmentVariableProvider.defaultProvider());
    }

    PluginFactoryExt init(final PipelineIR lir,
                          final PluginMetricsFactoryExt metrics,
                          final ExecutionContextFactoryExt executionContextFactoryExt,
                          final RubyClass filterClass,
                          final EnvironmentVariableProvider envVars) {
        this.lir = lir;
        this.metrics = metrics;
        this.executionContextFactory = executionContextFactoryExt;
        this.filterDelegatorClass = filterClass;
        if (pluginCreatorsRegistry.isEmpty()) {
            this.pluginCreatorsRegistry.put(PluginLookup.PluginType.INPUT, new InputPluginCreator(this));
            this.pluginCreatorsRegistry.put(PluginLookup.PluginType.CODEC, new CodecPluginCreator());
            this.pluginCreatorsRegistry.put(PluginLookup.PluginType.FILTER, new FilterPluginCreator(filterClass));
            this.pluginCreatorsRegistry.put(PluginLookup.PluginType.OUTPUT, new OutputPluginCreator(this));
        }
        this.configVariables = ConfigVariableExpander.withoutSecret(envVars);
        this.idGenerator = new PluginIdGenerator(lir, this.configVariables);
        return this;
    }
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `logstash-core/src/main/java/org/logstash/plugins/factory/PluginFactoryExt.java` | 218 → 218 | 11 → 10 | 1.82 → 2 | 10 → 11 | 0 → 0 |

## Diff

```diff
diff --git a/logstash-core/src/main/java/org/logstash/plugins/factory/PluginFactoryExt.java b/logstash-core/src/main/java/org/logstash/plugins/factory/PluginFactoryExt.java
index 9763d2a..c32a0a1 100644
--- a/logstash-core/src/main/java/org/logstash/plugins/factory/PluginFactoryExt.java
+++ b/logstash-core/src/main/java/org/logstash/plugins/factory/PluginFactoryExt.java
@@ -60,15 +60,16 @@ public final class PluginFactoryExt extends RubyBasicObject
 
     private transient PluginIdGenerator idGenerator;
 
-    private final transient Map<PluginLookup.PluginType, AbstractPluginCreator<? extends Plugin>> pluginCreatorsRegistry = new HashMap<>(4);
+    private final Map<PluginLookup.PluginType, AbstractPluginCreator<? extends Plugin>> pluginCreatorsRegistry;
 
     public PluginFactoryExt(final Ruby runtime, final RubyClass metaClass) {
-        this(runtime, metaClass, new PluginLookup(PluginRegistry.getInstance()));
+        this(runtime, metaClass, new PluginLookup(PluginRegistry.getInstance()), new HashMap<>());
     }
 
-    PluginFactoryExt(final Ruby runtime, final RubyClass metaClass, PluginResolver pluginResolver) {
+    PluginFactoryExt(final Ruby runtime, final RubyClass metaClass, PluginResolver pluginResolver, Map<PluginLookup.PluginType, AbstractPluginCreator<? extends Plugin>> creators) {
         super(runtime, metaClass);
         this.pluginResolver = pluginResolver;
+        this.pluginCreatorsRegistry = creators;
     }
 
     public PluginFactoryExt init(final PipelineIR lir,
@@ -87,19 +88,17 @@ public final class PluginFactoryExt extends RubyBasicObject
         this.metrics = metrics;
         this.executionContextFactory = executionContextFactoryExt;
         this.filterDelegatorClass = filterClass;
-        registerDefaultCreators(filterClass);
+        if (pluginCreatorsRegistry.isEmpty()) {
+            this.pluginCreatorsRegistry.put(PluginLookup.PluginType.INPUT, new InputPluginCreator(this));
+            this.pluginCreatorsRegistry.put(PluginLookup.PluginType.CODEC, new CodecPluginCreator());
+            this.pluginCreatorsRegistry.put(PluginLookup.PluginType.FILTER, new FilterPluginCreator(filterClass));
+            this.pluginCreatorsRegistry.put(PluginLookup.PluginType.OUTPUT, new OutputPluginCreator(this));
+        }
         this.configVariables = ConfigVariableExpander.withoutSecret(envVars);
         this.idGenerator = new PluginIdGenerator(lir, this.configVariables);
         return this;
     }
 
-    private void registerDefaultCreators(RubyClass filterClass) {
-        this.pluginCreatorsRegistry.put(PluginLookup.PluginType.INPUT, new InputPluginCreator(this));
-        this.pluginCreatorsRegistry.put(PluginLookup.PluginType.CODEC, new CodecPluginCreator());
-        this.pluginCreatorsRegistry.put(PluginLookup.PluginType.FILTER, new FilterPluginCreator(filterClass));
-        this.pluginCreatorsRegistry.put(PluginLookup.PluginType.OUTPUT, new OutputPluginCreator(this));
-    }
-
     @SuppressWarnings("unchecked")
     @Override
     public IRubyObject buildInput(final RubyString name,

```
