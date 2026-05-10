# Refactor DIP-001 (DIP): Gson directly instantiates internal implementation details.

**Status:** `patch_failed`  
**Branch:** `refactor/DIP-001` -> `main`  
**Head commit:** `29fb26dc6739abacd329814707753280ac11a2e7`  
**LLM finish:** `FinishReason.STOP` (prompt 17112, completion 1644)  

## Detected issue

- **File**: `gson/src/main/java/com/google/gson/Gson.java`
- **Entity**: `Gson.Gson` (method)
- **Lines (at detection time)**: L248–L255
- **Severity**: high
- **Confidence**: detected by 5 scan(s)

**Description.** Gson directly instantiates internal implementation details.

**Reasoning.** The high-level Gson facade directly instantiates ConstructorConstructor and JsonAdapterAnnotationTypeAdapterFactory using the 'new' keyword. This couples the high-level module to specific low-level implementation details rather than depending on abstractions or receiving these components via dependency injection.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 3
- **Files modified** (2): `gson/src/main/java/com/google/gson/Gson.java`, `gson/src/main/java/com/google/gson/GsonBuilder.java`

**Summary.** Refactor Gson constructor to use dependency injection for internal components

**Rationale.** The Gson class was directly instantiating ConstructorConstructor and JsonAdapterAnnotationTypeAdapterFactory. By moving this instantiation logic to the GsonBuilder (which is the factory for Gson), we decouple Gson from these specific implementations, adhering to the Dependency Inversion Principle.

## Changes overview

_3 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `gson/src/main/java/com/google/gson/Gson.java` (10-line block → 3-line replacement)

**Replaces:**

```java
    if (builder == GsonBuilder.DEFAULT) {
      this.constructorConstructor = GsonBuilder.DEFAULT_CONSTRUCTOR_CONSTRUCTOR;
      this.jsonAdapterFactory = GsonBuilder.DEFAULT_JSON_ADAPTER_ANNOTATION_TYPE_ADAPTER_FACTORY;
      this.factories = GsonBuilder.DEFAULT_TYPE_ADAPTER_FACTORIES;
    } else {
      this.constructorConstructor =
          new ConstructorConstructor(instanceCreators, useJdkUnsafe, reflectionFilters);
      this.jsonAdapterFactory = new JsonAdapterAnnotationTypeAdapterFactory(constructorConstructor);
      this.factories = builder.createFactories(constructorConstructor, jsonAdapterFactory);
    }
```

**With:**

```java
    this.constructorConstructor = builder.constructorConstructor;
    this.jsonAdapterFactory = builder.jsonAdapterFactory;
    this.factories = builder.factories;
```

### 2. EDIT `gson/src/main/java/com/google/gson/GsonBuilder.java` (26-line block → 32-line replacement)

**Replaces:**

```java
  private final List<ReflectionAccessFilter> reflectionFilters = new ArrayList<>();

  public GsonBuilder() {}

  GsonBuilder(Gson gson) {
    this.excluder = gson.excluder;
    this.fieldNamingPolicy = gson.fieldNamingStrategy;
    this.instanceCreators.putAll(gson.instanceCreators);
    this.complexMapKeySerialization = gson.complexMapKeySerialization;
    this.serializeNulls = gson.jsonWriterSettings.serializeNulls;
    this.generateNonExecutableJson = gson.jsonWriterSettings.generateNonExecutableJson;
    this.escapeHtmlChars = !gson.jsonWriterSettings.htmlSafe;
    this.formattingStyle = gson.jsonWriterSettings.formattingStyle;
    this.strictness = gson.jsonWriterSettings.strictness;
    this.serializeSpecialFloatingPointValues = gson.serializeSpecialFloatingPointValues;
    this.useJdkUnsafe = gson.useJdkUnsafe;
    this.longSerializationPolicy = gson.longSerializationPolicy;
    this.datePattern = gson.datePattern;
    this.dateStyle = gson.dateStyle;
    this.timeStyle = gson.timeStyle;
    this.factories.addAll(gson.builderFactories);
    this.hierarchyFactories.addAll(gson.builderHierarchyFactories);
    this.objectToNumberStrategy = gson.objectToNumberStrategy;
    this.numberToNumberStrategy = gson.numberToNumberStrategy;
    this.reflectionFilters.addAll(gson.reflectionFilters);
  }
```

**With:**

