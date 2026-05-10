# Refactor LSP-004 (LSP): Base class uses type-querying methods to distinguish subtypes.

**Status:** `patch_failed`  
**Branch:** `refactor/LSP-004` -> `main`  
**Head commit:** `d878a9f6a7d33b8a9f689f8c4f980f1a9c6889e4`  
**LLM finish:** `FinishReason.STOP` (prompt 2925, completion 232)  

## Detected issue

- **File**: `extras/catch_amalgamated.hpp`
- **Entity**: `Catch::ITransientExpression` (class)
- **Lines (at detection time)**: L1845–L1868
- **Severity**: medium
- **Confidence**: detected by 2 scan(s)

**Description.** Base class uses type-querying methods to distinguish subtypes.

**Reasoning.** The base class ITransientExpression includes the method isBinaryExpression(). This pattern of 'Type Tagging' or manual type querying suggests that consumers of the interface are expected to branch logic based on the concrete subtype rather than relying on polymorphic behavior. Subtypes should be substitutable without the caller needing to query their specific nature.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `extras/catch_amalgamated.hpp`

**Summary.** Remove type-querying method from ITransientExpression to adhere to LSP

**Rationale.** The ITransientExpression interface contained a type-querying method (isBinaryExpression) which forces consumers to perform manual type checking, violating the Liskov Substitution Principle. Removing this method encourages polymorphic usage of the interface.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `extras/catch_amalgamated.hpp` (7-line block → 6-line replacement)

**Replaces:**

```
    class ITransientExpression {
    public:
        virtual ~ITransientExpression();
        virtual bool isBinaryExpression() const = 0;
        virtual bool getResult() const = 0;
        virtual void streamReconstructedExpression( std::ostream& os ) const = 0;
    };
```

**With:**

```
    class ITransientExpression {
    public:
        virtual ~ITransientExpression();
        virtual bool getResult() const = 0;
        virtual void streamReconstructedExpression( std::ostream& os ) const = 0;
    };
```

## Apply error

```
search_text not found in extras/catch_amalgamated.hpp (block 0)
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `extras/catch_amalgamated.hpp` | 10485 → - | 3 → - | 428.33 → - | 1283 → - | 0 → - |

## Diff

*(no diff — patch was not applied)*
