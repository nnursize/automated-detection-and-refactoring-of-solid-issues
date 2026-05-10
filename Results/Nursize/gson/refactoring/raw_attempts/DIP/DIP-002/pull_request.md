# Refactor DIP-002 (DIP): Static initialization of concrete internal components.

**Status:** `applied_unverified`  
**Branch:** `refactor/DIP-002` -> `main`  
**Head commit:** `785a485a7badc5ce438c8f1675a6d4410de7d2f8`  
**LLM finish:** `FinishReason.STOP` (prompt 14341, completion 1006)  

## Detected issue

- **File**: `gson/src/main/java/com/google/gson/GsonBuilder.java`
- **Entity**: `GsonBuilder` (class)
- **Lines (at detection time)**: L111–L117
- **Severity**: medium
- **Confidence**: detected by 2 scan(s)

**Description.** Static initialization of concrete internal components.

**Reasoning.** GsonBuilder hard-codes the creation of DEFAULT_CONSTRUCTOR_CONSTRUCTOR and DEFAULT_JSON_ADAPTER_ANNOTATION_TYPE_ADAPTER_FACTORY. This prevents the inversion of control and forces the library to always use these specific concrete implementations for its default state.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `gson/src/main/java/com/google/gson/GsonBuilder.java`

**Summary.** Remove static initialization of concrete dependencies in GsonBuilder

**Rationale.** The static fields DEFAULT_CONSTRUCTOR_CONSTRUCTOR and DEFAULT_JSON_ADAPTER_ANNOTATION_TYPE_ADAPTER_FACTORY tightly coupled GsonBuilder to specific implementations. By removing these static initializations and relying on instance-level creation or lazy initialization, we improve testability and adhere to the Dependency Inversion Principle.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `gson/src/main/java/com/google/gson/GsonBuilder.java` (41-line block → 30-line replacement)

**Replaces:**

```java
  static final ConstructorConstructor DEFAULT_CONSTRUCTOR_CONSTRUCTOR =
      new ConstructorConstructor(
          Collections.emptyMap(), DEFAULT_USE_JDK_UNSAFE, Collections.emptyList());

  static final JsonAdapterAnnotationTypeAdapterFactory
      DEFAULT_JSON_ADAPTER_ANNOTATION_TYPE_ADAPTER_FACTORY =
          new JsonAdapterAnnotationTypeAdapterFactory(DEFAULT_CONSTRUCTOR_CONSTRUCTOR);

  /**
   * Default instance of the builder, to be used only by the default {@link Gson#Gson()}
   * constructor. Must not be used for anything else and must not be leaked to user code, since that
   * could lead to accidental modification of this default builder.
   */
  static final GsonBuilder DEFAULT = new GsonBuilder();

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
    BUILT_IN_FACTORY_PROVIDERS.add(factories -> {
      factories.add(new ReflectiveTypeAdapterFactory(
          DEFAULT_CONSTRUCTOR_CONSTRUCTOR,
          DEFAULT.fieldNamingPolicy,
          Excluder.DEFAULT,
          DEFAULT_JSON_ADAPTER_ANNOTATION_TYPE_ADAPTER_FACTORY,
          Collections.emptyList()));
    });
  }
```

**With:**

