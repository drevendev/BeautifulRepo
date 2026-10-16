# Slugline — a checkout-only library example

A deliberately small Python module turns ASCII phrases into predictable URL
slugs. It rejects non-ASCII input rather than pretending to transliterate it.

**Availability:** included in this repository as source; **not published on PyPI**.
No third-party dependencies or installer are required.

**Verified runtime:** Python 3.13.5 on 2026-10-11. This example has not been
verified against older Python versions or other operating systems.

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

Run tests from the repository root:

```bash
python -m unittest discover -s examples/library-starter/tests -v
```

The public API is `slugline(text: str) -> str`. It raises `TypeError` for non-strings
and `ValueError` for non-ASCII or empty/non-alphanumeric ASCII input. It does not
support transliteration or language-specific casing.

See the [library repository guide](../../guides/library-repositories.md) for how to
present real distributed packages and [MIT license](../../LICENSE) for source terms.
