# Prooflane v0.1 — Product Requirements Document (PRD)
>
> **Target repo path:** `prooflane-spec/spec/0.1-draft/PRD.md`  
> **Audience:** Spec editors, implementers, integrators (vendors/OSS), security & compliance reviewers  
> **License:** Spec text CC-BY-4.0; reference code Apache-2.0

## 1) Problem & Vision

Enterprise documents lose **portable provenance** once they leave their tenant (e.g., M365/ECM). Version history, approvals, policy, and search signals are siloed; AI answers lack verifiable, **commit-time** citations.  
**Prooflane (.pla)** is an **open ZIP-based container** that travels with:

1) a cryptographically verifiable **commit/lineage**,
2) explicit **workflow** state + append-only event log,
3) **governance-in-file** (classification, retention, legal hold), and
4) an **AI-ready search section** (chunk map + embeddings + commit citations).

**Goal:** Do for **truth** what PDF did for **layout**—a neutral, vendor-agnostic standard.

## 2) Success Criteria (v0.1 Draft)

- **Interoperability:** Two independent implementations produce/consume the same `.pla`; verification & basic search results match.
- **Verifiability:** A public verifier validates **manifest**, **commit chain**, **workflow log**, and (when present) **signatures & timestamps**.
- **AI-readiness:** Retrieval engines index chunks/embeddings and return stable citations `(doc_id, commit_id, chunk_id, start_offset, end_offset)`.
- **Portability:** Evidence bundles exportable to **ASiC-E** or **PDF/A-3** verify offline.
- **Spec quality:** MUST/SHOULD/MAY used correctly; conformance classes and fixtures exist; validator CI is green.

## 3) Non-Goals (v0.1)

- Not a word-processing format (OOXML/ODF remain sources/renditions).
- No mandatory blockchain; timestamp **anchors** optional.
- No DRM/TEE; encryption/policy portability deferred to v0.2.
- No CRDT/collab transport (Studio/editor separate).

## 4) Personas

- **Implementer:** SDKs/viewers/servers; needs schemas, canonicalization, examples, tests.
- **Security/Compliance:** signature profiles, timestamp anchors, evidence export, threat model.
- **Search/AI Engineer:** deterministic chunk/embedding layout + commit-linked citations.
- **Records/Legal:** governance-in-file, long-term verification & export.

## 5) Scope & Requirements

### 5.1 Container & Naming

- **Extension:** `.pla`  
- **Media type (proposed):** `application/vnd.prooflane+zip`  
- **Packaging:** ZIP; root **MUST** include `manifest.json` with `"format": "PROOFLANE"`.
- **Path rules:** UTF-8; forward slashes; case-sensitive; no `..` traversal; max path length 255.

### 5.2 Manifest (normative)

`/manifest.json` **MUST** include:

```json
{
  "format": "PROOFLANE",
  "spec_version": "0.1",
  "title": "…",
  "created": "RFC3339/ISO-8601",
  "doc_id": "pla:…",
  "latest_commit": "pla:… or hash",
  "commits": ["history/0001.json", "history/0002.json"],
  "workflow": {"state":"workflow/state.json","log":"workflow/log.jsonl"},
  "search": {"chunks":"search/chunks.jsonl","embeddings":"search/embeddings.bin","meta":"search/metadata.json"},
  "security": {"trustchain":"security/trustchain.json","policies":"security/policies.json"}
}
```

- Forward-compatibility: unknown fields **MAY** be ignored unless a future spec marks them required.

### 5.3 History (Commit Objects)

- Location: `history/NNNN.json` (zero-padded).  
- Each commit **MUST** include: `parent|null`, `timestamp`, `author{name,email}`, `purpose`, `delta {added[], changed[], removed[]}`, `commit_id`.  
- `signatures[]` **MAY** be present (see 5.6). `anchors[]` **MAY** contain timestamp tokens.  
- **Canonicalization:** JSON Canonicalization Scheme (JCS) for signature inputs (normative reference).

### 5.4 Workflow

- `workflow/state.json` **MUST** define `version`, `states[]`, `initial_state`, `current_state`, `transitions[] {from,to,action,guard?}`.  
- `workflow/log.jsonl` **MUST** append events `{ts, actor, action, meta?}`; entries **MUST NOT** be rewritten.

### 5.5 Canonical View

- `canonical/index.html` **MUST** exist; deterministic rendering (no network fetches).  
- Accessibility baseline: headings, alt text, language tag.  
- **Anchors:** Viewer **SHOULD** expose deep-links to `commit_id` and `chunk_id`.

### 5.6 Security (Signatures, Timestamps, Trust)

