# Refactor SRP-008 (SRP): Handles JSON serialization, streamed body management, multipart file encoding...

**Status:** `detection_rejected`  
**Branch:** `refactor/SRP-008` -> `main`  
**Head commit:** `178332b19159a5d45228c36e03126748061c76d5`  

## Detected issue

- **File**: `src/requests/models.py`
- **Entity**: `PreparedRequest.prepare_body` (method)
- **Lines (at detection time)**: L320–L378
- **Severity**: high
- **Confidence**: detected by 5 scan(s)

**Description.** Handles JSON serialization, streamed body management, multipart file encoding, URL-encoded data, and Content-Type inference.

**Reasoning.** This method is a 'god method' for preparing the request body. It has too many reasons to change: 1) Changes in JSON serialization (e.g., `complexjson.dumps` behavior, error handling). 2) Changes in streamed body handling (e.g., `super_len`, `body.tell()`, `Content-Length`/`Transfer-Encoding` logic). 3) Changes in multipart file encoding (delegating to `_encode_files`). 4) Changes in URL-encoded data handling (delegating to `_encode_params`). 5) Changes in how `Content-Type` is inferred and set. Each of these is a distinct responsibility that could evolve independently.

## Detection label

- **Label**: `false`

## Diff

*(no diff — patch was not applied)*
