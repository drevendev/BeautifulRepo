# Research and data repositories: show the evidence chain

A good research repository lets a reader distinguish **the question, the inputs,
the transformation, the result, and the limits of what can be reused**. A code
checkout alone does not guarantee reproducibility; a notebook screenshot alone
is not evidence that another person can execute the method.

## A trustworthy first screen

A reader should find these answers before opening a large notebook:

1. **Question and scope.** What claim or computation does this repository support?
   Identify the dataset's population, sampling period and important exclusions.
2. **Data status.** Are the inputs *synthetic*, *publicly reusable*, *available with
   permission*, *restricted* or *not redistributable*? Do not equate code's MIT
   license with ownership or redistribution permission for third-party data.
3. **Provenance.** State where each input came from, when it was collected/accessed,
   which version was used, the schema or data dictionary, and transformation steps.
4. **First reproduction.** Give one local command, its runtime and dependencies,
   and the expected text or checksum. Never describe a command as validated
   unless it was actually run on the checked-in sample.
5. **What is *not* proven.** A toy example tests documentation flow, not scientific
   validity, external data access, original paper claims or the full environment.

## A tested, self-contained example

[Research-data starter](../examples/research-data-starter/README.md) contains six
**fabricated** site counts, a CSV schema, a pure-stdlib analysis and regression tests.
It illustrates the evidence path without an account, API key, download, notebook kernel,
package installation or personal information. From the example directory:

```bash
python analysis.py
python -m unittest discover -s tests -v
```

Expected aggregate (registered with the test suite as structured JSON):

<!-- beautifulrepo:research-result:start -->
```json
{
  "grand_total": 60,
  "rows": 6,
  "totals": {
    "A": 36,
    "B": 24
  }
}
```
<!-- beautifulrepo:research-result:end -->

The result is compared with the shared
[expected-result fixture](../examples/research-data-starter/expected-result.json)
in `tests/test_research_data_starter.py`; the actual CLI output is checked
against the same fixture. JSON object key order is not significant.
The CLI emits pretty-printed JSON; its output key order is deterministic. The test suite
checks the result, reproducibility under input reordering and rejection of invalid
schema, dates, counts and duplicates.

## Data dictionary and transformations

Provide one line per field with type, units, valid range, missing-value conventions
and whether an identifier can reveal a person or location. Separate raw from derived
files; document how a reader can regenerate outputs. Prefer a small safe fixture to
having readers download gigabytes merely to check the analysis route.

For real work, record a pinned input version or checksum *after* verifying it,
and explain whether an external archive is required. Do not invent a SHA-256, DOI,
collection date, provenance record or license to fill a README template. If original
data cannot be redistributed, show a truthful access route and keep the sample
synthetic and clearly labeled. Public metadata can remain useful when the full
underlying data must remain restricted.

## Where does the data live?

A Git repository is useful for small, reviewable text fixtures and code. It is not
an unlimited archive for large changing binary files. Consider an appropriate
repository or archival service for large datasets; document stable identifiers,
checksums and retrieval requirements. Git LFS can address some large-file workflows,
but carries storage, bandwidth and client-configuration trade-offs. Review current
provider constraints before recommending it for a specific project.

A repository release, a dataset archive deposit and a Git commit are **different
artifacts**. Cite or link the one readers actually need. Never imply a DOI or a
permanent preservation commitment for a source checkout without one.

## Citation, license and privacy

GitHub supports a root `CITATION.cff` file and recognizes `type: dataset` when
appropriate. Add it only with accurate authors, title, version and real identifiers;
a `CITATION.cff` file is not itself a DOI minting process. For research software,
distinguish the package or source version from a related paper. The citation-file-format
specification supports these distinctions. A paper DOI, dataset DOI and software DOI
should not be treated as interchangeable.

Document **code license** and **data license or access restrictions** separately.
Review third-party redistribution rights, ethical approvals and potential identifying
details before publication. Synthetic examples are safer for teaching workflows,
but the word "synthetic" must not be a euphemism for lightly anonymized actual
participant or customer records.

The FAIR principles—findable, accessible, interoperable, reusable—are guidance,
not a declaration that all research data must be unrestricted. FAIR access can
involve authenticated, authorized access. Do not claim that following this short
guide alone makes a dataset FAIR-compliant.

## Suggested README sequence

**Outcome → data availability → schema/provenance → one reproduced result →
methods/environment → licenses/access restrictions → citation → limitations →
contribution and maintenance.** Use the
[research-data README template](../templates/RESEARCH_DATA_README.template.md)
as a starting point, then delete sections that do not apply.

## Source review and limitations

Reviewed **2026-10-16** (primary public guidance):

- [The Turing Way: research data management](https://book.the-turing-way.org/reproducible-research/rdm/)
  — reproducible and ethical data science requires sharing appropriate code,
  methods and accessible evidence, not only documentation aesthetics.
- [GO FAIR principles](https://www.gofair.us/fair-principles) and
  [Foundation A1.2 guidance](https://www.gofair.foundation/a1-2)
  — persistent identifiers, provenance, metadata and appropriate controlled access.
- [GitHub: citation files](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-citation-files)
  — citation file behavior, including dataset citation support.
- [Citation File Format](https://citation-file-format.github.io/)
  — machine-readable citation metadata; use real project facts.
- [DataCite: software citation and reuse](https://support.datacite.org/docs/software-citation-and-reuse)
  — research-software identifiers and metadata are distinct from GitHub commits.
- [GitHub: About large files](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github)
  — Git repository and large-file limitations; review current service policy.

This is a general-purpose documentation pattern, **not** a legal opinion, human
subjects/ethics clearance, FAIR certification, or domain-specific scientific
validation. Distribution, data access and retention requirements vary by institution,
discipline, jurisdiction and dataset.
