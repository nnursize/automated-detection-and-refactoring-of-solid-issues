# Refactor SRP-046 (SRP): The Column class combines text content storage, text layout configuration, an...

**Status:** `applied_unverified`  
**Branch:** `refactor/SRP-046` -> `main`  
**Head commit:** `54a5882f307ef215f4ccad5da24858aad03b7fbc`  
**LLM finish:** `FinishReason.STOP` (prompt 12208, completion 2210)  

## Detected issue

- **File**: `third_party/clara.hpp`
- **Entity**: `Column` (class)
- **Lines (at detection time)**: L71–L241
- **Severity**: medium
- **Confidence**: detected by 3 scan(s)

**Description.** The Column class combines text content storage, text layout configuration, and rendering logic.

**Reasoning.** The class stores the raw text (`m_strings`), defines layout parameters (`m_width`, `m_indent`, `m_initialIndent`), and provides an iterator that applies these layout rules. Additionally, it offers `operator<<` and `toString()` for rendering the formatted output. A change in text content, layout rules, or rendering mechanism would all require modifications to this single class.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 4
- **Files modified** (1): `third_party/clara.hpp`

**Summary.** Extract layout configuration from Column class into a separate ColumnLayout struct

**Rationale.** The Column class was violating SRP by managing both data storage and layout parameters. By introducing a ColumnLayout struct, we separate the configuration (width, indent) from the data storage and iteration logic, making the code more maintainable and adhering to the Single Responsibility Principle.

## Changes overview

_4 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `third_party/clara.hpp` (70-line block → 74-line replacement)

**Replaces:**

```
    class Column {
        std::vector<std::string> m_strings;
        size_t m_width = CLARA_TEXTFLOW_CONFIG_CONSOLE_WIDTH;
        size_t m_indent = 0;
        size_t m_initialIndent = std::string::npos;

    public:
        class iterator {
            friend Column;

            Column const& m_column;
            size_t m_stringIndex = 0;
            size_t m_pos = 0;

            size_t m_len = 0;
            size_t m_end = 0;
            bool m_suffix = false;

            iterator( Column const& column, size_t stringIndex )
            :   m_column( column ),
                m_stringIndex( stringIndex )
            {}

            auto line() const -> std::string const& { return m_column.m_strings[m_stringIndex]; }

            auto isBoundary( size_t at ) const -> bool {
                assert( at > 0 );
                assert( at <= line().size() );

                return at == line().size() ||
                       ( isWhitespace( line()[at] ) && !isWhitespace( line()[at-1] ) ) ||
                       isBreakableBefore( line()[at] ) ||
                       isBreakableAfter( line()[at-1] );
            }

            void calcLength() {
                assert( m_stringIndex < m_column.m_strings.size() );

                m_suffix = false;
                auto width = m_column.m_width-indent();
                m_end = m_pos;
                if (line()[m_pos] == '\n') {
                    ++m_end;
                }
                while( m_end < line().size() && line()[m_end] != '\n' )
                    ++m_end;

                if( m_end < m_pos + width ) {
                    m_len = m_end - m_pos;
                }
                else {
                    size_t len = width;
                    while (len > 0 && !isBoundary(m_pos + len))
                        --len;
                    while (len > 0 && isWhitespace( line()[m_pos + len - 1] ))
                        --len;

                    if (len > 0) {
                        m_len = len;
                    } else {
... (10 more line(s) truncated)
```

**With:**

