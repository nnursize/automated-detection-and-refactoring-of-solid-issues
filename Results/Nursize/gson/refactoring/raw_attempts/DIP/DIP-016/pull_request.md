# Refactor DIP-016 (DIP): Gson directly instantiates internal implementation details instead of using i...

**Status:** `patch_failed`  
**Branch:** `refactor/DIP-016` -> `main`  
**Head commit:** `29fb26dc6739abacd329814707753280ac11a2e7`  
**LLM finish:** `FinishReason.MAX_TOKENS` (prompt 17122, completion 65532)  

## Detected issue

- **File**: `gson/src/main/java/com/google/gson/Gson.java`
- **Entity**: `Gson.Gson` (method)
- **Lines (at detection time)**: L256–L261
- **Severity**: high
- **Confidence**: detected by 2 scan(s)

**Description.** Gson directly instantiates internal implementation details instead of using injection.

**Reasoning.** Hard-coded dependency smell -> DIP violation because the high-level Gson class directly instantiates ConstructorConstructor and JsonAdapterAnnotationTypeAdapterFactory. These are low-level implementation details. Gson should depend on abstractions for object construction and annotation handling, ideally provided through dependency injection or a factory pattern.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 0

**Summary.** Inject ConstructorConstructor and JsonAdapterAnnotationTypeAdapterFactory via GsonBuilder

**Rationale.** The Gson class was directly instantiating low-level implementation details. By moving the instantiation logic into the GsonBuilder (which is already responsible for configuring the Gson instance), we decouple Gson from these concrete implementations, adhering to the Dependency Inversion Principle.

## Apply error

```
LLM response was truncated (finish_reason=FinishReason.MAX_TOKENS, completion_tokens=65532). Parsed patch blocks were discarded and no changes were applied. Try splitting the issue into a smaller refactor or switching models.
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `gson/src/main/java/com/google/gson/Gson.java` | 1181 → - | 38 → - | 7.21 → - | 237 → - | 0 → - |

## Diff

*(no diff — patch was not applied)*
