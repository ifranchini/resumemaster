"""Resolve PDF font names to local font file paths."""

from __future__ import annotations

import re
from pathlib import Path

from resumemaster.models import FontMap, FontMapping, StyleProfile

# ---------------------------------------------------------------------------
# macOS font directories
# ---------------------------------------------------------------------------

MACOS_FONT_DIRS = [
    Path.home() / "Library" / "Fonts",
    Path("/Library/Fonts"),
    Path("/System/Library/Fonts"),
    Path("/System/Library/Fonts/Supplemental"),
]

# ---------------------------------------------------------------------------
# Common font name aliases (PDF name -> canonical family name)
# ---------------------------------------------------------------------------

FONT_ALIASES: dict[str, str] = {
    # Arial variants
    "ArialMT": "Arial",
    "Arial-BoldMT": "Arial Bold",
    "Arial-ItalicMT": "Arial Italic",
    "Arial-BoldItalicMT": "Arial Bold Italic",
    # Times variants
    "TimesNewRomanPSMT": "Times New Roman",
    "TimesNewRomanPS-BoldMT": "Times New Roman Bold",
    "TimesNewRomanPS-ItalicMT": "Times New Roman Italic",
    "TimesNewRomanPS-BoldItalicMT": "Times New Roman Bold Italic",
    # Helvetica variants
    "HelveticaNeue": "Helvetica Neue",
    "HelveticaNeue-Bold": "Helvetica Neue Bold",
    "HelveticaNeue-Light": "Helvetica Neue Light",
    "HelveticaNeue-Medium": "Helvetica Neue Medium",
    # Calibri
    "Calibri": "Calibri",
    "Calibri-Bold": "Calibri Bold",
    "Calibri-Italic": "Calibri Italic",
    "Calibri-BoldItalic": "Calibri Bold Italic",
    # Garamond
    "GaramondPremrPro": "Garamond Premier Pro",
    "GaramondPremrPro-It": "Garamond Premier Pro Italic",
    # Georgia
    "Georgia": "Georgia",
    "Georgia-Bold": "Georgia Bold",
    "Georgia-Italic": "Georgia Italic",
    # Cambria
    "Cambria": "Cambria",
    "Cambria-Bold": "Cambria Bold",
}

# ---------------------------------------------------------------------------
# Google Fonts equivalents for common system fonts
# ---------------------------------------------------------------------------

GOOGLE_FONTS_SUGGESTIONS: dict[str, str] = {
    "Helvetica": "Inter",
    "Helvetica Neue": "Inter",
    "Arial": "Inter",
    "Calibri": "Carlito",
    "Cambria": "Caladea",
    "Times New Roman": "Tinos",
    "Georgia": "Gelasio",
    "Trebuchet MS": "Fira Sans",
    "Verdana": "DejaVu Sans",
    "Palatino": "EB Garamond",
    "Garamond": "EB Garamond",
    "Century Gothic": "Raleway",
}


def _strip_subset_prefix(name: str) -> str:
    """Strip 6-char subset prefix (e.g., ABCDEF+ArialBold -> ArialBold)."""
    return re.sub(r"^[A-Z]{6}\+", "", name)


def _normalize_name(name: str) -> str:
    """Normalize a font name for fuzzy matching: lowercase, strip separators."""
    name = _strip_subset_prefix(name)
    return re.sub(r"[-_\s]+", "", name).lower()


