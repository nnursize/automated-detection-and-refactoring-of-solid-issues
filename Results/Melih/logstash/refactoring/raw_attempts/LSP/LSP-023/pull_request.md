# Refactor LSP-023 (LSP): Method throws specific SecretStoreException subtype not declared by the base...

**Status:** `applied_unverified`  
**Branch:** `refactor/LSP-023` -> `main`  
**Head commit:** `dcd8375313790ad4d5184da6eab806b13724e9e9`  
**LLM finish:** `FinishReason.STOP` (prompt 5962, completion 259)  

## Detected issue

- **File**: `logstash-core/src/main/java/org/logstash/secret/store/backend/JavaKeyStore.java`
- **Entity**: `JavaKeyStore.delete` (method)
- **Lines (at detection time)**: L93–L103
- **Severity**: high
- **Confidence**: detected by 2 scan(s)

**Description.** Method throws specific SecretStoreException subtype not declared by the base interface.

**Reasoning.** The `SecretStore` interface defines a `delete()` method. `JavaKeyStore#delete` throws `SecretStoreException.UnknownException`. If the `SecretStore` interface does not declare this specific `RuntimeException` subtype, then `JavaKeyStore` violates LSP.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `logstash-core/src/main/java/org/logstash/secret/store/backend/JavaKeyStore.java`

**Summary.** Replace SecretStoreException.UnknownException with SecretStoreException in delete() method to comply with interface contract.

**Rationale.** The SecretStore interface defines the delete() method. By throwing a specific subtype (UnknownException) not explicitly declared in the interface (or expected by the contract), the implementation violates the Liskov Substitution Principle. Using the base SecretStoreException allows the implementation to remain compliant while still signaling an error.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `logstash-core/src/main/java/org/logstash/secret/store/backend/JavaKeyStore.java` (5-line block → 5-line replacement)

**Replaces:**

```java
        } catch (SecretStoreException sse) {
            throw sse;
        } catch (Exception e) { //should never happen
            throw new SecretStoreException.UnknownException("Error while trying to delete the Logstash keystore", e);
        } finally {
```

**With:**

```java
        } catch (SecretStoreException sse) {
            throw sse;
        } catch (Exception e) { //should never happen
            throw new SecretStoreException("Error while trying to delete the Logstash keystore", e);
        } finally {
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `logstash-core/src/main/java/org/logstash/secret/store/backend/JavaKeyStore.java` | 409 → 409 | 16 → 16 | 5.44 → 5.44 | 72 → 72 | 0 → 0 |

## Diff

```diff
diff --git a/logstash-core/src/main/java/org/logstash/secret/store/backend/JavaKeyStore.java b/logstash-core/src/main/java/org/logstash/secret/store/backend/JavaKeyStore.java
index 1bcf1f2..466453d 100644
--- a/logstash-core/src/main/java/org/logstash/secret/store/backend/JavaKeyStore.java
+++ b/logstash-core/src/main/java/org/logstash/secret/store/backend/JavaKeyStore.java
@@ -152,7 +152,7 @@ public final class JavaKeyStore implements SecretStore {
         } catch (SecretStoreException sse) {
             throw sse;
         } catch (Exception e) { //should never happen
-            throw new SecretStoreException.UnknownException("Error while trying to delete the Logstash keystore", e);
+            throw new SecretStoreException("Error while trying to delete the Logstash keystore", e);
         } finally {
             releaseLock(lock);
             config.clearValues();

```
