# Refactor SRP-007 (SRP): The ReflectiveTypeAdapterFactory orchestrates a complex process of class intr...

**Status:** `applied_unverified`  
**Branch:** `refactor/SRP-007` -> `main`  
**Head commit:** `c369ce2a5b0db349a63447adb4b21d9030414e5c`  
**LLM finish:** `FinishReason.STOP` (prompt 7768, completion 999)  

## Detected issue

- **File**: `gson/src/main/java/com/google/gson/internal/bind/ReflectiveTypeAdapterFactory.java`
- **Entity**: `ReflectiveTypeAdapterFactory` (class)
- **Lines (at detection time)**: L40–L457
- **Severity**: high
- **Confidence**: detected by 3 scan(s)

**Description.** The ReflectiveTypeAdapterFactory orchestrates a complex process of class introspection, applying various configuration rules (exclusion, naming, access), and creating specialized adapters for different class structures.

**Reasoning.** This class exhibits the God Class smell. It is responsible for a multitude of concerns related to reflective type adaptation: delegating field exclusion to `excluder`, determining JSON field names based on `fieldNamingPolicy` and `@SerializedName` (`getFieldNames`), applying reflection access filters, handling different class types (regular classes vs. Java Records), creating object constructors via `constructorConstructor`, managing `@JsonAdapter` annotations, building `BoundField` representations, and traversing the class hierarchy (`getBoundFields`). This broad and intricate set of responsibilities means it has many independent reasons to change, such as updates to field naming conventions, new record features, or changes in reflection access rules, violating SRP.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 2
- **Files created** (1): `gson/src/main/java/com/google/gson/internal/bind/FieldNamingHelper.java`
- **Files modified** (1): `gson/src/main/java/com/google/gson/internal/bind/ReflectiveTypeAdapterFactory.java`

**Summary.** Extract field naming logic into a dedicated helper class

**Rationale.** The ReflectiveTypeAdapterFactory was handling field naming policy logic directly, which is a distinct responsibility. Moving this to a helper class reduces the size and complexity of the factory, adhering better to SRP.

## Changes overview

_2 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `gson/src/main/java/com/google/gson/internal/bind/ReflectiveTypeAdapterFactory.java` (24-line block → 12-line replacement)

**Replaces:**

```java
  /** first element holds the default name */
  @SuppressWarnings("MixedMutabilityReturnType")
  private List<String> getFieldNames(Field f) {

    String fieldName;
    List<String> alternates;
    SerializedName annotation = f.getAnnotation(SerializedName.class);
    if (annotation == null) {
      fieldName = fieldNamingPolicy.translateName(f);
      alternates = fieldNamingPolicy.alternateNames(f);
    } else {
      fieldName = annotation.value();
      alternates = Arrays.asList(annotation.alternate());
    }

    if (alternates.isEmpty()) {
      return Collections.singletonList(fieldName);
    }

    List<String> fieldNames = new ArrayList<>(alternates.size() + 1);
    fieldNames.add(fieldName);
    fieldNames.addAll(alternates);
    return fieldNames;
  }
```

**With:**

```java
>>>>>>> REPLACE

<<<<<<< SEARCH gson/src/main/java/com/google/gson/internal/bind/ReflectiveTypeAdapterFactory.java
        Type fieldType = GsonTypes.resolve(type.getType(), raw, field.getGenericType());
        List<String> fieldNames = getFieldNames(field);
        String serializedName = fieldNames.get(0);
        BoundField boundField =
=======
        Type fieldType = GsonTypes.resolve(type.getType(), raw, field.getGenericType());
        List<String> fieldNames = FieldNamingHelper.getFieldNames(fieldNamingPolicy, field);
        String serializedName = fieldNames.get(0);
        BoundField boundField =
```

### 2. CREATE `gson/src/main/java/com/google/gson/internal/bind/FieldNamingHelper.java` (51 line(s))

