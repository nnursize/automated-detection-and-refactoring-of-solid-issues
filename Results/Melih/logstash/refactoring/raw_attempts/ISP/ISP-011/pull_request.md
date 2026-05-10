# Refactor ISP-011 (ISP): The 'SecretStore' interface combines management, query, and persistence opera...

**Status:** `obsolete`  
**Branch:** `refactor/ISP-011` -> `main`  
**Head commit:** `c86960ad45d225a0604034d8f0b69a79cde0356a`  

## Detected issue

- **File**: `logstash-core/src/main/java/org/logstash/secret/store/backend/JavaKeyStore.java`
- **Entity**: `org.logstash.secret.store.SecretStore` (class)
- **Lines (at detection time)**: L45–L45
- **Severity**: medium
- **Confidence**: detected by 3 scan(s)

**Description.** The 'SecretStore' interface combines management, query, and persistence operations.

**Reasoning.** The `SecretStore` interface includes methods for creating/deleting the store (`create`, `delete`), loading (`load`), listing/checking secrets (`list`, `containsSecret`), and persisting/retrieving/purging individual secrets (`persistSecret`, `retrieveSecret`, `purgeSecret`). A client that only needs to read secrets (e.g., for configuration expansion) is forced to depend on methods for modifying the store or secrets, which it does not use. This makes the interface fat for such clients.

## Obsolete

entity `org.logstash.secret.store.SecretStore` not found in current source of `logstash-core/src/main/java/org/logstash/secret/store/backend/JavaKeyStore.java` — likely renamed/removed by an earlier refactor

## Diff

*(no diff — patch was not applied)*
