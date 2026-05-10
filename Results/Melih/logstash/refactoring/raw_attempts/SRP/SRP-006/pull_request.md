# Refactor SRP-006 (SRP): Combines plugin resolution with specific wiring logic for different plugin ty...

**Status:** `applied_unverified`  
**Branch:** `refactor/SRP-006` -> `main`  
**Head commit:** `35dea20c06626fcdd3105683ab602910f8605765`  
**LLM finish:** `FinishReason.STOP` (prompt 4882, completion 2418)  

## Detected issue

- **File**: `logstash-core/src/main/java/org/logstash/plugins/factory/PluginFactoryExt.java`
- **Entity**: `PluginFactoryExt` (class)
- **Lines (at detection time)**: L30–L260
- **Severity**: medium
- **Confidence**: detected by 1 scan(s)

**Description.** Combines plugin resolution with specific wiring logic for different plugin types.

**Reasoning.** The class is responsible for: 1) Resolving plugin names to classes, 2) Generating unique IDs, 3) Instantiating Ruby vs Java plugins, and 4) Wiring specific metrics and execution contexts into the plugins. It contains specialized logic for 'FilterDelegators' and 'OutputDelegators' that goes beyond simple instantiation, mixing factory logic with configuration and monitoring setup.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 5
- **Files created** (1): `logstash-core/src/main/java/org/logstash/plugins/factory/PluginIdGenerator.java`
- **Files modified** (1): `logstash-core/src/main/java/org/logstash/plugins/factory/PluginFactoryExt.java`

**Summary.** Extract plugin ID generation logic to a dedicated helper class

**Rationale.** The PluginFactoryExt class was responsible for both plugin instantiation and complex ID generation logic. Moving the ID generation to a dedicated PluginIdGenerator class improves SRP by separating the concern of identifying plugins from the concern of creating them.

## Changes overview

_5 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `logstash-core/src/main/java/org/logstash/plugins/factory/PluginFactoryExt.java` (5-line block → 7-line replacement)

**Replaces:**

```java
    private transient ConfigVariableExpander configVariables;

    private transient PluginResolver pluginResolver;

    private final transient Map<PluginLookup.PluginType, AbstractPluginCreator<? extends Plugin>> pluginCreatorsRegistry = new HashMap<>(4);
```

**With:**

```java
    private transient ConfigVariableExpander configVariables;

    private transient PluginResolver pluginResolver;

    private transient PluginIdGenerator idGenerator;

    private final transient Map<PluginLookup.PluginType, AbstractPluginCreator<? extends Plugin>> pluginCreatorsRegistry = new HashMap<>(4);
```

### 2. EDIT `logstash-core/src/main/java/org/logstash/plugins/factory/PluginFactoryExt.java` (5-line block → 6-line replacement)

**Replaces:**

```java
        this.pluginCreatorsRegistry.put(PluginLookup.PluginType.FILTER, new FilterPluginCreator());
        this.pluginCreatorsRegistry.put(PluginLookup.PluginType.OUTPUT, new OutputPluginCreator(this));
        this.configVariables = ConfigVariableExpander.withoutSecret(envVars);
        return this;
    }
```

**With:**

```java
        this.pluginCreatorsRegistry.put(PluginLookup.PluginType.FILTER, new FilterPluginCreator());
        this.pluginCreatorsRegistry.put(PluginLookup.PluginType.OUTPUT, new OutputPluginCreator(this));
        this.configVariables = ConfigVariableExpander.withoutSecret(envVars);
        this.idGenerator = new PluginIdGenerator(lir, this.configVariables);
        return this;
    }
```

### 3. EDIT `logstash-core/src/main/java/org/logstash/plugins/factory/PluginFactoryExt.java` (8-line block → 8-line replacement)

**Replaces:**

```java
    private IRubyObject plugin(final ThreadContext context,
                               final PluginLookup.PluginType type,
                               final String name,
                               final RubyHash args,
                               final SourceWithMetadata source) {
        final String id = generateOrRetrievePluginId(type, source, args);

        if (id == null) {
```

**With:**

```java
    private IRubyObject plugin(final ThreadContext context,
                               final PluginLookup.PluginType type,
                               final String name,
                               final RubyHash args,
                               final SourceWithMetadata source) {
        final String id = idGenerator.generateOrRetrievePluginId(type, source, args);

        if (id == null) {
```

