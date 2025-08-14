# Prooflane v0.1 Conformance Test Suite

This directory contains the comprehensive conformance test suite for Prooflane v0.1, covering all acceptance tests (AT-001 through AT-080) defined in the PRD.

## Test Categories

### 1. Schema Validation Tests
- **AT-001**: Manifest validation
- **AT-002**: Commit schema validation
- **AT-003**: Workflow state validation
- **AT-004**: Workflow log validation
- **AT-005**: Search metadata validation
- **AT-006**: Chunk schema validation

### 2. File Structure Tests
- **AT-007**: Required file presence
- **AT-008**: File path validation
- **AT-009**: Directory structure validation
- **AT-010**: Commit chain validation

### 3. Workflow Tests
- **AT-020**: Workflow immutability
- **AT-021**: State transition validation
- **AT-022**: Event log integrity
- **AT-023**: Actor attribution

### 4. Security Tests
- **AT-030**: Signature verification
- **AT-031**: Timestamp anchor validation
- **AT-032**: Trust chain validation
- **AT-033**: Policy enforcement

### 5. AI/Search Tests
- **AT-050**: Embedding dimension validation
- **AT-051**: Chunk reference integrity
- **AT-052**: Search metadata consistency
- **AT-053**: Citation generation

### 6. Accessibility Tests
- **AT-070**: HTML validation
- **AT-071**: Accessibility compliance
- **AT-072**: Deep linking functionality
- **AT-073**: Keyboard navigation

### 7. Performance Tests
- **AT-080**: File size validation
- **AT-081**: Render performance
- **AT-082**: Validation speed
- **AT-083**: Search indexing performance

## Test Implementation

### Test Runner
```bash
# Run all tests
python -m pytest tests/

# Run specific test category
python -m pytest tests/test_schema.py

# Run specific test
python -m pytest tests/test_schema.py::test_manifest_validation

# Generate coverage report
python -m pytest --cov=prooflane --cov-report=html
```

### Test Structure
```
tests/
├── conftest.py              # Test configuration and fixtures
├── test_schema.py           # Schema validation tests
├── test_structure.py        # File structure tests
├── test_workflow.py         # Workflow validation tests
├── test_security.py         # Security and signature tests
├── test_search.py           # AI/search functionality tests
├── test_accessibility.py    # Accessibility compliance tests
├── test_performance.py      # Performance benchmark tests
└── fixtures/                # Test data and fixtures
    ├── valid/               # Valid Prooflane examples
    ├── invalid/             # Invalid examples for negative testing
    └── edge_cases/          # Edge case examples
```

## Conformance Classes

### PLA-Core Tests
- Basic manifest validation
- Required file presence
- Simple workflow validation
- Canonical HTML rendering

### PLA-Sign Tests
- Digital signature verification
- Timestamp anchor validation
- Trust chain validation
- Cryptographic integrity

### PLA-Govern Tests
- Policy enforcement
- Retention rule validation
- Legal hold compliance
- Access control validation

### PLA-RAG Tests
- Chunk indexing validation
- Embedding consistency
- Search metadata validation
- Citation generation

### PLA-Full Tests
- End-to-end validation
- Cross-feature integration
- Performance benchmarks
- Security compliance

## Test Results

### Pass/Fail Criteria
- **PASS**: All tests pass, implementation conforms to spec
- **FAIL**: One or more tests fail, implementation needs fixes
- **PARTIAL**: Some tests pass, partial conformance achieved

### Badge System
- **PLA-Core Badge**: Basic conformance achieved
- **PLA-Sign Badge**: Signature verification working
- **PLA-Govern Badge**: Governance features working
- **PLA-RAG Badge**: AI/search features working
- **PLA-Full Badge**: Complete conformance achieved

## Continuous Integration

### GitHub Actions
- Automated testing on all commits
- Conformance badge generation
- Performance regression detection
- Security vulnerability scanning

### Test Reports
- HTML coverage reports
- Performance benchmarks
- Security audit results
- Conformance matrix

## Contributing

### Adding New Tests
1. Create test file in appropriate category
2. Follow naming convention: `test_<feature>_<scenario>`
3. Include comprehensive assertions
4. Add to appropriate conformance class
5. Update documentation

### Test Data
- Use realistic examples
- Include edge cases
- Maintain test data quality
- Version control all fixtures

## Performance Benchmarks

### Target Metrics
- **File Creation**: < 100ms for 1MB documents
- **Validation**: < 50ms for basic checks
- **Search Indexing**: < 500ms for 10k chunks
- **Viewer Render**: < 1s for 10k-char docs

### Benchmark Suite
- Automated performance testing
- Regression detection
- Resource usage monitoring
- Scalability testing
