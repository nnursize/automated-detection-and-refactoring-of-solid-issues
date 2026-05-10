# Refactor DIP-021 (DIP): Direct instantiation of concrete UTF8StreamJsonParser.

**Status:** `patch_failed`  
**Branch:** `refactor/DIP-021` -> `main`  
**Head commit:** `1f88f255084094074ecf93ddbee18e92dd16b388`  
**LLM finish:** `FinishReason.STOP` (prompt 5866, completion 846)  

## Detected issue

- **File**: `src/main/java/tools/jackson/core/json/ByteSourceJsonBootstrapper.java`
- **Entity**: `ByteSourceJsonBootstrapper.constructParser` (class)
- **Lines (at detection time)**: L283–L300
- **Severity**: high
- **Confidence**: detected by 3 scan(s)

**Description.** Direct instantiation of concrete UTF8StreamJsonParser.

**Reasoning.** The constructParser method directly instantiates UTF8StreamJsonParser using the 'new' keyword. This violates DIP because a high-level component responsible for bootstrapping should depend on the JsonParser abstraction rather than a specific low-level implementation.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 0

**Summary.** Introduce a factory method in UTF8StreamJsonParser to decouple instantiation from ByteSourceJsonBootstrapper.

**Rationale.** Direct instantiation of concrete classes violates the Dependency Inversion Principle. By adding a static factory method to UTF8StreamJsonParser, the bootstrapper can create the parser without explicitly depending on the constructor, allowing for better abstraction and potential future dependency injection.

## Apply error

```
no patch blocks produced by LLM
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/main/java/tools/jackson/core/json/ByteSourceJsonBootstrapper.java` | 386 → - | 11 → - | 7.55 → - | 73 → - | 0 → - |

## Diff

*(no diff — patch was not applied)*
