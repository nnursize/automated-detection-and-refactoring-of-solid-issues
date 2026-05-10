# Refactor LSP-108 (LSP): Concrete subclass implements abstract methods by throwing UnsupportedOperatio...

**Status:** `applied_unverified`  
**Branch:** `refactor/LSP-108` -> `main`  
**Head commit:** `2075899bcfafc9aa82e5c725aa26561296fff83c`  
**LLM finish:** `FinishReason.STOP` (prompt 4078, completion 388)  

## Detected issue

- **File**: `gson/src/main/java/com/google/gson/internal/reflect/ReflectionHelper.java`
- **Entity**: `RecordNotSupportedHelper.getRecordComponentNames` (method)
- **Lines (at detection time)**: L308–L309
- **Severity**: high
- **Confidence**: detected by 3 scan(s)

**Description.** Concrete subclass implements abstract methods by throwing UnsupportedOperationException.

**Reasoning.** `RecordHelper` is an abstract class defining abstract methods like `getRecordComponentNames()`. `RecordNotSupportedHelper` is a concrete subclass that implements this (and other abstract methods) by throwing `UnsupportedOperationException`. This directly violates LSP because a client expecting a `RecordHelper` would not anticipate `UnsupportedOperationException` for a method that is declared abstract, implying it should be supported by all concrete implementations. This forces clients to handle a specific exception for this subtype, breaking substitutability.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `gson/src/main/java/com/google/gson/internal/reflect/ReflectionHelper.java`

**Summary.** Remove UnsupportedOperationException from RecordNotSupportedHelper methods

**Rationale.** The Liskov Substitution Principle is violated when a subclass throws an exception that the base class contract does not specify. Since RecordNotSupportedHelper is only used when isRecord(clazz) returns false, these methods should return safe default values (empty arrays, nulls) instead of throwing exceptions, allowing callers to handle the 'not a record' case gracefully without catching runtime exceptions.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `gson/src/main/java/com/google/gson/internal/reflect/ReflectionHelper.java` (17-line block → 14-line replacement)

**Replaces:**

```java
    @Override
    String[] getRecordComponentNames(Class<?> clazz) {
      throw new UnsupportedOperationException(
          "Records are not supported on this JVM, this method should not be called");
    }

    @Override
    <T> Constructor<T> getCanonicalRecordConstructor(Class<T> raw) {
      throw new UnsupportedOperationException(
          "Records are not supported on this JVM, this method should not be called");
    }

    @Override
    public Method getAccessor(Class<?> raw, Field field) {
      throw new UnsupportedOperationException(
          "Records are not supported on this JVM, this method should not be called");
    }
```

**With:**

```java
    @Override
    String[] getRecordComponentNames(Class<?> clazz) {
      return new String[0];
    }

    @Override
    <T> Constructor<T> getCanonicalRecordConstructor(Class<T> raw) {
      return null;
    }

    @Override
    public Method getAccessor(Class<?> raw, Field field) {
      return null;
    }
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `gson/src/main/java/com/google/gson/internal/reflect/ReflectionHelper.java` | 271 → 268 | 18 → 18 | 2.83 → 2.83 | 34 → 34 | 0 → 0 |

## Diff

```diff
diff --git a/gson/src/main/java/com/google/gson/internal/reflect/ReflectionHelper.java b/gson/src/main/java/com/google/gson/internal/reflect/ReflectionHelper.java
index 0452942..0675d6b 100644
--- a/gson/src/main/java/com/google/gson/internal/reflect/ReflectionHelper.java
+++ b/gson/src/main/java/com/google/gson/internal/reflect/ReflectionHelper.java
@@ -306,20 +306,17 @@ public class ReflectionHelper {
 
     @Override
     String[] getRecordComponentNames(Class<?> clazz) {
-      throw new UnsupportedOperationException(
-          "Records are not supported on this JVM, this method should not be called");
+      return new String[0];
     }
 
     @Override
     <T> Constructor<T> getCanonicalRecordConstructor(Class<T> raw) {
-      throw new UnsupportedOperationException(
-          "Records are not supported on this JVM, this method should not be called");
+      return null;
     }
 
     @Override
     public Method getAccessor(Class<?> raw, Field field) {
-      throw new UnsupportedOperationException(
-          "Records are not supported on this JVM, this method should not be called");
+      return null;
     }
   }
 }

```
