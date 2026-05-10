# Refactor DIP-019 (DIP): Factory method directly instantiates a concrete I/O context.

**Status:** `patch_failed`  
**Branch:** `refactor/DIP-019` -> `main`  
**Head commit:** `70ee934d5eea670f5238a219cd3df955090a48c2`  
**LLM finish:** `FinishReason.STOP` (prompt 14340, completion 739)  

## Detected issue

- **File**: `src/main/java/tools/jackson/core/TokenStreamFactory.java`
- **Entity**: `TokenStreamFactory._createContext` (method)
- **Lines (at detection time)**: L1277–L1301
- **Severity**: high
- **Confidence**: detected by 1 scan(s)

**Description.** Factory method directly instantiates a concrete I/O context.

**Reasoning.** The method _createContext directly instantiates the concrete class IOContext using the 'new' keyword. This violates DIP because the high-level factory module depends on the low-level implementation details of the I/O context rather than an abstraction or a provider.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 0

**Summary.** Introduce IOContextFactory to decouple TokenStreamFactory from concrete IOContext instantiation

**Rationale.** The TokenStreamFactory was directly instantiating DefaultIOContextFactory. By introducing an IOContextFactory interface (or using the existing one if it were an interface, but here we define a field/method to allow injection/override), we adhere to DIP. Since I cannot change the constructor of DefaultIOContextFactory without potentially breaking other code, I will add a protected field to TokenStreamFactory that holds the factory instance, allowing it to be configured or overridden, and use that instead of 'new'.

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
