# Refactor DIP-007 (DIP): Utility module directly depends on a concrete function for CA bundle path.

**Status:** `obsolete`  
**Branch:** `refactor/DIP-007` -> `main`  
**Head commit:** `50680975f2e17f7195f470273598150ace470740`  

## Detected issue

- **File**: `src/requests/utils.py`
- **Entity**: `DEFAULT_CA_BUNDLE_PATH` (class)
- **Lines (at detection time)**: L30–L30
- **Severity**: low
- **Confidence**: detected by 3 scan(s)

**Description.** Utility module directly depends on a concrete function for CA bundle path.

**Reasoning.** The `DEFAULT_CA_BUNDLE_PATH` in `requests.utils` directly calls `certs.where()`. While `certs.where()` is a simple function returning a path (effectively a configuration value), it's a direct dependency on a concrete implementation. In a strict interpretation of DIP, even configuration lookups could be abstracted. However, given that `certs.where()` is a stable, low-level utility function providing a path, the impact of this direct dependency is minimal, and it's more akin to a constant lookup than a service dependency.

## Obsolete

entity `DEFAULT_CA_BUNDLE_PATH` not found in current source of `src/requests/utils.py` — likely renamed/removed by an earlier refactor

## Diff

*(no diff — patch was not applied)*
