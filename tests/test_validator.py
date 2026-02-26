"""Tests for the style validator."""

from pathlib import Path

import pymupdf

from resumemaster.validator import StyleValidator


def test_validate_identical_pdfs(sample_pdf: Path):
    """Validating a PDF against itself should score near 1.0."""
    validator = StyleValidator(sample_pdf, sample_pdf)
    result = validator.validate()

    assert result.final_score > 0.9
    assert result.ssim_score > 0.9
    assert result.pixel_diff_score > 0.9
    assert result.structural_score > 0.9


def test_validate_produces_page_scores(sample_pdf: Path):
    """Validation produces per-page scores."""
    validator = StyleValidator(sample_pdf, sample_pdf)
    result = validator.validate()

    assert len(result.page_scores) == 1  # sample PDF has 1 page
    assert result.page_scores[0].page == 0


def test_validate_diff_images(sample_pdf: Path, tmp_path: Path):
    """Validation can produce diff images."""
    diff_dir = tmp_path / "diffs"
    validator = StyleValidator(sample_pdf, sample_pdf)
    result = validator.validate(diff_dir=str(diff_dir))

    assert result.page_scores[0].diff_image_path is not None
    assert Path(result.page_scores[0].diff_image_path).exists()


def test_validate_different_pdfs(sample_pdf: Path, tmp_path: Path):
    """Validating different PDFs should give a lower score than identical."""
    # Create a different PDF
    other_pdf = tmp_path / "other.pdf"
    doc = pymupdf.open()
    page = doc.new_page(width=595.28, height=841.89)
    page.insert_text(
        pymupdf.Point(100, 100),
        "Completely different content",
        fontname="helv",
        fontsize=20,
        color=(1, 0, 0),
    )
    doc.save(str(other_pdf))
    doc.close()

    validator = StyleValidator(sample_pdf, other_pdf)
    result = validator.validate()

    # Should be lower than identical comparison
    assert result.final_score < 0.95


def test_validate_result_serialization(sample_pdf: Path):
    """ValidationResult serializes to JSON."""
    validator = StyleValidator(sample_pdf, sample_pdf)
    result = validator.validate()

    json_str = result.model_dump_json()
    from resumemaster.models import ValidationResult

    restored = ValidationResult.model_validate_json(json_str)
    assert abs(restored.final_score - result.final_score) < 0.001
