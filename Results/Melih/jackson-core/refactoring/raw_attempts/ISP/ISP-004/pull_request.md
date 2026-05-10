# Refactor ISP-004 (ISP): ReaderBasedJsonParser implements the large JsonParser interface, forcing the...

**Status:** `patch_failed`  
**Branch:** `refactor/ISP-004` -> `main`  
**Head commit:** `5650ed69e32cc1205ea2281f12c8a5b6bcfeaebf`  
**LLM finish:** `FinishReason.STOP` (prompt 7841, completion 785)  

## Detected issue

- **File**: `src/main/java/tools/jackson/core/json/ReaderBasedJsonParser.java`
- **Entity**: `ReaderBasedJsonParser` (class)
- **Lines (at detection time)**: L17–L1150
- **Severity**: medium
- **Confidence**: detected by 1 scan(s)

**Description.** ReaderBasedJsonParser implements the large JsonParser interface, forcing the inclusion of methods for binary data and non-blocking parsing that are not its primary purpose.

**Reasoning.** ReaderBasedJsonParser is a character-based parser. The JsonParser interface is fat, containing methods for binary, stream, and async parsing. This forces the implementation to carry the overhead and complexity of an interface that covers diverse parsing models beyond character-based reading.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 0

## Apply error

```
no patch blocks produced by LLM
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/main/java/tools/jackson/core/json/ReaderBasedJsonParser.java` | 2604 → - | 85 → - | 9.92 → - | 759 → - | 0 → - |

## Diff

*(no diff — patch was not applied)*
