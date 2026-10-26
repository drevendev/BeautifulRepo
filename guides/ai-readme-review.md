# Review an AI-written README against evidence

A generated README can look polished while obscuring the first useful action or
inventing capabilities. Review the **claims and reader journey** before debating
typography, emoji or whether the page looks like a generic AI landing page.
This is a human review method, **not** an AI detector, beauty score or content
ban list. A quiet minimalist layout can be exactly right.

Use this with the [design-intent brief](../templates/DESIGN_INTENT.template.md)
and [visual README guidance](readme-visuals.md). You need only a text editor,
a local checkout and the project's normal test commands.

## An evidence-first review

1. **Name the reader's job.** Write one question the first screen must answer
   and one command or link that gets the visitor to a useful result.
2. **Extract testable claims.** For every number, compatibility statement,
   product screenshot, badge, performance adjective, install instruction,
   endorsement and release claim, write the exact source and revision.
   Label each claim **verified**, **illustrative**, **unverified** or **false**.
   Remove false claims. Qualify or withhold unverified ones.
3. **Run the first success.** Use a fresh checkout where practical. Capture
   the command, input, stdout/stderr, exit code, dependencies and environment.
   A screenshot alone is not a reproducible command.
4. **Read with images disabled.** Can a newcomer still find the purpose,
   the shortest working path, a limitation and a contribution route?
   Delete hero art that occupies attention without answering a question.
5. **Audit hierarchy, not a style blacklist.** A gradient, centered heading,
   concise slogan or clean card layout is not automatically bad. Ask what
   the choice clarifies *for this reader*. Watch for identical-weight cards,
   promises buried beneath badges, and generic copy that could name any repo.
6. **Make a deliberately different alternative.** Keep all verified facts
   identical. Try command-first versus use-case-first rather than swapping
   only adjectives and colors. Choose by audience and cost, not by a
   fabricated A/B-test winner.
7. **Record what was checked.** Offline link tests and text comparisons
   do not establish GitHub rendering, contrast, keyboard accessibility,
   narrow-screen wrapping, zoom or screen-reader behavior. Inspect those
   manually before claiming them.

**Stop-ship findings:** invented numbers or endorsements, non-working first
command, concealed data collection, unsupported platform compatibility,
fictitious security/contact routes, a mockup presented as a real screenshot,
or essential information available only inside an image.

**Editorial findings, not automatic defects:** an understated type scale,
a symmetrical layout, repeated cards, restrained color, emoji, or a familiar
heading pattern. Request a revision only when you can explain the reader cost.

## Check a workflow badge against the checkout

A CI badge is an *assertion about a workflow*, not a substitute for reading
the workflow and its latest check results. For one reproducible, offline test
of the reference itself, run this from a BeautifulRepo checkout:

```bash
python -I tools/workflow_badges.py --root . --repo drevendev/BeautifulRepo
```

This checks whether the root README's same-repository GitHub Actions status
badge points to a regular `.github/workflows/quality.yml` file. It reports
missing, redirected and unsupported file targets with source line numbers.
If no matching badges exist, that is **zero checked**, not a passing CI claim.
The tool never contacts GitHub or executes a workflow. It cannot tell whether
tests actually ran, passed, were required, or match the badge's implication.
Review current GitHub checks and any badge text separately. Other badge hosts,
reference-style image links and full Markdown rendering are out of scope.

