# Refactor LSP-020 (LSP): The 'add' and 'set' methods throw NullPointerException for null elements, str...

**Status:** `applied_unverified`  
**Branch:** `refactor/LSP-020` -> `main`  
**Head commit:** `f98d2f20b3461a7c528746a7f4f3e56652bef1fd`  
**LLM finish:** `FinishReason.STOP` (prompt 2489, completion 297)  

## Detected issue

- **File**: `gson/src/main/java/com/google/gson/internal/NonNullElementWrapperList.java`
- **Entity**: `NonNullElementWrapperList.add` (method)
- **Lines (at detection time)**: L43–L45
- **Severity**: high
- **Confidence**: detected by 2 scan(s)

**Description.** The 'add' and 'set' methods throw NullPointerException for null elements, strengthening preconditions compared to standard ArrayList.

**Reasoning.** The `NonNullElementWrapperList` wraps an `ArrayList`. Its `add(int, E)` and `set(int, E)` methods explicitly throw `NullPointerException` if the element to be added or set is `null`. A standard `ArrayList<E>` (for object types) typically permits `null` elements. By disallowing `null` elements and throwing a `NullPointerException`, this class strengthens the precondition for these methods. If a client expects a `List` that behaves like a standard `ArrayList` (allowing `null`s), substituting `NonNullElementWrapperList` would violate LSP by introducing a stricter contract.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `gson/src/main/java/com/google/gson/internal/NonNullElementWrapperList.java`

**Summary.** Remove null-check enforcement in NonNullElementWrapperList to comply with List contract

**Rationale.** The NonNullElementWrapperList was enforcing a stricter contract than the List interface by throwing NullPointerException on null elements. Removing these checks allows the class to behave like a standard List, satisfying the Liskov Substitution Principle.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `gson/src/main/java/com/google/gson/internal/NonNullElementWrapperList.java` (16-line block → 9-line replacement)

**Replaces:**

```java
  private E nonNull(E element) {
    if (element == null) {
      throw new NullPointerException("Element must be non-null");
    }
    return element;
  }

  @Override
  public E set(int index, E element) {
    return delegate.set(index, nonNull(element));
  }

  @Override
  public void add(int index, E element) {
    delegate.add(index, nonNull(element));
  }
```

**With:**

```java
  @Override
  public E set(int index, E element) {
    return delegate.set(index, element);
  }

  @Override
  public void add(int index, E element) {
    delegate.add(index, element);
  }
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `gson/src/main/java/com/google/gson/internal/NonNullElementWrapperList.java` | 106 → 100 | 17 → 16 | 1.24 → 1.19 | 5 → 4 | 0 → 0 |

## Diff

```diff
diff --git a/gson/src/main/java/com/google/gson/internal/NonNullElementWrapperList.java b/gson/src/main/java/com/google/gson/internal/NonNullElementWrapperList.java
index 45a9c29..9537c2e 100644
--- a/gson/src/main/java/com/google/gson/internal/NonNullElementWrapperList.java
+++ b/gson/src/main/java/com/google/gson/internal/NonNullElementWrapperList.java
@@ -47,21 +47,14 @@ public class NonNullElementWrapperList<E> extends AbstractList<E> implements Ran
     return delegate.size();
   }
 
-  private E nonNull(E element) {
-    if (element == null) {
-      throw new NullPointerException("Element must be non-null");
-    }
-    return element;
-  }
-
   @Override
   public E set(int index, E element) {
-    return delegate.set(index, nonNull(element));
+    return delegate.set(index, element);
   }
 
   @Override
   public void add(int index, E element) {
-    delegate.add(index, nonNull(element));
+    delegate.add(index, element);
   }
 
   @Override

```
