# Refactor SRP-022 (SRP): Factory directly manages opening I/O streams from a URL, mixing factory creat...

**Status:** `applied_unverified`  
**Branch:** `refactor/SRP-022` -> `main`  
**Head commit:** `0ba54c84a1992c712b13299318a7885b1bd303ab`  
**LLM finish:** `FinishReason.STOP` (prompt 14536, completion 1062)  

## Detected issue

- **File**: `src/main/java/tools/jackson/core/TokenStreamFactory.java`
- **Entity**: `TokenStreamFactory._optimizedStreamFromURL` (method)
- **Lines (at detection time)**: L1300–L1328
- **Severity**: medium
- **Confidence**: detected by 3 scan(s)

**Description.** Factory directly manages opening I/O streams from a URL, mixing factory creation with I/O resource management.

**Reasoning.** A `TokenStreamFactory`'s primary responsibility is to configure and create `JsonParser` and `JsonGenerator` instances. The `_optimizedStreamFromURL` method, however, directly handles the logic for opening an `InputStream` from a `URL`. This is a responsibility related to I/O resource management, which is distinct from the factory's core role. This I/O logic could be delegated to a separate utility class.

## Fix logic

- **Model**: `gemini-2.5-flash` (temperature 0.2)
- **Patch blocks**: 2
- **Files created** (1): `src/main/java/tools/jackson/core/io/URLResourceUtil.java`
- **Files modified** (1): `src/main/java/tools/jackson/core/TokenStreamFactory.java`

**Summary.** Extract URL stream opening logic into a dedicated utility class to improve SRP.

**Rationale.** The `_optimizedStreamFromURL` method in `TokenStreamFactory` was responsible for both configuring stream factories and managing I/O resources from a URL. This violates the Single Responsibility Principle. By moving the URL stream opening logic to a new utility class `URLResourceUtil` in the `tools.jackson.core.io` package, `TokenStreamFactory` can now delegate this I/O responsibility. The original method now simply calls the utility and handles the `IOException` wrapping, maintaining its existing public API and behavior.

## Changes overview

_2 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `src/main/java/tools/jackson/core/TokenStreamFactory.java` (29-line block → 8-line replacement)

**Replaces:**

```java
    @Deprecated // since 3.0
    protected InputStream _optimizedStreamFromURL(URL url) throws JacksonException {
        if ("file".equals(url.getProtocol())) {
            /* Cannot do this if the path refers
             * to a network drive on windows. This fixes the problem;
             * might not be needed on all platforms (NFS?), but should not
             * matter a lot: performance penalty of extra wrapping is more
             * relevant when accessing local file system.
             */
            String host = url.getHost();
            if (host == null || host.length() == 0) {
                // [core#48]: Let's try to avoid probs with URL encoded stuff
                String path = url.getPath();
                if (path.indexOf('%') < 0) {
                    try {
                        return new FileInputStream(url.getPath());
                    } catch (IOException e) {
                        throw _wrapIOFailure(e);
                    }
                }
                // otherwise, let's fall through and let URL decoder do its magic
            }
        }
        try {
            return url.openStream();
        } catch (IOException e) {
            throw _wrapIOFailure(e);
        }
    }
```

**With:**

```java
    @Deprecated // since 3.0
    protected InputStream _optimizedStreamFromURL(URL url) throws JacksonException {
        try {
            return URLResourceUtil.optimizedStreamFromURL(url);
        } catch (IOException e) {
            throw _wrapIOFailure(e);
        }
    }
```

### 2. CREATE `src/main/java/tools/jackson/core/io/URLResourceUtil.java` (53 line(s))

```java
/* Jackson JSON-processor.
 *
 * Copyright (c) 2007- Tatu Saloranta, tatu.saloranta@iki.fi
 */
package tools.jackson.core.io;

import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.net.URL;

/**
 * Internal utility class used by {@link tools.jackson.core.TokenStreamFactory}
 * for handling URL-based input stream creation.
 *
 * @since 3.0.1
 */
public final class URLResourceUtil {

    private URLResourceUtil() { }

    /**
     * Helper method used for constructing an optimal stream for
     * parsers to use, when input is to be read from an URL.
     * This helps when reading file content via URL.
     *
     * @param url Source to read content to parse from
     *
     * @return InputStream constructed for given {@link URL}
     *
     * @throws IOException If there is a problem accessing content from specified {@link URL}
     */
    public static InputStream optimizedStreamFromURL(URL url) throws IOException {
        if ("file".equals(url.getProtocol())) {
            /* Cannot do this if the path refers
             * to a network drive on windows. This fixes the problem;
             * might not be needed on all platforms (NFS?), but should not
             * matter a lot: performance penalty of extra wrapping is more
             * relevant when accessing local file system.
             */
            String host = url.getHost();
            if (host == null || host.length() == 0) {
                // [core#48]: Let's try to avoid probs with URL encoded stuff
                String path = url.getPath();
                if (path.indexOf('%') < 0) {
                    return new FileInputStream(url.getPath());
                }
                // otherwise, let's fall through and let URL decoder do its magic
            }
        }
        return url.openStream();
    }
}
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/main/java/tools/jackson/core/TokenStreamFactory.java` | 1294 → 1275 | 51 → 51 | 4.59 → 4.41 | 184 → 175 | 0 → 0 |
| `src/main/java/tools/jackson/core/io/URLResourceUtil.java` | - → 47 | - → 1 | - → 15 | - → 15 | - → 0 |

