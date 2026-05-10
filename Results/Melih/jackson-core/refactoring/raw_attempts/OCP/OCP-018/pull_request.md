# Refactor OCP-018 (OCP): Switch statement on token ID requires modification to handle new token types

**Status:** `patch_failed`  
**Branch:** `refactor/OCP-018` -> `main`  
**Head commit:** `68ce7e9ad175b8602bc625a892c37584b60ad05f`  
**LLM finish:** `FinishReason.STOP` (prompt 4021, completion 778)  

## Detected issue

- **File**: `src/main/java/tools/jackson/core/JsonGenerator.java`
- **Entity**: `JsonGenerator.copyCurrentEvent` (class)
- **Lines (at detection time)**: L863–L905
- **Severity**: high
- **Confidence**: detected by 3 scan(s)

**Description.** Switch statement on token ID requires modification to handle new token types

**Reasoning.** The copyCurrentEvent method uses a switch statement based on token IDs. Adding new token types would require modifying this switch block, violating the Open/Closed Principle.

## Fix logic

- **Model**: `gemini-2.5-flash` (temperature 0.2)
- **Patch blocks**: 0

**Summary.** Remove redundant `copyCurrentStructure` method with switch statement, delegating full logic to `JsonStreamCopier`.

**Rationale.** The `JsonGenerator` class contained two `copyCurrentStructure` methods. One `public JsonParser copyCurrentStructure(JsonParser p)` correctly delegates to `JsonStreamCopier.copyCurrentStructure(p, this)`. The other `public void copyCurrentStructure(JsonParser p)` implemented similar logic using a switch statement on token IDs, violating the Open/Closed Principle (OCP) as new token types would require modifying this switch. By removing the redundant `void` method and its associated Javadoc, we centralize the stream copying logic within `JsonStreamCopier`, ensuring `JsonGenerator` is closed for modification with respect to new token types while maintaining existing behavior through the delegated public API.

## Apply error

```
no patch blocks produced by LLM
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/main/java/tools/jackson/core/JsonGenerator.java` | 2247 → - | 66 → - | 8.52 → - | 497 → - | 0 → - |

## Diff

*(no diff — patch was not applied)*
