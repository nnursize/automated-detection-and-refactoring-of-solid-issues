# Refactor SRP-005 (SRP): The GsonBuilder class manages an excessive number of diverse configuration op...

**Status:** `patch_failed`  
**Branch:** `refactor/SRP-005` -> `main`  
**Head commit:** `cf52d3b9a5ea63893866f818757d67a215f63462`  
**LLM finish:** `FinishReason.STOP` (prompt 14192, completion 8193)  

## Detected issue

- **File**: `gson/src/main/java/com/google/gson/GsonBuilder.java`
- **Entity**: `GsonBuilder` (class)
- **Lines (at detection time)**: L45–L485
- **Severity**: high
- **Confidence**: detected by 2 scan(s)

**Description.** The GsonBuilder class manages an excessive number of diverse configuration options and complex factory creation logic for building a Gson instance.

**Reasoning.** This class exhibits the God Class smell. It aggregates an extensive set of configuration parameters, including exclusion strategies, field naming policies, instance creators, multiple lists of TypeAdapterFactories, null serialization, date formats, map key serialization, floating point handling, HTML escaping, non-executable JSON generation, strictness, JDK Unsafe usage, and reflection access filters. The `createFactories` method (lines 370-450) is particularly complex, orchestrating the assembly of numerous internal TypeAdapterFactory instances based on these diverse settings. This wide range of responsibilities means the class has many independent reasons to change, such as adding a new exclusion mechanism, modifying date format options, or introducing new number handling strategies, violating SRP.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 31
- **Files created** (1): `gson/src/main/java/com/google/gson/GsonConfiguration.java`
- **Files modified** (1): `gson/src/main/java/com/google/gson/GsonBuilder.java`

**Summary.** Extract Gson configuration state into a dedicated GsonConfiguration class

**Rationale.** The GsonBuilder class was acting as a God Object, managing both the builder API and the internal state of the Gson configuration. By extracting the configuration state into a separate class, we separate the responsibility of 'building' from the responsibility of 'holding configuration state', adhering to the Single Responsibility Principle.

## Changes overview

_31 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `gson/src/main/java/com/google/gson/GsonBuilder.java` (23-line block → 1-line replacement)

**Replaces:**

```java
  Excluder excluder = Excluder.DEFAULT;
  LongSerializationPolicy longSerializationPolicy = LongSerializationPolicy.DEFAULT;
  FieldNamingStrategy fieldNamingPolicy = DEFAULT_FIELD_NAMING_STRATEGY;
  final Map<Type, InstanceCreator<?>> instanceCreators = new HashMap<>();
  final List<TypeAdapterFactory> factories = new ArrayList<>();

  /** tree-style hierarchy factories. These come after factories for backwards compatibility. */
  final List<TypeAdapterFactory> hierarchyFactories = new ArrayList<>();

  boolean serializeNulls = DEFAULT_SERIALIZE_NULLS;
  String datePattern = DEFAULT_DATE_PATTERN;
  int dateStyle = DateFormat.DEFAULT;
  int timeStyle = DateFormat.DEFAULT;
  boolean complexMapKeySerialization = DEFAULT_COMPLEX_MAP_KEYS;
  boolean serializeSpecialFloatingPointValues = DEFAULT_SPECIALIZE_FLOAT_VALUES;
  boolean escapeHtmlChars = DEFAULT_ESCAPE_HTML;
  FormattingStyle formattingStyle = DEFAULT_FORMATTING_STYLE;
  boolean generateNonExecutableJson = DEFAULT_JSON_NON_EXECUTABLE;
  Strictness strictness = DEFAULT_STRICTNESS;
  boolean useJdkUnsafe = DEFAULT_USE_JDK_UNSAFE;
  ToNumberStrategy objectToNumberStrategy = DEFAULT_OBJECT_TO_NUMBER_STRATEGY;
  ToNumberStrategy numberToNumberStrategy = DEFAULT_NUMBER_TO_NUMBER_STRATEGY;
  final ArrayDeque<ReflectionAccessFilter> reflectionFilters = new ArrayDeque<>();
```

**With:**

```java
  final GsonConfiguration config = new GsonConfiguration();
```

### 2. EDIT `gson/src/main/java/com/google/gson/GsonBuilder.java` (22-line block → 22-line replacement)

**Replaces:**

