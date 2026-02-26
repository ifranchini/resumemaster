"""WeasyPrint-based resume generator using Jinja2 HTML templates."""

from __future__ import annotations

from pathlib import Path

import jinja2
import weasyprint

from resumemaster.generator.base import BaseGenerator
from resumemaster.models import FontMap, ResumeData, StyleProfile

_DEFAULT_TEMPLATE = Path(__file__).parent / "templates" / "resume.html.j2"


class WeasyPrintGenerator(BaseGenerator):
    """Generate a resume PDF via HTML/CSS rendering with WeasyPrint."""

    def __init__(
        self,
        style: StyleProfile,
        fonts: FontMap,
        data: ResumeData,
        template_path: str | Path | None = None,
    ):
        super().__init__(style, fonts, data)
        self.template_path = Path(template_path) if template_path else _DEFAULT_TEMPLATE

    # ------------------------------------------------------------------
    # CSS generation
    # ------------------------------------------------------------------

    def _build_font_faces(self) -> str:
        """Generate @font-face CSS declarations from the FontMap."""
        declarations: list[str] = []
        seen: set[str] = set()
        for mapping in self.fonts.mappings:
            if not mapping.local_path or not Path(mapping.local_path).exists():
                continue
            family = mapping.pdf_name
            if family in seen:
                continue
            seen.add(family)
            path = Path(mapping.local_path).as_uri()
            declarations.append(
                f"@font-face {{\n  font-family: '{family}';\n  src: url('{path}');\n}}"
            )
        return "\n".join(declarations)

    def _build_css_vars(self) -> dict[str, str]:
        """Map StyleProfile values to CSS custom properties."""
        layout = self.style.page_layout
        spacing = self.style.spacing
        palette = self.style.color_palette

        # Resolve font families for roles
        role_fonts: dict[str, str] = {}
        for rs in self.style.role_styles:
            role_fonts[rs.role.value] = rs.font.family

        return {
            # Page
            "page_width": f"{layout.width}pt",
            "page_height": f"{layout.height}pt",
            "margin_top": f"{layout.margin_top}pt",
            "margin_bottom": f"{layout.margin_bottom}pt",
            "margin_left": f"{layout.margin_left}pt",
            "margin_right": f"{layout.margin_right}pt",
            # Sidebar
            "has_sidebar": "true" if layout.has_sidebar else "false",
            "sidebar_width": f"{layout.sidebar_width}pt",
            "content_x": f"{layout.content_x}pt",
            # Spacing
            "line_height": f"{spacing.line_height}pt",
            "paragraph_spacing": f"{spacing.paragraph_spacing}pt",
            "section_gap": f"{spacing.section_gap}pt",
            # Colors
            "accent_color": palette[0] if palette else "#000000",
            "text_color": palette[1] if len(palette) > 1 else "#3d3d3d",
            "muted_color": palette[2] if len(palette) > 2 else "#8c8c8c",
            # Font families
            "font_name": role_fonts.get("name", "sans-serif"),
            "font_heading": role_fonts.get("heading", "sans-serif"),
            "font_body": role_fonts.get("body", "sans-serif"),
            "font_caption": role_fonts.get("caption", "sans-serif"),
            # Font sizes
            "name_size": self._role_size("name", 24),
            "heading_size": self._role_size("heading", 12),
            "subheading_size": self._role_size("subheading", 10.5),
            "body_size": self._role_size("body", 9.5),
            "caption_size": self._role_size("caption", 8),
        }

    def _role_size(self, role: str, default: float) -> str:
        spec = self._get_role_spec(role)
        size = spec.size if spec else default
        return f"{size}pt"

    # ------------------------------------------------------------------
    # Template rendering
    # ------------------------------------------------------------------

    def _render_html(self) -> str:
        """Render the Jinja2 template with style + data context."""
        loader = jinja2.FileSystemLoader(str(self.template_path.parent))
        env = jinja2.Environment(loader=loader, autoescape=True)
        template = env.get_template(self.template_path.name)

        context = {
            "font_faces": self._build_font_faces(),
            "css": self._build_css_vars(),
            "data": self.data,
            "style": self.style,
        }
        return template.render(**context)

    # ------------------------------------------------------------------
    # Generate
    # ------------------------------------------------------------------

    def generate(self, output_path: str | Path) -> Path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        html_content = self._render_html()
        doc = weasyprint.HTML(string=html_content)
        doc.write_pdf(str(output_path))

        return output_path
