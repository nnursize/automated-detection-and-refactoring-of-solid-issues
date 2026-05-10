# Refactor LSP-002 (LSP): Subclass implementation of _closeInput() is a no-op, violating the expected c...

**Status:** `detection_rejected`  
**Branch:** `refactor/LSP-002` -> `main`  
**Head commit:** `c445684d3c509e85f30ab38aa81d30048b3bda64`  

## Detected issue

- **File**: `src/main/java/tools/jackson/core/json/UTF8DataInputJsonParser.java`
- **Entity**: `UTF8DataInputJsonParser._closeInput` (method)
- **Lines (at detection time)**: L113–L113
- **Severity**: medium
- **Confidence**: detected by 5 scan(s)

**Description.** Subclass implementation of _closeInput() is a no-op, violating the expected cleanup contract.

**Reasoning.** The base class JsonParserBase defines _closeInput() as a protected method responsible for releasing resources. By providing an empty implementation, the subclass fails to perform necessary cleanup of the DataInput source, which violates the postcondition of the base class method contract.

## Detection label

- **Label**: `false`

The DataInput interface does not extend Closeable, so there is no resource to close. A no-op _closeInput() is the only correct implementation — there is no base class postcondition being violated. The detection incorrectly assumes DataInput is a closeable resource.

## Diff

*(no diff — patch was not applied)*
