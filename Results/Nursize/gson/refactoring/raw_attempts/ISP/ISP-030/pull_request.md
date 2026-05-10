# Refactor ISP-030 (ISP): The JsonStreamParser class implements the Iterator interface but throws Unsup...

**Status:** `applied_unverified`  
**Branch:** `refactor/ISP-030` -> `main`  
**Head commit:** `de90492db9f3797f7f81fa43a09671d1cdfe469f`  
**LLM finish:** `FinishReason.STOP` (prompt 2855, completion 187)  

## Detected issue

- **File**: `gson/src/main/java/com/google/gson/JsonStreamParser.java`
- **Entity**: `JsonStreamParser.remove` (method)
- **Lines (at detection time)**: L95–L97
- **Severity**: medium
- **Confidence**: detected by 2 scan(s)

**Description.** The JsonStreamParser class implements the Iterator interface but throws UnsupportedOperationException for the remove() method.

**Reasoning.** This is a clear violation of ISP. Clients of JsonStreamParser are forced to depend on the remove() method of the Iterator interface, even though JsonStreamParser does not support this operation. The Iterator interface is a 'fat interface' in this context because it combines traversal and modification responsibilities. Ideally, JsonStreamParser should implement a more specialized interface that only provides traversal, or Iterator should be split into Iterable and RemovableIterator.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `gson/src/main/java/com/google/gson/JsonStreamParser.java`

**Summary.** Remove the unsupported remove() method from JsonStreamParser

**Rationale.** The remove() method in Iterator is an optional operation that throws UnsupportedOperationException in this implementation. Removing it cleans up the API and adheres to the Interface Segregation Principle by not forcing clients to depend on a method that cannot be used.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `gson/src/main/java/com/google/gson/JsonStreamParser.java` (11-line block → 1-line replacement)

**Replaces:**

```java
  /**
   * This optional {@link Iterator} method is not relevant for stream parsing and hence is not
   * implemented.
   *
   * @since 1.4
   */
  @Override
  public void remove() {
    throw new UnsupportedOperationException();
  }
}
```

**With:**

```java
}
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `gson/src/main/java/com/google/gson/JsonStreamParser.java` | 117 → 107 | 3 → 2 | 5.67 → 7.5 | 15 → 14 | 0 → 0 |

## Diff

```diff
diff --git a/gson/src/main/java/com/google/gson/JsonStreamParser.java b/gson/src/main/java/com/google/gson/JsonStreamParser.java
index 2720335..1732be2 100644
--- a/gson/src/main/java/com/google/gson/JsonStreamParser.java
+++ b/gson/src/main/java/com/google/gson/JsonStreamParser.java
@@ -112,14 +112,4 @@ public final class JsonStreamParser implements Iterator<JsonElement> {
     }
   }
 
-  /**
-   * This optional {@link Iterator} method is not relevant for stream parsing and hence is not
-   * implemented.
-   *
-   * @since 1.4
-   */
-  @Override
-  public void remove() {
-    throw new UnsupportedOperationException();
-  }
 }

```
