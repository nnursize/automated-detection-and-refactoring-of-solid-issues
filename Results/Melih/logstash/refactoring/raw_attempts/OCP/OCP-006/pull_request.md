# Refactor OCP-006 (OCP): Hardcoded branching logic for plugin instantiation based on type

**Status:** `applied_unverified`  
**Branch:** `refactor/OCP-006` -> `main`  
**Head commit:** `4f259db5fd67516b137065985ee40103fe653f84`  
**LLM finish:** `FinishReason.STOP` (prompt 4325, completion 1527)  

## Detected issue

- **File**: `logstash-core/src/main/java/org/logstash/plugins/factory/PluginFactoryExt.java`
- **Entity**: `PluginFactoryExt.plugin` (method)
- **Lines (at detection time)**: L220–L251
- **Severity**: medium
- **Confidence**: detected by 3 scan(s)

**Description.** Hardcoded branching logic for plugin instantiation based on type

**Reasoning.** The private plugin method contains hardcoded if/else logic to handle specific PluginType values (OUTPUT, FILTER, etc.). The logic for creating delegators and assigning metrics is tightly coupled to these specific categories. Adding a new architectural plugin category would require modifying this factory method.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 3
- **Files modified** (1): `logstash-core/src/main/java/org/logstash/plugins/factory/PluginFactoryExt.java`

**Summary.** Refactor Ruby plugin instantiation to use the PluginCreator strategy pattern

**Rationale.** The hardcoded if/else logic for Ruby plugin types (OUTPUT, FILTER, etc.) was replaced by a registry-based approach using the existing AbstractPluginCreator hierarchy, ensuring the factory is closed for modification when new plugin types are added.

## Changes overview

_3 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `logstash-core/src/main/java/org/logstash/plugins/factory/PluginFactoryExt.java` (22-line block → 1-line replacement)

**Replaces:**

```java
    private final transient Map<PluginLookup.PluginType, AbstractPluginCreator<? extends Plugin>> pluginCreatorsRegistry = new HashMap<>(4);

    @JRubyMethod(name = "filter_delegator", meta = true, required = 5)
    public static IRubyObject filterDelegator(final ThreadContext context,
                                              final IRubyObject recv, final IRubyObject... args) {
        //  filterDelegatorClass, klass, rubyArgs, typeScopedMetric, executionCntx
        final RubyClass filterDelegatorClass = (RubyClass) args[0];
        final RubyClass klass = (RubyClass) args[1];
        final RubyHash arguments = (RubyHash) args[2];
        final AbstractMetricExt typeScopedMetric = (AbstractMetricExt) args[3];
        final ExecutionContextExt executionContext = (ExecutionContextExt) args[4];

        final IRubyObject filterInstance = ContextualizerExt.initializePlugin(context, executionContext, klass, arguments);

        final RubyString id = (RubyString) arguments.op_aref(context, ID_KEY);
        filterInstance.callMethod(
                context, "metric=",
                typeScopedMetric.namespace(context, id.intern())
        );

        return filterDelegatorClass.newInstance(context, filterInstance, id, Block.NULL_BLOCK);
    }
```

**With:**

```java
    private final transient Map<PluginLookup.PluginType, AbstractPluginCreator<? extends Plugin>> pluginCreatorsRegistry = new HashMap<>(4);
```

### 2. EDIT `logstash-core/src/main/java/org/logstash/plugins/factory/PluginFactoryExt.java` (4-line block → 4-line replacement)

**Replaces:**

```java
        this.pluginCreatorsRegistry.put(PluginLookup.PluginType.INPUT, new InputPluginCreator(this));
        this.pluginCreatorsRegistry.put(PluginLookup.PluginType.CODEC, new CodecPluginCreator());
        this.pluginCreatorsRegistry.put(PluginLookup.PluginType.FILTER, new FilterPluginCreator());
        this.pluginCreatorsRegistry.put(PluginLookup.PluginType.OUTPUT, new OutputPluginCreator(this));
```

**With:**

```java
        this.pluginCreatorsRegistry.put(PluginLookup.PluginType.INPUT, new InputPluginCreator(this));
        this.pluginCreatorsRegistry.put(PluginLookup.PluginType.CODEC, new CodecPluginCreator());
        this.pluginCreatorsRegistry.put(PluginLookup.PluginType.FILTER, new FilterPluginCreator(filterClass));
        this.pluginCreatorsRegistry.put(PluginLookup.PluginType.OUTPUT, new OutputPluginCreator(this));
```

### 3. EDIT `logstash-core/src/main/java/org/logstash/plugins/factory/PluginFactoryExt.java` (42-line block → 21-line replacement)

**Replaces:**

