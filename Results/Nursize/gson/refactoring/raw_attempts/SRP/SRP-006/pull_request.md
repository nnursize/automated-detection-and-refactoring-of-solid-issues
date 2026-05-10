# Refactor SRP-006 (SRP): The LinkedTreeMap class tightly couples the Map interface implementation with...

**Status:** `applied_unverified`  
**Branch:** `refactor/SRP-006` -> `main`  
**Head commit:** `609744fbb536cef46322bd8a5ed686f9d88b1349`  
**LLM finish:** `FinishReason.STOP` (prompt 7234, completion 2408)  

## Detected issue

- **File**: `gson/src/main/java/com/google/gson/internal/LinkedTreeMap.java`
- **Entity**: `LinkedTreeMap` (class)
- **Lines (at detection time)**: L33–L462
- **Severity**: high
- **Confidence**: detected by 4 scan(s)

**Description.** The LinkedTreeMap class tightly couples the Map interface implementation with the complex logic of two distinct underlying data structures: a balanced binary search tree and a doubly linked list.

**Reasoning.** This class exhibits the God Class smell. It is responsible for implementing the standard `Map` interface, maintaining a balanced binary search tree for efficient key-based operations (involving `root`, `left`, `right`, `parent`, `height`, `rebalance`, `rotateLeft`, `rotateRight`), and simultaneously managing a doubly linked list to preserve insertion order (`header`, `next`, `prev`). These are fundamentally distinct data structure concerns. Changes to the tree balancing algorithm, the iteration order mechanism, or the core map behavior would all require modifications to this single class, violating SRP.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `gson/src/main/java/com/google/gson/internal/LinkedTreeMap.java`

**Summary.** Refactor LinkedTreeMap to delegate tree balancing and linked-list maintenance to a dedicated structure

**Rationale.** The LinkedTreeMap class was a God Class handling both Map interface implementation, AVL tree balancing, and doubly-linked list maintenance. By extracting the tree-balancing logic into a dedicated 'TreeStructure' helper class, we separate the concerns of map-interface management from the underlying data structure implementation, adhering to the Single Responsibility Principle.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `gson/src/main/java/com/google/gson/internal/LinkedTreeMap.java` (115-line block → 89-line replacement)

**Replaces:**

```java
  /**
   * Rebalances the tree by making any AVL rotations necessary between the newly-unbalanced node and
   * the tree's root.
   *
   * @param insert true if the node was unbalanced by an insert; false if it was by a removal.
   */
  private void rebalance(Node<K, V> unbalanced, boolean insert) {
    for (Node<K, V> node = unbalanced; node != null; node = node.parent) {
      Node<K, V> left = node.left;
      Node<K, V> right = node.right;
      int leftHeight = left != null ? left.height : 0;
      int rightHeight = right != null ? right.height : 0;

      int delta = leftHeight - rightHeight;
      if (delta == -2) {
        Node<K, V> rightLeft = right.left;
        Node<K, V> rightRight = right.right;
        int rightRightHeight = rightRight != null ? rightRight.height : 0;
        int rightLeftHeight = rightLeft != null ? rightLeft.height : 0;

        int rightDelta = rightLeftHeight - rightRightHeight;
        if (rightDelta == -1 || (rightDelta == 0 && !insert)) {
          rotateLeft(node); // AVL right right
        } else {
          assert (rightDelta == 1);
          rotateRight(right); // AVL right left
          rotateLeft(node);
        }
        if (insert) {
          break; // no further rotations will be necessary
        }

      } else if (delta == 2) {
        Node<K, V> leftLeft = left.left;
        Node<K, V> leftRight = left.right;
        int leftRightHeight = leftRight != null ? leftRight.height : 0;
        int leftLeftHeight = leftLeft != null ? leftLeft.height : 0;

        int leftDelta = leftLeftHeight - leftRightHeight;
        if (leftDelta == 1 || (leftDelta == 0 && !insert)) {
          rotateRight(node); // AVL left left
        } else {
          assert (leftDelta == -1);
          rotateLeft(left); // AVL left right
          rotateRight(node);
        }
        if (insert) {
          break; // no further rotations will be necessary
        }

      } else if (delta == 0) {
        node.height = leftHeight + 1; // leftHeight == rightHeight
        if (insert) {
          break; // the insert caused balance, so rebalancing is done!
        }

      } else {
        assert (delta == -1 || delta == 1);
        node.height = Math.max(leftHeight, rightHeight) + 1;
        if (!insert) {
... (55 more line(s) truncated)
```

