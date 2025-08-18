#!/usr/bin/env python3
"""Build .pla ZIPs for conformance cases under spec/0.1-draft/conformance/*"""
import pathlib
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
CONF = ROOT / 'spec' / '0.1-draft' / 'conformance'
OUT = CONF / '_zips'

CASES = [
    'AT-001-missing-required',
    'AT-010-broken-parent',
    'AT-020-workflow-tampered',
    'AT-030-signature-mismatch',
    'AT-040-anchor-invalid',
    'AT-050-embedding-dim-mismatch',
    'AT-060-unknown-chunk-id',
]


def build_case(case: str) -> None:
    case_dir = CONF / case
    out_path = OUT / f"{case}.pla"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out_path, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        # include known paths if present
        for rel in [
            'manifest.json',
            'history/0001.json',
            'history/0002.json',
            'workflow/state.json',
            'workflow/log.jsonl',
            'canonical/index.html',
            'search/chunks.jsonl',
            'search/metadata.json',
            'search/embeddings.bin',
            'security/trustchain.json',
            'security/policies.json',
        ]:
            p = case_dir / rel
            if p.exists():
                z.write(p, arcname=rel)


def main() -> int:
    for c in CASES:
        build_case(c)
    print(f"Built conformance zips into {OUT}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
