"""Extract style profiles from PDF documents."""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

import pymupdf

from resumemaster.models import (
    EmbeddedFont,
    FontSpec,
    FontStyle,
    FontWeight,
    PageLayout,
    RoleStyle,
    SemanticRole,
    SpacingProfile,
    StyleProfile,
)


def _color_int_to_hex(color_int: int) -> str:
    """Convert PyMuPDF integer color to hex string."""
    return f"#{color_int:06x}"


def _parse_font_weight(font_name: str, flags: int) -> FontWeight:
    """Infer font weight from name and flags."""
    name_lower = font_name.lower()
    is_bold = bool(flags & (1 << 4))

    if "black" in name_lower or "heavy" in name_lower:
        return FontWeight.BLACK
    if "extrabold" in name_lower or "ultrabold" in name_lower:
        return FontWeight.EXTRABOLD
    if "semibold" in name_lower or "demibold" in name_lower:
        return FontWeight.SEMIBOLD
    if is_bold or "bold" in name_lower:
        return FontWeight.BOLD
    if "medium" in name_lower:
        return FontWeight.MEDIUM
    if "light" in name_lower or "thin" in name_lower:
        return FontWeight.LIGHT
    return FontWeight.REGULAR


def _parse_font_style(font_name: str, flags: int) -> FontStyle:
    """Infer font style from name and flags."""
    is_italic = bool(flags & (1 << 1))
    if is_italic or "italic" in font_name.lower() or "oblique" in font_name.lower():
        return FontStyle.ITALIC
    return FontStyle.NORMAL


def _strip_subset_prefix(name: str) -> str:
    """Strip the 6-char subset prefix (e.g., ABCDEF+ArialBold -> ArialBold)."""
    return re.sub(r"^[A-Z]{6}\+", "", name)


