# Refactor LSP-022 (LSP): Method throws multiple specific SecretStoreException subtypes not declared by...

**Status:** `applied_unverified`  
**Branch:** `refactor/LSP-022` -> `main`  
**Head commit:** `aacfd8aa0f5607accaa2440c2aa3afc4cb7f71bf`  
**LLM finish:** `FinishReason.STOP` (prompt 6025, completion 1335)  

## Detected issue

- **File**: `logstash-core/src/main/java/org/logstash/secret/store/backend/JavaKeyStore.java`
- **Entity**: `JavaKeyStore.create` (method)
- **Lines (at detection time)**: L57–L90
- **Severity**: high
- **Confidence**: detected by 2 scan(s)

**Description.** Method throws multiple specific SecretStoreException subtypes not declared by the base interface.

**Reasoning.** The `SecretStore` interface (implied by `JavaKeyStore` implementing it) defines a `create()` method. `JavaKeyStore#create` throws `SecretStoreException.AlreadyExistsException`, `SecretStoreException.CreateException`, and `SecretStoreException.UnknownException`. If the `SecretStore` interface does not declare these specific `RuntimeException` subtypes, then `JavaKeyStore` violates LSP by throwing exceptions that a client might not be prepared to handle, breaking the client's expectation of correctness.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `logstash-core/src/main/java/org/logstash/secret/store/backend/JavaKeyStore.java`

**Summary.** Update JavaKeyStore.create to throw base SecretStoreException instead of specific subtypes

**Rationale.** The Liskov Substitution Principle is violated when a subclass throws checked or unchecked exceptions not declared in the base interface. By catching the specific subtypes and rethrowing the base SecretStoreException, we maintain compatibility with the interface contract while preserving the underlying error information.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `logstash-core/src/main/java/org/logstash/secret/store/backend/JavaKeyStore.java` (43-line block → 43-line replacement)

**Replaces:**

```java
    @Override
    public JavaKeyStore create(SecureConfig config) {
        if (exists(config)) {
            throw new SecretStoreException.AlreadyExistsException(String.format("Logstash keystore at %s already exists.",
                    new String(config.getPlainText(PATH_KEY))));
        }
        try {
            init(config);
            lock.lock();
            LOGGER.debug("Creating new keystore at {}.", keyStorePath.toAbsolutePath());
            String keyStorePermissions = filePermissions;
            //create the keystore on disk with a default entry to identify this as a logstash keystore
            //can not set posix attributes on create here since not all Windows are posix, *nix will get the umask default and posix permissions will be set below
            Files.createFile(keyStorePath);
            try {
                keyStore = KeyStore.Builder.newInstance(KEYSTORE_TYPE, null, protectionParameter).getKeyStore();
                SecretKeyFactory factory = SecretKeyFactory.getInstance("PBE");
                byte[] base64 = SecretStoreUtil.base64Encode(LOGSTASH_MARKER.getKey().getBytes(StandardCharsets.UTF_8));
                SecretKey secretKey = factory.generateSecret(new PBEKeySpec(SecretStoreUtil.asciiBytesToChar(base64)));
                keyStore.setEntry(LOGSTASH_MARKER.toExternalForm(), new KeyStore.SecretKeyEntry(secretKey), protectionParameter);
                saveKeyStore();
                PosixFileAttributeView attrs = Files.getFileAttributeView(keyStorePath, PosixFileAttributeView.class);
                if (attrs != null) {
                    //the directory umask applies when creating the file, so re-apply permissions here
                    attrs.setPermissions(PosixFilePermissions.fromString(keyStorePermissions));
                }
                LOGGER.info("Created Logstash keystore at {}", keyStorePath.toAbsolutePath());
                return this;
            } catch (Exception e) {
                throw new SecretStoreException.CreateException("Failed to create Logstash keystore.", e);
            }
        } catch (SecretStoreException sse) {
            throw sse;
        } catch (NoSuchFileException | AccessDeniedException fe) {
            throw new SecretStoreException.CreateException("Error while trying to create the Logstash keystore. Please ensure that path to " + keyStorePath.toAbsolutePath() +
                    " exists and is writable", fe);
        } catch (Exception e) { //should never happen
            throw new SecretStoreException.UnknownException("Error while trying to create the Logstash keystore. ", e);
        } finally {
            releaseLock(lock);
            config.clearValues();
        }
    }
```

**With:**

