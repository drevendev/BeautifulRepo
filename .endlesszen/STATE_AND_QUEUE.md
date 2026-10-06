# BeautifulRepo working state

CONTROL_PROFILE: beautifulrepo-bootstrap-v1
PROJECT_STATUS: ACTIVE
SETUP_STATUS: PARTIAL
CURRENT_PHASE: maintenance tooling
CURRENT_UNIT: BR-LINKS-005
CURRENT_UNIT_STATUS: repair candidate on PR #3; fresh provider CI required; later-run acceptance follows a green unchanged head
STATE_REVISION: 4
LAST_RESULT: BR-FOUNDATION-001 and BR-VISUAL-002 are published on master; BR-LINKS-005 was retargeted to master and repaired for invalid decoded paths and invalid UTF-8 input
AUTOMATION_BINDING: resolve the single beautifulrepo-owner hourly task from its operator receipt
SCHEDULED_EXECUTION_EVIDENCE: observed through scheduled owner runs; scheduler configuration alone is not liveness proof

## Canonical recovery

`master` is the authoritative public project surface. Foundation PR #2 and visual PR #4
were merged on 2026-10-06; their GitHub-native merge/check facts remain native evidence.
The bootstrap branch is recovery history, not a current base for new work.

Current work is BR-LINKS-005 on PR #3 / branch `beautifulrepo/docs-links-20261004`,
retargeted to `master`. Resolve its current head, checks, comments and mergeability from
GitHub rather than copying drift-prone provider facts into this file.

## Next executable work

1. Let GitHub run the quality workflow for the current BR-LINKS-005 head after the master merge/reconciliation.
2. In a later run, review that unchanged head and actual provider checks; persist same-account judgment as COMMENT evidence, never independent approval.
3. If accepted and still mergeable, publish BR-LINKS-005 to master using an expected-head merge.
4. Continue the existing community-safety work only after this unit is finished or independently blocked.

## Confirmed and unverified

Confirmed: the public foundation and visual README patterns are on master; BR-LINKS-005
contains the offline checker, contributor/CI wiring and its bounded behavioral suite. The
current repair adds deterministic handling for percent-decoded NUL paths and invalid UTF-8
Markdown plus dedicated regressions.

Unverified until fresh native evidence: current PR #3 workflow result after reconciliation,
later-run acceptance for the repaired head, independent-actor approval, strict external
selection control and end-to-end ownership/fencing. Keep these unknown rather than PASS.
