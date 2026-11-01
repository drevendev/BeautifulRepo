#!/usr/bin/env python3
"""Apply one pre-approved README proposal with exact content-hash guards."""
from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import runpy
import stat
import sys
import tempfile

# Isolated Python (-I) omits the script directory from imports. Load only this
# installed BeautifulRepo sibling by its fixed path, never from the target.
_preview = runpy.run_path(str(Path(__file__).with_name("readme_preview.py")))
PreviewError = _preview["PreviewError"]
read_file = _preview["read_file"]
_redirect = _preview["_redirect"]
SHA256 = _preview["SHA256"]


class ApplyError(ValueError):
    """An exact-hash, input, or path precondition was not satisfied."""


def apply(root: Path, proposal: Path, approved_current: str, approved_proposed: str) -> str:
    """Replace only README.md; consent is a separate human/agent workflow gate."""
    try:
        if _redirect(root) or not stat.S_ISDIR(root.lstat().st_mode):
            raise ApplyError("root: expected an ordinary, non-symlinked directory.")
        if proposal.resolve(strict=True).is_relative_to(root.resolve(strict=True)):
            raise ApplyError("proposal must be outside the target checkout.")
        old, _ = read_file(root / "README.md", "README.md")
        new, _ = read_file(proposal, "proposal")
    except (OSError, RuntimeError) as exc:
        raise ApplyError("cannot inspect target or proposal.") from exc
    except PreviewError as exc:
        raise ApplyError(str(exc)) from exc

    current_hash = hashlib.sha256(old).hexdigest()
    proposed_hash = hashlib.sha256(new).hexdigest()
    if current_hash != approved_current:
        raise ApplyError("README.md does not match the approved current SHA-256; re-preview and re-approve.")
    if proposed_hash != approved_proposed:
        raise ApplyError("proposal does not match the approved SHA-256; re-preview and re-approve.")
    if old == new:
        return "No change: README.md already matches the approved proposal."

    readme = root / "README.md"
    staged: Path | None = None
    try:
        # Stage complete bytes in the same directory so the final replacement is
        # atomic on normal local filesystems; never mutate the candidate source.
        fd, name = tempfile.mkstemp(prefix=".beautifulrepo-readme-", suffix=".tmp", dir=root)
        staged = Path(name)
        with os.fdopen(fd, "wb") as stream:
            stream.write(new)
            stream.flush()
            os.fsync(stream.fileno())
        # Preserve POSIX file permission bits rather than making a private 0600
        # README by accident. Windows retains the parent directory's ACL model.
        if os.name == "posix":
            staged.chmod(stat.S_IMODE(readme.lstat().st_mode))
        # An intervening edit means the displayed and approved diff is stale.
        latest, _ = read_file(readme, "README.md")
        if latest != old:
            raise ApplyError("README.md changed after preview; re-preview and re-approve.")
        os.replace(staged, readme)
        staged = None
    except PreviewError as exc:
        raise ApplyError(str(exc)) from exc
    except OSError as exc:
        raise ApplyError("could not atomically replace README.md.") from exc
    finally:
        if staged is not None:
            try:
                staged.unlink(missing_ok=True)
            except OSError:
                pass
    return f"Applied README.md (SHA-256: {proposed_hash}). Consent must be verified outside this tool."


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True, help="authorized existing checkout")
    parser.add_argument("--proposal", type=Path, required=True, help="previously reviewed candidate outside checkout")
    parser.add_argument("--approved-current-sha256", required=True, help="current hash in the expressly approved preview")
    parser.add_argument("--approved-proposed-sha256", required=True, help="proposal hash in the expressly approved preview")
    args = parser.parse_args(argv)
    if not SHA256.fullmatch(args.approved_current_sha256):
        parser.error("--approved-current-sha256 must be 64 lowercase hex characters")
    if not SHA256.fullmatch(args.approved_proposed_sha256):
        parser.error("--approved-proposed-sha256 must be 64 lowercase hex characters")
    try:
        print(apply(args.root, args.proposal, args.approved_current_sha256, args.approved_proposed_sha256))
    except ApplyError as exc:
        print(f"readme_apply: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
