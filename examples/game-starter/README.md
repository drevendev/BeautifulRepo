# Lantern Row: first play for a source-only game

**Player promise:** light five lamps by choosing switches 1–5. Each switch flips
itself and its immediate neighbors. You have ten moves to light them all.

**Status:** small **terminal game source example**, not a published download,
browser demo, itch.io build, Steam game or production release. The playable
artifact here is [the Python source](lantern_row.py), not a hosted URL.
It requires Python 3.11+ and has no external packages.

## First success: see a reproducible win

From the **BeautifulRepo repository root**:

~~~sh
python -I examples/game-starter/lantern_row.py --demo
~~~

Expected stdout (the tests compare this fenced block with the program's decoded output):

~~~text
Lantern Row | deterministic offline transcript
Start: ..... (0/5 lit)
Switch 1: ##... (2/5 lit)
Switch 4: ##### (5/5 lit)
WIN in 2 moves
~~~

The # symbol means **lit**; the dot means **dark**. The five positions run
left to right. The script exits **0** for a win. This result was reproduced
using an isolated copy of the game source with Python 3.13.5 on Linux on
**2026-11-19**; that local check is not a clean-clone or hosted playtest.
The repository's automated tests exercise the same command in CI.

## Play it yourself

~~~sh
python -I examples/game-starter/lantern_row.py
~~~

The game starts with five dark lamps. Enter a switch number from **1** through
**5**, press Enter, and observe the updated text row. Enter q to quit without
saving; an invalid answer consumes no move. The game ends at a win or ten
valid moves, and resets when run again. For a deterministic attempt use
the --moves option:

~~~sh
python -I examples/game-starter/lantern_row.py --moves 1 4
~~~

## Show a failure, not just a happy screenshot

~~~sh
python -I examples/game-starter/lantern_row.py --moves 9
~~~

Expected stderr:

~~~text
ERROR: choose a switch from 1 to 5 (got 9)
~~~

That invalid input exits **2** without starting or partially replaying a
game. A valid but unsuccessful sequence (such as --moves 2) exits **1**
and reports no win. q or end-of-input in interactive mode exits **0** as a
voluntary exit, not as a win.

Run its independent Python regressions from the repository root:

~~~sh
python -m unittest discover -s tests -p 'test_game_starter.py' -v
~~~

The tests cover neighbor flips, immutable state, exact victory transcript,
unsuccessful attempts, validation before replay, move limit, invalid
interactive input and quit/EOF behavior. They are not human-player or
visual accessibility research.

## Scope, rights and trade-offs

- **Platform actually exercised:** a local Linux terminal with Python 3.13.5.
  CI additionally runs unit tests on its declared Python/OS matrix; passing CI
  is not the same as human testing on those platforms.
- **Network, data and saves:** no network requests, credentials, telemetry,
  files, saves or installed packages. Closing the terminal ends the session.
- **Controls:** keyboard number + Enter or q; text status uses both characters
  and a numeric lit count, not color or sound alone.
- **Visual evidence:** the transcript above is real terminal text. There is no
  gameplay screenshot, music, artwork, motion or controller support to claim.
  Screen readers, display scaling and keyboard ergonomics beyond input
  handling were not assessed.
- **Rights:** the example Python code falls under the parent repository's
  [MIT license](../../LICENSE); no third-party art, fonts or audio are bundled.
- **Intentional constraint:** only five lamps and a single puzzle. No package,
  binary build, release notes, hosted deployment or player-account flow exists.
  This keeps the *first-play evidence* reproducible, not representative of a
  full game production pipeline.

For a real game, replace this transcript with evidence from its **actual**
published build, tested platform(s), build/revision identity, current gameplay
media and path-specific asset rights. Adapt the
[game README guide](../../guides/game-repositories.md) and
[template](../../templates/GAME_README.template.md). A CI badge or a source
checkout alone does not prove a store upload works.
