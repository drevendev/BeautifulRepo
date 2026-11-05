#!/usr/bin/env python3
"""Reproduce a synthetic broken-link repair using the real combined audit."""
from __future__ import annotations

import argparse
import difflib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
BUNDLE = ROOT / "tools" / "audit_bundle.py"
LINK_CHECKS = ("markdown_links", "html_navigation")


def make_fixture(folder: Path, *, broken: bool) -> None:
    """Create a tiny fictional checkout; never touch a real project."""
    folder.mkdir()
    (folder / "docs").mkdir()
    destination = "docs/setup.md" if broken else "docs/guide.md"
    (folder / "README.md").write_text(
        "# Pocket Trails\n\n"
        "Pocket Trails is a fictional offline trail-notes project.\n\n"
        "## First success\n\n"
        f"Read the [setup guide]({destination}) to begin.\n\n"
        "## Contribute\n\n"
        "See [CONTRIBUTING.md](CONTRIBUTING.md).\n",
        encoding="utf-8",
    )
    (folder / "docs" / "guide.md").write_text(
        "# Setup guide\n\nThis is deliberately fictional documentation.\n",
        encoding="utf-8",
    )
    (folder / "LICENSE").write_text(
        "MIT License\n\nThis is a synthetic test fixture, not a real release.\n",
        encoding="utf-8",
    )
    (folder / "CONTRIBUTING.md").write_text(
        "# Contributing\n\nOpen a small, reproducible change.\n", encoding="utf-8"
    )


def file_bytes(folder: Path) -> dict[str, bytes]:
    return {
        file.relative_to(folder).as_posix(): file.read_bytes()
        for file in folder.rglob("*") if file.is_file()
    }


def run_audit(folder: Path) -> dict:
    original = file_bytes(folder)
    completed = subprocess.run(
        [sys.executable, "-I", str(BUNDLE), str(folder), "--format", "json",
         "--fail-on", "never"],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
        check=False, timeout=75,
    )
    if not completed.stdout:
        raise RuntimeError("combined audit produced no JSON: " +
                           completed.stderr.strip()[:250])
    try:
        report = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("combined audit did not produce valid JSON") from exc
    if (not isinstance(report, dict) or report.get("schema_version") != 1
            or report.get("exit_code") != completed.returncode):
        raise RuntimeError("combined audit exit status does not match its report")
    if file_bytes(folder) != original:
        raise RuntimeError("combined audit modified the synthetic checkout")
    return report


def demonstrate() -> dict:
    with tempfile.TemporaryDirectory(prefix="beautifulrepo-demo-") as temporary:
        root = Path(temporary)
        before, after = root / "before", root / "after"
        make_fixture(before, broken=True)
        make_fixture(after, broken=False)
        repair_diff = "".join(difflib.unified_diff(
            (before / "README.md").read_text(encoding="utf-8").splitlines(keepends=True),
            (after / "README.md").read_text(encoding="utf-8").splitlines(keepends=True),
            fromfile="before/README.md", tofile="after/README.md",
        ))
        results = {"before": run_audit(before), "after": run_audit(after)}
    for label, expected in (("before", 1), ("after", 0)):
        result = results[label]
        if result["exit_code"] != expected:
            raise RuntimeError(f"{label} audit exited {result['exit_code']}, expected {expected}")
        if any(item["state"] != "complete" for item in result["checks"].values()):
            raise RuntimeError(f"{label} audit is incomplete, not a valid demonstration")
    for checker in LINK_CHECKS:
        broken = results["before"]["checks"][checker]
        fixed = results["after"]["checks"][checker]
        if (broken["exit_code"] != 1 or fixed["exit_code"] != 0
                or not any("docs/setup.md" in line for line in broken["diagnostics"])):
            raise RuntimeError(f"{checker} did not reproduce the expected link repair")
    changed_lines = [
        line for line in repair_diff.splitlines()
        if line.startswith(("+", "-")) and not line.startswith(("+++", "---"))
    ]
    if changed_lines != [
        "-Read the [setup guide](docs/setup.md) to begin.",
        "+Read the [setup guide](docs/guide.md) to begin.",
    ]:
        raise RuntimeError("the fictional README repair is not one verified link edit")
    return {"fixture_kind": "synthetic", "reports": results,
            "repair_diff": repair_diff,
            "verification": "Both link checkers found the missing path before and cleared after; no fixture writes by the audit."}


