#!/usr/bin/env python3
"""Lantern Row: a tiny, offline, source-only terminal game.

Only built-in Python; no files, network, or telemetry. Switch positions are
1-based for players. This deliberately does not ship a browser or store build.
"""

from __future__ import annotations

import argparse
import sys

LAMP_COUNT = 5
START = (False,) * LAMP_COUNT
DEMO_MOVES = (1, 4)
MAX_MOVES = 10


def toggle(state: tuple[bool, ...], position: int) -> tuple[bool, ...]:
    """Flip the selected lamp and its immediate neighbors without mutation."""
    if len(state) != LAMP_COUNT or not 1 <= position <= LAMP_COUNT:
        raise ValueError(f"choose a switch from 1 to {LAMP_COUNT} (got {position})")
    selected = position - 1
    return tuple(not value if abs(index - selected) <= 1 else value
                 for index, value in enumerate(state))


def display(state: tuple[bool, ...]) -> str:
    return "".join("#" if lit else "." for lit in state) + f" ({sum(state)}/{LAMP_COUNT} lit)"


def play_moves(moves: tuple[int, ...]) -> tuple[list[str], bool]:
    """Produce stable transcript lines. Invalid input fails before any moves."""
    for position in moves:
        if not 1 <= position <= LAMP_COUNT:
            raise ValueError(f"choose a switch from 1 to {LAMP_COUNT} (got {position})")
    if len(moves) > MAX_MOVES:
        raise ValueError(f"at most {MAX_MOVES} moves are allowed")
    state = START
    lines = [f"Start: {display(state)}"]
    for turn, position in enumerate(moves, 1):
        state = toggle(state, position)
        lines.append(f"Switch {position}: {display(state)}")
        if all(state):
            lines.append(f"WIN in {turn} moves")
            return lines, True
    count = len(moves)
    lines.append(f"No win after {count} {'move' if count == 1 else 'moves'}")
    return lines, False


def interactive() -> int:
    state = START
    completed = 0
    print("Lantern Row | turn all five lamps on by flipping neighbors")
    print("Switches: 1 2 3 4 5 | # = lit, . = dark | q = quit")
    print(f"Start: {display(state)}")
    while completed < MAX_MOVES:
        try:
            answer = input("Switch 1-5 (q to quit): ").strip().lower()
        except EOFError:
            answer = "q"
        if answer == "q":
            print(f"Quit after {completed} moves")
            return 0
        if answer not in {str(i) for i in range(1, LAMP_COUNT + 1)}:
            print("Enter a switch number 1-5 or q; no move spent")
            continue
        completed += 1
        state = toggle(state, int(answer))
        print(f"Switch {answer}: {display(state)}")
        if all(state):
            print(f"WIN in {completed} moves")
            return 0
    print(f"No win after {MAX_MOVES} moves")
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Five-lamp, offline terminal puzzle")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--demo", action="store_true", help="replay a reproducible two-move win")
    group.add_argument("--moves", type=int, nargs="+", metavar="N",
                       help="play specified switch numbers (no interaction)")
    arguments = parser.parse_args(argv)
    if not arguments.demo and arguments.moves is None:
        return interactive()
    moves = DEMO_MOVES if arguments.demo else tuple(arguments.moves)
    try:
        lines, won = play_moves(moves)
    except ValueError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    print("Lantern Row | deterministic offline transcript")
    print("\n".join(lines))
    return 0 if won else 1


if __name__ == "__main__":
    raise SystemExit(main())
