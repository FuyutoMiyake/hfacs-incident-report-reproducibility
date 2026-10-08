"""Verify committed computational snapshot files, before regenerating outputs."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
manifest = json.loads((ROOT / "provenance/file_manifest.json").read_text())
for record in manifest["files"]:
    path = ROOT / record["path"]
    assert path.is_file(), record["path"]
    assert hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"], record["path"]
print(json.dumps(dict(files_checked=len(manifest["files"]), status="pass")))
