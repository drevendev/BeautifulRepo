"""Compare two fictional READMEs in a disposable directory, never a user project."""
from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from repo_audit import audit_repository  # noqa: E402 (needs the sys.path entry above)

BEFORE = """# Parcel

TBD

### Try it

| | |
| --- | --- |
| Promise | Evidence |
"""
AFTER = """# Parcel

A fictional example of a project that indexes notes.

## Try it

This fixture demonstrates README structure, not a distributed application.

- Promise: explain the outcome.
- Evidence: show a representative result.
"""


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="beautifulrepo-audit-demo-") as directory:
        readme = Path(directory) / "README.md"
        results = {}
        for name, content in (("before", BEFORE), ("after", AFTER)):
            readme.write_text(content, encoding="utf-8")
            report = audit_repository(directory)
            results[name] = {
                "summary": report["summary"],
                "rules": [item["rule_id"] for item in report["findings"]],
            }
        print(json.dumps(results, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
