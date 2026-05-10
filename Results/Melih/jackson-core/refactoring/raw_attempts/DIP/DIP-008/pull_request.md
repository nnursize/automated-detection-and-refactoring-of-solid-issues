# Refactor DIP-008 (DIP): Concrete parser implementation depends on a concrete symbol table implementation

**Status:** `applied_unverified`  
**Branch:** `refactor/DIP-008` -> `main`  
**Head commit:** `70ee934d5eea670f5238a219cd3df955090a48c2`  
**LLM finish:** `FinishReason.STOP` (prompt 7831, completion 684)  

## Detected issue

- **File**: `src/main/java/tools/jackson/core/json/ReaderBasedJsonParser.java`
- **Entity**: `ReaderBasedJsonParser` (class)
- **Lines (at detection time)**: L116–L130
- **Severity**: medium
- **Confidence**: detected by 2 scan(s)

**Description.** Concrete parser implementation depends on a concrete symbol table implementation

**Reasoning.** Rigid Coupling smell -> Similar to the UTF-8 parser, the ReaderBasedJsonParser depends on the concrete CharsToNameCanonicalizer. This prevents the inversion of control where different canonicalization strategies could be injected through a common interface or abstraction.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 5
- **Files created** (1): `src/main/java/tools/jackson/core/sym/NameCanonicalizer.java`
- **Files modified** (2): `src/main/java/tools/jackson/core/json/ReaderBasedJsonParser.java`, `src/main/java/tools/jackson/core/sym/CharsToNameCanonicalizer.java`

**Summary.** Introduce NameCanonicalizer interface to decouple ReaderBasedJsonParser from concrete CharsToNameCanonicalizer

**Rationale.** The ReaderBasedJsonParser was tightly coupled to the concrete CharsToNameCanonicalizer class. By introducing a NameCanonicalizer interface (or using the existing one if applicable, but here we define the abstraction) and updating the parser to depend on this interface, we adhere to the Dependency Inversion Principle. Note: Since CharsToNameCanonicalizer is a complex class, I am creating a NameCanonicalizer interface that it will implement, and updating the parser to use this interface.

## Changes overview

_5 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `src/main/java/tools/jackson/core/sym/CharsToNameCanonicalizer.java` (2-line block → 3-line replacement)

**Replaces:**

```java
public final class CharsToNameCanonicalizer
{
```

**With:**

```java
public final class CharsToNameCanonicalizer
    implements NameCanonicalizer
{
```

### 2. EDIT `src/main/java/tools/jackson/core/json/ReaderBasedJsonParser.java` (1-line block → 1-line replacement)

**Replaces:**

```java
    protected final CharsToNameCanonicalizer _symbols;
```

**With:**

```java
    protected final tools.jackson.core.sym.NameCanonicalizer _symbols;
```

### 3. EDIT `src/main/java/tools/jackson/core/json/ReaderBasedJsonParser.java` (5-line block → 5-line replacement)

**Replaces:**

```java
    public ReaderBasedJsonParser(ObjectReadContext readCtxt, IOContext ctxt,
            int stdFeatures, int formatFeatures, Reader r,
            CharsToNameCanonicalizer st,
            char[] inputBuffer, int start, int end,
            boolean bufferRecyclable)
```

**With:**

```java
    public ReaderBasedJsonParser(ObjectReadContext readCtxt, IOContext ctxt,
            int stdFeatures, int formatFeatures, Reader r,
            tools.jackson.core.sym.NameCanonicalizer st,
            char[] inputBuffer, int start, int end,
            boolean bufferRecyclable)
```

### 4. EDIT `src/main/java/tools/jackson/core/json/ReaderBasedJsonParser.java` (3-line block → 3-line replacement)

**Replaces:**

```java
    public ReaderBasedJsonParser(ObjectReadContext readCtxt, IOContext ctxt,
            int stdFeatures, int formatFeatures, Reader r,
            CharsToNameCanonicalizer st)
```

