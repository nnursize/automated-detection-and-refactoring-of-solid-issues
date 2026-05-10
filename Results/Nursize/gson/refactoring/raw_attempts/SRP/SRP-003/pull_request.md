# Refactor SRP-003 (SRP): The Gson class is responsible for object serialization/deserialization, manag...

**Status:** `applied_unverified`  
**Branch:** `refactor/SRP-003` -> `main`  
**Head commit:** `cf52d3b9a5ea63893866f818757d67a215f63462`  
**LLM finish:** `FinishReason.STOP` (prompt 17112, completion 3320)  

## Detected issue

- **File**: `gson/src/main/java/com/google/gson/Gson.java`
- **Entity**: `Gson` (class)
- **Lines (at detection time)**: L48–L744
- **Severity**: medium
- **Confidence**: detected by 3 scan(s)

**Description.** The Gson class is responsible for object serialization/deserialization, managing a type adapter cache, and configuring JSON I/O streams.

**Reasoning.** The core responsibility of Gson is to coordinate object graph serialization and deserialization. However, it also directly holds and applies numerous configuration settings (e.g., `serializeNulls`, `htmlSafe`, `formattingStyle`, `strictness`) that dictate how the underlying `JsonReader` and `JsonWriter` instances are configured. This mixes the high-level object mapping responsibility with the more granular responsibility of configuring I/O stream behavior. A change in JSON formatting rules or parsing strictness requires modifying `Gson`, which is distinct from changes to its core object mapping logic.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 9
- **Files created** (1): `gson/src/main/java/com/google/gson/JsonWriterSettings.java`
- **Files modified** (1): `gson/src/main/java/com/google/gson/Gson.java`

**Summary.** Extract JSON I/O configuration into a dedicated JsonWriterSettings class

**Rationale.** The Gson class was violating SRP by managing both object mapping and low-level JSON I/O configuration. By extracting the configuration fields into a separate class, we separate the responsibility of defining how JSON should be written/read from the responsibility of orchestrating the serialization/deserialization process.

## Changes overview

_9 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `gson/src/main/java/com/google/gson/Gson.java` (6-line block → 2-line replacement)

**Replaces:**

```java
  final boolean serializeNulls;
  final boolean complexMapKeySerialization;
  final boolean generateNonExecutableJson;
  final boolean htmlSafe;
  final FormattingStyle formattingStyle;
  final Strictness strictness;
```

**With:**

```java
  final boolean complexMapKeySerialization;
  final JsonWriterSettings jsonWriterSettings;
```

### 2. EDIT `gson/src/main/java/com/google/gson/Gson.java` (6-line block → 8-line replacement)

**Replaces:**

```java
    this.serializeNulls = builder.serializeNulls;
    this.complexMapKeySerialization = builder.complexMapKeySerialization;
    this.generateNonExecutableJson = builder.generateNonExecutableJson;
    this.htmlSafe = builder.escapeHtmlChars;
    this.formattingStyle = builder.formattingStyle;
    this.strictness = builder.strictness;
```

**With:**

```java
    this.complexMapKeySerialization = builder.complexMapKeySerialization;
    this.jsonWriterSettings = new JsonWriterSettings(
        builder.serializeNulls,
        builder.generateNonExecutableJson,
        builder.escapeHtmlChars,
        builder.formattingStyle,
        builder.strictness
    );
```

### 3. EDIT `gson/src/main/java/com/google/gson/Gson.java` (13-line block → 13-line replacement)

**Replaces:**

```java
  public boolean serializeNulls() {
    return serializeNulls;
  }

  /**
   * Returns whether this Gson instance produces JSON output which is HTML-safe, that means all HTML
   * characters are escaped.
   *
   * @see GsonBuilder#disableHtmlEscaping()
   */
  public boolean htmlSafe() {
    return htmlSafe;
  }
```

**With:**

```java
  public boolean serializeNulls() {
    return jsonWriterSettings.serializeNulls;
  }

  /**
   * Returns whether this Gson instance produces JSON output which is HTML-safe, that means all HTML
   * characters are escaped.
   *
   * @see GsonBuilder#disableHtmlEscaping()
   */
  public boolean htmlSafe() {
    return jsonWriterSettings.htmlSafe;
  }
```

