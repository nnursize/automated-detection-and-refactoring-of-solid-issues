# Refactor SRP-008 (SRP): Combines docstring parsing logic with string formatting/rendering logic.

**Status:** `applied_failed`  
**Branch:** `refactor/SRP-008` -> `main`  
**Head commit:** `11e83875a77e0bb4e9692f7d424a486dbeb007fc`  
**LLM finish:** `FinishReason.STOP` (prompt 7374, completion 2404)  

## Detected issue

- **File**: `seaborn/external/docscrape.py`
- **Entity**: `NumpyDocString` (class)
- **Lines (at detection time)**: L136–L561
- **Severity**: medium
- **Confidence**: detected by 3 scan(s)

**Description.** Combines docstring parsing logic with string formatting/rendering logic.

**Reasoning.** The class is responsible for both parsing raw docstrings into an internal mapping structure and generating formatted string outputs (e.g., _str_header, _str_param_list). These are two distinct responsibilities: data ingestion/parsing and data presentation/formatting.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 1
- **Files modified** (1): `seaborn/external/docscrape.py`

**Summary.** Extract docstring formatting logic into a separate NumpyDocStringFormatter class.

**Rationale.** The NumpyDocString class was violating SRP by handling both parsing and formatting. I have extracted the formatting methods into a new NumpyDocStringFormatter class to separate these concerns.

## Changes overview

_1 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `seaborn/external/docscrape.py` (132-line block → 139-line replacement)

**Replaces:**

```python
    def _error_location(self, msg, error=True):
        if hasattr(self, '_obj'):
            # we know where the docs came from:
            try:
                filename = inspect.getsourcefile(self._obj)
            except TypeError:
                filename = None
            msg = msg + f" in the docstring of {self._obj} in {filename}."
        if error:
            raise ValueError(msg)
        else:
            warn(msg)

    # string conversion routines

    def _str_header(self, name, symbol='-'):
        return [name, len(name)*symbol]

    def _str_indent(self, doc, indent=4):
        out = []
        for line in doc:
            out += [' '*indent + line]
        return out

    def _str_signature(self):
        if self['Signature']:
            return [self['Signature'].replace('*', r'\*')] + ['']
        else:
            return ['']

    def _str_summary(self):
        if self['Summary']:
            return self['Summary'] + ['']
        else:
            return []

    def _str_extended_summary(self):
        if self['Extended Summary']:
            return self['Extended Summary'] + ['']
        else:
            return []

    def _str_param_list(self, name):
        out = []
        if self[name]:
            out += self._str_header(name)
            for param in self[name]:
                parts = []
                if param.name:
                    parts.append(param.name)
                if param.type:
                    parts.append(param.type)
                out += [' : '.join(parts)]
                if param.desc and ''.join(param.desc).strip():
                    out += self._str_indent(param.desc)
            out += ['']
        return out

    def _str_section(self, name):
        out = []
... (72 more line(s) truncated)
```

**With:**

```python
    def _error_location(self, msg, error=True):
        if hasattr(self, '_obj'):
            # we know where the docs came from:
            try:
                filename = inspect.getsourcefile(self._obj)
            except TypeError:
                filename = None
            msg = msg + f" in the docstring of {self._obj} in {filename}."
        if error:
            raise ValueError(msg)
        else:
            warn(msg)

    def __str__(self, func_role=''):
        return str(NumpyDocStringFormatter(self, func_role))


class NumpyDocStringFormatter:
    def __init__(self, docstring, func_role=''):
        self.docstring = docstring
        self.func_role = func_role

    def _str_header(self, name, symbol='-'):
        return [name, len(name)*symbol]

    def _str_indent(self, doc, indent=4):
        out = []
        for line in doc:
            out += [' '*indent + line]
        return out

    def _str_signature(self):
        if self.docstring['Signature']:
            return [self.docstring['Signature'].replace('*', r'\*')] + ['']
        else:
            return ['']

    def _str_summary(self):
        if self.docstring['Summary']:
            return self.docstring['Summary'] + ['']
        else:
            return []

    def _str_extended_summary(self):
        if self.docstring['Extended Summary']:
            return self.docstring['Extended Summary'] + ['']
        else:
            return []

    def _str_param_list(self, name):
        out = []
        if self.docstring[name]:
            out += self._str_header(name)
            for param in self.docstring[name]:
                parts = []
                if param.name:
                    parts.append(param.name)
                if param.type:
                    parts.append(param.type)
                out += [' : '.join(parts)]
... (79 more line(s) truncated)
```

