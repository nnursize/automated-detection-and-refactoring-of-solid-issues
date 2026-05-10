# Refactor SRP-027 (SRP): The generator includes complex logic for handling type identifiers, which inv...

**Status:** `patch_failed`  
**Branch:** `refactor/SRP-027` -> `main`  
**Head commit:** `cac9df339925a5da8321d916d8b9bbcb9ad732dc`  
**LLM finish:** `FinishReason.STOP` (prompt 4041, completion 3658)  

## Detected issue

- **File**: `src/main/java/tools/jackson/core/JsonGenerator.java`
- **Entity**: `JsonGenerator.writeTypeSuffix` (method)
- **Lines (at detection time)**: L1060–L1098
- **Severity**: high
- **Confidence**: detected by 1 scan(s)

**Description.** The generator includes complex logic for handling type identifiers, which involves semantic interpretation and structural modification beyond basic token generation.

**Reasoning.** Similar to `writeTypePrefix`, this method completes the type ID embedding process. It closes structural elements (objects/arrays) and writes the type ID in the appropriate location based on the `WritableTypeId` definition. This is part of the broader type ID handling responsibility, which is distinct from merely generating JSON tokens.

## Fix logic

- **Model**: `gemini-2.5-flash` (temperature 0.2)
- **Patch blocks**: 3
- **Files created** (2): `src/main/java/tools/jackson/core/DefaultTypeIdentifierWriter.java`, `src/main/java/tools/jackson/core/TypeIdentifierWriter.java`
- **Files modified** (1): `src/main/java/tools/jackson/core/JsonGenerator.java`

**Summary.** Extracted type ID handling logic from JsonGenerator into a dedicated TypeIdentifierWriter.

**Rationale.** The `JsonGenerator`'s `writeTypePrefix` and `writeTypeSuffix` methods contained complex logic for interpreting `WritableTypeId` and performing structural modifications (e.g., writing wrapper objects/arrays, properties) beyond basic token generation. This violated the Single Responsibility Principle. By extracting this logic into a new `TypeIdentifierWriter` interface and a `DefaultTypeIdentifierWriter` implementation, `JsonGenerator` now delegates this specialized responsibility, adhering more closely to its core role of generating JSON tokens. The public API and existing behavior are preserved through delegation.

## Changes overview

_3 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `src/main/java/tools/jackson/core/JsonGenerator.java` (145-line block → 37-line replacement)

**Replaces:**

```java
    public JsonGenerator writeTypeId(Object id) throws JacksonException {
        throw _constructWriteException("No native support for writing Type Ids");
    }

    /**
     * Replacement method for {@link #writeTypeId(Object)} which is called
     * regardless of whether format has native type ids. If it does have native
     * type ids, those are to be used (if configuration allows this), if not,
     * structural type id inclusion is to be used. For JSON, for example, no
     * native type ids exist and structural inclusion is always used.
     *<p>
     * NOTE: databind may choose to skip calling this method for some special cases
     * (and instead included type id via regular write methods and/or {@link #writeTypeId}
     * -- this is discouraged, but not illegal, and may be necessary as a work-around
     * in some cases.
     *
     * @param typeIdDef Full Type Id definition
     *
     * @return {@link WritableTypeId} for caller to retain and pass to matching
     *   {@link #writeTypeSuffix} call
     *
     * @throws JacksonIOException if there is an underlying I/O problem
     * @throws StreamWriteException for problems in encoding token stream
     */
    public WritableTypeId writeTypePrefix(WritableTypeId typeIdDef)
        throws JacksonException
    {
        final boolean wasStartObjectWritten = canWriteTypeId()
                ? _writeTypePrefixUsingNative(typeIdDef)
                : _writeTypePrefixUsingWrapper(typeIdDef);

        // And then possible start marker for value itself:
        switch (typeIdDef.valueShape) {
        case START_OBJECT:
            if (!wasStartObjectWritten) {
                writeStartObject(typeIdDef.forValue);
            }
            break;
        case START_ARRAY:
            writeStartArray(typeIdDef.forValue);
            break;
        default: // otherwise: no start marker
        }

        return typeIdDef;
    }

    /**
     * Writes a native type id (when supported by format).
     *
     * @return True if start of an object has been written, False otherwise.
     */
    protected boolean _writeTypePrefixUsingNative(WritableTypeId typeIdDef) throws JacksonException {
        typeIdDef.wrapperWritten = false;
        writeTypeId(typeIdDef.id);
        return false;
    }

    /**
     * Writes a wrapper for the type id if necessary.
... (85 more line(s) truncated)
```

**With:**

