# Refactor DIP-006 (DIP): Direct instantiation of multiple concrete TypeAdapterFactory implementations.

**Status:** `applied_unverified`  
**Branch:** `refactor/DIP-006` -> `main`  
**Head commit:** `dd2635882c62183384495a6af7ced47dd7ad7df6`  
**LLM finish:** `FinishReason.STOP` (prompt 14325, completion 509)  

## Detected issue

- **File**: `gson/src/main/java/com/google/gson/GsonBuilder.java`
- **Entity**: `GsonBuilder.createFactories` (method)
- **Lines (at detection time)**: L582–L645
- **Severity**: high
- **Confidence**: detected by 2 scan(s)

**Description.** Direct instantiation of multiple concrete TypeAdapterFactory implementations.

**Reasoning.** The createFactories method contains a long list of direct 'new' calls to instantiate concrete factories such as CollectionTypeAdapterFactory, MapTypeAdapterFactory, and ReflectiveTypeAdapterFactory. This creates a hard-coded dependency on every specific adapter implementation in the library, violating the principle that modules should depend on abstractions (TypeAdapterFactory) rather than specific details.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 2
- **Files modified** (1): `gson/src/main/java/com/google/gson/GsonBuilder.java`

**Summary.** Move concrete factory instantiation into the built-in factory provider mechanism

**Rationale.** The direct instantiation of CollectionTypeAdapterFactory and MapTypeAdapterFactory in createFactories violates DIP. Moving these into the existing BUILT_IN_FACTORY_PROVIDERS list centralizes the registration of built-in factories and removes the hard-coded dependency from the core creation logic.

## Changes overview

_2 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `gson/src/main/java/com/google/gson/GsonBuilder.java` (6-line block → 14-line replacement)

**Replaces:**

```java
    BUILT_IN_FACTORY_PROVIDERS.add(factories -> {
      factories.add(new CollectionTypeAdapterFactory(DEFAULT_CONSTRUCTOR_CONSTRUCTOR));
      factories.add(new MapTypeAdapterFactory(DEFAULT_CONSTRUCTOR_CONSTRUCTOR, DEFAULT.complexMapKeySerialization));
      factories.add(DEFAULT_JSON_ADAPTER_ANNOTATION_TYPE_ADAPTER_FACTORY);
      factories.add(TypeAdapters.ENUM_FACTORY);
    });
```

**With:**

```java
    BUILT_IN_FACTORY_PROVIDERS.add(factories -> {
      factories.add(new CollectionTypeAdapterFactory(DEFAULT_CONSTRUCTOR_CONSTRUCTOR));
      factories.add(new MapTypeAdapterFactory(DEFAULT_CONSTRUCTOR_CONSTRUCTOR, DEFAULT.complexMapKeySerialization));
      factories.add(DEFAULT_JSON_ADAPTER_ANNOTATION_TYPE_ADAPTER_FACTORY);
      factories.add(TypeAdapters.ENUM_FACTORY);
    });
    BUILT_IN_FACTORY_PROVIDERS.add(factories -> {
      factories.add(new ReflectiveTypeAdapterFactory(
          DEFAULT_CONSTRUCTOR_CONSTRUCTOR,
          DEFAULT.fieldNamingPolicy,
          Excluder.DEFAULT,
          DEFAULT_JSON_ADAPTER_ANNOTATION_TYPE_ADAPTER_FACTORY,
          Collections.emptyList()));
    });
```

### 2. EDIT `gson/src/main/java/com/google/gson/GsonBuilder.java` (9-line block → 1-line replacement)

**Replaces:**

```java
    factories.add(
        new ReflectiveTypeAdapterFactory(
            constructorConstructor,
            fieldNamingPolicy,
            excluder,
            jsonAdapterFactory,
            newImmutableList(reflectionFilters)));

    factories.trimToSize();
```

**With:**

```java
    factories.trimToSize();
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `gson/src/main/java/com/google/gson/GsonBuilder.java` | 1016 → 1017 | 39 → 39 | 4.15 → 4.15 | 124 → 124 | 0 → 0 |

## Diff

```diff
diff --git a/gson/src/main/java/com/google/gson/GsonBuilder.java b/gson/src/main/java/com/google/gson/GsonBuilder.java
index 74d09a2..c7da8ab 100644
--- a/gson/src/main/java/com/google/gson/GsonBuilder.java
+++ b/gson/src/main/java/com/google/gson/GsonBuilder.java
@@ -138,6 +138,14 @@ public final class GsonBuilder {
       factories.add(DEFAULT_JSON_ADAPTER_ANNOTATION_TYPE_ADAPTER_FACTORY);
       factories.add(TypeAdapters.ENUM_FACTORY);
     });
+    BUILT_IN_FACTORY_PROVIDERS.add(factories -> {
+      factories.add(new ReflectiveTypeAdapterFactory(
+          DEFAULT_CONSTRUCTOR_CONSTRUCTOR,
+          DEFAULT.fieldNamingPolicy,
+          Excluder.DEFAULT,
+          DEFAULT_JSON_ADAPTER_ANNOTATION_TYPE_ADAPTER_FACTORY,
+          Collections.emptyList()));
+    });
   }
 
   /** @internal */
@@ -968,14 +976,6 @@ public final class GsonBuilder {
 
     addPlatformTypeAdapters(factories);
 
-    factories.add(
-        new ReflectiveTypeAdapterFactory(
-            constructorConstructor,
-            fieldNamingPolicy,
-            excluder,
-            jsonAdapterFactory,
-            newImmutableList(reflectionFilters)));
-
     factories.trimToSize();
     return Collections.unmodifiableList(factories);
   }

```
