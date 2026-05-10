# Refactor SRP-023 (SRP): Factory directly manages opening I/O streams from a File, mixing factory crea...

**Status:** `applied_unverified`  
**Branch:** `refactor/SRP-023` -> `main`  
**Head commit:** `cac9df339925a5da8321d916d8b9bbcb9ad732dc`  
**LLM finish:** `FinishReason.STOP` (prompt 14324, completion 1552)  

## Detected issue

- **File**: `src/main/java/tools/jackson/core/TokenStreamFactory.java`
- **Entity**: `TokenStreamFactory._fileInputStream` (method)
- **Lines (at detection time)**: L1330–L1338
- **Severity**: medium
- **Confidence**: detected by 2 scan(s)

**Description.** Factory directly manages opening I/O streams from a File, mixing factory creation with I/O resource management.

**Reasoning.** A `TokenStreamFactory`'s primary responsibility is to configure and create `JsonParser` and `JsonGenerator` instances. The `_fileInputStream` method, however, directly handles the logic for opening an `InputStream` from a `File`. This is a responsibility related to I/O resource management, which is distinct from the factory's core role. This I/O logic could be delegated to a separate utility class.

## Fix logic

- **Model**: `gemini-2.5-flash` (temperature 0.2)
- **Patch blocks**: 3
- **Files created** (1): `src/main/java/tools/jackson/core/io/FileStreamUtil.java`
- **Files modified** (1): `src/main/java/tools/jackson/core/TokenStreamFactory.java`

**Summary.** Delegates file and path I/O stream creation to a new utility class, `FileStreamUtil`.

**Rationale.** The `TokenStreamFactory`'s primary responsibility is to configure and create `JsonParser` and `JsonGenerator` instances. The original `_fileInputStream`, `_pathInputStream`, `_fileOutputStream`, and `_pathOutputStream` methods directly handled the logic for opening I/O streams from `File` and `Path` objects, which is an I/O resource management concern. By moving this logic to a new dedicated utility class, `FileStreamUtil` in the `tools.jackson.core.io` package, we separate the concern of stream creation from the factory's core responsibility. The `TokenStreamFactory` now delegates these I/O operations and retains the responsibility of wrapping `IOException` into `JacksonException`, which is appropriate for its domain.

## Changes overview

_3 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `src/main/java/tools/jackson/core/TokenStreamFactory.java` (4-line block → 5-line replacement)

**Replaces:**

```java
import java.nio.file.Path;
import java.util.List;
import java.util.Locale;
import java.util.Objects;
```

**With:**

```java
import java.nio.file.Path;
import tools.jackson.core.io.FileStreamUtil;
import java.util.List;
import java.util.Locale;
import java.util.Objects;
```

### 2. EDIT `src/main/java/tools/jackson/core/TokenStreamFactory.java` (45-line block → 45-line replacement)

**Replaces:**

```java
    protected InputStream _fileInputStream(File f) throws JacksonException
    {
        try {
            return new FileInputStream(f);
        } catch (IOException e) {
            throw _wrapIOFailure(e);
        }
    }

    protected InputStream _pathInputStream(Path p) throws JacksonException
    {
        try {
            return Files.newInputStream(p);
        } catch (IOException e) {
            throw _wrapIOFailure(e);
        }
    }

    /**
     * Helper methods used for constructing an {@link OutputStream} for
     * generator to use, when target is to be written into given {@link File}.
     *
     * @param f File to open stream for
     *
     * @return {@link OutputStream} constructed
     *
     * @throws JacksonException If there is a problem opening the stream
     */
    protected OutputStream _fileOutputStream(File f) throws JacksonException
    {
        try {
            return new FileOutputStream(f);
        } catch (IOException e) {
            throw _wrapIOFailure(e);
        }
    }

    protected OutputStream _pathOutputStream(Path p) throws JacksonException
    {
        try {
            return Files.newOutputStream(p);
        } catch (IOException e) {
            throw _wrapIOFailure(e);
        }
    }
```

