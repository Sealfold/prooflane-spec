# Conformance Suite (v0.1 Draft)

Mapped acceptance tests with MUST/SHOULD coverage and expected validator outcomes.

- AT-001: Missing required manifest keys → FAIL (`ERR_MANIFEST_MISSING_REQUIRED`)
- AT-010: Broken parent pointer → FAIL (`ERR_COMMIT_PARENT_INVALID`)
- AT-020: Workflow log tampered → FAIL (`ERR_WORKFLOW_EVENT_TYPE_INVALID` or tamper detection id)
- AT-030: Signature mismatch (PLA-Sign) → FAIL (`ERR_COMMIT_SIGNATURE_VALUE_INVALID`)
- AT-040: Timestamp anchor invalid → FAIL (`ERR_COMMIT_ANCHOR_TOKEN_INVALID`)
- AT-050: Embedding dim mismatch vs file length → FAIL (`ERR_SEARCH_META_DIM_INVALID`)
- AT-060: Unknown `chunk_id` in citation → FAIL (`ERR_CHUNK_ID_INVALID`)
- AT-070: Canonical HTML a11y baseline checks → WARN (non-blocking)
- AT-080: ASiC evidence export offline verify → PASS
