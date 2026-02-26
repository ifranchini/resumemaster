"""Tests for data models."""

from resumemaster.models import (
    ContactInfo,
    FontMap,
    FontMapping,
    FontSpec,
    PageLayout,
    ResumeData,
    RoleStyle,
    SemanticRole,
    SpacingProfile,
    StyleProfile,
    ValidationResult,
)


def test_style_profile_roundtrip():
    """StyleProfile serializes to JSON and back."""
    profile = StyleProfile(
        page_layout=PageLayout(
            width=595.28,
            height=841.89,
            margin_top=40,
            margin_bottom=40,
            margin_left=40,
            margin_right=40,
        ),
        spacing=SpacingProfile(line_height=13, paragraph_spacing=6, section_gap=18),
        role_styles=[
            RoleStyle(
                role=SemanticRole.BODY,
                font=FontSpec(family="Helvetica", size=10),
            ),
        ],
        color_palette=["#000000", "#3d3d3d"],
    )
    json_str = profile.model_dump_json()
    restored = StyleProfile.model_validate_json(json_str)
    assert restored.page_layout.width == 595.28
    assert restored.role_styles[0].font.family == "Helvetica"


def test_font_map_get_path():
    """FontMap.get_path returns correct path or None."""
    fm = FontMap(
        mappings=[
            FontMapping(pdf_name="Arial", local_path="/fonts/Arial.ttf", source="local"),
            FontMapping(pdf_name="Times", local_path=None, source="unresolved"),
        ]
    )
    assert fm.get_path("Arial") == "/fonts/Arial.ttf"
    assert fm.get_path("Times") is None
    assert fm.get_path("Unknown") is None


def test_resume_data_roundtrip():
    """ResumeData serializes to JSON and back."""
    data = ResumeData(
        contact=ContactInfo(name="Test User", email="test@example.com"),
        profile="A test profile.",
        skills={"Languages": ["Python", "Go"]},
    )
    json_str = data.model_dump_json()
    restored = ResumeData.model_validate_json(json_str)
    assert restored.contact.name == "Test User"
    assert restored.skills["Languages"] == ["Python", "Go"]


def test_validation_result_serialization():
    """ValidationResult serializes correctly."""
    result = ValidationResult(
        structural_score=0.85,
        ssim_score=0.72,
        pixel_diff_score=0.90,
        final_score=0.82,
    )
    json_str = result.model_dump_json()
    restored = ValidationResult.model_validate_json(json_str)
    assert restored.final_score == 0.82
