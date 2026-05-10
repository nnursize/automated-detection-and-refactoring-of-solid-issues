# Refactor OCP-092 (OCP): Hardcoded list of built-in TypeAdapterFactories violates OCP.

**Status:** `applied_unverified`  
**Branch:** `refactor/OCP-092` -> `main`  
**Head commit:** `222ee34f528a0b2cb308817b426bd47da75440c6`  
**LLM finish:** `FinishReason.STOP` (prompt 14114, completion 969)  

## Detected issue

- **File**: `gson/src/main/java/com/google/gson/GsonBuilder.java`
- **Entity**: `GsonBuilder.createFactories` (method)
- **Lines (at detection time)**: L700–L766
- **Severity**: high
- **Confidence**: detected by 3 scan(s)

**Description.** Hardcoded list of built-in TypeAdapterFactories violates OCP.

**Reasoning.** The `createFactories` method explicitly adds a fixed list of `TypeAdapterFactory` instances for various types. If Gson needs to support a new built-in type or a new way of handling an existing type, this method must be modified to add the new factory. This makes the class closed for extension without modification.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 2
- **Files modified** (1): `gson/src/main/java/com/google/gson/GsonBuilder.java`

**Summary.** Introduce a registry for built-in TypeAdapterFactories to support OCP

**Rationale.** By moving the hardcoded list of built-in factories into a registry (or a static list that can be extended), we allow new factories to be added without modifying the core GsonBuilder logic. This implementation uses a static list of providers that can be appended to, adhering to the Open/Closed Principle.

## Changes overview

_2 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `gson/src/main/java/com/google/gson/GsonBuilder.java` (5-line block → 30-line replacement)

**Replaces:**

```java
  static final List<TypeAdapterFactory> DEFAULT_TYPE_ADAPTER_FACTORIES =
      GsonBuilder.DEFAULT.createFactories(
          DEFAULT_CONSTRUCTOR_CONSTRUCTOR, DEFAULT_JSON_ADAPTER_ANNOTATION_TYPE_ADAPTER_FACTORY);

  Excluder excluder = Excluder.DEFAULT;
```

**With:**

```java
  static final List<TypeAdapterFactory> DEFAULT_TYPE_ADAPTER_FACTORIES =
      GsonBuilder.DEFAULT.createFactories(
          DEFAULT_CONSTRUCTOR_CONSTRUCTOR, DEFAULT_JSON_ADAPTER_ANNOTATION_TYPE_ADAPTER_FACTORY);

  private static final List<TypeAdapterFactoryProvider> BUILT_IN_FACTORY_PROVIDERS = new ArrayList<>();

  static {
    BUILT_IN_FACTORY_PROVIDERS.add(factories -> {
      factories.add(TypeAdapters.JSON_ELEMENT_FACTORY);
      factories.add(ObjectTypeAdapter.getFactory(DEFAULT.objectToNumberStrategy));
    });
    BUILT_IN_FACTORY_PROVIDERS.add(factories -> {
      factories.add(new CollectionTypeAdapterFactory(DEFAULT_CONSTRUCTOR_CONSTRUCTOR));
      factories.add(new MapTypeAdapterFactory(DEFAULT_CONSTRUCTOR_CONSTRUCTOR, DEFAULT.complexMapKeySerialization));
      factories.add(DEFAULT_JSON_ADAPTER_ANNOTATION_TYPE_ADAPTER_FACTORY);
      factories.add(TypeAdapters.ENUM_FACTORY);
    });
  }

  /** @internal */
  public static void registerBuiltInFactoryProvider(TypeAdapterFactoryProvider provider) {
    BUILT_IN_FACTORY_PROVIDERS.add(provider);
  }

  /** @internal */
  public interface TypeAdapterFactoryProvider {
    void addFactories(List<TypeAdapterFactory> factories);
  }

  Excluder excluder = Excluder.DEFAULT;
```

### 2. EDIT `gson/src/main/java/com/google/gson/GsonBuilder.java` (27-line block → 23-line replacement)

**Replaces:**

```java
    // built-in type adapters that cannot be overridden
    factories.add(TypeAdapters.JSON_ELEMENT_FACTORY);
    factories.add(ObjectTypeAdapter.getFactory(objectToNumberStrategy));

    // the excluder must precede all adapters that handle user-defined types
    factories.add(excluder);

    // users' type adapters
    addUserDefinedAdapters(factories);

    // custom Date adapters
    addDateTypeAdapters(factories);

    addPlatformTypeAdapters(factories);

    // type adapters for composite and user-defined types
    factories.add(new CollectionTypeAdapterFactory(constructorConstructor));
    factories.add(new MapTypeAdapterFactory(constructorConstructor, complexMapKeySerialization));
    factories.add(jsonAdapterFactory);
    factories.add(TypeAdapters.ENUM_FACTORY);
    factories.add(
        new ReflectiveTypeAdapterFactory(
            constructorConstructor,
            fieldNamingPolicy,
            excluder,
            jsonAdapterFactory,
            newImmutableList(reflectionFilters)));
```

