# Refactor DIP-018 (DIP): Factory class hard-codes dependency on concrete recycler pools.

**Status:** `patch_failed`  
**Branch:** `refactor/DIP-018` -> `main`  
**Head commit:** `70ee934d5eea670f5238a219cd3df955090a48c2`  
**LLM finish:** `FinishReason.STOP` (prompt 14330, completion 544)  

## Detected issue

- **File**: `src/main/java/tools/jackson/core/TokenStreamFactory.java`
- **Entity**: `TokenStreamFactory` (class)
- **Lines (at detection time)**: L226–L237
- **Severity**: high
- **Confidence**: detected by 1 scan(s)

**Description.** Factory class hard-codes dependency on concrete recycler pools.

**Reasoning.** The constructor of TokenStreamFactory directly calls JsonRecyclerPools.defaultPool(), coupling the high-level factory abstraction to a specific concrete implementation of buffer recycling. This makes it difficult to substitute different recycling strategies without modifying the factory.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 0

**Summary.** Inject RecyclerPool into TokenStreamFactory to remove hard-coded dependency

**Rationale.** The TokenStreamFactory constructor was hard-coding a dependency on JsonRecyclerPools.defaultPool(). By updating the constructors to accept an optional RecyclerPool and providing a default if null, we allow for dependency injection while maintaining backward compatibility for existing callers.

## Apply error

```
no patch blocks produced by LLM
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/main/java/tools/jackson/core/TokenStreamFactory.java` | 1276 → - | 51 → - | 4.41 → - | 175 → - | 0 → - |

## Diff

*(no diff — patch was not applied)*
