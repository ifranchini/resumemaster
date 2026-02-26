"""Shared test fixtures for resumemaster."""

from __future__ import annotations

from pathlib import Path

import pymupdf
import pytest

from resumemaster.models import (
    ContactInfo,
    EducationEntry,
    ExperienceEntry,
    FontMap,
    FontMapping,
    LanguageEntry,
    PublicationEntry,
    ResumeData,
    StyleProfile,
)


@pytest.fixture
def sample_pdf(tmp_path: Path) -> Path:
    """Generate a simple multi-style PDF for testing extraction."""
    pdf_path = tmp_path / "sample.pdf"
    doc = pymupdf.open()
    page = doc.new_page(width=595.28, height=841.89)

    # Name (large, bold)
    page.insert_text(
        pymupdf.Point(40, 50),
        "Jane Doe",
        fontname="hebo",
        fontsize=24,
        color=(0, 0, 0),
    )

    # Heading (medium, bold)
    page.insert_text(
        pymupdf.Point(40, 90),
        "Work Experience",
        fontname="hebo",
        fontsize=14,
        color=(0.2, 0.4, 0.8),
    )

    # Subheading (bold, body size)
    page.insert_text(
        pymupdf.Point(40, 115),
        "Senior Engineer",
        fontname="hebo",
        fontsize=10,
        color=(0, 0, 0),
    )

    # Body text (regular)
    page.insert_text(
        pymupdf.Point(40, 135),
        "Built scalable data pipelines processing 1M+ records daily.",
        fontname="helv",
        fontsize=10,
        color=(0.2, 0.2, 0.2),
    )
    page.insert_text(
        pymupdf.Point(40, 150),
        "Led a team of 5 engineers across 3 time zones.",
        fontname="helv",
        fontsize=10,
        color=(0.2, 0.2, 0.2),
    )

    # Caption/date (small)
    page.insert_text(
        pymupdf.Point(40, 170),
        "01/2020 - 12/2023  |  REMOTE, USA",
        fontname="helv",
        fontsize=8,
        color=(0.5, 0.5, 0.5),
    )

    # Second section (for spacing detection)
    page.insert_text(
        pymupdf.Point(40, 220),
        "Education",
        fontname="hebo",
        fontsize=14,
        color=(0.2, 0.4, 0.8),
    )
    page.insert_text(
        pymupdf.Point(40, 245),
        "MIT",
        fontname="hebo",
        fontsize=10,
        color=(0, 0, 0),
    )
    page.insert_text(
        pymupdf.Point(40, 260),
        "BSc Computer Science",
        fontname="helv",
        fontsize=10,
        color=(0.2, 0.2, 0.2),
    )

    doc.save(str(pdf_path), garbage=4, deflate=True)
    doc.close()
    return pdf_path


@pytest.fixture
def sample_resume_data() -> ResumeData:
    """Sample resume data for generation tests."""
    return ResumeData(
        contact=ContactInfo(
            name="Jane Doe",
            address="San Francisco, CA",
            phone="+1 (555) 123-4567",
            email="jane@example.com",
            linkedin="linkedin.com/in/janedoe",
        ),
        profile=(
            "Senior software engineer with 8+ years of experience "
            "building data-intensive applications and leading teams."
        ),
        experience=[
            ExperienceEntry(
                title="Senior Engineer",
                company="Acme Corp",
                dates="01/2020 - Present",
                location="Remote, USA",
                bullets=[
                    "Built scalable data pipelines processing 1M+ records daily",
                    "Led a team of 5 engineers across 3 time zones",
                ],
            ),
            ExperienceEntry(
                title="Software Engineer",
                company="StartupCo",
                dates="06/2016 - 12/2019",
                location="San Francisco, CA",
                bullets=[
                    "Developed REST APIs serving 10K+ requests per second",
                    "Implemented CI/CD pipelines reducing deployment time by 70%",
                ],
            ),
        ],
        skills={
            "Languages": ["Python", "TypeScript", "Go", "SQL"],
            "Infrastructure": ["AWS", "Docker", "Kubernetes", "Terraform"],
        },
        education=[
            EducationEntry(
                institution="MIT",
                degree="BSc Computer Science",
                dates="09/2012 - 06/2016",
                location="Cambridge, MA",
            ),
        ],
        languages=[
            LanguageEntry(language="English", level="Native"),
            LanguageEntry(language="Spanish", level="Conversational"),
        ],
        publications=[
            PublicationEntry(text="Scaling Data Pipelines at Acme (2022)"),
        ],
    )


@pytest.fixture
def sample_resume_data_json(tmp_path: Path, sample_resume_data: ResumeData) -> Path:
    """Write sample resume data to a JSON file."""
    path = tmp_path / "resume_data.json"
    path.write_text(sample_resume_data.model_dump_json(indent=2))
    return path


@pytest.fixture
def sample_style_profile(sample_pdf: Path) -> StyleProfile:
    """Extract a style profile from the sample PDF."""
    from resumemaster.extractor import StyleExtractor

    with StyleExtractor(sample_pdf) as ext:
        return ext.extract()


@pytest.fixture
def sample_style_json(tmp_path: Path, sample_style_profile: StyleProfile) -> Path:
    """Write sample style profile to a JSON file."""
    path = tmp_path / "style.json"
    path.write_text(sample_style_profile.model_dump_json(indent=2))
    return path


@pytest.fixture
def sample_font_map() -> FontMap:
    """A minimal font map using built-in PyMuPDF fonts."""
    return FontMap(
        mappings=[
            FontMapping(pdf_name="Helvetica", local_path=None, source="builtin"),
            FontMapping(pdf_name="Helvetica-Bold", local_path=None, source="builtin"),
        ]
    )
