# Refactor DIP-015 (DIP): Base class depends on concrete subclass through instanceof check and casting.

**Status:** `patch_failed`  
**Branch:** `refactor/DIP-015` -> `main`  
**Head commit:** `dd2635882c62183384495a6af7ced47dd7ad7df6`  
**LLM finish:** `FinishReason.STOP` (prompt 5888, completion 113)  

## Detected issue

- **File**: `gson/src/main/java/com/google/gson/stream/JsonReader.java`
- **Entity**: `JsonReader` (class)
- **Lines (at detection time)**: L1640–L1662
- **Severity**: high
- **Confidence**: detected by 2 scan(s)

**Description.** Base class depends on concrete subclass through instanceof check and casting.

**Reasoning.** Inappropriate Intimacy smell -> DIP violation because the base class JsonReader contains a static initializer that explicitly references JsonTreeReader (a subclass). Abstractions (JsonReader) should not depend on details (JsonTreeReader). This reverse dependency makes the base class fragile and tightly coupled to its specific implementations.

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
| `gson/src/main/java/com/google/gson/stream/JsonReader.java` | 1708 → - | 44 → - | 10.64 → - | 425 → - | 0 → - |

## Diff

*(no diff — patch was not applied)*
