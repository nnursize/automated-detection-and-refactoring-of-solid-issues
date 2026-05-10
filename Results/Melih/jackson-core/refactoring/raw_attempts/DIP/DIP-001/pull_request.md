# Refactor DIP-001 (DIP): Direct instantiation of TokenStreamLocation concrete class.

**Status:** `patch_failed`  
**Branch:** `refactor/DIP-001` -> `main`  
**Head commit:** `ad97fd088b013aa530f0a76273739381cb67c8cd`  
**LLM finish:** `FinishReason.STOP` (prompt 3948, completion 969)  

## Detected issue

- **File**: `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java`
- **Entity**: `UTF8StreamJsonParser._reportInvalidToken` (method)
- **Lines (at detection time)**: L1530–L1533
- **Severity**: low
- **Confidence**: detected by 3 scan(s)

**Description.** Direct instantiation of TokenStreamLocation concrete class.

**Reasoning.** The parser directly instantiates TokenStreamLocation instead of using a factory or receiving it via injection. While TokenStreamLocation is a value object, this creates a tight coupling between the high-level parsing logic and the specific implementation of location tracking.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 0

**Summary.** Introduce a factory method for TokenStreamLocation to avoid direct instantiation

**Rationale.** Direct instantiation of TokenStreamLocation violates the Dependency Inversion Principle. By introducing a protected factory method in the base class (or using existing infrastructure), we decouple the parser from the concrete implementation of the location object.

## Apply error

```
no patch blocks produced by LLM
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java` | 3558 → - | 114 → - | 9.62 → - | 984 → - | 0 → - |

## Diff

*(no diff — patch was not applied)*
