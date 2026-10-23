# 0006: No contact route, promise or policy is published before it works

- **Date:** 2026-10-08
- **Landed in:** [#6](https://github.com/drevendev/BeautifulRepo/pull/6), applied in [#94](https://github.com/drevendev/BeautifulRepo/pull/94)
- **Status:** accepted

**Context.** A handbook about trustworthy repositories can't advertise a security
inbox, conduct process or response time that nobody operates. A policy file that
exists only to tick a checklist box misleads exactly the reporter who needs it.

**Decision.** A route is published only once it is verified to work end to end.
`SECURITY.md` went live with GitHub's private vulnerability reporting enabled and a
named triager, and it promises no response time. There is no
`CODE_OF_CONDUCT.md` until a private conduct channel and an enforcement owner
exist; until then CONTRIBUTING points sensitive abuse to GitHub's platform reporting.

**Consequences.** Community checklists show an honest gap instead of a hollow pass.
Templates and examples may contain placeholders, but BeautifulRepo's own files may
not.
