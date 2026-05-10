# Refactor LSP-091 (LSP): Subtype throws UnsupportedOperationException for a base type method.

**Status:** `patch_failed`  
**Branch:** `refactor/LSP-091` -> `main`  
**Head commit:** `5ea01a543c2275e3945abae8f28a690757aa66bc`  
**LLM finish:** `FinishReason.STOP` (prompt 4431, completion 260)  

## Detected issue

- **File**: `logstash-core/src/main/java/org/logstash/ackedqueue/io/MmapPageIOV1.java`
- **Entity**: `MmapPageIOV1.create` (method)
- **Lines (at detection time)**: L146–L147
- **Severity**: high
- **Confidence**: detected by 2 scan(s)

**Description.** Subtype throws UnsupportedOperationException for a base type method.

**Reasoning.** The `create()` method in `MmapPageIOV1` explicitly throws `UnsupportedOperationException`. This violates LSP because a client expecting a `PageIO` (the base type) would assume `create()` is a supported operation, but substituting `MmapPageIOV1` breaks this expectation by throwing an exception not declared in the base contract, indicating the subtype cannot be used in place of the base type without altering correctness.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `logstash-core/src/main/java/org/logstash/ackedqueue/io/MmapPageIOV1.java`

**Summary.** Remove UnsupportedOperationException from MmapPageIOV1.create() to comply with LSP

**Rationale.** The MmapPageIOV1 class is a read-only implementation of PageIO. Throwing UnsupportedOperationException in create() violates the Liskov Substitution Principle. Since the class is intended for read-only operations, the create() method should be a no-op (as it was already, but with a comment) rather than throwing an exception, or the interface should be split. Given the constraints, removing the exception and keeping it as a no-op is the safest way to satisfy the contract without breaking existing callers that might expect the method to be callable.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `logstash-core/src/main/java/org/logstash/ackedqueue/io/MmapPageIOV1.java` (4-line block → 4-line replacement)

**Replaces:**

```java
    @Override
    public void create() {
        // No-op for read-only legacy V1 pages
    }
```

**With:**

```java
    @Override
    public void create() {
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
