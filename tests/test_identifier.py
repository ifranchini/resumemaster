"""Tests for the font identifier."""

from pathlib import Path

from resumemaster.identifier import FontIdentifier, _normalize_name, _strip_subset_prefix
from resumemaster.models import StyleProfile


def test_strip_subset_prefix():
    assert _strip_subset_prefix("ABCDEF+ArialBold") == "ArialBold"
    assert _strip_subset_prefix("ArialBold") == "ArialBold"
    assert _strip_subset_prefix("abcdef+NotPrefix") == "abcdef+NotPrefix"


def test_normalize_name():
    assert _normalize_name("Arial-Bold") == "arialbold"
    assert _normalize_name("ABCDEF+Helvetica Neue") == "helveticaneue"
    assert _normalize_name("Times_New_Roman") == "timesnewroman"


def test_identifier_scans_fonts():
    """FontIdentifier builds a font index without errors."""
    identifier = FontIdentifier()
    # The index should be populated (macOS has system fonts)
    assert len(identifier.font_index) > 0


def test_identify_from_profile(sample_style_profile: StyleProfile):
    """FontIdentifier produces a FontMap from a StyleProfile."""
    identifier = FontIdentifier()
    font_map = identifier.identify(sample_style_profile)

    assert len(font_map.mappings) > 0
    for m in font_map.mappings:
        assert m.pdf_name  # every mapping has a name


def test_google_fonts_suggestion():
    """FontIdentifier suggests Google Fonts alternatives."""
    identifier = FontIdentifier()
    suggestion = identifier._suggest_google_font("Helvetica")
    assert suggestion == "Inter"


def test_google_fonts_suggestion_unknown():
    """Unknown fonts get no suggestion."""
    identifier = FontIdentifier()
    suggestion = identifier._suggest_google_font("CompletelyMadeUpFont")
    assert suggestion is None


def test_extra_font_dirs(tmp_path: Path):
    """FontIdentifier accepts extra font directories."""
    # Create a fake font file
    fake_font = tmp_path / "CustomFont-Regular.ttf"
    fake_font.write_bytes(b"\x00" * 100)

    identifier = FontIdentifier(extra_font_dirs=[str(tmp_path)])
    assert "customfontregular" in identifier.font_index
