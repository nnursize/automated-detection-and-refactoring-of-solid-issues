# Refactor ISP-022 (ISP): Context class exposes methods for both IResultCapture and IConfig, potentiall...

**Status:** `applied_unverified`  
**Branch:** `refactor/ISP-022` -> `main`  
**Head commit:** `2a3e90bc5cf75ef551e4552f2be95f31800d55c5`  
**LLM finish:** `FinishReason.STOP` (prompt 3807, completion 513)  

## Detected issue

- **File**: `extras/catch_amalgamated.hpp`
- **Entity**: `Context` (class)
- **Lines (at detection time)**: L569–L587
- **Severity**: low
- **Confidence**: detected by 3 scan(s)

**Description.** Context class exposes methods for both IResultCapture and IConfig, potentially forcing clients to depend on unused interfaces.

**Reasoning.** The Context class has methods like getResultCapture() and getConfig() which return pointers to IResultCapture and IConfig respectively. If a client only needs one of these, it still depends on the Context class which aggregates both. This could be seen as a violation of ISP if Context is considered an 'interface' in itself, and clients are forced to depend on methods they don't use.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `extras/catch_amalgamated.hpp`

**Summary.** Split Context into IResultCaptureProvider and IConfigProvider to adhere to ISP

**Rationale.** The Context class was acting as a 'fat' interface provider. By introducing IResultCaptureProvider and IConfigProvider, clients can now depend on only the specific functionality they require, adhering to the Interface Segregation Principle.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `extras/catch_amalgamated.hpp` (18-line block → 30-line replacement)

**Replaces:**

```
    class Context {
        IConfig const* m_config = nullptr;
        IResultCapture* m_resultCapture = nullptr;

        CATCH_EXPORT static Context currentContext;
        friend Context& getCurrentMutableContext();
        friend Context const& getCurrentContext();

    public:
        constexpr IResultCapture* getResultCapture() const {
            return m_resultCapture;
        }
        constexpr IConfig const* getConfig() const { return m_config; }
        constexpr void setResultCapture( IResultCapture* resultCapture ) {
            m_resultCapture = resultCapture;
        }
        constexpr void setConfig( IConfig const* config ) { m_config = config; }
    };
```

**With:**

```
    class IResultCaptureProvider {
    public:
        virtual ~IResultCaptureProvider() = default;
        virtual IResultCapture* getResultCapture() const = 0;
    };

    class IConfigProvider {
    public:
        virtual ~IConfigProvider() = default;
        virtual IConfig const* getConfig() const = 0;
    };

    class Context : public IResultCaptureProvider, public IConfigProvider {
        IConfig const* m_config = nullptr;
        IResultCapture* m_resultCapture = nullptr;

        CATCH_EXPORT static Context currentContext;
        friend Context& getCurrentMutableContext();
        friend Context const& getCurrentContext();

    public:
        IResultCapture* getResultCapture() const override {
            return m_resultCapture;
        }
        IConfig const* getConfig() const override { return m_config; }
        void setResultCapture( IResultCapture* resultCapture ) {
            m_resultCapture = resultCapture;
        }
        void setConfig( IConfig const* config ) { m_config = config; }
    };
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `extras/catch_amalgamated.hpp` | 10486 → 10496 | 3 → 3 | 425 → 425 | 1273 → 1273 | 0 → 0 |

## Diff

```diff
diff --git a/extras/catch_amalgamated.hpp b/extras/catch_amalgamated.hpp
index e517e65..6435ff7 100644
--- a/extras/catch_amalgamated.hpp
+++ b/extras/catch_amalgamated.hpp
@@ -570,7 +570,19 @@ namespace Catch {
     class IRuntimeConfig;
     class IConfig;
 
-    class Context {
+    class IResultCaptureProvider {
+    public:
+        virtual ~IResultCaptureProvider() = default;
+        virtual IResultCapture* getResultCapture() const = 0;
+    };
+
+    class IConfigProvider {
+    public:
+        virtual ~IConfigProvider() = default;
+        virtual IConfig const* getConfig() const = 0;
+    };
+
+    class Context : public IResultCaptureProvider, public IConfigProvider {
         IConfig const* m_config = nullptr;
         IResultCapture* m_resultCapture = nullptr;
 
@@ -579,14 +591,14 @@ namespace Catch {
         friend Context const& getCurrentContext();
 
     public:
-        constexpr IResultCapture* getResultCapture() const {
+        IResultCapture* getResultCapture() const override {
             return m_resultCapture;
         }
-        constexpr IConfig const* getConfig() const { return m_config; }
-        constexpr void setResultCapture( IResultCapture* resultCapture ) {
+        IConfig const* getConfig() const override { return m_config; }
+        void setResultCapture( IResultCapture* resultCapture ) {
             m_resultCapture = resultCapture;
         }
-        constexpr void setConfig( IConfig const* config ) { m_config = config; }
+        void setConfig( IConfig const* config ) { m_config = config; }
     };
 
     class ITestConfig {

```
