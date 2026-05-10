# Refactor OCP-030 (OCP): Switch statement on Colour::Code enum violates OCP.

**Status:** `detection_rejected`  
**Branch:** `refactor/OCP-030` -> `main`  
**Head commit:** `017928ca08b9fa5c327391e5c70d8798c14ddeb2`  

## Detected issue

- **File**: `extras/catch_amalgamated.cpp`
- **Entity**: `ANSIColourImpl.use` (method)
- **Lines (at detection time)**: L3670–L3697
- **Severity**: high
- **Confidence**: detected by 1 scan(s)

**Description.** Switch statement on Colour::Code enum violates OCP.

**Reasoning.** Similar to Win32ColourImpl, the 'use' method in ANSIColourImpl contains a switch statement that dispatches logic based on the 'Colour::Code' enum. This directly violates OCP because introducing a new color code would necessitate modifying and recompiling this existing method, rather than extending the system with new behavior without altering existing code.

## Detection label

- **Label**: `false`

## Diff

*(no diff — patch was not applied)*