```java
    @Override
    public JavaKeyStore create(SecureConfig config) {
        if (exists(config)) {
            throw new SecretStoreException(String.format("Logstash keystore at %s already exists.",
                    new String(config.getPlainText(PATH_KEY))));
        }
        try {
            init(config);
            lock.lock();
            LOGGER.debug("Creating new keystore at {}.", keyStorePath.toAbsolutePath());
            String keyStorePermissions = filePermissions;
            //create the keystore on disk with a default entry to identify this as a logstash keystore
            //can not set posix attributes on create here since not all Windows are posix, *nix will get the umask default and posix permissions will be set below
            Files.createFile(keyStorePath);
            try {
                keyStore = KeyStore.Builder.newInstance(KEYSTORE_TYPE, null, protectionParameter).getKeyStore();
                SecretKeyFactory factory = SecretKeyFactory.getInstance("PBE");
                byte[] base64 = SecretStoreUtil.base64Encode(LOGSTASH_MARKER.getKey().getBytes(StandardCharsets.UTF_8));
                SecretKey secretKey = factory.generateSecret(new PBEKeySpec(SecretStoreUtil.asciiBytesToChar(base64)));
                keyStore.setEntry(LOGSTASH_MARKER.toExternalForm(), new KeyStore.SecretKeyEntry(secretKey), protectionParameter);
                saveKeyStore();
                PosixFileAttributeView attrs = Files.getFileAttributeView(keyStorePath, PosixFileAttributeView.class);
                if (attrs != null) {
                    //the directory umask applies when creating the file, so re-apply permissions here
                    attrs.setPermissions(PosixFilePermissions.fromString(keyStorePermissions));
                }
                LOGGER.info("Created Logstash keystore at {}", keyStorePath.toAbsolutePath());
                return this;
            } catch (Exception e) {
                throw new SecretStoreException("Failed to create Logstash keystore.", e);
            }
        } catch (SecretStoreException sse) {
            throw sse;
        } catch (NoSuchFileException | AccessDeniedException fe) {
            throw new SecretStoreException("Error while trying to create the Logstash keystore. Please ensure that path to " + keyStorePath.toAbsolutePath() +
                    " exists and is writable", fe);
        } catch (Exception e) { //should never happen
            throw new SecretStoreException("Error while trying to create the Logstash keystore. ", e);
        } finally {
            releaseLock(lock);
            config.clearValues();
        }
    }
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `logstash-core/src/main/java/org/logstash/secret/store/backend/JavaKeyStore.java` | 409 → 409 | 16 → 16 | 5.44 → 5.44 | 72 → 72 | 0 → 0 |

## Diff

```diff
diff --git a/logstash-core/src/main/java/org/logstash/secret/store/backend/JavaKeyStore.java b/logstash-core/src/main/java/org/logstash/secret/store/backend/JavaKeyStore.java
index f75a021..1bcf1f2 100644
--- a/logstash-core/src/main/java/org/logstash/secret/store/backend/JavaKeyStore.java
+++ b/logstash-core/src/main/java/org/logstash/secret/store/backend/JavaKeyStore.java
@@ -100,7 +100,7 @@ public final class JavaKeyStore implements SecretStore {
     @Override
     public JavaKeyStore create(SecureConfig config) {
         if (exists(config)) {
-            throw new SecretStoreException.AlreadyExistsException(String.format("Logstash keystore at %s already exists.",
+            throw new SecretStoreException(String.format("Logstash keystore at %s already exists.",
                     new String(config.getPlainText(PATH_KEY))));
         }
         try {
@@ -126,15 +126,15 @@ public final class JavaKeyStore implements SecretStore {
                 LOGGER.info("Created Logstash keystore at {}", keyStorePath.toAbsolutePath());
                 return this;
             } catch (Exception e) {
-                throw new SecretStoreException.CreateException("Failed to create Logstash keystore.", e);
+                throw new SecretStoreException("Failed to create Logstash keystore.", e);
             }
         } catch (SecretStoreException sse) {
             throw sse;
         } catch (NoSuchFileException | AccessDeniedException fe) {
-            throw new SecretStoreException.CreateException("Error while trying to create the Logstash keystore. Please ensure that path to " + keyStorePath.toAbsolutePath() +
+            throw new SecretStoreException("Error while trying to create the Logstash keystore. Please ensure that path to " + keyStorePath.toAbsolutePath() +
                     " exists and is writable", fe);
         } catch (Exception e) { //should never happen
-            throw new SecretStoreException.UnknownException("Error while trying to create the Logstash keystore. ", e);
+            throw new SecretStoreException("Error while trying to create the Logstash keystore. ", e);
         } finally {
             releaseLock(lock);
             config.clearValues();

```
