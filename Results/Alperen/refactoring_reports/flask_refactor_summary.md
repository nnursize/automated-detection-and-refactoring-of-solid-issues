# Refactor summary: flask

- Total attempts: **59**
  - `applied_passed`: 53
  - `patch_failed`: 1
  - `llm_error`: 5
- Final full-suite gate: **FAILED**

## All attempts

| Issue | Principle | Status | Tests passed/total | CC before -> after | MI before -> after | File |
|-------|-----------|--------|--------------------|--------------------|--------------------|------|
| DIP-001 | DIP | `applied_passed` | - | 2.72 -> 2.74 | 18.37 -> 18.21 | `src/flask/app.py` |
| DIP-002 | DIP | `applied_passed` | - | 2.25 -> 2.5 | 86.16 -> 83.89 | `src/flask/blueprints.py` |
| DIP-003 | DIP | `applied_passed` | - | 2.45 -> 2.41 | 31.2 -> 30.92 | `src/flask/sansio/app.py` |
| DIP-004 | DIP | `llm_error` | - | - | - | `src/flask/ctx.py` |
| DIP-005 | DIP | `llm_error` | - | - | - | `src/flask/cli.py` |
| DIP-006 | DIP | `applied_passed` | - | 2.03 -> 2.0 | 41.1 -> 40.67 | `src/flask/sansio/scaffold.py` |
| DIP-007 | DIP | `llm_error` | - | - | - | `src/flask/config.py` |
| DIP-008 | DIP | `llm_error` | - | - | - | `src/flask/sessions.py` |
| DIP-009 | DIP | `applied_passed` | - | 2.18 -> 2.08 | 62.73 -> 63.37 | `src/flask/json/provider.py` |
| DIP-010 | DIP | `applied_passed` | - | 2.31 -> 2.1 | 62.48 -> 60.5 | `src/flask/templating.py` |
| DIP-011 | DIP | `applied_passed` | - | 2.1 -> 2.0 | 60.5 -> 59.18 | `src/flask/templating.py` |
| ISP-001 | ISP | `applied_passed` | - | 3.05 -> 3.02 | 20.38 -> 20.23 | `src/flask/app.py` |
| ISP-002 | ISP | `applied_passed` | - | 3.02 -> 2.95 | 20.23 -> 20.31 | `src/flask/app.py` |
| ISP-003 | ISP | `llm_error` | - | - | - | `src/flask/app.py` |
| ISP-005 | ISP | `applied_passed` | - | 2.95 -> 2.86 | 20.31 -> 19.46 | `src/flask/app.py` |
| ISP-006 | ISP | `applied_passed` | - | 2.86 -> 2.77 | 19.46 -> 18.86 | `src/flask/app.py` |
| ISP-007 | ISP | `applied_passed` | - | 2.77 -> 2.72 | 18.86 -> 18.37 | `src/flask/app.py` |
| ISP-027 | ISP | `applied_passed` | - | 2.49 -> 2.45 | 31.37 -> 31.2 | `src/flask/sansio/app.py` |
| ISP-044 | ISP | `applied_passed` | - | 1.78 -> 2.03 | 42.81 -> 41.1 | `src/flask/sansio/scaffold.py` |
| ISP-074 | ISP | `applied_passed` | - | 2.0 -> 2.25 | 65.71 -> 79.26 | `src/flask/sessions.py` |
| ISP-079 | ISP | `applied_passed` | - | 2.07 -> 1.72 | 55.69 -> 81.36 | `src/flask/json/provider.py` |
| ISP-083 | ISP | `applied_passed` | - | 1.76 -> 1.84 | 51.12 -> 50.94 | `src/flask/ctx.py` |
| ISP-084 | ISP | `applied_passed` | - | 2.0 -> 1.85 | 68.15 -> 67.52 | `src/flask/sessions.py` |
| LSP-001 | LSP | `applied_passed` | - | 3.02 -> 3.05 | 20.8 -> 20.38 | `src/flask/app.py` |
| LSP-002 | LSP | `applied_passed` | - | 3.9 -> 3.83 | 24.01 -> 23.86 | `src/flask/app.py` |
| LSP-003 | LSP | `applied_passed` | - | 3.83 -> 3.56 | 23.86 -> 23.11 | `src/flask/app.py` |
| LSP-005 | LSP | `applied_passed` | - | 3.56 -> 3.5 | 23.11 -> 22.72 | `src/flask/app.py` |
| LSP-006 | LSP | `applied_passed` | - | 3.5 -> 3.45 | 22.72 -> 22.05 | `src/flask/app.py` |
| LSP-007 | LSP | `applied_passed` | - | 3.45 -> 3.4 | 22.05 -> 21.59 | `src/flask/app.py` |
| LSP-011 | LSP | `applied_passed` | - | 3.4 -> 3.35 | 21.59 -> 21.4 | `src/flask/app.py` |
| LSP-017 | LSP | `applied_passed` | - | 3.97 -> 3.9 | 24.23 -> 24.01 | `src/flask/app.py` |
| LSP-022 | LSP | `applied_passed` | - | 2.38 -> 2.49 | 32.2 -> 31.37 | `src/flask/sansio/app.py` |
| LSP-024 | LSP | `applied_passed` | - | 1.78 -> 1.78 | 43.09 -> 42.81 | `src/flask/sansio/scaffold.py` |
| LSP-025 | LSP | `applied_passed` | - | 4.5 -> 4.5 | 60.69 -> 60.69 | `src/flask/views.py` |
| LSP-027 | LSP | `patch_failed` | - | - | - | `src/flask/sansio/blueprints.py` |
| OCP-001 | OCP | `applied_passed` | - | 3.35 -> 3.3 | 21.4 -> 21.22 | `src/flask/app.py` |
| OCP-002 | OCP | `applied_passed` | - | 4.58 -> 4.58 | 26.14 -> 26.04 | `src/flask/cli.py` |
| OCP-003 | OCP | `applied_passed` | - | 4.58 -> 3.77 | 26.04 -> 48.73 | `src/flask/cli.py` |
| OCP-008 | OCP | `applied_passed` | - | 2.38 -> 2.38 | 32.43 -> 32.2 | `src/flask/sansio/app.py` |
| OCP-010 | OCP | `applied_passed` | - | 1.88 -> 2.64 | 43.89 -> 64.27 | `src/flask/sansio/scaffold.py` |
| OCP-011 | OCP | `applied_passed` | - | 2.58 -> 2.44 | 44.89 -> 44.21 | `src/flask/sansio/blueprints.py` |
| OCP-013 | OCP | `applied_passed` | - | 2.4 -> 2.12 | 57.72 -> 69.9 | `src/flask/json/provider.py` |
| OCP-020 | OCP | `applied_passed` | - | 3.05 -> 3.02 | 20.99 -> 20.8 | `src/flask/app.py` |
| OCP-022 | OCP | `applied_passed` | - | 3.92 -> 3.97 | 24.6 -> 24.23 | `src/flask/app.py` |
| OCP-027 | OCP | `applied_passed` | - | 3.3 -> 3.17 | 21.22 -> 20.82 | `src/flask/app.py` |
| OCP-033 | OCP | `applied_passed` | - | 3.17 -> 3.05 | 20.82 -> 20.99 | `src/flask/app.py` |
| OCP-042 | OCP | `applied_passed` | - | 4.37 -> 4.28 | 29.36 -> 28.69 | `src/flask/cli.py` |
| SRP-001 | SRP | `applied_passed` | - | 4.28 -> 3.13 | 22.29 -> 61.27 | `src/flask/app.py` |
| SRP-004 | SRP | `applied_passed` | - | 4.26 -> 7.99 | 22.54 -> 51.24 | `src/flask/app.py` |
| SRP-005 | SRP | `applied_passed` | - | 3.97 -> 2.96 | 24.26 -> 58.91 | `src/flask/app.py` |
| SRP-014 | SRP | `applied_passed` | - | 2.4 -> 2.25 | 81.73 -> 86.16 | `src/flask/blueprints.py` |
| SRP-025 | SRP | `applied_passed` | - | 2.38 -> 2.19 | 32.43 -> 66.22 | `src/flask/sansio/app.py` |
| SRP-030 | SRP | `applied_passed` | - | 1.88 -> 1.44 | 43.85 -> 71.94 | `src/flask/sansio/scaffold.py` |
| SRP-036 | SRP | `applied_passed` | 474/477 | 2.38 -> 2.4 | 58.28 -> 57.72 | `src/flask/json/provider.py` |
| SRP-040 | SRP | `applied_passed` | 474/477 | 2.62 -> 2.58 | 45.14 -> 44.89 | `src/flask/sansio/blueprints.py` |
| SRP-043 | SRP | `applied_passed` | - | 2.03 -> 2.25 | 49.53 -> 67.45 | `src/flask/ctx.py` |
| SRP-044 | SRP | `applied_passed` | - | 1.81 -> 1.75 | 59.25 -> 64.47 | `src/flask/sessions.py` |
| SRP-046 | SRP | `applied_passed` | 474/477 | 3.06 -> 2.84 | 57.45 -> 62.48 | `src/flask/config.py` |
| SRP-061 | SRP | `applied_passed` | - | 4.67 -> 4.58 | 26.77 -> 26.14 | `src/flask/cli.py` |