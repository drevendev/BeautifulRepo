# PatchPitch: an offline first success for a local-AI app

**Case status, 2026-10-23:** complete. The change merged through PatchPitch's own pull
request, and the documented first run was repeated from a fresh clone of the merge
commit. The model, the X composer, Linux and macOS, and real devices were not tested.

## Target and revisions

- Repository: [drevendev/PatchPitch](https://github.com/drevendev/PatchPitch), licence
  MIT, so short quotations below are attributed to it.
- Before: `1424fc8fbfef82a5cd473272843e0c5cdc097b36` (observed 2026-10-23). Issue
  [#81](https://github.com/drevendev/BeautifulRepo/issues/81) recorded `44ca597` on
  2026-10-22. One commit adding demo media landed in between, and none of the findings
  changed.
- Change: [PatchPitch#90](https://github.com/drevendev/PatchPitch/pull/90), branch
  commit `df50116`. After: merge commit
  `43284a7286ead07d37ff32b8206ac4000856fd04` (2026-10-23).
- BeautifulRepo tools: `4f06f26ccef6e8b28d77c71633482b7a1a68518a` (v0.2.0), run with
  `python -I` and an explicit root, per the [case procedure](README.md).

## Before

**Metadata.** Description "Turn selected changelog facts into a source-linked
announcement draft with local Gemma." No topics, no homepage, no releases or tags.
Private vulnerability reporting off (`enabled: false`). No branch protection. Pull
requests come from agent branches, but one commit went straight to `main`.

**Tools.** `repo_audit.py`: 0 errors, 0 warnings, 1 informational finding
(`contributing.missing`). `docs_links.py` and `html_navigation.py`: clean, 7 of 7
destinations.

**Checklist findings** (obstacle → reader → smallest fix → verification):

1. The "Run locally" section opens with the 0.2.0 review-candidate story
   (README:16-53), then "From the root of an already prepared Windows checkout"
   (README:54). → A first-time visitor can't tell where to start. → Lead with a
   first run and move the candidate details to `docs/`. → The first heading after the
   promise is a runnable path.
2. The only clean setup (README:84-92) installs Ollama and pulls `gemma4:12b`, a
   download of several GB. Yet loading a fact pack "never runs inference" (README:26).
   → A visitor without a model can't try the app at all. → Document a run without
   Ollama, with the exact messages. → A fresh clone with Ollama stopped shows them.
3. The Python requirement reads "install Python 3.12" (README:65) and "Python 3.11+"
   (README:84). → Readers on 3.11 can't tell whether it is supported. → One statement.
   → A grep finds one wording.
4. No CONTRIBUTING and no SECURITY file. Private reporting is off. → Contributors and
   reporters have no route. → Add both, and enable private reporting before the
   security route is advertised. → The audit detects CONTRIBUTING. The route resolves.

## Changes and trade-offs

[PatchPitch#90](https://github.com/drevendev/PatchPitch/pull/90) changes
documentation only:

- **"Try it" comes first.** The recorded demo, then a clean clone for Windows and
  Linux/macOS that runs without Ollama. The README quotes the app's real messages.
  The trade-off is that the 0.2.0 details are one click further away.
- **"Generate with local Gemma" follows**, with the model pull and the existing
  settings. Python reads "3.11+ (tested with 3.12)" everywhere.
- **Moved, unchanged:** the Social Field Test details and live-evidence steps go to
  `docs/social-field-test.md`; the prepared-workspace launcher goes to the demo
  tooling section.
- **CONTRIBUTING.md and SECURITY.md.** The security scope is drawn from the README's
  own guarantees: loopback only, Ollama at `127.0.0.1:11434`, the Git importer's
  limits and the Sentry allowlist. Merging waits for the owner to enable private
  vulnerability reporting, so the route exists when it is advertised.
- **Not changed here:** topics are a setting for the owner, and the PR suggests five.
  They were still unset at the after snapshot.

On the branch, the same pinned tools report 0 errors, 0 warnings and 0
informational findings, with CONTRIBUTING detected. Links and anchors are 13 of 13,
including the new `#try-it`. PatchPitch's own CI on the pull request passed:
`pytest -q`, 277 passed
([run 39941275194](https://github.com/drevendev/PatchPitch/actions/runs/39941275194)).

## First run without a model (observed)

On 2026-10-23, in a fresh clone at `1424fc8`, on Windows 11 with Python 3.13 and
Ollama not running:

- `pip install -r requirements.txt` installed FastAPI 0.146.0 and Pydantic 2.14.1.
- `uvicorn patchpitch.app:app --host 127.0.0.1` started, and `/api/health` returned
  `"ollama": "ollama_unavailable"`.
- Under **Reviewed fact packs**, **Load facts** answered "Facts loaded. Review the
  selected notes before generating." It showed 8 facts selected, 1 excluded, and the
  pack `patchpitch / public-workflow-v1`.
- **Write the announcement**, after the confirmation box was ticked, showed the alert
  "Ollama is not reachable at 127.0.0.1:11434. Start Ollama and try again." The input
  was kept.

The pull request documents exactly these messages. Application code is unchanged.

## Rendering at 320 px (measured)

GitHub-independent: the running app in Chrome 152's viewport emulation.

- **Light:** no sideways page scroll. The heading is 10.3:1 and the **Load facts**
  button 11.8:1. Fourteen small helper texts fall below 4.5:1: muted 8-10 px labels at
  4.3-4.47:1, and the "local files" and "local repository" hints at 2.98:1 (14 px).
- **Dark:** the app has one light palette. With `prefers-color-scheme: dark` it renders
  the same colours, and the same 14 texts fall below 4.5:1.

These are findings about PatchPitch's interface, outside this documentation change.
They belong in a separate PatchPitch issue.

## After

Snapshot of 2026-10-23, after the merge.

- **Metadata:** private vulnerability reporting is on (`enabled: true`), so the route in
  `SECURITY.md` exists. Description and licence are unchanged, and there are still no
  topics.
- **Tools** (the same v0.2.0 commit, on a fresh clone of `43284a7`): `repo_audit.py`
  0 errors, 0 warnings, 0 informational findings, with `CONTRIBUTING.md` detected.
  The before run had 1 informational finding. Links and anchors: 13 of 13.
- **First run, following the new README word for word:** in a fresh clone of the
  merge commit, on Windows 11 with Python 3.14.7 and Ollama not running.
  `python -m venv .venv`, then `.venv` pip install and uvicorn on port 8000.
  - `/api/health` reported `ollama_unavailable`.
  - **Load facts** showed "Facts loaded. Review the selected notes before generating."
    with 8 selected and 1 excluded.
  - **Write the announcement** showed "Ollama is not reachable at 127.0.0.1:11434.
    Start Ollama and try again." and the status "Your input and any previous draft
    are still here."

  Every message matched the README.
- **Rendering at 320 px:** the same as before, as expected for a documentation-only
  change. There is no sideways scroll, a single light palette in both colour schemes,
  and 14 of 33 texts below 4.5:1 (minimum 2.98:1).
- **CI** on the merge commit: `pytest -q`, 277 passed
  ([run 39945177303](https://github.com/drevendev/PatchPitch/actions/runs/39945177303)).

## What changed for a reader

Before, the README gave a visitor without a several-GB local model no way to try
PatchPitch locally, although the app already worked without one, and its first
section described a review candidate. After, the first section gets them to
a running app with real fact packs in a few commands, and states exactly what they
will see without a model. The model setup follows. Contributors and security
reporters have documented routes, and the security route works. The application
itself did not change, and its contrast and dark-mode findings remain open.

## Not tested

- Live model quality and the X composer, as #81 requires.
- `pytest -q` locally. The Playwright browser download was skipped; CI on the pull
  request and on the merge commit is the test evidence.
- Screenshots: the app window was hidden during the session, so the 320 px results
  are in-page measurements with the text equivalents above, not images.
- The Linux and macOS commands, real phones and screen readers.
