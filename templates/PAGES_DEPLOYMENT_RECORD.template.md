# Pages deployment evidence — editable record

> **DRAFT ONLY.** Delete placeholders and unsupported claims. This is not a
> verified deployment, a monitoring service or approval to change settings.
> Use [the read-only verification recipe](../guides/pages-deployment-evidence.md).

## Source and scope

- Repository: `OWNER/REPO`
- Intended full source SHA: `<40-character commit SHA>`
- Observed at (UTC and observer): `YYYY-MM-DD HH:MM UTC — <person>`
- Site publishing method: `BRANCH / ACTIONS / UNKNOWN / NOT APPLICABLE`
- Site URL (provider-reported, not guessed): `<URL or UNKNOWN>`
- Site audience: `PUBLIC / PRIVATE / UNKNOWN`

## Evidence checkpoints

For each line use **PASS / FAIL / INCONCLUSIVE / NOT RUN / NOT APPLICABLE**
and attach a dated, non-sensitive link or observation. Do not mark PASS
from a plan, template or previously green run.

- **Source revision:** `<verdict — SHA and source evidence>`
- **Build:** `<verdict — run URL, event, job conclusion, artifact if applicable>`
- **Deployment:** `<verdict — deployment ID/environment, status and observed time>`
- **HTTP/root:** `<verdict — requested and final URLs, status, time>`
- **Visible version marker:** `<verdict — exact text/evidence tied to source>`
- **First task:** `<verdict — starting URL, clicks, expected and observed result>`
- **Deep link/assets:** `<verdict — one route and asset status>`
- **Keyboard/narrow width:** `<verdict — viewport, input method, observed barriers>`
- **Failure route:** `<verdict — invalid route and helpful recovery or observed defect>`

## Decision

- Publication assessment: `VERIFIED FOR RECORDED SCOPE / FAILED / INCONCLUSIVE / NOT RUN`
- Material mismatch: `<source vs deploy vs served content, or NONE OBSERVED>`
- Smallest authorized follow-up: `<fix / verify / leave unknown>`
- Evidence limitations: `<what was not tested, e.g. real assistive technology, CDN, private viewer>`
- Reviewed by: `<person/date or NOT REVIEWED>`

**Do not call a Pages site verified merely because CI is green.**