```
    struct ColumnLayout {
        size_t width = CLARA_TEXTFLOW_CONFIG_CONSOLE_WIDTH;
        size_t indent = 0;
        size_t initialIndent = std::string::npos;
    };

    class Column {
        std::vector<std::string> m_strings;
        ColumnLayout m_layout;

    public:
        class iterator {
            friend Column;

            Column const& m_column;
            size_t m_stringIndex = 0;
            size_t m_pos = 0;

            size_t m_len = 0;
            size_t m_end = 0;
            bool m_suffix = false;

            iterator( Column const& column, size_t stringIndex )
            :   m_column( column ),
                m_stringIndex( stringIndex )
            {}

            auto line() const -> std::string const& { return m_column.m_strings[m_stringIndex]; }

            auto isBoundary( size_t at ) const -> bool {
                assert( at > 0 );
                assert( at <= line().size() );

                return at == line().size() ||
                       ( isWhitespace( line()[at] ) && !isWhitespace( line()[at-1] ) ) ||
                       isBreakableBefore( line()[at] ) ||
                       isBreakableAfter( line()[at-1] );
            }

            void calcLength() {
                assert( m_stringIndex < m_column.m_strings.size() );

                m_suffix = false;
                auto width = m_column.m_layout.width-indent();
                m_end = m_pos;
                if (line()[m_pos] == '\n') {
                    ++m_end;
                }
                while( m_end < line().size() && line()[m_end] != '\n' )
                    ++m_end;

                if( m_end < m_pos + width ) {
                    m_len = m_end - m_pos;
                }
                else {
                    size_t len = width;
                    while (len > 0 && !isBoundary(m_pos + len))
                        --len;
                    while (len > 0 && isWhitespace( line()[m_pos + len - 1] ))
                        --len;
... (14 more line(s) truncated)
```

### 2. EDIT `third_party/clara.hpp` (5-line block → 5-line replacement)

**Replaces:**

```
            explicit iterator( Column const& column ) : m_column( column ) {
                assert( m_column.m_width > m_column.m_indent );
                assert( m_column.m_initialIndent == std::string::npos || m_column.m_width > m_column.m_initialIndent );
                calcLength();
                if( m_len == 0 )
```

**With:**

```
            explicit iterator( Column const& column ) : m_column( column ) {
                assert( m_column.m_layout.width > m_column.m_layout.indent );
                assert( m_column.m_layout.initialIndent == std::string::npos || m_column.m_layout.width > m_column.m_layout.initialIndent );
                calcLength();
                if( m_len == 0 )
```

### 3. EDIT `third_party/clara.hpp` (17-line block → 17-line replacement)

**Replaces:**

```
        explicit Column( std::string const& text ) { m_strings.push_back( text ); }

        auto width( size_t newWidth ) -> Column& {
            assert( newWidth > 0 );
            m_width = newWidth;
            return *this;
        }
        auto indent( size_t newIndent ) -> Column& {
            m_indent = newIndent;
            return *this;
        }
        auto initialIndent( size_t newIndent ) -> Column& {
            m_initialIndent = newIndent;
            return *this;
        }

        auto width() const -> size_t { return m_width; }
```

**With:**

```
        explicit Column( std::string const& text ) { m_strings.push_back( text ); }

        auto width( size_t newWidth ) -> Column& {
            assert( newWidth > 0 );
            m_layout.width = newWidth;
            return *this;
        }
        auto indent( size_t newIndent ) -> Column& {
            m_layout.indent = newIndent;
            return *this;
        }
        auto initialIndent( size_t newIndent ) -> Column& {
            m_layout.initialIndent = newIndent;
            return *this;
        }

        auto width() const -> size_t { return m_layout.width; }
```

### 4. EDIT `third_party/clara.hpp` (12-line block → 12-line replacement)

**Replaces:**

```
                    auto width = m_columns[i].width();
                    if( m_iterators[i] != m_columns[i].end() ) {
                        std::string col = *m_iterators[i];
                        row += padding + col;
                        if( col.size() < width )
                            padding = std::string( width - col.size(), ' ' );
                        else
                            padding = "";
                    }
                    else {
                        padding += std::string( width, ' ' );
                    }
```

**With:**