**With:**

```java
    protected InputStream _fileInputStream(File f) throws JacksonException
    {
        try {
            return FileStreamUtil.fileInputStream(f);
        } catch (IOException e) {
            throw _wrapIOFailure(e);
        }
    }

    protected InputStream _pathInputStream(Path p) throws JacksonException
    {
        try {
            return FileStreamUtil.pathInputStream(p);
        } catch (IOException e) {
            throw _wrapIOFailure(e);
        }
    }

    /**
     * Helper methods used for constructing an {@link OutputStream} for
     * generator to use, when target is to be written into given {@link File}.
     *
     * @param f File to open stream for
     *
     * @return {@link OutputStream} constructed
     *
     * @throws JacksonException If there is a problem opening the stream
     */
    protected OutputStream _fileOutputStream(File f) throws JacksonException
    {
        try {
            return FileStreamUtil.fileOutputStream(f);
        } catch (IOException e) {
            throw _wrapIOFailure(e);
        }
    }

    protected OutputStream _pathOutputStream(Path p) throws JacksonException
    {
        try {
            return FileStreamUtil.pathOutputStream(p);
        } catch (IOException e) {
            throw _wrapIOFailure(e);
        }
    }
```

### 3. CREATE `src/main/java/tools/jackson/core/io/FileStreamUtil.java` (66 line(s))

```java
package tools.jackson.core.io;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.file.Files;
import java.nio.file.Path;

/**
 * Utility class for creating I/O streams from {@link File} and {@link Path} objects.
 * This class encapsulates the direct I/O resource opening logic, separating it
 * from factory classes like {@code TokenStreamFactory}.
 *
 * @since 3.0
 */
public final class FileStreamUtil {

    private FileStreamUtil() { }

    /**
     * Creates a new {@link FileInputStream} for the given {@link File}.
     *
     * @param f File to open stream for
     * @return {@link InputStream} constructed
     * @throws IOException If there is a problem opening the stream
     */
    public static InputStream fileInputStream(File f) throws IOException {
        return new FileInputStream(f);
    }

    /**
     * Creates a new {@link InputStream} for the given {@link Path}.
     *
     * @param p Path to open stream for
     * @return {@link InputStream} constructed
     * @throws IOException If there is a problem opening the stream
     */
    public static InputStream pathInputStream(Path p) throws IOException {
        return Files.newInputStream(p);
    }

    /**
     * Creates a new {@link FileOutputStream} for the given {@link File}.
     *
     * @param f File to open stream for
     * @return {@link OutputStream} constructed
     * @throws IOException If there is a problem opening the stream
     */
    public static OutputStream fileOutputStream(File f) throws IOException {
        return new FileOutputStream(f);
    }

    /**
     * Creates a new {@link OutputStream} for the given {@link Path}.
     *
     * @param p Path to open stream for
     * @return {@link OutputStream} constructed
... (6 more line(s) truncated)
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/main/java/tools/jackson/core/TokenStreamFactory.java` | 1275 → 1276 | 51 → 51 | 4.41 → 4.41 | 175 → 175 | 0 → 0 |
| `src/main/java/tools/jackson/core/io/FileStreamUtil.java` | - → 59 | - → 4 | - → 3.25 | - → 10 | - → 0 |

## Diff

