# Refactor SRP-021 (SRP): Configures SSL certificate verification settings on a urllib3 connection, inc...

**Status:** `detection_rejected`  
**Branch:** `refactor/SRP-021` -> `main`  
**Head commit:** `178332b19159a5d45228c36e03126748061c76d5`  

## Detected issue

- **File**: `src/requests/adapters.py`
- **Entity**: `HTTPAdapter.cert_verify` (method)
- **Lines (at detection time)**: L158–L204
- **Severity**: high
- **Confidence**: detected by 5 scan(s)

**Description.** Configures SSL certificate verification settings on a urllib3 connection, including CA bundles, client certificates, and path validation.

**Reasoning.** This method has multiple responsibilities related to SSL certificate configuration: 1) Determining the CA certificate bundle location (from `verify` or `DEFAULT_CA_BUNDLE_PATH`, including handling zipped paths). 2) Setting the `cert_reqs` on the connection (required or none). 3) Setting `ca_certs` or `ca_cert_dir`. 4) Configuring client certificates (`cert_file`, `key_file`). 5) Validating the existence of all specified certificate files. These are distinct aspects of TLS configuration and validation.

## Detection label

- **Label**: `false`

## Diff

*(no diff — patch was not applied)*
