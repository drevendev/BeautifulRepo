# Slugline — a checkout-only library example

A deliberately small Python module turns ASCII phrases into predictable URL
slugs. It rejects non-ASCII input rather than pretending to transliterate it.

**Availability:** included in this repository as source; **not published on PyPI**.
No third-party dependencies or installer are required.

**Verified runtime:** the [2026-11-27 Quality CI run](https://github.com/drevendev/BeautifulRepo/actions/runs/45927765999)
passed the nested API tests and demo on Python 3.11 and 3.14 on Linux, and
3.14 on Windows. This is checkout evidence, not a published package's support
policy or a promise about every intermediate version.

The public API is a plain import:

```python
from slugline import slugline
print(slugline("Hello, Library 101!"))
```

To reproduce the result without shell-specific quote escaping, run this command
from `examples/library-starter`:

```bash
python demo.py
```

Expected output:

```text
hello-library-101
```

## Handle a rejected value

The API rejects non-ASCII input rather than silently losing characters. Catch
the exception where a caller can decide what to do next:

```python
from slugline import slugline

try:
    slugline("café")
except ValueError as exc:
    print(f"{type(exc).__name__}: {exc}")
```

Expected output:

```text
ValueError: text must be nonempty ASCII
```

Both displayed Python calls and their outputs are exercised by the root
integration suite. The exception handling belongs to the caller, not the
library; an uncaught exception would behave differently.

Run tests from the repository root:

```bash
python -m unittest discover -s examples/library-starter/tests -v
```

The public API is `slugline(text: str) -> str`. It raises `TypeError` for non-strings
and `ValueError` for non-ASCII or empty/non-alphanumeric ASCII input. It does not
support transliteration or language-specific casing.

See the [library repository guide](../../guides/library-repositories.md) for how to
present real distributed packages and [MIT license](../../LICENSE) for source terms.
