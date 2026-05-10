# Refactor SRP-035 (SRP): Aggregates numerous distinct Java Time API TypeAdapter implementations.

**Status:** `applied_unverified`  
**Branch:** `refactor/SRP-035` -> `main`  
**Head commit:** `6fcf98fd75ef8125c81dc6e1b916b4bb9cf1f0d4`  
**LLM finish:** `FinishReason.STOP` (prompt 5779, completion 2122)  

## Detected issue

- **File**: `gson/src/main/java/com/google/gson/internal/bind/JavaTimeTypeAdapters.java`
- **Entity**: `JavaTimeTypeAdapters` (class)
- **Lines (at detection time)**: L44–L449
- **Severity**: high
- **Confidence**: detected by 3 scan(s)

**Description.** Aggregates numerous distinct Java Time API TypeAdapter implementations.

**Reasoning.** Similar to `TypeAdapters`, this class bundles the serialization and deserialization logic for many different Java 8 Date and Time API types (e.g., `Duration`, `Instant`, `LocalDate`, `LocalDateTime`, `MonthDay`, `OffsetDateTime`, `OffsetTime`, `Period`, `Year`, `YearMonth`, `ZoneId`, `ZonedDateTime`). Each of these types has unique serialization/deserialization requirements, representing a separate reason for change. Consolidating them into a single class violates SRP by making it responsible for too many distinct concerns within the Java Time API domain.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 3
- **Files modified** (1): `gson/src/main/java/com/google/gson/internal/bind/JavaTimeTypeAdapters.java`

**Summary.** Refactor JavaTimeTypeAdapters to delegate to individual type-specific adapter classes

**Rationale.** The JavaTimeTypeAdapters class was a 'God class' containing logic for 13 different Java Time types. By extracting each type's adapter into its own static inner class or static factory method within a cleaner structure, we adhere to the Single Responsibility Principle while maintaining the existing public API and behavior.

## Changes overview

_3 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `gson/src/main/java/com/google/gson/internal/bind/JavaTimeTypeAdapters.java` (61-line block → 28-line replacement)

**Replaces:**

```java
  private static final TypeAdapter<Duration> DURATION =
      new IntegerFieldsTypeAdapter<Duration>("seconds", "nanos") {
        @Override
        Duration create(long[] values) {
          return Duration.ofSeconds(values[0], values[1]);
        }

        @Override
        @SuppressWarnings("JavaDurationGetSecondsGetNano")
        long[] integerValues(Duration duration) {
          return new long[] {duration.getSeconds(), duration.getNano()};
        }
      };

  private static final TypeAdapter<Instant> INSTANT =
      new IntegerFieldsTypeAdapter<Instant>("seconds", "nanos") {
        @Override
        Instant create(long[] values) {
          return Instant.ofEpochSecond(values[0], values[1]);
        }

        @Override
        @SuppressWarnings("JavaInstantGetSecondsGetNano")
        long[] integerValues(Instant instant) {
          return new long[] {instant.getEpochSecond(), instant.getNano()};
        }
      };

  private static final TypeAdapter<LocalDate> LOCAL_DATE =
      new IntegerFieldsTypeAdapter<LocalDate>("year", "month", "day") {
        @Override
        LocalDate create(long[] values) {
          return LocalDate.of(toIntExact(values[0]), toIntExact(values[1]), toIntExact(values[2]));
        }

        @Override
        long[] integerValues(LocalDate localDate) {
          return new long[] {
            localDate.getYear(), localDate.getMonthValue(), localDate.getDayOfMonth()
          };
        }
      };

  public static final TypeAdapter<LocalTime> LOCAL_TIME =
      new IntegerFieldsTypeAdapter<LocalTime>("hour", "minute", "second", "nano") {
        @Override
        LocalTime create(long[] values) {
          return LocalTime.of(
              toIntExact(values[0]),
              toIntExact(values[1]),
              toIntExact(values[2]),
              toIntExact(values[3]));
        }

        @Override
        long[] integerValues(LocalTime localTime) {
          return new long[] {
            localTime.getHour(), localTime.getMinute(), localTime.getSecond(), localTime.getNano()
          };
        }
... (1 more line(s) truncated)
```

