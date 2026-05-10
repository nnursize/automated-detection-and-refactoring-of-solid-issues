# Refactor OCP-027 (OCP): Switch statement on `Colour::Code` in `use` method, violating OCP.

**Status:** `detection_rejected`  
**Branch:** `refactor/OCP-027` -> `main`  
**Head commit:** `851b4f2cf0e00bbe1cd47018b1837e2247af8f88`  

## Detected issue

- **File**: `extras/catch_amalgamated.cpp`
- **Entity**: `Win32ColourImpl.use` (method)
- **Lines (at detection time)**: L3591–L3611
- **Severity**: high
- **Confidence**: detected by 2 scan(s)

**Description.** Switch statement on `Colour::Code` in `use` method, violating OCP.

**Reasoning.** The `Win32ColourImpl::use` method contains a `switch` statement that dispatches logic based on `Colour::Code`. If a new `Colour::Code` is added to the system, this `switch` statement must be modified to include the new case, requiring changes to existing code. This directly violates the Open/Closed Principle, as the class is not closed for modification when new color types are introduced. A more OCP-compliant design would use a polymorphic approach where each color type is an object that encapsulates its specific behavior.

## Detection label

- **Label**: `false`

## Diff

*(no diff — patch was not applied)*