### 4. EDIT `gson/src/main/java/com/google/gson/Gson.java` (30-line block → 30-line replacement)

**Replaces:**

```java
  public void toJson(Object src, Type typeOfSrc, JsonWriter writer) throws JsonIOException {
    @SuppressWarnings("unchecked")
    TypeAdapter<Object> adapter = (TypeAdapter<Object>) getAdapter(TypeToken.get(typeOfSrc));

    Strictness oldStrictness = writer.getStrictness();
    if (this.strictness != null) {
      writer.setStrictness(this.strictness);
    } else if (writer.getStrictness() == Strictness.LEGACY_STRICT) {
      // For backward compatibility change to LENIENT if writer has default strictness LEGACY_STRICT
      writer.setStrictness(Strictness.LENIENT);
    }

    boolean oldHtmlSafe = writer.isHtmlSafe();
    boolean oldSerializeNulls = writer.getSerializeNulls();

    writer.setHtmlSafe(htmlSafe);
    writer.setSerializeNulls(serializeNulls);
    try {
      adapter.write(writer, src);
    } catch (IOException e) {
      throw new JsonIOException(e);
    } catch (AssertionError e) {
      throw new AssertionError(
          "AssertionError (GSON " + GsonBuildConfig.VERSION + "): " + e.getMessage(), e);
    } finally {
      writer.setStrictness(oldStrictness);
      writer.setHtmlSafe(oldHtmlSafe);
      writer.setSerializeNulls(oldSerializeNulls);
    }
  }
```

**With:**

```java
  public void toJson(Object src, Type typeOfSrc, JsonWriter writer) throws JsonIOException {
    @SuppressWarnings("unchecked")
    TypeAdapter<Object> adapter = (TypeAdapter<Object>) getAdapter(TypeToken.get(typeOfSrc));

    Strictness oldStrictness = writer.getStrictness();
    if (jsonWriterSettings.strictness != null) {
      writer.setStrictness(jsonWriterSettings.strictness);
    } else if (writer.getStrictness() == Strictness.LEGACY_STRICT) {
      // For backward compatibility change to LENIENT if writer has default strictness LEGACY_STRICT
      writer.setStrictness(Strictness.LENIENT);
    }

    boolean oldHtmlSafe = writer.isHtmlSafe();
    boolean oldSerializeNulls = writer.getSerializeNulls();

    writer.setHtmlSafe(jsonWriterSettings.htmlSafe);
    writer.setSerializeNulls(jsonWriterSettings.serializeNulls);
    try {
      adapter.write(writer, src);
    } catch (IOException e) {
      throw new JsonIOException(e);
    } catch (AssertionError e) {
      throw new AssertionError(
          "AssertionError (GSON " + GsonBuildConfig.VERSION + "): " + e.getMessage(), e);
    } finally {
      writer.setStrictness(oldStrictness);
      writer.setHtmlSafe(oldHtmlSafe);
      writer.setSerializeNulls(oldSerializeNulls);
    }
  }
```

### 5. EDIT `gson/src/main/java/com/google/gson/Gson.java` (28-line block → 28-line replacement)

**Replaces:**

```java
  public void toJson(JsonElement jsonElement, JsonWriter writer) throws JsonIOException {
    Strictness oldStrictness = writer.getStrictness();
    boolean oldHtmlSafe = writer.isHtmlSafe();
    boolean oldSerializeNulls = writer.getSerializeNulls();

    writer.setHtmlSafe(htmlSafe);
    writer.setSerializeNulls(serializeNulls);

    if (this.strictness != null) {
      writer.setStrictness(this.strictness);
    } else if (writer.getStrictness() == Strictness.LEGACY_STRICT) {
      // For backward compatibility change to LENIENT if writer has default strictness LEGACY_STRICT
      writer.setStrictness(Strictness.LENIENT);
    }

    try {
      Streams.write(jsonElement, writer);
    } catch (IOException e) {
      throw new JsonIOException(e);
    } catch (AssertionError e) {
      throw new AssertionError(
          "AssertionError (GSON " + GsonBuildConfig.VERSION + "): " + e.getMessage(), e);
    } finally {
      writer.setStrictness(oldStrictness);
      writer.setHtmlSafe(oldHtmlSafe);
      writer.setSerializeNulls(oldSerializeNulls);
    }
  }
```

