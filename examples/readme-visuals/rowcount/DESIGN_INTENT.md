# Rowcount: a design-intent decision from actual code

**Scope:** three alternative Rowcount README first screens:
[editorial](editorial.md), [terminal-led](terminal-led.md) and
[contract-first](contract-first.md).
Both describe a checkout-only example, **not** a released Python package.
This is a filled application of the
[reusable design-intent template](../../../templates/DESIGN_INTENT.template.md),
not an endorsement of a single visual style.

## Scope and reader

The editorial reader wants to know whether a local CLI solves the right CSV
counting task and what it will *not* validate. The terminal-led reader wants
to see a concrete output before reading implementation details. The
contract-first reader checks input assumptions and failure behavior first.
All three need a copyable first success and a truthful local-data boundary.

**One-sentence promise:** count nonblank data records after a CSV header,
locally, and print a single number.

**Constraints:** Python 3.11+, Git checkout, standard library only, no network
service; illustrative media must not replace the executable command.

## Evidence boundary

- **Verified fixture and code:** the actual
  [sample.csv](../../cli-starter/sample.csv) and
  [rowcount.py](../../cli-starter/rowcount.py) at
  [BeautifulRepo commit `1db96d552d4e2ba6e9893cbd348d8f67eb3507fe`](https://github.com/drevendev/BeautifulRepo/commit/1db96d552d4e2ba6e9893cbd348d8f67eb3507fe).
- **Reproduction from repository root:**
  `python examples/cli-starter/rowcount.py examples/cli-starter/sample.csv`.
  The fixture has one header and three data records; observed stdout is
  `Data rows: 3`. The existing
  [black-box test](../../../tests/test_rowcount_visual_evidence.py)
  checks both documented invocations on the installed Python interpreter.
- **Illustrative assets:** [light](rowcount-light.svg) and
  [dark](rowcount-dark.svg) are original **SVG drawings of a transcript**,
  not screenshots of GitHub, a terminal, a deployed app or a measured user
  session. Both show the shorter invocation from `examples/cli-starter`.
- **Limits:** the CLI is not a CSV schema, dialect or type validator. These
  tests do not demonstrate screenshot fidelity, a package install,
  browser rendering, user preference or accessibility certification.

## First-screen alternatives

1. **Editorial:** job and privacy constraint → prerequisite → real command →
   observed result → input and validity limits. Best when the reader is deciding
   if the tool fits their task. Cost: fewer visual cues at a glance.
2. **Terminal-led:** labeled transcript drawing → identical real command and
   stdout in selectable text → prerequisites → limits. Best when quickly
   checking what the command produces. Cost: a decorative-looking graphic could
   delay discovery of the actual command unless the text stays adjacent.
3. **Contract-first:** count/validation boundary table → identical real
   command → observed result → source and errors. Best when evaluating whether
   a small tool's assumptions fit existing data. Cost: a table can feel dense
   and reflow poorly; keep it to two short columns and inspect narrow widths.

No variant is universally superior. Keep the same facts, limitations
and navigation in all three; test with actual users before claiming a preference.
The full command and output remain understandable with images disabled.

## Visual and interaction decisions

- **Hierarchy:** one headline, a compact specific promise, and an early
  first-success path instead of a badge wall or abstract gradient.
- **Contract-first:** compact semantic Markdown table, no extra graphic or
  third-party visual library. Input and output facts remain selectable text.
- **Theme:** two local SVG colour variants selected with HTML `picture`;
  labels and values stay identical, with a default `img` fallback.
- **Alternative text:** the HTML image describes the command and result.
  Nearby selectable text repeats them, rather than relying on SVG colours.
  Embedded SVG `title` and `desc` provide additional source metadata.
- **Width and zoom:** the example uses normal Markdown flow and a local image.
  Narrow-width GitHub rendering and 400% zoom were **not tested** for these three
  variant pages; source-level assertions cannot establish reflow.
- **Provenance:** original SVGs stored in this repository, no third-party brand
  assets, fonts, animation, CDN or JavaScript.
- **Maintenance trigger:** rerun the fixture and revise both pages and SVG
  transcript if Rowcount arguments, printed result or data semantics change.

## Rejected approaches

- **Fabricated speedup, user counts or screenshots:** no measurement or
  deployed UI exists to support them.
- **Image-only output:** excludes readers who disable images or need to copy
  the command; the result must remain real text.
- **Generic product-landing hero:** steals the first screen from the one
  thing this tiny CLI can actually demonstrate.

## Verification and decision

**Source-verified, 2026-10-26:** the documented command, output, theme labels,
fallback alt text and linked files were inspected at the above named source
revision and in the three-page README comparison. Source contract:
`python -m unittest discover -s tests -p test_rowcount_visual_evidence.py -v`
(run from a checkout). The prior PR's GitHub CI checks are provider evidence; **no new
local test run, browser visual inspection or model evaluation is claimed
by this brief**.

**Manual checks still required:** GitHub's actual rendering in both themes at
desktop/375 px/320 px, images-off reading order, keyboard/focus, screen
reader, real 400% zoom and contrast. Until those are performed, the safe
decision is to **publish as three inspectable source-backed alternatives**, not
to recommend a winning visual design or certify either presentation.

Method: [README visual guidance](../../../guides/readme-visuals.md) and
[W3C image alternatives](https://www.w3.org/WAI/tutorials/images/).
