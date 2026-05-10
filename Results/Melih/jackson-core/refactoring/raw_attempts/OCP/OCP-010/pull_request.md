# Refactor OCP-010 (OCP): Switch statement on character input requires modification to handle new value...

**Status:** `patch_failed`  
**Branch:** `refactor/OCP-010` -> `main`  
**Head commit:** `830edb6aac4f165c94a5fdc01dc77dc6a23643ba`  
**LLM finish:** `FinishReason.STOP` (prompt 3678, completion 161)  

## Detected issue

- **File**: `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java`
- **Entity**: `UTF8StreamJsonParser._isNextTokenNameMaybe` (class)
- **Lines (at detection time)**: L1105–L1165
- **Severity**: high
- **Confidence**: detected by 3 scan(s)

**Description.** Switch statement on character input requires modification to handle new value types

**Reasoning.** The _isNextTokenNameMaybe method uses a switch statement to dispatch parsing based on the first character of a value. Adding new value types would require modifying this switch block, violating the Open/Closed Principle.

## Fix logic

- **Model**: `gemini-2.5-flash` (temperature 0.2)
- **Patch blocks**: 0

**Summary.** Cannot refactor: target method implementation not provided in snippet.

**Rationale.** The detected violation points to a switch statement within the `_isNextTokenNameMaybe` method. However, the provided source code snippet for `UTF8StreamJsonParser.java` only shows a call to `_isNextTokenNameMaybe` (around line 954, as indicated by the violation), but not its implementation. Without the actual code of the method containing the problematic switch statement, it is not possible to safely apply the refactoring while adhering to the strict output format and ensuring no unrelated code is modified. Therefore, the refactoring cannot be performed in one shot.

## Apply error

```
no patch blocks produced by LLM
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/main/java/tools/jackson/core/json/UTF8StreamJsonParser.java` | 3534 → - | 112 → - | 9.81 → - | 988 → - | 0 → - |

## Diff

*(no diff — patch was not applied)*