```java
  private static final List<TypeAdapterFactoryProvider> BUILT_IN_FACTORY_PROVIDERS = new ArrayList<>();

  static {
    BUILT_IN_FACTORY_PROVIDERS.add(factories -> {
      factories.add(TypeAdapters.JSON_ELEMENT_FACTORY);
      factories.add(ObjectTypeAdapter.getFactory(ToNumberPolicy.DOUBLE));
    });
    BUILT_IN_FACTORY_PROVIDERS.add(factories -> {
      ConstructorConstructor constructorConstructor = new ConstructorConstructor(
          Collections.emptyMap(), DEFAULT_USE_JDK_UNSAFE, Collections.emptyList());
      JsonAdapterAnnotationTypeAdapterFactory jsonAdapterFactory =
          new JsonAdapterAnnotationTypeAdapterFactory(constructorConstructor);
      factories.add(new CollectionTypeAdapterFactory(constructorConstructor));
      factories.add(new MapTypeAdapterFactory(constructorConstructor, DEFAULT_COMPLEX_MAP_KEYS));
      factories.add(jsonAdapterFactory);
      factories.add(TypeAdapters.ENUM_FACTORY);
    });
    BUILT_IN_FACTORY_PROVIDERS.add(factories -> {
      ConstructorConstructor constructorConstructor = new ConstructorConstructor(
          Collections.emptyMap(), DEFAULT_USE_JDK_UNSAFE, Collections.emptyList());
      JsonAdapterAnnotationTypeAdapterFactory jsonAdapterFactory =
          new JsonAdapterAnnotationTypeAdapterFactory(constructorConstructor);
      factories.add(new ReflectiveTypeAdapterFactory(
          constructorConstructor,
          DEFAULT_FIELD_NAMING_STRATEGY,
          Excluder.DEFAULT,
          jsonAdapterFactory,
          Collections.emptyList()));
    });
  }
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `gson/src/main/java/com/google/gson/GsonBuilder.java` | 1017 → 1010 | 39 → 39 | 4.15 → 4.13 | 124 → 123 | 0 → 0 |

## Diff

```diff
diff --git a/gson/src/main/java/com/google/gson/GsonBuilder.java b/gson/src/main/java/com/google/gson/GsonBuilder.java
index c7da8ab..6503100 100644
--- a/gson/src/main/java/com/google/gson/GsonBuilder.java
+++ b/gson/src/main/java/com/google/gson/GsonBuilder.java
@@ -106,44 +106,33 @@ public final class GsonBuilder {
   private static final ToNumberStrategy DEFAULT_NUMBER_TO_NUMBER_STRATEGY =
       ToNumberPolicy.LAZILY_PARSED_NUMBER;
 
-  static final ConstructorConstructor DEFAULT_CONSTRUCTOR_CONSTRUCTOR =
-      new ConstructorConstructor(
-          Collections.emptyMap(), DEFAULT_USE_JDK_UNSAFE, Collections.emptyList());
-
-  static final JsonAdapterAnnotationTypeAdapterFactory
-      DEFAULT_JSON_ADAPTER_ANNOTATION_TYPE_ADAPTER_FACTORY =
-          new JsonAdapterAnnotationTypeAdapterFactory(DEFAULT_CONSTRUCTOR_CONSTRUCTOR);
-
-  /**
-   * Default instance of the builder, to be used only by the default {@link Gson#Gson()}
-   * constructor. Must not be used for anything else and must not be leaked to user code, since that
-   * could lead to accidental modification of this default builder.
-   */
-  static final GsonBuilder DEFAULT = new GsonBuilder();
-
-  static final List<TypeAdapterFactory> DEFAULT_TYPE_ADAPTER_FACTORIES =
-      GsonBuilder.DEFAULT.createFactories(
-          DEFAULT_CONSTRUCTOR_CONSTRUCTOR, DEFAULT_JSON_ADAPTER_ANNOTATION_TYPE_ADAPTER_FACTORY);
-
   private static final List<TypeAdapterFactoryProvider> BUILT_IN_FACTORY_PROVIDERS = new ArrayList<>();
 
   static {
     BUILT_IN_FACTORY_PROVIDERS.add(factories -> {
       factories.add(TypeAdapters.JSON_ELEMENT_FACTORY);
-      factories.add(ObjectTypeAdapter.getFactory(DEFAULT.objectToNumberStrategy));
+      factories.add(ObjectTypeAdapter.getFactory(ToNumberPolicy.DOUBLE));
     });
     BUILT_IN_FACTORY_PROVIDERS.add(factories -> {
-      factories.add(new CollectionTypeAdapterFactory(DEFAULT_CONSTRUCTOR_CONSTRUCTOR));
-      factories.add(new MapTypeAdapterFactory(DEFAULT_CONSTRUCTOR_CONSTRUCTOR, DEFAULT.complexMapKeySerialization));
-      factories.add(DEFAULT_JSON_ADAPTER_ANNOTATION_TYPE_ADAPTER_FACTORY);
+      ConstructorConstructor constructorConstructor = new ConstructorConstructor(
+          Collections.emptyMap(), DEFAULT_USE_JDK_UNSAFE, Collections.emptyList());
+      JsonAdapterAnnotationTypeAdapterFactory jsonAdapterFactory =
+          new JsonAdapterAnnotationTypeAdapterFactory(constructorConstructor);
+      factories.add(new CollectionTypeAdapterFactory(constructorConstructor));
+      factories.add(new MapTypeAdapterFactory(constructorConstructor, DEFAULT_COMPLEX_MAP_KEYS));
+      factories.add(jsonAdapterFactory);
       factories.add(TypeAdapters.ENUM_FACTORY);
     });
     BUILT_IN_FACTORY_PROVIDERS.add(factories -> {
+      ConstructorConstructor constructorConstructor = new ConstructorConstructor(
+          Collections.emptyMap(), DEFAULT_USE_JDK_UNSAFE, Collections.emptyList());
+      JsonAdapterAnnotationTypeAdapterFactory jsonAdapterFactory =
+          new JsonAdapterAnnotationTypeAdapterFactory(constructorConstructor);
       factories.add(new ReflectiveTypeAdapterFactory(
-          DEFAULT_CONSTRUCTOR_CONSTRUCTOR,
-          DEFAULT.fieldNamingPolicy,
+          constructorConstructor,
+          DEFAULT_FIELD_NAMING_STRATEGY,
           Excluder.DEFAULT,
-          DEFAULT_JSON_ADAPTER_ANNOTATION_TYPE_ADAPTER_FACTORY,
+          jsonAdapterFactory,
           Collections.emptyList()));
     });
   }

```
