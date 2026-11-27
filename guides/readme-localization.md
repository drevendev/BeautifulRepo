# Localize a README without splitting its source of truth

A translated README should shorten the route to a useful result, not create
another version of the project's promises. Start with one maintained language
and add another only when the important facts can be reviewed.

## Choose a small, honest structure

- Keep one default README. GitHub selects README locations in this order:
  `.github/`, the root, then `docs/`. A second README in a higher-priority
  location can inadvertently replace the entrance for all readers.
- Use clearly named translation files and a language switch near the title
  in each version. Use language names in their own script, not country flags.
- Link to shared commands, fixtures and reference pages rather than copying
  instructions that can drift. Label destinations in the default language.
  A translated README does not imply translated UI, documentation or support.
- On an HTML site you control, declare the page language and use `lang`
  for passages and links in other languages. For GitHub Markdown, inspect
  the rendered output before claiming that language markup or assistive
  technology works as intended.

Sources: [GitHub README discovery and relative links](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes),
[W3C language of parts](https://www.w3.org/WAI/WCAG22/Understanding/language-of-parts.html)
and [W3C language of page](https://www.w3.org/WAI/WCAG22/Understanding/language-of-page.html).
Reviewed 2026-11-27. These support the navigation and language-markup
principles, not an accessibility certificate for a GitHub README.

## Worked example: a partial translation

In a fictional CSV utility, French readers previously had to scroll through
two full README copies to discover the French instructions were obsolete.
Replace that arrangement with two files. The English page is authoritative;
the French page is an introduction and bridge, not another installation guide.

Root file: `README.md`

```markdown
# Sample Counter

English · [Français](docs/README.fr.md)

Count rows in a local CSV file.

## First run

From the repository root, run `python count.py sample.csv`.
For the bundled example, expect three data rows.
```

Translated file: `docs/README.fr.md`

```markdown
# Sample Counter

[English](../README.md) · Français

Comptez les lignes d'un fichier CSV local.

Traduction partielle : les instructions et les exemples sont en anglais.
Consultez le [premier essai (en anglais)](../README.md#first-run).
```

The command and result are fictional; this example tests documentation
routes, not CSV counting. The language switch uses file-relative paths.
The bridge uses the actual authoritative heading fragment, not a guessed
translation of it. The translation does not promise French support.

## Review translations when facts change

Keep a compact record with each translation or in a maintainer-visible
document. Name the source revision, not just the date:

```text
Language: fr
Coverage: purpose and first-run link only
Authoritative file: README.md
Source revision: <full Git commit>
Last human language review: <date or NOT REVIEWED>
Trigger: first-run, prerequisites, support or limitation changes
If stale: retain the language switch and point to the current source;
          remove unsafe or obsolete translated instructions
```

This is a template, not evidence of review. Translate visible labels and
useful image alternative text, not command names, flags, filenames or
machine output. See the [W3C translation technical steps](https://www.w3.org/WAI/about/translating/resources/technical-steps/)
(reviewed 2026-11-27) for a concrete separation of prose from markup and code.

Before merging a source change, inspect linked translations for changed
prerequisites, commands, versions, support routes and limitations. If no
fluent reviewer is available, mark the affected translation partial or
stale and offer the maintained source. Automated translation and matching
revision markers do not establish linguistic quality.

## Verify the reader's route

From a trusted pinned BeautifulRepo checkout beside the target checkout:

```sh
python -I tools/docs_links.py --root ../target-repo
python -I tools/html_navigation.py --root ../target-repo
```

The local destination checker catches a deleted translation; the fragment
checker can catch a stale link after a heading rename. The regression tests
materialize the two displayed Markdown files and exercise both cases.
They do not assess translation quality, execute the fictional command,
inspect rendered language attributes or observe a human reader.

For rendered acceptance, follow both language switches from the actual
repository entrance, follow the first-run bridge, inspect narrow layout
and test keyboard navigation. Record the exact revision, observed outcomes
and any unavailable language or assistive-technology review. See the
[task-first navigation guide](documentation-navigation.md) and
[visual acceptance checklist](../checklists/visual-accessibility-acceptance.md).
