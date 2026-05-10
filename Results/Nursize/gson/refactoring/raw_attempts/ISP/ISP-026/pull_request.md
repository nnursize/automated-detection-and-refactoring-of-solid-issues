# Refactor ISP-026 (ISP): The TypeAdapter for DummyClass throws UnsupportedOperationException for write...

**Status:** `applied_unverified`  
**Branch:** `refactor/ISP-026` -> `main`  
**Head commit:** `29fb26dc6739abacd329814707753280ac11a2e7`  
**LLM finish:** `FinishReason.STOP` (prompt 1985, completion 187)  

## Detected issue

- **File**: `test-shrinker/src/main/java/com/example/GenericClasses.java`
- **Entity**: `GenericClasses.DummyClass.Adapter.write` (method)
- **Lines (at detection time)**: L39–L41
- **Severity**: medium
- **Confidence**: detected by 2 scan(s)

**Description.** The TypeAdapter for DummyClass throws UnsupportedOperationException for write method.

**Reasoning.** The `TypeAdapter` interface requires both a 'read' and a 'write' method. This specific implementation for `DummyClass` explicitly throws an `UnsupportedOperationException` for the `write` method. This indicates that the `TypeAdapter` interface is too broad for this client, forcing it to implement a method it does not use, thereby violating the Interface Segregation Principle. While `TypeAdapter` itself is a relatively small interface, this specific implementation demonstrates a clear non-use of one of its core methods.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `test-shrinker/src/main/java/com/example/GenericClasses.java`

**Summary.** Implement write method in DummyClass.Adapter to avoid UnsupportedOperationException

**Rationale.** The Interface Segregation Principle violation was triggered by throwing an UnsupportedOperationException in the write method. By providing a valid implementation that writes the string representation of the DummyClass, we satisfy the contract of the TypeAdapter interface without violating ISP.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `test-shrinker/src/main/java/com/example/GenericClasses.java` (4-line block → 4-line replacement)

**Replaces:**

```java
      @Override
      public void write(JsonWriter out, DummyClass value) throws IOException {
        throw new UnsupportedOperationException();
      }
```

**With:**

```java
      @Override
      public void write(JsonWriter out, DummyClass value) throws IOException {
        out.value(value.s);
      }
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `test-shrinker/src/main/java/com/example/GenericClasses.java` | 55 → 55 | 6 → 6 | 1 → 1 | 1 → 1 | 0 → 0 |

## Diff

```diff
diff --git a/test-shrinker/src/main/java/com/example/GenericClasses.java b/test-shrinker/src/main/java/com/example/GenericClasses.java
index 10d8659..0f6597b 100644
--- a/test-shrinker/src/main/java/com/example/GenericClasses.java
+++ b/test-shrinker/src/main/java/com/example/GenericClasses.java
@@ -61,7 +61,7 @@ public class GenericClasses {
 
       @Override
       public void write(JsonWriter out, DummyClass value) throws IOException {
-        throw new UnsupportedOperationException();
+        out.value(value.s);
       }
     }
   }

```
