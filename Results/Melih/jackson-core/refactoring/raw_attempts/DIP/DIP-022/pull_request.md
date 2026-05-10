# Refactor DIP-022 (DIP): Direct instantiation of concrete TextBuffer implementations.

**Status:** `applied_unverified`  
**Branch:** `refactor/DIP-022` -> `main`  
**Head commit:** `1f88f255084094074ecf93ddbee18e92dd16b388`  
**LLM finish:** `FinishReason.STOP` (prompt 5080, completion 608)  

## Detected issue

- **File**: `src/main/java/tools/jackson/core/io/IOContext.java`
- **Entity**: `IOContext.constructTextBuffer` (class)
- **Lines (at detection time)**: L214–L221
- **Severity**: high
- **Confidence**: detected by 3 scan(s)

**Description.** Direct instantiation of concrete TextBuffer implementations.

**Reasoning.** The constructTextBuffer and constructReadConstrainedTextBuffer methods directly instantiate TextBuffer and ReadConstrainedTextBuffer. This prevents the inversion of control where alternative buffer strategies could be injected into the context.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 2
- **Files created** (1): `src/main/java/tools/jackson/core/io/TextBufferFactory.java`
- **Files modified** (1): `src/main/java/tools/jackson/core/io/IOContext.java`

**Summary.** Introduce a TextBufferFactory to decouple IOContext from concrete TextBuffer implementations.

**Rationale.** The IOContext class was directly instantiating TextBuffer and ReadConstrainedTextBuffer. By introducing a factory interface and a default implementation, we allow the creation logic to be abstracted, adhering to the Dependency Inversion Principle.

## Changes overview

_2 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `src/main/java/tools/jackson/core/io/IOContext.java` (13-line block → 13-line replacement)

**Replaces:**

```java
    /*
    /**********************************************************************
    /* Public API, buffer management
    /**********************************************************************
     */

    public TextBuffer constructTextBuffer() {
        return new TextBuffer(_bufferRecycler);
    }

    public TextBuffer constructReadConstrainedTextBuffer() {
        return new ReadConstrainedTextBuffer(_streamReadConstraints, _bufferRecycler);
    }
```

**With:**

```java
    /*
    /**********************************************************************
    /* Public API, buffer management
    /**********************************************************************
     */

    public TextBuffer constructTextBuffer() {
        return TextBufferFactory.DEFAULT.constructTextBuffer(_bufferRecycler);
    }

    public TextBuffer constructReadConstrainedTextBuffer() {
        return TextBufferFactory.DEFAULT.constructReadConstrainedTextBuffer(_streamReadConstraints, _bufferRecycler);
    }
```

### 2. CREATE `src/main/java/tools/jackson/core/io/TextBufferFactory.java` (26 line(s))

```java
package tools.jackson.core.io;

import tools.jackson.core.StreamReadConstraints;
import tools.jackson.core.util.BufferRecycler;
import tools.jackson.core.util.ReadConstrainedTextBuffer;
import tools.jackson.core.util.TextBuffer;

/**
 * Factory for creating {@link TextBuffer} instances.
 */
public interface TextBufferFactory {
    TextBuffer constructTextBuffer(BufferRecycler recycler);
    TextBuffer constructReadConstrainedTextBuffer(StreamReadConstraints src, BufferRecycler recycler);

    TextBufferFactory DEFAULT = new TextBufferFactory() {
        @Override
        public TextBuffer constructTextBuffer(BufferRecycler recycler) {
            return new TextBuffer(recycler);
        }

        @Override
        public TextBuffer constructReadConstrainedTextBuffer(StreamReadConstraints src, BufferRecycler recycler) {
            return new ReadConstrainedTextBuffer(src, recycler);
        }
    };
}
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/main/java/tools/jackson/core/io/IOContext.java` | 351 → 351 | 32 → 32 | 2.66 → 2.66 | 54 → 54 | 0 → 0 |
| `src/main/java/tools/jackson/core/io/TextBufferFactory.java` | - → 22 | - → 2 | - → 1.5 | - → 2 | - → 0 |

## Diff

```diff
diff --git a/src/main/java/tools/jackson/core/io/IOContext.java b/src/main/java/tools/jackson/core/io/IOContext.java
index 9304ec4..396abe6 100644
--- a/src/main/java/tools/jackson/core/io/IOContext.java
+++ b/src/main/java/tools/jackson/core/io/IOContext.java
@@ -213,11 +213,11 @@ public class IOContext implements AutoCloseable
      */
 
     public TextBuffer constructTextBuffer() {
-        return new TextBuffer(_bufferRecycler);
+        return TextBufferFactory.DEFAULT.constructTextBuffer(_bufferRecycler);
     }
 
     public TextBuffer constructReadConstrainedTextBuffer() {
-        return new ReadConstrainedTextBuffer(_streamReadConstraints, _bufferRecycler);
+        return TextBufferFactory.DEFAULT.constructReadConstrainedTextBuffer(_streamReadConstraints, _bufferRecycler);
     }
 
     /**
diff --git a/src/main/java/tools/jackson/core/io/TextBufferFactory.java b/src/main/java/tools/jackson/core/io/TextBufferFactory.java
new file mode 100644
index 0000000..0000000
--- /dev/null
+++ b/src/main/java/tools/jackson/core/io/TextBufferFactory.java
@@ -0,0 +1,26 @@
+package tools.jackson.core.io;
+
+import tools.jackson.core.StreamReadConstraints;
+import tools.jackson.core.util.BufferRecycler;
+import tools.jackson.core.util.ReadConstrainedTextBuffer;
+import tools.jackson.core.util.TextBuffer;
+
+/**
+ * Factory for creating {@link TextBuffer} instances.
+ */
+public interface TextBufferFactory {
+    TextBuffer constructTextBuffer(BufferRecycler recycler);
+    TextBuffer constructReadConstrainedTextBuffer(StreamReadConstraints src, BufferRecycler recycler);
+
+    TextBufferFactory DEFAULT = new TextBufferFactory() {
+        @Override
+        public TextBuffer constructTextBuffer(BufferRecycler recycler) {
+            return new TextBuffer(recycler);
+        }
+
+        @Override
+        public TextBuffer constructReadConstrainedTextBuffer(StreamReadConstraints src, BufferRecycler recycler) {
+            return new ReadConstrainedTextBuffer(src, recycler);
+        }
+    };
+}
\ No newline at end of file

```
