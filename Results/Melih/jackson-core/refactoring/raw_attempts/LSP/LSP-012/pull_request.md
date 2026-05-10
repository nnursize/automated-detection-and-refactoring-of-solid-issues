# Refactor LSP-012 (LSP): Abstract methods in a base class force subclasses into a specific non-blockin...

**Status:** `detection_rejected`  
**Branch:** `refactor/LSP-012` -> `main`  
**Head commit:** `c445684d3c509e85f30ab38aa81d30048b3bda64`  

## Detected issue

- **File**: `src/main/java/tools/jackson/core/json/async/NonBlockingJsonParserBase.java`
- **Entity**: `NonBlockingJsonParserBase.getNextSignedByteFromBuffer` (class)
- **Lines (at detection time)**: L172–L172
- **Severity**: high
- **Confidence**: detected by 1 scan(s)

**Description.** Abstract methods in a base class force subclasses into a specific non-blocking contract that violates the standard JsonParser contract.

**Reasoning.** The introduction of abstract methods like getNextSignedByteFromBuffer forces subclasses to implement a specific non-blocking state machine, which is not part of the standard JsonParser interface, breaking the ability to treat all JsonParsers uniformly.

## Detection label

- **Label**: `false`

The cited method getNextSignedByteFromBuffer does not exist in NonBlockingJsonParserBase. The method is actually defined in concrete subclasses (NonBlockingByteArrayJsonParser, NonBlockingByteBufferJsonParser) and NonBlockingJsonParserBase itself only declares one abstract method (releaseBuffered). The detection cites the wrong class.

## Diff

*(no diff — patch was not applied)*
