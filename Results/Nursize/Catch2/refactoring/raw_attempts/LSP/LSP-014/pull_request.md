# Refactor LSP-014 (LSP): Class Column is used as a base class for Spacer but lacks a virtual destructor.

**Status:** `detection_rejected`  
**Branch:** `refactor/LSP-014` -> `main`  
**Head commit:** `3649d6b45268af01f256aa903a2d14a1b3c3de44`  

## Detected issue

- **File**: `third_party/clara.hpp`
- **Entity**: `Column` (class)
- **Lines (at detection time)**: L71–L241
- **Severity**: high
- **Confidence**: detected by 1 scan(s)

**Description.** Class Column is used as a base class for Spacer but lacks a virtual destructor.

**Reasoning.** The Liskov Substitution Principle requires that subtypes be substitutable for their base types. In C++, if a subclass (like Spacer) is deleted through a pointer to a base class (Column) that lacks a virtual destructor, the resulting behavior is undefined. This prevents safe polymorphic substitution in any context involving dynamic memory management and base-class pointers.

## Detection label

- **Label**: `false`

## Diff

*(no diff — patch was not applied)*
