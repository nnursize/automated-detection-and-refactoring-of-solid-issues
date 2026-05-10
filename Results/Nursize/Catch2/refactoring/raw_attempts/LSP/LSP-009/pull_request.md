# Refactor LSP-009 (LSP): Subclasses can disable mandatory data collection, leading to Undefined Behavi...

**Status:** `patch_failed`  
**Branch:** `refactor/LSP-009` -> `main`  
**Head commit:** `c4fb8fdc2847e98069506246b6cf6bdb5e597f83`  
**LLM finish:** `FinishReason.STOP` (prompt 4126, completion 422)  

## Detected issue

- **File**: `extras/catch_amalgamated.hpp`
- **Entity**: `CumulativeReporterBase` (class)
- **Lines (at detection time)**: L3497–L3535
- **Severity**: high
- **Confidence**: detected by 1 scan(s)

**Description.** Subclasses can disable mandatory data collection, leading to Undefined Behavior in the base class contract

**Reasoning.** Refused Bequest smell -> LSP violation because the base class provides protected flags (m_shouldStoreSuccesfulAssertions and m_shouldStoreFailedAssertions) that allow subclasses to opt-out of fulfilling the data collection contract. However, the base class's internal logic and its consumers (who interact with the resulting node tree) expect this data to be present. As noted in the source comments (line 3505), accessing this data when a subclass has opted out results in Undefined Behavior. This makes such subclasses non-substitutable for the base type in any context where the cumulative results are processed, as they break the expected postconditions of the event-handling methods.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 2
- **Files modified** (1): `extras/catch_amalgamated.hpp`

**Summary.** Remove opt-out flags from CumulativeReporterBase to enforce data collection contract

**Rationale.** The flags `m_shouldStoreSuccesfulAssertions` and `m_shouldStoreFailedAssertions` allowed subclasses to break the internal data structure consistency, leading to undefined behavior. By removing these flags and making the base class always store the necessary data, we ensure that the `SectionNode` tree is always fully populated, satisfying the Liskov Substitution Principle.

## Changes overview

_2 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `extras/catch_amalgamated.hpp` (11-line block → 4-line replacement)

**Replaces:**

```
        /**
         * Due to the way this base functions, it has to expand assertions up-front,
         * even if they are later unused (e.g. because the deriving reporter does
         * not report successful assertions, or because the deriving reporter does
         * not use assertion expansion at all). Derived classes can use two
         * customization points, `m_shouldStoreSuccesfulAssertions` and
         * `m_shouldStoreFailedAssertions`, to disable the expansion and gain extra
         * performance. **Accessing the assertion expansions if it wasn't stored is
         * UB.**
         */
        class CumulativeReporterBase : public ReporterBase {
```

**With:**

```
        /**
         * Due to the way this base functions, it has to expand assertions up-front.
         */
        class CumulativeReporterBase : public ReporterBase {
```

### 2. EDIT `extras/catch_amalgamated.hpp` (7-line block → 2-line replacement)

**Replaces:**

```
    protected:
        //! Should the cumulative base store the assertion expansion for successful assertions?
        bool m_shouldStoreSuccesfulAssertions = true;
        //! Should the cumulative base store the assertion expansion for failed assertions?
        bool m_shouldStoreFailedAssertions = true;

        // We need lazy construction here. We should probably refactor it
```

**With:**

```
    protected:
        // We need lazy construction here. We should probably refactor it
```

## Apply error

```
search_text not found in extras/catch_amalgamated.hpp (block 0)
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `extras/catch_amalgamated.hpp` | 10470 → - | 3 → - | 426.33 → - | 1277 → - | 0 → - |

## Diff

*(no diff — patch was not applied)*