```java
  GsonBuilder(Gson gson) {
    this.excluder = gson.excluder;
    this.fieldNamingPolicy = gson.fieldNamingStrategy;
    this.instanceCreators.putAll(gson.instanceCreators);
    this.serializeNulls = gson.serializeNulls;
    this.complexMapKeySerialization = gson.complexMapKeySerialization;
    this.generateNonExecutableJson = gson.generateNonExecutableJson;
    this.escapeHtmlChars = gson.htmlSafe;
    this.formattingStyle = gson.formattingStyle;
    this.strictness = gson.strictness;
    this.serializeSpecialFloatingPointValues = gson.serializeSpecialFloatingPointValues;
    this.longSerializationPolicy = gson.longSerializationPolicy;
    this.datePattern = gson.datePattern;
    this.dateStyle = gson.dateStyle;
    this.timeStyle = gson.timeStyle;
    this.factories.addAll(gson.builderFactories);
    this.hierarchyFactories.addAll(gson.builderHierarchyFactories);
    this.useJdkUnsafe = gson.useJdkUnsafe;
    this.objectToNumberStrategy = gson.objectToNumberStrategy;
    this.numberToNumberStrategy = gson.numberToNumberStrategy;
    this.reflectionFilters.addAll(gson.reflectionFilters);
  }
```

**With:**

```java
  GsonBuilder(Gson gson) {
    this.config.excluder = gson.excluder;
    this.config.fieldNamingPolicy = gson.fieldNamingStrategy;
    this.config.instanceCreators.putAll(gson.instanceCreators);
    this.config.serializeNulls = gson.serializeNulls;
    this.config.complexMapKeySerialization = gson.complexMapKeySerialization;
    this.config.generateNonExecutableJson = gson.generateNonExecutableJson;
    this.config.escapeHtmlChars = gson.htmlSafe;
    this.config.formattingStyle = gson.formattingStyle;
    this.config.strictness = gson.strictness;
    this.config.serializeSpecialFloatingPointValues = gson.serializeSpecialFloatingPointValues;
    this.config.longSerializationPolicy = gson.longSerializationPolicy;
    this.config.datePattern = gson.datePattern;
    this.config.dateStyle = gson.dateStyle;
    this.config.timeStyle = gson.timeStyle;
    this.config.factories.addAll(gson.builderFactories);
    this.config.hierarchyFactories.addAll(gson.builderHierarchyFactories);
    this.config.useJdkUnsafe = gson.useJdkUnsafe;
    this.config.objectToNumberStrategy = gson.objectToNumberStrategy;
    this.config.numberToNumberStrategy = gson.numberToNumberStrategy;
    this.config.reflectionFilters.addAll(gson.reflectionFilters);
  }
```

### 3. EDIT `gson/src/main/java/com/google/gson/GsonBuilder.java` (7-line block → 7-line replacement)

**Replaces:**

```java
  public GsonBuilder setVersion(double version) {
    if (Double.isNaN(version) || version < 0.0) {
      throw new IllegalArgumentException("Invalid version: " + version);
    }
    excluder = excluder.withVersion(version);
    return this;
  }
```

**With:**

```java
  public GsonBuilder setVersion(double version) {
    if (Double.isNaN(version) || version < 0.0) {
      throw new IllegalArgumentException("Invalid version: " + version);
    }
    config.excluder = config.excluder.withVersion(version);
    return this;
  }
```

### 4. EDIT `gson/src/main/java/com/google/gson/GsonBuilder.java` (5-line block → 5-line replacement)

**Replaces:**

```java
  public GsonBuilder excludeFieldsWithModifiers(int... modifiers) {
    Objects.requireNonNull(modifiers);
    excluder = excluder.withModifiers(modifiers);
    return this;
  }
```

**With:**

```java
  public GsonBuilder excludeFieldsWithModifiers(int... modifiers) {
    Objects.requireNonNull(modifiers);
    config.excluder = config.excluder.withModifiers(modifiers);
    return this;
  }
```

### 5. EDIT `gson/src/main/java/com/google/gson/GsonBuilder.java` (4-line block → 4-line replacement)

**Replaces:**

```java
  public GsonBuilder generateNonExecutableJson() {
    this.generateNonExecutableJson = true;
    return this;
  }
```

**With:**

```java
  public GsonBuilder generateNonExecutableJson() {
    this.config.generateNonExecutableJson = true;
    return this;
  }
```

### 6. EDIT `gson/src/main/java/com/google/gson/GsonBuilder.java` (4-line block → 4-line replacement)

**Replaces:**

```java
  public GsonBuilder excludeFieldsWithoutExposeAnnotation() {
    excluder = excluder.excludeFieldsWithoutExposeAnnotation();
    return this;
  }
```

**With:**

```java
  public GsonBuilder excludeFieldsWithoutExposeAnnotation() {
    config.excluder = config.excluder.excludeFieldsWithoutExposeAnnotation();
    return this;
  }
```

### 7. EDIT `gson/src/main/java/com/google/gson/GsonBuilder.java` (4-line block → 4-line replacement)

**Replaces:**

```java
  public GsonBuilder serializeNulls() {
    this.serializeNulls = true;
    return this;
  }
```

**With:**

```java
  public GsonBuilder serializeNulls() {
    this.config.serializeNulls = true;
    return this;
  }
```

### 8. EDIT `gson/src/main/java/com/google/gson/GsonBuilder.java` (4-line block → 4-line replacement)