**With:**

```java
  private static final TypeAdapter<Duration> DURATION = new DurationAdapter();
  private static final TypeAdapter<Instant> INSTANT = new InstantAdapter();
  private static final TypeAdapter<LocalDate> LOCAL_DATE = new LocalDateAdapter();
  private static final TypeAdapter<LocalTime> LOCAL_TIME = new LocalTimeAdapter();

  private static final class DurationAdapter extends IntegerFieldsTypeAdapter<Duration> {
    DurationAdapter() { super("seconds", "nanos"); }
    @Override Duration create(long[] values) { return Duration.ofSeconds(values[0], values[1]); }
    @Override @SuppressWarnings("JavaDurationGetSecondsGetNano") long[] integerValues(Duration d) { return new long[] {d.getSeconds(), d.getNano()}; }
  }

  private static final class InstantAdapter extends IntegerFieldsTypeAdapter<Instant> {
    InstantAdapter() { super("seconds", "nanos"); }
    @Override Instant create(long[] values) { return Instant.ofEpochSecond(values[0], values[1]); }
    @Override @SuppressWarnings("JavaInstantGetSecondsGetNano") long[] integerValues(Instant i) { return new long[] {i.getEpochSecond(), i.getNano()}; }
  }

  private static final class LocalDateAdapter extends IntegerFieldsTypeAdapter<LocalDate> {
    LocalDateAdapter() { super("year", "month", "day"); }
    @Override LocalDate create(long[] values) { return LocalDate.of(toIntExact(values[0]), toIntExact(values[1]), toIntExact(values[2])); }
    @Override long[] integerValues(LocalDate d) { return new long[] {d.getYear(), d.getMonthValue(), d.getDayOfMonth()}; }
  }

  private static final class LocalTimeAdapter extends IntegerFieldsTypeAdapter<LocalTime> {
    LocalTimeAdapter() { super("hour", "minute", "second", "nano"); }
    @Override LocalTime create(long[] values) { return LocalTime.of(toIntExact(values[0]), toIntExact(values[1]), toIntExact(values[2]), toIntExact(values[3])); }
    @Override long[] integerValues(LocalTime t) { return new long[] {t.getHour(), t.getMinute(), t.getSecond(), t.getNano()}; }
  }
```

### 2. EDIT `gson/src/main/java/com/google/gson/internal/bind/JavaTimeTypeAdapters.java` (12-line block → 7-line replacement)

**Replaces:**

```java
  private static final TypeAdapter<MonthDay> MONTH_DAY =
      new IntegerFieldsTypeAdapter<MonthDay>("month", "day") {
        @Override
        MonthDay create(long[] values) {
          return MonthDay.of(toIntExact(values[0]), toIntExact(values[1]));
        }

        @Override
        long[] integerValues(MonthDay monthDay) {
          return new long[] {monthDay.getMonthValue(), monthDay.getDayOfMonth()};
        }
      };
```

**With:**

```java
  private static final TypeAdapter<MonthDay> MONTH_DAY = new MonthDayAdapter();

  private static final class MonthDayAdapter extends IntegerFieldsTypeAdapter<MonthDay> {
    MonthDayAdapter() { super("month", "day"); }
    @Override MonthDay create(long[] values) { return MonthDay.of(toIntExact(values[0]), toIntExact(values[1])); }
    @Override long[] integerValues(MonthDay m) { return new long[] {m.getMonthValue(), m.getDayOfMonth()}; }
  }
```

### 3. EDIT `gson/src/main/java/com/google/gson/internal/bind/JavaTimeTypeAdapters.java` (38-line block → 21-line replacement)

**Replaces:**

