# Refactor summary: seaborn-master

- Total attempts: **60**
  - `applied_passed`: 44
  - `applied_failed`: 9
  - `patch_failed`: 7
- Final full-suite gate: **FAILED**

## All attempts

| Issue | Principle | Status | Tests passed/total | CC before -> after | MI before -> after | File |
|-------|-----------|--------|--------------------|--------------------|--------------------|------|
| DIP-001 | DIP | `applied_passed` | - | 7.21 -> 7.21 | 0.0 -> 0.0 | `seaborn/categorical.py` |
| DIP-002 | DIP | `applied_passed` | - | 8.75 -> 8.75 | 0.0 -> 0.0 | `seaborn/distributions.py` |
| DIP-004 | DIP | `applied_passed` | - | 6.14 -> 6.16 | 0.0 -> 0.0 | `seaborn/axisgrid.py` |
| DIP-005 | DIP | `patch_failed` | - | - | - | `seaborn/_core/plot.py` |
| DIP-006 | DIP | `applied_passed` | - | 7.21 -> 7.21 | 0.0 -> 0.0 | `seaborn/categorical.py` |
| DIP-007 | DIP | `applied_passed` | - | 5.22 -> 5.22 | 0.0 -> 0.0 | `seaborn/_core/plot.py` |
| DIP-008 | DIP | `applied_passed` | - | 8.75 -> 8.4 | 0.0 -> 0.0 | `seaborn/distributions.py` |
| DIP-009 | DIP | `applied_passed` | - | 6.13 -> 6.14 | 0.0 -> 0.0 | `seaborn/axisgrid.py` |
| DIP-010 | DIP | `applied_passed` | - | 6.76 -> 6.78 | 0.0 -> 0.0 | `seaborn/_base.py` |
| DIP-011 | DIP | `applied_passed` | - | 2.61 -> 2.61 | 21.94 -> 21.94 | `seaborn/_core/scales.py` |
| DIP-016 | DIP | `applied_passed` | - | 7.21 -> 7.23 | 0.0 -> 0.0 | `seaborn/categorical.py` |
| DIP-031 | DIP | `applied_passed` | - | 2.57 -> 2.61 | 21.68 -> 21.94 | `seaborn/_core/scales.py` |
| ISP-001 | ISP | `applied_passed` | - | 2.66 -> 2.64 | 21.81 -> 21.74 | `seaborn/_core/scales.py` |
| ISP-002 | ISP | `patch_failed` | - | - | - | `seaborn/_base.py` |
| ISP-003 | ISP | `applied_passed` | - | 7.09 -> 7.21 | 0.0 -> 0.0 | `seaborn/categorical.py` |
| ISP-004 | ISP | `applied_passed` | - | 6.82 -> 6.76 | 0.0 -> 0.0 | `seaborn/_base.py` |
| ISP-005 | ISP | `applied_passed` | - | 2.64 -> 2.57 | 21.69 -> 21.88 | `seaborn/_core/scales.py` |
| ISP-006 | ISP | `applied_passed` | - | 11.2 -> 8.75 | 0.0 -> 0.0 | `seaborn/distributions.py` |
| ISP-007 | ISP | `applied_passed` | - | 2.64 -> 2.64 | 21.74 -> 21.74 | `seaborn/_core/scales.py` |
| ISP-008 | ISP | `applied_passed` | - | 5.76 -> 5.76 | 20.95 -> 20.95 | `seaborn/matrix.py` |
| ISP-009 | ISP | `applied_passed` | - | 5.19 -> 5.22 | 0.0 -> 0.0 | `seaborn/_core/plot.py` |
| ISP-010 | ISP | `applied_passed` | - | 5.22 -> 5.22 | 0.0 -> 0.0 | `seaborn/_core/plot.py` |
| ISP-011 | ISP | `applied_passed` | - | 2.57 -> 2.57 | 21.88 -> 21.88 | `seaborn/_core/scales.py` |
| ISP-015 | ISP | `applied_passed` | - | 2.64 -> 2.64 | 21.74 -> 21.69 | `seaborn/_core/scales.py` |
| LSP-001 | LSP | `patch_failed` | - | - | - | `seaborn/_core/scales.py` |
| LSP-002 | LSP | `patch_failed` | - | - | - | `seaborn/_core/properties.py` |
| LSP-004 | LSP | `applied_passed` | - | 11.2 -> 11.2 | 0.0 -> 0.0 | `seaborn/distributions.py` |
| LSP-005 | LSP | `applied_passed` | - | 2.57 -> 2.57 | 21.88 -> 21.68 | `seaborn/_core/scales.py` |
| LSP-006 | LSP | `applied_passed` | - | 2.89 -> 2.94 | 23.43 -> 23.05 | `seaborn/_core/properties.py` |
| LSP-007 | LSP | `applied_passed` | - | 2.79 -> 2.79 | 23.47 -> 23.47 | `seaborn/_core/scales.py` |
| LSP-008 | LSP | `applied_passed` | - | 6.84 -> 6.82 | 0.0 -> 0.0 | `seaborn/_base.py` |
| LSP-010 | LSP | `applied_passed` | - | 7.0 -> 7.0 | 0.0 -> 0.0 | `seaborn/categorical.py` |
| LSP-012 | LSP | `applied_passed` | - | 7.0 -> 7.09 | 0.0 -> 0.0 | `seaborn/categorical.py` |
| LSP-020 | LSP | `applied_passed` | - | 5.0 -> 5.09 | 27.93 -> 27.42 | `seaborn/regression.py` |
| LSP-023 | LSP | `applied_passed` | - | 2.79 -> 2.66 | 23.27 -> 21.81 | `seaborn/_core/scales.py` |
| LSP-025 | LSP | `applied_passed` | - | 2.79 -> 2.79 | 23.47 -> 23.27 | `seaborn/_core/scales.py` |
| OCP-001 | OCP | `applied_passed` | - | 7.46 -> 7.23 | 0.0 -> 0.0 | `seaborn/categorical.py` |
| OCP-002 | OCP | `applied_passed` | - | 13.19 -> 11.53 | 0.0 -> 0.0 | `seaborn/distributions.py` |
| OCP-003 | OCP | `applied_passed` | - | 11.53 -> 11.2 | 0.0 -> 0.0 | `seaborn/distributions.py` |
| OCP-012 | OCP | `applied_passed` | - | 2.89 -> 2.89 | 23.52 -> 23.49 | `seaborn/_core/scales.py` |
| OCP-013 | OCP | `applied_passed` | - | 2.89 -> 2.79 | 23.49 -> 23.47 | `seaborn/_core/scales.py` |
| OCP-016 | OCP | `applied_passed` | - | 2.94 -> 2.89 | 23.32 -> 24.0 | `seaborn/_core/properties.py` |
| OCP-017 | OCP | `applied_passed` | - | 7.85 -> 7.46 | 0.0 -> 0.0 | `seaborn/categorical.py` |
| OCP-052 | OCP | `applied_passed` | - | 2.94 -> 2.94 | 23.93 -> 23.32 | `seaborn/_core/properties.py` |
| OCP-075 | OCP | `applied_passed` | - | 2.89 -> 2.89 | 24.0 -> 23.43 | `seaborn/_core/properties.py` |
| OCP-077 | OCP | `applied_passed` | - | 7.23 -> 7.23 | 0.0 -> 0.0 | `seaborn/categorical.py` |
| OCP-104 | OCP | `applied_passed` | - | 6.96 -> 7.0 | 0.0 -> 0.0 | `seaborn/categorical.py` |
| OCP-105 | OCP | `applied_passed` | - | 7.23 -> 6.96 | 0.0 -> 0.0 | `seaborn/categorical.py` |
| SRP-001 | SRP | `patch_failed` | - | - | - | `seaborn/categorical.py` |
| SRP-003 | SRP | `applied_failed` | 1036/1044 | - | - | `seaborn/categorical.py` |
| SRP-004 | SRP | `patch_failed` | - | - | - | `seaborn/distributions.py` |
| SRP-005 | SRP | `applied_failed` | 169/176 | - | - | `seaborn/matrix.py` |
| SRP-006 | SRP | `applied_failed` | 98/100 | - | - | `seaborn/_core/plot.py` |
| SRP-007 | SRP | `applied_failed` | 169/176 | - | - | `seaborn/regression.py` |
| SRP-008 | SRP | `applied_failed` | 784/792 | - | - | `seaborn/external/docscrape.py` |
| SRP-010 | SRP | `applied_failed` | 754/762 | - | - | `seaborn/_base.py` |
| SRP-011 | SRP | `applied_failed` | 748/756 | - | - | `seaborn/matrix.py` |
| SRP-018 | SRP | `applied_failed` | 815/823 | - | - | `seaborn/axisgrid.py` |
| SRP-019 | SRP | `applied_failed` | 169/176 | - | - | `seaborn/_core/plot.py` |
| SRP-021 | SRP | `patch_failed` | - | - | - | `seaborn/_base.py` |