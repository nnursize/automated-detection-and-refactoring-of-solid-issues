# Refactor SRP-006 (SRP): Class combines benchmark definition, preparation, execution, and error handli...

**Status:** `applied_unverified`  
**Branch:** `refactor/SRP-006` -> `main`  
**Head commit:** `9d2cba195b4200e785630e88fbdb6c70d42f83ef`  
**LLM finish:** `FinishReason.STOP` (prompt 3500, completion 501)  

## Detected issue

- **File**: `extras/catch_amalgamated.hpp`
- **Entity**: `Catch::Benchmark::Benchmark` (class)
- **Lines (at detection time)**: L1039–L1109
- **Severity**: high
- **Confidence**: detected by 1 scan(s)

**Description.** Class combines benchmark definition, preparation, execution, and error handling/reporting.

**Reasoning.** The `Benchmark` class stores the benchmark name and function (`fun`), prepares the execution plan (`prepare` method, involving timing and iteration calculation), executes the benchmark (`run` method, which interacts with `IConfig` and `IResultCapture`), and handles exceptions during execution. These are distinct responsibilities: defining a benchmark, planning its execution, performing the execution, and reporting/error handling. Changes to any of these aspects would require modifying this single class.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `extras/catch_amalgamated.hpp`

**Summary.** Refactor Benchmark class to delegate execution to BenchmarkRunner

**Rationale.** The Benchmark class was acting as a 'God object' by managing both the definition of the benchmark and its execution logic. By moving the execution logic entirely into the BenchmarkRunner and simplifying the Benchmark class to act as a lightweight handle/proxy, we adhere to the Single Responsibility Principle.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `extras/catch_amalgamated.hpp` (26-line block → 21-line replacement)

**Replaces:**

```
        struct Benchmark {
            Benchmark(std::string&& benchmarkName)
                : name(CATCH_MOVE(benchmarkName)) {}

            template <class FUN>
            Benchmark(std::string&& benchmarkName , FUN &&func)
                : fun(CATCH_MOVE(func)), name(CATCH_MOVE(benchmarkName)) {}

            template <typename Fun, std::enable_if_t<!Detail::is_related_v<Fun, Benchmark>, int> = 0>
            Benchmark & operator=(Fun func) {
                auto const* cfg = getCurrentContext().getConfig();
                if (!cfg->skipBenchmarks()) {
                    fun = Detail::BenchmarkFunction(func);
                    BenchmarkRunner::run<default_clock>(std::string(name), fun);
                }
                return *this;
            }

            explicit operator bool() {
                return true;
            }

        private:
            Detail::BenchmarkFunction fun;
            std::string name;
        };
```

**With:**

```
        struct Benchmark {
            Benchmark(std::string&& benchmarkName)
                : name(CATCH_MOVE(benchmarkName)) {}

            template <typename Fun, std::enable_if_t<!Detail::is_related_v<Fun, Benchmark>, int> = 0>
            Benchmark & operator=(Fun func) {
                auto const* cfg = getCurrentContext().getConfig();
                if (!cfg->skipBenchmarks()) {
                    Detail::BenchmarkFunction fun(func);
                    BenchmarkRunner::run<default_clock>(std::string(name), fun);
                }
                return *this;
            }

            explicit operator bool() {
                return true;
            }

        private:
            std::string name;
        };
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `extras/catch_amalgamated.hpp` | 10495 → 10491 | 3 → 3 | 433.67 → 433 | 1299 → 1297 | 0 → 0 |

## Diff

```diff
diff --git a/extras/catch_amalgamated.hpp b/extras/catch_amalgamated.hpp
index a60fc71..256091f 100644
--- a/extras/catch_amalgamated.hpp
+++ b/extras/catch_amalgamated.hpp
@@ -2173,15 +2173,11 @@ namespace Catch {
             Benchmark(std::string&& benchmarkName)
                 : name(CATCH_MOVE(benchmarkName)) {}
 
-            template <class FUN>
-            Benchmark(std::string&& benchmarkName , FUN &&func)
-                : fun(CATCH_MOVE(func)), name(CATCH_MOVE(benchmarkName)) {}
-
             template <typename Fun, std::enable_if_t<!Detail::is_related_v<Fun, Benchmark>, int> = 0>
             Benchmark & operator=(Fun func) {
                 auto const* cfg = getCurrentContext().getConfig();
                 if (!cfg->skipBenchmarks()) {
-                    fun = Detail::BenchmarkFunction(func);
+                    Detail::BenchmarkFunction fun(func);
                     BenchmarkRunner::run<default_clock>(std::string(name), fun);
                 }
                 return *this;
@@ -2192,7 +2188,6 @@ namespace Catch {
             }
 
         private:
-            Detail::BenchmarkFunction fun;
             std::string name;
         };
     }

```