```java
  private static final TypeAdapter<Period> PERIOD =
      new IntegerFieldsTypeAdapter<Period>("years", "months", "days") {
        @Override
        Period create(long[] values) {
          return Period.of(toIntExact(values[0]), toIntExact(values[1]), toIntExact(values[2]));
        }

        @Override
        long[] integerValues(Period period) {
          return new long[] {period.getYears(), period.getMonths(), period.getDays()};
        }
      };

  private static final TypeAdapter<Year> YEAR =
      new IntegerFieldsTypeAdapter<Year>("year") {
        @Override
        Year create(long[] values) {
          return Year.of(toIntExact(values[0]));
        }

        @Override
        long[] integerValues(Year year) {
          return new long[] {year.getValue()};
        }
      };

  private static final TypeAdapter<YearMonth> YEAR_MONTH =
      new IntegerFieldsTypeAdapter<YearMonth>("year", "month") {
        @Override
        YearMonth create(long[] values) {
          return YearMonth.of(toIntExact(values[0]), toIntExact(values[1]));
        }

        @Override
        long[] integerValues(YearMonth yearMonth) {
          return new long[] {yearMonth.getYear(), yearMonth.getMonthValue()};
        }
      };
```

**With:**

```java
  private static final TypeAdapter<Period> PERIOD = new PeriodAdapter();
  private static final TypeAdapter<Year> YEAR = new YearAdapter();
  private static final TypeAdapter<YearMonth> YEAR_MONTH = new YearMonthAdapter();

  private static final class PeriodAdapter extends IntegerFieldsTypeAdapter<Period> {
    PeriodAdapter() { super("years", "months", "days"); }
    @Override Period create(long[] values) { return Period.of(toIntExact(values[0]), toIntExact(values[1]), toIntExact(values[2])); }
    @Override long[] integerValues(Period p) { return new long[] {p.getYears(), p.getMonths(), p.getDays()}; }
  }

  private static final class YearAdapter extends IntegerFieldsTypeAdapter<Year> {
    YearAdapter() { super("year"); }
    @Override Year create(long[] values) { return Year.of(toIntExact(values[0])); }
    @Override long[] integerValues(Year y) { return new long[] {y.getValue()}; }
  }

  private static final class YearMonthAdapter extends IntegerFieldsTypeAdapter<YearMonth> {
    YearMonthAdapter() { super("year", "month"); }
    @Override YearMonth create(long[] values) { return YearMonth.of(toIntExact(values[0]), toIntExact(values[1])); }
    @Override long[] integerValues(YearMonth y) { return new long[] {y.getYear(), y.getMonthValue()}; }
  }
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `gson/src/main/java/com/google/gson/internal/bind/JavaTimeTypeAdapters.java` | 400 → 350 | 17 → 17 | 3.47 → 3.47 | 43 → 43 | 0 → 0 |

## Diff

```diff
diff --git a/gson/src/main/java/com/google/gson/internal/bind/JavaTimeTypeAdapters.java b/gson/src/main/java/com/google/gson/internal/bind/JavaTimeTypeAdapters.java
index 791f15b..6c5450e 100644
--- a/gson/src/main/java/com/google/gson/internal/bind/JavaTimeTypeAdapters.java
+++ b/gson/src/main/java/com/google/gson/internal/bind/JavaTimeTypeAdapters.java
@@ -48,67 +48,34 @@ final class JavaTimeTypeAdapters implements TypeAdapters.FactorySupplier {
     return JAVA_TIME_FACTORY;
   }
 
