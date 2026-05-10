# Refactor OCP-018 (OCP): Large if-else if chain for specific java.time types violates OCP.

**Status:** `applied_unverified`  
**Branch:** `refactor/OCP-018` -> `main`  
**Head commit:** `04a632b05fe1b7980330a1de38f2ad9fa993f310`  
**LLM finish:** `FinishReason.STOP` (prompt 5851, completion 1205)  

## Detected issue

- **File**: `gson/src/main/java/com/google/gson/internal/bind/JavaTimeTypeAdapters.java`
- **Entity**: `JavaTimeTypeAdapters.JAVA_TIME_FACTORY.create` (method)
- **Lines (at detection time)**: L340–L376
- **Severity**: high
- **Confidence**: detected by 3 scan(s)

**Description.** Large if-else if chain for specific java.time types violates OCP.

**Reasoning.** The `create` method in `JAVA_TIME_FACTORY` contains a long `if-else if` chain that explicitly checks for numerous `java.time` classes (Duration, Instant, LocalDate, etc.) to return their respective type adapters. Adding support for any new `java.time` type would require modifying this method, making it a clear violation of OCP.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `gson/src/main/java/com/google/gson/internal/bind/JavaTimeTypeAdapters.java`

**Summary.** Replace if-else chain in JavaTimeTypeAdapters with a Map-based registry for OCP compliance.

**Rationale.** By using a Map to store TypeAdapter providers (functional interfaces), we eliminate the hardcoded if-else chain. New java.time types can now be supported by simply adding an entry to the registry map, adhering to the Open/Closed Principle.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `gson/src/main/java/com/google/gson/internal/bind/JavaTimeTypeAdapters.java` (48-line block → 38-line replacement)

**Replaces:**

```java
  static final TypeAdapterFactory JAVA_TIME_FACTORY =
      new TypeAdapterFactory() {
        @Override
        public <T> TypeAdapter<T> create(Gson gson, TypeToken<T> typeToken) {
          Class<? super T> rawType = typeToken.getRawType();
          if (!rawType.getName().startsWith("java.time.")) {
            // Immediately return null so we don't load all these classes when nobody's doing
            // anything with java.time.
            return null;
          }
          TypeAdapter<?> adapter = null;
          if (rawType == Duration.class) {
            adapter = DURATION;
          } else if (rawType == Instant.class) {
            adapter = INSTANT;
          } else if (rawType == LocalDate.class) {
            adapter = LOCAL_DATE;
          } else if (rawType == LocalTime.class) {
            adapter = LOCAL_TIME;
          } else if (rawType == LocalDateTime.class) {
            adapter = localDateTime(gson);
          } else if (rawType == MonthDay.class) {
            adapter = MONTH_DAY;
          } else if (rawType == OffsetDateTime.class) {
            adapter = offsetDateTime(gson);
          } else if (rawType == OffsetTime.class) {
            adapter = offsetTime(gson);
          } else if (rawType == Period.class) {
            adapter = PERIOD;
          } else if (rawType == Year.class) {
            adapter = YEAR;
          } else if (rawType == YearMonth.class) {
            adapter = YEAR_MONTH;
          } else if (rawType == ZoneId.class || rawType == ZoneOffset.class) {
            // We don't check ZoneId.class.isAssignableFrom(rawType) because we don't want to match
            // the non-public class ZoneRegion in the runtime type check in
            // TypeAdapterRuntimeTypeWrapper.write. If we did, then our ZONE_ID would take
            // precedence over a ZoneId adapter that the user might have registered. (This exact
            // situation showed up in a Google-internal test.)
            adapter = ZONE_ID;
          } else if (rawType == ZonedDateTime.class) {
            adapter = zonedDateTime(gson);
          }
          @SuppressWarnings("unchecked")
          TypeAdapter<T> result = (TypeAdapter<T>) adapter;
          return result;
        }
      };
```

**With:**

```java
  private interface AdapterProvider {
    TypeAdapter<?> get(Gson gson);
  }

  private static final java.util.Map<Class<?>, AdapterProvider> ADAPTER_REGISTRY = new java.util.HashMap<>();

  static {
    ADAPTER_REGISTRY.put(Duration.class, g -> DURATION);
    ADAPTER_REGISTRY.put(Instant.class, g -> INSTANT);
    ADAPTER_REGISTRY.put(LocalDate.class, g -> LOCAL_DATE);
    ADAPTER_REGISTRY.put(LocalTime.class, g -> LOCAL_TIME);
    ADAPTER_REGISTRY.put(LocalDateTime.class, JavaTimeTypeAdapters::localDateTime);
    ADAPTER_REGISTRY.put(MonthDay.class, g -> MONTH_DAY);
    ADAPTER_REGISTRY.put(OffsetDateTime.class, JavaTimeTypeAdapters::offsetDateTime);
    ADAPTER_REGISTRY.put(OffsetTime.class, JavaTimeTypeAdapters::offsetTime);
    ADAPTER_REGISTRY.put(Period.class, g -> PERIOD);
    ADAPTER_REGISTRY.put(Year.class, g -> YEAR);
    ADAPTER_REGISTRY.put(YearMonth.class, g -> YEAR_MONTH);
    ADAPTER_REGISTRY.put(ZoneId.class, g -> ZONE_ID);
    ADAPTER_REGISTRY.put(ZoneOffset.class, g -> ZONE_ID);
    ADAPTER_REGISTRY.put(ZonedDateTime.class, JavaTimeTypeAdapters::zonedDateTime);
  }

  static final TypeAdapterFactory JAVA_TIME_FACTORY =
      new TypeAdapterFactory() {
        @Override
        public <T> TypeAdapter<T> create(Gson gson, TypeToken<T> typeToken) {
          Class<? super T> rawType = typeToken.getRawType();
          if (!rawType.getName().startsWith("java.time.")) {
            return null;
          }
          AdapterProvider provider = ADAPTER_REGISTRY.get(rawType);
          if (provider == null) return null;
          @SuppressWarnings("unchecked")
          TypeAdapter<T> result = (TypeAdapter<T>) provider.get(gson);
          return result;
        }
      };
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `gson/src/main/java/com/google/gson/internal/bind/JavaTimeTypeAdapters.java` | 350 → 344 | 17 → 17 | 3.47 → 2.65 | 43 → 29 | 0 → 0 |

## Diff

```diff
diff --git a/gson/src/main/java/com/google/gson/internal/bind/JavaTimeTypeAdapters.java b/gson/src/main/java/com/google/gson/internal/bind/JavaTimeTypeAdapters.java
index 6c5450e..5a729cc 100644
--- a/gson/src/main/java/com/google/gson/internal/bind/JavaTimeTypeAdapters.java
+++ b/gson/src/main/java/com/google/gson/internal/bind/JavaTimeTypeAdapters.java
@@ -335,51 +335,41 @@ final class JavaTimeTypeAdapters implements TypeAdapters.FactorySupplier {
     }.nullSafe();
   }
 