```java
        final PluginLookup.PluginClass pluginClass = pluginResolver.resolve(type, name);
        if (pluginClass.language() == PluginLookup.PluginLanguage.RUBY) {

            final Map<String, Object> newArgs = new HashMap<>(args);
            newArgs.put("id", id);
            final RubyClass klass = (RubyClass) pluginClass.klass();
            final ExecutionContextExt executionCntx = executionContextFactory.create(
                    context, RubyUtil.RUBY.newString(id), klass.callMethod(context, "config_name")
            );
            final RubyHash rubyArgs = RubyHash.newHash(context.runtime);
            rubyArgs.putAll(newArgs);
            if (type == PluginLookup.PluginType.OUTPUT) {
                return new OutputDelegatorExt(context.runtime, RubyUtil.RUBY_OUTPUT_DELEGATOR_CLASS).initialize(
                        context,
                        new IRubyObject[]{
                                klass, typeScopedMetric, executionCntx,
                                OutputStrategyExt.OutputStrategyRegistryExt.instance(context, null),
                                rubyArgs
                        }
                );
            } else if (type == PluginLookup.PluginType.FILTER) {
                return filterDelegator(
                        context, null,
                        filterDelegatorClass, klass, rubyArgs, typeScopedMetric, executionCntx);
            } else {
                final IRubyObject pluginInstance = ContextualizerExt.initializePlugin(context, executionCntx, klass, rubyArgs);

                final AbstractNamespacedMetricExt scopedMetric = typeScopedMetric.namespace(context, RubyUtil.RUBY.newString(id).intern());
                scopedMetric.gauge(context, MetricKeys.NAME_KEY, pluginInstance.callMethod(context, "config_name"));
                pluginInstance.callMethod(context, "metric=", scopedMetric);
                return pluginInstance;
            }
        } else {
            AbstractPluginCreator<? extends Plugin> pluginCreator = pluginCreatorsRegistry.get(type);
            if (pluginCreator == null) {
                throw new IllegalStateException("Unable to create plugin: " + pluginClass.toReadableString());
            }

            Context contextWithMetrics = executionContextFactory.toContext(type, metrics.getRoot(context));
            return pluginCreator.createDelegator(name, convertToJavaCoercible(args), id, typeScopedMetric, pluginClass, contextWithMetrics);
        }
    }
```

**With:**

```java
        final PluginLookup.PluginClass pluginClass = pluginResolver.resolve(type, name);
        AbstractPluginCreator<? extends Plugin> pluginCreator = pluginCreatorsRegistry.get(type);
        if (pluginCreator == null) {
            throw new IllegalStateException("Unable to create plugin: " + pluginClass.toReadableString());
        }

        if (pluginClass.language() == PluginLookup.PluginLanguage.RUBY) {
            final Map<String, Object> newArgs = new HashMap<>(args);
            newArgs.put("id", id);
            final RubyClass klass = (RubyClass) pluginClass.klass();
            final ExecutionContextExt executionCntx = executionContextFactory.create(
                    context, RubyUtil.RUBY.newString(id), klass.callMethod(context, "config_name")
            );
            final RubyHash rubyArgs = RubyHash.newHash(context.runtime);
            rubyArgs.putAll(newArgs);
            return pluginCreator.createRubyDelegator(context, klass, rubyArgs, typeScopedMetric, executionCntx);
        } else {
            Context contextWithMetrics = executionContextFactory.toContext(type, metrics.getRoot(context));
            return pluginCreator.createDelegator(name, convertToJavaCoercible(args), id, typeScopedMetric, pluginClass, contextWithMetrics);
        }
    }
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `logstash-core/src/main/java/org/logstash/plugins/factory/PluginFactoryExt.java` | 250 → 215 | 11 → 10 | 2 → 1.9 | 12 → 10 | 0 → 0 |

## Diff

```diff
diff --git a/logstash-core/src/main/java/org/logstash/plugins/factory/PluginFactoryExt.java b/logstash-core/src/main/java/org/logstash/plugins/factory/PluginFactoryExt.java
index db0aaf2..75ac666 100644
--- a/logstash-core/src/main/java/org/logstash/plugins/factory/PluginFactoryExt.java
+++ b/logstash-core/src/main/java/org/logstash/plugins/factory/PluginFactoryExt.java
@@ -62,27 +62,6 @@ public final class PluginFactoryExt extends RubyBasicObject
 
     private final transient Map<PluginLookup.PluginType, AbstractPluginCreator<? extends Plugin>> pluginCreatorsRegistry = new HashMap<>(4);
 
