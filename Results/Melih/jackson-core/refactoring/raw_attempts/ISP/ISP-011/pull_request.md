# Refactor ISP-011 (ISP): The FilteringParserDelegate class is forced to implement overrideCurrentName...

**Status:** `patch_failed`  
**Branch:** `refactor/ISP-011` -> `main`  
**Head commit:** `5650ed69e32cc1205ea2281f12c8a5b6bcfeaebf`  
**LLM finish:** `FinishReason.STOP` (prompt 10212, completion 282)  

## Detected issue

- **File**: `src/main/java/tools/jackson/core/filter/FilteringParserDelegate.java`
- **Entity**: `FilteringParserDelegate.overrideCurrentName` (method)
- **Lines (at detection time)**: L251–L255
- **Severity**: high
- **Confidence**: detected by 1 scan(s)

**Description.** The FilteringParserDelegate class is forced to implement overrideCurrentName from JsonParser but explicitly throws UnsupportedOperationException.

**Reasoning.** The 'JsonParser' interface (or an abstract class it extends) includes a method to override the current name. 'FilteringParserDelegate', a specialized parser that modifies token streams, explicitly throws 'UnsupportedOperationException' for 'overrideCurrentName()'. This indicates that not all concrete parser implementations can or should support this operation, making the 'JsonParser' interface too broad and forcing clients to implement unneeded methods.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 0

**Summary.** Remove the unused and unsupported overrideCurrentName method from FilteringParserDelegate

**Rationale.** The method was commented out and explicitly threw UnsupportedOperationException, indicating it is not part of the functional contract for this class. Removing it cleans up the implementation and avoids forcing the class to adhere to an interface method it cannot support.

## Apply error

```
no patch blocks produced by LLM
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/main/java/tools/jackson/core/filter/FilteringParserDelegate.java` | 914 → - | 20 → - | 11.9 → - | 219 → - | 0 → - |

## Diff

*(no diff — patch was not applied)*
