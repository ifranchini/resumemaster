"""PyMuPDF-based resume generator."""

from __future__ import annotations

from pathlib import Path

import pymupdf

from resumemaster.generator.base import BaseGenerator
from resumemaster.models import FontMap, ResumeData, StyleProfile

# Built-in PyMuPDF font names as fallback
_BUILTIN_REGULAR = "helv"
_BUILTIN_BOLD = "hebo"
_BUILTIN_ITALIC = "hebi"


class PyMuPDFGenerator(BaseGenerator):
    """Generate a resume PDF using PyMuPDF, parameterized by StyleProfile."""

    def __init__(
        self,
        style: StyleProfile,
        fonts: FontMap,
        data: ResumeData,
    ):
        super().__init__(style, fonts, data)
        self.doc = pymupdf.open()
        self.page = None
        self.y = 0.0
        self.page_num = 0
        self.current_section_label: str | None = None
        self.section_label_written = False

        # Resolve layout from style profile
        layout = self.style.page_layout
        self.page_width = layout.width
        self.page_height = layout.height
        self.margin_top = layout.margin_top
        self.margin_bottom = layout.margin_bottom
        self.margin_left = layout.margin_left
        self.margin_right = layout.margin_right
        self.has_sidebar = layout.has_sidebar
        self.sidebar_width = layout.sidebar_width
        self.divider_x = layout.divider_x
        self.content_x = layout.content_x if layout.has_sidebar else layout.margin_left
        self.content_width = self.page_width - self.content_x - self.margin_right

        # Spacing
        sp = self.style.spacing
        self.line_height = sp.line_height
        self.paragraph_spacing = sp.paragraph_spacing
        self.section_gap = sp.section_gap

        # Color palette
        self.accent_color = self._hex_to_rgb(
            self.style.color_palette[0] if self.style.color_palette else "#000000"
        )
        self.text_color = self._hex_to_rgb(
            self.style.color_palette[1] if len(self.style.color_palette) > 1 else "#3d3d3d"
        )
        self.muted_color = (0.55, 0.55, 0.55)
        self.black = (0, 0, 0)

        # Font resolution: map roles to (fontname, fontfile) pairs
        self._font_objects: dict[str, pymupdf.Font] = {}
        self._font_names: dict[str, tuple[str, str | None]] = {}
        self._resolve_fonts()

    # ------------------------------------------------------------------
    # Font resolution
    # ------------------------------------------------------------------

    def _resolve_fonts(self):
        """Build font name/file mappings for each role."""
        for rs in self.style.role_styles:
            font_path = self._get_font_path(rs.font.family)
            role = rs.role.value

            if font_path and Path(font_path).exists():
                # Sanitize: PyMuPDF fontnames cannot contain spaces
                font_name = Path(font_path).stem.replace(" ", "")
                self._font_names[role] = (font_name, font_path)
                self._font_objects[role] = pymupdf.Font(fontfile=font_path)
            else:
                # Fallback to built-in fonts
                if rs.font.weight.value in ("bold", "semibold", "extrabold", "black"):
                    self._font_names[role] = (_BUILTIN_BOLD, None)
                elif rs.font.style.value == "italic":
                    self._font_names[role] = (_BUILTIN_ITALIC, None)
                else:
                    self._font_names[role] = (_BUILTIN_REGULAR, None)

        # Ensure we always have body/heading/name defaults
        for role, default in [
            ("body", (_BUILTIN_REGULAR, None)),
            ("heading", (_BUILTIN_BOLD, None)),
            ("name", (_BUILTIN_BOLD, None)),
            ("subheading", (_BUILTIN_BOLD, None)),
            ("caption", (_BUILTIN_REGULAR, None)),
        ]:
            if role not in self._font_names:
                self._font_names[role] = default

    def _get_fontname(self, role: str) -> str:
        return self._font_names.get(role, (_BUILTIN_REGULAR, None))[0]

    def _get_fontfile(self, role: str) -> str | None:
        return self._font_names.get(role, (_BUILTIN_REGULAR, None))[1]

    def _get_fontsize(self, role: str) -> float:
        spec = self._get_role_spec(role)
        return spec.size if spec else 9.5

    def _get_font_color(self, role: str) -> tuple[float, float, float]:
        spec = self._get_role_spec(role)
        if spec:
            return self._hex_to_rgb(spec.color_hex)
        return self.text_color

    # ------------------------------------------------------------------
    # Text measurement & wrapping
    # ------------------------------------------------------------------

    def _text_width(self, text: str, role: str, fontsize: float | None = None) -> float:
        if fontsize is None:
            fontsize = self._get_fontsize(role)
        if role in self._font_objects:
            return self._font_objects[role].text_length(text, fontsize=fontsize)
        fontname = self._get_fontname(role)
        return pymupdf.get_text_length(text, fontname=fontname, fontsize=fontsize)

    def _wrap_text(
        self, text: str, role: str, max_width: float, fontsize: float | None = None
    ) -> list[str]:
        if fontsize is None:
            fontsize = self._get_fontsize(role)
        words = text.split()
        lines: list[str] = []
        current = ""

        for word in words:
            test = f"{current} {word}".strip() if current else word
            if self._text_width(test, role, fontsize) <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    def _insert_text(
        self,
        x: float,
        y: float,
        text: str,
        role: str,
        fontsize: float | None = None,
        color: tuple[float, float, float] | None = None,
    ):
        """Insert text on the current page, registering custom fonts as needed."""
        if fontsize is None:
            fontsize = self._get_fontsize(role)
        if color is None:
            color = self._get_font_color(role)

        fontname = self._get_fontname(role)
        fontfile = self._get_fontfile(role)

        if fontfile:
            self.page.insert_font(fontname=fontname, fontfile=fontfile)

        self.page.insert_text(
            pymupdf.Point(x, y),
            text,
            fontname=fontname,
            fontsize=fontsize,
            color=color,
        )

    # ------------------------------------------------------------------
    # Page management
    # ------------------------------------------------------------------

    def new_page(self):
        self.page = self.doc.new_page(width=self.page_width, height=self.page_height)
        self.y = self.margin_top
        self.page_num += 1

        if self.has_sidebar:
            self.page.draw_line(
                pymupdf.Point(self.divider_x, self.margin_top - 5),
                pymupdf.Point(self.divider_x, self.page_height - self.margin_bottom),
                color=self.muted_color,
                width=0.5,
            )

    def check_space(self, needed: float) -> bool:
        if self.y + needed > self.page_height - self.margin_bottom:
            self.new_page()
            if self.current_section_label and not self.section_label_written:
                self._write_sidebar_label(self.current_section_label)
            return True
        return False

    # ------------------------------------------------------------------
    # Section management
    # ------------------------------------------------------------------

    def _write_sidebar_label(self, label: str):
        if self.has_sidebar:
            rule_y = self.y - 8
            self.page.draw_line(
                pymupdf.Point(self.margin_left, rule_y),
                pymupdf.Point(self.divider_x - 8, rule_y),
                color=self.muted_color,
                width=0.5,
            )
            self._insert_text(
                self.margin_left,
                self.y + 2,
                label,
                "heading",
                fontsize=self._get_fontsize("heading") * 0.85,
                color=self.accent_color,
            )
        else:
            # No sidebar — inline section header with underline
            self._insert_text(
                self.content_x,
                self.y,
                label.upper(),
                "heading",
                color=self.accent_color,
            )
            self.page.draw_line(
                pymupdf.Point(self.content_x, self.y + 3),
                pymupdf.Point(self.content_x + self.content_width, self.y + 3),
                color=self.muted_color,
                width=0.5,
            )
            self.y += self._get_fontsize("heading") + 4

        self.section_label_written = True

    def start_section(self, label: str):
        self.y += self.section_gap
        self.current_section_label = label
        self.section_label_written = False
        self._write_sidebar_label(label)

    # ------------------------------------------------------------------
    # Text writing helpers
    # ------------------------------------------------------------------

    def write_text(
        self,
        text: str,
        role: str = "body",
        x: float | None = None,
        max_width: float | None = None,
        fontsize: float | None = None,
        color: tuple[float, float, float] | None = None,
    ):
        if x is None:
            x = self.content_x
        if max_width is None:
            max_width = self.content_width
        if fontsize is None:
            fontsize = self._get_fontsize(role)
        lh = fontsize + 3.5

        lines = self._wrap_text(text, role, max_width, fontsize)
        for line in lines:
            self.check_space(lh)
            self._insert_text(x, self.y, line, role, fontsize, color)
            self.y += lh

    def write_bullet(
        self,
        text: str,
        role: str = "body",
        fontsize: float | None = None,
        color: tuple[float, float, float] | None = None,
    ):
        if fontsize is None:
            fontsize = self._get_fontsize(role)
        bullet_indent = 10
        text_x = self.content_x + bullet_indent
        text_width = self.content_width - bullet_indent
        lh = fontsize + 3.5

        lines = self._wrap_text(text, role, text_width, fontsize)
        needed = lh * min(len(lines), 2)
        self.check_space(needed)

        for i, line in enumerate(lines):
            self.check_space(lh)
            if i == 0:
                self._insert_text(self.content_x, self.y, "\u2022", role, fontsize, color)
            self._insert_text(text_x, self.y, line, role, fontsize, color)
            self.y += lh

    # ------------------------------------------------------------------
    # Section writers
    # ------------------------------------------------------------------

    def _write_header(self):
        name_size = self._get_fontsize("name")
        contact = self.data.contact

        self._insert_text(self.content_x, self.y + 10, contact.name, "name")
        self.y += name_size + 15

        body_size = self._get_fontsize("body")
        contact_items = []
        if contact.address:
            contact_items.append(("Address:", contact.address))
        if contact.phone:
            contact_items.append(("Phone:", contact.phone))
        if contact.email:
            contact_items.append(("Email:", contact.email))
        if contact.linkedin:
            contact_items.append(("LinkedIn:", contact.linkedin))
        if contact.github:
            contact_items.append(("GitHub:", contact.github))
        if contact.website:
            contact_items.append(("Website:", contact.website))

        for label, value in contact_items:
            self._insert_text(self.content_x, self.y, label, "subheading", fontsize=body_size)
            label_w = self._text_width(label + "  ", "subheading", body_size)
            self._insert_text(
                self.content_x + label_w,
                self.y,
                value,
                "body",
                fontsize=body_size,
                color=self.text_color,
            )
            self.y += body_size + 4.5

        self.y += 5

    def _write_profile(self):
        if not self.data.profile:
            return
        self.start_section("Profile")
        self.y += 2
        self.write_text(self.data.profile)

    def _write_experience(self):
        if not self.data.experience:
            return
        self.start_section("Work Experience")

        heading_size = self._get_fontsize("heading")
        subheading_size = self._get_fontsize("subheading")
        caption_size = self._get_fontsize("caption") if self._get_role_spec("caption") else 8.0

        for i, job in enumerate(self.data.experience):
            if i > 0:
                self.y += self.paragraph_spacing
            self.check_space(55)

            self._insert_text(self.content_x, self.y, job.title, "heading", fontsize=heading_size)
            self.y += heading_size + 3

            self._insert_text(
                self.content_x,
                self.y,
                job.company,
                "subheading",
                fontsize=subheading_size,
            )
            self.y += subheading_size + 3

            date_loc = f"{job.dates}  |  {job.location.upper()}" if job.location else job.dates
            self._insert_text(
                self.content_x,
                self.y,
                date_loc,
                "caption",
                fontsize=caption_size,
                color=self.muted_color,
            )
            self.y += caption_size + 6

            for bullet in job.bullets:
                self.write_bullet(bullet)
                self.y += 3

    def _write_skills(self):
        if not self.data.skills:
            return
        self.start_section("Skills")
        self.y += 2

        caption_size = self._get_fontsize("caption") if self._get_role_spec("caption") else 8.0

        for category, skills in self.data.skills.items():
            self.check_space(24)
            self._insert_text(
                self.content_x,
                self.y,
                category.upper(),
                "subheading",
                fontsize=caption_size,
            )
            self.y += 13
            self.write_text("  |  ".join(skills))
            self.y += 4

    def _write_education(self):
        if not self.data.education:
            return
        self.start_section("Education")

        heading_size = self._get_fontsize("heading")
        caption_size = self._get_fontsize("caption") if self._get_role_spec("caption") else 8.0

        for i, edu in enumerate(self.data.education):
            if i > 0:
                self.y += self.paragraph_spacing
            self.check_space(40)

            self._insert_text(
                self.content_x,
                self.y,
                edu.institution,
                "heading",
                fontsize=heading_size,
            )
            self.y += heading_size + 3

            self._insert_text(self.content_x, self.y, edu.degree, "body")
            self.y += self._get_fontsize("body") + 3

            date_loc = f"{edu.dates}  |  {edu.location.upper()}" if edu.location else edu.dates
            self._insert_text(
                self.content_x,
                self.y,
                date_loc,
                "caption",
                fontsize=caption_size,
                color=self.muted_color,
            )
            self.y += caption_size + 4

    def _write_languages(self):
        if not self.data.languages:
            return
        self.start_section("Languages")
        self.y += 2

        parts = [f"{lang.language} ({lang.level})" for lang in self.data.languages]
        self.write_text("  |  ".join(parts))

    def _write_publications(self):
        if not self.data.publications:
            return
        self.start_section("Publications")
        self.y += 2

        body_size = self._get_fontsize("body")
        for pub in self.data.publications:
            self.write_bullet(pub.text, fontsize=body_size - 0.5)
            self.y += 2

    def _write_certifications(self):
        if not self.data.certifications:
            return
        self.start_section("Certifications")
        self.y += 2

        for cert in self.data.certifications:
            text = cert.name
            if cert.issuer:
                text += f" — {cert.issuer}"
            if cert.date:
                text += f" ({cert.date})"
            self.write_bullet(text)
            self.y += 2

    # ------------------------------------------------------------------
    # Generate
    # ------------------------------------------------------------------

    def generate(self, output_path: str | Path) -> Path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        self.new_page()
        self._write_header()

        # Horizontal rule below header
        rule_y = self.y - 2
        self.page.draw_line(
            pymupdf.Point(self.content_x, rule_y),
            pymupdf.Point(self.page_width - self.margin_right, rule_y),
            color=self.muted_color,
            width=0.5,
        )
        self.y += 5

        self._write_profile()
        self._write_experience()
        self._write_skills()
        self._write_education()
        self._write_languages()
        self._write_publications()
        self._write_certifications()

        self.doc.subset_fonts()
        self.doc.save(str(output_path), garbage=4, deflate=True)
        self.doc.close()

        return output_path
