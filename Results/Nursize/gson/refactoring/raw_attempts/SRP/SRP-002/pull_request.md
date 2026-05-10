# Refactor SRP-002 (SRP): The createFactories method is a 'God method' that orchestrates the creation a...

**Status:** `applied_unverified`  
**Branch:** `refactor/SRP-002` -> `main`  
**Head commit:** `49ec2cb266d0dbaf0c01f92a24779d77753809d2`  
**LLM finish:** `FinishReason.STOP` (prompt 14154, completion 1534)  

## Detected issue

- **File**: `gson/src/main/java/com/google/gson/GsonBuilder.java`
- **Entity**: `GsonBuilder.createFactories` (method)
- **Lines (at detection time)**: L570–L639
- **Severity**: medium
- **Confidence**: detected by 2 scan(s)

**Description.** The createFactories method is a 'God method' that orchestrates the creation and ordering of a large number of TypeAdapterFactory instances.

**Reasoning.** This method is responsible for assembling the entire list of TypeAdapterFactory instances, including built-in adapters, user-defined adapters, custom date adapters, and reflective adapters. It contains extensive knowledge about the dependencies and specific ordering requirements of all these factories. If a new built-in adapter is added, or the order changes, this method needs modification. This combines the responsibilities of discovering, ordering, and instantiating all available factories, which could be decomposed into more focused helper methods or a dedicated factory assembler.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 2
- **Files modified** (1): `gson/src/main/java/com/google/gson/GsonBuilder.java`

**Summary.** Decompose createFactories into smaller, focused methods to improve SRP

**Rationale.** The createFactories method was a 'God method' handling too many responsibilities. By extracting the registration of platform type adapters into a dedicated method, the orchestration logic is simplified and easier to maintain.

## Changes overview

_2 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `gson/src/main/java/com/google/gson/GsonBuilder.java` (43-line block → 1-line replacement)

**Replaces:**

```java
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
    factories.add(TypeAdapters.CLASS_FACTORY);
```

**With:**

```java
    addPlatformTypeAdapters(factories);
```

### 2. EDIT `gson/src/main/java/com/google/gson/GsonBuilder.java` (1-line block → 44-line replacement)

**Replaces:**

```java
  private void addDateTypeAdapters(List<TypeAdapterFactory> factories) {
```

**With:**

