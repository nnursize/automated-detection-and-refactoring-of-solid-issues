# Refactor LSP-012 (LSP): Subclass-driven state changes lead to Undefined Behavior in base class contract

**Status:** `applied_unverified`  
**Branch:** `refactor/LSP-012` -> `main`  
**Head commit:** `0143d25da3ee2b47a8fb7462f83a2de2fdb86bc0`  
**LLM finish:** `FinishReason.STOP` (prompt 4102, completion 617)  

## Detected issue

- **File**: `extras/catch_amalgamated.hpp`
- **Entity**: `Catch::CumulativeReporterBase` (class)
- **Lines (at detection time)**: L5078–L5128
- **Severity**: high
- **Confidence**: detected by 1 scan(s)

**Description.** Subclass-driven state changes lead to Undefined Behavior in base class contract

**Reasoning.** The class documentation explicitly states that subclasses can set 'm_shouldStoreSuccesfulAssertions' or 'm_shouldStoreFailedAssertions' to false, but that 'Accessing the assertion expansions if it wasn't stored is UB.' This is a postcondition weakening smell. A consumer using a pointer to the base class CumulativeReporterBase expects a valid contract where assertion data is available. If a subclass weakens this postcondition by disabling storage, it breaks the program's correctness for any component relying on the base class's standard behavior, fulfilling the definition of an LSP violation.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 2
- **Files modified** (1): `extras/catch_amalgamated.hpp`

**Summary.** Remove UB-inducing customization points from CumulativeReporterBase

**Rationale.** The customization points m_shouldStoreSuccesfulAssertions and m_shouldStoreFailedAssertions allowed subclasses to disable storage, which caused Undefined Behavior when accessing assertion data. Removing these flags ensures the base class contract is always satisfied, adhering to the Liskov Substitution Principle.

## Changes overview

_2 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `extras/catch_amalgamated.hpp` (21-line block → 12-line replacement)

**Replaces:**

```
    /**
     * Utility base for reporters that need to handle all results at once
     *
     * It stores tree of all test cases, sections and assertions, and after the
     * test run is finished, calls into `testRunEndedCumulative` to pass the
     * control to the deriving class.
     *
     * If you are deriving from this class and override any testing related
     * member functions, you should first call into the base's implementation to
     * avoid breaking the tree construction.
     *
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
     * Utility base for reporters that need to handle all results at once
     *
     * It stores tree of all test cases, sections and assertions, and after the
     * test run is finished, calls into `testRunEndedCumulative` to pass the
     * control to the deriving class.
     *
     * If you are deriving from this class and override any testing related
     * member functions, you should first call into the base's implementation to
     * avoid breaking the tree construction.
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

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `extras/catch_amalgamated.hpp` | 10470 → 10459 | 3 → 3 | 426.33 → 425 | 1277 → 1273 | 0 → 0 |

## Diff

```diff
diff --git a/extras/catch_amalgamated.hpp b/extras/catch_amalgamated.hpp
index b589142..c9df2ab 100644
--- a/extras/catch_amalgamated.hpp
+++ b/extras/catch_amalgamated.hpp
@@ -13489,15 +13489,6 @@ namespace Catch {
      * If you are deriving from this class and override any testing related
      * member functions, you should first call into the base's implementation to
      * avoid breaking the tree construction.
-     *
-     * Due to the way this base functions, it has to expand assertions up-front,
-     * even if they are later unused (e.g. because the deriving reporter does
-     * not report successful assertions, or because the deriving reporter does
-     * not use assertion expansion at all). Derived classes can use two
-     * customization points, `m_shouldStoreSuccesfulAssertions` and
-     * `m_shouldStoreFailedAssertions`, to disable the expansion and gain extra
-     * performance. **Accessing the assertion expansions if it wasn't stored is
-     * UB.**
      */
     class CumulativeReporterBase : public ReporterBase {
     public:
@@ -13564,11 +13555,6 @@ namespace Catch {
         void skipTest(TestCaseInfo const&) override {}
 
     protected:
-        //! Should the cumulative base store the assertion expansion for successful assertions?
-        bool m_shouldStoreSuccesfulAssertions = true;
-        //! Should the cumulative base store the assertion expansion for failed assertions?
-        bool m_shouldStoreFailedAssertions = true;
-
         // We need lazy construction here. We should probably refactor it
         // later, after the events are redone.
         //! The root node of the test run tree.

```