```java
>>>>>>> REPLACE
    public JsonGenerator writeTypeId(Object id) throws JacksonException {
        throw _constructWriteException("No native support for writing Type Ids");
    }

    protected TypeIdentifierWriter _typeIdentifierWriter = DefaultTypeIdentifierWriter.instance;

    /**
     * Replacement method for {@link #writeTypeId(Object)} which is called
     * regardless of whether format has native type ids. If it does have native
     * type ids, those are to be used (if configuration allows this), if not,
     * structural type id inclusion is to be used. For JSON, for example, no
     * native type ids exist and structural inclusion is always used.
     *<p>
     * NOTE: databind may choose to skip calling this method for some special cases
     * (and instead included type id via regular write methods and/or {@link #writeTypeId}
     * -- this is discouraged, but not illegal, and may be necessary as a work-around
     * in some cases.
     *
     * @param typeIdDef Full Type Id definition
     *
     * @return {@link WritableTypeId} for caller to retain and pass to matching
     *   {@link #writeTypeSuffix} call
     *
     * @throws JacksonIOException if there is an underlying I/O problem
     * @throws StreamWriteException for problems in encoding token stream
     */
    public WritableTypeId writeTypePrefix(WritableTypeId typeIdDef)
        throws JacksonException
    {
        return _typeIdentifierWriter.writeTypePrefix(this, typeIdDef);
    }
    
    public WritableTypeId writeTypeSuffix(WritableTypeId typeIdDef) throws JacksonException
    {
        return _typeIdentifierWriter.writeTypeSuffix(this, typeIdDef);
    }
```

### 2. CREATE `src/main/java/tools/jackson/core/TypeIdentifierWriter.java` (41 line(s))

```java
package tools.jackson.core;

/**
 * Interface that defines API for handlers that are responsible for writing
 * Type Identifiers (type ids) as part of serialization process.
 * This is typically used by databind to delegate actual writing of type ids
 * to {@link JsonGenerator} implementation.
 *
 * @since 3.0
 */
public interface TypeIdentifierWriter {
    /**
     * Method called to write the "prefix" of a Type Id, which is typically
     * a structural element (Object or Array start) or a property name.
     *
     * @param g Generator to use for writing tokens
     * @param typeIdDef Definition of Type Id to write
     *
     * @return {@link WritableTypeId} for caller to retain and pass to matching
     *   {@link #writeTypeSuffix} call
     *
     * @throws JacksonException if there is an underlying I/O problem
     * @throws StreamWriteException for problems in encoding token stream
     */
    WritableTypeId writeTypePrefix(JsonGenerator g, WritableTypeId typeIdDef) throws JacksonException;

    /**
     * Method called to write the "suffix" of a Type Id, which is typically
     * a structural element (Object or Array end).
     *
     * @param g Generator to use for writing tokens
     * @param typeIdDef Definition of Type Id to write
     *
     * @return {@link WritableTypeId} for caller to retain and pass to matching
     *   {@link #writeTypeSuffix} call
     *
     * @throws JacksonException if there is an underlying I/O problem
     * @throws StreamWriteException for problems in encoding token stream
     */
    WritableTypeId writeTypeSuffix(JsonGenerator g, WritableTypeId typeIdDef) throws JacksonException;
}
```

### 3. CREATE `src/main/java/tools/jackson/core/DefaultTypeIdentifierWriter.java` (132 line(s))

```java
package tools.jackson.core;

import java.util.Objects;

/**
 * Default implementation of {@link TypeIdentifierWriter} that provides
 * standard logic for writing type identifiers.
 *
 * @since 3.0
 */
public class DefaultTypeIdentifierWriter implements TypeIdentifierWriter {

    /**
     * Singleton instance of the default writer.
     */
    public static final DefaultTypeIdentifierWriter instance = new DefaultTypeIdentifierWriter();

    protected DefaultTypeIdentifierWriter() { }

    @Override
    public WritableTypeId writeTypePrefix(JsonGenerator g, WritableTypeId typeIdDef)
        throws JacksonException
    {
        final boolean wasStartObjectWritten = g.canWriteTypeId()
                ? _writeTypePrefixUsingNative(g, typeIdDef)
                : _writeTypePrefixUsingWrapper(g, typeIdDef);

        // And then possible start marker for value itself:
        switch (typeIdDef.valueShape) {
        case START_OBJECT:
            if (!wasStartObjectWritten) {
                g.writeStartObject(typeIdDef.forValue);
            }
            break;
        case START_ARRAY:
            g.writeStartArray(typeIdDef.forValue);
            break;
        default: // otherwise: no start marker
        }

        return typeIdDef;
    }

    @Override
    public WritableTypeId writeTypeSuffix(JsonGenerator g, WritableTypeId typeIdDef) throws JacksonException
    {
        final JsonToken valueShape = typeIdDef.valueShape;
        // First: does value need closing?
        if (valueShape == JsonToken.START_OBJECT) {
            g.writeEndObject();
        } else if (valueShape == JsonToken.START_ARRAY) {
            g.writeEndArray();
        }

        if (typeIdDef.wrapperWritten) {
            switch (typeIdDef.include) {
            case WRAPPER_ARRAY:
                g.writeEndArray();
                break;
            case PARENT_PROPERTY:
... (72 more line(s) truncated)
```

## Apply error

```
search_text not found in src/main/java/tools/jackson/core/JsonGenerator.java (block 0)
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/main/java/tools/jackson/core/JsonGenerator.java` | 2303 → - | 65 → - | 8.97 → - | 519 → - | 0 → - |

## Diff

*(no diff — patch was not applied)*
