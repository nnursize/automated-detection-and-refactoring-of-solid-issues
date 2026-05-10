# Refactor OCP-037 (OCP): The `use` method employs a switch statement on `Colour::Code`, violating OCP.

**Status:** `detection_rejected`  
**Branch:** `refactor/OCP-037` -> `main`  
**Head commit:** `017928ca08b9fa5c327391e5c70d8798c14ddeb2`  

## Detected issue

- **File**: `extras/catch_amalgamated.cpp`
- **Entity**: `Win32ColourImpl::use` (method)
- **Lines (at detection time)**: L3591–L3611
- **Severity**: high
- **Confidence**: detected by 1 scan(s)

**Description.** The `use` method employs a switch statement on `Colour::Code`, violating OCP.

**Reasoning.** The `Win32ColourImpl::use` method (and similarly `ANSIColourImpl::use` in L3670-L3697) uses a `switch` statement to apply different console colors based on a `Colour::Code` enum. This design means that if a new `Colour::Code` is introduced (extension), the `use` method must be modified (adding a new `case` branch). This is a classic violation of OCP, as it makes the existing code not closed for modification when new color types are added. A more extensible design would use polymorphism, where each `Colour::Code` could correspond to a specific `IColourStrategy` object, and adding new colors would involve creating a new strategy without modifying existing code.

## Detection label

- **Label**: `false`

## Diff

*(no diff — patch was not applied)*
