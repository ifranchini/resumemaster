"""Tests for the resume generators."""

from pathlib import Path

import pymupdf

from resumemaster.generator.pymupdf_gen import PyMuPDFGenerator
from resumemaster.models import FontMap, ResumeData, StyleProfile


def test_pymupdf_generates_pdf(
    sample_style_profile: StyleProfile,
    sample_font_map: FontMap,
    sample_resume_data: ResumeData,
    tmp_path: Path,
):
    """PyMuPDFGenerator produces a valid PDF."""
    output = tmp_path / "output.pdf"
    gen = PyMuPDFGenerator(sample_style_profile, sample_font_map, sample_resume_data)
    result = gen.generate(output)

    assert result.exists()
    assert result.stat().st_size > 0

    # Verify it's a valid PDF
    doc = pymupdf.open(str(result))
    assert len(doc) >= 1
    doc.close()


def test_pymupdf_contains_name(
    sample_style_profile: StyleProfile,
    sample_font_map: FontMap,
    sample_resume_data: ResumeData,
    tmp_path: Path,
):
    """Generated PDF contains the contact name."""
    output = tmp_path / "output.pdf"
    gen = PyMuPDFGenerator(sample_style_profile, sample_font_map, sample_resume_data)
    gen.generate(output)

    doc = pymupdf.open(str(output))
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()

    assert "Jane Doe" in text


def test_pymupdf_contains_sections(
    sample_style_profile: StyleProfile,
    sample_font_map: FontMap,
    sample_resume_data: ResumeData,
    tmp_path: Path,
):
    """Generated PDF contains expected section content."""
    output = tmp_path / "output.pdf"
    gen = PyMuPDFGenerator(sample_style_profile, sample_font_map, sample_resume_data)
    gen.generate(output)

    doc = pymupdf.open(str(output))
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()

    assert "Acme Corp" in text
    assert "MIT" in text
    assert "Python" in text


def test_pymupdf_empty_sections(
    sample_style_profile: StyleProfile,
    sample_font_map: FontMap,
    tmp_path: Path,
):
    """Generator handles ResumeData with only contact info."""
    from resumemaster.models import ContactInfo

    data = ResumeData(contact=ContactInfo(name="Minimal Resume"))
    output = tmp_path / "minimal.pdf"
    gen = PyMuPDFGenerator(sample_style_profile, sample_font_map, data)
    result = gen.generate(output)

    assert result.exists()
    doc = pymupdf.open(str(result))
    assert len(doc) >= 1
    doc.close()


def test_pymupdf_page_dimensions(
    sample_style_profile: StyleProfile,
    sample_font_map: FontMap,
    sample_resume_data: ResumeData,
    tmp_path: Path,
):
    """Generated PDF has correct page dimensions from StyleProfile."""
    output = tmp_path / "output.pdf"
    gen = PyMuPDFGenerator(sample_style_profile, sample_font_map, sample_resume_data)
    gen.generate(output)

    doc = pymupdf.open(str(output))
    page = doc[0]
    # Should match the style profile (A4)
    assert abs(page.rect.width - sample_style_profile.page_layout.width) < 1
    assert abs(page.rect.height - sample_style_profile.page_layout.height) < 1
    doc.close()
