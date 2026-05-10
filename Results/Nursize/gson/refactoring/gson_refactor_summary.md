# Refactor summary: gson

- Total attempts: **60**
  - `applied_unverified`: 42
  - `patch_failed`: 17
  - `llm_error`: 1

## All attempts

| Issue | Principle | Status | Tests passed/total | CC before -> after | MI before -> after | File |
|-------|-----------|--------|--------------------|--------------------|--------------------|------|
| DIP-001 | DIP | `patch_failed` | - | - | - | `gson/src/main/java/com/google/gson/Gson.java` |
| DIP-002 | DIP | `applied_unverified` | - | 4.15 -> 4.13 | 0.0 -> 0.0 | `gson/src/main/java/com/google/gson/GsonBuilder.java` |
| DIP-004 | DIP | `applied_unverified` | - | 11.88 -> 9.7 | 0.0 -> 0.0 | `gson/src/main/java/com/google/gson/internal/bind/ReflectiveTypeAdapterFactory.java` |
| DIP-005 | DIP | `patch_failed` | - | - | - | `gson/src/main/java/com/google/gson/internal/bind/JsonAdapterAnnotationTypeAdapterFactory.java` |
| DIP-006 | DIP | `applied_unverified` | - | 4.15 -> 4.15 | 0.0 -> 0.0 | `gson/src/main/java/com/google/gson/GsonBuilder.java` |
| DIP-011 | DIP | `patch_failed` | - | - | - | `gson/src/main/java/com/google/gson/GsonBuilder.java` |
| DIP-012 | DIP | `patch_failed` | - | - | - | `gson/src/main/java/com/google/gson/TypeAdapter.java` |
| DIP-014 | DIP | `patch_failed` | - | - | - | `gson/src/main/java/com/google/gson/stream/JsonReader.java` |
| DIP-015 | DIP | `patch_failed` | - | - | - | `gson/src/main/java/com/google/gson/stream/JsonReader.java` |
| DIP-016 | DIP | `patch_failed` | - | - | - | `gson/src/main/java/com/google/gson/Gson.java` |
| DIP-021 | DIP | `patch_failed` | - | - | - | `gson/src/main/java/com/google/gson/GsonBuilder.java` |
| DIP-023 | DIP | `applied_unverified` | - | 7.23 -> 6.92 | 0.0 -> 0.0 | `gson/src/main/java/com/google/gson/internal/ConstructorConstructor.java` |
| ISP-001 | ISP | `applied_unverified` | - | 2.01 -> 2.01 | 0.0 -> 0.0 | `gson/src/main/java/com/google/gson/internal/bind/TypeAdapters.java` |
| ISP-002 | ISP | `applied_unverified` | - | 11.62 -> 11.88 | 0.0 -> 0.0 | `gson/src/main/java/com/google/gson/internal/bind/ReflectiveTypeAdapterFactory.java` |
| ISP-006 | ISP | `applied_unverified` | - | 4.19 -> 2.62 | 0.0 -> 0.0 | `gson/src/main/java/com/google/gson/JsonElement.java` |
| ISP-010 | ISP | `patch_failed` | - | - | - | `gson/src/main/java/com/google/gson/JsonArray.java` |
| ISP-019 | ISP | `patch_failed` | - | - | - | `gson/src/main/java/com/google/gson/JsonObject.java` |
| ISP-022 | ISP | `patch_failed` | - | - | - | `gson/src/main/java/com/google/gson/JsonElement.java` |
| ISP-026 | ISP | `applied_unverified` | - | 1.0 -> 1.0 | 0.0 -> 0.0 | `test-shrinker/src/main/java/com/example/GenericClasses.java` |
| ISP-028 | ISP | `patch_failed` | - | - | - | `gson/src/main/java/com/google/gson/JsonNull.java` |
| ISP-030 | ISP | `applied_unverified` | - | 5.67 -> 7.5 | 0.0 -> 0.0 | `gson/src/main/java/com/google/gson/JsonStreamParser.java` |
| ISP-036 | ISP | `applied_unverified` | - | 2.01 -> 2.01 | 0.0 -> 0.0 | `gson/src/main/java/com/google/gson/internal/bind/TypeAdapters.java` |
| ISP-039 | ISP | `applied_unverified` | - | 2.83 -> 3.4 | 0.0 -> 0.0 | `gson/src/main/java/com/google/gson/internal/reflect/ReflectionHelper.java` |
| ISP-041 | ISP | `applied_unverified` | - | 6.5 -> 7.6 | 0.0 -> 0.0 | `gson/src/main/java/com/google/gson/internal/bind/JsonAdapterAnnotationTypeAdapterFactory.java` |
| LSP-009 | LSP | `applied_unverified` | - | 3.28 -> 3.28 | 0.0 -> 0.0 | `gson/src/main/java/com/google/gson/internal/bind/JsonTreeReader.java` |
| LSP-013 | LSP | `applied_unverified` | - | 2.08 -> 2.05 | 0.0 -> 0.0 | `gson/src/main/java/com/google/gson/internal/bind/TypeAdapters.java` |
| LSP-019 | LSP | `patch_failed` | - | - | - | `gson/src/main/java/com/google/gson/JsonArray.java` |
| LSP-020 | LSP | `applied_unverified` | - | 1.24 -> 1.19 | 0.0 -> 0.0 | `gson/src/main/java/com/google/gson/internal/NonNullElementWrapperList.java` |
| LSP-028 | LSP | `applied_unverified` | - | 9.8 -> 11.62 | 0.0 -> 0.0 | `gson/src/main/java/com/google/gson/internal/bind/ReflectiveTypeAdapterFactory.java` |
| LSP-058 | LSP | `applied_unverified` | - | 2.05 -> 2.01 | 0.0 -> 0.0 | `gson/src/main/java/com/google/gson/internal/bind/TypeAdapters.java` |
| LSP-059 | LSP | `llm_error` | - | - | - | `gson/src/main/java/com/google/gson/internal/bind/TypeAdapters.java` |
| LSP-085 | LSP | `applied_unverified` | - | 7.23 -> 7.23 | 0.0 -> 0.0 | `gson/src/main/java/com/google/gson/internal/ConstructorConstructor.java` |
| LSP-105 | LSP | `patch_failed` | - | - | - | `gson/src/main/java/com/google/gson/JsonElement.java` |
| LSP-107 | LSP | `applied_unverified` | - | 3.32 -> 3.32 | 0.0 -> 0.0 | `gson/src/main/java/com/google/gson/JsonPrimitive.java` |
| LSP-108 | LSP | `applied_unverified` | - | 2.83 -> 2.83 | 0.0 -> 0.0 | `gson/src/main/java/com/google/gson/internal/reflect/ReflectionHelper.java` |
| LSP-112 | LSP | `applied_unverified` | - | 4.64 -> 4.57 | 0.0 -> 0.0 | `proto/src/main/java/com/google/gson/protobuf/ProtoTypeAdapter.java` |
| OCP-002 | OCP | `applied_unverified` | - | 10.64 -> 1.0 | 0.0 -> 0.0 | `gson/src/main/java/com/google/gson/stream/JsonReader.java` |
| OCP-018 | OCP | `applied_unverified` | - | 3.47 -> 2.65 | 0.0 -> 0.0 | `gson/src/main/java/com/google/gson/internal/bind/JavaTimeTypeAdapters.java` |
| OCP-019 | OCP | `applied_unverified` | - | 4.24 -> 2.0 | 0.0 -> 0.0 | `gson/src/main/java/com/google/gson/GsonBuilder.java` |
| OCP-023 | OCP | `applied_unverified` | - | 9.09 -> 9.8 | 0.0 -> 0.0 | `gson/src/main/java/com/google/gson/internal/bind/ReflectiveTypeAdapterFactory.java` |
| OCP-025 | OCP | `applied_unverified` | - | 7.38 -> 7.15 | 0.0 -> 0.0 | `gson/src/main/java/com/google/gson/internal/ConstructorConstructor.java` |
| OCP-026 | OCP | `applied_unverified` | - | 7.15 -> 7.23 | 0.0 -> 0.0 | `gson/src/main/java/com/google/gson/internal/ConstructorConstructor.java` |
| OCP-028 | OCP | `applied_unverified` | - | 7.23 -> 6.92 | 0.0 -> 0.0 | `gson/src/main/java/com/google/gson/internal/ConstructorConstructor.java` |
| OCP-029 | OCP | `applied_unverified` | - | 6.92 -> 7.23 | 0.0 -> 0.0 | `gson/src/main/java/com/google/gson/internal/ConstructorConstructor.java` |
| OCP-041 | OCP | `applied_unverified` | - | 8.5 -> 8.5 | 0.0 -> 0.0 | `gson/src/main/java/com/google/gson/internal/bind/JsonElementTypeAdapter.java` |
| OCP-069 | OCP | `applied_unverified` | - | 3.32 -> 3.28 | 0.0 -> 0.0 | `gson/src/main/java/com/google/gson/internal/bind/JsonTreeReader.java` |
| OCP-070 | OCP | `applied_unverified` | - | 8.5 -> 9.33 | 0.0 -> 0.0 | `gson/src/main/java/com/google/gson/internal/bind/JsonElementTypeAdapter.java` |
| OCP-092 | OCP | `applied_unverified` | - | 4.24 -> 4.15 | 0.0 -> 0.0 | `gson/src/main/java/com/google/gson/GsonBuilder.java` |
| SRP-001 | SRP | `applied_unverified` | - | 10.86 -> 5.92 | 0.0 -> 0.0 | `gson/src/main/java/com/google/gson/stream/JsonReader.java` |
| SRP-002 | SRP | `applied_unverified` | - | 4.38 -> 4.24 | 0.0 -> 0.0 | `gson/src/main/java/com/google/gson/GsonBuilder.java` |
| SRP-003 | SRP | `applied_unverified` | - | 7.21 -> 4.61 | 0.0 -> 0.0 | `gson/src/main/java/com/google/gson/Gson.java` |
| SRP-004 | SRP | `applied_unverified` | - | 2.17 -> 2.6 | 0.0 -> 0.0 | `gson/src/main/java/com/google/gson/internal/bind/TypeAdapters.java` |
| SRP-005 | SRP | `patch_failed` | - | - | - | `gson/src/main/java/com/google/gson/GsonBuilder.java` |
| SRP-006 | SRP | `applied_unverified` | - | 2.79 -> 2.72 | 0.0 -> 0.0 | `gson/src/main/java/com/google/gson/internal/LinkedTreeMap.java` |
| SRP-007 | SRP | `applied_unverified` | - | 8.58 -> 6.54 | 0.0 -> 0.0 | `gson/src/main/java/com/google/gson/internal/bind/ReflectiveTypeAdapterFactory.java` |
| SRP-008 | SRP | `applied_unverified` | - | 3.5 -> 4.97 | 0.0 -> 0.0 | `gson/src/main/java/com/google/gson/stream/JsonWriter.java` |
| SRP-011 | SRP | `patch_failed` | - | - | - | `gson/src/main/java/com/google/gson/JsonArray.java` |
| SRP-012 | SRP | `patch_failed` | - | - | - | `gson/src/main/java/com/google/gson/JsonElement.java` |
| SRP-021 | SRP | `applied_unverified` | - | 2.88 -> 2.81 | 0.0 -> 0.0 | `metrics/src/main/java/com/google/gson/metrics/ParseBenchmark.java` |
| SRP-035 | SRP | `applied_unverified` | - | 3.47 -> 3.47 | 0.0 -> 0.0 | `gson/src/main/java/com/google/gson/internal/bind/JavaTimeTypeAdapters.java` |