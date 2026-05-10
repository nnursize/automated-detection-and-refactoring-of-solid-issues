# Refactor DIP-026 (DIP): Direct call to `pyopenssl.inject_into_urllib3()` for SNI support.

**Status:** `obsolete`  
**Branch:** `refactor/DIP-026` -> `main`  
**Head commit:** `234d6a661d2a0df2a426b39622a2ae205c2d6868`  

## Detected issue

- **File**: `src/requests/__init__.py`
- **Entity**: `Global Scope` (module)
- **Lines (at detection time)**: L67–L72
- **Severity**: high
- **Confidence**: detected by 1 scan(s)

**Description.** Direct call to `pyopenssl.inject_into_urllib3()` for SNI support.

**Reasoning.** The `__init__.py` file, a high-level entry point for package initialization, directly calls `pyopenssl.inject_into_urllib3()`. This hardcodes a specific, low-level integration detail of how `pyopenssl` enhances `urllib3` for SNI support, rather than depending on an abstraction for SSL context management or allowing for alternative SNI implementations.

## Obsolete

entity `Global Scope` not found in current source of `src/requests/__init__.py` — likely renamed/removed by an earlier refactor

## Diff

*(no diff — patch was not applied)*
