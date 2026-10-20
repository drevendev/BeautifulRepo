"""Validate and render a small, source-backed collection without network access."""
from __future__ import annotations

import argparse
from datetime import date
from html import escape
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

HERE = Path(__file__).resolve().parent
SAMPLE = HERE / "items.json"
MAX_INPUT_BYTES = 1024 * 1024
REQUIRED_TOP = {"title", "scope", "entries"}
REQUIRED_ITEM = {"id", "title", "url", "category", "why", "use_when", "limitation", "verified_on"}
SLUG = re.compile(r"[a-z][a-z0-9-]{1,39}\Z")
ISO_DATE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}\Z")


def checked_text(value: object, label: str, minimum: int = 5, maximum: int = 300) -> str:
    if not isinstance(value, str) or not minimum <= len(value) <= maximum:
        raise ValueError(f"Invalid {label}")
    if value != value.strip() or any(ord(c) < 32 or ord(c) == 127 or 0xD800 <= ord(c) <= 0xDFFF for c in value):
        raise ValueError(f"Invalid {label}")
    return value


def checked_date(value: object) -> date:
    if not isinstance(value, str) or not ISO_DATE.fullmatch(value):
        raise ValueError("Invalid reviewed date")
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise ValueError("Invalid reviewed date") from None


def checked_url(value: object) -> str:
    if not isinstance(value, str) or len(value) > 2048 or any(
        c.isspace() or ord(c) < 32 or ord(c) == 127 or 0xD800 <= ord(c) <= 0xDFFF or c in '<>\\"\'()[]' for c in value
    ):
        raise ValueError("Invalid link URL")
    try:
        parts = urlsplit(value)
        if parts.scheme != "https" or not parts.hostname or "." not in parts.hostname:
            raise ValueError("Invalid link URL")
        if parts.username is not None or parts.password is not None or parts.port is not None:
            raise ValueError("Invalid link URL")
    except ValueError:
        raise ValueError("Invalid link URL") from None
    # Deliberately accept ordinary ASCII DNS names, not every legal URI form.
    # This is a syntax boundary; no DNS or destination-safety check is performed.
    host = parts.hostname
    labels = host.split(".")
    if (parts.netloc.lower() != host or len(host) > 253
            or any(not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?", label)
                   for label in labels)
            or re.search(r"%(?![0-9A-Fa-f]{2})", value)):
        raise ValueError("Invalid link URL")
    # A trailing '#' is still an explicit fragment delimiter.
    # Encoded '%23' remains valid path or query content.
    if "#" in value:
        raise ValueError("Use an unfragmented canonical URL")
    return value


def reject_duplicate_json_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    """Reject ambiguous JSON metadata before any values are silently overwritten."""
    fields: dict[str, object] = {}
    for key, value in pairs:
        if key in fields:
            raise ValueError("Duplicate JSON object key")
        fields[key] = value
    return fields


def validate(raw: object, as_of: date) -> list[dict[str, str]]:
    if not isinstance(raw, dict) or set(raw) != REQUIRED_TOP:
        raise ValueError("Invalid collection metadata")
    checked_text(raw["title"], "collection title", 5, 120)
    checked_text(raw["scope"], "collection scope", 15, 400)
    entries = raw["entries"]
    if not isinstance(entries, list) or not 1 <= len(entries) <= 50:
        raise ValueError("Expected 1–50 items")
    seen_ids: set[str] = set()
    seen_urls: set[str] = set()
    checked: list[dict[str, str]] = []
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != REQUIRED_ITEM:
            raise ValueError("Invalid item fields")
        ident = entry["id"]
        category = entry["category"]
        if not isinstance(ident, str) or not SLUG.fullmatch(ident) or ident in seen_ids:
            raise ValueError("Invalid or duplicate item id")
        if not isinstance(category, str) or not SLUG.fullmatch(category):
            raise ValueError("Invalid category")
        verified = checked_date(entry["verified_on"])
        if verified > as_of:
            raise ValueError("Review date cannot be in the future")
        url = checked_url(entry["url"])
        parts = urlsplit(url)
        canonical = parts.hostname.lower() + parts.path.rstrip("/") + ("?" + parts.query if parts.query else "")
        if canonical in seen_urls:
            raise ValueError("Duplicate destination")
        for field in ("title", "why", "use_when", "limitation"):
            checked_text(entry[field], field, 5 if field == "title" else 15, 300)
        seen_ids.add(ident)
        seen_urls.add(canonical)
        checked.append(entry.copy())
    return sorted(checked, key=lambda item: (item["category"], item["title"].casefold(), item["id"]))


def report(raw: object, as_of: date, max_age: int) -> dict:
    if max_age < 1:
        raise ValueError("max-age-days must be positive")
    checked = validate(raw, as_of)
    entries = [{**item, "review_due": (as_of - checked_date(item["verified_on"])).days > max_age}
               for item in checked]
    return {"title": raw["title"], "scope": raw["scope"], "as_of": as_of.isoformat(),
            "max_age_days": max_age, "entries": entries,
            "review_due": sum(item["review_due"] for item in entries)}


def markdown_text(value: str) -> str:
    """Escape inline Markdown controls as well as HTML, including link-label delimiters."""
    return re.sub(r"([\\\[\]*_`~])", r"\\\1", escape(value, quote=False))


def markdown(result: dict) -> str:
    lines = [f'# {markdown_text(result["title"])}', "", f'**Scope:** {markdown_text(result["scope"])}', "",
             f'Offline audit as of {result["as_of"]}. The script does not visit links.', ""]
    prior = None
    for item in result["entries"]:
        if item["category"] != prior:
            lines.extend([f'## {markdown_text(item["category"].replace("-", " ").title())}', ""])
            prior = item["category"]
        flag = " · **Review due**" if item["review_due"] else ""
        lines.extend([
            f'- **[{markdown_text(item["title"])}]({item["url"]})** (checked {item["verified_on"]}{flag})',
            f'  - **Use when:** {markdown_text(item["use_when"])}',
            f'  - **Why:** {markdown_text(item["why"])}',
            f'  - **Limit:** {markdown_text(item["limitation"])}',
            "",
        ])
    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit a curated collection offline")
    parser.add_argument("--data", type=Path, default=SAMPLE)
    parser.add_argument("--as-of", default=date.today().isoformat(), help="YYYY-MM-DD")
    parser.add_argument("--max-age-days", type=int, default=180)
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--fail-on-stale", action="store_true")
    options = parser.parse_args(argv)
    try:
        as_of = checked_date(options.as_of)
        with options.data.open("rb") as handle:
            content = handle.read(MAX_INPUT_BYTES + 1)
        if len(content) > MAX_INPUT_BYTES:
            raise ValueError("Collection input exceeds the documented read limit")
        raw = json.loads(content.decode("utf-8"),
                         object_pairs_hook=reject_duplicate_json_keys)
        output = report(raw, as_of, options.max_age_days)
    except (OSError, ValueError, UnicodeError, RecursionError):
        parser.exit(1, "Invalid collection input or unavailable file\n")
    if options.format == "json":
        print(json.dumps(output, indent=2, ensure_ascii=False, sort_keys=True))
    else:
        print(markdown(output), end="")
    return 2 if options.fail_on_stale and output["review_due"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
