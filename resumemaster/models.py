"""Pydantic data models for the resumemaster pipeline."""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class FontWeight(StrEnum):
    THIN = "thin"
    LIGHT = "light"
    REGULAR = "regular"
    MEDIUM = "medium"
    SEMIBOLD = "semibold"
    BOLD = "bold"
    EXTRABOLD = "extrabold"
    BLACK = "black"


class FontStyle(StrEnum):
    NORMAL = "normal"
    ITALIC = "italic"


class SemanticRole(StrEnum):
    NAME = "name"
    HEADING = "heading"
    SUBHEADING = "subheading"
    BODY = "body"
    CAPTION = "caption"
    DATE = "date"


# ---------------------------------------------------------------------------
# Style Profile
# ---------------------------------------------------------------------------


class PageLayout(BaseModel):
    width: float
    height: float
    margin_top: float
    margin_bottom: float
    margin_left: float
    margin_right: float
    has_sidebar: bool = False
    sidebar_width: float = 0.0
    divider_x: float = 0.0
    content_x: float = 0.0


class SpacingProfile(BaseModel):
    line_height: float
    paragraph_spacing: float
    section_gap: float


class FontSpec(BaseModel):
    family: str
    size: float
    weight: FontWeight = FontWeight.REGULAR
    style: FontStyle = FontStyle.NORMAL
    color_hex: str = "#000000"


class RoleStyle(BaseModel):
    role: SemanticRole
    font: FontSpec


class EmbeddedFont(BaseModel):
    pdf_name: str
    xref: int
    ext: str
    path: str | None = None


class StyleProfile(BaseModel):
    """Complete style profile extracted from a PDF."""

    page_layout: PageLayout
    spacing: SpacingProfile
    role_styles: list[RoleStyle]
    color_palette: list[str] = Field(default_factory=list)
    raw_font_specs: list[FontSpec] = Field(default_factory=list)
    embedded_fonts: list[EmbeddedFont] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Font Map
# ---------------------------------------------------------------------------


class FontMapping(BaseModel):
    pdf_name: str
    local_path: str | None = None
    source: str = "unknown"
    fallback_suggestion: str | None = None


class FontMap(BaseModel):
    """Maps PDF font names to resolved local font file paths."""

    mappings: list[FontMapping] = Field(default_factory=list)

    def get_path(self, pdf_name: str) -> str | None:
        """Return local path for a PDF font name, or None."""
        for m in self.mappings:
            if m.pdf_name == pdf_name:
                return m.local_path
        return None

    def get_path_or_fallback(self, pdf_name: str) -> str | None:
        """Return local path, falling back to embedded path from suggestion."""
        for m in self.mappings:
            if m.pdf_name == pdf_name:
                if m.local_path and Path(m.local_path).exists():
                    return m.local_path
                return None
        return None


# ---------------------------------------------------------------------------
# Resume Data
# ---------------------------------------------------------------------------


class ContactInfo(BaseModel):
    name: str
    address: str = ""
    phone: str = ""
    email: str = ""
    linkedin: str = ""
    github: str = ""
    website: str = ""


class ExperienceEntry(BaseModel):
    title: str
    company: str
    dates: str
    location: str = ""
    bullets: list[str] = Field(default_factory=list)


class EducationEntry(BaseModel):
    institution: str
    degree: str
    dates: str
    location: str = ""


class LanguageEntry(BaseModel):
    language: str
    level: str


class PublicationEntry(BaseModel):
    text: str


class CertificationEntry(BaseModel):
    name: str
    issuer: str = ""
    date: str = ""


class ResumeData(BaseModel):
    """Structured resume content for generation."""

    contact: ContactInfo
    profile: str = ""
    experience: list[ExperienceEntry] = Field(default_factory=list)
    skills: dict[str, list[str]] = Field(default_factory=dict)
    education: list[EducationEntry] = Field(default_factory=list)
    languages: list[LanguageEntry] = Field(default_factory=list)
    publications: list[PublicationEntry] = Field(default_factory=list)
    certifications: list[CertificationEntry] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Validation Result
# ---------------------------------------------------------------------------


class PageScore(BaseModel):
    page: int
    structural: float
    ssim: float
    pixel_diff: float
    combined: float
    diff_image_path: str | None = None


class ValidationResult(BaseModel):
    """Validation scores comparing original and generated PDFs."""

    structural_score: float
    ssim_score: float
    pixel_diff_score: float
    final_score: float
    page_scores: list[PageScore] = Field(default_factory=list)
    details: dict = Field(default_factory=dict)
