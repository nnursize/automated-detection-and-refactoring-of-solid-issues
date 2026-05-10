# Refactor DIP-011 (DIP): Direct instantiation of concrete IOContext

**Status:** `applied_unverified`  
**Branch:** `refactor/DIP-011` -> `main`  
**Head commit:** `a22e116b998cb3a799f97bced0e55be280b01767`  
**LLM finish:** `FinishReason.STOP` (prompt 14320, completion 1053)  

## Detected issue

- **File**: `src/main/java/tools/jackson/core/TokenStreamFactory.java`
- **Entity**: `TokenStreamFactory._createContext` (method)
- **Lines (at detection time)**: L1310–L1340
- **Severity**: medium
- **Confidence**: detected by 3 scan(s)

**Description.** Direct instantiation of concrete IOContext

**Reasoning.** The high-level TokenStreamFactory directly instantiates the concrete IOContext class. According to DIP, high-level modules should depend on abstractions, and dependencies should be injected rather than hard-coded through direct instantiation.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 3
- **Files created** (2): `src/main/java/tools/jackson/core/io/DefaultIOContextFactory.java`, `src/main/java/tools/jackson/core/io/IOContextFactory.java`
- **Files modified** (1): `src/main/java/tools/jackson/core/TokenStreamFactory.java`

**Summary.** Introduce IOContextFactory to decouple TokenStreamFactory from concrete IOContext instantiation

**Rationale.** The TokenStreamFactory was directly instantiating IOContext, violating the Dependency Inversion Principle. By introducing an IOContextFactory interface and a default implementation, we allow for abstraction of the context creation process.

## Changes overview

_3 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `src/main/java/tools/jackson/core/TokenStreamFactory.java` (23-line block → 23-line replacement)

**Replaces:**

```java
    protected IOContext _createContext(ContentReference contentRef, boolean resourceManaged,
            JsonEncoding enc)
    {
        BufferRecycler br = null;
        Object content = (contentRef == null) ? null : contentRef.getRawContent();
        // 18-Jan-2024, tatu: [core#1195] Let's see if we can reuse already allocated recycler
        //   (is the case when SegmentedStringWriter / ByteArrayBuilder passed)
        if (content instanceof BufferRecycler.Gettable) {
            br = ((BufferRecycler.Gettable) content).bufferRecycler();
        }
        boolean recyclerExternal = (br != null);
        if (!recyclerExternal) {
            br = _getBufferRecycler();
        }
        IOContext ctxt = new IOContext(_streamReadConstraints, _streamWriteConstraints,
                _errorReportConfiguration,
                br, contentRef,
                resourceManaged, enc);
        if (recyclerExternal) {
            ctxt.markBufferRecyclerReleased();
        }
        return ctxt;
    }
```

**With:**

```java
    protected IOContext _createContext(ContentReference contentRef, boolean resourceManaged,
            JsonEncoding enc)
    {
        BufferRecycler br = null;
        Object content = (contentRef == null) ? null : contentRef.getRawContent();
        // 18-Jan-2024, tatu: [core#1195] Let's see if we can reuse already allocated recycler
        //   (is the case when SegmentedStringWriter / ByteArrayBuilder passed)
        if (content instanceof BufferRecycler.Gettable) {
            br = ((BufferRecycler.Gettable) content).bufferRecycler();
        }
        boolean recyclerExternal = (br != null);
        if (!recyclerExternal) {
            br = _getBufferRecycler();
        }
        IOContext ctxt = new DefaultIOContextFactory().createContext(_streamReadConstraints, _streamWriteConstraints,
                _errorReportConfiguration,
                br, contentRef,
                resourceManaged, enc);
        if (recyclerExternal) {
            ctxt.markBufferRecyclerReleased();
        }
        return ctxt;
    }
```

### 2. CREATE `src/main/java/tools/jackson/core/io/IOContextFactory.java` (14 line(s))

```java
package tools.jackson.core.io;

import tools.jackson.core.JsonEncoding;
import tools.jackson.core.ErrorReportConfiguration;
import tools.jackson.core.StreamReadConstraints;
import tools.jackson.core.StreamWriteConstraints;
import tools.jackson.core.util.BufferRecycler;

public interface IOContextFactory {
    IOContext createContext(StreamReadConstraints src, StreamWriteConstraints swc,
                            ErrorReportConfiguration erc,
                            BufferRecycler br, ContentReference contentRef,
                            boolean resourceManaged, JsonEncoding enc);
}
```

