# Idle Fantasy Shop: the first play is below the release ledger

**Case status — 2026-11-18: source-only diagnosis and proposed reader-first
rewrite.** This is **not** a completed before/after case. No change to the game
repository, fresh-clone build, hosted playtest, accessibility evaluation or
target-native CI run was performed.

## Pinned sources and what was actually checked

- Target: [drevendev/IdleShop](https://github.com/drevendev/IdleShop),
  inspected at [`05c67fe0dcaaf9f8016860ff94717c362a29342a`](https://github.com/drevendev/IdleShop/tree/05c67fe0dcaaf9f8016860ff94717c362a29342a)
  on 2026-11-18. The observations below refer to its
  [README](https://github.com/drevendev/IdleShop/blob/05c67fe0dcaaf9f8016860ff94717c362a29342a/README.md)
  and [package.json](https://github.com/drevendev/IdleShop/blob/05c67fe0dcaaf9f8016860ff94717c362a29342a/package.json),
  **not** whatever later appears on `master`.
- The external [0.16.0 itch.io devlog](https://drevengames.itch.io/idle-fantasy-shop/devlog/1784704/0160-a-changing-market-and-a-clearer-shop)
  lists a browser-playable ZIP uploaded on **2026-11-16 at 18:59 UTC**.
  Checked as public page content on 2026-11-18. This is **not** an observed
  browser launch, a GitHub tag, or proof that the uploaded ZIP matches a
  particular source commit.
- Applicable [game README guidance](../guides/game-repositories.md) and
  [first-success checklist](../checklists/first-success.md). Their advice is
  a rubric, not a claim that the target was evaluated by real players.

## The reader obstacle

The target's first screen is a repository-maintenance chronology. After the
title it immediately links owner-facing UI/delivery rules, then presents many
dated release preparation, review, packaging and decision entries. The
explanation beginning *“A cozy, information-dense browser idle game”* and
its play link come **much later**, after the long release ledger. A visitor
looking for the game must scan operational history before learning what they
can play.

That chronology is valuable to maintainers. Moving it behind a short
reader entrance would preserve its history while changing the default
audience from release operators to players and prospective contributors.

A separate source inconsistency needs care: the top of the inspected README
records publication of `0.16.0+216571b` on 16 November, but a lower
`## Status` section still calls `0.14.0/schema14` current. The older entry
may be retained as history; **two sections cannot both be an undated current
release indicator**. A fix must preserve the qualification distinction
between original `ff215ee` and later credits-only `216571b`. Neither the
itch.io version label nor this case establishes source-to-ZIP identity.

## Proposed first screen (editorial mock-up only)

This is **copy to verify**, not a patch applied to IdleShop. The facts come
from the inspected source and store listing; the first-minute gameplay
steps and responsive layout still need a real hosted check.

```markdown
# Idle Fantasy Shop

Run a small shop in Latchford. Gather and craft goods, stock your shelves,
choose prices and see which visitors buy. A browser idle game with English
and Russian text.

[Play in your browser on itch.io](https://drevengames.itch.io/idle-fantasy-shop)

**Published on itch.io:** 0.16.0 (store page checked 18 November 2026).
For save updates, export a backup in Settings and close older game tabs.

## First minute
[Add three actual, observed player actions and their on-screen results here.]
[Confirm save persistence, keyboard controls and mobile support before claiming them.]

## Develop locally
Requires Node.js 24 and npm 11.

```sh
npm ci
npm run dev
```

[Release history and qualification evidence](docs/release/README.md)
[Development roadmap](docs/ROADMAP.md)
```

The commands and runtime requirements are copied from the pinned
`package.json` and README; **they were not executed** for this case.
The playable link and update-backup instruction come from public game
materials, not from a fresh browser test. The brackets are deliberately
unfilled: guessing controls or on-screen results would turn a useful
template into fabricated evidence.

## Smallest real target change, if separately authorized

1. Put the player promise and hosted play link above the release chronology.
   Keep a short dated current-status line and move the long chronology to a
   clearly labelled historical page or existing release index.
2. Resolve the `0.16` versus `0.14` *current* contradiction without changing
   the original qualification, release and ZIP evidence.
3. Reproduce one clean first minute in the hosted build. Record actual
   actions, visible results, save/reload behavior and a failure path.
4. Recheck the target's own CI, play/build identity and README at exact
   before/after SHAs. Then capture narrow-width light/dark rendering with
   a text equivalent and remaining accessibility unknowns.

The trade-off is one more click to the historical operator log. The
gain is immediate orientation for a visitor who has never heard of the
game. The [case-study procedure](README.md) requires a target PR,
after-merge SHA, same-tool audits, first-run traces and native checks
before this can be promoted from **source-only** to **complete**.

## Explicitly not established

No target edits or PR; no observed `npm ci`, `npm run dev`, browser
session, published ZIP checksum, save migration, screenshot, mobile test,
keyboard test, screen-reader test or real-player success. No licence or
third-party asset reuse claims are drawn from the game source. The
source-only observation does **not** count as a successful before/after
transformation in [#88](https://github.com/drevendev/BeautifulRepo/issues/88).
