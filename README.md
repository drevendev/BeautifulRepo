# BeautifulRepo

**Make your repository easy to understand, pleasant to explore, and worth contributing to.**

A practical handbook of checklists, reusable templates, annotated examples and small
quality tools. For maintainers of libraries, applications, command-line tools and
knowledge collections. Start with clarity; add personality without getting in the way.

[Start here](#start-here) · [Checklist](checklists/repository.md) ·
[Patterns](case-studies/first-patterns.md) · [Resources](catalog/README.md) ·
[Contribute](CONTRIBUTING.md)

---

## Start here

**Improving an existing repository?** Work through the
[essential checklist](checklists/repository.md#1-make-the-project-understandable).
Fix the first broken step in a new visitor's journey before adding decoration.

**Starting from scratch?** Adapt the [README scaffold](templates/README.template.md),
then provide one working example and an honest status statement.

**Looking for inspiration?** Explore the [first pattern studies](case-studies/first-patterns.md).
Each explains what to borrow, how to apply it and what not to copy.

## The visitor's journey

| Visitor asks | Your repository should provide |
| --- | --- |
| What is this, and is it for me? | One clear promise, intended audience and useful boundaries |
| What would I get? | A real example, screenshot or output, with a text explanation |
| Can I try it? | Prerequisites, a short path to success and expected results |
| Can I trust it? | Accurate status, license, limitations and verification evidence |
| How can I help? | A small contribution path, actionable issues and visible decisions |

## Explore the handbook

| Material | Use it for |
| --- | --- |
| [Repository checklist](checklists/repository.md) | Prioritize essential information, polish and maintenance |
| [README design guide](guides/readme.md) | Build a useful front page without turning it into a manual |
| [Visual README patterns](guides/readme-visuals.md) | Make screenshots, diagrams and theme-aware media carry evidence |
| [README scaffold](templates/README.template.md) | Adapt a starting structure to your own project |
| [Annotated pattern studies](case-studies/first-patterns.md) | Learn from Devostasis, Hungry Crab and Gum |
| [Curated source catalog](catalog/README.md) | Find primary guidance with application notes and caveats |
| [Programs and community events](guides/programs.md) | Separate current program rules from evergreen preparation |
| [Roadmap](ROADMAP.md) | See what exists and what comes next |

## A tool that maintains this collection

The catalog is structured data, not a second list somebody must remember to update.
Our dependency-free Python utility validates it and checks that the readable catalog
matches the data. It runs offline and never fetches or executes linked repositories.

From a checkout, with **Python 3.11 or newer**:

```bash
python tools/catalog.py
python tools/docs_links.py
python -m unittest discover -s tests -v
```

A successful catalog check prints `OK: 11 resources; generated catalog is current`
for this first edition and exits with code zero. The count changes as the catalog grows.
Failures name the entry and field that need attention. Time-sensitive records can emit
freshness warnings even when their structure is valid.

`python tools/docs_links.py` separately checks that repository-owned relative Markdown links
and image paths resolve to existing files or directories without network access. External URLs
and section fragments are intentionally out of scope; see [tool documentation](tools/README.md).

This is **not** a live-link checker, security scanner, accessibility certification or
repository beauty score. See [tool documentation](tools/README.md).

## Principles

**Clarity before decoration.** Explain the result before the implementation.
**Evidence before badges.** A badge must represent a real, relevant fact.
**Patterns before imitation.** Reuse ideas; verify permissions before copying material.
**Useful before exhaustive.** Every resource needs a reason to exist here and a next action.
**Accessible by default.** Keep essential information readable without images, animation or color.

## Status and contribution

This is the first working edition, not an exhaustive or independently certified handbook.
The [roadmap](ROADMAP.md) includes deeper visual examples, more reusable templates,
external-tool trials and accessibility testing. Suggestions and small improvements are welcome;
start with [CONTRIBUTING](CONTRIBUTING.md). Please report accessibility barriers through
[an issue](https://github.com/drevendev/BeautifulRepo/issues/new/choose).

Public documentation is maintained in English.

## License

[MIT](LICENSE). Linked projects and their assets retain their own licenses and trademarks.
Listing a source does not endorse every claim it makes or relicense its contents.