**Replaces:**

```java
  public GsonBuilder enableComplexMapKeySerialization() {
    complexMapKeySerialization = true;
    return this;
  }
```

**With:**

```java
  public GsonBuilder enableComplexMapKeySerialization() {
    config.complexMapKeySerialization = true;
    return this;
  }
```

### 9. EDIT `gson/src/main/java/com/google/gson/GsonBuilder.java` (4-line block → 4-line replacement)

**Replaces:**

```java
  public GsonBuilder disableInnerClassSerialization() {
    excluder = excluder.disableInnerClassSerialization();
    return this;
  }
```

**With:**

```java
  public GsonBuilder disableInnerClassSerialization() {
    config.excluder = config.excluder.disableInnerClassSerialization();
    return this;
  }
```

### 10. EDIT `gson/src/main/java/com/google/gson/GsonBuilder.java` (4-line block → 4-line replacement)

**Replaces:**

```java
  public GsonBuilder setLongSerializationPolicy(LongSerializationPolicy serializationPolicy) {
    this.longSerializationPolicy = Objects.requireNonNull(serializationPolicy);
    return this;
  }
```

**With:**

```java
  public GsonBuilder setLongSerializationPolicy(LongSerializationPolicy serializationPolicy) {
    this.config.longSerializationPolicy = Objects.requireNonNull(serializationPolicy);
    return this;
  }
```

### 11. EDIT `gson/src/main/java/com/google/gson/GsonBuilder.java` (4-line block → 4-line replacement)

**Replaces:**

```java
  public GsonBuilder setFieldNamingStrategy(FieldNamingStrategy fieldNamingStrategy) {
    this.fieldNamingPolicy = Objects.requireNonNull(fieldNamingStrategy);
    return this;
  }
```

**With:**

```java
  public GsonBuilder setFieldNamingStrategy(FieldNamingStrategy fieldNamingStrategy) {
    this.config.fieldNamingPolicy = Objects.requireNonNull(fieldNamingStrategy);
    return this;
  }
```

### 12. EDIT `gson/src/main/java/com/google/gson/GsonBuilder.java` (4-line block → 4-line replacement)

**Replaces:**

```java
  public GsonBuilder setObjectToNumberStrategy(ToNumberStrategy objectToNumberStrategy) {
    this.objectToNumberStrategy = Objects.requireNonNull(objectToNumberStrategy);
    return this;
  }
```

**With:**

```java
  public GsonBuilder setObjectToNumberStrategy(ToNumberStrategy objectToNumberStrategy) {
    this.config.objectToNumberStrategy = Objects.requireNonNull(objectToNumberStrategy);
    return this;
  }
```

### 13. EDIT `gson/src/main/java/com/google/gson/GsonBuilder.java` (4-line block → 4-line replacement)

**Replaces:**

```java
  public GsonBuilder setNumberToNumberStrategy(ToNumberStrategy numberToNumberStrategy) {
    this.numberToNumberStrategy = Objects.requireNonNull(numberToNumberStrategy);
    return this;
  }
```

**With:**

```java
  public GsonBuilder setNumberToNumberStrategy(ToNumberStrategy numberToNumberStrategy) {
    this.config.numberToNumberStrategy = Objects.requireNonNull(numberToNumberStrategy);
    return this;
  }
```

### 14. EDIT `gson/src/main/java/com/google/gson/GsonBuilder.java` (7-line block → 7-line replacement)

**Replaces:**

```java
  public GsonBuilder setExclusionStrategies(ExclusionStrategy... strategies) {
    Objects.requireNonNull(strategies);
    for (ExclusionStrategy strategy : strategies) {
      excluder = excluder.withExclusionStrategy(strategy, true, true);
    }
    return this;
  }
```

**With:**

```java
  public GsonBuilder setExclusionStrategies(ExclusionStrategy... strategies) {
    Objects.requireNonNull(strategies);
    for (ExclusionStrategy strategy : strategies) {
      config.excluder = config.excluder.withExclusionStrategy(strategy, true, true);
    }
    return this;
  }
```

### 15. EDIT `gson/src/main/java/com/google/gson/GsonBuilder.java` (5-line block → 5-line replacement)

**Replaces:**

```java
  public GsonBuilder addSerializationExclusionStrategy(ExclusionStrategy strategy) {
    Objects.requireNonNull(strategy);
    excluder = excluder.withExclusionStrategy(strategy, true, false);
    return this;
  }
```

**With:**

```java
  public GsonBuilder addSerializationExclusionStrategy(ExclusionStrategy strategy) {
    Objects.requireNonNull(strategy);
    config.excluder = config.excluder.withExclusionStrategy(strategy, true, false);
    return this;
  }
```

### 16. EDIT `gson/src/main/java/com/google/gson/GsonBuilder.java` (5-line block → 5-line replacement)

**Replaces:**