class StyleExtractor:
    """Extract a StyleProfile from a PDF file."""

    def __init__(self, pdf_path: str | Path):
        self.pdf_path = Path(pdf_path)
        self.doc = pymupdf.open(str(self.pdf_path))

    def close(self):
        self.doc.close()

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        self.close()

    def extract(self, font_output_dir: str | Path | None = None) -> StyleProfile:
        """Extract the complete style profile from the PDF."""
        spans = self._collect_spans()
        layout = self._detect_layout(spans)
        spacing = self._detect_spacing(spans)
        role_styles = self._assign_roles(spans)
        palette = self._extract_palette(spans)
        raw_specs = self._extract_raw_specs(spans)
        embedded = self._extract_embedded_fonts(font_output_dir)

        return StyleProfile(
            page_layout=layout,
            spacing=spacing,
            role_styles=role_styles,
            color_palette=palette,
            raw_font_specs=raw_specs,
            embedded_fonts=embedded,
        )

    # ------------------------------------------------------------------
    # Span collection
    # ------------------------------------------------------------------

    def _collect_spans(self) -> list[dict]:
        """Collect all text spans from all pages with metadata."""
        all_spans = []
        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            blocks = page.get_text("dict", flags=pymupdf.TEXT_PRESERVE_WHITESPACE)["blocks"]
            for block in blocks:
                if block["type"] != 0:
                    continue
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"].strip()
                        if not text:
                            continue
                        all_spans.append(
                            {
                                "text": text,
                                "font": span["font"],
                                "size": round(span["size"], 2),
                                "color": span["color"],
                                "color_hex": _color_int_to_hex(span["color"]),
                                "flags": span["flags"],
                                "bold": bool(span["flags"] & (1 << 4)),
                                "italic": bool(span["flags"] & (1 << 1)),
                                "origin_x": round(span["origin"][0], 2),
                                "origin_y": round(span["origin"][1], 2),
                                "bbox": [round(x, 2) for x in span["bbox"]],
                                "page": page_num,
                            }
                        )
        return all_spans

    # ------------------------------------------------------------------
    # Layout detection
    # ------------------------------------------------------------------

    def _detect_layout(self, spans: list[dict]) -> PageLayout:
        """Derive page layout from content boundaries and detect sidebar."""
        page = self.doc[0]
        width = page.rect.width
        height = page.rect.height

        if not spans:
            return PageLayout(
                width=width,
                height=height,
                margin_top=40,
                margin_bottom=40,
                margin_left=40,
                margin_right=40,
            )

        # Content boundaries from bounding boxes
        min_x = min(s["bbox"][0] for s in spans)
        max_x = max(s["bbox"][2] for s in spans)
        min_y = min(s["bbox"][1] for s in spans)
        max_y = max(s["bbox"][3] for s in spans)

        margin_left = max(0, min_x - 5)
        margin_right = max(0, width - max_x - 5)
        margin_top = max(0, min_y - 5)
        margin_bottom = max(0, height - max_y - 5)

        # Sidebar detection: cluster x-origins and look for a gap
        x_origins = sorted(set(s["origin_x"] for s in spans))
        has_sidebar = False
        sidebar_width = 0.0
        divider_x = 0.0
        content_x = margin_left

        if len(x_origins) >= 2:
            # Look for a gap > 30pt in the left 40% of the page
            threshold_x = width * 0.4
            left_origins = [x for x in x_origins if x < threshold_x]
            right_origins = [x for x in x_origins if x >= threshold_x]

            if left_origins and right_origins:
                max_left = max(left_origins)
                min_right = min(right_origins)
                gap = min_right - max_left

                if gap > 30:
                    has_sidebar = True
                    sidebar_width = max_left - margin_left + 10
                    divider_x = max_left + gap / 2
                    content_x = min_right

        return PageLayout(
            width=width,
            height=height,
            margin_top=round(margin_top, 1),
            margin_bottom=round(margin_bottom, 1),
            margin_left=round(margin_left, 1),
            margin_right=round(margin_right, 1),
            has_sidebar=has_sidebar,
            sidebar_width=round(sidebar_width, 1),
            divider_x=round(divider_x, 1),
            content_x=round(content_x, 1),
        )

    # ------------------------------------------------------------------
    # Spacing detection
    # ------------------------------------------------------------------

    def _detect_spacing(self, spans: list[dict]) -> SpacingProfile:
        """Detect line height, paragraph spacing, and section gap from vertical gaps."""
        if len(spans) < 2:
            return SpacingProfile(line_height=13, paragraph_spacing=6, section_gap=18)

        # Sort by page then y-origin
        sorted_spans = sorted(spans, key=lambda s: (s["page"], s["origin_y"]))

        gaps = []
        for i in range(1, len(sorted_spans)):
            if sorted_spans[i]["page"] != sorted_spans[i - 1]["page"]:
                continue
            gap = sorted_spans[i]["origin_y"] - sorted_spans[i - 1]["origin_y"]
            if 0 < gap < 100:  # ignore page breaks and overlapping text
                gaps.append(gap)

        if not gaps:
            return SpacingProfile(line_height=13, paragraph_spacing=6, section_gap=18)

        gaps.sort()
        n = len(gaps)

        # Classify: small gaps = line_height, medium = paragraph, large = section
        # Use percentiles
        line_height = gaps[n // 4] if n > 4 else gaps[0]
        paragraph_spacing = gaps[n // 2] if n > 2 else line_height * 1.5
        section_gap = gaps[int(n * 0.85)] if n > 5 else paragraph_spacing * 2

        return SpacingProfile(
            line_height=round(line_height, 1),
            paragraph_spacing=round(paragraph_spacing, 1),
            section_gap=round(section_gap, 1),
        )

    # ------------------------------------------------------------------
    # Semantic role assignment
    # ------------------------------------------------------------------

    def _assign_roles(self, spans: list[dict]) -> list[RoleStyle]:
        """Assign semantic roles based on font size and weight patterns."""
        if not spans:
            return []

        # Collect unique style combos with frequency
        style_counter: Counter[tuple[str, float, bool, str]] = Counter()
        for s in spans:
            key = (s["font"], s["size"], s["bold"], s["color_hex"])
            style_counter[key] += len(s["text"])

        # Sort by size descending
        styles_by_size = sorted(style_counter.keys(), key=lambda x: -x[1])

        # Most frequent size (by total text length) = BODY
        body_size = max(style_counter, key=lambda k: style_counter[k])[1]

        roles: list[RoleStyle] = []
        assigned_roles: set[SemanticRole] = set()

        for font_name, size, bold, color_hex in styles_by_size:
            weight = _parse_font_weight(font_name, (1 << 4) if bold else 0)
            style = _parse_font_style(font_name, 0)
            spec = FontSpec(
                family=_strip_subset_prefix(font_name),
                size=size,
                weight=weight,
                style=style,
                color_hex=color_hex,
            )

            max_size = max(s[1] for s in styles_by_size)
            is_name = size == max_size and SemanticRole.NAME not in assigned_roles
            is_heading = size > body_size and bold and SemanticRole.HEADING not in assigned_roles
            is_sub = (
                bold
                and abs(size - body_size) < 1.5
                and SemanticRole.SUBHEADING not in assigned_roles
            )
            is_body = (
                abs(size - body_size) < 0.5 and not bold and SemanticRole.BODY not in assigned_roles
            )

            if is_name:
                role = SemanticRole.NAME
            elif is_heading:
                role = SemanticRole.HEADING
            elif is_sub:
                role = SemanticRole.SUBHEADING
            elif is_body:
                role = SemanticRole.BODY
            elif size < body_size and SemanticRole.CAPTION not in assigned_roles:
                role = SemanticRole.CAPTION
            else:
                continue

            roles.append(RoleStyle(role=role, font=spec))
            assigned_roles.add(role)

        return roles

    # ------------------------------------------------------------------
    # Color palette
    # ------------------------------------------------------------------

    def _extract_palette(self, spans: list[dict]) -> list[str]:
        """Extract unique colors, ordered by frequency."""
        counter: Counter[str] = Counter()
        for s in spans:
            counter[s["color_hex"]] += 1
        return [color for color, _ in counter.most_common()]

    # ------------------------------------------------------------------
    # Raw font specs
    # ------------------------------------------------------------------

    def _extract_raw_specs(self, spans: list[dict]) -> list[FontSpec]:
        """Extract all unique font specifications found in the PDF."""
        seen: set[tuple[str, float, str, str]] = set()
        specs: list[FontSpec] = []

        for s in spans:
            weight = _parse_font_weight(s["font"], s["flags"])
            style = _parse_font_style(s["font"], s["flags"])
            key = (s["font"], s["size"], weight.value, style.value)
            if key not in seen:
                seen.add(key)
                specs.append(
                    FontSpec(
                        family=_strip_subset_prefix(s["font"]),
                        size=s["size"],
                        weight=weight,
                        style=style,
                        color_hex=s["color_hex"],
                    )
                )
        return specs

    # ------------------------------------------------------------------
    # Embedded font extraction
    # ------------------------------------------------------------------

    def _extract_embedded_fonts(self, output_dir: str | Path | None = None) -> list[EmbeddedFont]:
        """Extract embedded font binaries from the PDF."""
        fonts_seen: set[int] = set()
        embedded: list[EmbeddedFont] = []

        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            for f in page.get_fonts(full=True):
                xref = f[0]
                if xref in fonts_seen:
                    continue
                fonts_seen.add(xref)

                ext = f[1]
                basefont = _strip_subset_prefix(f[3])
                name = f[4]

                path = None
                if output_dir and ext in ("ttf", "otf", "cff"):
                    try:
                        _name, _ext, _type, content = self.doc.extract_font(xref)
                        if content:
                            out_dir = Path(output_dir)
                            out_dir.mkdir(parents=True, exist_ok=True)
                            out_path = out_dir / f"{basefont}.{ext}"
                            out_path.write_bytes(content)
                            path = str(out_path)
                    except Exception:
                        pass

                embedded.append(
                    EmbeddedFont(
                        pdf_name=name or basefont,
                        xref=xref,
                        ext=ext,
                        path=path,
                    )
                )

        return embedded