### 3. CREATE `src/main/java/tools/jackson/core/io/DefaultIOContextFactory.java` (17 line(s))

```java
package tools.jackson.core.io;

import tools.jackson.core.JsonEncoding;
import tools.jackson.core.ErrorReportConfiguration;
import tools.jackson.core.StreamReadConstraints;
import tools.jackson.core.StreamWriteConstraints;
import tools.jackson.core.util.BufferRecycler;

public class DefaultIOContextFactory implements IOContextFactory {
    @Override
    public IOContext createContext(StreamReadConstraints src, StreamWriteConstraints swc,
                                   ErrorReportConfiguration erc,
                                   BufferRecycler br, ContentReference contentRef,
                                   boolean resourceManaged, JsonEncoding enc) {
        return new IOContext(src, swc, erc, br, contentRef, resourceManaged, enc);
    }
}
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/main/java/tools/jackson/core/TokenStreamFactory.java` | 1276 → 1276 | 51 → 51 | 4.41 → 4.41 | 175 → 175 | 0 → 0 |
| `src/main/java/tools/jackson/core/io/DefaultIOContextFactory.java` | - → 15 | - → 1 | - → 1 | - → 1 | - → 0 |
| `src/main/java/tools/jackson/core/io/IOContextFactory.java` | - → 12 | - → 0 | - → 1 | - → 1 | - → 0 |

## Diff

```diff
diff --git a/src/main/java/tools/jackson/core/TokenStreamFactory.java b/src/main/java/tools/jackson/core/TokenStreamFactory.java
index db6e706..b307069 100644
--- a/src/main/java/tools/jackson/core/TokenStreamFactory.java
+++ b/src/main/java/tools/jackson/core/TokenStreamFactory.java
@@ -1230,7 +1230,7 @@ public abstract class TokenStreamFactory
         if (!recyclerExternal) {
             br = _getBufferRecycler();
         }
-        IOContext ctxt = new IOContext(_streamReadConstraints, _streamWriteConstraints,
+        IOContext ctxt = new DefaultIOContextFactory().createContext(_streamReadConstraints, _streamWriteConstraints,
                 _errorReportConfiguration,
                 br, contentRef,
                 resourceManaged, enc);
diff --git a/src/main/java/tools/jackson/core/io/IOContextFactory.java b/src/main/java/tools/jackson/core/io/IOContextFactory.java
new file mode 100644
index 0000000..0000000
--- /dev/null
+++ b/src/main/java/tools/jackson/core/io/IOContextFactory.java
@@ -0,0 +1,14 @@
+package tools.jackson.core.io;
+
+import tools.jackson.core.JsonEncoding;
+import tools.jackson.core.ErrorReportConfiguration;
+import tools.jackson.core.StreamReadConstraints;
+import tools.jackson.core.StreamWriteConstraints;
+import tools.jackson.core.util.BufferRecycler;
+
+public interface IOContextFactory {
+    IOContext createContext(StreamReadConstraints src, StreamWriteConstraints swc,
+                            ErrorReportConfiguration erc,
+                            BufferRecycler br, ContentReference contentRef,
+                            boolean resourceManaged, JsonEncoding enc);
+}
\ No newline at end of file
diff --git a/src/main/java/tools/jackson/core/io/DefaultIOContextFactory.java b/src/main/java/tools/jackson/core/io/DefaultIOContextFactory.java
new file mode 100644
index 0000000..0000000
--- /dev/null
+++ b/src/main/java/tools/jackson/core/io/DefaultIOContextFactory.java
@@ -0,0 +1,17 @@
+package tools.jackson.core.io;
+
+import tools.jackson.core.JsonEncoding;
+import tools.jackson.core.ErrorReportConfiguration;
+import tools.jackson.core.StreamReadConstraints;
+import tools.jackson.core.StreamWriteConstraints;
+import tools.jackson.core.util.BufferRecycler;
+
+public class DefaultIOContextFactory implements IOContextFactory {
+    @Override
+    public IOContext createContext(StreamReadConstraints src, StreamWriteConstraints swc,
+                                   ErrorReportConfiguration erc,
+                                   BufferRecycler br, ContentReference contentRef,
+                                   boolean resourceManaged, JsonEncoding enc) {
+        return new IOContext(src, swc, erc, br, contentRef, resourceManaged, enc);
+    }
+}
\ No newline at end of file

```
