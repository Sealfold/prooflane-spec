# Prooflane Specification v0.1 (Draft)

## 1. Introduction

This document defines the Prooflane (.pla) format, an open ZIP-based container for portable document provenance. Prooflane preserves cryptographic verification, workflow state, governance policies, and AI-ready search capabilities across system boundaries.

### 1.1 Scope

This specification covers:
- Container format and file structure
- Manifest schema and validation rules
- Commit chain and history management
- Workflow state and event logging
- Search indexing and embedding storage
- Security and signature profiles
- Conformance classes and requirements

### 1.2 Conformance Classes

| Class | Mandatory Files | Signatures | Governance | AI/Search | Use Case |
|-------|----------------|------------|------------|-----------|----------|
| **PLA-Core** | manifest, history, workflow, canonical | optional | optional | optional | Basic readers/viewers |
| **PLA-Sign** | + signature profile | **required** | optional | optional | Regulated sign/verify |
| **PLA-Govern** | + policies.json | optional | **required** | optional | Records/legal |
| **PLA-RAG** | + chunks/embeddings/meta | optional | optional | **required** | Search/AI engines |
| **PLA-Full** | all of the above | **required** | **required** | **required** | End-to-end systems |

## 2. Container Format

### 2.1 File Extension and Media Type

- **Extension**: `.pla`
- **Media Type**: `application/vnd.prooflane+zip` (proposed)
- **Packaging**: ZIP archive with UTF-8 encoding

### 2.2 Path Rules

- **Encoding**: UTF-8
- **Separators**: Forward slashes (`/`)
- **Case Sensitivity**: Yes
- **Traversal**: No `..` allowed
- **Max Length**: 255 characters per path component

### 2.3 Required Root Structure

```
/
├── manifest.json              # MUST exist
├── history/                   # MUST exist
├── workflow/                  # MUST exist
├── canonical/                 # MUST exist
├── search/                    # Optional (PLA-RAG+)
└── security/                  # Optional (PLA-Sign+)
```

## 3. Manifest Schema

### 3.1 Required Fields

The `manifest.json` file MUST contain:

```json
{
  "format": "PROOFLANE",
  "spec_version": "0.1",
  "title": "string",
  "created": "RFC3339/ISO-8601",
  "doc_id": "pla:...",
  "latest_commit": "pla:... or hash",
  "commits": ["history/0001.json", "history/0002.json"],
  "workflow": {
    "state": "workflow/state.json",
    "log": "workflow/log.jsonl"
  },
  "search": {
    "chunks": "search/chunks.jsonl",
    "embeddings": "search/embeddings.bin",
    "meta": "search/metadata.json"
  },
  "security": {
    "trustchain": "security/trustchain.json",
    "policies": "security/policies.json"
  }
}
```

### 3.2 Field Descriptions

- **format**: MUST be "PROOFLANE"
- **spec_version**: MUST match this specification version
- **title**: Human-readable document title
- **created**: ISO-8601 timestamp of creation
- **doc_id**: Unique identifier in `pla:` namespace
- **latest_commit**: Reference to most recent commit
- **commits**: Array of commit file paths
- **workflow**: Paths to workflow state and log files
- **search**: Paths to search index files (optional)
- **security**: Paths to security files (optional)

## 4. Commit Chain

### 4.1 Commit File Naming

Commits are stored in `history/NNNN.json` format:
- **Location**: `history/` directory
- **Format**: Zero-padded 4-digit sequence
- **Extension**: `.json`

### 4.2 Commit Schema

Each commit MUST contain:

```json
{
  "parent": "pla:... or null",
  "timestamp": "RFC3339/ISO-8601",
  "author": {
    "name": "string",
    "email": "string"
  },
  "purpose": "string",
  "delta": {
    "added": ["path1", "path2"],
    "changed": ["path1", "path2"],
    "removed": ["path1", "path2"]
  },
  "commit_id": "pla:...",
  "signatures": [],
  "anchors": []
}
```

### 4.3 Commit Validation Rules

- **Parent Chain**: MUST form valid chain back to root
- **Timestamps**: MUST be monotonically increasing
- **Delta**: MUST accurately reflect file changes
- **Signatures**: MAY be present for verification
- **Anchors**: MAY contain timestamp tokens

## 5. Workflow Management

### 5.1 Workflow State

`workflow/state.json` MUST define:

```json
{
  "version": "string",
  "states": ["draft", "review", "approved", "archived"],
  "initial_state": "draft",
  "current_state": "review",
  "transitions": [
    {
      "from": "draft",
      "to": "review",
      "action": "submit_for_review",
      "guard": "has_content"
    }
  ]
}
```

### 5.2 Workflow Log

`workflow/log.jsonl` MUST contain append-only events:

```json
{"ts": "2025-01-13T10:00:00Z", "actor": "user@example.com", "action": "submit_for_review", "meta": {"comment": "Ready for review"}}
{"ts": "2025-01-13T11:00:00Z", "actor": "reviewer@example.com", "action": "approve", "meta": {"comment": "Looks good"}}
```

### 5.3 Workflow Rules

- **Immutability**: Log entries MUST NOT be modified
- **State Transitions**: MUST follow defined transition rules
- **Actor Tracking**: All actions MUST be attributed

## 6. Search and AI Indexing

### 6.1 Chunk Schema

`search/chunks.jsonl` contains text chunks:

