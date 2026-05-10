# Refactor DIP-005 (DIP): Direct instantiation of TreeTypeAdapter.

**Status:** `patch_failed`  
**Branch:** `refactor/DIP-005` -> `main`  
**Head commit:** `29fb26dc6739abacd329814707753280ac11a2e7`  
**LLM finish:** `FinishReason.STOP` (prompt 3679, completion 838)  

## Detected issue

- **File**: `gson/src/main/java/com/google/gson/internal/bind/JsonAdapterAnnotationTypeAdapterFactory.java`
- **Entity**: `JsonAdapterAnnotationTypeAdapterFactory.getTypeAdapter` (method)
- **Lines (at detection time)**: L102–L104
- **Severity**: medium
- **Confidence**: detected by 3 scan(s)

**Description.** Direct instantiation of TreeTypeAdapter.

**Reasoning.** The factory directly instantiates TreeTypeAdapter when handling @JsonAdapter annotations. This creates a hard dependency on the TreeTypeAdapter implementation detail rather than interacting with it through a more generic interface or injecting the adapter creation logic.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 0

**Summary.** Introduce a factory method for creating TreeTypeAdapter to decouple from its concrete implementation.

**Rationale.** The direct instantiation of TreeTypeAdapter violates the Dependency Inversion Principle. By introducing a static factory method (or delegating creation), we can abstract the instantiation logic. Since TreeTypeAdapter is already in the same package, I will add a static factory method within TreeTypeAdapter to encapsulate its creation, allowing the factory to remain decoupled from the constructor signature.

## Apply error

```
no patch blocks produced by LLM
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `gson/src/main/java/com/google/gson/internal/bind/JsonAdapterAnnotationTypeAdapterFactory.java` | 151 → - | 5 → - | 7.6 → - | 34 → - | 0 → - |

## Diff

*(no diff — patch was not applied)*
