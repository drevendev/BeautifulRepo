"""Black-box and pure-function regressions for the source-only game starter."""
from __future__ import annotations

import importlib.util
import re
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "examples/game-starter/lantern_row.py"


def load_game():
    spec = importlib.util.spec_from_file_location("lantern_row", GAME)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class GameStarterTests(unittest.TestCase):
    def invoke(self, *args: str, stdin: str | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-I", str(GAME), *args],
            input=stdin, capture_output=True, text=True, encoding="utf-8",
            timeout=10, check=False,
        )

    def test_neighbors_and_boundaries(self):
        game = load_game()
        self.assertEqual((True, True, False, False, False), game.toggle(game.START, 1))
        self.assertEqual((False, True, True, True, False), game.toggle(game.START, 3))
        self.assertEqual((False, False, False, True, True), game.toggle(game.START, 5))
        self.assertEqual(game.START, game.toggle(game.toggle(game.START, 1), 1))

    def test_pure_function_does_not_mutate_input(self):
        game = load_game()
        state = game.START
        self.assertEqual(5, len(game.toggle(state, 2)))
        self.assertEqual((False,) * 5, state)

    def test_demo_has_exact_reproducible_win(self):
        run = self.invoke("--demo")
        self.assertEqual(0, run.returncode, run.stderr)
        self.assertEqual(
            "Lantern Row | deterministic offline transcript\n"
            "Start: ..... (0/5 lit)\n"
            "Switch 1: ##... (2/5 lit)\n"
            "Switch 4: ##### (5/5 lit)\n"
            "WIN in 2 moves\n", run.stdout,
        )
        self.assertEqual("", run.stderr)

    def test_scripted_first_success_matches_demo(self):
        self.assertEqual(self.invoke("--demo").stdout, self.invoke("--moves", "1", "4").stdout)

    def test_undone_game_returns_one_without_claiming_victory(self):
        run = self.invoke("--moves", "2")
        self.assertEqual(1, run.returncode)
        self.assertIn("No win after 1 move", run.stdout)
        self.assertNotIn("WIN", run.stdout)

    def test_invalid_move_rejected_before_partial_transcript(self):
        run = self.invoke("--moves", "1", "9")
        self.assertEqual(2, run.returncode)
        self.assertEqual("", run.stdout)
        self.assertIn("choose a switch from 1 to 5 (got 9)", run.stderr)

    def test_too_many_moves_are_rejected(self):
        run = self.invoke("--moves", *(["1"] * 11))
        self.assertEqual(2, run.returncode)
        self.assertIn("at most 10 moves", run.stderr)
        self.assertEqual("", run.stdout)

    def test_interactive_invalid_input_does_not_use_turn(self):
        run = self.invoke(stdin="oops\n1\n4\n")
        self.assertEqual(0, run.returncode, run.stdout + run.stderr)
        self.assertIn("no move spent", run.stdout)
        self.assertIn("WIN in 2 moves", run.stdout)

    def test_interactive_quit_and_eof_do_not_crash(self):
        quit_run = self.invoke(stdin="q\n")
        self.assertEqual(0, quit_run.returncode)
        self.assertIn("Quit after 0 moves", quit_run.stdout)
        eof = self.invoke(stdin="")
        self.assertEqual(0, eof.returncode)
        self.assertIn("Quit after 0 moves", eof.stdout)

    @staticmethod
    def readme_fence(section: str, language: str) -> str:
        """Read one documented code block; reject missing or ambiguous evidence."""
        text = (ROOT / "examples/game-starter/README.md").read_text(encoding="utf-8")
        heading = f"## {section}\n"
        if text.count(heading) != 1:
            raise AssertionError(f"expected one README section: {section}")
        body = text.split(heading, 1)[1].split("\n## ", 1)[0]
        blocks = re.findall(rf"(?ms)^~~~{re.escape(language)}\n(.*?)^~~~ *$", body)
        if len(blocks) != 1:
            raise AssertionError(f"expected one {language} block in {section}")
        return blocks[0]

    def test_readme_demo_transcript_matches_live_program(self):
        section = "First success: see a reproducible win"
        # Never execute arbitrary commands extracted from the README.
        self.assertEqual(self.readme_fence(section, "sh").strip(),
                         "python -I examples/game-starter/lantern_row.py --demo")
        run = self.invoke("--demo")
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(self.readme_fence(section, "text"), run.stdout)

    def test_readme_invalid_input_transcript_matches_live_program(self):
        section = "Show a failure, not just a happy screenshot"
        self.assertEqual(self.readme_fence(section, "sh").strip(),
                         "python -I examples/game-starter/lantern_row.py --moves 9")
        run = self.invoke("--moves", "9")
        self.assertEqual(run.returncode, 2)
        self.assertEqual(self.readme_fence(section, "text"), run.stderr)

    def test_game_is_offline_and_has_no_storage_or_external_imports(self):
        source = GAME.read_text(encoding="utf-8")
        for prohibited in ("requests", "urllib", "socket", "open(", "write_text", "subprocess"):
            self.assertNotIn(prohibited, source)


if __name__ == "__main__":
    unittest.main()
