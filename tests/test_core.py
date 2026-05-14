"""Tests for music_transpose.core."""

import pytest

from music_transpose.core import (
    Chord,
    Note,
    transpose_chord,
    transpose_chord_chart,
    transpose_note,
    transpose_to_key,
)

# ---------------------------------------------------------------------------
# Note tests
# ---------------------------------------------------------------------------


class TestNote:
    def test_from_name_natural(self):
        assert Note.from_name("C").pitch_class == 0
        assert Note.from_name("G").pitch_class == 7

    def test_from_name_sharp(self):
        assert Note.from_name("F#").pitch_class == 6

    def test_from_name_flat(self):
        n = Note.from_name("Bb")
        assert n.pitch_class == 10
        assert n.prefer_flat is True

    def test_from_name_invalid(self):
        with pytest.raises(ValueError):
            Note.from_name("X")

    def test_transpose_up(self):
        n = Note.from_name("C")
        assert n.transpose(2).name == "D"

    def test_transpose_wraps(self):
        n = Note.from_name("A")
        assert n.transpose(3).name == "C"

    def test_transpose_down(self):
        n = Note.from_name("D")
        assert n.transpose(-2).name == "C"

    def test_transpose_preserves_flat_preference(self):
        n = Note.from_name("Bb")
        assert n.transpose(2).name == "C"
        assert n.transpose(1).name == "B"

    def test_equality(self):
        assert Note.from_name("C#") == Note.from_name("Db")


# ---------------------------------------------------------------------------
# transpose_note tests
# ---------------------------------------------------------------------------


class TestTransposeNote:
    def test_basic_sharp(self):
        assert transpose_note("C", 1) == "C#"

    def test_basic_flat(self):
        assert transpose_note("C", 1, use_flats=True) == "Db"

    def test_full_octave(self):
        assert transpose_note("E", 12) == "E"

    def test_negative_semitones(self):
        assert transpose_note("C", -1) == "B"

    @pytest.mark.parametrize(
        "note,semitones,expected",
        [
            ("C", 0, "C"),
            ("C", 2, "D"),
            ("C", 4, "E"),
            ("C", 5, "F"),
            ("C", 7, "G"),
            ("C", 9, "A"),
            ("C", 11, "B"),
        ],
    )
    def test_c_major_scale(self, note, semitones, expected):
        assert transpose_note(note, semitones) == expected

    def test_enharmonic_input(self):
        assert transpose_note("E#", 0) == "F"


# ---------------------------------------------------------------------------
# Chord tests
# ---------------------------------------------------------------------------


class TestChord:
    def test_parse_simple(self):
        c = Chord.from_symbol("Am")
        assert c.root.name == "A"
        assert c.quality == "m"
        assert c.bass is None

    def test_parse_with_extensions(self):
        c = Chord.from_symbol("Cmaj7")
        assert c.root.name == "C"
        assert c.quality == "maj7"

    def test_parse_with_bass(self):
        c = Chord.from_symbol("C/G")
        assert c.root.name == "C"
        assert c.quality == ""
        assert c.bass is not None
        assert c.bass.name == "G"

    def test_parse_complex(self):
        c = Chord.from_symbol("F#m7b5")
        assert c.root.name == "F#"
        assert c.quality == "m7b5"

    def test_parse_invalid(self):
        with pytest.raises(ValueError):
            Chord.from_symbol("xyz")

    def test_transpose(self):
        c = Chord.from_symbol("Am7")
        t = c.transpose(2)
        assert t.symbol == "Bm7"

    def test_transpose_with_bass(self):
        c = Chord.from_symbol("C/G")
        t = c.transpose(5)
        assert t.symbol == "F/C"

    def test_symbol_roundtrip(self):
        symbols = ["C", "Am7", "F#dim", "Bbmaj7", "D/F#", "Gsus4"]
        for s in symbols:
            assert Chord.from_symbol(s).symbol == s


# ---------------------------------------------------------------------------
# transpose_chord tests
# ---------------------------------------------------------------------------