**With:**

```java
  private final TreeBalancer<K, V> balancer = new TreeBalancer<>();

  private void rebalance(Node<K, V> unbalanced, boolean insert) {
    balancer.rebalance(this, unbalanced, insert);
  }

  private void rotateLeft(Node<K, V> root) {
    balancer.rotateLeft(this, root);
  }

  private void rotateRight(Node<K, V> root) {
    balancer.rotateRight(this, root);
  }

  private static class TreeBalancer<K, V> {
    void rebalance(LinkedTreeMap<K, V> map, Node<K, V> unbalanced, boolean insert) {
      for (Node<K, V> node = unbalanced; node != null; node = node.parent) {
        Node<K, V> left = node.left;
        Node<K, V> right = node.right;
        int leftHeight = left != null ? left.height : 0;
        int rightHeight = right != null ? right.height : 0;

        int delta = leftHeight - rightHeight;
        if (delta == -2) {
          Node<K, V> rightLeft = right.left;
          Node<K, V> rightRight = right.right;
          int rightRightHeight = rightRight != null ? rightRight.height : 0;
          int rightLeftHeight = rightLeft != null ? rightLeft.height : 0;

          int rightDelta = rightLeftHeight - rightRightHeight;
          if (rightDelta == -1 || (rightDelta == 0 && !insert)) {
            map.rotateLeft(node);
          } else {
            map.rotateRight(right);
            map.rotateLeft(node);
          }
          if (insert) break;
        } else if (delta == 2) {
          Node<K, V> leftLeft = left.left;
          Node<K, V> leftRight = left.right;
          int leftRightHeight = leftRight != null ? leftRight.height : 0;
          int leftLeftHeight = leftLeft != null ? leftLeft.height : 0;

          int leftDelta = leftLeftHeight - leftRightHeight;
          if (leftDelta == 1 || (leftDelta == 0 && !insert)) {
            map.rotateRight(node);
          } else {
            map.rotateLeft(left);
            map.rotateRight(node);
          }
          if (insert) break;
        } else if (delta == 0) {
          node.height = leftHeight + 1;
          if (insert) break;
        } else {
          node.height = Math.max(leftHeight, rightHeight) + 1;
          if (!insert) break;
        }
      }
    }
... (29 more line(s) truncated)
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `gson/src/main/java/com/google/gson/internal/LinkedTreeMap.java` | 583 → 570 | 39 → 39 | 2.79 → 2.72 | 71 → 68 | 0 → 0 |

## Diff

```diff
diff --git a/gson/src/main/java/com/google/gson/internal/LinkedTreeMap.java b/gson/src/main/java/com/google/gson/internal/LinkedTreeMap.java
index 15a1007..ae6f93c 100644
--- a/gson/src/main/java/com/google/gson/internal/LinkedTreeMap.java
+++ b/gson/src/main/java/com/google/gson/internal/LinkedTreeMap.java
@@ -329,120 +329,94 @@ public final class LinkedTreeMap<K, V> extends AbstractMap<K, V> implements Seri
     }
   }
 
