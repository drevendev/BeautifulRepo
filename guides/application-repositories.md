# Application repositories: prove the first user journey

Application README pages should give visitors a **real result and a working path to it**,
not a marketing screenshot that can no longer be reproduced. Unlike a small library,
an application needs to explain its runtime, lifecycle and data boundary as well
as installation or build commands.

## A useful first screen

1. **Purpose:** name the user, problem and visible result, without broad superlatives.
2. **Evidence:** show a *current* screenshot, text alternative, or actual first-run
   output, dated and tied to a revision. If no screenshot has been captured, do not
   substitute an imaginary image or badge.
3. **Safe local start:** list the required runtime, the actual launch command,
   where it listens, and what credentials/data (if any) are needed.
4. **First interaction:** tell a newcomer exactly what to click or request, and
   the expected state change; provide a text-first route.
5. **Data and trust:** say what is persisted, where it is stored, and which external
   services or outbound calls exist. Do not call a demo "privacy safe" merely
   because it runs on localhost.
6. **Tests and limits:** separate unit, HTTP integration, browser, accessibility,
   deployment and production security validation. Do not imply tests you did not run.

## Small verified example

[Pocket Board](../examples/application-starter/README.md) is a local-only, read-only
application with five invented tasks, server-rendered HTML and a native status filter.
The example works without client-side JavaScript, cookies, a third-party package or
an external API. Most WSGI tests run in memory; one real HTTP integration test
starts a temporary loopback listener and shuts it down afterwards. Its
`/health` check reports local fixture/stylesheet availability, not a production
readiness, monitoring or uptime guarantee.

From its directory:

```bash
python app.py --port 8000
```

Visit `http://127.0.0.1:8000/` and select **Open**: three tasks, 12 fictional
points. **Done** shows two tasks, three points. The sample is never modified.
This is a deliberately small example of a *repository onboarding path*, not a
production architecture template or an endorsement of `wsgiref` for deployment.

## Before calling it production-ready

Document actual deployment topology, backup/restore, data retention, failure modes,
authentication/authorization, CSRF and request-size handling, dependency update
policy, supported runtimes and security reporting **only where implemented**.
Adding headings is not evidence that these capabilities exist. Production servers
need a deliberately chosen deployment stack and security review; this tutorial
neither configures nor endorses one.

For a substantial application, maintain navigation from the first screen to a
user guide, contribution route, developer setup, architecture overview, known
limitations, release notes and supported runtime matrix. Avoid information that
gets silently stale, such as unverified uptime or maintenance guarantees.

## Accessibility, screenshots and communication

Use native form elements and visible labels, keyboard-operable controls, readable
focus states and text equivalents for media. Color cannot be the only way to
communicate status. Keep text alternatives useful even if CSS and images fail.
Light/dark theming is optional; do not claim full accessibility certification
from a static lint pass. Test the actual browser and assistive technologies for
real deployments.

## Primary references and scope

Reviewed **2026-10-16**:

- [GitHub: About READMEs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes)
  — repository entry points and relative navigation.
- [Python: `wsgiref` reference server](https://docs.python.org/3.13/library/wsgiref.html)
  — WSGI contracts and explicit non-production warning.
- [W3C WAI: Labeling Controls](https://www.w3.org/WAI/tutorials/forms/labels/)
  — native controls, associated visible labels and understandable submit buttons.

This guide describes general repository documentation practice; it is not a
security, accessibility, privacy, deployment or compliance certification.
