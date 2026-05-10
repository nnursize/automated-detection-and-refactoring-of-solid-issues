# Refactor SRP-006 (SRP): Combines URL path construction with two distinct data encoding responsibiliti...

**Status:** `detection_rejected`  
**Branch:** `refactor/SRP-006` -> `main`  
**Head commit:** `178332b19159a5d45228c36e03126748061c76d5`  

## Detected issue

- **File**: `src/requests/models.py`
- **Entity**: `RequestEncodingMixin` (class)
- **Lines (at detection time)**: L50–L134
- **Severity**: medium
- **Confidence**: detected by 7 scan(s)

**Description.** Combines URL path construction with two distinct data encoding responsibilities (URL parameters and multipart files).

**Reasoning.** This mixin includes `path_url` (URL path construction), `_encode_params` (URL-encoded parameter serialization), and `_encode_files` (multipart/form-data serialization). While both `_encode_params` and `_encode_files` are about 'encoding', they handle fundamentally different data formats and involve distinct logic (simple key-value encoding vs. complex file handling, content-type inference, filename guessing). A change in URL parameter encoding would not affect multipart file encoding, and vice-versa, indicating separate responsibilities.

## Detection label

- **Label**: `false`

## Diff

*(no diff — patch was not applied)*
