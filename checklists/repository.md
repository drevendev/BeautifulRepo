# Repository checklist

Use this as an audit, not a points system. Record **done**, **missing**, **not checked**
or **not applicable with a reason**. File presence is not proof that the file is useful.
Choose the smallest change that removes an actual reader or contributor obstacle.

## 1. Make the project understandable

- [ ] The name and first sentence explain the outcome and intended user.
- [ ] The README distinguishes implemented capabilities from plans and limitations.
- [ ] One real result is visible: example output, annotated screenshot or small walkthrough.
- [ ] Essential information has a text equivalent; it is not trapped in an image.
- [ ] The first-use path states prerequisites, working directory and supported environment.
- [ ] Example commands show expected results and have been tried against a named revision.
- [ ] A license is present; third-party material has separate provenance where needed.
- [ ] Help, bug reporting and contribution instructions are easy to find.

## 2. Make it pleasant to explore

- [ ] Headings follow a logical hierarchy; links describe their destination.
- [ ] The README links to deeper documentation instead of embedding every detail.
- [ ] Badges are few, relevant and truthful; a missing check is not a green check.
- [ ] Images have useful alternatives; long diagrams also have an adjacent explanation.
- [ ] Screenshots are legible in narrow layouts and both light and dark environments.
- [ ] Motion is optional rather than essential; a static or text alternative exists.
- [ ] Tables compare genuinely comparable things and remain usable on small screens.
- [ ] Names, terminology, code blocks and navigation are consistent across documents.

## 3. Make contributions sustainable

- [ ] CONTRIBUTING explains a small contribution, local checks and review expectations.
- [ ] Issue forms request evidence without forcing unnecessary personal information.
- [ ] The project has a workable conduct policy and a real reporting route, not placeholders.
- [ ] Security reporting guidance matches the channels that are actually available.
- [ ] Beginner tasks include scope, relevant files, acceptance criteria and an example.
- [ ] Changes and releases distinguish what shipped, changed, broke or was deprecated.
- [ ] CI checks the promises automation can verify; manual judgments remain explicit.
- [ ] Important external resources have provenance, a review date and an update trigger.

## Turn the audit into work

Write one finding per problem: **observed obstacle → affected reader → smallest fix →
verification**. For example: “The install command assumes a package manager not named in
prerequisites; a clean-machine user cannot start. Name it and test the documented path.”
Do not label an issue beginner-friendly merely because its title is short.

## Basis and limits

GitHub's [community profile documentation](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/about-community-profiles-for-public-repositories)
explains which community files it recognizes. Presence is only one part of this checklist.
Open Source Guides informs [project setup](https://opensource.guide/starting-a-project/),
[maintenance](https://opensource.guide/best-practices/) and
[accessible documentation](https://opensource.guide/accessibility-best-practices-for-your-project/).
These are editorial recommendations, not a claim of legal or accessibility compliance.