```java
  public GsonBuilder addDeserializationExclusionStrategy(ExclusionStrategy strategy) {
    Objects.requireNonNull(strategy);
    excluder = excluder.withExclusionStrategy(strategy, false, true);
    return this;
  }
```

**With:**

```java
  public GsonBuilder addDeserializationExclusionStrategy(ExclusionStrategy strategy) {
    Objects.requireNonNull(strategy);
    config.excluder = config.excluder.withExclusionStrategy(strategy, false, true);
    return this;
  }
```

### 17. EDIT `gson/src/main/java/com/google/gson/GsonBuilder.java` (4-line block → 4-line replacement)

**Replaces:**

```java
  public GsonBuilder setFormattingStyle(FormattingStyle formattingStyle) {
    this.formattingStyle = Objects.requireNonNull(formattingStyle);
    return this;
  }
```

**With:**

```java
  public GsonBuilder setFormattingStyle(FormattingStyle formattingStyle) {
    this.config.formattingStyle = Objects.requireNonNull(formattingStyle);
    return this;
  }
```

### 18. EDIT `gson/src/main/java/com/google/gson/GsonBuilder.java` (4-line block → 4-line replacement)

**Replaces:**

```java
  public GsonBuilder setStrictness(Strictness strictness) {
    this.strictness = Objects.requireNonNull(strictness);
    return this;
  }
```

**With:**

```java
  public GsonBuilder setStrictness(Strictness strictness) {
    this.config.strictness = Objects.requireNonNull(strictness);
    return this;
  }
```

### 19. EDIT `gson/src/main/java/com/google/gson/GsonBuilder.java` (4-line block → 4-line replacement)

**Replaces:**

```java
  public GsonBuilder disableHtmlEscaping() {
    this.escapeHtmlChars = false;
    return this;
  }
```

**With:**

```java
  public GsonBuilder disableHtmlEscaping() {
    this.config.escapeHtmlChars = false;
    return this;
  }
```

### 20. EDIT `gson/src/main/java/com/google/gson/GsonBuilder.java` (12-line block → 12-line replacement)

**Replaces:**

```java
  public GsonBuilder setDateFormat(String pattern) {
    if (pattern != null) {
      try {
        new SimpleDateFormat(pattern);
      } catch (IllegalArgumentException e) {
        // Throw exception if it is an invalid date format
        throw new IllegalArgumentException("The date pattern '" + pattern + "' is not valid", e);
      }
    }
    this.datePattern = pattern;
    return this;
  }
```

**With:**

```java
  public GsonBuilder setDateFormat(String pattern) {
    if (pattern != null) {
      try {
        new SimpleDateFormat(pattern);
      } catch (IllegalArgumentException e) {
        // Throw exception if it is an invalid date format
        throw new IllegalArgumentException("The date pattern '" + pattern + "' is not valid", e);
      }
    }
    this.config.datePattern = pattern;
    return this;
  }
```

### 21. EDIT `gson/src/main/java/com/google/gson/GsonBuilder.java` (5-line block → 5-line replacement)

**Replaces:**

```java
  public GsonBuilder setDateFormat(int dateStyle) {
    this.dateStyle = checkDateFormatStyle(dateStyle);
    this.datePattern = null;
    return this;
  }
```

**With:**

```java
  public GsonBuilder setDateFormat(int dateStyle) {
    this.config.dateStyle = checkDateFormatStyle(dateStyle);
    this.config.datePattern = null;
    return this;
  }
```

### 22. EDIT `gson/src/main/java/com/google/gson/GsonBuilder.java` (6-line block → 6-line replacement)

**Replaces:**

```java
  public GsonBuilder setDateFormat(int dateStyle, int timeStyle) {
    this.dateStyle = checkDateFormatStyle(dateStyle);
    this.timeStyle = checkDateFormatStyle(timeStyle);
    this.datePattern = null;
    return this;
  }
```

**With:**

```java
  public GsonBuilder setDateFormat(int dateStyle, int timeStyle) {
    this.config.dateStyle = checkDateFormatStyle(dateStyle);
    this.config.timeStyle = checkDateFormatStyle(timeStyle);
    this.config.datePattern = null;
    return this;
  }
```

### 23. EDIT `gson/src/main/java/com/google/gson/GsonBuilder.java` (15-line block → 15-line replacement)

**Replaces:**

```java
    if (typeAdapter instanceof InstanceCreator<?>) {
      instanceCreators.put(type, (InstanceCreator<?>) typeAdapter);
    }
    if (typeAdapter instanceof JsonSerializer<?> || typeAdapter instanceof JsonDeserializer<?>) {
      TypeToken<?> typeToken = TypeToken.get(type);
      factories.add(TreeTypeAdapter.newFactoryWithMatchRawType(typeToken, typeAdapter));
    }
    if (typeAdapter instanceof TypeAdapter<?>) {
      @SuppressWarnings({"unchecked", "rawtypes"})
      TypeAdapterFactory factory =
          TypeAdapters.newFactory(TypeToken.get(type), (TypeAdapter) typeAdapter);
      factories.add(factory);
    }
    return this;
  }
```