def text_report(result: dict) -> str:
    lines = ["Synthetic Pocket Trails — real BeautifulRepo combined audit output",
             "The repair changes one README link to an existing local guide."]
    lines.extend(("\nExact fictional README repair (unified diff):",
                  result["repair_diff"].rstrip("\n")))
    for label in ("before", "after"):
        report = result["reports"][label]
        lines.append(f"\n{label.upper()}: combined exit {report['exit_code']}")
        for checker, item in report["checks"].items():
            if checker == "entry_points":
                counts = item["report"]["summary"]
                lines.append(
                    f"  {checker}: {counts['error']} errors, {counts['warning']} warnings, "
                    f"{counts['info']} informational findings"
                )
            else:
                lines.append(f"  {checker}: exit {item['exit_code']}, "
                             f"{item['inspected_markdown_files']} Markdown files inspected")
                if label == "before":
                    lines.extend(f"    {message}" for message in item["diagnostics"])
    lines.extend(("\n" + result["verification"],
                  "Synthetic exercise; not a real repository improvement, external link check, "
                  "rendering test or accessibility certificate."))
    return "\n".join(lines) + "\n"

def html_report(result: dict) -> str:
    """Render a responsive comparison of the real synthetic checker observations."""
    from html import escape

    def safe(value: object) -> str:
        # Prevent control and format characters from forging report content.
        printable = "".join(
            char if char.isprintable() else f"\\u{ord(char):04x}"
            for char in str(value)
        )
        return escape(printable, quote=True)

    def safe_multiline(value: object) -> str:
        # Preserve the diff's line structure in <pre>, escaping each line.
        return "\n".join(safe(line) for line in str(value).split("\n"))

    parts = [
        "<!doctype html>",
        '<html lang="en"><head><meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        "<title>Pocket Trails | BeautifulRepo before/after audit</title>",
        "<style>",
        ":root { color-scheme: light dark; font-family: system-ui, sans-serif; }",
        "body { max-width: 78rem; margin: auto; padding: clamp(1rem, 3vw, 2rem); "
        "line-height: 1.55; }",
        ".reports { display: grid; gap: 1.25rem; }",
        "@media (min-width: 55rem) { .reports { "
        "grid-template-columns: repeat(2, minmax(0, 1fr)); } }",
        "article { border: 1px solid #8888; border-radius: .65rem; "
        "padding: 1.25rem; min-width: 0; }",
        "article section { border-top: 1px solid #8888; margin-top: 1.2rem; }",
        "code { overflow-wrap: anywhere; white-space: pre-wrap; }",
        "pre { padding: 1rem; border: 1px solid #8888; border-radius: .5rem; "
        "overflow-wrap: anywhere; white-space: pre-wrap; }",
        "li { margin: .5rem 0; }",
        ".outcome { border-inline-start: .3rem solid currentColor; "
        "padding: .25rem 0 .25rem .75rem; }",
        ".overview-grid { display: grid; gap: .75rem; }",
        "@media (min-width: 35rem) { .overview-grid { "
        "grid-template-columns: repeat(2, minmax(0, 1fr)); } }",
        ".overview-item { margin: 0; border: 1px solid #8888; "
        "border-radius: .5rem; padding: .75rem; }",
        "</style></head><body><main>",
        "<h1>One broken link, two independent checkers</h1>",
        "<p><strong>Synthetic Pocket Trails fixture.</strong> These are "
        "observations from BeautifulRepo's actual offline checkers on "
        "disposable local directories. No real repository was repaired.</p>",
        '<section aria-labelledby="overview-heading">',
        '<h2 id="overview-heading">Before and after at a glance</h2>',
        '<div class="overview-grid">',
    ]
    # Put observed outcomes above the long diff for first-screen readers.
    # The detailed report below uses the same check result dictionaries.
    for label in ("before", "after"):
        report = result["reports"][label]
        local_checks_passing = sum(
            report["checks"][checker]["exit_code"] == 0
            for checker in LINK_CHECKS
        )
        parts.append(
            f'<p class="overview-item"><strong>{label.title()}:</strong> '
            f'{local_checks_passing}/{len(LINK_CHECKS)} local-link checks pass; '
            f'combined audit exit {report["exit_code"]}.</p>'
        )
    parts.extend((
        '</div>',
        '</section>',
        '<p><a href="#after-title">Jump to after repair</a></p>',
        '<section aria-labelledby="repair-heading">',
        '<h2 id="repair-heading">The exact fictional README change</h2>',
        '<p>Source-derived unified diff from the two fixture READMEs, not an edit '
        'to an outside repository.</p>',
        f'<pre><code>{safe_multiline(result["repair_diff"])}</code></pre>',
        '</section>',
        '<div class="reports">',
    ))
    for label in ("before", "after"):
        report = result["reports"][label]
        title = "Before repair" if label == "before" else "After repair"
        local_checks_passing = sum(
            report["checks"][checker]["exit_code"] == 0
            for checker in LINK_CHECKS
        )
        outcome_title = (
            "Before: missing local link found."
            if label == "before" else "After: link corrected."
        )
        parts.extend((
            f'<article aria-labelledby="{label}-title">',
            f'<h2 id="{label}-title">{title}</h2>',
            f'<p class="outcome"><strong>{outcome_title}</strong> '
            f'{local_checks_passing}/{len(LINK_CHECKS)} local-link checks pass.</p>',
            f"<p><strong>Combined audit exit {report['exit_code']}</strong></p>",
        ))
        for checker in ("entry_points", "markdown_links", "html_navigation"):
            item = report["checks"][checker]
            parts.extend((
                "<section>",
                f"<h3>{safe(checker.replace('_', ' ').title())}</h3>",
                f"<p>State: {safe(item['state'])}; "
                f"checker exit {item['exit_code']}.</p>",
            ))
            if checker == "entry_points":
                summary = item["report"]["summary"]
                parts.append(
                    f"<p>{summary['error']} errors, {summary['warning']} warnings, "
                    f"{summary['info']} informational findings.</p>"
                )
                entries = [
                    f"{finding['severity']} [{finding['rule_id']}] "
                    f"{finding['path']}: {finding['message']} "
                    f"Next: {finding['remediation']}"
                    for finding in item["report"]["findings"]
                ]
            else:
                parts.append(
                    f"<p>{item['inspected_markdown_files']} Markdown files inspected; "
                    f"{item['checked_destinations']} local destinations checked.</p>"
                )
                entries = item["diagnostics"]
            if entries:
                parts.append("<ul>")
                parts.extend(f"<li><code>{safe(entry)}</code></li>" for entry in entries)
                parts.append("</ul>")
            else:
                parts.append("<p>No findings from this checker.</p>")
            parts.append("</section>")
        parts.append("</article>")
    parts.extend((
        "</div>",
        f"<p>{safe(result['verification'])}</p>",
        "<p>This example does not check external URLs, rendered GitHub Markdown, "
        "accessibility conformance or real-user outcomes. Review audit paths and "
        "diagnostics before sharing any report from your own repository.</p>",
        "</main></body></html>",
    ))
    return "\n".join(parts) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--format", choices=("text", "json", "html"), default="text")
    args = parser.parse_args(argv)
    try:
        result = demonstrate()
    except (RuntimeError, OSError, subprocess.TimeoutExpired) as exc:
        print(f"Demo incomplete: {exc}", file=sys.stderr)
        return 2
    if args.format == "json":
        print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=True))
    elif args.format == "html":
        print(html_report(result), end="")
    else:
        print(text_report(result), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