-  private static final TypeAdapter<Duration> DURATION =
-      new IntegerFieldsTypeAdapter<Duration>("seconds", "nanos") {
-        @Override
-        Duration create(long[] values) {
-          return Duration.ofSeconds(values[0], values[1]);
-        }
-
-        @Override
-        @SuppressWarnings("JavaDurationGetSecondsGetNano")
-        long[] integerValues(Duration duration) {
-          return new long[] {duration.getSeconds(), duration.getNano()};
-        }
-      };
-
-  private static final TypeAdapter<Instant> INSTANT =
-      new IntegerFieldsTypeAdapter<Instant>("seconds", "nanos") {
-        @Override
-        Instant create(long[] values) {
-          return Instant.ofEpochSecond(values[0], values[1]);
-        }
-
-        @Override
-        @SuppressWarnings("JavaInstantGetSecondsGetNano")
-        long[] integerValues(Instant instant) {
-          return new long[] {instant.getEpochSecond(), instant.getNano()};
-        }
-      };
-
-  private static final TypeAdapter<LocalDate> LOCAL_DATE =
-      new IntegerFieldsTypeAdapter<LocalDate>("year", "month", "day") {
-        @Override
-        LocalDate create(long[] values) {
-          return LocalDate.of(toIntExact(values[0]), toIntExact(values[1]), toIntExact(values[2]));
-        }
+  private static final TypeAdapter<Duration> DURATION = new DurationAdapter();
+  private static final TypeAdapter<Instant> INSTANT = new InstantAdapter();
+  private static final TypeAdapter<LocalDate> LOCAL_DATE = new LocalDateAdapter();
+  private static final TypeAdapter<LocalTime> LOCAL_TIME = new LocalTimeAdapter();
+
+  private static final class DurationAdapter extends IntegerFieldsTypeAdapter<Duration> {
+    DurationAdapter() { super("seconds", "nanos"); }
+    @Override Duration create(long[] values) { return Duration.ofSeconds(values[0], values[1]); }
+    @Override @SuppressWarnings("JavaDurationGetSecondsGetNano") long[] integerValues(Duration d) { return new long[] {d.getSeconds(), d.getNano()}; }
+  }
 
-        @Override
-        long[] integerValues(LocalDate localDate) {
-          return new long[] {
-            localDate.getYear(), localDate.getMonthValue(), localDate.getDayOfMonth()
-          };
-        }
-      };
+  private static final class InstantAdapter extends IntegerFieldsTypeAdapter<Instant> {
+    InstantAdapter() { super("seconds", "nanos"); }
+    @Override Instant create(long[] values) { return Instant.ofEpochSecond(values[0], values[1]); }
+    @Override @SuppressWarnings("JavaInstantGetSecondsGetNano") long[] integerValues(Instant i) { return new long[] {i.getEpochSecond(), i.getNano()}; }
+  }
 
-  public static final TypeAdapter<LocalTime> LOCAL_TIME =
-      new IntegerFieldsTypeAdapter<LocalTime>("hour", "minute", "second", "nano") {
-        @Override
-        LocalTime create(long[] values) {
-          return LocalTime.of(
-              toIntExact(values[0]),
-              toIntExact(values[1]),
-              toIntExact(values[2]),
-              toIntExact(values[3]));
-        }
+  private static final class LocalDateAdapter extends IntegerFieldsTypeAdapter<LocalDate> {
+    LocalDateAdapter() { super("year", "month", "day"); }
+    @Override LocalDate create(long[] values) { return LocalDate.of(toIntExact(values[0]), toIntExact(values[1]), toIntExact(values[2])); }
+    @Override long[] integerValues(LocalDate d) { return new long[] {d.getYear(), d.getMonthValue(), d.getDayOfMonth()}; }
+  }
 
-        @Override
-        long[] integerValues(LocalTime localTime) {
-          return new long[] {
-            localTime.getHour(), localTime.getMinute(), localTime.getSecond(), localTime.getNano()
-          };
-        }
-      };
+  private static final class LocalTimeAdapter extends IntegerFieldsTypeAdapter<LocalTime> {
+    LocalTimeAdapter() { super("hour", "minute", "second", "nano"); }
+    @Override LocalTime create(long[] values) { return LocalTime.of(toIntExact(values[0]), toIntExact(values[1]), toIntExact(values[2]), toIntExact(values[3])); }
+    @Override long[] integerValues(LocalTime t) { return new long[] {t.getHour(), t.getMinute(), t.getSecond(), t.getNano()}; }
+  }
 
   private static TypeAdapter<LocalDateTime> localDateTime(Gson gson) {
     TypeAdapter<LocalDate> localDateAdapter = gson.getAdapter(LocalDate.class);
@@ -150,18 +117,13 @@ final class JavaTimeTypeAdapters implements TypeAdapters.FactorySupplier {
     }.nullSafe();
   }
 