```java
  private final List<ReflectionAccessFilter> reflectionFilters = new ArrayList<>();

  ConstructorConstructor constructorConstructor;
  JsonAdapterAnnotationTypeAdapterFactory jsonAdapterFactory;
  List<TypeAdapterFactory> factories;

  public GsonBuilder() {}

  GsonBuilder(Gson gson) {
    this.excluder = gson.excluder;
    this.fieldNamingPolicy = gson.fieldNamingStrategy;
    this.instanceCreators.putAll(gson.instanceCreators);
    this.complexMapKeySerialization = gson.complexMapKeySerialization;
    this.serializeNulls = gson.jsonWriterSettings.serializeNulls;
    this.generateNonExecutableJson = gson.jsonWriterSettings.generateNonExecutableJson;
    this.escapeHtmlChars = !gson.jsonWriterSettings.htmlSafe;
    this.formattingStyle = gson.jsonWriterSettings.formattingStyle;
    this.strictness = gson.jsonWriterSettings.strictness;
    this.serializeSpecialFloatingPointValues = gson.serializeSpecialFloatingPointValues;
    this.useJdkUnsafe = gson.useJdkUnsafe;
    this.longSerializationPolicy = gson.longSerializationPolicy;
    this.datePattern = gson.datePattern;
    this.dateStyle = gson.dateStyle;
    this.timeStyle = gson.timeStyle;
    this.factories = new ArrayList<>(gson.builderFactories);
    this.hierarchyFactories = new ArrayList<>(gson.builderHierarchyFactories);
    this.objectToNumberStrategy = gson.objectToNumberStrategy;
    this.numberToNumberStrategy = gson.numberToNumberStrategy;
    this.reflectionFilters.addAll(gson.reflectionFilters);
    this.constructorConstructor = gson.constructorConstructor;
    this.jsonAdapterFactory = gson.jsonAdapterFactory;
  }
```

### 3. EDIT `gson/src/main/java/com/google/gson/GsonBuilder.java` (32-line block → 20-line replacement)

**Replaces:**

```java
  public Gson create() {
    List<TypeAdapterFactory> factories = new ArrayList<>(this.factories.size() + this.hierarchyFactories.size() + 3);
    factories.addAll(this.factories);
    Collections.reverse(factories);
    List<TypeAdapterFactory> hierarchyFactories = new ArrayList<>(this.hierarchyFactories);
    Collections.reverse(hierarchyFactories);
    factories.addAll(hierarchyFactories);
    addTypeAdaptersForDate(datePattern, dateStyle, timeStyle, factories);

    return new Gson(
        excluder,
        fieldNamingPolicy,
        new HashMap<>(instanceCreators),
        complexMapKeySerialization,
        serializeNulls,
        generateNonExecutableJson,
        escapeHtmlChars,
        formattingStyle,
        strictness,
        serializeSpecialFloatingPointValues,
        useJdkUnsafe,
        longSerializationPolicy,
        datePattern,
        dateStyle,
        timeStyle,
        new ArrayList<>(this.factories),
        new ArrayList<>(this.hierarchyFactories),
        factories,
        objectToNumberStrategy,
        numberToNumberStrategy,
        new ArrayList<>(reflectionFilters));
  }
```

**With:**

```java
  public Gson create() {
    List<TypeAdapterFactory> factories = new ArrayList<>(this.factories.size() + this.hierarchyFactories.size() + 3);
    factories.addAll(this.factories);
    Collections.reverse(factories);
    List<TypeAdapterFactory> hierarchyFactories = new ArrayList<>(this.hierarchyFactories);
    Collections.reverse(hierarchyFactories);
    factories.addAll(hierarchyFactories);
    addTypeAdaptersForDate(datePattern, dateStyle, timeStyle, factories);

    ConstructorConstructor constructorConstructor = new ConstructorConstructor(instanceCreators, useJdkUnsafe, reflectionFilters);
    JsonAdapterAnnotationTypeAdapterFactory jsonAdapterFactory = new JsonAdapterAnnotationTypeAdapterFactory(constructorConstructor);
    List<TypeAdapterFactory> finalFactories = createFactories(constructorConstructor, jsonAdapterFactory);

    GsonBuilder builder = new GsonBuilder(this);
    builder.constructorConstructor = constructorConstructor;
    builder.jsonAdapterFactory = jsonAdapterFactory;
    builder.factories = finalFactories;

    return new Gson(builder);
  }
```

## Apply error

```
search_text not found in gson/src/main/java/com/google/gson/GsonBuilder.java (block 1)
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `gson/src/main/java/com/google/gson/Gson.java` | 1181 → - | 38 → - | 7.21 → - | 237 → - | 0 → - |

## Diff

*(no diff — patch was not applied)*
