## Reader problem and change

Explain the improvement and link the relevant issue when there is one.
For unfinished work, use `Related: #<issue-number>` and describe what remains.
Only use an issue-closing keyword when the PR actually completes that issue.

## Evidence

Name primary sources, inspected revisions and any reuse permissions that matter.

## Verification

- [ ] Local Python verification passed: `python -I scripts/verify_checkout.py`
      (see [CONTRIBUTING](https://github.com/drevendev/BeautifulRepo/blob/master/CONTRIBUTING.md#verify-a-change-locally)).
      Record exact commands and results below; leave unchecked if incomplete.
- [ ] If the catalog changed, its generated view was regenerated and the diff reviewed.
- [ ] Documentation links and examples were inspected.
- [ ] Accessibility and visual checks actually performed are described, not assumed.

Local verification is not the hosted CI matrix, Action self-tests or lint job.
Record actual hosted results separately when available.

## Limitations

Separate not-run checks, source-only observations and remaining work from verified results.