## Test results

**FAILED** — 784/792 passed, 1 failed, 1 skipped, 0 errored (duration 35769 ms).

- New failures introduced by this refactor: **1**
- Pre-existing failures (unrelated to this refactor): **0**

New-failure node IDs (first 25):

  - `tests/test_axisgrid.py::TestFacetGrid::test_refline`

Command: `C:\Users\User\Desktop\SDP-Codex\S1-T7-Okeyish\refactor_workspaces\seaborn-master\.venv\Scripts\python.exe -m pytest --tb=short -q --no-header -p no:cacheprovider -x --json-report --json-report-file=C:\Users\User\Desktop\SDP-Codex\S1-T7-Okeyish\refactor_workspaces\seaborn-master\.pytest_report.json`

<details><summary>Output tail</summary>

```
....................................s................................... [  3%]
.................................x............x...x................x.x.. [  6%]
........................................................................ [  9%]
........................................................................ [ 12%]
........................................................................ [ 15%]
........................................................................ [ 18%]
.....................................................................x.. [ 21%]
........................................................................ [ 24%]
........................................................................ [ 27%]
........................................................................ [ 30%]
.......................................................................F [ 33%]

================================== FAILURES ===================================
_________________________ TestFacetGrid.test_refline __________________________
tests\test_axisgrid.py:653: in test_refline
    g = ag.FacetGrid(self.df, row="a", col="b")
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
seaborn\axisgrid.py:453: in __init__
    fig = plt.figure(figsize=figsize)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^
.venv\Lib\site-packages\matplotlib\pyplot.py:1041: in figure
    manager = new_figure_manager(
.venv\Lib\site-packages\matplotlib\pyplot.py:551: in new_figure_manager
    return _get_backend_mod().new_figure_manager(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.venv\Lib\site-packages\matplotlib\backend_bases.py:3504: in new_figure_manager
    return cls.new_figure_manager_given_figure(num, fig)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.venv\Lib\site-packages\matplotlib\backend_bases.py:3509: in new_figure_manager_given_figure
    return cls.FigureCanvas.new_manager(figure, num)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.venv\Lib\site-packages\matplotlib\backend_bases.py:1785: in new_manager
    return cls.manager_class.create_with_canvas(cls, figure, num)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.venv\Lib\site-packages\matplotlib\backends\_backend_tk.py:535: in create_with_canvas
    window = tk.Tk(className="matplotlib")
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Users\User\miniconda3\Lib\tkinter\__init__.py:2326: in __init__
    self.tk = _tkinter.create(screenName, baseName, className, interactive, wantobjects, useTk, sync, use)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   _tkinter.TclError: Can't find a usable tk.tcl in the following directories: 
E       C:/Users/User/miniconda3/Library/lib/tcl8.6/tk8.6 C:/Users/User/miniconda3/Library/lib/tk8.6 C:/Users/User/lib/tk8.6 C:/Users/User/lib/tk8.6 C:/Users/lib/tk8.6 C:/Users/User/library
E   
E   C:/Users/User/miniconda3/Library/lib/tk8.6/tk.tcl: couldn't read file "C:/Users/User/miniconda3/Library/lib/tk8.6/entry.tcl": no such file or directory
E   couldn't read file "C:/Users/User/miniconda3/Library/lib/tk8.6/entry.tcl": no such file or directory
E       while executing
E   "source -encoding utf-8 C:/Users/User/miniconda3/Library/lib/tk8.6/entry.tcl"
E       (in namespace eval "::" script line 1)
E       invoked from within
E   "namespace eval :: [list source -encoding utf-8 [file join $::tk_library $file.tcl]]"
E       (procedure "SourceLibFile" line 2)
E       invoked from within
E   "SourceLibFile entry"
E       (in namespace eval "::tk" script line 4)
E       invoked from within
E   "namespace eval ::tk {
E   	SourceLibFile icons
E   	SourceLibFile button
E   	SourceLibFile entry
E   	SourceLibFile listbox
E   	SourceLibFile menu
E   	SourceLibFile panedw..."
E       (file "C:/Users/User/miniconda3/Library/lib/tk8.6/tk.tcl" line 501)
E       invoked from within
E   "source C:/Users/User/miniconda3/Library/lib/tk8.6/tk.tcl"
E       ("uplevel" body line 1)
E       invoked from within
E   "uplevel #0 [list source $file]"
E   
E   
E   This probably means that tk wasn't installed properly.
=========================== short test summary info ===========================
FAILED tests/test_axisgrid.py::TestFacetGrid::test_refline - _tkinter.TclErro...
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!
1 failed, 784 passed, 1 skipped, 6 xfailed in 34.59s

```

