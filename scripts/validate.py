import json, pathlib, sys
from jsonschema import validate, Draft202012Validator
ROOT = pathlib.Path(__file__).resolve().parents[1] / 'spec' / '0.1-draft'
schemas = {p.name: json.loads(p.read_text()) for p in (ROOT / 'schemas').glob('*.json')}
examples = list((ROOT / 'examples').rglob('*.json'))
ok = True
for ex in examples:
    data = json.loads(ex.read_text())
    if 'manifest' in ex.name:
        Draft202012Validator.check_schema(schemas['manifest.schema.json'])
        try:
            validate(data, schemas['manifest.schema.json'])
        except Exception as e:
            print(f'Invalid example {ex}: {e}'); ok = False
print('ALL GOOD' if ok else 'FAIL'); sys.exit(0 if ok else 1)
