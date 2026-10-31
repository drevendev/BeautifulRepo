# Entry-point audit rule reference

This is the complete rule-ID index for the offline [repository entry-point audit](../tools/repo_audit.py) at the time of review (**2026-10-31**, `master` at `b21b022`). It describes **source observations**, not an accessibility certificate, a license verdict, or a promise that these identifiers will never change.

Run `python tools/repo_audit.py . --format json` and inspect each `findings[].rule_id`. Every finding also includes severity, relative path, optional source line, message, and remediation. The [audit guide](repository-audit.md) explains input limits, profile behavior, thresholds and the JSON contract.

The severity shown applies to `--profile public` unless another profile is noted. **Error** fails the default `--fail-on error` threshold; **warning** is advisory by default but fails `--fail-on warning`; **info** never triggers a threshold failure. An invalid target or incomplete inventory instead causes exit code 2, **without** a finding ID.

## Selected documents and filesystem

The audit selects at most one README, license and contribution document using its documented local precedence. These rules apply to the selected document or to an entry-point directory, not a recursive repository scan.

| Rule ID | Severity | When it is emitted |
| --- | --- | --- |
| `readme.missing` | error | No supported README in root, `.github`, or `docs`. |
| `license.missing` | warning (public); info (internal/private) | No root-level `LICENSE`, `LICENCE`, or `COPYING` candidate with a recognized suffix. Not a conclusion about license rights. |
| `contributing.missing` | info | No supported dedicated CONTRIBUTING file; an intentional alternative may exist. |
| `readme.empty` | error | Selected README contains no non-whitespace text. |
| `license.empty` | warning | Selected dedicated license file contains no non-whitespace text. |
| `contributing.empty` | warning | Selected CONTRIBUTING file contains no non-whitespace text. |
| `path.symlink` | warning | An entry-point directory is a symlink or Windows junction; it was not traversed. |
| `path.non_regular` | error | A selected document is a symlink or other non-regular file; it was not read. |
| `document.too_large` | error | A selected document exceeds the 500 KiB read limit. |
| `document.encoding` | error | A selected document cannot be decoded as UTF-8 or contains NUL bytes. |
| `document.unreadable` | error | Reading a selected document raises an operating-system error. |

## README content checks

These checks inspect a nonempty **Markdown** README (`.md` or `.markdown`) using a deliberately limited parser, except where the table says otherwise.

| Rule ID | Severity | When it is emitted |
| --- | --- | --- |
| `readme.unsupported_format` | info | A nonempty README was found in another supported text format; Markdown-specific rules were not run. |
| `readme.title` | warning | No supported nonempty level-one heading was found. |
| `heading.skipped_level` | warning | The detected heading order jumps over a level. |
| `heading.multiple_titles` | info | Another detected level-one heading follows the first. |
| `table.empty_headers` | warning | A pipe table's header cells are all empty in the supported syntax. |
| `readme.placeholder` | warning | A visible uppercase TODO/TBD/FIXME or `{{PROJECT_NAME}}`-style token appears outside supported code/comments. |
| `link.vague_text` | info | A simple inline Markdown link uses a context-dependent label such as “here” or “read more”. Its surrounding context is **not** assessed. |
| `readme.absolute_repo_asset` | warning | A supported Markdown or HTML image points to a recognized GitHub raw-file URL instead of a checkout-relative asset. |
| `image.missing_alt` | warning | An HTML `<img>` has no `alt` and no supported explicit naming/decorative marker. |
| `image.empty_alt` | info | A supported Markdown or HTML image has empty alternative text; this may be correct for decoration. |
| `image.duplicate_attribute` | warning | An HTML `<img>` repeats `alt`, `src`, `role`, `aria-label`, `aria-labelledby`, or `aria-hidden`. The first value controls the audit. |
| `readme.owner_contact` | warning (internal/private only) | A selected nonempty README has no recognizable owner, maintainer, contact or support heading/labelled field. The tool does not verify that any route is real or reachable. |

The Markdown checks ignore the supported fenced/inline code and HTML-comment regions, but **do not** implement the full GitHub Markdown renderer. The link-label heuristic ignores destinations longer than 2,048 characters; the HTML-image rules do not compute the final accessible name.

## Examples, verification and boundaries

- [Executable before/after example](../examples/repository-audit/README.md) — explains which findings remain after an illustrative README repair.
- [Audit behavior and profile tests](../tests/test_repo_audit.py) — covers missing and empty documents, profile-specific findings, images, headings, source limits and reported lines.
- [Code-span regressions](../tests/test_audit_code_spans.py) and [bounded-scanning tests](../tests/test_scan_bounds.py) — guard supported literal-region handling and parser limits.
- [Rule-index coverage test](../tests/test_audit_rule_index.py) — compares the documented ID rows with the `finding()` call sites and their three document-kind variants. It is a **source-level consistency check**, not proof that every rule triggers under all operating systems or renderer conditions.

The table lists **all 23 IDs** emitted by this implementation, not every possible failure mode. In particular, directory inventory exhaustion and invalid CLI inputs are exit-code-2 input errors, not hidden finding IDs. To inspect how and when an ID is detected, read [the implementation](../tools/repo_audit.py) alongside the [audit guide](repository-audit.md). Do not use this diagnostic alone to block accessibility, license or security decisions.