**With:**

```java
    if (typeAdapter instanceof InstanceCreator<?>) {
      config.instanceCreators.put(type, (InstanceCreator<?>) typeAdapter);
    }
    if (typeAdapter instanceof JsonSerializer<?> || typeAdapter instanceof JsonDeserializer<?>) {
      TypeToken<?> typeToken = TypeToken.get(type);
      config.factories.add(TreeTypeAdapter.newFactoryWithMatchRawType(typeToken, typeAdapter));
    }
    if (typeAdapter instanceof TypeAdapter<?>) {
      @SuppressWarnings({"unchecked", "rawtypes"})
      TypeAdapterFactory factory =
          TypeAdapters.newFactory(TypeToken.get(type), (TypeAdapter) typeAdapter);
      config.factories.add(factory);
    }
    return this;
  }
```

### 24. EDIT `gson/src/main/java/com/google/gson/GsonBuilder.java` (5-line block → 5-line replacement)

**Replaces:**

```java
  public GsonBuilder registerTypeAdapterFactory(TypeAdapterFactory factory) {
    Objects.requireNonNull(factory);
    factories.add(factory);
    return this;
  }
```

**With:**

```java
  public GsonBuilder registerTypeAdapterFactory(TypeAdapterFactory factory) {
    Objects.requireNonNull(factory);
    config.factories.add(factory);
    return this;
  }
```

### 25. EDIT `gson/src/main/java/com/google/gson/GsonBuilder.java` (11-line block → 11-line replacement)

**Replaces:**

```java
    if (typeAdapter instanceof JsonDeserializer || typeAdapter instanceof JsonSerializer) {
      hierarchyFactories.add(TreeTypeAdapter.newTypeHierarchyFactory(baseType, typeAdapter));
    }
    if (typeAdapter instanceof TypeAdapter<?>) {
      @SuppressWarnings({"unchecked", "rawtypes"})
      TypeAdapterFactory factory =
          TypeAdapters.newTypeHierarchyFactory(baseType, (TypeAdapter) typeAdapter);
      factories.add(factory);
    }
    return this;
  }
```

**With:**

```java
    if (typeAdapter instanceof JsonDeserializer || typeAdapter instanceof JsonSerializer) {
      config.hierarchyFactories.add(TreeTypeAdapter.newTypeHierarchyFactory(baseType, typeAdapter));
    }
    if (typeAdapter instanceof TypeAdapter<?>) {
      @SuppressWarnings({"unchecked", "rawtypes"})
      TypeAdapterFactory factory =
          TypeAdapters.newTypeHierarchyFactory(baseType, (TypeAdapter) typeAdapter);
      config.factories.add(factory);
    }
    return this;
  }
```

### 26. EDIT `gson/src/main/java/com/google/gson/GsonBuilder.java` (4-line block → 4-line replacement)

**Replaces:**

```java
  public GsonBuilder serializeSpecialFloatingPointValues() {
    this.serializeSpecialFloatingPointValues = true;
    return this;
  }
```

**With:**

```java
  public GsonBuilder serializeSpecialFloatingPointValues() {
    this.config.serializeSpecialFloatingPointValues = true;
    return this;
  }
```

### 27. EDIT `gson/src/main/java/com/google/gson/GsonBuilder.java` (4-line block → 4-line replacement)

**Replaces:**

```java
  public GsonBuilder disableJdkUnsafe() {
    this.useJdkUnsafe = false;
    return this;
  }
```

**With:**

```java
  public GsonBuilder disableJdkUnsafe() {
    this.config.useJdkUnsafe = false;
    return this;
  }
```

### 28. EDIT `gson/src/main/java/com/google/gson/GsonBuilder.java` (5-line block → 5-line replacement)

**Replaces:**

```java
  public GsonBuilder addReflectionAccessFilter(ReflectionAccessFilter filter) {
    Objects.requireNonNull(filter);
    reflectionFilters.addFirst(filter);
    return this;
  }
```

**With:**

```java
  public GsonBuilder addReflectionAccessFilter(ReflectionAccessFilter filter) {
    Objects.requireNonNull(filter);
    config.reflectionFilters.addFirst(filter);
    return this;
  }
```

### 29. EDIT `gson/src/main/java/com/google/gson/GsonBuilder.java` (78-line block → 78-line replacement)

**Replaces:**

