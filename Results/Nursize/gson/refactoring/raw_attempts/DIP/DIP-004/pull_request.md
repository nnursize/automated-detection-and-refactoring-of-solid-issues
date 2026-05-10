# Refactor DIP-004 (DIP): Factory directly instantiates concrete adapter implementations.

**Status:** `applied_unverified`  
**Branch:** `refactor/DIP-004` -> `main`  
**Head commit:** `d58fae43adf571e5356b24759685b816717995d8`  
**LLM finish:** `FinishReason.STOP` (prompt 7518, completion 932)  

## Detected issue

- **File**: `gson/src/main/java/com/google/gson/internal/bind/ReflectiveTypeAdapterFactory.java`
- **Entity**: `ReflectiveTypeAdapterFactory.create` (method)
- **Lines (at detection time)**: L121–L128
- **Severity**: medium
- **Confidence**: detected by 2 scan(s)

**Description.** Factory directly instantiates concrete adapter implementations.

**Reasoning.** The factory directly instantiates RecordAdapter and FieldReflectionAdapter. While factories are intended to create objects, DIP suggests that the logic should ideally depend on the TypeAdapter abstraction. Direct instantiation of these internal private classes couples the factory logic to specific implementation details of reflection-based adaptation.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 3
- **Files modified** (1): `gson/src/main/java/com/google/gson/internal/bind/ReflectiveTypeAdapterFactory.java`

**Summary.** Introduce a factory method for creating reflection-based adapters to decouple instantiation.

**Rationale.** The ReflectiveTypeAdapterFactory was directly instantiating concrete adapter implementations (RecordAdapter and FieldReflectionAdapter). By introducing a factory method (or simply keeping the logic encapsulated within the Adapter hierarchy), we reduce direct coupling to concrete implementations. Since these adapters are private inner classes, the most idiomatic way to adhere to DIP while maintaining encapsulation is to delegate the creation to a static factory method within the Adapter base class or the factory itself, effectively treating the Adapter as the abstraction.

## Changes overview

_3 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `gson/src/main/java/com/google/gson/internal/bind/ReflectiveTypeAdapterFactory.java` (14-line block → 12-line replacement)

**Replaces:**

```java
    if (ReflectionHelper.isRecord(raw)) {
      return (TypeAdapter<T>) new RecordAdapter<>(
          raw, getBoundFields(gson, type, raw, blockInaccessible, true), blockInaccessible);
    }

    // If the class is anonymous or a local class, we cannot reflectively instantiate it.
    // We return null to let other factories handle it or to let Gson skip it.
    if (raw.isAnonymousClass() || raw.isLocalClass()) {
      return null;
    }

    ObjectConstructor<T> constructor = constructorConstructor.get(type, true);
    return new FieldReflectionAdapter<>(
        constructor, getBoundFields(gson, type, raw, blockInaccessible, false));
```

**With:**

```java
    if (ReflectionHelper.isRecord(raw)) {
      return RecordAdapter.create(raw, getBoundFields(gson, type, raw, blockInaccessible, true), blockInaccessible);
    }

    // If the class is anonymous or a local class, we cannot reflectively instantiate it.
    // We return null to let other factories handle it or to let Gson skip it.
    if (raw.isAnonymousClass() || raw.isLocalClass()) {
      return null;
    }

    ObjectConstructor<T> constructor = constructorConstructor.get(type, true);
    return FieldReflectionAdapter.create(constructor, getBoundFields(gson, type, raw, blockInaccessible, false));
```

### 2. EDIT `gson/src/main/java/com/google/gson/internal/bind/ReflectiveTypeAdapterFactory.java` (9-line block → 13-line replacement)

**Replaces:**

```java
  private static final class FieldReflectionAdapter<T> extends Adapter<T, T> {
    private final ObjectConstructor<T> constructor;

    FieldReflectionAdapter(ObjectConstructor<T> constructor, FieldsData fieldsData) {
      super(fieldsData);
      this.constructor = constructor;
    }

    @Override
```

**With:**

```java
  private static final class FieldReflectionAdapter<T> extends Adapter<T, T> {
    private final ObjectConstructor<T> constructor;

    static <T> FieldReflectionAdapter<T> create(ObjectConstructor<T> constructor, FieldsData fieldsData) {
      return new FieldReflectionAdapter<>(constructor, fieldsData);
    }

    private FieldReflectionAdapter(ObjectConstructor<T> constructor, FieldsData fieldsData) {
      super(fieldsData);
      this.constructor = constructor;
    }

    @Override
```