class TestTransposeChord:
    def test_simple(self):
        assert transpose_chord("Am", 2) == "Bm"

    def test_seventh(self):
        assert transpose_chord("G7", 2) == "A7"

    def test_with_flats(self):
        assert transpose_chord("G7", 3, use_flats=True) == "Bb7"

    def test_slash_chord(self):
        assert transpose_chord("C/G", 5) == "F/C"

    def test_diminished(self):
        assert transpose_chord("Bdim", 1) == "Cdim"

    def test_full_octave(self):
        assert transpose_chord("Dm7", 12) == "Dm7"


# ---------------------------------------------------------------------------
# transpose_to_key tests
# ---------------------------------------------------------------------------


class TestTransposeToKey:
    def test_c_to_g(self):
        result = transpose_to_key(["C", "Am", "F", "G"], "C", "G")
        assert result == ["G", "Em", "C", "D"]

    def test_c_to_f(self):
        result = transpose_to_key(["C", "G", "Am", "F"], "C", "F")
        assert result == ["F", "C", "Dm", "Bb"]

    def test_am_to_em(self):
        result = transpose_to_key(["Am", "Dm", "E7", "Am"], "Am", "Em")
        assert result == ["Em", "Am", "B7", "Em"]

    def test_same_key(self):
        chords = ["C", "F", "G"]
        assert transpose_to_key(chords, "C", "C") == chords

    def test_g_to_a(self):
        result = transpose_to_key(["G", "C", "D"], "G", "A")
        assert result == ["A", "D", "E"]


# ---------------------------------------------------------------------------
# transpose_chord_chart tests
# ---------------------------------------------------------------------------


class TestTransposeChordChart:
    def test_simple_chart(self):
        chart = "Am  G  F  G"
        result = transpose_chord_chart(chart, semitones=2)
        assert "Bm" in result
        assert "A" in result

    def test_with_lyrics(self):
        chart = "Am  G  F  G\nSome lyrics here"
        result = transpose_chord_chart(chart, semitones=2)
        lines = result.split("\n")
        assert "Bm" in lines[0]
        assert lines[1] == "Some lyrics here"

    def test_key_based_chart(self):
        chart = "C  Am  F  G\nVerse lyrics"
        result = transpose_chord_chart(chart, from_key="C", to_key="G")
        lines = result.split("\n")
        assert "G" in lines[0]
        assert lines[1] == "Verse lyrics"

    def test_empty_chart(self):
        assert transpose_chord_chart("", semitones=1) == ""

    def test_preserves_blank_lines(self):
        chart = "Am  G\n\nF  G"
        result = transpose_chord_chart(chart, semitones=0)
        assert "\n\n" in result

    def test_multi_section_chart(self):
        chart = (
            "[Verse]\n"
            "Am  F  C  G\n"
            "Walking down the road\n"
            "\n"
            "[Chorus]\n"
            "F  G  Am\n"
            "Singing out loud"
        )
        result = transpose_chord_chart(chart, semitones=2)
        assert "Bm" in result
        assert "Walking down the road" in result
        assert "Singing out loud" in result

    def test_lyrics_with_note_letter_words_not_corrupted(self):
        chart = "Am  G  F  G\nBlue Eyes\nC  F  G\nCome And Go"
        result = transpose_chord_chart(chart, semitones=2)
        lines = result.split("\n")
        assert "Bm" in lines[0]
        assert lines[1] == "Blue Eyes"
        assert "D" in lines[2]
        assert lines[3] == "Come And Go"

    def test_single_word_lyrics_starting_with_note(self):
        chart = "Am  G\nA man walked down the road"
        result = transpose_chord_chart(chart, semitones=2)
        lines = result.split("\n")
        assert "Bm" in lines[0]
        assert lines[1] == "A man walked down the road"

    def test_all_valid_chord_qualities_still_parse(self):
        valid_chords = [
            "C", "Am", "F#m7", "Bbmaj7", "Bdim", "Gaug",
            "Dsus4", "Asus2", "Dm9", "G7", "Cadd9", "F#m7b5",
        ]
        for chord_str in valid_chords:
            result = transpose_chord(chord_str, 0)
            assert result == chord_str, f"Chord {chord_str} should round-trip"