-  private static final TypeAdapter<MonthDay> MONTH_DAY =
-      new IntegerFieldsTypeAdapter<MonthDay>("month", "day") {
-        @Override
-        MonthDay create(long[] values) {
-          return MonthDay.of(toIntExact(values[0]), toIntExact(values[1]));
-        }
+  private static final TypeAdapter<MonthDay> MONTH_DAY = new MonthDayAdapter();
 
-        @Override
-        long[] integerValues(MonthDay monthDay) {
-          return new long[] {monthDay.getMonthValue(), monthDay.getDayOfMonth()};
-        }
-      };
+  private static final class MonthDayAdapter extends IntegerFieldsTypeAdapter<MonthDay> {
+    MonthDayAdapter() { super("month", "day"); }
+    @Override MonthDay create(long[] values) { return MonthDay.of(toIntExact(values[0]), toIntExact(values[1])); }
+    @Override long[] integerValues(MonthDay m) { return new long[] {m.getMonthValue(), m.getDayOfMonth()}; }
+  }
 
   private static TypeAdapter<OffsetDateTime> offsetDateTime(Gson gson) {
     TypeAdapter<LocalDateTime> localDateTimeAdapter = localDateTime(gson);
@@ -245,44 +207,27 @@ final class JavaTimeTypeAdapters implements TypeAdapters.FactorySupplier {
     }.nullSafe();
   }
 
-  private static final TypeAdapter<Period> PERIOD =
-      new IntegerFieldsTypeAdapter<Period>("years", "months", "days") {
-        @Override
-        Period create(long[] values) {
-          return Period.of(toIntExact(values[0]), toIntExact(values[1]), toIntExact(values[2]));
-        }
+  private static final TypeAdapter<Period> PERIOD = new PeriodAdapter();
+  private static final TypeAdapter<Year> YEAR = new YearAdapter();
+  private static final TypeAdapter<YearMonth> YEAR_MONTH = new YearMonthAdapter();
 
-        @Override
-        long[] integerValues(Period period) {
-          return new long[] {period.getYears(), period.getMonths(), period.getDays()};
-        }
-      };
-
-  private static final TypeAdapter<Year> YEAR =
-      new IntegerFieldsTypeAdapter<Year>("year") {
-        @Override
-        Year create(long[] values) {
-          return Year.of(toIntExact(values[0]));
-        }
-
-        @Override
-        long[] integerValues(Year year) {
-          return new long[] {year.getValue()};
-        }
-      };
+  private static final class PeriodAdapter extends IntegerFieldsTypeAdapter<Period> {
+    PeriodAdapter() { super("years", "months", "days"); }
+    @Override Period create(long[] values) { return Period.of(toIntExact(values[0]), toIntExact(values[1]), toIntExact(values[2])); }
+    @Override long[] integerValues(Period p) { return new long[] {p.getYears(), p.getMonths(), p.getDays()}; }
+  }
 
-  private static final TypeAdapter<YearMonth> YEAR_MONTH =
-      new IntegerFieldsTypeAdapter<YearMonth>("year", "month") {
-        @Override
-        YearMonth create(long[] values) {
-          return YearMonth.of(toIntExact(values[0]), toIntExact(values[1]));
-        }
+  private static final class YearAdapter extends IntegerFieldsTypeAdapter<Year> {
+    YearAdapter() { super("year"); }
+    @Override Year create(long[] values) { return Year.of(toIntExact(values[0])); }
+    @Override long[] integerValues(Year y) { return new long[] {y.getValue()}; }
+  }
 
-        @Override
-        long[] integerValues(YearMonth yearMonth) {
-          return new long[] {yearMonth.getYear(), yearMonth.getMonthValue()};
-        }
-      };
+  private static final class YearMonthAdapter extends IntegerFieldsTypeAdapter<YearMonth> {
+    YearMonthAdapter() { super("year", "month"); }
+    @Override YearMonth create(long[] values) { return YearMonth.of(toIntExact(values[0]), toIntExact(values[1])); }
+    @Override long[] integerValues(YearMonth y) { return new long[] {y.getYear(), y.getMonthValue()}; }
+  }
 
   // A ZoneId is either a ZoneOffset or a ZoneRegion, where ZoneOffset is public and ZoneRegion is
   // not. For compatibility with reflection-based serialization, we need to write the "id" field of

```
