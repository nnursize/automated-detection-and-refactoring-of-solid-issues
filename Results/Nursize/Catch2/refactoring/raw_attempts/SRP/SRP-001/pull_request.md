# Refactor SRP-001 (SRP): The 'Benchmark' class combines benchmark definition, preparation, execution o...

**Status:** `applied_unverified`  
**Branch:** `refactor/SRP-001` -> `main`  
**Head commit:** `05ad0d759640976bb377d6b83b0ae9d1cece77e6`  
**LLM finish:** `FinishReason.STOP` (prompt 4001, completion 1576)  

## Detected issue

- **File**: `extras/catch_amalgamated.hpp`
- **Entity**: `Catch::Benchmark::Benchmark` (class)
- **Lines (at detection time)**: L1000–L1058
- **Severity**: high
- **Confidence**: detected by 2 scan(s)

**Description.** The 'Benchmark' class combines benchmark definition, preparation, execution orchestration, and error handling/reporting.

**Reasoning.** This class has multiple reasons to change: if the way benchmarks are defined changes, if the preparation logic (e.g., iteration calculation) changes, if the execution flow changes, or if the error reporting mechanism changes. It acts as a 'God object' for the entire benchmarking process, rather than delegating these distinct responsibilities to separate components.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `extras/catch_amalgamated.hpp`

**Summary.** Delegate benchmark execution to a dedicated Runner class to improve SRP

**Rationale.** The Benchmark class was acting as a God object. By extracting the execution logic into a 'BenchmarkRunner' struct, we separate the definition of the benchmark from the orchestration of its execution, error handling, and reporting.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `extras/catch_amalgamated.hpp` (68-line block → 56-line replacement)

**Replaces:**

```
        struct Benchmark {
            Benchmark(std::string&& benchmarkName)
                : name(CATCH_MOVE(benchmarkName)) {}

            template <class FUN>
            Benchmark(std::string&& benchmarkName , FUN &&func)
                : fun(CATCH_MOVE(func)), name(CATCH_MOVE(benchmarkName)) {}

            template <typename Clock>
            ExecutionPlan prepare(const IConfig &cfg, Environment env) {
                auto min_time = env.clock_resolution.mean * Detail::minimum_ticks;
                auto run_time = std::max(min_time, std::chrono::duration_cast<decltype(min_time)>(cfg.benchmarkWarmupTime()));
                auto&& test = Detail::run_for_at_least<Clock>(std::chrono::duration_cast<IDuration>(run_time), 1, fun);
                int new_iters = static_cast<int>(std::ceil(min_time * test.iterations / test.elapsed));
                return { new_iters, test.elapsed / test.iterations * new_iters * cfg.benchmarkSamples(), CATCH_MOVE(fun), std::chrono::duration_cast<FDuration>(cfg.benchmarkWarmupTime()), Detail::warmup_iterations };
            }

            template <typename Clock = default_clock>
            void run() {
                static_assert( Clock::is_steady,
                               "Benchmarking clock should be steady" );
                auto const* cfg = getCurrentContext().getConfig();

                auto env = Detail::measure_environment<Clock>();

                getResultCapture().benchmarkPreparing(name);
                CATCH_TRY{
                    auto plan = user_code([&] {
                        return prepare<Clock>(*cfg, env);
                    });

                    BenchmarkInfo info {
                        CATCH_MOVE(name),
                        plan.estimated_duration.count(),
                        plan.iterations_per_sample,
                        cfg->benchmarkSamples(),
                        cfg->benchmarkResamples(),
                        env.clock_resolution.mean.count(),
                        env.clock_cost.mean.count()
                    };

                    getResultCapture().benchmarkStarting(info);

                    auto samples = user_code([&] {
                        return plan.template run<Clock>(*cfg, env);
                    });

                    auto analysis = Detail::analyse(*cfg, samples.data(), samples.data() + samples.size());
                    BenchmarkStats<> stats{ CATCH_MOVE(info), CATCH_MOVE(analysis.samples), analysis.mean, analysis.standard_deviation, analysis.outliers, analysis.outlier_variance };
                    getResultCapture().benchmarkEnded(stats);
                } CATCH_CATCH_ALL {
                    getResultCapture().benchmarkFailed(translateActiveException());
                    // We let the exception go further up so that the
                    // test case is marked as failed.
                    std::rethrow_exception(std::current_exception());
                }
            }

            // sets lambda to be used in fun *and* executes benchmark!
            template <typename Fun, std::enable_if_t<!Detail::is_related_v<Fun, Benchmark>, int> = 0>
... (8 more line(s) truncated)
```

