# Prooflane v0.1 Example Fixtures

This directory contains example Prooflane (.pla) files demonstrating all conformance classes defined in the specification.

## Conformance Classes

### PLA-Core (Basic)
- **Purpose**: Basic readers/viewers
- **Required**: manifest, history, workflow, canonical
- **Optional**: signatures, governance, AI/search

### PLA-Sign (Signed)
- **Purpose**: Regulated sign/verify workflows
- **Required**: PLA-Core + signature profile
- **Use Case**: Legal documents, compliance requirements

### PLA-Govern (Governance)
- **Purpose**: Records management and legal hold
- **Required**: PLA-Core + policies.json
- **Use Case**: Corporate records, legal compliance

### PLA-RAG (AI/Search)
- **Purpose**: Search engines and AI systems
- **Required**: PLA-Core + chunks/embeddings/meta
- **Use Case**: RAG systems, semantic search

### PLA-Full (Complete)
- **Purpose**: End-to-end systems
- **Required**: All features (signatures, governance, AI/search)
- **Use Case**: Enterprise document management

## Example Structure

```
examples/
├── README.md                    # This file
├── minimal/                     # PLA-Core example
│   ├── manifest.json
│   ├── history/
│   ├── workflow/
│   └── canonical/
├── signed/                      # PLA-Sign example
│   ├── manifest.json
│   ├── history/
│   ├── workflow/
│   ├── canonical/
│   └── security/
├── governance/                  # PLA-Govern example
│   ├── manifest.json
│   ├── history/
│   ├── workflow/
│   ├── canonical/
│   └── security/
├── rag/                        # PLA-RAG example
│   ├── manifest.json
│   ├── history/
│   ├── workflow/
│   ├── canonical/
│   └── search/
└── full/                       # PLA-Full example
    ├── manifest.json
    ├── history/
    ├── workflow/
    ├── canonical/
    ├── search/
    └── security/
```

## Testing

Each example can be validated using the Prooflane validator:

```bash
# Validate all examples
python scripts/validate.py

# Validate specific example
python scripts/validate.py examples/minimal/
```

## Validation Rules

- All examples MUST pass schema validation
- All examples MUST have valid file references
- All examples MUST demonstrate proper structure
- All examples MUST be under 10MB for conformance testing