```json
{"chunk_id": "chunk_001", "text_hash": "sha256:...", "text_len": 150, "role": "body", "page_hint": 1, "offset_hint": 0}
{"chunk_id": "chunk_002", "text_hash": "sha256:...", "text_len": 200, "role": "body", "page_hint": 1, "offset_hint": 150}
```

### 6.2 Embedding Storage

`search/embeddings.bin` contains:
- **Format**: Row-major float32 or float16
- **Endianness**: Little-endian
- **Dimensions**: Defined in metadata.json

### 6.3 Search Metadata

`search/metadata.json` defines:

```json
{
  "encoder": "text-embedding-ada-002",
  "dim": 1536,
  "created": "2025-01-13T10:00:00Z",
  "align": "none",
  "notes": "Generated using OpenAI embeddings"
}
```

## 7. Security and Signatures

### 7.1 Signature Profile

Baseline signature profile (v0.1):
- **Algorithm**: Ed25519
- **Format**: COSE_Sign1
- **Canonicalization**: JSON Canonicalization Scheme (JCS)

### 7.2 Trust Chain

`security/trustchain.json` lists:

```json
{
  "signers": [
    {
      "id": "user@example.com",
      "public_key": "ed25519:...",
      "role": "author"
    }
  ],
  "roots": ["certificate_authority_1"]
}
```

### 7.3 Governance Policies

`security/policies.json` contains:

```json
{
  "classification": "internal",
  "retention": "7_years",
  "legal_hold": false,
  "access_control": ["group:legal", "group:compliance"]
}
```

## 8. Canonical View

### 8.1 HTML Requirements

`canonical/index.html` MUST:
- Exist and be accessible
- Render deterministically (no network fetches)
- Include proper accessibility markup
- Support deep-linking to commits and chunks

### 8.2 Accessibility Baseline

- **Headings**: Proper heading hierarchy
- **Alt Text**: Descriptive alt text for images
- **Language**: Proper language tag
- **Navigation**: Keyboard navigation support

## 9. Validation Rules

### 9.1 Schema Validation

All JSON files MUST:
- Parse as valid JSON
- Conform to defined schemas
- Pass schema validation tests

### 9.2 File Presence Validation

Required files MUST exist:
- `manifest.json` at root
- All referenced commit files
- All referenced workflow files
- All referenced canonical files

### 9.3 Cross-Reference Validation

- Commit parent references MUST be valid
- File path references MUST exist
- Workflow state transitions MUST be valid

## 10. Conformance Testing

### 10.1 Test Categories

- **Schema Tests**: Validate all JSON schemas
- **File Tests**: Verify file presence and structure
- **Logic Tests**: Validate business rules
- **Performance Tests**: Verify size and speed requirements

### 10.2 Test Implementation

Tests MUST:
- Cover all MUST/SHOULD requirements
- Provide clear error messages
- Support automated execution
- Generate conformance reports

## 11. Interoperability

### 11.1 W3C PROV Integration

Prooflane commits map to PROV entities:
- **Commit** → **Entity**
- **Author** → **Agent**
- **Workflow Action** → **Activity**

### 11.2 Evidence Export

Support for:
- **ASiC-E**: Advanced Electronic Signatures
- **PDF/A-3**: PDF for long-term preservation
- **PAdES**: PDF Advanced Electronic Signatures

### 11.3 C2PA Integration

Allow embedding C2PA assertion stores for media referenced in canonical HTML.

## 12. Performance Requirements

### 12.1 Size Targets

- **PLA-Core**: < 50 MB typical
- **PLA-RAG**: Embeddings SHOULD use float16 when acceptable
- **Conformance Files**: < 10 MB

### 12.2 Speed Targets

- **Viewer Render**: < 1s for 10k-char docs
- **Validation**: < 50ms for basic checks
- **Search Indexing**: < 500ms for 10k chunks

## 13. Security Considerations

### 13.1 Threat Model

- **Tampering**: Prevented by cryptographic signatures
- **Path Traversal**: Blocked by path validation rules
- **Downgrade Attacks**: Prevented by version checking
- **Timestamp Spoofing**: Mitigated by multiple anchors

### 13.2 Mitigation Strategies

- **JCS Canonicalization**: Ensures signature consistency
- **Path Validation**: Prevents traversal attacks
- **Multi-Anchor Support**: Reduces timestamp risks
- **Explicit Field Coverage**: Prevents signature bypass

## 14. Implementation Notes

### 14.1 Reference Implementations

- **Python**: Primary reference implementation
- **JavaScript**: Web and Node.js support
- **Go**: High-performance implementation

### 14.2 Development Tools

- **Validator CLI**: Command-line validation tool
- **Schema Tools**: JSON Schema validation utilities
- **Test Framework**: Conformance testing suite

### 14.3 Deployment

- **Package Managers**: NPM, PyPI, Go modules
- **Container Images**: Docker support
- **CI/CD**: GitHub Actions integration

## 15. Versioning and Evolution

### 15.1 Version Strategy

- **SemVer-like**: Major.Minor.Patch
- **Backward Compatibility**: Minor versions add optional fields
- **Breaking Changes**: Major versions with migration notes

### 15.2 Migration Support

- **Automated Tools**: Migration scripts and utilities
- **Documentation**: Comprehensive migration guides
- **Validation**: Migration validation tests

---

**Note**: This is a draft specification. Final version will include additional examples, edge cases, and implementation details based on community feedback and testing.
