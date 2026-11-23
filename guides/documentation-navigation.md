# Make repository documentation navigable by task

A repository can have working links and still be difficult to use. A newcomer
may reach a page called “Reference” but not the command that produces a first
result. An experienced user may be forced through a tutorial just to find an
option. Treat navigation as **reader decisions**, not a directory listing.

This recipe is for GitHub repositories with multiple Markdown pages. It does
not require a new documentation generator, hosted site, or folder hierarchy.

## Start with four reader questions

Write down four *hypotheses* about likely visitors; observe actual readers
before claiming that navigation works:

1. **First result:** Where can I run a small example, and what should I see?
2. **Next task:** Where can I solve an existing problem without starting over?
3. **Exact answer:** Where are the options, schema, errors, and limitations?
4. **Trust and help:** Where are project status, support, and contribution routes?

Choose a primary destination for each supported task. If one is unavailable,
say so instead of inventing a page. [Diátaxis](https://diataxis.fr/start-here/)
is a useful *editorial lens*, not a required directory structure: tutorials
teach by doing; how-to guides solve tasks; references describe exact facts;
explanations explore why. Reviewed 2026-11-23.

## Two layers, two jobs

**Root README:** one promise, an observable result, prerequisites, and a short
choice of next routes. Do not bury the first command under a file inventory.

**Documentation index:** task names, useful destinations, and one-sentence
outcomes. Link the index from the README and link back. Start with the
[editable docs index](../templates/DOCS_INDEX.template.md), not another
copy of a long README.

Consider a *fictional* CLI repository:

```text
README.md
docs/
  README.md
  quickstart.md
  how-to/retry-failed-import.md
  reference/cli.md
  explanation/import-model.md
CONTRIBUTING.md
```

“Documentation: guides, CLI, concepts” forces people to guess. Instead, a
root README can show the actual decisions:

```markdown
- [Run a sample import](docs/quickstart.md) — produces a local report.
- [Retry a failed import](docs/how-to/retry-failed-import.md) —
  diagnose an existing run without repeating the tutorial.
- [CLI options and exit codes](docs/reference/cli.md) — exact behavior.
- [Why imports are staged](docs/explanation/import-model.md) —
  design rationale, not step-by-step instructions.
```

These paths and outcomes are **illustrative**, not real BeautifulRepo features
or tested commands. Create and verify the destination files before adopting
this copy.

## Keep the route working

- Prefer **relative links** between files in the same repository. From
  `docs/README.md`, link to `quickstart.md`, not `docs/quickstart.md`.
- Use link names that make sense out of context: “CLI options and exit codes”
  beats “read more.”
- Give pages one primary job; split a tutorial from the parameter reference
  only when doing so eliminates actual reader friction.
- Keep heading text stable where other pages link to its fragments. GitHub's
  automatic outline is useful, but repeated headings can change fragment IDs.
- Add a return path from deep reference pages to the index or a related task.
- Put supported environments and untested cases next to their commands.
  Never present an abandoned discussion channel as live support.
- Small repositories can use only a README and one guide. Extra layers are
  not inherently better.

GitHub documents README discovery order, relative paths, headings and section
links in [About READMEs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes).
[Write the Docs' principles](https://www.writethedocs.org/guide/writing/docs-principles/)
emphasize discoverability and directly addressable sections. Both reviewed
2026-11-23.

## Record a navigation walkthrough

Give an unfamiliar reader a **task**, not a page name. Start at the repository
root; observe their route. A compact record looks like:

```text
Task: Find the first executable example
Starting page: root README
Observed path: README → examples index → example README
Outcome: found command / unable to locate / NOT TESTED
Obstacle: exact link text or missing destination
Smallest change: rename a link or add one bridge
Verification: follow the new route on rendered GitHub
```

This is a *recording template*, not evidence that a trial occurred. Preserve
the date, inspected revision and browser/viewport. Distinguish author
self-review from independent newcomer testing. Neither successful mouse
navigation nor valid Markdown establishes keyboard or screen-reader usability.

## Check links without claiming usability

From a pinned BeautifulRepo checkout beside a target checkout, run:

```sh
python -I tools/docs_links.py --root ../target-repo
python -I tools/html_navigation.py --root ../target-repo
```

The [offline tools](../tools/README.md) check supported **local destinations
and fragments**. They do not fetch external URLs, prove that every page is
discoverable, validate hosted-site navigation, or observe user comprehension.
A clean run is not a navigation PASS.

BeautifulRepo itself illustrates layered routes:
[the first-screen chooser](../README.md#start-here) leads to a
[working-example index](../examples/README.md),
[case-study index](../case-studies/README.md) and
[tool reference](../tools/README.md). Those are inspected source paths, not
independently verified visitor journeys.

## Acceptance checklist

- The README identifies a useful first result with an honest prerequisite.
- The index names real tasks and answers, not only document categories.
- Promised destinations exist at the revision under review.
- Deep pages offer a return route and a meaningful next action.
- Local link/fragment checks pass on the changed checkout.
- A rendered-page task walkthrough is recorded, or explicitly **NOT TESTED**.
- No installation, host-rendering, mobile, or accessibility result is claimed
  solely because Markdown links are correct.

The outcome is a person reaching the right answer, not a beautiful directory
tree.