**With:**

```
        struct BenchmarkRunner {
            template <typename Clock>
            static void run(std::string&& name, Detail::BenchmarkFunction& fun) {
                static_assert( Clock::is_steady, "Benchmarking clock should be steady" );
                auto const* cfg = getCurrentContext().getConfig();
                auto env = Detail::measure_environment<Clock>();

                getResultCapture().benchmarkPreparing(name);
                CATCH_TRY{
                    auto plan = user_code([&] {
                        auto min_time = env.clock_resolution.mean * Detail::minimum_ticks;
                        auto run_time = std::max(min_time, std::chrono::duration_cast<decltype(min_time)>(cfg->benchmarkWarmupTime()));
                        auto&& test = Detail::run_for_at_least<Clock>(std::chrono::duration_cast<IDuration>(run_time), 1, fun);
                        int new_iters = static_cast<int>(std::ceil(min_time * test.iterations / test.elapsed));
                        return ExecutionPlan{ new_iters, test.elapsed / test.iterations * new_iters * cfg->benchmarkSamples(), fun, std::chrono::duration_cast<FDuration>(cfg->benchmarkWarmupTime()), Detail::warmup_iterations };
                    });

                    BenchmarkInfo info {
                        name,
                        plan.estimated_duration.count(),
                        plan.iterations_per_sample,
                        cfg->benchmarkSamples(),
                        cfg->benchmarkResamples(),
                        env.clock_resolution.mean.count(),
                        env.clock_cost.mean.count()
                    };

                    getResultCapture().benchmarkStarting(info);
                    auto samples = user_code([&] { return plan.template run<Clock>(*cfg, env); });
                    auto analysis = Detail::analyse(*cfg, samples.data(), samples.data() + samples.size());
                    BenchmarkStats<> stats{ CATCH_MOVE(info), CATCH_MOVE(analysis.samples), analysis.mean, analysis.standard_deviation, analysis.outliers, analysis.outlier_variance };
                    getResultCapture().benchmarkEnded(stats);
                } CATCH_CATCH_ALL {
                    getResultCapture().benchmarkFailed(translateActiveException());
                    std::rethrow_exception(std::current_exception());
                }
            }
        };

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
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `extras/catch_amalgamated.hpp` | 10500 → 10495 | 3 → 3 | 433.67 → 433.67 | 1299 → 1299 | 0 → 0 |

## Diff

```diff
diff --git a/extras/catch_amalgamated.hpp b/extras/catch_amalgamated.hpp
index 00fc3ee..a60fc71 100644
--- a/extras/catch_amalgamated.hpp
+++ b/extras/catch_amalgamated.hpp
@@ -2130,39 +2130,25 @@ namespace Catch {
 
 namespace Catch {
     namespace Benchmark {
-        struct Benchmark {
-            Benchmark(std::string&& benchmarkName)
-                : name(CATCH_MOVE(benchmarkName)) {}
-
-            template <class FUN>
-            Benchmark(std::string&& benchmarkName , FUN &&func)
-                : fun(CATCH_MOVE(func)), name(CATCH_MOVE(benchmarkName)) {}
-
+        struct BenchmarkRunner {
             template <typename Clock>
-            ExecutionPlan prepare(const IConfig &cfg, Environment env) {
-                auto min_time = env.clock_resolution.mean * Detail::minimum_ticks;
-                auto run_time = std::max(min_time, std::chrono::duration_cast<decltype(min_time)>(cfg.benchmarkWarmupTime()));
-                auto&& test = Detail::run_for_at_least<Clock>(std::chrono::duration_cast<IDuration>(run_time), 1, fun);
-                int new_iters = static_cast<int>(std::ceil(min_time * test.iterations / test.elapsed));
-                return { new_iters, test.elapsed / test.iterations * new_iters * cfg.benchmarkSamples(), CATCH_MOVE(fun), std::chrono::duration_cast<FDuration>(cfg.benchmarkWarmupTime()), Detail::warmup_iterations };
-            }
-
-            template <typename Clock = default_clock>
-            void run() {
-                static_assert( Clock::is_steady,
-                               "Benchmarking clock should be steady" );
+            static void run(std::string&& name, Detail::BenchmarkFunction& fun) {
+                static_assert( Clock::is_steady, "Benchmarking clock should be steady" );
                 auto const* cfg = getCurrentContext().getConfig();
-
                 auto env = Detail::measure_environment<Clock>();
 
                 getResultCapture().benchmarkPreparing(name);
                 CATCH_TRY{
                     auto plan = user_code([&] {
-                        return prepare<Clock>(*cfg, env);
+                        auto min_time = env.clock_resolution.mean * Detail::minimum_ticks;
+                        auto run_time = std::max(min_time, std::chrono::duration_cast<decltype(min_time)>(cfg->benchmarkWarmupTime()));
+                        auto&& test = Detail::run_for_at_least<Clock>(std::chrono::duration_cast<IDuration>(run_time), 1, fun);
+                        int new_iters = static_cast<int>(std::ceil(min_time * test.iterations / test.elapsed));
+                        return ExecutionPlan{ new_iters, test.elapsed / test.iterations * new_iters * cfg->benchmarkSamples(), fun, std::chrono::duration_cast<FDuration>(cfg->benchmarkWarmupTime()), Detail::warmup_iterations };
                     });
 
                     BenchmarkInfo info {
-                        CATCH_MOVE(name),
+                        name,
                         plan.estimated_duration.count(),
                         plan.iterations_per_sample,
                         cfg->benchmarkSamples(),
@@ -2172,29 +2158,31 @@ namespace Catch {
                     };
 
                     getResultCapture().benchmarkStarting(info);
-
-                    auto samples = user_code([&] {
-                        return plan.template run<Clock>(*cfg, env);
-                    });
-
+                    auto samples = user_code([&] { return plan.template run<Clock>(*cfg, env); });
                     auto analysis = Detail::analyse(*cfg, samples.data(), samples.data() + samples.size());
                     BenchmarkStats<> stats{ CATCH_MOVE(info), CATCH_MOVE(analysis.samples), analysis.mean, analysis.standard_deviation, analysis.outliers, analysis.outlier_variance };
                     getResultCapture().benchmarkEnded(stats);
                 } CATCH_CATCH_ALL {
                     getResultCapture().benchmarkFailed(translateActiveException());
-                    // We let the exception go further up so that the
-                    // test case is marked as failed.
                     std::rethrow_exception(std::current_exception());
                 }
             }
+        };
+
+        struct Benchmark {
+            Benchmark(std::string&& benchmarkName)
+                : name(CATCH_MOVE(benchmarkName)) {}
+
+            template <class FUN>
+            Benchmark(std::string&& benchmarkName , FUN &&func)
+                : fun(CATCH_MOVE(func)), name(CATCH_MOVE(benchmarkName)) {}
 
-            // sets lambda to be used in fun *and* executes benchmark!
             template <typename Fun, std::enable_if_t<!Detail::is_related_v<Fun, Benchmark>, int> = 0>
-                Benchmark & operator=(Fun func) {
+            Benchmark & operator=(Fun func) {
                 auto const* cfg = getCurrentContext().getConfig();
                 if (!cfg->skipBenchmarks()) {
                     fun = Detail::BenchmarkFunction(func);
-                    run();
+                    BenchmarkRunner::run<default_clock>(std::string(name), fun);
                 }
                 return *this;
             }

```
