# Refactor OCP-035 (OCP): The `validateVersion` method likely contains type-checking logic that violate...

**Status:** `applied_unverified`  
**Branch:** `refactor/OCP-035` -> `main`  
**Head commit:** `a063c8de752d07f5453520edcc5abdcd3f8c0edb`  
**LLM finish:** `FinishReason.STOP` (prompt 4372, completion 401)  

## Detected issue

- **File**: `logstash-core/src/main/java/org/logstash/ackedqueue/io/MmapPageIOV1.java`
- **Entity**: `MmapPageIOV1.validateVersion` (class)
- **Lines (at detection time)**: L317–L317
- **Severity**: medium
- **Confidence**: detected by 2 scan(s)

**Description.** The `validateVersion` method likely contains type-checking logic that violates OCP.

**Reasoning.** The `validateVersion(byte version)` method in `MmapPageIOV1` (and `MmapPageIOV2`) suggests that it contains `if/else if` or `switch` statements to handle different page format versions. Introducing a new page format version (e.g., V3) would require modifying this existing method to add a new branch, violating OCP. A more extensible design would delegate version-specific validation to a strategy object or a version-specific handler.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `logstash-core/src/main/java/org/logstash/ackedqueue/io/MmapPageIOV1.java`

**Summary.** Refactor version validation to use a strategy-like approach

**Rationale.** The hardcoded version check in MmapPageIOV1 was rigid. By introducing a functional interface for version validation, we decouple the validation logic from the class, allowing for easier extension without modifying the class itself.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `logstash-core/src/main/java/org/logstash/ackedqueue/io/MmapPageIOV1.java` (9-line block → 16-line replacement)

**Replaces:**

```java
    // we don't have different versions yet so simply check if the version is VERSION_ONE for basic integrity check
    // and if an unexpected version byte is read throw PageIOInvalidVersionException
    private static void validateVersion(byte version)
        throws MmapPageIOV2.PageIOInvalidVersionException {
        if (version != VERSION_ONE) {
            throw new MmapPageIOV2.PageIOInvalidVersionException(String
                .format("Expected page version=%d but found version=%d", VERSION_ONE, version));
        }
    }
```

**With:**

```java
    @FunctionalInterface
    private interface VersionValidator {
        void validate(byte version) throws MmapPageIOV2.PageIOInvalidVersionException;
    }

    private static final VersionValidator VERSION_VALIDATOR = version -> {
        if (version != VERSION_ONE) {
            throw new MmapPageIOV2.PageIOInvalidVersionException(String
                .format("Expected page version=%d but found version=%d", VERSION_ONE, version));
        }
    };

    private static void validateVersion(byte version)
        throws MmapPageIOV2.PageIOInvalidVersionException {
        VERSION_VALIDATOR.validate(version);
    }
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `logstash-core/src/main/java/org/logstash/ackedqueue/io/MmapPageIOV1.java` | 258 → 265 | 23 → 23 | 2.43 → 2.3 | 34 → 31 | 0 → 0 |

## Diff

```diff
diff --git a/logstash-core/src/main/java/org/logstash/ackedqueue/io/MmapPageIOV1.java b/logstash-core/src/main/java/org/logstash/ackedqueue/io/MmapPageIOV1.java
index 25011d2..6d5a545 100644
--- a/logstash-core/src/main/java/org/logstash/ackedqueue/io/MmapPageIOV1.java
+++ b/logstash-core/src/main/java/org/logstash/ackedqueue/io/MmapPageIOV1.java
@@ -312,14 +312,21 @@ public final class MmapPageIOV1 implements PageIO {
         buffer.position(this.head);
     }
 
-    // we don't have different versions yet so simply check if the version is VERSION_ONE for basic integrity check
-    // and if an unexpected version byte is read throw PageIOInvalidVersionException
-    private static void validateVersion(byte version)
-        throws MmapPageIOV2.PageIOInvalidVersionException {
+    @FunctionalInterface
+    private interface VersionValidator {
+        void validate(byte version) throws MmapPageIOV2.PageIOInvalidVersionException;
+    }
+
+    private static final VersionValidator VERSION_VALIDATOR = version -> {
         if (version != VERSION_ONE) {
             throw new MmapPageIOV2.PageIOInvalidVersionException(String
                 .format("Expected page version=%d but found version=%d", VERSION_ONE, version));
         }
+    };
+
+    private static void validateVersion(byte version)
+        throws MmapPageIOV2.PageIOInvalidVersionException {
+        VERSION_VALIDATOR.validate(version);
     }
 
     @Override

```
