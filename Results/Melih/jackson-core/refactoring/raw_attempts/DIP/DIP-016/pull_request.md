# Refactor DIP-016 (DIP): Abstract base class depends on a concrete context implementation.

**Status:** `patch_failed`  
**Branch:** `refactor/DIP-016` -> `main`  
**Head commit:** `ad97fd088b013aa530f0a76273739381cb67c8cd`  
**LLM finish:** `FinishReason.STOP` (prompt 5870, completion 387)  

## Detected issue

- **File**: `src/main/java/tools/jackson/core/json/JsonParserBase.java`
- **Entity**: `JsonParserBase` (class)
- **Lines (at detection time)**: L74–L80
- **Severity**: medium
- **Confidence**: detected by 2 scan(s)

**Description.** Abstract base class depends on a concrete context implementation.

**Reasoning.** The abstract class JsonParserBase directly instantiates and depends on the concrete class JsonReadContext via the call to JsonReadContext.createRootContext(dups). This violates DIP as the high-level abstraction (JsonParserBase) depends on a low-level implementation detail (JsonReadContext) instead of an abstraction.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 0

**Summary.** Inject JsonReadContext factory into JsonParserBase to decouple from concrete implementation

**Rationale.** JsonParserBase was directly instantiating JsonReadContext. By introducing a protected abstract method to create the root context, subclasses can provide the specific implementation, adhering to the Dependency Inversion Principle.

## Apply error

```
no patch blocks produced by LLM
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/main/java/tools/jackson/core/json/JsonParserBase.java` | 371 → - | 23 → - | 3.48 → - | 58 → - | 0 → - |

## Diff

*(no diff — patch was not applied)*