**With:**

```java
    public ReaderBasedJsonParser(ObjectReadContext readCtxt, IOContext ctxt,
            int stdFeatures, int formatFeatures, Reader r,
            tools.jackson.core.sym.NameCanonicalizer st)
```

### 5. CREATE `src/main/java/tools/jackson/core/sym/NameCanonicalizer.java` (6 line(s))

```java
package tools.jackson.core.sym;

public interface NameCanonicalizer {
    int hashSeed();
    void release();
}
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/main/java/tools/jackson/core/json/ReaderBasedJsonParser.java` | 2604 → 2604 | 85 → 85 | 9.92 → 9.92 | 759 → 759 | 0 → 0 |
| `src/main/java/tools/jackson/core/sym/CharsToNameCanonicalizer.java` | - → 741 | - → 26 | - → 6.23 | - → 137 | - → 0 |
| `src/main/java/tools/jackson/core/sym/NameCanonicalizer.java` | - → 5 | - → 0 | - → 1 | - → 1 | - → 0 |

## Diff

```diff
diff --git a/src/main/java/tools/jackson/core/json/ReaderBasedJsonParser.java b/src/main/java/tools/jackson/core/json/ReaderBasedJsonParser.java
index 9b40c94..601359f 100644
--- a/src/main/java/tools/jackson/core/json/ReaderBasedJsonParser.java
+++ b/src/main/java/tools/jackson/core/json/ReaderBasedJsonParser.java
@@ -70,7 +70,7 @@ public class ReaderBasedJsonParser
     /**********************************************************************
      */
 
-    protected final CharsToNameCanonicalizer _symbols;
+    protected final tools.jackson.core.sym.NameCanonicalizer _symbols;
 
     protected final int _hashSeed;
 
@@ -124,7 +124,7 @@ public class ReaderBasedJsonParser
      */
     public ReaderBasedJsonParser(ObjectReadContext readCtxt, IOContext ctxt,
             int stdFeatures, int formatFeatures, Reader r,
-            CharsToNameCanonicalizer st,
+            tools.jackson.core.sym.NameCanonicalizer st,
             char[] inputBuffer, int start, int end,
             boolean bufferRecyclable)
     {
@@ -155,7 +155,7 @@ public class ReaderBasedJsonParser
      */
     public ReaderBasedJsonParser(ObjectReadContext readCtxt, IOContext ctxt,
             int stdFeatures, int formatFeatures, Reader r,
-            CharsToNameCanonicalizer st)
+            tools.jackson.core.sym.NameCanonicalizer st)
     {
         super(readCtxt, ctxt, stdFeatures, formatFeatures);
         _reader = r;
diff --git a/src/main/java/tools/jackson/core/sym/CharsToNameCanonicalizer.java b/src/main/java/tools/jackson/core/sym/CharsToNameCanonicalizer.java
index d6969d5..4f64604 100644
--- a/src/main/java/tools/jackson/core/sym/CharsToNameCanonicalizer.java
+++ b/src/main/java/tools/jackson/core/sym/CharsToNameCanonicalizer.java
@@ -46,6 +46,7 @@ import tools.jackson.core.util.InternCache;
  * access to master instance is read-only (i.e. no modifications done).
  */
 public final class CharsToNameCanonicalizer
+    implements NameCanonicalizer
 {
     /* If we use "multiply-add" based hash algorithm, this is the multiplier
      * we use.
diff --git a/src/main/java/tools/jackson/core/sym/NameCanonicalizer.java b/src/main/java/tools/jackson/core/sym/NameCanonicalizer.java
new file mode 100644
index 0000000..0000000
--- /dev/null
+++ b/src/main/java/tools/jackson/core/sym/NameCanonicalizer.java
@@ -0,0 +1,6 @@
+package tools.jackson.core.sym;
+
+public interface NameCanonicalizer {
+    int hashSeed();
+    void release();
+}
\ No newline at end of file

```
