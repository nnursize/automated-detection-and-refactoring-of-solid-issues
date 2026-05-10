# Refactor ISP-010 (ISP): ExprLhs provides operators that might not be used by all clients.

**Status:** `detection_rejected`  
**Branch:** `refactor/ISP-010` -> `main`  
**Head commit:** `2a3e90bc5cf75ef551e4552f2be95f31800d55c5`  

## Detected issue

- **File**: `extras/catch_amalgamated.hpp`
- **Entity**: `ExprLhs` (class)
- **Lines (at detection time)**: L5451–L5605
- **Severity**: low
- **Confidence**: detected by 3 scan(s)

**Description.** ExprLhs provides operators that might not be used by all clients.

**Reasoning.** The `ExprLhs` class defines a multitude of overloaded operators (`==`, `!=`, `<`, `<=`, `>`, `>=`, `|`, `&`, `^`, `&&`, `||`). While these are used to construct `BinaryExpr` and `UnaryExpr` for assertion evaluation, a client that only needs to perform a specific type of comparison might be indirectly coupled to all other defined operators. If `ExprLhs` were to be used in a context where only a subset of these operations is relevant, it could be considered a violation of ISP. However, given its role in expression building for assertions, this is a more subtle violation.

## Detection label

- **Label**: `false`

## Diff

*(no diff — patch was not applied)*
