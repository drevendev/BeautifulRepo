# CI failure record — copy and replace every bracketed field

> **Purpose:** One diagnostic decision for one exact CI attempt. This is not
> a parallel status dashboard, a required review policy or a substitute for
> the GitHub check and PR pages.

- **Reader impact:** [What promised behavior or integration is blocked?]
- **PR / issue:** [Native GitHub link]
- **Head and workflow:** [40-character head SHA] · [workflow URL]
- **Failed run / attempt:** [URL and attempt number; include original attempt]
- **Job / environment / step:** [exact job label, OS, runtime, first failed step]
- **Observed error:** [small redacted excerpt or direct log link]
- **Comparison:** [Which other matrix cell/attempt passed, failed, or was skipped?]
- **Hypothesis (not fact):** [suspected cause and a test that could refute it]
- **Reproduction:** [fixed command, disposable fixture, observed exit/output]
- **NOT RUN / unknown:** [what was inaccessible, skipped, or not reproduced]
- **Decision:** [REPAIR / RETRY WITH EVIDENCE / INCOMPLETE / ESCALATE]
- **Corrected head (if any):** [new SHA; never substitute an older PASS]
- **Verification:** [new-head run URL and exact job outcomes, or pending]
- **Scope / security:** [permissions, secret exposure or workflow changes?]
- **Next bounded action:** [one concrete test/fix/authorized decision]

## Example classification (fictional; not a real CI receipt)

> A Windows test fails when printing a non-ASCII filename. Ubuntu passes.
> The error is reproducible with a synthetic non-ASCII filename under an
> ASCII-constrained subprocess. **Decision: REPAIR.** Fix encoding, retain
> the failing fixture as regression, and check the changed head on Windows.
> Until that run finishes, mark Windows **PENDING**, not PASS.

For the **actual observed** Windows matrix failure and subsequent green run
in BeautifulRepo, see the [annotated CI triage case](../guides/ci-failure-triage.md#3-real-case-one-failing-windows-matrix-cell).
Never paste credentials, tokens or unredacted private logs into a public card.
