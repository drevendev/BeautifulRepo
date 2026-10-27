# Design intent — {repository or document surface}

**Use this before polishing a README or documentation entrance.** Replace the
braced fields with repository-specific evidence. A decision record is useful only
when another maintainer can reproduce the result and challenge the trade-off.
This is a planning and review aid, **not** an accessibility certificate.

## Scope and reader

- **Surface and audience:** {README landing screen, guide or example; who arrives}
- **Reader's job:** {one task they want to finish}
- **One-sentence promise:** {specific outcome, not a slogan}
- **First success:** {shortest real path to a useful result}
- **Constraints:** {runtime, privacy, bandwidth, licensing, mobile, maintenance}

## Evidence boundary

| Claim or asset | Status | Source and reproduction | Limits |
| --- | --- | --- | --- |
| {command/result or screenshot} | {verified, illustrative, or proposed} | {exact commit or file, input, command, expected result, review date} | {what this does not prove} |
| {second important claim} | {verified, illustrative, or proposed} | {traceable evidence or explicitly none} | {known uncertainty} |

Never represent a mockup as an application screenshot, a sample output as a
published release, or copied branding as original art. If there is no working
result yet, label the visual as **illustrative** and keep the limitation visible
on the README itself, not just in this brief.

## First-screen alternatives

Describe **two materially different hierarchies** using the *same facts*:

1. **{treatment name}:** {audience, first question, element order, intended gain,
   opportunity cost}.
2. **{treatment name}:** {audience, first question, element order, intended gain,
   opportunity cost}.

**Selection rule:** {when to use either; avoid declaring a taste-based winner}.
**Nonvisual reading order:** {what remains understandable when images fail}.
**Copyable path:** {where the actual command, sample and expected output live}.

## Visual and interaction decisions

- **Typography and hierarchy:** {why the page makes the result scannable}.
- **Colour and theme:** {light/dark behaviour and labels beyond colour}.
- **Images or diagrams:** {informative, decorative or complex; why each is needed;
  alt-text choice and nearby equivalent}.
- **Narrow view, zoom and motion:** {wrapping, overflow, focus, reduced-motion
  behaviour or explicit non-applicability}.
- **Dependencies and provenance:** {asset ownership, permission and size; prefer
  local assets and zero mandatory design services}.
- **Maintenance trigger:** {what product change invalidates this presentation}.

An informative image needs a text equivalent. A purely decorative image can
use `alt=""`; deciding which is appropriate requires editorial judgement.
Use real text for commands and key conclusions, even when an illustration
repeats them.

## Rejected approaches

- **{tempting approach}:** {specific reason it hides evidence or harms readers}.
- **{another approach}:** {specific maintenance, accessibility or honesty cost}.

## Verification and decision

For GitHub-rendered README work, copy the
[manual visual acceptance receipt](../checklists/visual-accessibility-acceptance.md)
and record actual light/dark, reflow, 400% zoom and assistive-technology results.
Leave unchecked environments as NOT RUN; do not infer them from source tests.

- **Source check:** {named revision, fixture/command, actual observed output}.
- **Automated checks:** {exact commands and results, or NOT RUN}.
- **Manual rendering:** {GitHub/browser, date, light/dark, widths, images off}.
- **Accessibility checks:** {keyboard, 400% zoom, screen reader, motion, or
  explicitly NOT CHECKED for each}.
- **Open risks:** {unverified assertions; owner of any follow-up}.
- **Decision:** {ship, revise, or defer, with the reason}.

Only mark a check **PASS** if it was actually performed on the stated version.
A source test does not prove contrast, responsive rendering, screen-reader
behaviour or improved reader comprehension.

**Method references (reviewed 2026-10-26):**
[BeautifulRepo visual guidance](../guides/readme-visuals.md) ·
[W3C WAI images tutorial](https://www.w3.org/WAI/tutorials/images/) ·
[W3C informative images](https://www.w3.org/WAI/tutorials/images/informative/) ·
[W3C decorative images](https://www.w3.org/WAI/tutorials/images/decorative/).