- `security/trustchain.json` lists signers/roots; `security/policies.json` records classification/retention/legal hold.  
- **Baseline signature profile (v0.1):** **Ed25519 + COSE_Sign1** over JCS-canonicalized commit object.  
- **Timestamp anchors (optional):** RFC-3161 tokens or Roughtime proofs in `anchors[]`.  
- **Bridges (informative v0.1):** Profiles for **PAdES**/**ASiC-E** evidence export; normative by v0.2.

### 5.7 AI / Search Section (Deterministic)

- `search/chunks.jsonl`: JSONL records with `chunk_id`, `text_hash` (SHA-256 of normalized text), `text_len`, `role`, `page_hint?`, `offset_hint?`.  
- **Normalization:** UTF-8 → Unicode **NFKC** → collapse whitespace → strip control chars (spec MUST define exact steps).  
- `search/embeddings.bin`: row‑major **float32** (v0.1) or **float16** (optional), little‑endian; length = `N * dim` from `metadata.json`.  
- `search/metadata.json`: `{"encoder": "string", "dim": int, "created":"ts", "align":"none|…", "notes?":"…"}`.  
- Search engines **MUST** return citations `(doc_id, commit_id, chunk_id, start_offset, end_offset)`.

### 5.8 Interoperability (Informative v0.1)

- **W3C PROV JSON‑LD**: normative context + mapping of commits/workflow to `Entity/Activity/Agent`.  
- **C2PA**: allow embedding assertion stores for media referenced in canonical HTML.  
- **OPC/OOXML / ODF / PDF/A‑3**: how to embed/reference sources or renditions while preserving lineage links.  
- **OpenTDF Policy**: optional mapping for portable access attributes in `policies.json`.

### 5.9 Conformance Classes

| Class | Mandatory files | Signatures | Governance | AI/Search | Intended implementers |
|---|---|---:|---:|---:|---|
| **PLA-Core** | manifest, history, workflow, canonical | optional | optional | optional | basic readers/viewers |
| **PLA-Sign** | + signature profile | **required** | optional | optional | regulated sign/verify |
| **PLA-Govern** | + `policies.json` retention/holds | optional | **required** | optional | records/legal |
| **PLA-RAG** | + chunks/embeddings/meta | optional | optional | **required** | search/AI engines |
| **PLA-Full** | all of the above | **required** | **required** | **required** | end‑to‑end systems |

Implementations **MUST** declare the highest class they fully support.

## 6) Deliverables (v0.1)

1. **Spec text** (`spec/0.1-draft/spec.md`) with normative algorithms & examples.  
2. **Schemas** (`spec/0.1-draft/schemas/*.json`) for manifest, commit, workflow, chunk, search metadata.  
3. **Validator CLI** (OSS) + CI action: loads `.pla`, validates schemas & presence, optional signature checks.  
4. **Fixtures** (`spec/0.1-draft/examples/**`): minimal PLA‑Core, PLA‑RAG, PLA‑Sign.  
5. **Neutral Viewer** (public): renders canonical view; badges for verification/workflow; deep‑links to commits/chunks.  
6. **Conformance suite**: tests mapped to MUST/SHOULD; badge matrix per implementation.  
7. **Interoperability appendix**: PROV JSON‑LD, PAdES/ASiC guidance, C2PA note.

## 7) Acceptance Tests (excerpt)

- **AT‑001 (manifest):** Missing required keys → validator fails with clear error.  
- **AT‑010 (history chain):** Broken parent pointer → verification fails.  
- **AT‑020 (workflow immutability):** Removing a prior event → verification detects mismatch.  
- **AT‑030 (signatures):** Commit modified post‑signature → signature verification fails.  
- **AT‑040 (timestamp anchor):** RFC‑3161 token invalid → verification fails with reason.  
- **AT‑050 (AI index):** `dim` mismatch vs `embeddings.bin` length → validator fails.  
- **AT‑060 (citations):** Search engine returns unknown chunk_id → conformance test fails.  
- **AT‑070 (a11y):** Viewer Lighthouse/aXe baseline rules pass on canonical HTML.  
- **AT‑080 (evidence export):** ASiC bundle contains manifest, commits, signatures, timestamps, verifier HTML; offline verify passes.

## 8) Governance & Versioning

- **Spec versioning:** SemVer-like; backward-compatible minor bumps add optional fields; breaking changes in major versions with migration notes.  
- **Licensing:** Spec CC‑BY‑4.0; schemas & reference code Apache‑2.0.  
- **Change control:** Public issues; proposals via RFCs in `/rfcs/` with design, security review, conformance impact.

## 9) Security & Privacy

- **Threats:** tampering, truncated archives, path traversal, downgrade attacks, signature replay, timestamp spoofing.  
- **Mitigations:** JCS canonicalization; deny `..` paths; require explicit covered fields for signatures; multi‑anchor option.  
- **PII:** minimize personal data in logs; prefer pseudonymous actor IDs with out‑of‑band directory mapping.  
- **Telemetry:** none in spec artifacts.

## 10) Performance & Size

- **Targets (guidance):** PLA‑Core < 50 MB typical; PLA‑RAG embeddings **SHOULD** use float16 when acceptable.  
- Viewer initial render < 1s for 10k‑char docs on modern laptops.  
- Conformance files kept < 10 MB.

## 11) Milestones & Timeline (proposal)

- **M0 (Spec outline + schemas)** — Done (scaffold exists).  
- **M1 (Validator alpha + fixtures)** — *T+4 weeks*: publish CLI, 3 fixtures, CI green.  
- **M2 (Interoperability appendix)** — *T+8 weeks*: PROV JSON‑LD, PAdES/ASiC guidance, C2PA note.  
- **M3 (Conformance + Viewer v1)** — *T+12 weeks*: badges, public demo.  
- **v0.1 Draft Freeze** — *T+14 weeks*; **RC** — *T+16 weeks*; **v0.1** — *T+20 weeks*.

## 12) Open Questions

- Make float16 the default for embeddings?  
- Fix a single hash algo (SHA‑256) or allow a registry?  
- IANA media type registration details.  
- Policy profile interop (OpenTDF) moves to normative in v0.2?

## 13) File Layout (illustrative)

```
/manifest.json
/history/0001.json
/history/0002.json
/workflow/state.json
/workflow/log.jsonl
/search/chunks.jsonl
/search/embeddings.bin
/search/metadata.json
/security/trustchain.json
/security/policies.json
/canonical/index.html
/attachments/**            (optional sources, renditions, evidence)
/evidence/**               (optional ASiC/PAdES/PDF-A-3 bundles)
/prov/prov.jsonld          (optional W3C PROV view)
```
