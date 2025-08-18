# Evidence Export (Informative v0.1)

- ASiC-E: Bundle manifest, commit chain, signatures, timestamp tokens, and a verifier HTML. Include minimal metadata for offline verification.
- PAdES: Embed Prooflane evidence as a PDF/A-3 attachment; reference commit IDs and timestamp anchors in document-level metadata.
- PDF/A-3: Store .pla as an embedded file with associated relationship; provide a human-readable summary in the canonical view.

Security note: Signature verification MUST cover explicit fields under JCS canonicalization.
