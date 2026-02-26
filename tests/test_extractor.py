"""Tests for the style extractor."""

from pathlib import Path

from resumemaster.extractor import StyleExtractor
from resumemaster.models import SemanticRole


def test_extract_produces_valid_profile(sample_pdf: Path):
    """Extractor produces a StyleProfile with expected fields."""
    with StyleExtractor(sample_pdf) as ext:
        profile = ext.extract()

    assert profile.page_layout.width > 0
    assert profile.page_layout.height > 0
    assert len(profile.raw_font_specs) > 0
    assert len(profile.color_palette) > 0


def test_extract_detects_multiple_sizes(sample_pdf: Path):
    """Extractor detects different font sizes in the sample PDF."""
    with StyleExtractor(sample_pdf) as ext:
        profile = ext.extract()

    sizes = {spec.size for spec in profile.raw_font_specs}
    # Our sample has 24pt (name), 14pt (heading), 10pt (body), 8pt (caption)
    assert len(sizes) >= 3


def test_extract_assigns_roles(sample_pdf: Path):
    """Extractor assigns semantic roles."""
    with StyleExtractor(sample_pdf) as ext:
        profile = ext.extract()

    roles = {rs.role for rs in profile.role_styles}
    # Should detect at least NAME (24pt) and BODY (10pt)
    assert SemanticRole.NAME in roles


def test_extract_detects_colors(sample_pdf: Path):
    """Extractor extracts a color palette."""
    with StyleExtractor(sample_pdf) as ext:
        profile = ext.extract()

    assert len(profile.color_palette) >= 2


def test_extract_spacing(sample_pdf: Path):
    """Extractor detects spacing values."""
    with StyleExtractor(sample_pdf) as ext:
        profile = ext.extract()

    assert profile.spacing.line_height > 0
    assert profile.spacing.section_gap > profile.spacing.line_height


def test_extract_with_font_output(sample_pdf: Path, tmp_path: Path):
    """Extractor can run with font output dir (even if no fonts to extract)."""
    font_dir = tmp_path / "fonts"
    with StyleExtractor(sample_pdf) as ext:
        profile = ext.extract(font_output_dir=font_dir)

    # Built-in fonts can't be extracted, so embedded list may be empty or have no paths
    assert isinstance(profile.embedded_fonts, list)


def test_profile_json_roundtrip(sample_pdf: Path):
    """Extracted profile survives JSON serialization."""
    with StyleExtractor(sample_pdf) as ext:
        profile = ext.extract()

    from resumemaster.models import StyleProfile

    json_str = profile.model_dump_json()
    restored = StyleProfile.model_validate_json(json_str)
    assert restored.page_layout.width == profile.page_layout.width