```java
  private void addPlatformTypeAdapters(List<TypeAdapterFactory> factories) {
    TypeAdapter<Number> longAdapter = longSerializationPolicy.typeAdapter();
    factories.add(TypeAdapters.STRING_FACTORY);
    factories.add(TypeAdapters.INTEGER_FACTORY);
    factories.add(TypeAdapters.BOOLEAN_FACTORY);
    factories.add(TypeAdapters.BYTE_FACTORY);
    factories.add(TypeAdapters.SHORT_FACTORY);
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
    factories.add(TypeAdapters.CLASS_FACTORY);
  }

  private void addDateTypeAdapters(List<TypeAdapterFactory> factories) {
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `gson/src/main/java/com/google/gson/GsonBuilder.java` | 995 → 998 | 37 → 38 | 4.38 → 4.24 | 126 → 124 | 0 → 0 |

## Diff

```diff
diff --git a/gson/src/main/java/com/google/gson/GsonBuilder.java b/gson/src/main/java/com/google/gson/GsonBuilder.java
index 1cd29f9..6e411f6 100644
--- a/gson/src/main/java/com/google/gson/GsonBuilder.java
+++ b/gson/src/main/java/com/google/gson/GsonBuilder.java
@@ -940,49 +940,7 @@ public final class GsonBuilder {
     // custom Date adapters
     addDateTypeAdapters(factories);
 
-    // type adapters for basic platform types
-    factories.add(TypeAdapters.STRING_FACTORY);
-    factories.add(TypeAdapters.INTEGER_FACTORY);
-    factories.add(TypeAdapters.BOOLEAN_FACTORY);
-    factories.add(TypeAdapters.BYTE_FACTORY);
-    factories.add(TypeAdapters.SHORT_FACTORY);
-    TypeAdapter<Number> longAdapter = longSerializationPolicy.typeAdapter();
-    factories.add(TypeAdapters.newFactory(long.class, Long.class, longAdapter));
-    factories.add(TypeAdapters.newFactory(double.class, Double.class, doubleAdapter()));
-    factories.add(TypeAdapters.newFactory(float.class, Float.class, floatAdapter()));
-    factories.add(NumberTypeAdapter.getFactory(numberToNumberStrategy));
-    factories.add(TypeAdapters.ATOMIC_INTEGER_FACTORY);
-    factories.add(TypeAdapters.ATOMIC_BOOLEAN_FACTORY);
-    factories.add(
-        TypeAdapters.newFactory(AtomicLong.class, TypeAdapters.atomicLongAdapter(longAdapter)));
-    factories.add(
-        TypeAdapters.newFactory(
-            AtomicLongArray.class, TypeAdapters.atomicLongArrayAdapter(longAdapter)));
-    factories.add(TypeAdapters.ATOMIC_INTEGER_ARRAY_FACTORY);
-    factories.add(TypeAdapters.CHARACTER_FACTORY);
-    factories.add(TypeAdapters.STRING_BUILDER_FACTORY);
-    factories.add(TypeAdapters.STRING_BUFFER_FACTORY);
-    factories.add(TypeAdapters.BIG_DECIMAL_FACTORY);
-    factories.add(TypeAdapters.BIG_INTEGER_FACTORY);
-    // Add adapter for LazilyParsedNumber because user can obtain it from Gson and then try to
-    // serialize it again
-    factories.add(TypeAdapters.LAZILY_PARSED_NUMBER_FACTORY);
-    factories.add(TypeAdapters.URL_FACTORY);
-    factories.add(TypeAdapters.URI_FACTORY);
-    factories.add(TypeAdapters.UUID_FACTORY);
-    factories.add(TypeAdapters.CURRENCY_FACTORY);
-    factories.add(TypeAdapters.LOCALE_FACTORY);
-    factories.add(TypeAdapters.INET_ADDRESS_FACTORY);
-    factories.add(TypeAdapters.BIT_SET_FACTORY);
-    factories.add(DefaultDateTypeAdapter.DEFAULT_STYLE_FACTORY);
-    factories.add(TypeAdapters.CALENDAR_FACTORY);
-    TypeAdapterFactory javaTimeFactory = TypeAdapters.javaTimeTypeAdapterFactory();
-    if (javaTimeFactory != null) {
-      factories.add(javaTimeFactory);
-    }
-    factories.addAll(SqlTypesSupport.SQL_TYPE_FACTORIES);
-    factories.add(ArrayTypeAdapter.FACTORY);
-    factories.add(TypeAdapters.CLASS_FACTORY);
+    addPlatformTypeAdapters(factories);
 
     // type adapters for composite and user-defined types
     factories.add(new CollectionTypeAdapterFactory(constructorConstructor));
@@ -1039,6 +997,49 @@ public final class GsonBuilder {
     }
   }
 
+  private void addPlatformTypeAdapters(List<TypeAdapterFactory> factories) {
+    TypeAdapter<Number> longAdapter = longSerializationPolicy.typeAdapter();
+    factories.add(TypeAdapters.STRING_FACTORY);
+    factories.add(TypeAdapters.INTEGER_FACTORY);
+    factories.add(TypeAdapters.BOOLEAN_FACTORY);
+    factories.add(TypeAdapters.BYTE_FACTORY);
+    factories.add(TypeAdapters.SHORT_FACTORY);
+    factories.add(TypeAdapters.newFactory(long.class, Long.class, longAdapter));
+    factories.add(TypeAdapters.newFactory(double.class, Double.class, doubleAdapter()));
+    factories.add(TypeAdapters.newFactory(float.class, Float.class, floatAdapter()));
+    factories.add(NumberTypeAdapter.getFactory(numberToNumberStrategy));
+    factories.add(TypeAdapters.ATOMIC_INTEGER_FACTORY);
+    factories.add(TypeAdapters.ATOMIC_BOOLEAN_FACTORY);
+    factories.add(
+        TypeAdapters.newFactory(AtomicLong.class, TypeAdapters.atomicLongAdapter(longAdapter)));
+    factories.add(
+        TypeAdapters.newFactory(
+            AtomicLongArray.class, TypeAdapters.atomicLongArrayAdapter(longAdapter)));
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
+  }
+
   private void addDateTypeAdapters(List<TypeAdapterFactory> factories) {
     TypeAdapterFactory dateAdapterFactory;
     boolean sqlTypesSupported = SqlTypesSupport.SUPPORTS_SQL_TYPES;

```
