# Refactor LSP-112 (LSP): Subtype strengthens precondition by restricting input types not specified in...

**Status:** `applied_unverified`  
**Branch:** `refactor/LSP-112` -> `main`  
**Head commit:** `222eae250a0a4feb4064c8fb9cf8f3b5d4154aba`  
**LLM finish:** `FinishReason.STOP` (prompt 5636, completion 253)  

## Detected issue

- **File**: `proto/src/main/java/com/google/gson/protobuf/ProtoTypeAdapter.java`
- **Entity**: `ProtoTypeAdapter.deserialize` (method)
- **Lines (at detection time)**: L295–L295
- **Severity**: medium
- **Confidence**: detected by 3 scan(s)

**Description.** Subtype strengthens precondition by restricting input types not specified in the base interface.

**Reasoning.** `ProtoTypeAdapter` implements `JsonDeserializer<Message>`. Its `deserialize` method throws an `IllegalStateException` with the message 'only generated messages are supported'. The `JsonDeserializer` interface's `deserialize` method contract does not specify such a restriction on the `Message` type. By imposing this stronger precondition, `ProtoTypeAdapter` violates LSP, as it cannot be substituted for a general `JsonDeserializer<Message>` without potentially causing unexpected runtime errors for clients providing non-generated `Message` types.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `proto/src/main/java/com/google/gson/protobuf/ProtoTypeAdapter.java`

**Summary.** Remove the unsupported DynamicMessage check in ProtoTypeAdapter.deserialize

**Rationale.** The check for DynamicMessage was an arbitrary restriction that violated the Liskov Substitution Principle by narrowing the contract of the JsonDeserializer interface. Removing it allows the adapter to attempt deserialization for any Message type, which is consistent with the interface contract.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `proto/src/main/java/com/google/gson/protobuf/ProtoTypeAdapter.java` (8-line block → 4-line replacement)

**Replaces:**

```java
      @SuppressWarnings("unchecked")
      Class<? extends Message> protoClass = (Class<? extends Message>) typeOfT;

      if (DynamicMessage.class.isAssignableFrom(protoClass)) {
        throw new IllegalStateException("only generated messages are supported");
      }

      // Invoke the ProtoClass.newBuilder() method
```

**With:**

```java
      @SuppressWarnings("unchecked")
      Class<? extends Message> protoClass = (Class<? extends Message>) typeOfT;

      // Invoke the ProtoClass.newBuilder() method
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `proto/src/main/java/com/google/gson/protobuf/ProtoTypeAdapter.java` | 404 → 401 | 14 → 14 | 4.64 → 4.57 | 52 → 51 | 0 → 0 |

## Diff

```diff
diff --git a/proto/src/main/java/com/google/gson/protobuf/ProtoTypeAdapter.java b/proto/src/main/java/com/google/gson/protobuf/ProtoTypeAdapter.java
index 620046a..4f99233 100644
--- a/proto/src/main/java/com/google/gson/protobuf/ProtoTypeAdapter.java
+++ b/proto/src/main/java/com/google/gson/protobuf/ProtoTypeAdapter.java
@@ -291,10 +291,6 @@ public class ProtoTypeAdapter implements JsonSerializer<Message>, JsonDeserializ
       @SuppressWarnings("unchecked")
       Class<? extends Message> protoClass = (Class<? extends Message>) typeOfT;
 
-      if (DynamicMessage.class.isAssignableFrom(protoClass)) {
-        throw new IllegalStateException("only generated messages are supported");
-      }
-
       // Invoke the ProtoClass.newBuilder() method
       Message.Builder protoBuilder =
           (Message.Builder) getCachedMethod(protoClass, "newBuilder").invoke(null);

```
