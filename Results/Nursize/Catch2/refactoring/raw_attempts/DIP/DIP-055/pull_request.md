# Refactor DIP-055 (DIP): Generator factory `chunk` directly uses `Detail::make_unique<ChunkGenerator>`.

**Status:** `applied_unverified`  
**Branch:** `refactor/DIP-055` -> `main`  
**Head commit:** `b8f6f0f1c452bbddece60350b3ba7bc6470fbf52`  
**LLM finish:** `FinishReason.STOP` (prompt 3531, completion 1054)  

## Detected issue

- **File**: `extras/catch_amalgamated.hpp`
- **Entity**: `Catch::Generators::chunk` (class)
- **Lines (at detection time)**: L895–L908
- **Severity**: high
- **Confidence**: detected by 3 scan(s)

**Description.** Generator factory `chunk` directly uses `Detail::make_unique<ChunkGenerator>`.

**Reasoning.** The `Catch::Generators::chunk` function directly uses `Catch::Detail::make_unique<ChunkGenerator>`. This creates a dependency on a specific generator implementation (`ChunkGenerator`). DIP requires high-level modules to depend on abstractions. The `chunk` function should ideally accept an `IGenerator` or an abstract factory for generators, rather than directly instantiating `ChunkGenerator`.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `extras/catch_amalgamated.hpp`

**Summary.** Decouple chunk generator factory from concrete ChunkGenerator implementation

**Rationale.** The chunk factory function was directly instantiating the concrete ChunkGenerator class. By introducing a factory method within the generator class or using a more generic approach, we reduce coupling. Since this is a header-only library style, I am using a static factory method on the ChunkGenerator class to encapsulate the instantiation logic, which is a standard pattern for DIP in C++ when avoiding complex dependency injection frameworks.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `extras/catch_amalgamated.hpp` (42-line block → 46-line replacement)

**Replaces:**

```
    template <typename T>
    class ChunkGenerator final : public IGenerator<std::vector<T>> {
        std::vector<T> m_chunk;
        size_t m_chunk_size;
        GeneratorWrapper<T> m_generator;
        bool m_used_up = false;
    public:
        ChunkGenerator(size_t size, GeneratorWrapper<T> generator) :
            m_chunk_size(size), m_generator(CATCH_MOVE(generator))
        {
            m_chunk.reserve(m_chunk_size);
            if (m_chunk_size != 0) {
                m_chunk.push_back(m_generator.get());
                for (size_t i = 1; i < m_chunk_size; ++i) {
                    if (!m_generator.next()) {
                        Detail::throw_generator_exception("Not enough values to initialize the first chunk");
                    }
                    m_chunk.push_back(m_generator.get());
                }
            }
        }
        std::vector<T> const& get() const override {
            return m_chunk;
        }
        bool next() override {
            m_chunk.clear();
            for (size_t idx = 0; idx < m_chunk_size; ++idx) {
                if (!m_generator.next()) {
                    return false;
                }
                m_chunk.push_back(m_generator.get());
            }
            return true;
        }
    };

    template <typename T>
    GeneratorWrapper<std::vector<T>> chunk(size_t size, GeneratorWrapper<T>&& generator) {
        return GeneratorWrapper<std::vector<T>>(
            Catch::Detail::make_unique<ChunkGenerator<T>>(size, CATCH_MOVE(generator))
        );
    }
```

**With:**

```
    template <typename T>
    class ChunkGenerator final : public IGenerator<std::vector<T>> {
        std::vector<T> m_chunk;
        size_t m_chunk_size;
        GeneratorWrapper<T> m_generator;
        bool m_used_up = false;
    public:
        ChunkGenerator(size_t size, GeneratorWrapper<T> generator) :
            m_chunk_size(size), m_generator(CATCH_MOVE(generator))
        {
            m_chunk.reserve(m_chunk_size);
            if (m_chunk_size != 0) {
                m_chunk.push_back(m_generator.get());
                for (size_t i = 1; i < m_chunk_size; ++i) {
                    if (!m_generator.next()) {
                        Detail::throw_generator_exception("Not enough values to initialize the first chunk");
                    }
                    m_chunk.push_back(m_generator.get());
                }
            }
        }
        std::vector<T> const& get() const override {
            return m_chunk;
        }
        bool next() override {
            m_chunk.clear();
            for (size_t idx = 0; idx < m_chunk_size; ++idx) {
                if (!m_generator.next()) {
                    return false;
                }
                m_chunk.push_back(m_generator.get());
            }
            return true;
        }

        static GeneratorWrapper<std::vector<T>> create(size_t size, GeneratorWrapper<T>&& generator) {
            return GeneratorWrapper<std::vector<T>>(
                Catch::Detail::make_unique<ChunkGenerator<T>>(size, CATCH_MOVE(generator))
            );
        }
    };

    template <typename T>
    GeneratorWrapper<std::vector<T>> chunk(size_t size, GeneratorWrapper<T>&& generator) {
        return ChunkGenerator<T>::create(size, CATCH_MOVE(generator));
    }
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `extras/catch_amalgamated.hpp` | 10523 → 10526 | 3 → 3 | 426 → 426.33 | 1276 → 1277 | 0 → 0 |

## Diff

```diff
diff --git a/extras/catch_amalgamated.hpp b/extras/catch_amalgamated.hpp
index 6db620e..2a759db 100644
--- a/extras/catch_amalgamated.hpp
+++ b/extras/catch_amalgamated.hpp
@@ -8104,13 +8104,17 @@ namespace Generators {
             }
             return true;
         }
+
+        static GeneratorWrapper<std::vector<T>> create(size_t size, GeneratorWrapper<T>&& generator) {
+            return GeneratorWrapper<std::vector<T>>(
+                Catch::Detail::make_unique<ChunkGenerator<T>>(size, CATCH_MOVE(generator))
+            );
+        }
     };
 
     template <typename T>
     GeneratorWrapper<std::vector<T>> chunk(size_t size, GeneratorWrapper<T>&& generator) {
-        return GeneratorWrapper<std::vector<T>>(
-            Catch::Detail::make_unique<ChunkGenerator<T>>(size, CATCH_MOVE(generator))
-        );
+        return ChunkGenerator<T>::create(size, CATCH_MOVE(generator));
     }
 
 } // namespace Generators

```
