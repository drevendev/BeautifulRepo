# Contribute to BeautifulRepo

Thank you for helping make repositories easier to understand. Useful contributions
include a clearer example, a repaired link, an accessibility improvement, a tested
workflow or a small tool with a well-defined purpose.

## Start small

Read the [roadmap](ROADMAP.md) and search existing issues and pull requests. Describe the
reader's problem before proposing a solution. An issue is helpful for a large change;
a small correction can go straight to a pull request. Keep one topic per contribution.

## Add a resource

Edit `catalog/resources.json`, not its generated README. Each resource needs a primary
source, a specific benefit, a local application, a limitation, a real review date and
honest coverage. “Popular” and “awesome” are not sufficient reasons to list something.
Separate reading documentation from running a tool. Link to copyrighted material rather
than copying it; check permissions and preserve required attribution before any reuse.

From the repository root with Python 3.11 or newer:

```bash
python tools/catalog.py --write
python tools/catalog.py
python -m unittest discover -s tests -v
```

The first command explicitly regenerates `catalog/README.md`; the others are checks.
Review the generated diff. No network access or third-party Python packages are needed.

## Quality expectations

Public documentation is in English. Use descriptive headings and links, text alternatives
for meaningful images, and short, verified examples. Identify incomplete investigations.
Do not add tracking images, copied brand assets, misleading badges, unsupported benchmark
claims, referral promotions or bulk low-effort changes.

A pull request should explain the change, evidence, checks actually run and remaining
limitations. Reports about documentation, code and accessibility are all welcome. The
maintainer handles review and implementation; contributors are not expected to rescue an
abandoned queue. No guaranteed response-time service level is claimed.

## Respect and safety

Discuss the work, not personal attributes. Harassment, doxxing and discriminatory conduct
are not welcome. Do not post secrets, private logs or personal contact information in
issues. A dedicated conduct policy and confirmed confidential reporting route remain on
the roadmap; their absence must not be represented as complete community compliance.
For sensitive abuse that cannot safely be posted here, use GitHub's platform reporting
facilities rather than disclosing private details in an issue.
