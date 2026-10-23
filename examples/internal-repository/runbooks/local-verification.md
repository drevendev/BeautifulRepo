# Sample Queue — local verification runbook

This is a fictional, offline example; there is no production queue or on-call team.

## Reproduce

From the BeautifulRepo root with Python 3.11+:

```sh
python -I examples/internal-repository/verify_example.py
```

Expected output: `Sample records: 2` and exit code 0.

## If the check fails

1. Confirm the interpreter is Python 3.11+ with `python --version`.
2. Confirm `sample_records.json` and `verify_example.py` are present in
   the [example directory](../README.md).
3. Restore changed fixture values from the reviewed checkout and rerun.
4. If adapting this for a real internal project, escalate through its
   **verified** contact process rather than the fictional channel above.

Do not paste internal logs, tokens or unredacted paths into public issues.
Use the [confidentiality checklist](../../../checklists/confidentiality.md)
before sharing findings.
