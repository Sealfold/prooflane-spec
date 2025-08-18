#!/usr/bin/env python3
"""
Prooflane v0.1 Validator CLI

Validates Prooflane (.pla) files against the specification.
Supports both individual files and complete .pla containers.

Usage:
    python validate.py <path>
    python validate.py --help
    python validate.py --version
"""

import argparse
import json
import pathlib
import sys
import zipfile
from typing import Dict, List, Tuple, Optional
from jsonschema import validate, Draft202012Validator, ValidationError
import hashlib
import time
from datetime import datetime

class ProoflaneValidator:
    """Validates Prooflane files against the specification."""
    
    def __init__(self, spec_root: pathlib.Path):
        self.spec_root = spec_root
        self.schemas = self._load_schemas()
        self.errors = []
        self.warnings = []
        self.start_time = time.time()
        
    def _load_schemas(self) -> Dict[str, dict]:
        """Load all JSON schemas from the spec directory."""
        schemas = {}
        schema_dir = self.spec_root / 'schemas'
        
        for schema_file in schema_dir.glob('*.json'):
            try:
                with open(schema_file, 'r', encoding='utf-8') as f:
                    schemas[schema_file.stem] = json.load(f)
            except Exception as e:
                self.errors.append(f"Failed to load schema {schema_file}: {e}")
                
        return schemas
    
    def validate_pla_file(self, pla_path: pathlib.Path) -> bool:
        """Validate a complete .pla file (ZIP container)."""
        if not pla_path.exists():
            self.errors.append(f"File not found: {pla_path}")
            return False
            
        if not zipfile.is_zipfile(pla_path):
            self.errors.append(f"Not a valid ZIP file: {pla_path}")
            return False
            
        try:
            with zipfile.ZipFile(pla_path, 'r') as zip_file:
                return self._validate_pla_contents(zip_file)
        except Exception as e:
            self.errors.append(f"Failed to read ZIP file: {e}")
            return False
    
    def _validate_pla_contents(self, zip_file: zipfile.ZipFile) -> bool:
        """Validate the contents of a .pla ZIP file."""
        # Check for required files
        file_list = zip_file.namelist()
        
        # Validate manifest.json
        if 'manifest.json' not in file_list:
            self.errors.append("Missing required file: manifest.json")
            return False
            
        try:
            with zip_file.open('manifest.json') as f:
                manifest = json.load(f)
        except Exception as e:
            self.errors.append(f"Failed to parse manifest.json: {e}")
            return False
            
        # Validate manifest schema
        if not self._validate_manifest(manifest):
            return False
            
        # Validate all referenced files exist
        if not self._validate_file_references(zip_file, manifest):
            return False
            
        # Validate individual files
        if not self._validate_all_files(zip_file, manifest):
            return False
            
        return True
    
    def _validate_manifest(self, manifest: dict) -> bool:
        """Validate the manifest against its schema."""
        try:
            validate(manifest, self.schemas['manifest.schema'])
        except ValidationError as e:
            self.errors.append(f"Manifest validation failed: {e.message}")
            return False
            
        # Check required fields
        required_fields = ['format', 'spec_version', 'title', 'created', 'doc_id', 'latest_commit', 'commits', 'workflow']
        for field in required_fields:
            if field not in manifest:
                self.errors.append(f"Missing required manifest field: {field}")
                return False
                
        # Validate format
        if manifest.get('format') != 'PROOFLANE':
            self.errors.append("Invalid format: must be 'PROOFLANE'")
            return False
            
        # Validate spec version
        if manifest.get('spec_version') != '0.1':
            self.errors.append("Invalid spec version: must be '0.1'")
            return False
            
        return True
    
    def _validate_file_references(self, zip_file: zipfile.ZipFile, manifest: dict) -> bool:
        """Validate that all referenced files exist in the ZIP."""
        file_list = zip_file.namelist()
        
        # Check commit files
        for commit_path in manifest.get('commits', []):
            if commit_path not in file_list:
                self.errors.append(f"Referenced commit file not found: {commit_path}")
                return False
                
        # Check workflow files
        workflow = manifest.get('workflow', {})
        for workflow_file in [workflow.get('state'), workflow.get('log')]:
            if workflow_file and workflow_file not in file_list:
                self.errors.append(f"Referenced workflow file not found: {workflow_file}")
                return False
                
        # Check search files (optional)
        search = manifest.get('search', {})
        if search:
            for search_file in [search.get('chunks'), search.get('embeddings'), search.get('meta')]:
                if search_file and search_file not in file_list:
                    self.errors.append(f"Referenced search file not found: {search_file}")
                    return False
                    
        # Check security files (optional)
        security = manifest.get('security', {})
        if security:
            for security_file in [security.get('trustchain'), security.get('policies')]:
                if security_file and security_file not in file_list:
                    self.errors.append(f"Referenced security file not found: {security_file}")
                    return False
                    
        return True
    
    def _validate_all_files(self, zip_file: zipfile.ZipFile, manifest: dict) -> bool:
        """Validate all files in the ZIP against their schemas."""
        # Validate commit files
        for commit_path in manifest.get('commits', []):
            if not self._validate_commit_file(zip_file, commit_path):
                return False
        
        # Validate commit chain integrity and timestamp ordering
        if not self._validate_commit_chain(zip_file, manifest.get('commits', [])):
            return False
                
        # Validate workflow files
        workflow = manifest.get('workflow', {})
        if workflow.get('state'):
            if not self._validate_workflow_state(zip_file, workflow['state']):
                return False
                
        if workflow.get('log'):
            if not self._validate_workflow_log(zip_file, workflow['log']):
                return False
                
        # Validate search files (optional)
        search = manifest.get('search', {})
        if search:
            if not self._validate_search_files(zip_file, search):
                return False
                
        # Validate security files (optional)
        security = manifest.get('security', {})
        if security:
            if not self._validate_security_files(zip_file, security):
                return False
                
        return True
    
    def _validate_commit_file(self, zip_file: zipfile.ZipFile, commit_path: str) -> bool:
        """Validate a commit file against its schema."""
        try:
            with zip_file.open(commit_path) as f:
                commit_data = json.load(f)
        except Exception as e:
            self.errors.append(f"Failed to parse commit file {commit_path}: {e}")
            return False
            
        try:
            validate(commit_data, self.schemas['commit.schema'])
        except ValidationError as e:
            self.errors.append(f"Commit validation failed for {commit_path}: {e.message}")
            return False
            
        return True
    
    def _validate_workflow_state(self, zip_file: zipfile.ZipFile, state_path: str) -> bool:
        """Validate a workflow state file against its schema."""
        try:
            with zip_file.open(state_path) as f:
                state_data = json.load(f)
        except Exception as e:
            self.errors.append(f"Failed to parse workflow state file {state_path}: {e}")
            return False
            
        try:
            validate(state_data, self.schemas['workflow_state.schema'])
        except ValidationError as e:
            self.errors.append(f"Workflow state validation failed for {state_path}: {e.message}")
            return False
            
        return True
    
    def _validate_workflow_log(self, zip_file: zipfile.ZipFile, log_path: str) -> bool:
        """Validate a workflow log file against its schema."""
        try:
            with zip_file.open(log_path) as f:
                log_content = f.read().decode('utf-8')
        except Exception as e:
            self.errors.append(f"Failed to read workflow log file {log_path}: {e}")
            return False
            
        # Validate each line as JSON and monotonic timestamps if present
        last_ts: Optional[datetime] = None
        for line_num, line in enumerate(log_content.strip().split('\n'), 1):
            if line.strip():
                try:
                    event = json.loads(line)
                except json.JSONDecodeError as e:
                    self.errors.append(f"Invalid JSON in workflow log {log_path} at line {line_num}: {e}")
                    return False
                ts_value = event.get('ts')
                if ts_value is not None:
                    try:
                        current_ts = self._parse_iso8601(ts_value)
                    except Exception:
                        self.errors.append(f"Invalid timestamp format in {log_path} at line {line_num}: {ts_value}")
                        return False
                    if last_ts is not None and current_ts < last_ts:
                        self.errors.append(f"Non-monotonic workflow log timestamp at line {line_num}")
                        return False
                    last_ts = current_ts
        
        return True
    
    def _validate_search_files(self, zip_file: zipfile.ZipFile, search: dict) -> bool:
        """Validate search-related files."""
        # Validate chunks file
        if search.get('chunks'):
            if not self._validate_chunks_file(zip_file, search['chunks']):
                return False
                
        # Validate metadata file and optionally embeddings file size vs dim
        meta_data: Optional[dict] = None
        if search.get('meta'):
            try:
                with zip_file.open(search['meta']) as f:
                    meta_data = json.load(f)
            except Exception as e:
                self.errors.append(f"Failed to parse search metadata file {search['meta']}: {e}")
                return False
            try:
                validate(meta_data, self.schemas['search_meta.schema'])
            except ValidationError as e:
                self.errors.append(f"Search metadata validation failed for {search['meta']}: {e.message}")
                return False
        
        # Validate embeddings file size matches metadata dim (if both present)
        if search.get('embeddings') and meta_data is not None:
            try:
                with zip_file.open(search['embeddings']) as f:
                    raw = f.read()
            except Exception as e:
                self.errors.append(f"Failed to read embeddings file {search['embeddings']}: {e}")
                return False
            dim = meta_data.get('dim')
            if not isinstance(dim, int) or dim <= 0:
                self.errors.append("Invalid 'dim' in search metadata; must be positive integer")
                return False
            dtype = meta_data.get('dtype', 'float32')
            if dtype not in ('float32', 'float16'):
                self.errors.append("Invalid 'dtype' in search metadata; allowed: 'float32', 'float16'")
                return False
            bytes_per_element = 4 if dtype == 'float32' else 2
            row_size = dim * bytes_per_element
            if row_size == 0:
                self.errors.append("Computed row size is zero; invalid 'dim' or 'dtype'")
                return False
            if len(raw) == 0 or (len(raw) % row_size) != 0:
                self.errors.append(
                    f"Embeddings file length {len(raw)} is not a multiple of dim({dim})*bytes_per_element({bytes_per_element})"
                )
                return False
        
        return True
    
    def _validate_chunks_file(self, zip_file: zipfile.ZipFile, chunks_path: str) -> bool:
        """Validate a chunks file against its schema."""
        try:
            with zip_file.open(chunks_path) as f:
                chunks_content = f.read().decode('utf-8')
        except Exception as e:
            self.errors.append(f"Failed to read chunks file {chunks_path}: {e}")
            return False
            
        # Validate each line as JSON
        for line_num, line in enumerate(chunks_content.strip().split('\n'), 1):
            if line.strip():
                try:
                    chunk_data = json.loads(line)
                    validate(chunk_data, self.schemas['chunk.schema'])
                except json.JSONDecodeError as e:
                    self.errors.append(f"Invalid JSON in chunks file {chunks_path} at line {line_num}: {e}")
                    return False
                except ValidationError as e:
                    self.errors.append(f"Chunk validation failed in {chunks_path} at line {line_num}: {e.message}")
                    return False
                    
        return True
    
    def _validate_search_metadata(self, zip_file: zipfile.ZipFile, meta_path: str) -> bool:
        """Validate search metadata file against its schema."""
        try:
            with zip_file.open(meta_path) as f:
                meta_data = json.load(f)
        except Exception as e:
            self.errors.append(f"Failed to parse search metadata file {meta_path}: {e}")
            return False
            
        try:
            validate(meta_data, self.schemas['search_meta.schema'])
        except ValidationError as e:
            self.errors.append(f"Search metadata validation failed for {meta_path}: {e.message}")
            return False
            
        return True
    
    def _validate_security_files(self, zip_file: zipfile.ZipFile, security: dict) -> bool:
        """Validate security-related files."""
        # This is a placeholder for future security validation
        # For now, just check that files exist and are valid JSON
        for security_file in [security.get('trustchain'), security.get('policies')]:
            if security_file:
                try:
                    with zip_file.open(security_file) as f:
                        json.load(f)  # Just check it's valid JSON
                except Exception as e:
                    self.errors.append(f"Failed to parse security file {security_file}: {e}")
                    return False
                    
        return True
    
    def validate_examples(self) -> bool:
        """Validate all example files in the spec directory."""
        examples_dir = self.spec_root / 'examples'
        if not examples_dir.exists():
            self.warnings.append("Examples directory not found")
            return True
            
        all_valid = True
        for example_file in examples_dir.rglob('*.json'):
            try:
                with open(example_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if 'manifest' in example_file.name:
                    # Validate manifest schema
                    Draft202012Validator.check_schema(self.schemas['manifest.schema'])
                    try:
                        validate(data, self.schemas['manifest.schema'])
                    except ValidationError as e:
                        self.errors.append(f'Invalid example {example_file}: {e.message}')
                        all_valid = False
                
            except Exception as e:
                self.errors.append(f'Failed to validate example {example_file}: {e}')
                all_valid = False
                
        return all_valid
    
    def get_results(self) -> Tuple[List[str], List[str], float]:
        """Get validation results."""
        return self.errors, self.warnings, time.time() - self.start_time
    
    def print_results(self):
        """Print validation results in a user-friendly format."""
        errors, warnings, duration = self.get_results()
        
        print(f"\n{'='*60}")
        print(f"Prooflane Validation Results")
        print(f"{'='*60}")
        
        if errors:
            print(f"\nValidation FAILED ({len(errors)} errors)")
            for error in errors:
                print(f"  • {error}")
        else:
            print(f"\nValidation PASSED")
            
        if warnings:
            print(f"\nWarnings ({len(warnings)})")
            for warning in warnings:
                print(f"  • {warning}")
                
        print(f"\nValidation completed in {duration:.2f}s")
        print(f"{'='*60}")
        
        return len(errors) == 0

    def _validate_commit_chain(self, zip_file: zipfile.ZipFile, commit_paths: List[str]) -> bool:
        """Validate that commit parents and timestamps form a proper chain."""
        previous_commit: Optional[dict] = None
        for index, commit_path in enumerate(commit_paths):
            try:
                with zip_file.open(commit_path) as f:
                    commit_obj = json.load(f)
            except Exception as e:
                self.errors.append(f"Failed to parse commit file {commit_path}: {e}")
                return False
            # Parent check
            if index == 0:
                if commit_obj.get('parent') is not None:
                    self.errors.append(f"First commit {commit_path} must have parent = null")
                    return False
            else:
                expected_parent = previous_commit.get('commit_id') if previous_commit else None
                if commit_obj.get('parent') != expected_parent:
                    self.errors.append(
                        f"Broken commit chain at {commit_path}: parent {commit_obj.get('parent')} != previous commit_id {expected_parent}"
                    )
                    return False
            # Timestamp monotonicity (strictly increasing)
            try:
                current_ts = self._parse_iso8601(commit_obj.get('timestamp'))
            except Exception:
                self.errors.append(f"Invalid commit timestamp format in {commit_path}: {commit_obj.get('timestamp')}")
                return False
            if previous_commit is not None:
                prev_ts = self._parse_iso8601(previous_commit.get('timestamp'))
                if current_ts <= prev_ts:
                    self.errors.append(
                        f"Commit timestamps not strictly increasing at {commit_path}"
                    )
                    return False
            previous_commit = commit_obj
        return True

    def _parse_iso8601(self, value: Optional[str]) -> datetime:
        """Parse ISO-8601 timestamps including 'Z' suffix."""
        if value is None:
            raise ValueError("timestamp is None")
        clean = value.replace('Z', '+00:00')
        return datetime.fromisoformat(clean)

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Validate Prooflane (.pla) files against the specification",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python validate.py document.pla                    # Validate a .pla file
  python validate.py --examples                     # Validate all examples
  python validate.py --verbose document.pla         # Verbose output
  python validate.py --output report.json document.pla  # Output to JSON
        """
    )
    
    parser.add_argument('path', nargs='?', help='Path to .pla file or directory to validate')
    parser.add_argument('--examples', action='store_true', help='Validate all examples in spec directory')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--output', '-o', help='Output results to JSON file')
    parser.add_argument('--version', action='version', version='Prooflane Validator v0.1')
    
    args = parser.parse_args()
    
    # Determine spec root
    script_dir = pathlib.Path(__file__).resolve().parent
    spec_root = script_dir.parent / 'spec' / '0.1-draft'
    
    if not spec_root.exists():
        print(f"❌ Spec directory not found: {spec_root}")
        sys.exit(1)
        
    # Initialize validator
    validator = ProoflaneValidator(spec_root)
    
    success = True
    
    # Validate examples if requested
    if args.examples:
        if args.verbose:
            print("🔍 Validating examples...")
        success = validator.validate_examples() and success
        
    # Validate specific path if provided
    if args.path:
        path = pathlib.Path(args.path)
        if args.verbose:
            print(f"🔍 Validating: {path}")
            
        if path.is_file() and path.suffix == '.pla':
            success = validator.validate_pla_file(path) and success
        elif path.is_dir():
            # Validate all .pla files in directory
            for pla_file in path.glob('*.pla'):
                if args.verbose:
                    print(f"🔍 Validating: {pla_file}")
                success = validator.validate_pla_file(pla_file) and success
        else:
            print(f"❌ Invalid path: {path}")
            sys.exit(1)
            
    # If no specific validation requested, validate examples by default
    if not args.examples and not args.path:
        if args.verbose:
            print("🔍 No specific validation requested, validating examples...")
        success = validator.validate_examples() and success
        
    # Print results
    success = validator.print_results() and success
    
    # Output to JSON if requested
    if args.output:
        errors, warnings, duration = validator.get_results()
        output_data = {
            'timestamp': time.time(),
            'success': success,
            'errors': errors,
            'warnings': warnings,
            'duration': duration
        }
        
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2)
            print(f"\nResults written to: {args.output}")
        except Exception as e:
            print(f"Failed to write output file: {e}")
            
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
