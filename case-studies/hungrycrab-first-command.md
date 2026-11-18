# Hungry Crab: put the first safe command before release history

**Case status (2026-11-18): source-only review and proposed README excerpt.**
The source repository is public and the observations below are independently
checkable at a fixed commit. No change was made to HungryCrab, no target PR was
opened and no installation, first-run, rendered-width or after-state test was
performed. This is **not** a completed before/after case under our
[case procedure](README.md).

## Source and scope

- Target: [drevendev/HungryCrab](https://github.com/drevendev/HungryCrab)
  at [`d20850c4e71382c796c4b4dac554137ebcb7e937`](https://github.com/drevendev/HungryCrab/tree/d20850c4e71382c796c4b4dac554137ebcb7e937),
  observed on 2026-11-18; repository visibility was **public** when checked.
- [Pinned README](https://github.com/drevendev/HungryCrab/blob/d20850c4e71382c796c4b4dac554137ebcb7e937/README.md)
  (blob `b7bcabe38e54a9cc73940d0d1a6deef63448a33c`),
  [package metadata](https://github.com/drevendev/HungryCrab/blob/d20850c4e71382c796c4b4dac554137ebcb7e937/pyproject.toml),
  [Everywhere guide](https://github.com/drevendev/HungryCrab/blob/d20850c4e71382c796c4b4dac554137ebcb7e937/docs/everywhere.md)
  and [MIT license](https://github.com/drevendev/HungryCrab/blob/d20850c4e71382c796c4b4dac554137ebcb7e937/LICENSE)
  were read from that commit.
- This is an **editorial first-visit inspection**. The repository's running
  behavior, GitHub release list, PyPI publication, optional host plugins,
  security properties and live private-reporting status were not verified.

## What the original does well

The opening has memorable ASCII art, a clear product identity and a concrete
explanation of how repository evidence becomes a human-reviewed menu.
The [glossary](https://github.com/drevendev/HungryCrab/blob/d20850c4e71382c796c4b4dac554137ebcb7e937/README.md#L68-L77)
explains the names instead of expecting everyone to know them. The
[install section](https://github.com/drevendev/HungryCrab/blob/d20850c4e71382c796c4b4dac554137ebcb7e937/README.md#L79-L97)
contains copyable commands, while the
[CLI verification subsection](https://github.com/drevendev/HungryCrab/blob/d20850c4e71382c796c4b4dac554137ebcb7e937/README.md#L154-L167)
explicitly says what its no-network checks do **not** prove. These are worth
preserving, not replacing with an empty badge wall.

## The specific first-visit friction

| Pinned location | Visitor obstacle | Smallest proposed change |
| --- | --- | --- |
| [README:1–39](https://github.com/drevendev/HungryCrab/blob/d20850c4e71382c796c4b4dac554137ebcb7e937/README.md#L1-L39) | A newcomer sees a large text illustration, badges and several explanatory paragraphs before a way to try the CLI. | Keep the identity but put a short, clearly named first-command path immediately after the promise. |
| [README:41–66](https://github.com/drevendev/HungryCrab/blob/d20850c4e71382c796c4b4dac554137ebcb7e937/README.md#L41-L66) | Detailed 0.6.10 maintenance and 0.6.11 development/research history separates the promise from install. | Retain those caveats under **Release status and limitations** below first use; link there from the start. |
| [README:68–96 and 154–167](https://github.com/drevendev/HungryCrab/blob/d20850c4e71382c796c4b4dac554137ebcb7e937/README.md#L68-L96) | Six glossary terms and the full plugin setup precede a safe, two-command post-install smoke route. | Surface the existing no-network `--version` and `--help` checks first, then link to the full guide and terms. |

The source's `pyproject.toml` declares **`0.6.11.dev0`** while the
README discusses a **0.6.10 maintenance release**. These describe different
source/distribution states; they are **not evidence of a mismatched published
release**. A revised first screen should say clearly that the installed
package's actual version must be checked on the user's machine.

## An annotated proposed first screen

The following is **proposed copy for the target README**, not a change
already applied to HungryCrab and not observed CLI output. It deliberately
reuses the target's own installation and verification commands rather than
inventing a demonstration.

> **Hungry Crab** — inspect another repository for ideas your own project
> could adapt, with source evidence, license-aware decisions and human review.
>
> **Try the CLI.** Requires Python 3.11+ and `uv`; installation downloads
> packages. These two checks run *after* installation and do not contact GitHub:
>
> ```sh
> uv tool install hungry-crab
> crab --version
> crab --help
> ```
>
> Next: [inspect your first repository](https://github.com/drevendev/HungryCrab/blob/d20850c4e71382c796c4b4dac554137ebcb7e937/README.md#feed-the-crab)
> (network/GitHub access required; `git` and `gh` are used in the
> documented GitHub workflow), or
> [set up a local MCP/plugin host](https://github.com/drevendev/HungryCrab/blob/d20850c4e71382c796c4b4dac554137ebcb7e937/docs/everywhere.md).
> [Read release scope and limitations](https://github.com/drevendev/HungryCrab/blob/d20850c4e71382c796c4b4dac554137ebcb7e937/README.md#L41-L66)
> before relying on automation. The project describes its stable analysis
> scope as human-supervised and its autonomous publication paths as experimental.

**What changes:** the first action is observable and limited. The metaphor,
detailed install options, version history, safety qualifications and
demonstration commands remain available below it. In an upstream patch, use
**relative links** to in-repository headings/files instead of these
commit-pinned absolute inspection links.

**What does not change:** the CLI's actual behavior, required authentication
for live repository operations, host-plugin support, releases or permissions.
The proposed text is not permission to install software on a user's machine.

## Acceptance needed for a real before/after

1. Obtain authorization to modify HungryCrab and submit the change via its
   own normal PR (BeautifulRepo has no permission to write that target).
2. Check the target's real latest release/tag and the pinned install
   instructions separately. Reproduce a clean installation, the two CLI
   smoke commands, expected exit codes and one deliberate failure path,
   recording OS, Python, exact package version and output.
3. Capture the old and proposed README at narrow width in light and dark
   GitHub themes, with text equivalents. A source-only layout comparison
   cannot certify mobile readability, keyboard access or screen-reader use.
4. After any target merge, re-run the same checks on the **merge SHA** and
   link its own CI run. Record unknown, skipped and failed checks rather than
   treating them as success.

Until those steps happen, this case is an **independently verifiable source
analysis and useful copy proposal**, not an implemented change or measured
increase in adoption.

## Transferable pattern

For a complex CLI or agent toolkit: **one concrete promise → one bounded
first command → honest requirements and limitations → the full workflow**.
Long release records are valuable evidence, but they work better as linked
details than as a barrier between a visitor and a safe first action.

This arrangement follows [GitHub's README guidance](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes)
and the [Open Source Guides' starting-a-project advice](https://opensource.guide/starting-a-project/),
reviewed 2026-11-18. Neither source asserts that this particular rewrite
will improve conversion or usability; that requires actual observation.
