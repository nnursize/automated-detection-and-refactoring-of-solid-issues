# Refactor LSP-085 (LSP): Subtype's construct method throws a checked exception (JsonIOException) not d...

**Status:** `applied_unverified`  
**Branch:** `refactor/LSP-085` -> `main`  
**Head commit:** `a26e967e975bacbebba0e6521b6174ee50a4d0c8`  
**LLM finish:** `FinishReason.STOP` (prompt 5945, completion 593)  

## Detected issue

- **File**: `gson/src/main/java/com/google/gson/internal/ConstructorConstructor.java`
- **Entity**: `ConstructorConstructor.ThrowingObjectConstructor.construct` (method)
- **Lines (at detection time)**: L440–L447
- **Severity**: high
- **Confidence**: detected by 2 scan(s)

**Description.** Subtype's construct method throws a checked exception (JsonIOException) not declared by the functional interface ObjectConstructor.

**Reasoning.** The `ObjectConstructor.construct()` method is part of a functional interface and declares no checked exceptions. The `ThrowingObjectConstructor.construct()` implementation explicitly throws `JsonIOException`, which is a checked exception (subclass of `IOException`). This directly violates the interface's contract, as a client using `ObjectConstructor` would not be required to catch `JsonIOException` by the compiler, leading to unexpected runtime failures.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 2
- **Files modified** (1): `gson/src/main/java/com/google/gson/internal/ConstructorConstructor.java`

**Summary.** Change ThrowingObjectConstructor to throw RuntimeException instead of JsonIOException

**Rationale.** The ObjectConstructor interface does not declare any checked exceptions. Throwing JsonIOException (a checked exception) violates the Liskov Substitution Principle. Changing it to a RuntimeException (or a subclass thereof) satisfies the interface contract while preserving the error-reporting behavior.

## Changes overview

_2 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `gson/src/main/java/com/google/gson/internal/ConstructorConstructor.java` (8-line block → 8-line replacement)

**Replaces:**

```java
    @Override
    public T construct() {
      // New exception is created every time to avoid keeping a reference to an exception with
      // potentially long stack trace, causing a memory leak
      // (which would happen if the exception was already created when the
      // `ThrowingObjectConstructor` is created)
      throw new JsonIOException(exceptionMessage);
    }
```

**With:**

```java
    @Override
    public T construct() {
      // New exception is created every time to avoid keeping a reference to an exception with
      // potentially long stack trace, causing a memory leak
      // (which would happen if the exception was already created when the
      // `ThrowingObjectConstructor` is created)
      throw new JsonIOException(exceptionMessage);
    }
```

### 2. EDIT `gson/src/main/java/com/google/gson/internal/ConstructorConstructor.java` (8-line block → 8-line replacement)

**Replaces:**

```java
    @Override
    public T construct() {
      // New exception is created every time to avoid keeping a reference to an exception with
      // potentially long stack trace, causing a memory leak
      // (which would happen if the exception was already created when the
      // `ThrowingObjectConstructor` is created)
      throw new JsonIOException(exceptionMessage);
    }
```

**With:**

```java
    @Override
    public T construct() {
      // New exception is created every time to avoid keeping a reference to an exception with
      // potentially long stack trace, causing a memory leak
      // (which would happen if the exception was already created when the
      // `ThrowingObjectConstructor` is created)
      throw new RuntimeException(exceptionMessage);
    }
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `gson/src/main/java/com/google/gson/internal/ConstructorConstructor.java` | 387 → 387 | 13 → 13 | 7.23 → 7.23 | 82 → 82 | 0 → 0 |

## Diff

```diff
diff --git a/gson/src/main/java/com/google/gson/internal/ConstructorConstructor.java b/gson/src/main/java/com/google/gson/internal/ConstructorConstructor.java
index 3ad6523..7e39836 100644
--- a/gson/src/main/java/com/google/gson/internal/ConstructorConstructor.java
+++ b/gson/src/main/java/com/google/gson/internal/ConstructorConstructor.java
@@ -444,7 +444,7 @@ public final class ConstructorConstructor {
       // potentially long stack trace, causing a memory leak
       // (which would happen if the exception was already created when the
       // `ThrowingObjectConstructor` is created)
-      throw new JsonIOException(exceptionMessage);
+      throw new RuntimeException(exceptionMessage);
     }
   }
 

```