```
                    auto colWidth = m_columns[i].width();
                    if( m_iterators[i] != m_columns[i].end() ) {
                        std::string col = *m_iterators[i];
                        row += padding + col;
                        if( col.size() < colWidth )
                            padding = std::string( colWidth - col.size(), ' ' );
                        else
                            padding = "";
                    }
                    else {
                        padding += std::string( colWidth, ' ' );
                    }
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `third_party/clara.hpp` | 1007 → 1010 | 1 → 1 | 145 → 145 | 145 → 145 | 0 → 0 |

## Diff

```diff
diff --git a/third_party/clara.hpp b/third_party/clara.hpp
index eb4c727..9bdc986 100644
--- a/third_party/clara.hpp
+++ b/third_party/clara.hpp
@@ -69,11 +69,15 @@ namespace clara { namespace TextFlow {
 
     class Columns;
 
+    struct ColumnLayout {
+        size_t width = CLARA_TEXTFLOW_CONFIG_CONSOLE_WIDTH;
+        size_t indent = 0;
+        size_t initialIndent = std::string::npos;
+    };
+
     class Column {
         std::vector<std::string> m_strings;
-        size_t m_width = CLARA_TEXTFLOW_CONFIG_CONSOLE_WIDTH;
-        size_t m_indent = 0;
-        size_t m_initialIndent = std::string::npos;
+        ColumnLayout m_layout;
 
     public:
         class iterator {
@@ -108,7 +112,7 @@ namespace clara { namespace TextFlow {
                 assert( m_stringIndex < m_column.m_strings.size() );
 
                 m_suffix = false;
-                auto width = m_column.m_width-indent();
+                auto width = m_column.m_layout.width-indent();
                 m_end = m_pos;
                 if (line()[m_pos] == '\n') {
                     ++m_end;
@@ -136,8 +140,8 @@ namespace clara { namespace TextFlow {
             }
 
             auto indent() const -> size_t {
-                auto initial = m_pos == 0 && m_stringIndex == 0 ? m_column.m_initialIndent : std::string::npos;
-                return initial == std::string::npos ? m_column.m_indent : initial;
+                auto initial = m_pos == 0 && m_stringIndex == 0 ? m_column.m_layout.initialIndent : std::string::npos;
+                return initial == std::string::npos ? m_column.m_layout.indent : initial;
             }
 
             auto addIndentAndSuffix(std::string const &plain) const -> std::string {
@@ -152,8 +156,8 @@ namespace clara { namespace TextFlow {
             using iterator_category = std::forward_iterator_tag;
 
             explicit iterator( Column const& column ) : m_column( column ) {
-                assert( m_column.m_width > m_column.m_indent );
-                assert( m_column.m_initialIndent == std::string::npos || m_column.m_width > m_column.m_initialIndent );
+                assert( m_column.m_layout.width > m_column.m_layout.indent );
+                assert( m_column.m_layout.initialIndent == std::string::npos || m_column.m_layout.width > m_column.m_layout.initialIndent );
                 calcLength();
                 if( m_len == 0 )
                     m_stringIndex++; // Empty string
@@ -203,19 +207,19 @@ namespace clara { namespace TextFlow {
 
         auto width( size_t newWidth ) -> Column& {
             assert( newWidth > 0 );
-            m_width = newWidth;
+            m_layout.width = newWidth;
             return *this;
         }
         auto indent( size_t newIndent ) -> Column& {
-            m_indent = newIndent;
+            m_layout.indent = newIndent;
             return *this;
         }
         auto initialIndent( size_t newIndent ) -> Column& {
-            m_initialIndent = newIndent;
+            m_layout.initialIndent = newIndent;
             return *this;
         }
 
-        auto width() const -> size_t { return m_width; }
+        auto width() const -> size_t { return m_layout.width; }
         auto begin() const -> iterator { return iterator( *this ); }
         auto end() const -> iterator { return { *this, m_strings.size() }; }
 
@@ -298,17 +302,17 @@ namespace clara { namespace TextFlow {
                 std::string row, padding;
 
                 for( size_t i = 0; i < m_columns.size(); ++i ) {
-                    auto width = m_columns[i].width();
+                    auto colWidth = m_columns[i].width();
                     if( m_iterators[i] != m_columns[i].end() ) {
                         std::string col = *m_iterators[i];
                         row += padding + col;
-                        if( col.size() < width )
-                            padding = std::string( width - col.size(), ' ' );
+                        if( col.size() < colWidth )
+                            padding = std::string( colWidth - col.size(), ' ' );
                         else
                             padding = "";
                     }
                     else {
-                        padding += std::string( width, ' ' );
+                        padding += std::string( colWidth, ' ' );
                     }
                 }
                 return row;

```
