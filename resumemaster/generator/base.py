"""Abstract base class for resume generators."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from resumemaster.models import FontMap, ResumeData, StyleProfile


class BaseGenerator(ABC):
    """Base class for resume PDF generators."""

    def __init__(
        self,
        style: StyleProfile,
        fonts: FontMap,
        data: ResumeData,
    ):
        self.style = style
        self.fonts = fonts
        self.data = data

    @abstractmethod
    def generate(self, output_path: str | Path) -> Path:
        """Generate a PDF resume and return the output path."""
        ...

    def _get_font_path(self, pdf_name: str) -> str | None:
        """Resolve a font name to a local file path via the FontMap."""
        return self.fonts.get_path_or_fallback(pdf_name)

    def _get_role_spec(self, role: str):
        """Get the FontSpec for a semantic role, or None."""
        for rs in self.style.role_styles:
            if rs.role.value == role:
                return rs.font
        return None

    def _hex_to_rgb(self, hex_color: str) -> tuple[float, float, float]:
        """Convert '#rrggbb' to (r, g, b) in 0-1 range."""
        h = hex_color.lstrip("#")
        return (int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255)