```java
/*
 * Copyright (C) 2024 Google Inc.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package com.google.gson.internal.bind;

import com.google.gson.FieldNamingStrategy;
import com.google.gson.annotations.SerializedName;
import java.lang.reflect.Field;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

final class FieldNamingHelper {
  private FieldNamingHelper() {}

  static List<String> getFieldNames(FieldNamingStrategy fieldNamingPolicy, Field f) {
    String fieldName;
    List<String> alternates;
    SerializedName annotation = f.getAnnotation(SerializedName.class);
    if (annotation == null) {
      fieldName = fieldNamingPolicy.translateName(f);
      alternates = fieldNamingPolicy.alternateNames(f);
    } else {
      fieldName = annotation.value();
      alternates = Arrays.asList(annotation.alternate());
    }

    if (alternates.isEmpty()) {
      return Collections.singletonList(fieldName);
    }

    List<String> fieldNames = new ArrayList<>(alternates.size() + 1);
    fieldNames.add(fieldName);
    fieldNames.addAll(alternates);
    return fieldNames;
  }
}
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `gson/src/main/java/com/google/gson/internal/bind/FieldNamingHelper.java` | - → 45 | - → 1 | - → 4 | - → 4 | - → 0 |
| `gson/src/main/java/com/google/gson/internal/bind/ReflectiveTypeAdapterFactory.java` | 548 → 538 | 12 → 11 | 8.58 → 9.09 | 92 → 90 | 0 → 0 |

## Diff

```diff
diff --git a/gson/src/main/java/com/google/gson/internal/bind/ReflectiveTypeAdapterFactory.java b/gson/src/main/java/com/google/gson/internal/bind/ReflectiveTypeAdapterFactory.java
index ef46468..3010bef 100644
--- a/gson/src/main/java/com/google/gson/internal/bind/ReflectiveTypeAdapterFactory.java
+++ b/gson/src/main/java/com/google/gson/internal/bind/ReflectiveTypeAdapterFactory.java
@@ -81,30 +81,18 @@ public final class ReflectiveTypeAdapterFactory implements TypeAdapterFactory {
     return !excluder.excludeField(f, serialize);
   }
 
-  /** first element holds the default name */
-  @SuppressWarnings("MixedMutabilityReturnType")
-  private List<String> getFieldNames(Field f) {
-
-    String fieldName;
-    List<String> alternates;
-    SerializedName annotation = f.getAnnotation(SerializedName.class);
-    if (annotation == null) {
-      fieldName = fieldNamingPolicy.translateName(f);
-      alternates = fieldNamingPolicy.alternateNames(f);
-    } else {
-      fieldName = annotation.value();
-      alternates = Arrays.asList(annotation.alternate());
-    }
-
-    if (alternates.isEmpty()) {
-      return Collections.singletonList(fieldName);
-    }
+>>>>>>> REPLACE
 
-    List<String> fieldNames = new ArrayList<>(alternates.size() + 1);
-    fieldNames.add(fieldName);
-    fieldNames.addAll(alternates);
-    return fieldNames;
-  }
+<<<<<<< SEARCH gson/src/main/java/com/google/gson/internal/bind/ReflectiveTypeAdapterFactory.java
+        Type fieldType = GsonTypes.resolve(type.getType(), raw, field.getGenericType());
+        List<String> fieldNames = getFieldNames(field);
+        String serializedName = fieldNames.get(0);
+        BoundField boundField =
+=======
+        Type fieldType = GsonTypes.resolve(type.getType(), raw, field.getGenericType());
+        List<String> fieldNames = FieldNamingHelper.getFieldNames(fieldNamingPolicy, field);
+        String serializedName = fieldNames.get(0);
+        BoundField boundField =
 
   @Override
   public <T> TypeAdapter<T> create(Gson gson, TypeToken<T> type) {
diff --git a/gson/src/main/java/com/google/gson/internal/bind/FieldNamingHelper.java b/gson/src/main/java/com/google/gson/internal/bind/FieldNamingHelper.java
new file mode 100644
index 0000000..0000000
--- /dev/null
+++ b/gson/src/main/java/com/google/gson/internal/bind/FieldNamingHelper.java
@@ -0,0 +1,51 @@
+/*
+ * Copyright (C) 2024 Google Inc.
+ *
+ * Licensed under the Apache License, Version 2.0 (the "License");
+ * you may not use this file except in compliance with the License.
+ * You may obtain a copy of the License at
+ *
+ *      http://www.apache.org/licenses/LICENSE-2.0
+ *
+ * Unless required by applicable law or agreed to in writing, software
+ * distributed under the License is distributed on an "AS IS" BASIS,
+ * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
+ * See the License for the specific language governing permissions and
+ * limitations under the License.
+ */
+
+package com.google.gson.internal.bind;
+
+import com.google.gson.FieldNamingStrategy;
+import com.google.gson.annotations.SerializedName;
+import java.lang.reflect.Field;
+import java.util.ArrayList;
+import java.util.Arrays;
+import java.util.Collections;
+import java.util.List;
+
+final class FieldNamingHelper {
+  private FieldNamingHelper() {}
+
+  static List<String> getFieldNames(FieldNamingStrategy fieldNamingPolicy, Field f) {
+    String fieldName;
+    List<String> alternates;
+    SerializedName annotation = f.getAnnotation(SerializedName.class);
+    if (annotation == null) {
+      fieldName = fieldNamingPolicy.translateName(f);
+      alternates = fieldNamingPolicy.alternateNames(f);
+    } else {
+      fieldName = annotation.value();
+      alternates = Arrays.asList(annotation.alternate());
+    }
+
+    if (alternates.isEmpty()) {
+      return Collections.singletonList(fieldName);
+    }
+
+    List<String> fieldNames = new ArrayList<>(alternates.size() + 1);
+    fieldNames.add(fieldName);
+    fieldNames.addAll(alternates);
+    return fieldNames;
+  }
+}
\ No newline at end of file

```