```diff
diff --git a/src/main/java/tools/jackson/core/TokenStreamFactory.java b/src/main/java/tools/jackson/core/TokenStreamFactory.java
index 2f33b7d..db6e706 100644
--- a/src/main/java/tools/jackson/core/TokenStreamFactory.java
+++ b/src/main/java/tools/jackson/core/TokenStreamFactory.java
@@ -8,6 +8,7 @@ import java.io.*;
 import java.net.URL;
 import java.nio.file.Files;
 import java.nio.file.Path;
+import tools.jackson.core.io.FileStreamUtil;
 import java.util.List;
 import java.util.Locale;
 import java.util.Objects;
@@ -1303,7 +1304,7 @@ public abstract class TokenStreamFactory
     protected InputStream _fileInputStream(File f) throws JacksonException
     {
         try {
-            return new FileInputStream(f);
+            return FileStreamUtil.fileInputStream(f);
         } catch (IOException e) {
             throw _wrapIOFailure(e);
         }
@@ -1312,7 +1313,7 @@ public abstract class TokenStreamFactory
     protected InputStream _pathInputStream(Path p) throws JacksonException
     {
         try {
-            return Files.newInputStream(p);
+            return FileStreamUtil.pathInputStream(p);
         } catch (IOException e) {
             throw _wrapIOFailure(e);
         }
@@ -1331,7 +1332,7 @@ public abstract class TokenStreamFactory
     protected OutputStream _fileOutputStream(File f) throws JacksonException
     {
         try {
-            return new FileOutputStream(f);
+            return FileStreamUtil.fileOutputStream(f);
         } catch (IOException e) {
             throw _wrapIOFailure(e);
         }
@@ -1340,7 +1341,7 @@ public abstract class TokenStreamFactory
     protected OutputStream _pathOutputStream(Path p) throws JacksonException
     {
         try {
-            return Files.newOutputStream(p);
+            return FileStreamUtil.pathOutputStream(p);
         } catch (IOException e) {
             throw _wrapIOFailure(e);
         }
diff --git a/src/main/java/tools/jackson/core/io/FileStreamUtil.java b/src/main/java/tools/jackson/core/io/FileStreamUtil.java
new file mode 100644
index 0000000..0000000
--- /dev/null
+++ b/src/main/java/tools/jackson/core/io/FileStreamUtil.java
@@ -0,0 +1,66 @@
+package tools.jackson.core.io;
+
+import java.io.File;
+import java.io.FileInputStream;
+import java.io.FileOutputStream;
+import java.io.IOException;
+import java.io.InputStream;
+import java.io.OutputStream;
+import java.nio.file.Files;
+import java.nio.file.Path;
+
+/**
+ * Utility class for creating I/O streams from {@link File} and {@link Path} objects.
+ * This class encapsulates the direct I/O resource opening logic, separating it
+ * from factory classes like {@code TokenStreamFactory}.
+ *
+ * @since 3.0
+ */
+public final class FileStreamUtil {
+
+    private FileStreamUtil() { }
+
+    /**
+     * Creates a new {@link FileInputStream} for the given {@link File}.
+     *
+     * @param f File to open stream for
+     * @return {@link InputStream} constructed
+     * @throws IOException If there is a problem opening the stream
+     */
+    public static InputStream fileInputStream(File f) throws IOException {
+        return new FileInputStream(f);
+    }
+
+    /**
+     * Creates a new {@link InputStream} for the given {@link Path}.
+     *
+     * @param p Path to open stream for
+     * @return {@link InputStream} constructed
+     * @throws IOException If there is a problem opening the stream
+     */
+    public static InputStream pathInputStream(Path p) throws IOException {
+        return Files.newInputStream(p);
+    }
+
+    /**
+     * Creates a new {@link FileOutputStream} for the given {@link File}.
+     *
+     * @param f File to open stream for
+     * @return {@link OutputStream} constructed
+     * @throws IOException If there is a problem opening the stream
+     */
+    public static OutputStream fileOutputStream(File f) throws IOException {
+        return new FileOutputStream(f);
+    }
+
+    /**
+     * Creates a new {@link OutputStream} for the given {@link Path}.
+     *
+     * @param p Path to open stream for
+     * @return {@link OutputStream} constructed
+     * @throws IOException If there is a problem opening the stream
+     */
+    public static OutputStream pathOutputStream(Path p) throws IOException {
+        return Files.newOutputStream(p);
+    }
+}
\ No newline at end of file

```
