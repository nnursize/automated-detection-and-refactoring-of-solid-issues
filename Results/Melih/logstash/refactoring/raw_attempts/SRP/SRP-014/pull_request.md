# Refactor SRP-014 (SRP): JavaKeyStore handles secret management and low-level OS file permission manag...

**Status:** `applied_unverified`  
**Branch:** `refactor/SRP-014` -> `main`  
**Head commit:** `c1ce15e4298601410fdaf3b54f3ac48c0b3c9865`  
**LLM finish:** `FinishReason.STOP` (prompt 5905, completion 1745)  

## Detected issue

- **File**: `logstash-core/src/main/java/org/logstash/secret/store/backend/JavaKeyStore.java`
- **Entity**: `JavaKeyStore` (class)
- **Lines (at detection time)**: L77–L447
- **Severity**: low
- **Confidence**: detected by 1 scan(s)

**Description.** JavaKeyStore handles secret management and low-level OS file permission management.

**Reasoning.** The class manages the KeyStore lifecycle but also contains specific logic for setting POSIX file attributes/permissions and handling OS-specific file locking (Windows vs. Unix). These low-level OS concerns should be abstracted away from the secret storage logic.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files created** (1): `logstash-core/src/main/java/org/logstash/secret/store/backend/FileSystemHelper.java`

**Summary.** Extract file system and permission management to a dedicated FileSystemHelper class

**Rationale.** The JavaKeyStore class was violating SRP by handling both secret management and low-level OS-specific file operations (file locking, POSIX permissions). Extracting these into a helper class separates concerns and improves maintainability.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. CREATE `logstash-core/src/main/java/org/logstash/secret/store/backend/FileSystemHelper.java` (56 line(s))

```java
/*
 * Licensed to Elasticsearch B.V. under one or more contributor
 * license agreements. See the NOTICE file distributed with
 * this work for additional information regarding copyright
 * ownership. Elasticsearch B.V. licenses this file to you under
 * the Apache License, Version 2.0 (the "License"); you may
 * not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *	http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */

package org.logstash.secret.store.backend;

import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.channels.FileLock;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.attribute.PosixFileAttributeView;
import java.nio.file.attribute.PosixFilePermissions;

public final class FileSystemHelper {
    private static final boolean IS_WINDOWS = System.getProperty("os.name").startsWith("Windows");

    public static void setPosixPermissions(Path path, String permissions) throws IOException {
        PosixFileAttributeView attrs = Files.getFileAttributeView(path, PosixFileAttributeView.class);
        if (attrs != null) {
            attrs.setPermissions(PosixFilePermissions.fromString(permissions));
        }
    }

    public static FileLock lockFile(FileOutputStream fos, Path path) throws IOException {
        if (!IS_WINDOWS) {
            FileLock fileLock = fos.getChannel().tryLock();
            if (fileLock == null) {
                throw new IllegalStateException("Can not save Logstash keystore. Some other process has locked on the file: " + path.toAbsolutePath());
            }
            return fileLock;
        }
        return null;
    }

    public static void releaseLock(FileLock fileLock) throws IOException {
        if (fileLock != null && fileLock.isValid()) {
            fileLock.release();
        }
    }
}
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `logstash-core/src/main/java/org/logstash/secret/store/backend/FileSystemHelper.java` | - → 50 | - → 3 | - → 3.33 | - → 8 | - → 0 |
| `logstash-core/src/main/java/org/logstash/secret/store/backend/JavaKeyStore.java` | 409 → - | 16 → - | 5.44 → - | 72 → - | 0 → - |

## Diff

```diff
diff --git a/logstash-core/src/main/java/org/logstash/secret/store/backend/FileSystemHelper.java b/logstash-core/src/main/java/org/logstash/secret/store/backend/FileSystemHelper.java
new file mode 100644
index 0000000..0000000
--- /dev/null
+++ b/logstash-core/src/main/java/org/logstash/secret/store/backend/FileSystemHelper.java
@@ -0,0 +1,56 @@
+/*
+ * Licensed to Elasticsearch B.V. under one or more contributor
+ * license agreements. See the NOTICE file distributed with
+ * this work for additional information regarding copyright
+ * ownership. Elasticsearch B.V. licenses this file to you under
+ * the Apache License, Version 2.0 (the "License"); you may
+ * not use this file except in compliance with the License.
+ * You may obtain a copy of the License at
+ *
+ *	http://www.apache.org/licenses/LICENSE-2.0
+ *
+ * Unless required by applicable law or agreed to in writing,
+ * software distributed under the License is distributed on an
+ * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
+ * KIND, either express or implied.  See the License for the
+ * specific language governing permissions and limitations
+ * under the License.
+ */
+
+package org.logstash.secret.store.backend;
+
+import java.io.FileOutputStream;
+import java.io.IOException;
+import java.nio.channels.FileLock;
+import java.nio.file.Files;
+import java.nio.file.Path;
+import java.nio.file.attribute.PosixFileAttributeView;
+import java.nio.file.attribute.PosixFilePermissions;
+
+public final class FileSystemHelper {
+    private static final boolean IS_WINDOWS = System.getProperty("os.name").startsWith("Windows");
+
+    public static void setPosixPermissions(Path path, String permissions) throws IOException {
+        PosixFileAttributeView attrs = Files.getFileAttributeView(path, PosixFileAttributeView.class);
+        if (attrs != null) {
+            attrs.setPermissions(PosixFilePermissions.fromString(permissions));
+        }
+    }
+
+    public static FileLock lockFile(FileOutputStream fos, Path path) throws IOException {
+        if (!IS_WINDOWS) {
+            FileLock fileLock = fos.getChannel().tryLock();
+            if (fileLock == null) {
+                throw new IllegalStateException("Can not save Logstash keystore. Some other process has locked on the file: " + path.toAbsolutePath());
+            }
+            return fileLock;
+        }
+        return null;
+    }
+
+    public static void releaseLock(FileLock fileLock) throws IOException {
+        if (fileLock != null && fileLock.isValid()) {
+            fileLock.release();
+        }
+    }
+}
\ No newline at end of file

```
