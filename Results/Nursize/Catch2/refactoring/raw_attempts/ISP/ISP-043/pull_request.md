# Refactor ISP-043 (ISP): Parser class has methods for parsing, validation, help generation, and stream...

**Status:** `applied_unverified`  
**Branch:** `refactor/ISP-043` -> `main`  
**Head commit:** `68a12ee244efe5aada3a99d4c1d5f1292ae2be11`  
**LLM finish:** `FinishReason.STOP` (prompt 7515, completion 1256)  

## Detected issue

- **File**: `src/catch2/internal/catch_clara.hpp`
- **Entity**: `Parser` (class)
- **Lines (at detection time)**: L644–L701
- **Severity**: low
- **Confidence**: detected by 3 scan(s)

**Description.** Parser class has methods for parsing, validation, help generation, and stream writing, which could be segregated.

**Reasoning.** The Parser class includes methods for parsing arguments, validating them, writing help to a stream, and getting help columns. A client that only needs to parse arguments might be forced to depend on validation or help generation logic.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 2
- **Files modified** (1): `src/catch2/internal/catch_clara.hpp`

**Summary.** Segregate Parser interface into Parser and HelpGenerator

**Rationale.** The Parser class was violating the Interface Segregation Principle by combining parsing logic with help generation logic. By introducing a HelpGenerator interface, clients that only need to parse arguments are no longer forced to depend on help generation methods.

## Changes overview

_2 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `src/catch2/internal/catch_clara.hpp` (11-line block → 18-line replacement)

**Replaces:**

```
            class ParserBase {
            public:
                virtual ~ParserBase() = default;
                virtual auto validate() const -> Result { return Result::ok(); }
                virtual auto parse( std::string const& exeName,
                                    TokenStream tokens ) const
                    -> InternalParseResult = 0;
                virtual size_t cardinality() const;

                InternalParseResult parse( Args const& args ) const;
            };
```

**With:**

```
            class ParserBase {
            public:
                virtual ~ParserBase() = default;
                virtual auto validate() const -> Result { return Result::ok(); }
                virtual auto parse( std::string const& exeName,
                                    TokenStream tokens ) const
                    -> InternalParseResult = 0;
                virtual size_t cardinality() const;

                InternalParseResult parse( Args const& args ) const;
            };

            class HelpGenerator {
            public:
                virtual ~HelpGenerator() = default;
                virtual std::vector<HelpColumns> getHelpColumns() const = 0;
                virtual void writeToStream(std::ostream& os) const = 0;
            };
```

### 2. EDIT `src/catch2/internal/catch_clara.hpp` (59-line block → 59-line replacement)

**Replaces:**

```
        // A Combined parser
        class Parser : Detail::ParserBase {
            mutable ExeName m_exeName;
            std::vector<Opt> m_options;
            std::vector<Arg> m_args;

        public:

            auto operator|=(ExeName const& exeName) -> Parser& {
                m_exeName = exeName;
                return *this;
            }

            auto operator|=(Arg const& arg) -> Parser& {
                m_args.push_back(arg);
                return *this;
            }

            friend Parser& operator|=( Parser& p, Opt const& opt ) {
                p.m_options.push_back( opt );
                return p;
            }
            friend Parser& operator|=( Parser& p, Opt&& opt ) {
                p.m_options.push_back( CATCH_MOVE(opt) );
                return p;
            }

            Parser& operator|=(Parser const& other);

            template <typename T>
            friend Parser operator|( Parser const& p, T&& rhs ) {
                Parser temp( p );
                temp |= rhs;
                return temp;
            }

            template <typename T>
            friend Parser operator|( Parser&& p, T&& rhs ) {
                p |= CATCH_FORWARD(rhs);
                return CATCH_MOVE(p);
            }

            std::vector<Detail::HelpColumns> getHelpColumns() const;

            void writeToStream(std::ostream& os) const;

            friend auto operator<<(std::ostream& os, Parser const& parser)
                -> std::ostream& {
                parser.writeToStream(os);
                return os;
            }

            Detail::Result validate() const override;

            using ParserBase::parse;
            Detail::InternalParseResult
                parse(std::string const& exeName,
                      Detail::TokenStream tokens) const override;
        };
```

**With:**

```
        // A Combined parser
        class Parser : Detail::ParserBase, Detail::HelpGenerator {
            mutable ExeName m_exeName;
            std::vector<Opt> m_options;
            std::vector<Arg> m_args;

        public:

            auto operator|=(ExeName const& exeName) -> Parser& {
                m_exeName = exeName;
                return *this;
            }

            auto operator|=(Arg const& arg) -> Parser& {
                m_args.push_back(arg);
                return *this;
            }

            friend Parser& operator|=( Parser& p, Opt const& opt ) {
                p.m_options.push_back( opt );
                return p;
            }
            friend Parser& operator|=( Parser& p, Opt&& opt ) {
                p.m_options.push_back( CATCH_MOVE(opt) );
                return p;
            }

            Parser& operator|=(Parser const& other);

            template <typename T>
            friend Parser operator|( Parser const& p, T&& rhs ) {
                Parser temp( p );
                temp |= rhs;
                return temp;
            }

            template <typename T>
            friend Parser operator|( Parser&& p, T&& rhs ) {
                p |= CATCH_FORWARD(rhs);
                return CATCH_MOVE(p);
            }

            std::vector<Detail::HelpColumns> getHelpColumns() const override;

            void writeToStream(std::ostream& os) const override;

            friend auto operator<<(std::ostream& os, Parser const& parser)
                -> std::ostream& {
                parser.writeToStream(os);
                return os;
            }

            Detail::Result validate() const override;

            using ParserBase::parse;
            Detail::InternalParseResult
                parse(std::string const& exeName,
                      Detail::TokenStream tokens) const override;
        };
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `src/catch2/internal/catch_clara.hpp` | 580 → 586 | 0 → 0 | 55 → 55 | 55 → 55 | 0 → 0 |

## Diff

```diff
diff --git a/src/catch2/internal/catch_clara.hpp b/src/catch2/internal/catch_clara.hpp
index 85874a1..df678a2 100644
--- a/src/catch2/internal/catch_clara.hpp
+++ b/src/catch2/internal/catch_clara.hpp
@@ -476,6 +476,13 @@ namespace Catch {
                 InternalParseResult parse( Args const& args ) const;
             };
 
+            class HelpGenerator {
+            public:
+                virtual ~HelpGenerator() = default;
+                virtual std::vector<HelpColumns> getHelpColumns() const = 0;
+                virtual void writeToStream(std::ostream& os) const = 0;
+            };
+
             template <typename DerivedT>
             class ComposableParserImpl : public ParserBase {
             public:
@@ -641,7 +648,7 @@ namespace Catch {
 
 
         // A Combined parser
-        class Parser : Detail::ParserBase {
+        class Parser : Detail::ParserBase, Detail::HelpGenerator {
             mutable ExeName m_exeName;
             std::vector<Opt> m_options;
             std::vector<Arg> m_args;
@@ -682,9 +689,9 @@ namespace Catch {
                 return CATCH_MOVE(p);
             }
 
-            std::vector<Detail::HelpColumns> getHelpColumns() const;
+            std::vector<Detail::HelpColumns> getHelpColumns() const override;
 
-            void writeToStream(std::ostream& os) const;
+            void writeToStream(std::ostream& os) const override;
 
             friend auto operator<<(std::ostream& os, Parser const& parser)
                 -> std::ostream& {

```