**With:**

```java
  public void toJson(JsonElement jsonElement, JsonWriter writer) throws JsonIOException {
    Strictness oldStrictness = writer.getStrictness();
    boolean oldHtmlSafe = writer.isHtmlSafe();
    boolean oldSerializeNulls = writer.getSerializeNulls();

    writer.setHtmlSafe(jsonWriterSettings.htmlSafe);
    writer.setSerializeNulls(jsonWriterSettings.serializeNulls);

    if (jsonWriterSettings.strictness != null) {
      writer.setStrictness(jsonWriterSettings.strictness);
    } else if (writer.getStrictness() == Strictness.LEGACY_STRICT) {
      // For backward compatibility change to LENIENT if writer has default strictness LEGACY_STRICT
      writer.setStrictness(Strictness.LENIENT);
    }

    try {
      Streams.write(jsonElement, writer);
    } catch (IOException e) {
      throw new JsonIOException(e);
    } catch (AssertionError e) {
      throw new AssertionError(
          "AssertionError (GSON " + GsonBuildConfig.VERSION + "): " + e.getMessage(), e);
    } finally {
      writer.setStrictness(oldStrictness);
      writer.setHtmlSafe(oldHtmlSafe);
      writer.setSerializeNulls(oldSerializeNulls);
    }
  }
```

### 6. EDIT `gson/src/main/java/com/google/gson/Gson.java` (29-line block → 29-line replacement)

**Replaces:**

```java
  public JsonWriter newJsonWriter(Writer writer) throws IOException {
    if (generateNonExecutableJson) {
      writer.write(JSON_NON_EXECUTABLE_PREFIX);
    }
    JsonWriter jsonWriter = new JsonWriter(writer);
    jsonWriter.setFormattingStyle(formattingStyle);
    jsonWriter.setHtmlSafe(htmlSafe);
    jsonWriter.setStrictness(strictness == null ? Strictness.LEGACY_STRICT : strictness);
    jsonWriter.setSerializeNulls(serializeNulls);
    return jsonWriter;
  }

  /**
   * Returns a new JSON reader configured for the settings on this Gson instance.
   *
   * <p>The following settings are considered:
   *
   * <ul>
   *   <li>{@link GsonBuilder#setStrictness(Strictness)}. If no {@linkplain
   *       GsonBuilder#setStrictness(Strictness) explicit strictness has been set} the created
   *       reader will have a strictness of {@link Strictness#LEGACY_STRICT}. Otherwise, the
   *       strictness of the {@code Gson} instance will be used for the created reader.
   * </ul>
   */
  public JsonReader newJsonReader(Reader reader) {
    JsonReader jsonReader = new JsonReader(reader);
    jsonReader.setStrictness(strictness == null ? Strictness.LEGACY_STRICT : strictness);
    return jsonReader;
  }
```

**With:**

```java
  public JsonWriter newJsonWriter(Writer writer) throws IOException {
    if (jsonWriterSettings.generateNonExecutableJson) {
      writer.write(JSON_NON_EXECUTABLE_PREFIX);
    }
    JsonWriter jsonWriter = new JsonWriter(writer);
    jsonWriter.setFormattingStyle(jsonWriterSettings.formattingStyle);
    jsonWriter.setHtmlSafe(jsonWriterSettings.htmlSafe);
    jsonWriter.setStrictness(jsonWriterSettings.strictness == null ? Strictness.LEGACY_STRICT : jsonWriterSettings.strictness);
    jsonWriter.setSerializeNulls(jsonWriterSettings.serializeNulls);
    return jsonWriter;
  }

  /**
   * Returns a new JSON reader configured for the settings on this Gson instance.
   *
   * <p>The following settings are considered:
   *
   * <ul>
   *   <li>{@link GsonBuilder#setStrictness(Strictness)}. If no {@linkplain
   *       GsonBuilder#setStrictness(Strictness) explicit strictness has been set} the created
   *       reader will have a strictness of {@link Strictness#LEGACY_STRICT}. Otherwise, the
   *       strictness of the {@code Gson} instance will be used for the created reader.
   * </ul>
   */
  public JsonReader newJsonReader(Reader reader) {
    JsonReader jsonReader = new JsonReader(reader);
    jsonReader.setStrictness(jsonWriterSettings.strictness == null ? Strictness.LEGACY_STRICT : jsonWriterSettings.strictness);
    return jsonReader;
  }
```

