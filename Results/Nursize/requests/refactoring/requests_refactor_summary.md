# Refactor summary: requests

- Total attempts: **60**
  - `applied_passed`: 35
  - `applied_failed`: 9
  - `patch_failed`: 7
  - `detection_rejected`: 3
  - `obsolete`: 2
  - `llm_error`: 4
- Final full-suite gate: **FAILED**

## All attempts

| Issue | Principle | Status | Tests passed/total | CC before -> after | MI before -> after | File |
|-------|-----------|--------|--------------------|--------------------|--------------------|------|
| DIP-001 | DIP | `applied_passed` | 606/610 | 1.0 -> 1.0 | 100.0 -> 100.0 | `src/requests/api.py` |
| DIP-002 | DIP | `applied_passed` | 606/610 | 3.85 -> 3.91 | 37.21 -> 36.83 | `src/requests/sessions.py` |
| DIP-003 | DIP | `applied_passed` | 606/610 | 3.86 -> 3.88 | 20.36 -> 20.13 | `src/requests/models.py` |
| DIP-004 | DIP | `patch_failed` | - | - | - | `src/requests/adapters.py` |
| DIP-006 | DIP | `patch_failed` | - | - | - | `src/requests/auth.py` |
| DIP-007 | DIP | `obsolete` | - | - | - | `src/requests/utils.py` |
| DIP-008 | DIP | `applied_passed` | 606/610 | 3.88 -> 3.88 | 20.13 -> 20.13 | `src/requests/models.py` |
| DIP-012 | DIP | `applied_passed` | 606/610 | 2.42 -> 2.42 | 39.73 -> 39.74 | `src/requests/cookies.py` |
| DIP-015 | DIP | `applied_passed` | 606/610 | 1.0 -> 1.0 | 100.0 -> 100.0 | `src/requests/api.py` |
| DIP-020 | DIP | `applied_passed` | 606/610 | 3.88 -> 3.83 | 20.13 -> 20.06 | `src/requests/models.py` |
| DIP-026 | DIP | `obsolete` | - | - | - | `src/requests/__init__.py` |
| DIP-029 | DIP | `applied_failed` | 309/312 | - | - | `src/requests/sessions.py` |
| ISP-001 | ISP | `patch_failed` | - | - | - | `src/requests/cookies.py` |
| ISP-002 | ISP | `applied_passed` | 606/610 | 2.42 -> 2.4 | 39.73 -> 39.52 | `src/requests/cookies.py` |
| ISP-003 | ISP | `applied_passed` | 606/610 | 2.4 -> 2.42 | 39.51 -> 39.73 | `src/requests/cookies.py` |
| ISP-004 | ISP | `applied_failed` | 7/8 | - | - | `src/requests/adapters.py` |
| ISP-005 | ISP | `applied_passed` | 606/610 | 2.42 -> 2.4 | 39.73 -> 39.51 | `src/requests/cookies.py` |
| ISP-006 | ISP | `applied_passed` | 606/610 | 2.4 -> 2.42 | 39.52 -> 39.73 | `src/requests/cookies.py` |
| ISP-007 | ISP | `llm_error` | - | - | - | `src/requests/adapters.py` |
| ISP-008 | ISP | `applied_passed` | 606/610 | 2.4 -> 2.42 | 39.51 -> 39.73 | `src/requests/cookies.py` |
| ISP-009 | ISP | `applied_passed` | 606/610 | 4.18 -> 4.2 | 21.48 -> 21.45 | `src/requests/models.py` |
| ISP-010 | ISP | `llm_error` | - | - | - | `src/requests/cookies.py` |
| ISP-011 | ISP | `applied_passed` | 606/610 | 4.2 -> 3.86 | 21.45 -> 20.36 | `src/requests/models.py` |
| ISP-012 | ISP | `applied_passed` | 606/610 | 3.93 -> 3.85 | 38.99 -> 37.21 | `src/requests/sessions.py` |
| LSP-001 | LSP | `llm_error` | - | - | - | `src/requests/structures.py` |
| LSP-002 | LSP | `applied_passed` | 606/610 | 2.38 -> 2.38 | 39.8 -> 39.8 | `src/requests/cookies.py` |
| LSP-004 | LSP | `applied_failed` | 177/179 | - | - | `src/requests/cookies.py` |
| LSP-005 | LSP | `applied_failed` | 177/179 | - | - | `src/requests/cookies.py` |
| LSP-006 | LSP | `applied_passed` | 606/610 | 2.38 -> 2.4 | 39.8 -> 39.51 | `src/requests/cookies.py` |
| LSP-007 | LSP | `applied_passed` | 606/610 | 2.38 -> 2.4 | 39.8 -> 39.51 | `src/requests/cookies.py` |
| LSP-008 | LSP | `applied_passed` | 606/610 | 2.63 -> 2.41 | 50.08 -> 48.46 | `src/requests/auth.py` |
| LSP-009 | LSP | `applied_failed` | 352/355 | - | - | `src/requests/structures.py` |
| LSP-010 | LSP | `patch_failed` | - | - | - | `src/requests/auth.py` |
| LSP-015 | LSP | `patch_failed` | - | - | - | `src/requests/auth.py` |
| LSP-016 | LSP | `applied_passed` | 606/610 | 2.38 -> 2.38 | 39.76 -> 39.8 | `src/requests/cookies.py` |
| LSP-019 | LSP | `applied_passed` | 606/610 | 2.4 -> 2.38 | 39.51 -> 39.8 | `src/requests/cookies.py` |
| OCP-002 | OCP | `applied_passed` | 606/610 | 4.29 -> 4.29 | 25.03 -> 25.03 | `src/requests/utils.py` |
| OCP-007 | OCP | `applied_passed` | 606/610 | 4.46 -> 4.24 | 20.13 -> 21.18 | `src/requests/models.py` |
| OCP-008 | OCP | `applied_passed` | 606/610 | 4.24 -> 4.18 | 21.18 -> 21.48 | `src/requests/models.py` |
| OCP-010 | OCP | `applied_failed` | 41/42 | - | - | `src/requests/models.py` |
| OCP-020 | OCP | `applied_passed` | 606/610 | 2.58 -> 2.63 | 48.8 -> 50.08 | `src/requests/auth.py` |
| OCP-021 | OCP | `applied_passed` | 606/610 | 4.07 -> 3.93 | 38.09 -> 38.95 | `src/requests/sessions.py` |
| OCP-022 | OCP | `applied_passed` | 606/610 | 4.55 -> 4.29 | 25.21 -> 25.03 | `src/requests/utils.py` |
| OCP-025 | OCP | `applied_failed` | 41/42 | - | - | `src/requests/models.py` |
| OCP-029 | OCP | `applied_passed` | 606/610 | 3.42 -> 3.42 | 47.34 -> 46.92 | `src/requests/adapters.py` |
| OCP-030 | OCP | `applied_passed` | 606/610 | 3.93 -> 3.93 | 38.95 -> 38.99 | `src/requests/sessions.py` |
| OCP-031 | OCP | `applied_passed` | 606/610 | 3.42 -> 3.29 | 46.92 -> 47.37 | `src/requests/adapters.py` |
| OCP-033 | OCP | `patch_failed` | - | - | - | `src/requests/sessions.py` |
| SRP-001 | SRP | `llm_error` | - | - | - | `src/requests/utils.py` |
| SRP-006 | SRP | `detection_rejected` | - | - | - | `src/requests/models.py` |
| SRP-007 | SRP | `applied_passed` | 606/610 | 4.46 -> 4.39 | 21.73 -> 21.22 | `src/requests/models.py` |
| SRP-008 | SRP | `detection_rejected` | - | - | - | `src/requests/models.py` |
| SRP-010 | SRP | `applied_passed` | 606/610 | 4.39 -> 4.46 | 21.22 -> 20.13 | `src/requests/models.py` |
| SRP-013 | SRP | `applied_failed` | 64/65 | - | - | `src/requests/sessions.py` |
| SRP-016 | SRP | `patch_failed` | - | - | - | `src/requests/sessions.py` |
| SRP-020 | SRP | `applied_passed` | 606/610 | 3.73 -> 3.61 | 47.52 -> 47.34 | `src/requests/adapters.py` |
| SRP-021 | SRP | `detection_rejected` | - | - | - | `src/requests/adapters.py` |
| SRP-024 | SRP | `applied_passed` | 606/610 | 3.61 -> 3.42 | 47.34 -> 47.34 | `src/requests/adapters.py` |
| SRP-028 | SRP | `applied_passed` | 606/610 | 2.95 -> 2.58 | 47.4 -> 48.8 | `src/requests/auth.py` |
| SRP-056 | SRP | `applied_failed` | 183/185 | - | - | `src/requests/models.py` |