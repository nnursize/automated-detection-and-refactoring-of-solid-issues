# Refactor OCP-012 (OCP): Switch statement on minor state requires modification to handle new states

**Status:** `patch_failed`  
**Branch:** `refactor/OCP-012` -> `main`  
**Head commit:** `830edb6aac4f165c94a5fdc01dc77dc6a23643ba`  
**LLM finish:** `FinishReason.STOP` (prompt 3533, completion 161)  

## Detected issue

- **File**: `src/main/java/tools/jackson/core/json/async/NonBlockingUtf8JsonParserBase.java`
- **Entity**: `NonBlockingUtf8JsonParserBase._finishToken` (class)
- **Lines (at detection time)**: L172–L308
- **Severity**: high
- **Confidence**: detected by 3 scan(s)

**Description.** Switch statement on minor state requires modification to handle new states

**Reasoning.** The _finishToken method uses a switch statement on _minorState. Adding new states or parsing logic would require modifying this switch block, violating the Open/Closed Principle.

## Fix logic

- **Model**: `gemini-2.5-flash` (temperature 0.2)
- **Patch blocks**: 0

**Summary.** Cannot safely refactor due to truncated source code for the switch statement.

**Rationale.** The provided source code for the `_finishToken` method is truncated, specifically the `switch (_minorState)` statement. The line `# ... 2800 later lines elided ...` indicates that many `case` branches are missing. Without the complete set of `case` statements, it is impossible to safely refactor the switch statement into a dispatch mechanism (e.g., using a map of handlers) without risking an incomplete fix that would break existing behavior for the unhandled states. Adhering to rule 8, a partial refactor is not emitted.

## Apply error

```
no patch blocks produced by LLM
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/main/java/tools/jackson/core/json/async/NonBlockingUtf8JsonParserBase.java` | 2634 → - | 63 → - | 12.56 → - | 729 → - | 0 → - |

## Diff

*(no diff — patch was not applied)*
