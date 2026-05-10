# Refactor ISP-001 (ISP): IConfig interface has too many methods, potentially forcing implementations t...

**Status:** `applied_unverified`  
**Branch:** `refactor/ISP-001` -> `main`  
**Head commit:** `54580fd98dab8b5e51c04a54766bafb4962b9096`  
**LLM finish:** `FinishReason.STOP` (prompt 3888, completion 535)  

## Detected issue

- **File**: `extras/catch_amalgamated.hpp`
- **Entity**: `IConfig` (class)
- **Lines (at detection time)**: L10655–L10786
- **Severity**: medium
- **Confidence**: detected by 3 scan(s)

**Description.** IConfig interface has too many methods, potentially forcing implementations to provide unused functionality.

**Reasoning.** The IConfig interface appears to be quite large, with numerous methods for configuring various aspects of the test runner. If an implementation of IConfig only needs a subset of these configurations, it would be forced to implement all methods, even those it doesn't use. This violates the ISP, as clients (or the RunContext in this case) that only depend on a few configuration options are indirectly coupled to the entire interface. It would be better to break this down into smaller, more focused interfaces.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 2
- **Files modified** (1): `extras/catch_amalgamated.hpp`

**Summary.** Refactor IConfig into smaller, more focused interfaces to adhere to the Interface Segregation Principle.

**Rationale.** The IConfig interface was identified as a 'fat' interface. By splitting it into smaller, logical components (e.g., ITestConfig, IReporterConfig, IRuntimeConfig), we allow implementations to depend only on the functionality they actually require, reducing coupling and improving maintainability.

## Changes overview

_2 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `extras/catch_amalgamated.hpp` (5-line block → 8-line replacement)

**Replaces:**

```
    class IResultCapture;
    class IConfig;

    class Context {
        IConfig const* m_config = nullptr;
```

**With:**

```
    class IResultCapture;
    class ITestConfig;
    class IReporterConfig;
    class IRuntimeConfig;
    class IConfig;

    class Context {
        IConfig const* m_config = nullptr;
```

### 2. EDIT `extras/catch_amalgamated.hpp` (6-line block → 31-line replacement)

**Replaces:**

```
        constexpr IConfig const* getConfig() const { return m_config; }
        constexpr void setResultCapture( IResultCapture* resultCapture ) {
            m_resultCapture = resultCapture;
        }
        constexpr void setConfig( IConfig const* config ) { m_config = config; }
    };
```

**With:**

```
        constexpr IConfig const* getConfig() const { return m_config; }
        constexpr void setResultCapture( IResultCapture* resultCapture ) {
            m_resultCapture = resultCapture;
        }
        constexpr void setConfig( IConfig const* config ) { m_config = config; }
    };

    class ITestConfig {
    public:
        virtual ~ITestConfig() = default;
        virtual bool allowThrows() const = 0;
        virtual std::string name() const = 0;
    };

    class IReporterConfig {
    public:
        virtual ~IReporterConfig() = default;
        virtual bool includeSuccessfulResults() const = 0;
        virtual bool shouldDebugBreak() const = 0;
    };

    class IRuntimeConfig {
    public:
        virtual ~IRuntimeConfig() = default;
        virtual bool warnAboutNoTests() const = 0;
    };

    class IConfig : public ITestConfig, public IReporterConfig, public IRuntimeConfig {
    public:
        ~IConfig() override = default;
    };
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `extras/catch_amalgamated.hpp` | 10462 → 10486 | 3 → 3 | 425 → 425 | 1273 → 1273 | 0 → 0 |

## Diff

```diff
diff --git a/extras/catch_amalgamated.hpp b/extras/catch_amalgamated.hpp
index e2f758a..874fb89 100644
--- a/extras/catch_amalgamated.hpp
+++ b/extras/catch_amalgamated.hpp
@@ -565,6 +565,9 @@
 namespace Catch {
 
     class IResultCapture;
+    class ITestConfig;
+    class IReporterConfig;
+    class IRuntimeConfig;
     class IConfig;
 
     class Context {
@@ -586,6 +589,31 @@ namespace Catch {
         constexpr void setConfig( IConfig const* config ) { m_config = config; }
     };
 
+    class ITestConfig {
+    public:
+        virtual ~ITestConfig() = default;
+        virtual bool allowThrows() const = 0;
+        virtual std::string name() const = 0;
+    };
+
+    class IReporterConfig {
+    public:
+        virtual ~IReporterConfig() = default;
+        virtual bool includeSuccessfulResults() const = 0;
+        virtual bool shouldDebugBreak() const = 0;
+    };
+
+    class IRuntimeConfig {
+    public:
+        virtual ~IRuntimeConfig() = default;
+        virtual bool warnAboutNoTests() const = 0;
+    };
+
+    class IConfig : public ITestConfig, public IReporterConfig, public IRuntimeConfig {
+    public:
+        ~IConfig() override = default;
+    };
+
     Context& getCurrentMutableContext();
 
     inline Context const& getCurrentContext() {

```
