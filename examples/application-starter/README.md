# Pocket Board — a read-only application repository starter

> **Preview only:** a fabricated task board, served on local loopback. It is not
> deployed, does not store user data, and has no authentication, cookies,
> outbound telemetry, build service or production security review.
> The development server still prints local HTTP access logs.

## What the application does

Five invented tasks are displayed as cards. The reader can filter **All / Open / Done**
using a native HTML form, with no JavaScript required. The server recomputes the
number of visible tasks and their total effort points. These points are fictional
estimates, not hours or any observed metrics.

**Expected first success:** the unfiltered page shows **5 tasks, 15 effort points**.
Choosing **Open** shows 3 tasks with 12 points; **Done** shows 2 tasks with 3 points.
The URL is `/?status=open` or `/?status=done` after submitting the form.
The local `/health` route returns `200 OK` when both the sample data and
stylesheet can be read, or `503 Service Unavailable` if either is unavailable.
It is a tiny demo readiness check, **not** proof of production health, uptime,
security or any externally deployed service.

## Run locally

Verified in **Python 3.13.5 on 2026-10-16**, standard library only.
From `examples/application-starter`:

```bash
python app.py --port 8000
```

Then open `http://127.0.0.1:8000/` in a browser. Stop with `Ctrl+C`.
If that port is busy, choose another local port. The server listens only on
`127.0.0.1`; do not expose it on a public interface or reverse proxy.

From the **repository root**, run the unit and integration checks (including one
short-lived loopback HTTP server):

```bash
python -m unittest discover -s tests -v
```

The root test suite includes this example's unit/integration checks. Individual
example files can also be explored without a package installation.

## Where to look

- [`app.py`](app.py): small WSGI application and explicit local preview entry point.
- [`data/tasks.json`](data/tasks.json): invented, checked-in, read-only example data.
- [`style.css`](style.css): responsive light/dark presentation and keyboard focus.
- [`../../tests/test_application_starter.py`](../../tests/test_application_starter.py): fixture, route and error-path tests.

## What is and isn't checked

Most tests invoke the WSGI handler directly. One additional integration test
opens an ephemeral `127.0.0.1` listener and verifies real HTTP responses for
the task board, stylesheet and health endpoint without external network access.
The suite checks route/filter responses, predictable summaries, unsafe sample-data
rejection, escaping, generic missing-asset error responses, basic security headers, failure-aware local readiness checks
and no writes to the input fixture.
This does **not** validate screen-reader interoperability, visual contrast on every
display, browser support, WSGI server hardening or real production traffic.

### Rendered keyboard, contrast and reflow check (2026-10-23)

The running app (`python app.py --port 8765`) was checked once by hand in Chrome 152,
the browser built into the Claude desktop app. Widths and colour schemes were set by
viewport emulation, and colours and layout were measured in the page. These are not
screenshots of real devices.

| Check | Light | Dark |
| --- | --- | --- |
| Status `select` border against the panel | 4.5:1 | 4.9:1 |
| Focus outline (about 3 px, solid) against its background | 5.3–5.8:1 | 8.9–10.4:1 |
| Body / muted text against the background | 15.0:1 / 7.0:1 | 15.1:1 / 9.3:1 |
| Sideways page scroll at 375 px and 320 px | none | none |

- Tab moves through the skip link, which appears when focused, then the "Pocket
  Board" link, the status filter and the button. Each shows the outline.
- Arrow keys change the filter and Enter on the button applies it. The chosen value
  stays selected after the page reloads.
- At 320 px, about 400% zoom of a 1280 px window, the header wraps and long task
  titles break inside their cards.
- The dropdown keeps the browser's native arrow (`appearance: auto`); its drawing was
  not measured.
- `tests/test_workshop_hardening.py` keeps the colour pairs above at 3:1 for
  boundaries and focus, and 4.5:1 for text.

**Not checked:** screen readers, Windows high-contrast or other forced-colours modes,
real phones, browsers other than Chrome, and real 400% browser zoom.

The implementation uses the `wsgiref` reference server. Python explicitly warns
that it is **not recommended for production**. It is appropriate here only to
demonstrate a local first-success route with no third-party dependencies.

The fictional data is included under BeautifulRepo's [MIT license](../../LICENSE).
No real user/customer data was used to make it. See the
[application repository guide](../../guides/application-repositories.md) for a
practical checklist on demo fidelity, onboarding, health checks and limits.