```java
  List<TypeAdapterFactory> createFactories(
      ConstructorConstructor constructorConstructor,
      JsonAdapterAnnotationTypeAdapterFactory jsonAdapterFactory) {
    ArrayList<TypeAdapterFactory> factories = new ArrayList<>();

    // built-in type adapters that cannot be overridden
    factories.add(TypeAdapters.JSON_ELEMENT_FACTORY);
    factories.add(ObjectTypeAdapter.getFactory(objectToNumberStrategy));

    // the excluder must precede all adapters that handle user-defined types
    factories.add(excluder);

    // users' type adapters
    addUserDefinedAdapters(factories);

    // custom Date adapters
    addDateTypeAdapters(factories);

    // type adapters for basic platform types
    factories.add(TypeAdapters.STRING_FACTORY);
    factories.add(TypeAdapters.INTEGER_FACTORY);
    factories.add(TypeAdapters.BOOLEAN_FACTORY);
    factories.add(TypeAdapters.BYTE_FACTORY);
    factories.add(TypeAdapters.SHORT_FACTORY);
    TypeAdapter<Number> longAdapter = longSerializationPolicy.typeAdapter();
    factories.add(TypeAdapters.newFactory(long.class, Long.class, longAdapter));
    factories.add(TypeAdapters.newFactory(double.class, Double.class, doubleAdapter()));
    factories.add(TypeAdapters.newFactory(float.class, Float.class, floatAdapter()));
    factories.add(NumberTypeAdapter.getFactory(numberToNumberStrategy));
    factories.add(TypeAdapters.ATOMIC_INTEGER_FACTORY);
    factories.add(TypeAdapters.ATOMIC_BOOLEAN_FACTORY);
    factories.add(
        TypeAdapters.newFactory(AtomicLong.class, TypeAdapters.atomicLongAdapter(longAdapter)));
    factories.add(
        TypeAdapters.newFactory(
            AtomicLongArray.class, TypeAdapters.atomicLongArrayAdapter(longAdapter)));
    factories.add(TypeAdapters.ATOMIC_INTEGER_ARRAY_FACTORY);
    factories.add(TypeAdapters.CHARACTER_FACTORY);
    factories.add(TypeAdapters.STRING_BUILDER_FACTORY);
    factories.add(TypeAdapters.STRING_BUFFER_FACTORY);
    factories.add(TypeAdapters.BIG_DECIMAL_FACTORY);
    factories.add(TypeAdapters.BIG_INTEGER_FACTORY);
    // Add adapter for LazilyParsedNumber because user can obtain it from Gson and then try to
    // serialize it again
    factories.add(TypeAdapters.LAZILY_PARSED_NUMBER_FACTORY);
    factories.add(TypeAdapters.URL_FACTORY);
    factories.add(TypeAdapters.URI_FACTORY);
    factories.add(TypeAdapters.UUID_FACTORY);
    factories.add(TypeAdapters.CURRENCY_FACTORY);
    factories.add(TypeAdapters.LOCALE_FACTORY);
    factories.add(TypeAdapters.INET_ADDRESS_FACTORY);
    factories.add(TypeAdapters.BIT_SET_FACTORY);
    factories.add(DefaultDateTypeAdapter.DEFAULT_STYLE_FACTORY);
    factories.add(TypeAdapters.CALENDAR_FACTORY);
    TypeAdapterFactory javaTimeFactory = TypeAdapters.javaTimeTypeAdapterFactory();
    if (javaTimeFactory != null) {
      factories.add(javaTimeFactory);
    }
    factories.addAll(SqlTypesSupport.SQL_TYPE_FACTORIES);
    factories.add(ArrayTypeAdapter.FACTORY);
... (18 more line(s) truncated)
```

**With:**

