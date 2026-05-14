"""Core music transposition logic."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional

# Chromatic scale using sharps
SHARP_NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# Chromatic scale using flats
FLAT_NOTES = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]

# Enharmonic mapping to normalize note names
ENHARMONIC_MAP = {
    "C": 0, "B#": 0,
    "C#": 1, "Db": 1,
    "D": 2,
    "D#": 3, "Eb": 3,
    "E": 4, "Fb": 4,
    "F": 5, "E#": 5,
    "F#": 6, "Gb": 6,
    "G": 7,
    "G#": 8, "Ab": 8,
    "A": 9,
    "A#": 10, "Bb": 10,
    "B": 11, "Cb": 11,
}

# Keys that conventionally use flats
FLAT_KEYS = {"F", "Bb", "Eb", "Ab", "Db", "Gb", "Dm", "Gm", "Cm", "Fm", "Bbm", "Ebm"}

# Major scale intervals (in semitones from root)
MAJOR_SCALE_INTERVALS = [0, 2, 4, 5, 7, 9, 11]

# Minor scale intervals (in semitones from root)
MINOR_SCALE_INTERVALS = [0, 2, 3, 5, 7, 8, 10]

# Regex to parse a chord symbol: root note + optional quality/extensions
# The quality group is restricted to valid chord suffixes to avoid matching
# English words like "Blue", "Come", "And", etc.
CHORD_PATTERN = re.compile(
    r"^([A-G][#b]?)"
    r"((?:maj|min|m|M|dim|aug|sus|add|no)?"
    r"(?:[0-9]+)?"
    r"(?:[#b][0-9]+)*"
    r"(?:sus[24])?"
    r"(?:add[0-9]+)?)"
    r"(/([A-G][#b]?))?$"
)


@dataclass
class Note:
    """Represents a musical note with a pitch class (0-11)."""

    pitch_class: int
    prefer_flat: bool = False

    @classmethod
    def from_name(cls, name: str) -> Note:
        """Create a Note from a note name like 'C#' or 'Bb'."""
        name = _normalize_accidental(name)
        if name not in ENHARMONIC_MAP:
            raise ValueError(f"Unknown note: {name}")
        prefer_flat = "b" in name and name not in ("B",)
        return cls(pitch_class=ENHARMONIC_MAP[name], prefer_flat=prefer_flat)

    @property
    def name(self) -> str:
        """Return the canonical name of this note."""
        scale = FLAT_NOTES if self.prefer_flat else SHARP_NOTES
        return scale[self.pitch_class % 12]

    def transpose(self, semitones: int) -> Note:
        """Return a new Note transposed by the given number of semitones."""
        return Note(
            pitch_class=(self.pitch_class + semitones) % 12,
            prefer_flat=self.prefer_flat,
        )

    def __repr__(self) -> str:
        return f"Note({self.name})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Note):
            return NotImplemented
        return self.pitch_class == other.pitch_class


@dataclass
class Chord:
    """Represents a chord with a root note, quality string, and optional bass note."""

    root: Note
    quality: str
    bass: Optional[Note] = None

    @classmethod
    def from_symbol(cls, symbol: str) -> Chord:
        """Parse a chord symbol like 'Am7', 'F#m', 'C/G', 'Bbmaj7/D'."""
        symbol = symbol.strip()
        match = CHORD_PATTERN.match(symbol)
        if not match:
            raise ValueError(f"Cannot parse chord symbol: {symbol}")

        root_name = match.group(1)
        quality = match.group(2) or ""
        bass_name = match.group(4)

        root = Note.from_name(root_name)
        bass = Note.from_name(bass_name) if bass_name else None

        return cls(root=root, quality=quality, bass=bass)

    @property
    def symbol(self) -> str:
        """Return the chord symbol string."""
        result = self.root.name + self.quality
        if self.bass is not None:
            result += "/" + self.bass.name
        return result

    def transpose(self, semitones: int) -> Chord:
        """Return a new Chord transposed by the given number of semitones."""
        new_root = self.root.transpose(semitones)
        new_bass = self.bass.transpose(semitones) if self.bass else None
        return Chord(root=new_root, quality=self.quality, bass=new_bass)

    def __repr__(self) -> str:
        return f"Chord({self.symbol})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Chord):
            return NotImplemented
        return self.root == other.root and self.quality == other.quality and self.bass == other.bass


def transpose_note(note_name: str, semitones: int, use_flats: bool = False) -> str:
    """Transpose a single note name by a number of semitones.

    Args:
        note_name: The note to transpose (e.g., 'C', 'F#', 'Bb').
        semitones: Number of semitones to transpose (positive = up, negative = down).
        use_flats: If True, prefer flat names for accidentals.

    Returns:
        The transposed note name.

    Examples:
        >>> transpose_note("C", 2)
        'D'
        >>> transpose_note("A", 3)
        'C'
        >>> transpose_note("G", 1, use_flats=True)
        'Ab'
    """
    note = Note.from_name(note_name)
    note.prefer_flat = use_flats or note.prefer_flat
    transposed = note.transpose(semitones)
    return transposed.name


def transpose_chord(chord_symbol: str, semitones: int, use_flats: bool = False) -> str:
    """Transpose a chord symbol by a number of semitones.

    Args:
        chord_symbol: The chord to transpose (e.g., 'Am7', 'F#dim', 'C/G').
        semitones: Number of semitones to transpose.
        use_flats: If True, prefer flat names for accidentals.

    Returns:
        The transposed chord symbol.

    Examples:
        >>> transpose_chord("Am", 2)
        'Bm'
        >>> transpose_chord("G7", 3)
        'A#7'
        >>> transpose_chord("G7", 3, use_flats=True)
        'Bb7'
        >>> transpose_chord("C/G", 5)
        'F/C'
    """
    chord = Chord.from_symbol(chord_symbol)
    if use_flats:
        chord.root.prefer_flat = True
        if chord.bass:
            chord.bass.prefer_flat = True
    transposed = chord.transpose(semitones)
    return transposed.symbol


def transpose_to_key(
    chord_symbols: List[str],
    from_key: str,
    to_key: str,
) -> List[str]:
    """Transpose a list of chord symbols from one key to another.

    Args:
        chord_symbols: List of chord symbols to transpose.
        from_key: The source key (e.g., 'C', 'Am', 'F#', 'Bbm').
        to_key: The target key (e.g., 'G', 'Em', 'A', 'Dm').

    Returns:
        List of transposed chord symbols.

    Examples:
        >>> transpose_to_key(["C", "Am", "F", "G"], "C", "G")
        ['G', 'Em', 'C', 'D']
        >>> transpose_to_key(["Am", "Dm", "E7", "Am"], "Am", "Em")
        ['Em', 'Am', 'B7', 'Em']
    """
    from_root = Note.from_name(_strip_minor(from_key))
    to_root = Note.from_name(_strip_minor(to_key))
    semitones = (to_root.pitch_class - from_root.pitch_class) % 12

    use_flats = to_key in FLAT_KEYS
    return [transpose_chord(cs, semitones, use_flats=use_flats) for cs in chord_symbols]


def transpose_chord_chart(
    chart: str,
    semitones: int = 0,
    from_key: Optional[str] = None,
    to_key: Optional[str] = None,
    use_flats: bool = False,
) -> str:
    """Transpose an entire chord chart (text with inline chord symbols).

    Chords are detected as tokens matching the chord pattern. Lines that look like
    lyrics with chords above them are handled. Provide either `semitones` for direct
    transposition, or `from_key`/`to_key` for key-based transposition.

    Args:
        chart: The chord chart text with chord symbols.
        semitones: Number of semitones to transpose (used if from_key/to_key not set).
        from_key: Source key for key-based transposition.
        to_key: Target key for key-based transposition.
        use_flats: Prefer flat accidentals in output.

    Returns:
        The transposed chord chart text.

    Examples:
        >>> chart = "Am  G  F  G\\nSome lyrics here"
        >>> transpose_chord_chart(chart, semitones=2)
        'Bm  A  G  A\\nSome lyrics here'
    """
    if from_key and to_key:
        from_root = Note.from_name(_strip_minor(from_key))
        to_root = Note.from_name(_strip_minor(to_key))
        semitones = (to_root.pitch_class - from_root.pitch_class) % 12
        use_flats = use_flats or to_key in FLAT_KEYS

    lines = chart.split("\n")
    result_lines = []

    for line in lines:
        if _is_chord_line(line):
            result_lines.append(_transpose_chord_line(line, semitones, use_flats))
        else:
            result_lines.append(line)

    return "\n".join(result_lines)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _normalize_accidental(name: str) -> str:
    """Normalize accidental characters (e.g., unicode sharp/flat)."""
    return name.replace("\u266f", "#").replace("\u266d", "b")


def _strip_minor(key: str) -> str:
    """Strip trailing 'm' from a minor key name to get the root note."""
    if key.endswith("m") and key not in ("Am", "Bm", "Cm", "Dm", "Em", "Fm", "Gm"):
        # Handle cases like 'Bbm', 'F#m'
        root = key[:-1]
    elif len(key) >= 2 and key[-1] == "m" and key[-2] not in ("#", "b"):
        root = key[:-1]
    else:
        root = key
    # For keys like 'Am', 'Bbm', etc., strip the 'm'
    if key.endswith("m"):
        root = key[:-1]
    return root


def _is_chord_line(line: str) -> bool:
    """Heuristic to detect if a line is a chord line vs. a lyric line."""
    stripped = line.strip()
    if not stripped:
        return False

    tokens = stripped.split()
    if not tokens:
        return False

    chord_count = sum(1 for t in tokens if _looks_like_chord(t))
    # Consider it a chord line if more than half the tokens are chords
    return chord_count > len(tokens) / 2


def _looks_like_chord(token: str) -> bool:
    """Check if a token looks like a chord symbol."""
    # Remove common surrounding punctuation
    token = token.strip("()|[]")
    if not token:
        return False
    return CHORD_PATTERN.match(token) is not None


def _transpose_chord_line(line: str, semitones: int, use_flats: bool) -> str:
    """Transpose all chords in a chord line while preserving spacing."""
    result = []
    i = 0
    while i < len(line):
        if line[i] == " ":
            result.append(" ")
            i += 1
            continue

        # Try to extract a chord token
        j = i
        while j < len(line) and line[j] != " ":
            j += 1
        token = line[i:j]

        # Check if it's a chord
        clean = token.strip("()|[]")
        prefix = token[: token.index(clean[0])] if clean and clean[0] in token else ""
        suffix = token[len(prefix) + len(clean) :] if clean else ""

        if _looks_like_chord(clean):
            transposed = transpose_chord(clean, semitones, use_flats)
            result.append(prefix + transposed + suffix)
        else:
            result.append(token)

        i = j

    return "".join(result)
