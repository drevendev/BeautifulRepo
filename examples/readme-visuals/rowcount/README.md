# Rowcount: three truthful first screens

**Design exercise on working code, not a released package.** All three presentations refer to
the same [Rowcount CLI](../../cli-starter/README.md), sample input and observed output.
Choose a first-screen hierarchy for the reader; do not change the facts to fit the layout.

The source was inspected at BeautifulRepo commit
[`1db96d552d4e2ba6e9893cbd348d8f67eb3507fe`](https://github.com/drevendev/BeautifulRepo/commit/1db96d552d4e2ba6e9893cbd348d8f67eb3507fe).
The checked-in sample contains a header and three data records. This example
uses Python 3.11+ and no third-party dependencies.

## Three distinct presentations

- [Editorial](editorial.md): purpose and local-data boundary first, then the runnable command.
- [Terminal-led](terminal-led.md): a labelled illustration of the verified result first,
  followed immediately by the actual checkout command and limitations.
- [Contract-first](contract-first.md): a scannable input/output and validation
  boundary card before the same reproducible command.

All three preserve this exact reproducible first success, run **from the repository root**:

```bash
python examples/cli-starter/rowcount.py examples/cli-starter/sample.csv
```

Verified stdout:

```text
Data rows: 3
```

An alternate, equivalent run from `examples/cli-starter` is
`python rowcount.py sample.csv`. The SVGs draw that shorter, real invocation;
they are **illustrations of text**, not screenshots of GitHub, a terminal session
or a shipped product. They show no simulated metrics other than this observed result.

## Design intent and trade-offs

- **Editorial — task fit:** asks what the local command solves before showing a
  runnable result. Risk: may feel too quiet; mitigation: early copyable command.
- **Terminal-led — verification:** shows the same observed result through a small,
  original theme-aware illustration. Risk: artwork hides the real command;
  mitigation: the complete text command and output sit outside the image.
- **Contract-first — technical boundaries:** leads with a compact behavior table
  for readers checking assumptions about headers, blanks and malformed widths.
  Risk: feels too much like reference documentation; mitigation: the actual
  checkout command and observed output immediately follow the table.

Only terminal-led uses paired light/dark SVGs for desktop and narrow widths,
with embedded `title` and `desc`, meaningful HTML `alt` text and nearby
selectable equivalents. Compact art preserves the command and result without
shrinking the desktop transcript to tiny text.
Review the GitHub-rendered Markdown manually at narrow widths and in both themes;
the source tests do not certify renderer behavior, contrast or screen-reader output.
The [filled Rowcount design-intent brief](DESIGN_INTENT.md) records the
trade-offs and verification limits for all three variants. Use the
[blank design-intent template](../../../templates/DESIGN_INTENT.template.md)
for your own product rather than copying this visual identity.
The original [PocketDiff design-intent exercise](../DESIGN_INTENT.md) uses
fictional numbers, whereas this Rowcount comparison uses actual CLI output.

Related: [visual README guide](../../../guides/readme-visuals.md).
