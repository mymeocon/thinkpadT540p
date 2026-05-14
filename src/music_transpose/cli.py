"""Command-line interface for music-transpose."""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from music_transpose.core import (
    transpose_chord,
    transpose_chord_chart,
    transpose_note,
    transpose_to_key,
)


def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(
        prog="music-transpose",
        description="Transpose notes, chords, keys, and chord charts.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- note sub-command ---
    p_note = subparsers.add_parser("note", help="Transpose a single note by semitones")
    p_note.add_argument("note", help="Note name (e.g. C, F#, Bb)")
    p_note.add_argument("semitones", type=int, help="Semitones to transpose (positive=up)")
    p_note.add_argument("--flats", action="store_true", help="Prefer flat accidentals")

    # --- chord sub-command ---
    p_chord = subparsers.add_parser("chord", help="Transpose a chord symbol by semitones")
    p_chord.add_argument("chord", help="Chord symbol (e.g. Am7, F#dim, C/G)")
    p_chord.add_argument("semitones", type=int, help="Semitones to transpose")
    p_chord.add_argument("--flats", action="store_true", help="Prefer flat accidentals")

    # --- key sub-command ---
    p_key = subparsers.add_parser("key", help="Transpose chords from one key to another")
    p_key.add_argument("--from", dest="from_key", required=True, help="Source key (e.g. C, Am)")
    p_key.add_argument("--to", dest="to_key", required=True, help="Target key (e.g. G, Em)")
    p_key.add_argument("chords", nargs="+", help="Chord symbols to transpose")

    # --- chart sub-command ---
    p_chart = subparsers.add_parser("chart", help="Transpose a chord chart (reads from stdin)")
    p_chart_group = p_chart.add_mutually_exclusive_group(required=True)
    p_chart_group.add_argument("-s", "--semitones", type=int, help="Semitones to transpose")
    p_chart_group.add_argument("--key", nargs=2, metavar=("FROM", "TO"), help="Transpose by key")
    p_chart.add_argument("--flats", action="store_true", help="Prefer flat accidentals")

    args = parser.parse_args(argv)

    if args.command == "note":
        print(transpose_note(args.note, args.semitones, use_flats=args.flats))

    elif args.command == "chord":
        print(transpose_chord(args.chord, args.semitones, use_flats=args.flats))

    elif args.command == "key":
        result = transpose_to_key(args.chords, args.from_key, args.to_key)
        print(" ".join(result))

    elif args.command == "chart":
        chart_text = sys.stdin.read()
        if args.key:
            from_key, to_key = args.key
            print(
                transpose_chord_chart(
                    chart_text, from_key=from_key, to_key=to_key, use_flats=args.flats
                )
            )
        else:
            print(
                transpose_chord_chart(
                    chart_text, semitones=args.semitones, use_flats=args.flats
                )
            )


if __name__ == "__main__":
    main()
