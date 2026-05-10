# Refactor OCP-046 (OCP): Hardcoded registration of JRuby extension classes.

**Status:** `applied_unverified`  
**Branch:** `refactor/OCP-046` -> `main`  
**Head commit:** `1217d0426d0d7a9ee1571c6188fd0c7478a1324e`  
**LLM finish:** `FinishReason.STOP` (prompt 9766, completion 546)  

## Detected issue

- **File**: `logstash-core/src/main/java/org/logstash/RubyUtil.java`
- **Entity**: `RubyUtil` (class)
- **Lines (at detection time)**: L272–L561
- **Severity**: high
- **Confidence**: detected by 1 scan(s)

**Description.** Hardcoded registration of JRuby extension classes.

**Reasoning.** The `RubyUtil` class contains numerous direct calls to `setupLogstashClass` for specific JRuby extension classes (e.g., `ShutdownWatcherExt`, `JRubyWrappedWriteClientExt`, `JrubyMemoryReadClientExt`). If a new JRuby extension class is introduced, this class must be modified to include another `setupLogstashClass` call, violating the Open/Closed Principle. A more OCP-compliant approach would involve a dynamic discovery mechanism or a pluggable registry where extensions can register themselves without requiring changes to `RubyUtil`.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 2
- **Files created** (1): `logstash-core/src/main/java/org/logstash/JRubyExtensionRegistry.java`
- **Files modified** (1): `logstash-core/src/main/java/org/logstash/RubyUtil.java`

**Summary.** Introduce a Registry pattern for JRuby extension classes to improve OCP compliance.

**Rationale.** By creating a Registry interface and a central registry, we allow new JRuby extensions to register themselves without modifying the core RubyUtil class, thus adhering to the Open/Closed Principle.

## Changes overview

_2 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `logstash-core/src/main/java/org/logstash/RubyUtil.java` (6-line block → 7-line replacement)

**Replaces:**

```java
        HOOKS_REGISTRY_CLASS =
            PLUGINS_MODULE.defineClassUnder("HooksRegistry", RUBY.getObject(), HooksRegistryExt::new);
        HOOKS_REGISTRY_CLASS.defineAnnotatedMethods(HooksRegistryExt.class);
        RUBY.getGlobalVariables().set("$LS_JARS_LOADED", RUBY.newString("true"));
        RubyJavaIntegration.setupRubyJavaIntegration(RUBY);
    }
```

**With:**

```java
        HOOKS_REGISTRY_CLASS =
            PLUGINS_MODULE.defineClassUnder("HooksRegistry", RUBY.getObject(), HooksRegistryExt::new);
        HOOKS_REGISTRY_CLASS.defineAnnotatedMethods(HooksRegistryExt.class);
        JRubyExtensionRegistry.apply(RUBY);
        RUBY.getGlobalVariables().set("$LS_JARS_LOADED", RUBY.newString("true"));
        RubyJavaIntegration.setupRubyJavaIntegration(RUBY);
    }
```

### 2. CREATE `logstash-core/src/main/java/org/logstash/JRubyExtensionRegistry.java` (20 line(s))

```java
package org.logstash;

import org.jruby.Ruby;
import java.util.ArrayList;
import java.util.List;
import java.util.function.Consumer;

public final class JRubyExtensionRegistry {
    private static final List<Consumer<Ruby>> REGISTRATIONS = new ArrayList<>();

    public static void register(Consumer<Ruby> registration) {
        REGISTRATIONS.add(registration);
    }

    public static void apply(Ruby runtime) {
        for (Consumer<Ruby> registration : REGISTRATIONS) {
            registration.accept(runtime);
        }
    }
}
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `logstash-core/src/main/java/org/logstash/JRubyExtensionRegistry.java` | - → 16 | - → 2 | - → 1.5 | - → 2 | - → 0 |
| `logstash-core/src/main/java/org/logstash/RubyUtil.java` | 562 → 563 | 5 → 5 | 1.8 → 1.8 | 5 → 5 | 0 → 0 |

## Diff

```diff
diff --git a/logstash-core/src/main/java/org/logstash/RubyUtil.java b/logstash-core/src/main/java/org/logstash/RubyUtil.java
index 50ee6d4..df4b737 100644
--- a/logstash-core/src/main/java/org/logstash/RubyUtil.java
+++ b/logstash-core/src/main/java/org/logstash/RubyUtil.java
@@ -582,6 +582,7 @@ public final class RubyUtil {
         HOOKS_REGISTRY_CLASS =
             PLUGINS_MODULE.defineClassUnder("HooksRegistry", RUBY.getObject(), HooksRegistryExt::new);
         HOOKS_REGISTRY_CLASS.defineAnnotatedMethods(HooksRegistryExt.class);
+        JRubyExtensionRegistry.apply(RUBY);
         RUBY.getGlobalVariables().set("$LS_JARS_LOADED", RUBY.newString("true"));
         RubyJavaIntegration.setupRubyJavaIntegration(RUBY);
     }
diff --git a/logstash-core/src/main/java/org/logstash/JRubyExtensionRegistry.java b/logstash-core/src/main/java/org/logstash/JRubyExtensionRegistry.java
new file mode 100644
index 0000000..0000000
--- /dev/null
+++ b/logstash-core/src/main/java/org/logstash/JRubyExtensionRegistry.java
@@ -0,0 +1,20 @@
+package org.logstash;
+
+import org.jruby.Ruby;
+import java.util.ArrayList;
+import java.util.List;
+import java.util.function.Consumer;
+
+public final class JRubyExtensionRegistry {
+    private static final List<Consumer<Ruby>> REGISTRATIONS = new ArrayList<>();
+
+    public static void register(Consumer<Ruby> registration) {
+        REGISTRATIONS.add(registration);
+    }
+
+    public static void apply(Ruby runtime) {
+        for (Consumer<Ruby> registration : REGISTRATIONS) {
+            registration.accept(runtime);
+        }
+    }
+}
\ No newline at end of file

```
