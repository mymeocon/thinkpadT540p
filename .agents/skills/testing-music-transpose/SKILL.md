---
name: testing-music-transpose
description: Test the music-transpose Python library and CLI end-to-end. Use when verifying transposition logic, CLI subcommands, or chord chart parsing changes.
---

# Testing music-transpose

## Setup

```bash
cd /home/ubuntu/repos/music-transpose
pip install -e ".[dev]"
```

## Running Unit Tests

```bash
pytest -v
```

## Lint

```bash
ruff check src/ tests/
ruff check --fix src/ tests/  # auto-fix import sorting
```

## CLI Subcommands

The CLI is `music-transpose` with 4 subcommands:

- `music-transpose note <NOTE> <SEMITONES> [--flats]` — transpose a single note
- `music-transpose chord <CHORD> <SEMITONES> [--flats]` — transpose a chord symbol
- `music-transpose key --from <KEY> --to <KEY> <CHORDS...>` — transpose chords between keys
- `echo "chart" | music-transpose chart -s <SEMITONES>` — transpose a chord chart from stdin
- `echo "chart" | music-transpose chart --key <FROM> <TO>` — transpose chart by key

## Key Edge Cases to Test

1. **Negative semitones**: `music-transpose note C -1` should output `B`
2. **Full octave identity**: `music-transpose note E 12` should output `E`
3. **Enharmonic inputs**: `music-transpose note E# 0` should output `F`
4. **Flat preference**: `music-transpose note G 1 --flats` should output `Ab` (not `G#`)
5. **Flat key auto-detection**: When transposing to key F, accidentals should use flats (Bb not A#)
6. **Slash chord transposition**: Both root and bass note must transpose (e.g., C/G +5 = F/C)
7. **Quality preservation**: Chord quality strings (m7, dim, aug, sus4, etc.) must be preserved verbatim
8. **Lyric vs chord line detection**: Lines where most tokens aren't chords should NOT be transposed. Test with "A man walked down the road" which starts with note name "A"
9. **Invalid input handling**: Invalid notes/chords should produce ValueError with descriptive message and non-zero exit code

## Python API

```python
from music_transpose import transpose_note, transpose_chord, transpose_to_key, transpose_chord_chart

transpose_note("C", 2)  # "D"
transpose_chord("Am7", 2)  # "Bm7"
transpose_to_key(["C", "Am", "F", "G"], "C", "G")  # ["G", "Em", "C", "D"]
transpose_chord_chart("Am  G\nLyrics", semitones=2)  # "Bm  A\nLyrics"
```

## Testing Notes

- All testing is CLI/shell-based — no browser recording needed
- No external services or credentials required
- No CI is configured on this repo; rely on local pytest + ruff