-    @JRubyMethod(name = "filter_delegator", meta = true, required = 5)
-    public static IRubyObject filterDelegator(final ThreadContext context,
-                                              final IRubyObject recv, final IRubyObject... args) {
-        //  filterDelegatorClass, klass, rubyArgs, typeScopedMetric, executionCntx
-        final RubyClass filterDelegatorClass = (RubyClass) args[0];
-        final RubyClass klass = (RubyClass) args[1];
-        final RubyHash arguments = (RubyHash) args[2];
-        final AbstractMetricExt typeScopedMetric = (AbstractMetricExt) args[3];
-        final ExecutionContextExt executionContext = (ExecutionContextExt) args[4];
-
-        final IRubyObject filterInstance = ContextualizerExt.initializePlugin(context, executionContext, klass, arguments);
-
-        final RubyString id = (RubyString) arguments.op_aref(context, ID_KEY);
-        filterInstance.callMethod(
-                context, "metric=",
-                typeScopedMetric.namespace(context, id.intern())
-        );
-
-        return filterDelegatorClass.newInstance(context, filterInstance, id, Block.NULL_BLOCK);
-    }
-
     public PluginFactoryExt(final Ruby runtime, final RubyClass metaClass) {
         this(runtime, metaClass, new PluginLookup(PluginRegistry.getInstance()));
     }
@@ -110,7 +89,7 @@ public final class PluginFactoryExt extends RubyBasicObject
         this.filterDelegatorClass = filterClass;
         this.pluginCreatorsRegistry.put(PluginLookup.PluginType.INPUT, new InputPluginCreator(this));
         this.pluginCreatorsRegistry.put(PluginLookup.PluginType.CODEC, new CodecPluginCreator());
-        this.pluginCreatorsRegistry.put(PluginLookup.PluginType.FILTER, new FilterPluginCreator());
+        this.pluginCreatorsRegistry.put(PluginLookup.PluginType.FILTER, new FilterPluginCreator(filterClass));
         this.pluginCreatorsRegistry.put(PluginLookup.PluginType.OUTPUT, new OutputPluginCreator(this));
         this.configVariables = ConfigVariableExpander.withoutSecret(envVars);
         this.idGenerator = new PluginIdGenerator(lir, this.configVariables);
@@ -230,8 +209,12 @@ public final class PluginFactoryExt extends RubyBasicObject
         final AbstractNamespacedMetricExt typeScopedMetric = metrics.create(context, type.rubyLabel());
 
         final PluginLookup.PluginClass pluginClass = pluginResolver.resolve(type, name);
-        if (pluginClass.language() == PluginLookup.PluginLanguage.RUBY) {
+        AbstractPluginCreator<? extends Plugin> pluginCreator = pluginCreatorsRegistry.get(type);
+        if (pluginCreator == null) {
+            throw new IllegalStateException("Unable to create plugin: " + pluginClass.toReadableString());
+        }
 
+        if (pluginClass.language() == PluginLookup.PluginLanguage.RUBY) {
             final Map<String, Object> newArgs = new HashMap<>(args);
             newArgs.put("id", id);
             final RubyClass klass = (RubyClass) pluginClass.klass();
@@ -240,33 +223,8 @@ public final class PluginFactoryExt extends RubyBasicObject
             );
             final RubyHash rubyArgs = RubyHash.newHash(context.runtime);
             rubyArgs.putAll(newArgs);
-            if (type == PluginLookup.PluginType.OUTPUT) {
-                return new OutputDelegatorExt(context.runtime, RubyUtil.RUBY_OUTPUT_DELEGATOR_CLASS).initialize(
-                        context,
-                        new IRubyObject[]{
-                                klass, typeScopedMetric, executionCntx,
-                                OutputStrategyExt.OutputStrategyRegistryExt.instance(context, null),
-                                rubyArgs
-                        }
-                );
-            } else if (type == PluginLookup.PluginType.FILTER) {
-                return filterDelegator(
-                        context, null,
-                        filterDelegatorClass, klass, rubyArgs, typeScopedMetric, executionCntx);
-            } else {
-                final IRubyObject pluginInstance = ContextualizerExt.initializePlugin(context, executionCntx, klass, rubyArgs);
-
-                final AbstractNamespacedMetricExt scopedMetric = typeScopedMetric.namespace(context, RubyUtil.RUBY.newString(id).intern());
-                scopedMetric.gauge(context, MetricKeys.NAME_KEY, pluginInstance.callMethod(context, "config_name"));
-                pluginInstance.callMethod(context, "metric=", scopedMetric);
-                return pluginInstance;
-            }
+            return pluginCreator.createRubyDelegator(context, klass, rubyArgs, typeScopedMetric, executionCntx);
         } else {
-            AbstractPluginCreator<? extends Plugin> pluginCreator = pluginCreatorsRegistry.get(type);
-            if (pluginCreator == null) {
-                throw new IllegalStateException("Unable to create plugin: " + pluginClass.toReadableString());
-            }
-
             Context contextWithMetrics = executionContextFactory.toContext(type, metrics.getRoot(context));
             return pluginCreator.createDelegator(name, convertToJavaCoercible(args), id, typeScopedMetric, pluginClass, contextWithMetrics);
         }

```
