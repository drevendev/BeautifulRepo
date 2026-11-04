"""Compare fictional READMEs in a disposable directory, never a user project."""
from __future__ import annotations

import argparse
from collections import Counter
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


def render_text(results: dict) -> str:
    """Show specific source observations, without implying a beauty score."""
    lines = [
        "Synthetic README before/after — offline, disposable fixture",
        "The audit is read-only; only this demo writes temporary fictional READMEs.",
        "",
    ]
    for label in ("before", "after"):
        report = results[label]
        counts = report["summary"]
        lines.append(
            f"{label.upper()}: {counts['error']} error(s), "
            f"{counts['warning']} warning(s), {counts['info']} info"
        )
        for item in report["findings"]:
            location = item["path"]
            if item["line"] is not None:
                location += f":{item['line']}"
            lines.append(
                f"  [{item['severity']}] {item['rule_id']} at {location}: "
                f"{item['message']}"
            )
        lines.append("")

    before = Counter(item["rule_id"] for item in results["before"]["findings"])
    after = Counter(item["rule_id"] for item in results["after"]["findings"])
    removed = sorted((before - after).elements())
    retained = sorted((before & after).elements())
    added = sorted((after - before).elements())
    lines.append("Not reported after the fictional edit: " +
                 (", ".join(removed) if removed else "none"))
    lines.append("Still reported: " +
                 (", ".join(retained) if retained else "none"))
    if added:
        lines.append("New observations: " + ", ".join(added))
    lines.append("Different findings do not prove readability, accessibility or readiness.")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--format", choices=("json", "text"), default="json",
        help="JSON for regression tests (default); text for a human-readable demo",
    )
    args = parser.parse_args(argv)

    with tempfile.TemporaryDirectory(prefix="beautifulrepo-audit-demo-") as directory:
        readme = Path(directory) / "README.md"
        reports = {}
        for name, content in (("before", BEFORE), ("after", AFTER)):
            readme.write_text(content, encoding="utf-8")
            reports[name] = audit_repository(directory)

        if args.format == "text":
            print(render_text(reports))
        else:
            summary = {
                name: {
                    "summary": report["summary"],
                    "rules": [item["rule_id"] for item in report["findings"]],
                }
                for name, report in reports.items()
            }
            print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