```java
  List<TypeAdapterFactory> createFactories(
      ConstructorConstructor constructorConstructor,
      JsonAdapterAnnotationTypeAdapterFactory jsonAdapterFactory) {
    ArrayList<TypeAdapterFactory> factories = new ArrayList<>();

    // built-in type adapters that cannot be overridden
    factories.add(TypeAdapters.JSON_ELEMENT_FACTORY);
    factories.add(ObjectTypeAdapter.getFactory(config.objectToNumberStrategy));

    // the excluder must precede all adapters that handle user-defined types
    factories.add(config.excluder);

    // users' type adapters
    addUserDefinedAdapters(factories);

    // custom Date adapters
    addDateTypeAdapters(factories);

    // type adapters for basic platform types
    factories.add(TypeAdapters.STRING_FACTORY);
    factories.add(TypeAdapters.INTEGER_FACTORY);
    factories.add(TypeAdapters.BOOLEAN_FACTORY);
    factories.add(TypeAdapters.BYTE_FACTORY);
    factories.add(TypeAdapters.SHORT_FACTORY);
    TypeAdapter<Number> longAdapter = config.longSerializationPolicy.typeAdapter();
    factories.add(TypeAdapters.newFactory(long.class, Long.class, longAdapter));
    factories.add(TypeAdapters.newFactory(double.class, Double.class, doubleAdapter()));
    factories.add(TypeAdapters.newFactory(float.class, Float.class, floatAdapter()));
    factories.add(NumberTypeAdapter.getFactory(config.numberToNumberStrategy));
    factories.add(TypeAdapters.ATOMIC_INTEGER_FACTORY);
    factories.add(TypeAdapters.ATOMIC_BOOLEAN_FACTORY);
    factories.add(
        TypeAdapters.newFactory(AtomicLong.class, TypeAdapters.atomicLongAdapter(longAdapter)));
    factories.add(
        TypeAdapters.newFactory(
            AtomicLongArray.class, TypeAdapters.atomicLongArrayAdapter(longAdapter)));
    factories.add(TypeAdapters.ATOMIC_INTEGER_ARRAY_FACTORY);
    factories.add(TypeAdapters.CHARACTER_FACTORY);
    factories.add(TypeAdapters.STRING_BUILDER_FACTORY);
    factories.add(TypeAdapters.STRING_BUFFER_FACTORY);
    factories.add(TypeAdapters.BIG_DECIMAL_FACTORY);
    factories.add(TypeAdapters.BIG_INTEGER_FACTORY);
    // Add adapter for LazilyParsedNumber because user can obtain it from Gson and then try to
    // serialize it again
    factories.add(TypeAdapters.LAZILY_PARSED_NUMBER_FACTORY);
    factories.add(TypeAdapters.URL_FACTORY);
    factories.add(TypeAdapters.URI_FACTORY);
    factories.add(TypeAdapters.UUID_FACTORY);
    factories.add(TypeAdapters.CURRENCY_FACTORY);
    factories.add(TypeAdapters.LOCALE_FACTORY);
    factories.add(TypeAdapters.INET_ADDRESS_FACTORY);
    factories.add(TypeAdapters.BIT_SET_FACTORY);
    factories.add(DefaultDateTypeAdapter.DEFAULT_STYLE_FACTORY);
    factories.add(TypeAdapters.CALENDAR_FACTORY);
    TypeAdapterFactory javaTimeFactory = TypeAdapters.javaTimeTypeAdapterFactory();
    if (javaTimeFactory != null) {
      factories.add(javaTimeFactory);
    }
    factories.addAll(SqlTypesSupport.SQL_TYPE_FACTORIES);
    factories.add(ArrayTypeAdapter.FACTORY);
... (18 more line(s) truncated)
```

### 30. EDIT `gson/src/main/java/com/google/gson/GsonBuilder.java` (49-line block → 49-line replacement)

**Replaces:**

```java
  private TypeAdapter<Number> doubleAdapter() {
    return serializeSpecialFloatingPointValues ? TypeAdapters.DOUBLE : TypeAdapters.DOUBLE_STRICT;
  }

  private TypeAdapter<Number> floatAdapter() {
    return serializeSpecialFloatingPointValues ? TypeAdapters.FLOAT : TypeAdapters.FLOAT_STRICT;
  }

  private void addUserDefinedAdapters(List<TypeAdapterFactory> all) {
    if (!this.factories.isEmpty()) {
      List<TypeAdapterFactory> reversedFactories = new ArrayList<>(this.factories);
      Collections.reverse(reversedFactories);
      all.addAll(reversedFactories);
    }

    if (!this.hierarchyFactories.isEmpty()) {
      List<TypeAdapterFactory> reversedHierarchyFactories =
          new ArrayList<>(this.hierarchyFactories);
      Collections.reverse(reversedHierarchyFactories);
      all.addAll(reversedHierarchyFactories);
    }
  }

  private void addDateTypeAdapters(List<TypeAdapterFactory> factories) {
    TypeAdapterFactory dateAdapterFactory;
    boolean sqlTypesSupported = SqlTypesSupport.SUPPORTS_SQL_TYPES;
    TypeAdapterFactory sqlTimestampAdapterFactory = null;
    TypeAdapterFactory sqlDateAdapterFactory = null;

    if (datePattern != null && !datePattern.trim().isEmpty()) {
      dateAdapterFactory = DefaultDateTypeAdapter.DateType.DATE.createAdapterFactory(datePattern);

      if (sqlTypesSupported) {
        sqlTimestampAdapterFactory =
            SqlTypesSupport.TIMESTAMP_DATE_TYPE.createAdapterFactory(datePattern);
        sqlDateAdapterFactory = SqlTypesSupport.DATE_DATE_TYPE.createAdapterFactory(datePattern);
      }
    } else if (dateStyle != DateFormat.DEFAULT || timeStyle != DateFormat.DEFAULT) {
      dateAdapterFactory =
          DefaultDateTypeAdapter.DateType.DATE.createAdapterFactory(dateStyle, timeStyle);

      if (sqlTypesSupported) {
        sqlTimestampAdapterFactory =
            SqlTypesSupport.TIMESTAMP_DATE_TYPE.createAdapterFactory(dateStyle, timeStyle);
        sqlDateAdapterFactory = SqlTypesSupport.DATE_DATE_TYPE.createAdapterFactory(dateStyle, timeStyle);
      }
    } else {
      return;
    }
```

