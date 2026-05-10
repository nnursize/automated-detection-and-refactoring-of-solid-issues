# Refactor SRP-048 (SRP): The ExprLhs class combines expression decomposition with early test failure l...

**Status:** `detection_rejected`  
**Branch:** `refactor/SRP-048` -> `main`  
**Head commit:** `35e191d1c2f08e9b285da19cba8ba76d54d727e1`  

## Detected issue

- **File**: `src/catch2/internal/catch_decomposer.hpp`
- **Entity**: `ExprLhs` (class)
- **Lines (at detection time)**: L285–L439
- **Severity**: medium
- **Confidence**: detected by 2 scan(s)

**Description.** The ExprLhs class combines expression decomposition with early test failure logic for specific comparison patterns.

**Reasoning.** Its primary role is to capture the left-hand side of an expression and, through overloaded operators, construct `BinaryExpr` objects for later evaluation. However, some operator overloads (specifically for `is_eq_0_comparable` cases) also contain `throw_test_failure_exception()` calls, introducing a responsibility for enforcing specific semantic rules and potentially short-circuiting test execution. This mixes expression representation with test control flow.

## Detection label

- **Label**: `false`

## Diff

*(no diff — patch was not applied)*