## Diff

```diff
diff --git a/src/main/java/tools/jackson/core/TokenStreamFactory.java b/src/main/java/tools/jackson/core/TokenStreamFactory.java
index b6480bd..2f33b7d 100644
--- a/src/main/java/tools/jackson/core/TokenStreamFactory.java
+++ b/src/main/java/tools/jackson/core/TokenStreamFactory.java
@@ -1283,29 +1283,8 @@ public abstract class TokenStreamFactory
      */
     @Deprecated // since 3.0
     protected InputStream _optimizedStreamFromURL(URL url) throws JacksonException {
-        if ("file".equals(url.getProtocol())) {
-            /* Cannot do this if the path refers
-             * to a network drive on windows. This fixes the problem;
-             * might not be needed on all platforms (NFS?), but should not
-             * matter a lot: performance penalty of extra wrapping is more
-             * relevant when accessing local file system.
-             */
-            String host = url.getHost();
-            if (host == null || host.length() == 0) {
-                // [core#48]: Let's try to avoid probs with URL encoded stuff
-                String path = url.getPath();
-                if (path.indexOf('%') < 0) {
-                    try {
-                        return new FileInputStream(url.getPath());
-                    } catch (IOException e) {
-                        throw _wrapIOFailure(e);
-                    }
-                }
-                // otherwise, let's fall through and let URL decoder do its magic
-            }
-        }
         try {
-            return url.openStream();
+            return URLResourceUtil.optimizedStreamFromURL(url);
         } catch (IOException e) {
             throw _wrapIOFailure(e);
         }
diff --git a/src/main/java/tools/jackson/core/io/URLResourceUtil.java b/src/main/java/tools/jackson/core/io/URLResourceUtil.java
new file mode 100644
index 0000000..0000000
--- /dev/null
+++ b/src/main/java/tools/jackson/core/io/URLResourceUtil.java
@@ -0,0 +1,53 @@
+/* Jackson JSON-processor.
+ *
+ * Copyright (c) 2007- Tatu Saloranta, tatu.saloranta@iki.fi
+ */
+package tools.jackson.core.io;
+
+import java.io.FileInputStream;
+import java.io.IOException;
+import java.io.InputStream;
+import java.net.URL;
+
+/**
+ * Internal utility class used by {@link tools.jackson.core.TokenStreamFactory}
+ * for handling URL-based input stream creation.
+ *
+ * @since 3.0.1
+ */
+public final class URLResourceUtil {
+
+    private URLResourceUtil() { }
+
+    /**
+     * Helper method used for constructing an optimal stream for
+     * parsers to use, when input is to be read from an URL.
+     * This helps when reading file content via URL.
+     *
+     * @param url Source to read content to parse from
+     *
+     * @return InputStream constructed for given {@link URL}
+     *
+     * @throws IOException If there is a problem accessing content from specified {@link URL}
+     */
+    public static InputStream optimizedStreamFromURL(URL url) throws IOException {
+        if ("file".equals(url.getProtocol())) {
+            /* Cannot do this if the path refers
+             * to a network drive on windows. This fixes the problem;
+             * might not be needed on all platforms (NFS?), but should not
+             * matter a lot: performance penalty of extra wrapping is more
+             * relevant when accessing local file system.
+             */
+            String host = url.getHost();
+            if (host == null || host.length() == 0) {
+                // [core#48]: Let's try to avoid probs with URL encoded stuff
+                String path = url.getPath();
+                if (path.indexOf('%') < 0) {
+                    return new FileInputStream(url.getPath());
+                }
+                // otherwise, let's fall through and let URL decoder do its magic
+            }
+        }
+        return url.openStream();
+    }
+}
\ No newline at end of file

```
