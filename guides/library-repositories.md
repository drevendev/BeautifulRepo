# Library repositories: make the first import trustworthy

A library repository is useful when a reader can identify its public API, execute a
minimal call, see a representative result, and distinguish a local source checkout
from a published package. A badge, import statement, or package name alone is not
proof of installability.

## The five-minute path

1. **Promise:** say what problem the library solves, its supported language/runtime,
   and one important limit. Avoid broad claims such as "production-ready" without evidence.
2. **Public API:** show the real import name and exact call signature. State whether
   the example runs against a source checkout, an installed wheel, or a CDN build.
3. **First result:** show expected output and a command to reproduce it. Verify this
   against the checked-in implementation in CI; never treat a screenshot as the only result.
4. **Compatibility:** publish only versions, platforms, or dependency ranges actually
   exercised. Keep minimum supported runtime distinct from the runner used in CI.
5. **Trust:** link to license, development/testing commands, breaking-change policy,
   support route, and actual release history. Absence of a release should be explicit.

## A working checkout-only example

The [library starter](../examples/library-starter/README.md) includes a single-file
Python module, a shell-agnostic runnable first call, and black-box tests. From
the repository root:

```bash
python examples/library-starter/demo.py
python -m unittest discover -s examples/library-starter/tests -v
```

Its API is intentionally simple, but the call, expected output, and invalid-input
behavior are checked. **It is not a published distribution.** Do not advertise
`pip install` for this example or claim a package is on PyPI.

## README anatomy for a genuine published library

Keep the first screen compact: outcome, one working import, expected result, then
installation (only when actually available), compatibility, and links to reference
material. Put exhaustive API detail in a dedicated guide; link it with relative paths.

When a distribution is published, confirm three separate facts before documenting it:

- **Distribution name:** the name the package index accepts for installation.
- **Import name:** the actual module or namespace imported in code; it may differ.
- **Published artifact:** a verified wheel/source archive and supported version.

Do not infer these facts from a folder name or a `pyproject.toml` draft. Verify the
install command in an isolated environment and check the built artifact, not just
imports made possible by running inside the repository root.

Start from the [library README template](../templates/LIBRARY_README.template.md)
and remove sections that are not applicable rather than leaving decorative blanks.

## Test the claims, not the formatting

At minimum, CI should execute the documented first call, assert output/error behavior,
exercise the supported runtime matrix, and check internal documentation links. A
structural README test is useful against accidental route regressions but does not
prove packages were published or accessibility was certified.

## Sources and applicability

Reviewed **2026-10-11**:

- [GitHub: About READMEs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes) — visitor goals and relative links.
- [Google Style Guides: READMEs](https://google.github.io/styleguide/docguide/READMEs.html) — package-level onboarding and documentation pointers.
- [Python Packaging User Guide](https://packaging.python.org/en/latest/) — distinguish packaging guidance from a checked-out module example.

This is a Python-focused example, not a universal packaging recipe; npm, Rust,
Java and other ecosystems have different import and distribution conventions.
