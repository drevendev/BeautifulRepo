# Rowcount: two truthful first screens

**Design exercise on working code, not a released package.** Both presentations refer to
the same [Rowcount CLI](../../cli-starter/README.md), sample input and observed output.
Choose a first-screen hierarchy for the reader; do not change the facts to fit the layout.

The source was inspected at BeautifulRepo commit
[`1db96d552d4e2ba6e9893cbd348d8f67eb3507fe`](https://github.com/drevendev/BeautifulRepo/commit/1db96d552d4e2ba6e9893cbd348d8f67eb3507fe).
The checked-in sample contains a header and three data records. This example
uses Python 3.11+ and no third-party dependencies.

## Two distinct presentations

- [Editorial](editorial.md): purpose and local-data boundary first, then the runnable command.
- [Terminal-led](terminal-led.md): a labelled illustration of the verified result first,
  followed immediately by the actual checkout command and limitations.

Both preserve this exact reproducible first success, run **from the repository root**:

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

| Choice | Editorial | Terminal-led |
| --- | --- | --- |
| Reader | Someone deciding whether the command addresses their CSV task | Someone looking for a quick verification signal |
| First question | What problem does this solve? | What happens when I run it? |
| Visual device | Text hierarchy with no hero artwork | Small original theme-aware transcript illustration |
| Risk | Feels too quiet without a product demo | A terminal graphic could obscure prerequisites |
| Mitigation | Copyable command and precise output remain above the fold | Complete text command, stdout and limitations remain outside the SVG |

The artwork has separate light/dark palettes, embedded `title` and `desc`,
a meaningful HTML `alt`, and nearby plain-text equivalents.
Review the GitHub-rendered Markdown manually at narrow widths and in both themes;
the source tests do not certify renderer behavior, contrast or screen-reader output.
The original [design-intent method](../DESIGN_INTENT.md) is reusable; these
Rowcount source/output facts, not PocketDiff's fictional numbers, are the evidence.

Related: [visual README guide](../../../guides/readme-visuals.md).