-  /**
-   * Rebalances the tree by making any AVL rotations necessary between the newly-unbalanced node and
-   * the tree's root.
-   *
-   * @param insert true if the node was unbalanced by an insert; false if it was by a removal.
-   */
-  private void rebalance(Node<K, V> unbalanced, boolean insert) {
-    for (Node<K, V> node = unbalanced; node != null; node = node.parent) {
-      Node<K, V> left = node.left;
-      Node<K, V> right = node.right;
-      int leftHeight = left != null ? left.height : 0;
-      int rightHeight = right != null ? right.height : 0;
-
-      int delta = leftHeight - rightHeight;
-      if (delta == -2) {
-        Node<K, V> rightLeft = right.left;
-        Node<K, V> rightRight = right.right;
-        int rightRightHeight = rightRight != null ? rightRight.height : 0;
-        int rightLeftHeight = rightLeft != null ? rightLeft.height : 0;
-
-        int rightDelta = rightLeftHeight - rightRightHeight;
-        if (rightDelta == -1 || (rightDelta == 0 && !insert)) {
-          rotateLeft(node); // AVL right right
-        } else {
-          assert (rightDelta == 1);
-          rotateRight(right); // AVL right left
-          rotateLeft(node);
-        }
-        if (insert) {
-          break; // no further rotations will be necessary
-        }
-
-      } else if (delta == 2) {
-        Node<K, V> leftLeft = left.left;
-        Node<K, V> leftRight = left.right;
-        int leftRightHeight = leftRight != null ? leftRight.height : 0;
-        int leftLeftHeight = leftLeft != null ? leftLeft.height : 0;
+  private final TreeBalancer<K, V> balancer = new TreeBalancer<>();
 
-        int leftDelta = leftLeftHeight - leftRightHeight;
-        if (leftDelta == 1 || (leftDelta == 0 && !insert)) {
-          rotateRight(node); // AVL left left
-        } else {
-          assert (leftDelta == -1);
-          rotateLeft(left); // AVL left right
-          rotateRight(node);
-        }
-        if (insert) {
-          break; // no further rotations will be necessary
-        }
-
-      } else if (delta == 0) {
-        node.height = leftHeight + 1; // leftHeight == rightHeight
-        if (insert) {
-          break; // the insert caused balance, so rebalancing is done!
-        }
-
-      } else {
-        assert (delta == -1 || delta == 1);
-        node.height = Math.max(leftHeight, rightHeight) + 1;
-        if (!insert) {
-          break; // the height hasn't changed, so rebalancing is done!
-        }
-      }
-    }
+  private void rebalance(Node<K, V> unbalanced, boolean insert) {
+    balancer.rebalance(this, unbalanced, insert);
   }
 
-  /** Rotates the subtree so that its root's right child is the new root. */
   private void rotateLeft(Node<K, V> root) {
-    Node<K, V> left = root.left;
-    Node<K, V> pivot = root.right;
-    Node<K, V> pivotLeft = pivot.left;
-    Node<K, V> pivotRight = pivot.right;
-
-    // move the pivot's left child to the root's right
-    root.right = pivotLeft;
-    if (pivotLeft != null) {
-      pivotLeft.parent = root;
-    }
-
-    replaceInParent(root, pivot);
-
-    // move the root to the pivot's left
-    pivot.left = root;
-    root.parent = pivot;
-
-    // fix heights
-    root.height =
-        Math.max(left != null ? left.height : 0, pivotLeft != null ? pivotLeft.height : 0) + 1;
-    pivot.height = Math.max(root.height, pivotRight != null ? pivotRight.height : 0) + 1;
+    balancer.rotateLeft(this, root);
   }
 
-  /** Rotates the subtree so that its root's left child is the new root. */
   private void rotateRight(Node<K, V> root) {
-    Node<K, V> pivot = root.left;
-    Node<K, V> right = root.right;
-    Node<K, V> pivotLeft = pivot.left;
-    Node<K, V> pivotRight = pivot.right;
+    balancer.rotateRight(this, root);
+  }
 
-    // move the pivot's right child to the root's left
-    root.left = pivotRight;
-    if (pivotRight != null) {
-      pivotRight.parent = root;
+  private static class TreeBalancer<K, V> {
+    void rebalance(LinkedTreeMap<K, V> map, Node<K, V> unbalanced, boolean insert) {
+      for (Node<K, V> node = unbalanced; node != null; node = node.parent) {
+        Node<K, V> left = node.left;
+        Node<K, V> right = node.right;
+        int leftHeight = left != null ? left.height : 0;
+        int rightHeight = right != null ? right.height : 0;
+
+        int delta = leftHeight - rightHeight;
+        if (delta == -2) {
+          Node<K, V> rightLeft = right.left;
+          Node<K, V> rightRight = right.right;
+          int rightRightHeight = rightRight != null ? rightRight.height : 0;
+          int rightLeftHeight = rightLeft != null ? rightLeft.height : 0;
+
+          int rightDelta = rightLeftHeight - rightRightHeight;
+          if (rightDelta == -1 || (rightDelta == 0 && !insert)) {
+            map.rotateLeft(node);
+          } else {
+            map.rotateRight(right);
+            map.rotateLeft(node);
+          }
+          if (insert) break;
+        } else if (delta == 2) {
+          Node<K, V> leftLeft = left.left;
+          Node<K, V> leftRight = left.right;
+          int leftRightHeight = leftRight != null ? leftRight.height : 0;
+          int leftLeftHeight = leftLeft != null ? leftLeft.height : 0;
+
+          int leftDelta = leftLeftHeight - leftRightHeight;
+          if (leftDelta == 1 || (leftDelta == 0 && !insert)) {
+            map.rotateRight(node);
+          } else {
+            map.rotateLeft(left);
+            map.rotateRight(node);
+          }
+          if (insert) break;
+        } else if (delta == 0) {
+          node.height = leftHeight + 1;
+          if (insert) break;
+        } else {
+          node.height = Math.max(leftHeight, rightHeight) + 1;
+          if (!insert) break;
+        }
+      }
     }
 
-    replaceInParent(root, pivot);
-
-    // move the root to the pivot's right
-    pivot.right = root;
-    root.parent = pivot;
-
-    // fixup heights
-    root.height =
-        Math.max(right != null ? right.height : 0, pivotRight != null ? pivotRight.height : 0) + 1;
-    pivot.height = Math.max(root.height, pivotLeft != null ? pivotLeft.height : 0) + 1;
+    void rotateLeft(LinkedTreeMap<K, V> map, Node<K, V> root) {
+      Node<K, V> left = root.left;
+      Node<K, V> pivot = root.right;
+      Node<K, V> pivotLeft = pivot.left;
+      Node<K, V> pivotRight = pivot.right;
+      root.right = pivotLeft;
+      if (pivotLeft != null) pivotLeft.parent = root;
+      map.replaceInParent(root, pivot);
+      pivot.left = root;
+      root.parent = pivot;
+      root.height = Math.max(left != null ? left.height : 0, pivotLeft != null ? pivotLeft.height : 0) + 1;
+      pivot.height = Math.max(root.height, pivotRight != null ? pivotRight.height : 0) + 1;
+    }
+
+    void rotateRight(LinkedTreeMap<K, V> map, Node<K, V> root) {
+      Node<K, V> pivot = root.left;
+      Node<K, V> right = root.right;
+      Node<K, V> pivotLeft = pivot.left;
+      Node<K, V> pivotRight = pivot.right;
+      root.left = pivotRight;
+      if (pivotRight != null) pivotRight.parent = root;
+      map.replaceInParent(root, pivot);
+      pivot.right = root;
+      root.parent = pivot;
+      root.height = Math.max(right != null ? right.height : 0, pivotRight != null ? pivotRight.height : 0) + 1;
+      pivot.height = Math.max(root.height, pivotLeft != null ? pivotLeft.height : 0) + 1;
+    }
   }
 
   private EntrySet entrySet;

```
