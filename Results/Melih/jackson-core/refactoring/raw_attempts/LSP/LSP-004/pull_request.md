# Refactor LSP-004 (LSP): Method signature in subclass forces checked exception handling not present in...

**Status:** `detection_rejected`  
**Branch:** `refactor/LSP-004` -> `main`  
**Head commit:** `c445684d3c509e85f30ab38aa81d30048b3bda64`  

## Detected issue

- **File**: `src/main/java/tools/jackson/core/json/ReaderBasedJsonParser.java`
- **Entity**: `ReaderBasedJsonParser._decodeEscaped` (method)
- **Lines (at detection time)**: L1056–L1062
- **Severity**: medium
- **Confidence**: detected by 4 scan(s)

**Description.** Method signature in subclass forces checked exception handling not present in base class.

**Reasoning.** While the method is protected, the pattern of catching IOException and wrapping it into a JacksonException is inconsistent across parser implementations. In this specific case, the implementation relies on the base class behavior but forces a wrapper that alters the signature expectations of internal components.

## Detection label

- **Label**: `false`

ReaderBasedJsonParser._decodeEscaped() at line 2653 provides a full, correct implementation that parses escape sequences and declares the same 'throws JacksonException' as the base class. There is no exception wrapping mismatch or contract alteration. The reasoning was confused and does not match the actual code.

## Diff

*(no diff — patch was not applied)*