+  private interface AdapterProvider {
+    TypeAdapter<?> get(Gson gson);
+  }
+
+  private static final java.util.Map<Class<?>, AdapterProvider> ADAPTER_REGISTRY = new java.util.HashMap<>();
+
+  static {
+    ADAPTER_REGISTRY.put(Duration.class, g -> DURATION);
+    ADAPTER_REGISTRY.put(Instant.class, g -> INSTANT);
+    ADAPTER_REGISTRY.put(LocalDate.class, g -> LOCAL_DATE);
+    ADAPTER_REGISTRY.put(LocalTime.class, g -> LOCAL_TIME);
+    ADAPTER_REGISTRY.put(LocalDateTime.class, JavaTimeTypeAdapters::localDateTime);
+    ADAPTER_REGISTRY.put(MonthDay.class, g -> MONTH_DAY);
+    ADAPTER_REGISTRY.put(OffsetDateTime.class, JavaTimeTypeAdapters::offsetDateTime);
+    ADAPTER_REGISTRY.put(OffsetTime.class, JavaTimeTypeAdapters::offsetTime);
+    ADAPTER_REGISTRY.put(Period.class, g -> PERIOD);
+    ADAPTER_REGISTRY.put(Year.class, g -> YEAR);
+    ADAPTER_REGISTRY.put(YearMonth.class, g -> YEAR_MONTH);
+    ADAPTER_REGISTRY.put(ZoneId.class, g -> ZONE_ID);
+    ADAPTER_REGISTRY.put(ZoneOffset.class, g -> ZONE_ID);
+    ADAPTER_REGISTRY.put(ZonedDateTime.class, JavaTimeTypeAdapters::zonedDateTime);
+  }
+
   static final TypeAdapterFactory JAVA_TIME_FACTORY =
       new TypeAdapterFactory() {
         @Override
         public <T> TypeAdapter<T> create(Gson gson, TypeToken<T> typeToken) {
           Class<? super T> rawType = typeToken.getRawType();
           if (!rawType.getName().startsWith("java.time.")) {
-            // Immediately return null so we don't load all these classes when nobody's doing
-            // anything with java.time.
             return null;
           }
-          TypeAdapter<?> adapter = null;
-          if (rawType == Duration.class) {
-            adapter = DURATION;
-          } else if (rawType == Instant.class) {
-            adapter = INSTANT;
-          } else if (rawType == LocalDate.class) {
-            adapter = LOCAL_DATE;
-          } else if (rawType == LocalTime.class) {
-            adapter = LOCAL_TIME;
-          } else if (rawType == LocalDateTime.class) {
-            adapter = localDateTime(gson);
-          } else if (rawType == MonthDay.class) {
-            adapter = MONTH_DAY;
-          } else if (rawType == OffsetDateTime.class) {
-            adapter = offsetDateTime(gson);
-          } else if (rawType == OffsetTime.class) {
-            adapter = offsetTime(gson);
-          } else if (rawType == Period.class) {
-            adapter = PERIOD;
-          } else if (rawType == Year.class) {
-            adapter = YEAR;
-          } else if (rawType == YearMonth.class) {
-            adapter = YEAR_MONTH;
-          } else if (rawType == ZoneId.class || rawType == ZoneOffset.class) {
-            // We don't check ZoneId.class.isAssignableFrom(rawType) because we don't want to match
-            // the non-public class ZoneRegion in the runtime type check in
-            // TypeAdapterRuntimeTypeWrapper.write. If we did, then our ZONE_ID would take
-            // precedence over a ZoneId adapter that the user might have registered. (This exact
-            // situation showed up in a Google-internal test.)
-            adapter = ZONE_ID;
-          } else if (rawType == ZonedDateTime.class) {
-            adapter = zonedDateTime(gson);
-          }
+          AdapterProvider provider = ADAPTER_REGISTRY.get(rawType);
+          if (provider == null) return null;
           @SuppressWarnings("unchecked")
-          TypeAdapter<T> result = (TypeAdapter<T>) adapter;
+          TypeAdapter<T> result = (TypeAdapter<T>) provider.get(gson);
           return result;
         }
       };

```
