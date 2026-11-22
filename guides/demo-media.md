# Demo video in a README: evidence before autoplay

A short demo can answer "what will happen when I try this?" faster than a feature list. It can also bury the real result behind motion or leave a non-visual visitor with no useful answer. Keep the **first-success fact in ordinary text** and treat moving media as optional evidence.

Use this for a real CLI run, application state, game preview or before/after. A still is better when motion adds nothing. Do not call a mockup a screenshot, or a synthetic check a live-user success.

## A three-part entrance you can reuse

The README must remain useful **without playing any video**:

```md
![A sample local-link audit finds one broken destination before repair and none after.](media/demo-still.png)

[Watch the 20-second demonstration (MP4, 600 KB)](media/demo.mp4) ·
[Read the complete sequence](docs/demo-sequence.md)

The command `python check.py sample/` finds one broken link.
After correcting its destination, the same command reports none.
```

These files, byte counts and command results are **illustrative placeholders**. Replace them with a source-pinned recording, real output and checked-in paths. A relative MP4 Markdown link is a usable file destination but **does not guarantee an inline GitHub README player**. Do not paste custom HTML video embeds and assume GitHub will render them. GitHub officially documents relative README links and media attachments in specific interface contexts; verify actual playback at a rendered commit. Keep a poster and text fallback even when a player works.

Copy the [demo evidence template](../templates/DEMO_MEDIA.template.md) before publishing.

## Give each alternative its own job

- **Still/poster:** capture the decisive state. Informative-image alt text should explain the observed outcome, not merely say "screenshot"; truly decorative images may use empty alt text.
- **Text equivalent:** supply key actions, commands, visible messages, resulting state and context in normal readable Markdown, independent of images or playback.
- **Captions:** represent meaningful speech and other audio. A silent video does not contain speech to transcribe; explicitly state that it is silent rather than presenting visual descriptions as spoken captions.
- **Visual description:** explain important visual-only actions for non-visual readers, as authored descriptive text, audio description or other suitable alternative.
- **Player:** keep pause/seek and keyboard controls accessible, avoid autoplay/looping motion, check zoom and reduced-motion expectations, and keep a direct fallback file link. A VTT file merely existing does not prove it was presented by the player or announced by assistive technology.

W3C WAI separates captions, descriptive transcripts and important visual descriptions; specific needs depend on the audio and visual information. WCAG 2.2's Pause, Stop, Hide criterion has particular conditions for automatically starting motion. Do not assume a play control by itself proves compliance or that flashing content can be made safe simply by adding pause.

## A real asset set with honest limits

BeautifulRepo's [Pocket Trails page](../showcase/pocket-trails/README.md) contains a [still](../showcase/pocket-trails/pocket-trails-still.png), [MP4](../showcase/pocket-trails/pocket-trails.mp4), [WebM](../showcase/pocket-trails/pocket-trails.webm), [descriptive VTT](../showcase/pocket-trails/pocket-trails.vtt), [offline player](../showcase/pocket-trails/pocket-trails-player.html) and a complete text sequence.

Its **23.52-second silent recording** shows a *fictional* report changing from zero of two local-link checks passing to two of two after correcting a README link. The checks themselves run against synthetic disposable fixtures. This is **not** a real-person session, a live CLI capture, an external repair or an independent accessibility test. The VTT describes visible changes, **not transcribed speech**. Earlier decoding/Chromium checks are recorded on that page; **current GitHub playback, complete keyboard behavior and screen-reader announcements are NOT RUN**. Do not transfer those older checks to the current README without a fresh trial.

For your own demo, reproduce the first-success result from a specific source revision, mask tokens and personal information in *every frame*, and document rights for images, trademarks, footage, fonts and music separately from the source-code license.

## Acceptance checklist: source proof is not a browser trial

1. **Paths and claims:** record the full source SHA and verify still, video, transcript/description and any VTT; reproduce the documented result or mark it NOT RUN.
2. **Privacy:** inspect all frames, visible notifications, filenames and captions for secrets and personal content before publication.
3. **Rendered page:** open the GitHub README at a full commit SHA; inspect without images, at narrow width, at actual zoom, and with light/dark themes. The text route must stand alone.
4. **Real playback:** record browser/OS; play, pause, seek, test keyboard focus, caption/description choices and the fallback link. Observe reduced motion, unsupported codecs and failures instead of inferring cross-browser success.
5. **Assistive technology:** name the screen reader/browser pair and what it announced, or record **NOT RUN**. Static links, a VTT source file, a saved screenshot or tests cannot certify this.

Keep motion optional. Prefer a static result over an auto-looping GIF if it demonstrates the same point.

## Sources and scope

Primary guidance reviewed **2026-11-22 UTC**; interfaces and requirements may change.

- [GitHub: About READMEs and relative links](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes)
- [GitHub: Attaching media files](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/attaching-files) — supported media types and codec caveats in supported attachment contexts, **not** a promise about a committed MP4 rendering inline in a README
- [W3C WAI: Planning audio and video media](https://www.w3.org/WAI/media/av/planning/)
- [W3C WCAG 2.2: Understanding Pause, Stop, Hide](https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html)
- [W3C WAI: Images tutorial](https://www.w3.org/WAI/tutorials/images/)
- [BeautifulRepo's recorded synthetic demonstration](../showcase/pocket-trails/README.md)

This recipe is not evidence that a browser, GitHub renderer or screen reader has passed an accessibility test.
