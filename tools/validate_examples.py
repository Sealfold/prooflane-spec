import json
import sys
import argparse
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

from jsonschema import Draft202012Validator
from referencing import Registry, Resource


REPO_ROOT = Path(__file__).resolve().parents[2]
SPEC_ROOT = REPO_ROOT / "prooflane-spec" / "spec" / "0.1-draft"
SCHEMA_DIR = SPEC_ROOT / "schemas"


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as ex:
                raise ValueError(f"{path}:{line_num}: invalid JSON: {ex}") from ex
    return rows


def build_registry() -> Registry:
    resources = {}
    for schema_path in SCHEMA_DIR.glob("*.schema.json"):
        data = load_json(schema_path)
        schema_id = data.get("$id") or f"file://{schema_path.as_posix()}"
        resources[schema_id] = Resource.from_contents(data)
    return Registry(resources=resources)


def iter_errors(validator: Draft202012Validator, instance: Any, ctx: str) -> List[str]:
    messages: List[str] = []
    for err in sorted(validator.iter_errors(instance), key=lambda e: e.path):
        loc = "/".join(map(str, err.path)) or "<root>"
        messages.append(f"[ERROR] {ctx}: {loc}: {err.message}")
    return messages


def validate_manifest_tree(manifest_path: Path) -> List[str]:
    msgs: List[str] = []
    registry = build_registry()

    # Validate manifest
    manifest_schema = load_json(SCHEMA_DIR / "manifest.schema.json")
    manifest_validator = Draft202012Validator(manifest_schema, registry=registry)
    manifest = load_json(manifest_path)
    msgs.extend(iter_errors(manifest_validator, manifest, str(manifest_path)))

    base_dir = manifest_path.parent

    # Check required paths exist from manifest
    def must_exist(rel_path: str, label: str) -> None:
        p = base_dir / rel_path
        if not p.exists():
            msgs.append(f"[ERROR] {manifest_path}: missing {label} path: {rel_path}")

    # history commits
    commits: List[str] = manifest.get("commits", [])
    commit_records: List[Dict[str, Any]] = []
    for c in commits:
        must_exist(c, "commit")
        try:
            commit_data = load_json(base_dir / c)
        except Exception as ex:
            msgs.append(f"[ERROR] {manifest_path}: commit {c}: cannot read: {ex}")
            continue
        commit_schema = load_json(SCHEMA_DIR / "commit.schema.json")
        commit_validator = Draft202012Validator(commit_schema, registry=registry)
        msgs.extend(iter_errors(commit_validator, commit_data, f"{base_dir / c}"))
        commit_records.append(commit_data)

    # Basic commit chain validation
    for idx, rec in enumerate(commit_records):
        parent = rec.get("parent")
        commit_id = rec.get("commit_id")
        if idx == 0:
            if parent is not None:
                msgs.append(f"[ERROR] {manifest_path}: commits[{idx}]: parent must be null for first commit")
        else:
            prev_id = commit_records[idx - 1].get("commit_id")
            if parent != prev_id:
                msgs.append(f"[ERROR] {manifest_path}: commits[{idx}]: parent '{parent}' does not match previous commit_id '{prev_id}'")

    # workflow files
    workflow = manifest.get("workflow", {})
    state_path = workflow.get("state")
    log_path = workflow.get("log")
    if state_path:
        must_exist(state_path, "workflow.state")
        try:
            state_data = load_json(base_dir / state_path)
            state_schema = load_json(SCHEMA_DIR / "workflow_state.schema.json")
            state_validator = Draft202012Validator(state_schema, registry=registry)
            msgs.extend(iter_errors(state_validator, state_data, f"{base_dir / state_path}"))
        except Exception as ex:
            msgs.append(f"[ERROR] {manifest_path}: workflow.state {state_path}: {ex}")
    if log_path:
        must_exist(log_path, "workflow.log")
        try:
            events = load_jsonl(base_dir / log_path)
            event_schema = load_json(SCHEMA_DIR / "workflow_event.schema.json")
            event_validator = Draft202012Validator(event_schema, registry=registry)
            for idx, ev in enumerate(events, start=1):
                msgs.extend(iter_errors(event_validator, ev, f"{base_dir / log_path}#{idx}"))
            # Monotonic timestamp check
            try:
                parsed = [datetime.fromisoformat(ev.get("ts")) for ev in events if isinstance(ev.get("ts"), str)]
                for i in range(1, len(parsed)):
                    if parsed[i] < parsed[i-1]:
                        msgs.append(f"[ERROR] {manifest_path}: {log_path}#{i+1}: timestamp not monotonic (earlier than previous)")
            except Exception:
                pass
        except Exception as ex:
            msgs.append(f"[ERROR] {manifest_path}: workflow.log {log_path}: {ex}")

    # search (RAG) files
    search = manifest.get("search", {})
    chunks_path = search.get("chunks") or "search/chunks.jsonl"
    meta_path = search.get("meta") or search.get("metadata") or "search/metadata.json"
    embeddings_path = search.get("embeddings") or "search/embeddings.bin"

    # Only validate search assets if directory exists
    if (base_dir / "search").exists():
        chunk_ids: List[str] = []
        if (base_dir / chunks_path).exists():
            try:
                chunks = load_jsonl(base_dir / chunks_path)
                chunk_schema = load_json(SCHEMA_DIR / "chunk.schema.json")
                chunk_validator = Draft202012Validator(chunk_schema, registry=registry)
                for idx, ch in enumerate(chunks, start=1):
                    msgs.extend(iter_errors(chunk_validator, ch, f"{base_dir / chunks_path}#{idx}"))
                    cid = ch.get("chunk_id")
                    if isinstance(cid, str):
                        chunk_ids.append(cid)
            except Exception as ex:
                msgs.append(f"[ERROR] {manifest_path}: chunks {chunks_path}: {ex}")
        else:
            msgs.append(f"[WARN] {manifest_path}: search dir present but missing chunks at {chunks_path}")

        if (base_dir / meta_path).exists():
            try:
                meta = load_json(base_dir / meta_path)
                meta_schema = load_json(SCHEMA_DIR / "search_meta.schema.json")
                meta_validator = Draft202012Validator(meta_schema, registry=registry)
                msgs.extend(iter_errors(meta_validator, meta, f"{base_dir / meta_path}"))
            except Exception as ex:
                msgs.append(f"[ERROR] {manifest_path}: metadata {meta_path}: {ex}")
        else:
            msgs.append(f"[WARN] {manifest_path}: search dir present but missing metadata at {meta_path}")

        # Embeddings presence & size check (float32)
        embeddings_file = base_dir / embeddings_path
        if not embeddings_file.exists():
            msgs.append(f"[WARN] {manifest_path}: search dir present but missing embeddings at {embeddings_path}")
        else:
            try:
                if (base_dir / meta_path).exists() and (base_dir / chunks_path).exists():
                    meta = load_json(base_dir / meta_path)
                    dim = int(meta.get("dim", 0))
                    if dim <= 0:
                        msgs.append(f"[ERROR] {manifest_path}: metadata {meta_path}: dim must be positive integer")
                    else:
                        num = len(chunk_ids)
                        expected = num * dim * 4
                        size = embeddings_file.stat().st_size
                        if size != expected:
                            msgs.append(f"[ERROR] {manifest_path}: embeddings size {size} != expected {expected} (num_chunks {num} × dim {dim} × 4)")
            except Exception as ex:
                msgs.append(f"[ERROR] {manifest_path}: embeddings check failed: {ex}")

        # Citations integrity (if present)
        citations_path = base_dir / "search" / "citations.jsonl"
        if citations_path.exists():
            try:
                citations = load_jsonl(citations_path)
                for idx, row in enumerate(citations, start=1):
                    ref = row.get("chunk_id")
                    if ref not in chunk_ids:
                        msgs.append(f"[ERROR] {manifest_path}: {citations_path.name}#{idx}: unknown chunk_id '{ref}'")
            except Exception as ex:
                msgs.append(f"[ERROR] {manifest_path}: citations {citations_path.name}: {ex}")

    # security (Sign) files
    security = manifest.get("security", {})
    trustchain = security.get("trustchain")
    policies = security.get("policies")
    if trustchain:
        must_exist(trustchain, "security.trustchain")
    if policies:
        must_exist(policies, "security.policies")

    # If Sign profile (security present), require at least one signature on latest commit
    if security and commit_records:
        last = commit_records[-1]
        sigs = last.get("signatures")
        if not isinstance(sigs, list) or len(sigs) == 0:
            msgs.append(f"[ERROR] {manifest_path}: latest commit must include at least one signature when security profile is present")

        # Anchors token format must look like base64:* if present
        anchors = last.get("anchors") or []
        if isinstance(anchors, list):
            for idx, a in enumerate(anchors, start=1):
                tok = (a or {}).get("token")
                if isinstance(tok, str) and not tok.startswith("base64:"):
                    msgs.append(f"[ERROR] {manifest_path}: anchors[{idx}].token must start with 'base64:'")

    return msgs


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Prooflane examples/fixtures")
    parser.add_argument("base", nargs="?", help="Base directory to scan (defaults to spec/examples)")
    parser.add_argument("--junit-out", dest="junit_out", help="Path to write JUnit XML report")
    args = parser.parse_args()

    base = None
    if args.base:
        base = Path(args.base).resolve()
        if not base.exists():
            print(f"Base path not found: {base}", file=sys.stderr)
            sys.exit(1)
    search_root = base if base is not None else (SPEC_ROOT / "examples")
    manifests = list(search_root.glob("**/manifest.json"))
    if not manifests:
        print("No manifests found under examples/", file=sys.stderr)
        sys.exit(1)

    failures = 0
    results = []  # (path, msgs)
    for m in manifests:
        msgs = []
        try:
            msgs = validate_manifest_tree(m)
        except Exception as ex:
            msgs.append(f"[ERROR] {m}: unexpected exception: {ex}")

        for msg in msgs:
            print(msg)

        if any(msg.startswith("[ERROR]") for msg in msgs):
            failures += 1
        else:
            print(f"OK   {m}")
        results.append((str(m), msgs))

    # Optional JUnit output
    if args.junit_out:
        testsuite = ET.Element("testsuite", name="prooflane-validate", tests=str(len(results)))
        for path, msgs in results:
            testcase = ET.SubElement(testsuite, "testcase", name=path)
            errs = [m for m in msgs if m.startswith("[ERROR]")]
            if errs:
                failure = ET.SubElement(testcase, "failure", message=f"{len(errs)} errors")
                failure.text = "\n".join(errs)
        tree = ET.ElementTree(testsuite)
        Path(args.junit_out).parent.mkdir(parents=True, exist_ok=True)
        tree.write(args.junit_out, encoding="utf-8", xml_declaration=True)

    if failures:
        print(f"Validation failures: {failures}")
        sys.exit(1)


if __name__ == "__main__":
    main()