### 3. EDIT `gson/src/main/java/com/google/gson/internal/bind/ReflectiveTypeAdapterFactory.java` (5-line block → 9-line replacement)

**Replaces:**

```java
    RecordAdapter(Class<T> raw, FieldsData fieldsData, boolean blockInaccessible) {
      super(fieldsData);
      constructor = ReflectionHelper.getCanonicalRecordConstructor(raw);

      if (blockInaccessible) {
```

**With:**

```java
    static <T> RecordAdapter<T> create(Class<T> raw, FieldsData fieldsData, boolean blockInaccessible) {
      return new RecordAdapter<>(raw, fieldsData, blockInaccessible);
    }

    private RecordAdapter(Class<T> raw, FieldsData fieldsData, boolean blockInaccessible) {
      super(fieldsData);
      constructor = ReflectionHelper.getCanonicalRecordConstructor(raw);

      if (blockInaccessible) {
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `gson/src/main/java/com/google/gson/internal/bind/ReflectiveTypeAdapterFactory.java` | 521 → 525 | 8 → 10 | 11.88 → 9.7 | 88 → 88 | 0 → 0 |

## Diff

```diff
diff --git a/gson/src/main/java/com/google/gson/internal/bind/ReflectiveTypeAdapterFactory.java b/gson/src/main/java/com/google/gson/internal/bind/ReflectiveTypeAdapterFactory.java
index 5979b7b..6d07f4d 100644
--- a/gson/src/main/java/com/google/gson/internal/bind/ReflectiveTypeAdapterFactory.java
+++ b/gson/src/main/java/com/google/gson/internal/bind/ReflectiveTypeAdapterFactory.java
@@ -113,8 +113,7 @@ public final class ReflectiveTypeAdapterFactory implements TypeAdapterFactory {
     boolean blockInaccessible = filterResult == FilterResult.BLOCK_INACCESSIBLE;
 
     if (ReflectionHelper.isRecord(raw)) {
-      return (TypeAdapter<T>) new RecordAdapter<>(
-          raw, getBoundFields(gson, type, raw, blockInaccessible, true), blockInaccessible);
+      return RecordAdapter.create(raw, getBoundFields(gson, type, raw, blockInaccessible, true), blockInaccessible);
     }
 
     // If the class is anonymous or a local class, we cannot reflectively instantiate it.
@@ -124,8 +123,7 @@ public final class ReflectiveTypeAdapterFactory implements TypeAdapterFactory {
     }
 
     ObjectConstructor<T> constructor = constructorConstructor.get(type, true);
-    return new FieldReflectionAdapter<>(
-        constructor, getBoundFields(gson, type, raw, blockInaccessible, false));
+    return FieldReflectionAdapter.create(constructor, getBoundFields(gson, type, raw, blockInaccessible, false));
   }
   }
 
@@ -507,7 +505,11 @@ public final class ReflectiveTypeAdapterFactory implements TypeAdapterFactory {
   private static final class FieldReflectionAdapter<T> extends Adapter<T, T> {
     private final ObjectConstructor<T> constructor;
 
-    FieldReflectionAdapter(ObjectConstructor<T> constructor, FieldsData fieldsData) {
+    static <T> FieldReflectionAdapter<T> create(ObjectConstructor<T> constructor, FieldsData fieldsData) {
+      return new FieldReflectionAdapter<>(constructor, fieldsData);
+    }
+
+    private FieldReflectionAdapter(ObjectConstructor<T> constructor, FieldsData fieldsData) {
       super(fieldsData);
       this.constructor = constructor;
     }
@@ -539,7 +541,11 @@ public final class ReflectiveTypeAdapterFactory implements TypeAdapterFactory {
     // Map from component names to index into the constructors arguments.
     private final Map<String, Integer> componentIndices = new HashMap<>();
 
-    RecordAdapter(Class<T> raw, FieldsData fieldsData, boolean blockInaccessible) {
+    static <T> RecordAdapter<T> create(Class<T> raw, FieldsData fieldsData, boolean blockInaccessible) {
+      return new RecordAdapter<>(raw, fieldsData, blockInaccessible);
+    }
+
+    private RecordAdapter(Class<T> raw, FieldsData fieldsData, boolean blockInaccessible) {
       super(fieldsData);
       constructor = ReflectionHelper.getCanonicalRecordConstructor(raw);
 

```