See the [tool contract](../tools/README.md#github-actions-readme-badge-file-presence-check)
and [GitHub's status-badge URL format](https://docs.github.com/en/actions/how-tos/monitor-workflows/add-a-status-badge)
(reviewed 2026-10-26). This is a small mechanical check in the larger
evidence-ledger review, not proof of overall README honesty or accessibility.

## Worked example: Rowcount, not a hypothetical product

The checked-in [Rowcount implementation](../examples/cli-starter/rowcount.py)
and [CSV fixture](../examples/cli-starter/sample.csv) were inspected at
[commit `1db96d5`](https://github.com/drevendev/BeautifulRepo/commit/1db96d552d4e2ba6e9893cbd348d8f67eb3507fe)
on 2026-10-26. The fixture has a header and three nonblank records;
the CLI counts records, not data types, and requires Python 3.11+.
It uses Python's standard library and reads local files.

### Candidate first screen — deliberately invented bad copy

> **Rowcount — the ultimate AI-powered CSV platform.**
>
> Instantly process any spreadsheet at enterprise scale with guaranteed
> accuracy. Trusted by thousands of teams. Explore the beautiful dashboard
> and get started in seconds.

**This paragraph is a fabricated negative example, not a product description.**
The checkout has no AI-powered service, dashboard, customer evidence, accuracy
guarantee or universal format support. It does not give a runnable first step.
Adding shiny screenshots or a benchmark badge would compound the problem.

### Evidence ledger for the review

| Draft claim | Source check | Decision |
| --- | --- | --- |
| AI-powered, dashboard | CLI source has neither a model nor a UI | **False — remove** |
| Any spreadsheet, guaranteed accuracy | It reads CSV and validates row width, not schema/types | **False — remove** |
| Thousands of users | No user-count source supplied | **Unverified — withhold** |
| Count local CSV data rows | Executable source and fixture at the pinned revision | **Verified — show result** |
| Three records in the bundled sample | Three fixture records below one header | **Verified — reproduce** |

This is a **claim review**, not a judgment that the author's voice is
necessarily machine-generated.

### Replacement — quiet, command-first treatment

> **Rowcount — count CSV data records locally.**
>
> A small Python CLI reads a CSV file and prints the number of nonblank data
> records after its required header. It does not upload your data.
>
> Python 3.11+; from the BeautifulRepo checkout root:

```bash
python examples/cli-starter/rowcount.py examples/cli-starter/sample.csv
```

Expected stdout for the bundled fixture:

```text
Data rows: 3
```

The script reports malformed row widths but does **not** validate column
types, arbitrary dialects or schemas. It is a checkout-only example, not a
published Python package or hosted product. The real README treatments—[editorial](../examples/readme-visuals/rowcount/editorial.md),
[terminal-led](../examples/readme-visuals/rowcount/terminal-led.md) and
[contract-first](../examples/readme-visuals/rowcount/contract-first.md)—all
use the same verified facts rather than the fabricated copy above.

The test `tests/test_ai_readme_review.py` executes the documented command
against the repository's actual fixture. It does not simulate a fresh clone,
evaluate a language model or inspect a browser. If this command or its output
changes, update both the evidence ledger and the test.

## A reusable review receipt

Copy these fields into a PR description or a private review note:

```text
Reader / first question:
Repository and inspected commit:
Claims: verified | illustrative | unverified | false (source for each):
First success: cwd | command | input | stdout | exit code | environment:
First-screen alternative A / audience / trade-off:
First-screen alternative B / audience / trade-off:
Images disabled: readable purpose, command, result and limitation?:
Manual rendering: widths | light/dark | zoom | keyboard | screen reader:
Checks actually run:
Open uncertainty and follow-up:
```

Do not fill an unperformed check with "pass." Keep real product screenshots
distinct from illustrations, and prefer repository-relative image links.
If the result requires a complex diagram, retain a full textual equivalent
near it. Informative images require a meaningful alternative; a purely
decorative or fully redundant image may use `alt=""`.

**Sources inspected 2026-10-26:** [GitHub Markdown syntax](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax),
[W3C WAI Images Tutorial](https://www.w3.org/WAI/tutorials/images/),
[WAI Informative Images](https://www.w3.org/WAI/tutorials/images/informative/)
and [WAI Decorative Images](https://www.w3.org/WAI/tutorials/images/decorative/).
The editorial checklist and Rowcount example are original BeautifulRepo work;
the external sources support link and alternative-text guidance, not a
universal rule for detecting AI text.