**With:**

```java
    // built-in type adapters
    for (TypeAdapterFactoryProvider provider : BUILT_IN_FACTORY_PROVIDERS) {
      provider.addFactories(factories);
    }

    // the excluder must precede all adapters that handle user-defined types
    factories.add(excluder);

    // users' type adapters
    addUserDefinedAdapters(factories);

    // custom Date adapters
    addDateTypeAdapters(factories);

    addPlatformTypeAdapters(factories);

    factories.add(
        new ReflectiveTypeAdapterFactory(
            constructorConstructor,
            fieldNamingPolicy,
            excluder,
            jsonAdapterFactory,
            newImmutableList(reflectionFilters)));
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `gson/src/main/java/com/google/gson/GsonBuilder.java` | 998 → 1016 | 38 → 39 | 4.24 → 4.15 | 124 → 124 | 0 → 0 |

## Diff

```diff
diff --git a/gson/src/main/java/com/google/gson/GsonBuilder.java b/gson/src/main/java/com/google/gson/GsonBuilder.java
index 6e411f6..74d09a2 100644
--- a/gson/src/main/java/com/google/gson/GsonBuilder.java
+++ b/gson/src/main/java/com/google/gson/GsonBuilder.java
@@ -125,6 +125,31 @@ public final class GsonBuilder {
       GsonBuilder.DEFAULT.createFactories(
           DEFAULT_CONSTRUCTOR_CONSTRUCTOR, DEFAULT_JSON_ADAPTER_ANNOTATION_TYPE_ADAPTER_FACTORY);
 
+  private static final List<TypeAdapterFactoryProvider> BUILT_IN_FACTORY_PROVIDERS = new ArrayList<>();
+
+  static {
+    BUILT_IN_FACTORY_PROVIDERS.add(factories -> {
+      factories.add(TypeAdapters.JSON_ELEMENT_FACTORY);
+      factories.add(ObjectTypeAdapter.getFactory(DEFAULT.objectToNumberStrategy));
+    });
+    BUILT_IN_FACTORY_PROVIDERS.add(factories -> {
+      factories.add(new CollectionTypeAdapterFactory(DEFAULT_CONSTRUCTOR_CONSTRUCTOR));
+      factories.add(new MapTypeAdapterFactory(DEFAULT_CONSTRUCTOR_CONSTRUCTOR, DEFAULT.complexMapKeySerialization));
+      factories.add(DEFAULT_JSON_ADAPTER_ANNOTATION_TYPE_ADAPTER_FACTORY);
+      factories.add(TypeAdapters.ENUM_FACTORY);
+    });
+  }
+
+  /** @internal */
+  public static void registerBuiltInFactoryProvider(TypeAdapterFactoryProvider provider) {
+    BUILT_IN_FACTORY_PROVIDERS.add(provider);
+  }
+
+  /** @internal */
+  public interface TypeAdapterFactoryProvider {
+    void addFactories(List<TypeAdapterFactory> factories);
+  }
+
   Excluder excluder = Excluder.DEFAULT;
   LongSerializationPolicy longSerializationPolicy = LongSerializationPolicy.DEFAULT;
   FieldNamingStrategy fieldNamingPolicy = DEFAULT_FIELD_NAMING_STRATEGY;
@@ -927,9 +952,10 @@ public final class GsonBuilder {
       JsonAdapterAnnotationTypeAdapterFactory jsonAdapterFactory) {
     ArrayList<TypeAdapterFactory> factories = new ArrayList<>();
 
-    // built-in type adapters that cannot be overridden
-    factories.add(TypeAdapters.JSON_ELEMENT_FACTORY);
-    factories.add(ObjectTypeAdapter.getFactory(objectToNumberStrategy));
+    // built-in type adapters
+    for (TypeAdapterFactoryProvider provider : BUILT_IN_FACTORY_PROVIDERS) {
+      provider.addFactories(factories);
+    }
 
     // the excluder must precede all adapters that handle user-defined types
     factories.add(excluder);
@@ -942,11 +968,6 @@ public final class GsonBuilder {
 
     addPlatformTypeAdapters(factories);
 
-    // type adapters for composite and user-defined types
-    factories.add(new CollectionTypeAdapterFactory(constructorConstructor));
-    factories.add(new MapTypeAdapterFactory(constructorConstructor, complexMapKeySerialization));
-    factories.add(jsonAdapterFactory);
-    factories.add(TypeAdapters.ENUM_FACTORY);
     factories.add(
         new ReflectiveTypeAdapterFactory(
             constructorConstructor,

```