### 7. EDIT `gson/src/main/java/com/google/gson/Gson.java` (11-line block → 11-line replacement)

**Replaces:**

```java
  public <T> T fromJson(JsonReader reader, TypeToken<T> typeOfT)
      throws JsonIOException, JsonSyntaxException {
    boolean isEmpty = true;
    Strictness oldStrictness = reader.getStrictness();

    if (this.strictness != null) {
      reader.setStrictness(this.strictness);
    } else if (reader.getStrictness() == Strictness.LEGACY_STRICT) {
      // For backward compatibility change to LENIENT if reader has default strictness LEGACY_STRICT
      reader.setStrictness(Strictness.LENIENT);
    }
```

**With:**

```java
  public <T> T fromJson(JsonReader reader, TypeToken<T> typeOfT)
      throws JsonIOException, JsonSyntaxException {
    boolean isEmpty = true;
    Strictness oldStrictness = reader.getStrictness();

    if (jsonWriterSettings.strictness != null) {
      reader.setStrictness(jsonWriterSettings.strictness);
    } else if (reader.getStrictness() == Strictness.LEGACY_STRICT) {
      // For backward compatibility change to LENIENT if reader has default strictness LEGACY_STRICT
      reader.setStrictness(Strictness.LENIENT);
    }
```

### 8. EDIT `gson/src/main/java/com/google/gson/Gson.java` (10-line block → 10-line replacement)

**Replaces:**

```java
  @Override
  public String toString() {
    return "{serializeNulls:"
        + serializeNulls
        + ",factories:"
        + factories
        + ",instanceCreators:"
        + constructorConstructor
        + "}";
  }
```

**With:**

```java
  @Override
  public String toString() {
    return "{serializeNulls:"
        + jsonWriterSettings.serializeNulls
        + ",factories:"
        + factories
        + ",instanceCreators:"
        + constructorConstructor
        + "}";
  }
```

### 9. CREATE `gson/src/main/java/com/google/gson/JsonWriterSettings.java` (20 line(s))