### 4. EDIT `logstash-core/src/main/java/org/logstash/plugins/factory/PluginFactoryExt.java` (88-line block → 17-line replacement)

**Replaces:**

```java
    private Map<String, Object> convertToJavaCoercible(Map<String, Object> input) {
        final Map<String, Object> output = new HashMap<>(input);

        // Intercept Codecs
        for (final Map.Entry<String, Object> entry : input.entrySet()) {
            final String key = entry.getKey();
            final Object value = entry.getValue();
            if (value instanceof IRubyObject) {
                final Object unwrapped = JavaUtil.unwrapJavaValue((IRubyObject) value);
                if (unwrapped instanceof Codec) {
                    output.put(key, unwrapped);
                }
            }
        }

        return output;
    }

    // TODO: caller seems to think that the args is `Map<String, IRubyObject>`, but
    //       at least any `id` present is actually a `String`.
    private String generateOrRetrievePluginId(final PluginLookup.PluginType type,
                                              final SourceWithMetadata source,
                                              final Map<String, ?> args) {
        final Optional<String> unprocessedId;
        if (source == null) {
            unprocessedId = extractId(() -> extractIdFromArgs(args),
                                      this::generateUUID);
        } else {
            unprocessedId = extractId(() -> extractIdFromLIR(source),
                                      () -> extractIdFromArgs(args),
                                      () -> generateUUIDForCodecs(type));
        }

        return unprocessedId
                .map(configVariables::expand)
                .filter(String.class::isInstance)
                .map(String.class::cast)
                .orElse(null);
    }

    private Optional<String> extractId(final IdExtractor... extractors) {
        for (IdExtractor extractor : extractors) {
            final Optional<String> extracted = extractor.extract();
            if (extracted.isPresent()) {
                return extracted;
            }
        }
        return Optional.empty();
    }

    @FunctionalInterface
    interface IdExtractor {
        Optional<String> extract();
    }

    private Optional<String> extractIdFromArgs(final Map<String, ?> args) {
        if (!args.containsKey("id")) {
            return Optional.empty();
        }

... (28 more line(s) truncated)
```

**With:**

```java
    private Map<String, Object> convertToJavaCoercible(Map<String, Object> input) {
        final Map<String, Object> output = new HashMap<>(input);

        // Intercept Codecs
        for (final Map.Entry<String, Object> entry : input.entrySet()) {
            final String key = entry.getKey();
            final Object value = entry.getValue();
            if (value instanceof IRubyObject) {
                final Object unwrapped = JavaUtil.unwrapJavaValue((IRubyObject) value);
                if (unwrapped instanceof Codec) {
                    output.put(key, unwrapped);
                }
            }
        }

        return output;
    }
```

### 5. CREATE `logstash-core/src/main/java/org/logstash/plugins/factory/PluginIdGenerator.java` (89 line(s))

```java
package org.logstash.plugins.factory;

import org.logstash.common.SourceWithMetadata;
import org.logstash.config.ir.PipelineIR;
import org.logstash.config.ir.graph.Vertex;
import org.logstash.plugins.ConfigVariableExpander;
import org.logstash.plugins.PluginLookup;
import org.jruby.RubyString;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;

public final class PluginIdGenerator {
    private final PipelineIR lir;
    private final ConfigVariableExpander configVariables;

    public PluginIdGenerator(PipelineIR lir, ConfigVariableExpander configVariables) {
        this.lir = lir;
        this.configVariables = configVariables;
    }

    public String generateOrRetrievePluginId(final PluginLookup.PluginType type,
                                              final SourceWithMetadata source,
                                              final Map<String, ?> args) {
        final Optional<String> unprocessedId;
        if (source == null) {
            unprocessedId = extractId(() -> extractIdFromArgs(args),
                                      this::generateUUID);
        } else {
            unprocessedId = extractId(() -> extractIdFromLIR(source),
                                      () -> extractIdFromArgs(args),
                                      () -> generateUUIDForCodecs(type));
        }

        return unprocessedId
                .map(configVariables::expand)
                .filter(String.class::isInstance)
                .map(String.class::cast)
                .orElse(null);
    }

    private Optional<String> extractId(final IdExtractor... extractors) {
        for (IdExtractor extractor : extractors) {
            final Optional<String> extracted = extractor.extract();
            if (extracted.isPresent()) {
                return extracted;
            }
        }
        return Optional.empty();
    }

    @FunctionalInterface
    interface IdExtractor {
        Optional<String> extract();
    }

    private Optional<String> extractIdFromArgs(final Map<String, ?> args) {
        if (!args.containsKey("id")) {
            return Optional.empty();
        }
... (29 more line(s) truncated)
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `logstash-core/src/main/java/org/logstash/plugins/factory/PluginFactoryExt.java` | 308 → 250 | 17 → 11 | 2.12 → 2 | 20 → 12 | 0 → 0 |
| `logstash-core/src/main/java/org/logstash/plugins/factory/PluginIdGenerator.java` | - → 78 | - → 6 | - → 2.33 | - → 9 | - → 0 |

## Diff

```diff
diff --git a/logstash-core/src/main/java/org/logstash/plugins/factory/PluginFactoryExt.java b/logstash-core/src/main/java/org/logstash/plugins/factory/PluginFactoryExt.java
index 13d231a..db0aaf2 100644
--- a/logstash-core/src/main/java/org/logstash/plugins/factory/PluginFactoryExt.java
+++ b/logstash-core/src/main/java/org/logstash/plugins/factory/PluginFactoryExt.java
@@ -58,6 +58,8 @@ public final class PluginFactoryExt extends RubyBasicObject
 
     private transient PluginResolver pluginResolver;
 