**With:**

```java
  private TypeAdapter<Number> doubleAdapter() {
    return config.serializeSpecialFloatingPointValues ? TypeAdapters.DOUBLE : TypeAdapters.DOUBLE_STRICT;
  }

  private TypeAdapter<Number> floatAdapter() {
    return config.serializeSpecialFloatingPointValues ? TypeAdapters.FLOAT : TypeAdapters.FLOAT_STRICT;
  }

  private void addUserDefinedAdapters(List<TypeAdapterFactory> all) {
    if (!config.factories.isEmpty()) {
      List<TypeAdapterFactory> reversedFactories = new ArrayList<>(config.factories);
      Collections.reverse(reversedFactories);
      all.addAll(reversedFactories);
    }

    if (!config.hierarchyFactories.isEmpty()) {
      List<TypeAdapterFactory> reversedHierarchyFactories =
          new ArrayList<>(config.hierarchyFactories);
      Collections.reverse(reversedHierarchyFactories);
      all.addAll(reversedHierarchyFactories);
    }
  }

  private void addDateTypeAdapters(List<TypeAdapterFactory> factories) {
    TypeAdapterFactory dateAdapterFactory;
    boolean sqlTypesSupported = SqlTypesSupport.SUPPORTS_SQL_TYPES;
    TypeAdapterFactory sqlTimestampAdapterFactory = null;
    TypeAdapterFactory sqlDateAdapterFactory = null;

    if (config.datePattern != null && !config.datePattern.trim().isEmpty()) {
      dateAdapterFactory = DefaultDateTypeAdapter.DateType.DATE.createAdapterFactory(config.datePattern);

      if (sqlTypesSupported) {
        sqlTimestampAdapterFactory =
            SqlTypesSupport.TIMESTAMP_DATE_TYPE.createAdapterFactory(config.datePattern);
        sqlDateAdapterFactory = SqlTypesSupport.DATE_DATE_TYPE.createAdapterFactory(config.datePattern);
      }
    } else if (config.dateStyle != DateFormat.DEFAULT || config.timeStyle != DateFormat.DEFAULT) {
      dateAdapterFactory =
          DefaultDateTypeAdapter.DateType.DATE.createAdapterFactory(config.dateStyle, config.timeStyle);

      if (sqlTypesSupported) {
        sqlTimestampAdapterFactory =
            SqlTypesSupport.TIMESTAMP_DATE_TYPE.createAdapterFactory(config.dateStyle, config.timeStyle);
        sqlDateAdapterFactory = SqlTypesSupport.DATE_DATE_TYPE.createAdapterFactory(config.dateStyle, config.timeStyle);
      }
    } else {
      return;
    }
```

### 31. CREATE `gson/src/main/java/com/google/gson/GsonConfiguration.java` (36 line(s))

```java
package com.google.gson;

import com.google.gson.internal.Excluder;
import java.text.DateFormat;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Holds the configuration state for a {@link Gson} instance.
 */
class GsonConfiguration {
  Excluder excluder = Excluder.DEFAULT;
  LongSerializationPolicy longSerializationPolicy = LongSerializationPolicy.DEFAULT;
  FieldNamingStrategy fieldNamingPolicy = FieldNamingPolicy.IDENTITY;
  final Map<java.lang.reflect.Type, InstanceCreator<?>> instanceCreators = new HashMap<>();
  final List<TypeAdapterFactory> factories = new ArrayList<>();
  final List<TypeAdapterFactory> hierarchyFactories = new ArrayList<>();

  boolean serializeNulls = false;
  String datePattern = null;
  int dateStyle = DateFormat.DEFAULT;
  int timeStyle = DateFormat.DEFAULT;
  boolean complexMapKeySerialization = false;
  boolean serializeSpecialFloatingPointValues = false;
  boolean escapeHtmlChars = true;
  FormattingStyle formattingStyle = FormattingStyle.COMPACT;
  boolean generateNonExecutableJson = false;
  Strictness strictness = null;
  boolean useJdkUnsafe = true;
  ToNumberStrategy objectToNumberStrategy = ToNumberPolicy.DOUBLE;
  ToNumberStrategy numberToNumberStrategy = ToNumberPolicy.LAZILY_PARSED_NUMBER;
  final ArrayDeque<ReflectionAccessFilter> reflectionFilters = new ArrayDeque<>();
}
```

## Apply error

```
search_text not found in gson/src/main/java/com/google/gson/GsonBuilder.java (block 29)
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `gson/src/main/java/com/google/gson/GsonBuilder.java` | 995 → - | 37 → - | 4.38 → - | 126 → - | 0 → - |

## Diff

*(no diff — patch was not applied)*