```java
package com.google.gson;

/**
 * Configuration settings for JSON I/O operations.
 */
public final class JsonWriterSettings {
  final boolean serializeNulls;
  final boolean generateNonExecutableJson;
  final boolean htmlSafe;
  final FormattingStyle formattingStyle;
  final Strictness strictness;

  public JsonWriterSettings(boolean serializeNulls, boolean generateNonExecutableJson, boolean htmlSafe, FormattingStyle formattingStyle, Strictness strictness) {
    this.serializeNulls = serializeNulls;
    this.generateNonExecutableJson = generateNonExecutableJson;
    this.htmlSafe = htmlSafe;
    this.formattingStyle = formattingStyle;
    this.strictness = strictness;
  }
}
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `gson/src/main/java/com/google/gson/Gson.java` | 1183 → 1181 | 38 → 38 | 7.21 → 7.21 | 237 → 237 | 0 → 0 |
| `gson/src/main/java/com/google/gson/JsonWriterSettings.java` | - → 18 | - → 0 | - → 2 | - → 2 | - → 0 |

## Diff

```diff
diff --git a/gson/src/main/java/com/google/gson/Gson.java b/gson/src/main/java/com/google/gson/Gson.java
index a06f290..07666ac 100644
--- a/gson/src/main/java/com/google/gson/Gson.java
+++ b/gson/src/main/java/com/google/gson/Gson.java
@@ -162,12 +162,8 @@ public final class Gson {
   final Excluder excluder;
   final FieldNamingStrategy fieldNamingStrategy;
   final Map<Type, InstanceCreator<?>> instanceCreators;
-  final boolean serializeNulls;
   final boolean complexMapKeySerialization;
-  final boolean generateNonExecutableJson;
-  final boolean htmlSafe;
-  final FormattingStyle formattingStyle;
-  final Strictness strictness;
+  final JsonWriterSettings jsonWriterSettings;
   final boolean serializeSpecialFloatingPointValues;
   final boolean useJdkUnsafe;
   final String datePattern;
@@ -227,12 +223,14 @@ public final class Gson {
     this.excluder = builder.excluder;
     this.fieldNamingStrategy = builder.fieldNamingPolicy;
     this.instanceCreators = new HashMap<>(builder.instanceCreators);
-    this.serializeNulls = builder.serializeNulls;
     this.complexMapKeySerialization = builder.complexMapKeySerialization;
-    this.generateNonExecutableJson = builder.generateNonExecutableJson;
-    this.htmlSafe = builder.escapeHtmlChars;
-    this.formattingStyle = builder.formattingStyle;
-    this.strictness = builder.strictness;
+    this.jsonWriterSettings = new JsonWriterSettings(
+        builder.serializeNulls,
+        builder.generateNonExecutableJson,
+        builder.escapeHtmlChars,
+        builder.formattingStyle,
+        builder.strictness
+    );
     this.serializeSpecialFloatingPointValues = builder.serializeSpecialFloatingPointValues;
     this.useJdkUnsafe = builder.useJdkUnsafe;
     this.longSerializationPolicy = builder.longSerializationPolicy;
@@ -292,7 +290,7 @@ public final class Gson {
    * @see GsonBuilder#serializeNulls()
    */
   public boolean serializeNulls() {
-    return serializeNulls;
+    return jsonWriterSettings.serializeNulls;
   }
 
   /**
@@ -302,7 +300,7 @@ public final class Gson {
    * @see GsonBuilder#disableHtmlEscaping()
    */
   public boolean htmlSafe() {
-    return htmlSafe;
+    return jsonWriterSettings.htmlSafe;
   }
 
   /**
@@ -649,8 +647,8 @@ public final class Gson {
     TypeAdapter<Object> adapter = (TypeAdapter<Object>) getAdapter(TypeToken.get(typeOfSrc));
 
     Strictness oldStrictness = writer.getStrictness();
-    if (this.strictness != null) {
-      writer.setStrictness(this.strictness);
+    if (jsonWriterSettings.strictness != null) {
+      writer.setStrictness(jsonWriterSettings.strictness);
     } else if (writer.getStrictness() == Strictness.LEGACY_STRICT) {
       // For backward compatibility change to LENIENT if writer has default strictness LEGACY_STRICT
       writer.setStrictness(Strictness.LENIENT);
@@ -659,8 +657,8 @@ public final class Gson {
     boolean oldHtmlSafe = writer.isHtmlSafe();
     boolean oldSerializeNulls = writer.getSerializeNulls();
 
-    writer.setHtmlSafe(htmlSafe);
-    writer.setSerializeNulls(serializeNulls);
+    writer.setHtmlSafe(jsonWriterSettings.htmlSafe);
+    writer.setSerializeNulls(jsonWriterSettings.serializeNulls);
     try {
       adapter.write(writer, src);
     } catch (IOException e) {
@@ -730,11 +728,11 @@ public final class Gson {
     boolean oldHtmlSafe = writer.isHtmlSafe();
     boolean oldSerializeNulls = writer.getSerializeNulls();
 
-    writer.setHtmlSafe(htmlSafe);
-    writer.setSerializeNulls(serializeNulls);
+    writer.setHtmlSafe(jsonWriterSettings.htmlSafe);
+    writer.setSerializeNulls(jsonWriterSettings.serializeNulls);
 
-    if (this.strictness != null) {
-      writer.setStrictness(this.strictness);
+    if (jsonWriterSettings.strictness != null) {
+      writer.setStrictness(jsonWriterSettings.strictness);
     } else if (writer.getStrictness() == Strictness.LEGACY_STRICT) {
       // For backward compatibility change to LENIENT if writer has default strictness LEGACY_STRICT
       writer.setStrictness(Strictness.LENIENT);
@@ -772,14 +770,14 @@ public final class Gson {
    * </ul>
    */
   public JsonWriter newJsonWriter(Writer writer) throws IOException {
-    if (generateNonExecutableJson) {
+    if (jsonWriterSettings.generateNonExecutableJson) {
       writer.write(JSON_NON_EXECUTABLE_PREFIX);
     }
     JsonWriter jsonWriter = new JsonWriter(writer);
-    jsonWriter.setFormattingStyle(formattingStyle);
-    jsonWriter.setHtmlSafe(htmlSafe);
-    jsonWriter.setStrictness(strictness == null ? Strictness.LEGACY_STRICT : strictness);
-    jsonWriter.setSerializeNulls(serializeNulls);
+    jsonWriter.setFormattingStyle(jsonWriterSettings.formattingStyle);
+    jsonWriter.setHtmlSafe(jsonWriterSettings.htmlSafe);
+    jsonWriter.setStrictness(jsonWriterSettings.strictness == null ? Strictness.LEGACY_STRICT : jsonWriterSettings.strictness);
+    jsonWriter.setSerializeNulls(jsonWriterSettings.serializeNulls);
     return jsonWriter;
   }
 
@@ -797,7 +795,7 @@ public final class Gson {
    */
   public JsonReader newJsonReader(Reader reader) {
     JsonReader jsonReader = new JsonReader(reader);
-    jsonReader.setStrictness(strictness == null ? Strictness.LEGACY_STRICT : strictness);
+    jsonReader.setStrictness(jsonWriterSettings.strictness == null ? Strictness.LEGACY_STRICT : jsonWriterSettings.strictness);
     return jsonReader;
   }
 
@@ -1066,8 +1064,8 @@ public final class Gson {
     boolean isEmpty = true;
     Strictness oldStrictness = reader.getStrictness();
 
-    if (this.strictness != null) {
-      reader.setStrictness(this.strictness);
+    if (jsonWriterSettings.strictness != null) {
+      reader.setStrictness(jsonWriterSettings.strictness);
     } else if (reader.getStrictness() == Strictness.LEGACY_STRICT) {
       // For backward compatibility change to LENIENT if reader has default strictness LEGACY_STRICT
       reader.setStrictness(Strictness.LENIENT);
@@ -1255,7 +1253,7 @@ public final class Gson {
   @Override
   public String toString() {
     return "{serializeNulls:"
-        + serializeNulls
+        + jsonWriterSettings.serializeNulls
         + ",factories:"
         + factories
         + ",instanceCreators:"
diff --git a/gson/src/main/java/com/google/gson/JsonWriterSettings.java b/gson/src/main/java/com/google/gson/JsonWriterSettings.java
new file mode 100644
index 0000000..0000000
--- /dev/null
+++ b/gson/src/main/java/com/google/gson/JsonWriterSettings.java
@@ -0,0 +1,20 @@
+package com.google.gson;
+
+/**
+ * Configuration settings for JSON I/O operations.
+ */
+public final class JsonWriterSettings {
+  final boolean serializeNulls;
+  final boolean generateNonExecutableJson;
+  final boolean htmlSafe;
+  final FormattingStyle formattingStyle;
+  final Strictness strictness;
+
+  public JsonWriterSettings(boolean serializeNulls, boolean generateNonExecutableJson, boolean htmlSafe, FormattingStyle formattingStyle, Strictness strictness) {
+    this.serializeNulls = serializeNulls;
+    this.generateNonExecutableJson = generateNonExecutableJson;
+    this.htmlSafe = htmlSafe;
+    this.formattingStyle = formattingStyle;
+    this.strictness = strictness;
+  }
+}
\ No newline at end of file

```
