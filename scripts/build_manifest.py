"""Freeze hashes for the allowlisted companion files, excluding generated outputs."""

import hashlib
from datetime import date
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SELF = "provenance/file_manifest.json"
files = []
patterns = [r"gh[pousr]_[A-Za-z0-9]{25,}", r"github_pat_[A-Za-z0-9_]{30,}",
            r"AIza[A-Za-z0-9_-]{30,}", r"sk-[A-Za-z0-9_-]{24,}", r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"]
names = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
                       cwd=ROOT, check=True, capture_output=True).stdout.decode().split("\0")
for rel in sorted(set(names) - {"", SELF}):
    path = ROOT / rel
    name = path.name
    assert path.suffix in {".md", ".py", ".txt", ".json", ".csv", ".cff"} or name == ".gitignore", rel
    assert not name.startswith(".env") and path.suffix not in {".key", ".pem"}, rel
    data = path.read_bytes()
    text = data.decode("utf-8-sig")
    for pattern in patterns:
        assert not re.search(pattern, text), ("potential credential", rel)
    files.append(dict(path=rel, size_bytes=len(data), sha256=hashlib.sha256(data).hexdigest()))
manifest = dict(prepared=date.today().isoformat(), private=False, files=files,
                scope="Curated numeric/code package, not clinical raw data or original Git history",
                review="Extension/credential-pattern scan; allowlisted exporter and manual scope review also required")
(ROOT / SELF).write_text(json.dumps(manifest, indent=2) + "\n")
print(json.dumps(dict(files=len(files), credential_pattern_scan="pass")))