class FontIdentifier:
    """Resolve PDF font names to local font file paths."""

    def __init__(self, extra_font_dirs: list[str | Path] | None = None):
        self.font_dirs = list(MACOS_FONT_DIRS)
        if extra_font_dirs:
            self.font_dirs.extend(Path(d) for d in extra_font_dirs)
        self._font_index: dict[str, str] | None = None

    @property
    def font_index(self) -> dict[str, str]:
        """Lazy-build an index mapping normalized names to file paths."""
        if self._font_index is None:
            self._font_index = self._build_index()
        return self._font_index

    def _build_index(self) -> dict[str, str]:
        """Scan font directories and build name -> path index."""
        index: dict[str, str] = {}
        for font_dir in self.font_dirs:
            if not font_dir.exists():
                continue
            for f in font_dir.rglob("*"):
                if f.suffix.lower() in (".ttf", ".otf", ".ttc", ".woff", ".woff2"):
                    # Index by filename stem (normalized)
                    key = _normalize_name(f.stem)
                    if key not in index:
                        index[key] = str(f)
        return index

    def identify(self, style: StyleProfile) -> FontMap:
        """Resolve all fonts in a StyleProfile to local paths."""
        # Collect unique PDF font names
        pdf_names: set[str] = set()
        for spec in style.raw_font_specs:
            pdf_names.add(spec.family)
        for emb in style.embedded_fonts:
            pdf_names.add(emb.pdf_name)

        mappings: list[FontMapping] = []
        for pdf_name in sorted(pdf_names):
            mapping = self._resolve_font(pdf_name, style)
            mappings.append(mapping)

        return FontMap(mappings=mappings)

    def _resolve_font(self, pdf_name: str, style: StyleProfile) -> FontMapping:
        """Try multiple strategies to resolve a single font name."""
        clean_name = _strip_subset_prefix(pdf_name)

        # Strategy 1: Direct match in font index
        normalized = _normalize_name(clean_name)
        if normalized in self.font_index:
            return FontMapping(
                pdf_name=pdf_name,
                local_path=self.font_index[normalized],
                source="local_direct",
            )

        # Strategy 2: Alias table lookup
        alias = FONT_ALIASES.get(clean_name)
        if alias:
            alias_norm = _normalize_name(alias)
            if alias_norm in self.font_index:
                return FontMapping(
                    pdf_name=pdf_name,
                    local_path=self.font_index[alias_norm],
                    source="local_alias",
                )

        # Strategy 3: Fuzzy match — try family name without weight/style suffixes
        weight_pattern = r"[-_]?(Bold|Italic|Light|Medium|Semi|Regular|Thin|Black|Heavy)"
        family_base = re.split(weight_pattern, clean_name, flags=re.IGNORECASE)[0]
        family_norm = _normalize_name(family_base)
        for key, path in self.font_index.items():
            if key.startswith(family_norm) or family_norm in key:
                return FontMapping(
                    pdf_name=pdf_name,
                    local_path=path,
                    source="local_fuzzy",
                )

        # Strategy 4: Embedded font path from extraction
        for emb in style.embedded_fonts:
            if emb.pdf_name == pdf_name and emb.path:
                return FontMapping(
                    pdf_name=pdf_name,
                    local_path=emb.path,
                    source="embedded",
                )

        # Strategy 5: Suggest Google Fonts equivalent
        suggestion = self._suggest_google_font(clean_name)
        return FontMapping(
            pdf_name=pdf_name,
            local_path=None,
            source="unresolved",
            fallback_suggestion=suggestion,
        )

    def _suggest_google_font(self, font_name: str) -> str | None:
        """Suggest a Google Fonts equivalent for a given font family."""
        # Extract base family (strip weight/style suffixes)
        base = re.split(
            r"[-_]?(Bold|Italic|Light|Medium|Semi|Regular|Thin|Black|Heavy)",
            font_name,
            flags=re.IGNORECASE,
        )[0].strip()

        # Direct lookup
        if base in GOOGLE_FONTS_SUGGESTIONS:
            return GOOGLE_FONTS_SUGGESTIONS[base]

        # Fuzzy: check if base starts with any known key
        base_lower = base.lower()
        for key, suggestion in GOOGLE_FONTS_SUGGESTIONS.items():
            if base_lower.startswith(key.lower()) or key.lower().startswith(base_lower):
                return suggestion

        return None