+    private transient PluginIdGenerator idGenerator;
+
     private final transient Map<PluginLookup.PluginType, AbstractPluginCreator<? extends Plugin>> pluginCreatorsRegistry = new HashMap<>(4);
 
     @JRubyMethod(name = "filter_delegator", meta = true, required = 5)
@@ -111,6 +113,7 @@ public final class PluginFactoryExt extends RubyBasicObject
         this.pluginCreatorsRegistry.put(PluginLookup.PluginType.FILTER, new FilterPluginCreator());
         this.pluginCreatorsRegistry.put(PluginLookup.PluginType.OUTPUT, new OutputPluginCreator(this));
         this.configVariables = ConfigVariableExpander.withoutSecret(envVars);
+        this.idGenerator = new PluginIdGenerator(lir, this.configVariables);
         return this;
     }
 
@@ -207,7 +210,7 @@ public final class PluginFactoryExt extends RubyBasicObject
                                final String name,
                                final RubyHash args,
                                final SourceWithMetadata source) {
-        final String id = generateOrRetrievePluginId(type, source, args);
+        final String id = idGenerator.generateOrRetrievePluginId(type, source, args);
 
         if (id == null) {
             throw context.runtime.newRaiseException(
@@ -287,77 +290,6 @@ public final class PluginFactoryExt extends RubyBasicObject
         return output;
     }
 
-    // TODO: caller seems to think that the args is `Map<String, IRubyObject>`, but
-    //       at least any `id` present is actually a `String`.
-    private String generateOrRetrievePluginId(final PluginLookup.PluginType type,
-                                              final SourceWithMetadata source,
-                                              final Map<String, ?> args) {
-        final Optional<String> unprocessedId;
-        if (source == null) {
-            unprocessedId = extractId(() -> extractIdFromArgs(args),
-                                      this::generateUUID);
-        } else {
-            unprocessedId = extractId(() -> extractIdFromLIR(source),
-                                      () -> extractIdFromArgs(args),
-                                      () -> generateUUIDForCodecs(type));
-        }
-
-        return unprocessedId
-                .map(configVariables::expand)
-                .filter(String.class::isInstance)
-                .map(String.class::cast)
-                .orElse(null);
-    }
-
-    private Optional<String> extractId(final IdExtractor... extractors) {
-        for (IdExtractor extractor : extractors) {
-            final Optional<String> extracted = extractor.extract();
-            if (extracted.isPresent()) {
-                return extracted;
-            }
-        }
-        return Optional.empty();
-    }
-
-    @FunctionalInterface
-    interface IdExtractor {
-        Optional<String> extract();
-    }
-
-    private Optional<String> extractIdFromArgs(final Map<String, ?> args) {
-        if (!args.containsKey("id")) {
-            return Optional.empty();
-        }
-
-        final Object explicitId = args.get("id");
-        if (explicitId instanceof String) {
-            return Optional.of((String) explicitId);
-        } else if (explicitId instanceof RubyString) {
-            return Optional.of(((RubyString) explicitId).asJavaString());
-        } else {
-            return Optional.empty();
-        }
-    }
-
-    private Optional<String> generateUUID() {
-        return Optional.of(UUID.randomUUID().toString());
-    }
-
-    private Optional<String> generateUUIDForCodecs(final PluginLookup.PluginType pluginType) {
-        if (pluginType == PluginLookup.PluginType.CODEC) {
-            return generateUUID();
-        }
-        return Optional.empty();
-    }
-
-    private Optional<String> extractIdFromLIR(final SourceWithMetadata source) {
-        return lir.getGraph().vertices()
-                .filter(v -> v.getSourceWithMetadata() != null
-                        && v.getSourceWithMetadata().equalsWithoutText(source))
-                .findFirst()
-                .map(Vertex::getId);
-    }
-
     ExecutionContextFactoryExt getExecutionContextFactory() {
         return executionContextFactory;
     }
diff --git a/logstash-core/src/main/java/org/logstash/plugins/factory/PluginIdGenerator.java b/logstash-core/src/main/java/org/logstash/plugins/factory/PluginIdGenerator.java
new file mode 100644
index 0000000..0000000
--- /dev/null
+++ b/logstash-core/src/main/java/org/logstash/plugins/factory/PluginIdGenerator.java
@@ -0,0 +1,89 @@
+package org.logstash.plugins.factory;
+
+import org.logstash.common.SourceWithMetadata;
+import org.logstash.config.ir.PipelineIR;
+import org.logstash.config.ir.graph.Vertex;
+import org.logstash.plugins.ConfigVariableExpander;
+import org.logstash.plugins.PluginLookup;
+import org.jruby.RubyString;
+import java.util.Map;
+import java.util.Optional;
+import java.util.UUID;
+
+public final class PluginIdGenerator {
+    private final PipelineIR lir;
+    private final ConfigVariableExpander configVariables;
+
+    public PluginIdGenerator(PipelineIR lir, ConfigVariableExpander configVariables) {
+        this.lir = lir;
+        this.configVariables = configVariables;
+    }
+
+    public String generateOrRetrievePluginId(final PluginLookup.PluginType type,
+                                              final SourceWithMetadata source,
+                                              final Map<String, ?> args) {
+        final Optional<String> unprocessedId;
+        if (source == null) {
+            unprocessedId = extractId(() -> extractIdFromArgs(args),
+                                      this::generateUUID);
+        } else {
+            unprocessedId = extractId(() -> extractIdFromLIR(source),
+                                      () -> extractIdFromArgs(args),
+                                      () -> generateUUIDForCodecs(type));
+        }
+
+        return unprocessedId
+                .map(configVariables::expand)
+                .filter(String.class::isInstance)
+                .map(String.class::cast)
+                .orElse(null);
+    }
+
+    private Optional<String> extractId(final IdExtractor... extractors) {
+        for (IdExtractor extractor : extractors) {
+            final Optional<String> extracted = extractor.extract();
+            if (extracted.isPresent()) {
+                return extracted;
+            }
+        }
+        return Optional.empty();
+    }
+
+    @FunctionalInterface
+    interface IdExtractor {
+        Optional<String> extract();
+    }
+
+    private Optional<String> extractIdFromArgs(final Map<String, ?> args) {
+        if (!args.containsKey("id")) {
+            return Optional.empty();
+        }
+        final Object explicitId = args.get("id");
+        if (explicitId instanceof String) {
+            return Optional.of((String) explicitId);
+        } else if (explicitId instanceof RubyString) {
+            return Optional.of(((RubyString) explicitId).asJavaString());
+        } else {
+            return Optional.empty();
+        }
+    }
+
+    private Optional<String> generateUUID() {
+        return Optional.of(UUID.randomUUID().toString());
+    }
+
+    private Optional<String> generateUUIDForCodecs(final PluginLookup.PluginType pluginType) {
+        if (pluginType == PluginLookup.PluginType.CODEC) {
+            return generateUUID();
+        }
+        return Optional.empty();
+    }
+
+    private Optional<String> extractIdFromLIR(final SourceWithMetadata source) {
+        return lir.getGraph().vertices()
+                .filter(v -> v.getSourceWithMetadata() != null
+                        && v.getSourceWithMetadata().equalsWithoutText(source))
+                .findFirst()
+                .map(Vertex::getId);
+    }
+}
\ No newline at end of file

```
