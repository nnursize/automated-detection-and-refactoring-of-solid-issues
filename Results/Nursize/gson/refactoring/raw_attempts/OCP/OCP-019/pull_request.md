# Refactor OCP-019 (OCP): Hardcoded list of built-in TypeAdapterFactories violates OCP.

**Status:** `applied_unverified`  
**Branch:** `refactor/OCP-019` -> `main`  
**Head commit:** `21b80c980a1afe6992adfb66be8905cb326980f4`  
**LLM finish:** `FinishReason.STOP` (prompt 14107, completion 2704)  

## Detected issue

- **File**: `gson/src/main/java/com/google/gson/GsonBuilder.java`
- **Entity**: `GsonBuilder.createFactories` (method)
- **Lines (at detection time)**: L444–L506
- **Severity**: high
- **Confidence**: detected by 4 scan(s)

**Description.** Hardcoded list of built-in TypeAdapterFactories violates OCP.

**Reasoning.** The `createFactories()` method explicitly adds a long, ordered list of built-in `TypeAdapterFactory` instances. Any new fundamental type adapter or change in the default serialization behavior for core types would require modifying this method to add or reorder factories, making it closed for extension.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files created** (1): `gson/src/main/java/com/google/gson/internal/bind/BuiltInTypeAdapterFactories.java`

**Summary.** Extract built-in TypeAdapterFactories into a registry to satisfy OCP

**Rationale.** The hardcoded list of factories in GsonBuilder.createFactories violates OCP. By moving the registration of built-in factories to a dedicated class (BuiltInTypeAdapterFactories), we allow the list to be managed independently of the builder's logic, making it easier to extend without modifying the builder itself.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. CREATE `gson/src/main/java/com/google/gson/internal/bind/BuiltInTypeAdapterFactories.java` (74 line(s))