</details>

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `seaborn/external/docscrape.py` | 572 → - | 53 → - | 4.04 → - | 18 → - | 12.29 → - |

## Diff

```diff
diff --git a/seaborn/external/docscrape.py b/seaborn/external/docscrape.py
index 99dc3ff..61c2e52 100644
--- a/seaborn/external/docscrape.py
+++ b/seaborn/external/docscrape.py
@@ -440,7 +440,14 @@ class NumpyDocString(Mapping):
         else:
             warn(msg)
 
-    # string conversion routines
+    def __str__(self, func_role=''):
+        return str(NumpyDocStringFormatter(self, func_role))
+
+
+class NumpyDocStringFormatter:
+    def __init__(self, docstring, func_role=''):
+        self.docstring = docstring
+        self.func_role = func_role
 
     def _str_header(self, name, symbol='-'):
         return [name, len(name)*symbol]
@@ -452,28 +459,28 @@ class NumpyDocString(Mapping):
         return out
 
     def _str_signature(self):
-        if self['Signature']:
-            return [self['Signature'].replace('*', r'\*')] + ['']
+        if self.docstring['Signature']:
+            return [self.docstring['Signature'].replace('*', r'\*')] + ['']
         else:
             return ['']
 
     def _str_summary(self):
-        if self['Summary']:
-            return self['Summary'] + ['']
+        if self.docstring['Summary']:
+            return self.docstring['Summary'] + ['']
         else:
             return []
 
     def _str_extended_summary(self):
-        if self['Extended Summary']:
-            return self['Extended Summary'] + ['']
+        if self.docstring['Extended Summary']:
+            return self.docstring['Extended Summary'] + ['']
         else:
             return []
 
     def _str_param_list(self, name):
         out = []
-        if self[name]:
+        if self.docstring[name]:
             out += self._str_header(name)
-            for param in self[name]:
+            for param in self.docstring[name]:
                 parts = []
                 if param.name:
                     parts.append(param.name)
@@ -487,27 +494,27 @@ class NumpyDocString(Mapping):
 
     def _str_section(self, name):
         out = []
-        if self[name]:
+        if self.docstring[name]:
             out += self._str_header(name)
-            out += self[name]
+            out += self.docstring[name]
             out += ['']
         return out
 
-    def _str_see_also(self, func_role):
-        if not self['See Also']:
+    def _str_see_also(self):
+        if not self.docstring['See Also']:
             return []
         out = []
         out += self._str_header("See Also")
         out += ['']
         last_had_desc = True
-        for funcs, desc in self['See Also']:
+        for funcs, desc in self.docstring['See Also']:
             assert isinstance(funcs, list)
             links = []
             for func, role in funcs:
                 if role:
                     link = f':{role}:`{func}`'
-                elif func_role:
-                    link = f':{func_role}:`{func}`'
+                elif self.func_role:
+                    link = f':{self.func_role}:`{func}`'
                 else:
                     link = f"`{func}`_"
                 links.append(link)
@@ -518,7 +525,7 @@ class NumpyDocString(Mapping):
                 last_had_desc = True
             else:
                 last_had_desc = False
-                out += self._str_indent([self.empty_description])
+                out += self._str_indent([self.docstring.empty_description])
 
         if last_had_desc:
             out += ['']
@@ -526,7 +533,7 @@ class NumpyDocString(Mapping):
         return out
 
     def _str_index(self):
-        idx = self['index']
+        idx = self.docstring['index']
         out = []
         output_index = False
         default_index = idx.get('default', '')
@@ -543,7 +550,7 @@ class NumpyDocString(Mapping):
         else:
             return ''
 
-    def __str__(self, func_role=''):
+    def __str__(self):
         out = []
         out += self._str_signature()
         out += self._str_summary()
@@ -552,7 +559,7 @@ class NumpyDocString(Mapping):
                            'Other Parameters', 'Raises', 'Warns'):
             out += self._str_param_list(param_list)
         out += self._str_section('Warnings')
-        out += self._str_see_also(func_role)
+        out += self._str_see_also()
         for s in ('Notes', 'References', 'Examples'):
             out += self._str_section(s)
         for param_list in ('Attributes', 'Methods'):

```
