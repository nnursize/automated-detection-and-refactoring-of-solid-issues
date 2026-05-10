# Refactor LSP-092 (LSP): Subtype throws UnsupportedOperationException for a base type method.

**Status:** `patch_failed`  
**Branch:** `refactor/LSP-092` -> `main`  
**Head commit:** `5ea01a543c2275e3945abae8f28a690757aa66bc`  
**LLM finish:** `FinishReason.STOP` (prompt 4437, completion 230)  

## Detected issue

- **File**: `logstash-core/src/main/java/org/logstash/ackedqueue/io/MmapPageIOV1.java`
- **Entity**: `MmapPageIOV1.ensurePersisted` (method)
- **Lines (at detection time)**: L166–L167
- **Severity**: high
- **Confidence**: detected by 2 scan(s)

**Description.** Subtype throws UnsupportedOperationException for a base type method.

**Reasoning.** The `ensurePersisted()` method in `MmapPageIOV1` explicitly throws `UnsupportedOperationException`. This violates LSP because a client expecting a `PageIO` (the base type) would assume `ensurePersisted()` is a supported operation, but substituting `MmapPageIOV1` breaks this expectation by throwing an exception not declared in the base contract, indicating the subtype cannot be used in place of the base type without altering correctness.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `logstash-core/src/main/java/org/logstash/ackedqueue/io/MmapPageIOV1.java`

**Summary.** Remove UnsupportedOperationException from MmapPageIOV1.ensurePersisted

**Rationale.** The method ensurePersisted() is a no-op for read-only pages. Throwing UnsupportedOperationException violates the Liskov Substitution Principle because it breaks the contract of the PageIO interface, which does not declare this exception. Changing it to a no-op aligns with the existing behavior of other methods in this class (like recover() and create()) and satisfies the interface contract.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `logstash-core/src/main/java/org/logstash/ackedqueue/io/MmapPageIOV1.java` (4-line block → 4-line replacement)

**Replaces:**

```java
    @Override
    public void ensurePersisted() {
        // No-op for read-only legacy V1 pages
    }
```

**With:**

```java
    @Override
    public void ensurePersisted() {
        // No-op for read-only legacy V1 pages
    }
```

## Apply error

```
patch applied but produced no net source changes; the LLM replacement was likely identical to the matched text
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `logstash-core/src/main/java/org/logstash/ackedqueue/io/MmapPageIOV1.java` | 262 → - | 23 → - | 2.48 → - | 35 → - | 0 → - |

## Diff

*(no diff — patch was not applied)*