```java
package com.google.gson.internal.bind;

import com.google.gson.TypeAdapterFactory;
import com.google.gson.internal.ConstructorConstructor;
import com.google.gson.internal.Excluder;
import com.google.gson.internal.sql.SqlTypesSupport;
import com.google.gson.ToNumberStrategy;
import com.google.gson.TypeAdapter;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.atomic.AtomicLongArray;

public final class BuiltInTypeAdapterFactories {
  private BuiltInTypeAdapterFactories() {}

  public static List<TypeAdapterFactory> getFactories(
      ConstructorConstructor constructorConstructor,
      Excluder excluder,
      ToNumberStrategy objectToNumberStrategy,
      ToNumberStrategy numberToNumberStrategy,
      TypeAdapter<Number> longAdapter,
      TypeAdapter<Number> doubleAdapter,
      TypeAdapter<Number> floatAdapter,
      boolean complexMapKeySerialization,
      JsonAdapterAnnotationTypeAdapterFactory jsonAdapterFactory) {
    List<TypeAdapterFactory> factories = new ArrayList<>();
    factories.add(TypeAdapters.JSON_ELEMENT_FACTORY);
    factories.add(ObjectTypeAdapter.getFactory(objectToNumberStrategy));
    factories.add(excluder);
    factories.add(new CollectionTypeAdapterFactory(constructorConstructor));
    factories.add(new MapTypeAdapterFactory(constructorConstructor, complexMapKeySerialization));
    factories.add(jsonAdapterFactory);
    factories.add(TypeAdapters.ENUM_FACTORY);
    
    factories.add(TypeAdapters.STRING_FACTORY);
    factories.add(TypeAdapters.INTEGER_FACTORY);
    factories.add(TypeAdapters.BOOLEAN_FACTORY);
    factories.add(TypeAdapters.BYTE_FACTORY);
    factories.add(TypeAdapters.SHORT_FACTORY);
    factories.add(TypeAdapters.newFactory(long.class, Long.class, longAdapter));
    factories.add(TypeAdapters.newFactory(double.class, Double.class, doubleAdapter));
    factories.add(TypeAdapters.newFactory(float.class, Float.class, floatAdapter));
    factories.add(NumberTypeAdapter.getFactory(numberToNumberStrategy));
    factories.add(TypeAdapters.ATOMIC_INTEGER_FACTORY);
    factories.add(TypeAdapters.ATOMIC_BOOLEAN_FACTORY);
    factories.add(TypeAdapters.newFactory(AtomicLong.class, TypeAdapters.atomicLongAdapter(longAdapter)));
    factories.add(TypeAdapters.newFactory(AtomicLongArray.class, TypeAdapters.atomicLongArrayAdapter(longAdapter)));
    factories.add(TypeAdapters.ATOMIC_INTEGER_ARRAY_FACTORY);
    factories.add(TypeAdapters.CHARACTER_FACTORY);
    factories.add(TypeAdapters.STRING_BUILDER_FACTORY);
    factories.add(TypeAdapters.STRING_BUFFER_FACTORY);
    factories.add(TypeAdapters.BIG_DECIMAL_FACTORY);
    factories.add(TypeAdapters.BIG_INTEGER_FACTORY);
    factories.add(TypeAdapters.LAZILY_PARSED_NUMBER_FACTORY);
    factories.add(TypeAdapters.URL_FACTORY);
    factories.add(TypeAdapters.URI_FACTORY);
    factories.add(TypeAdapters.UUID_FACTORY);
    factories.add(TypeAdapters.CURRENCY_FACTORY);
    factories.add(TypeAdapters.LOCALE_FACTORY);
... (14 more line(s) truncated)
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `gson/src/main/java/com/google/gson/GsonBuilder.java` | 998 → - | 38 → - | 4.24 → - | 124 → - | 0 → - |
| `gson/src/main/java/com/google/gson/internal/bind/BuiltInTypeAdapterFactories.java` | - → 70 | - → 1 | - → 2 | - → 2 | - → 0 |

## Diff

```diff
diff --git a/gson/src/main/java/com/google/gson/internal/bind/BuiltInTypeAdapterFactories.java b/gson/src/main/java/com/google/gson/internal/bind/BuiltInTypeAdapterFactories.java
new file mode 100644
index 0000000..0000000
--- /dev/null
+++ b/gson/src/main/java/com/google/gson/internal/bind/BuiltInTypeAdapterFactories.java
@@ -0,0 +1,74 @@
+package com.google.gson.internal.bind;
+
+import com.google.gson.TypeAdapterFactory;
+import com.google.gson.internal.ConstructorConstructor;
+import com.google.gson.internal.Excluder;
+import com.google.gson.internal.sql.SqlTypesSupport;
+import com.google.gson.ToNumberStrategy;
+import com.google.gson.TypeAdapter;
+import java.util.ArrayList;
+import java.util.List;
+import java.util.concurrent.atomic.AtomicLong;
+import java.util.concurrent.atomic.AtomicLongArray;
+
+public final class BuiltInTypeAdapterFactories {
+  private BuiltInTypeAdapterFactories() {}
+
+  public static List<TypeAdapterFactory> getFactories(
+      ConstructorConstructor constructorConstructor,
+      Excluder excluder,
+      ToNumberStrategy objectToNumberStrategy,
+      ToNumberStrategy numberToNumberStrategy,
+      TypeAdapter<Number> longAdapter,
+      TypeAdapter<Number> doubleAdapter,
+      TypeAdapter<Number> floatAdapter,
+      boolean complexMapKeySerialization,
+      JsonAdapterAnnotationTypeAdapterFactory jsonAdapterFactory) {
+    List<TypeAdapterFactory> factories = new ArrayList<>();
+    factories.add(TypeAdapters.JSON_ELEMENT_FACTORY);
+    factories.add(ObjectTypeAdapter.getFactory(objectToNumberStrategy));
+    factories.add(excluder);
+    factories.add(new CollectionTypeAdapterFactory(constructorConstructor));
+    factories.add(new MapTypeAdapterFactory(constructorConstructor, complexMapKeySerialization));
+    factories.add(jsonAdapterFactory);
+    factories.add(TypeAdapters.ENUM_FACTORY);
+    
+    factories.add(TypeAdapters.STRING_FACTORY);
+    factories.add(TypeAdapters.INTEGER_FACTORY);
+    factories.add(TypeAdapters.BOOLEAN_FACTORY);
+    factories.add(TypeAdapters.BYTE_FACTORY);
+    factories.add(TypeAdapters.SHORT_FACTORY);
+    factories.add(TypeAdapters.newFactory(long.class, Long.class, longAdapter));
+    factories.add(TypeAdapters.newFactory(double.class, Double.class, doubleAdapter));
+    factories.add(TypeAdapters.newFactory(float.class, Float.class, floatAdapter));
+    factories.add(NumberTypeAdapter.getFactory(numberToNumberStrategy));
+    factories.add(TypeAdapters.ATOMIC_INTEGER_FACTORY);
+    factories.add(TypeAdapters.ATOMIC_BOOLEAN_FACTORY);
+    factories.add(TypeAdapters.newFactory(AtomicLong.class, TypeAdapters.atomicLongAdapter(longAdapter)));
+    factories.add(TypeAdapters.newFactory(AtomicLongArray.class, TypeAdapters.atomicLongArrayAdapter(longAdapter)));
+    factories.add(TypeAdapters.ATOMIC_INTEGER_ARRAY_FACTORY);
+    factories.add(TypeAdapters.CHARACTER_FACTORY);
+    factories.add(TypeAdapters.STRING_BUILDER_FACTORY);
+    factories.add(TypeAdapters.STRING_BUFFER_FACTORY);
+    factories.add(TypeAdapters.BIG_DECIMAL_FACTORY);
+    factories.add(TypeAdapters.BIG_INTEGER_FACTORY);
+    factories.add(TypeAdapters.LAZILY_PARSED_NUMBER_FACTORY);
+    factories.add(TypeAdapters.URL_FACTORY);
+    factories.add(TypeAdapters.URI_FACTORY);
+    factories.add(TypeAdapters.UUID_FACTORY);
+    factories.add(TypeAdapters.CURRENCY_FACTORY);
+    factories.add(TypeAdapters.LOCALE_FACTORY);
+    factories.add(TypeAdapters.INET_ADDRESS_FACTORY);
+    factories.add(TypeAdapters.BIT_SET_FACTORY);
+    factories.add(DefaultDateTypeAdapter.DEFAULT_STYLE_FACTORY);
+    factories.add(TypeAdapters.CALENDAR_FACTORY);
+    TypeAdapterFactory javaTimeFactory = TypeAdapters.javaTimeTypeAdapterFactory();
+    if (javaTimeFactory != null) {
+      factories.add(javaTimeFactory);
+    }
+    factories.addAll(SqlTypesSupport.SQL_TYPE_FACTORIES);
+    factories.add(ArrayTypeAdapter.FACTORY);
+    factories.add(TypeAdapters.CLASS_FACTORY);
+    return factories;
+  }
+}
\ No newline at end of file

```
