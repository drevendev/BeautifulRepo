"""Offline integrity check for the fictional internal-repository fixture."""
from __future__ import annotations

import json
from pathlib import Path

EXPECTED = [{"id": "A-1", "state": "open"}, {"id": "A-2", "state": "closed"}]


def main() -> None:
    path = Path(__file__).with_name("sample_records.json")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SystemExit(f"ERROR: cannot read fixture: {exc.__class__.__name__}") from exc
    if payload != {"records": EXPECTED}:
        raise SystemExit("ERROR: sample records do not match the documented fixture")
    print(f"Sample records: {len(EXPECTED)}")


if __name__ == "__main__":
    main()
