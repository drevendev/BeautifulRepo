# Game repositories: prove the first play

A game README serves two audiences. A player wants a real build and a reason to
try it; a contributor wants reproducible source and clear rights to reuse it.
A Git repository is not evidence that a hosted game launches, and a store page
is not proof that the linked source can rebuild its binary.

## Show a player one verified minute

Put these answers near the top, before build-tool detail:

1. **Action and platform:** what the player does, on which platform, and
   whether this is a prototype, demo, shipped game or archived project.
2. **Launch route:** the specific browser URL or platform-specific download,
   the *observed* launch result, build ID and date tested. If there is no
   playable build, say **source only**.
3. **Gameplay evidence:** an actual current-build screenshot or short captioned
   capture. Describe the important state and player action in text, including
   a useful image alternative.
4. **First minute:** controls, immediate goal, expected result, restart/quit,
   and whether progress survives a browser refresh.
5. **Limitations:** tested devices/OS/browser, offline/network behavior,
   account requirements, known input/accessibility gaps and missing tests.

**Illustrative wording (fictional, not a shipped game).**

Before: "The ultimate fantasy puzzle — play now!"

After: "Sort six lanterns before the timer expires. Use the arrow keys to
swap neighbors; press R to restart. This five-minute browser prototype
does not save progress."

The second version enables a decision; no user testing is claimed.

## Separate a playable build from a reproducible source build

For a *clean checkout at a named commit*, document the tested game-engine
and runtime versions, dependency/setup steps, build command, first launch,
expected screen and test command. State which platforms were actually run.
A passing unit test or README-link check is **not** a browser/device test
or evidence that an external demo, store download or multiplayer server works.

Track the relationship between a Git commit, a GitHub tag/release, an
itch.io upload and a playable build. These are distinct artifacts and
events. Say which build the current screenshot and changelog describe;
do not silently reuse old captures as new-version gameplay.

## Screenshots, motion and store presentation

Use a real gameplay still before any large animation. Include descriptive
alt text and a written controls/result explanation. Avoid essential text
inside images, flashing autoplay, and audio-only instructions; caption or
transcribe video walkthroughs. Static source checks do not prove WCAG
conformance or a playable keyboard/controller route.

The [official itch.io creator guide](https://itch.io/docs/creators/getting-started)
recommends a 315:250 **cover aspect ratio** (for example 630×500) and
roughly 3–5 screenshots **for the itch.io page**. These are not GitHub
README image requirements. The [itch.io widget](https://itch.io/docs/creators/widget)
is intended for embedding on other websites; use a normal link in a GitHub
README rather than promising an embedded purchase or game iframe works.

## License code, art and audio explicitly

A public repository is not automatically open source. A code license
does not automatically give visitors permission to reuse game sprites,
music, sound effects, fonts, logos, trailers or third-party assets.
Identify exact file paths and the applicable rights for each category.
If an asset's terms are unknown, do not imply permission. Use the
[asset provenance guide](third-party-assets.md) and do not invent a
private security or takedown contact.

## Make updates and feedback actionable

Link real patch notes or devlogs for a verified playable build, including
save compatibility or reset behavior where tested. For bugs, request a
build ID, platform, short reproduction, expected/actual behavior and
sanitized evidence. Do not promise response times, security or accessibility
certification without the corresponding process and results.

Adapt the [game README template](../templates/GAME_README.template.md) and
use the [first-success checklist](../checklists/first-success.md).
The [application guide](application-repositories.md) has more detail on
services and data handling; this guide focuses on games' mixed audience.

## Sources and boundaries

Reviewed **2026-11-14**:

- [GitHub — About READMEs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes)
  — first-use information and navigation.
- [GitHub — Licensing a repository](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository)
  — public availability is not a reuse license.
- [itch.io — Your first page](https://itch.io/docs/creators/getting-started)
  — page presentation, cover and screenshot guidance.
- [itch.io — Embeddable widget](https://itch.io/docs/creators/widget)
  — embedding on external sites.

This guide is **documentation guidance**, not a bundled or tested game,
license opinion, accessibility certification or real-player evaluation.
