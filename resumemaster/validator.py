"""Validate generated PDFs against originals using structural, SSIM, and pixel diff scoring."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pymupdf
from PIL import Image
from skimage.metrics import structural_similarity

from resumemaster.extractor import StyleExtractor
from resumemaster.models import PageScore, StyleProfile, ValidationResult

# Scoring weights
W_STRUCTURAL = 0.50
W_SSIM = 0.30
W_PIXEL = 0.20

# Structural sub-weights
SW_FONTS = 0.25
SW_SIZES = 0.25
SW_COLORS = 0.20
SW_SPACING = 0.15
SW_DIMENSIONS = 0.15


def _jaccard(a: set, b: set) -> float:
    """Jaccard similarity between two sets."""
    if not a and not b:
        return 1.0
    union = a | b
    if not union:
        return 1.0
    return len(a & b) / len(union)


def _relative_diff(a: float, b: float) -> float:
    """Relative difference, returns 0-1 where 0 = identical."""
    if a == 0 and b == 0:
        return 0.0
    return abs(a - b) / max(abs(a), abs(b))


def _render_page_to_array(page, dpi: int = 150) -> np.ndarray:
    """Render a PyMuPDF page to a numpy array."""
    pix = page.get_pixmap(dpi=dpi)
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    return np.array(img)


class StyleValidator:
    """Compare an original PDF against a generated PDF."""

    def __init__(self, original_pdf: str | Path, generated_pdf: str | Path):
        self.original_path = Path(original_pdf)
        self.generated_path = Path(generated_pdf)

    def validate(self, diff_dir: str | Path | None = None) -> ValidationResult:
        """Run all validation layers and return a combined result."""
        orig_doc = pymupdf.open(str(self.original_path))
        gen_doc = pymupdf.open(str(self.generated_path))

        # Extract style profiles
        with StyleExtractor(self.original_path) as ext:
            orig_style = ext.extract()
        with StyleExtractor(self.generated_path) as ext:
            gen_style = ext.extract()

        # Structural score
        structural = self._structural_score(orig_style, gen_style)

        # Per-page visual scores
        n_orig = len(orig_doc)
        n_gen = len(gen_doc)
        n_compare = min(n_orig, n_gen)

        page_scores: list[PageScore] = []
        ssim_scores: list[float] = []
        pixel_scores: list[float] = []

        if diff_dir:
            diff_path = Path(diff_dir)
            diff_path.mkdir(parents=True, exist_ok=True)

        for i in range(n_compare):
            orig_arr = _render_page_to_array(orig_doc[i])
            gen_arr = _render_page_to_array(gen_doc[i])

            # Resize to match if needed
            if orig_arr.shape != gen_arr.shape:
                h = min(orig_arr.shape[0], gen_arr.shape[0])
                w = min(orig_arr.shape[1], gen_arr.shape[1])
                orig_arr = orig_arr[:h, :w]
                gen_arr = gen_arr[:h, :w]

            # SSIM
            ssim_val = structural_similarity(
                orig_arr,
                gen_arr,
                channel_axis=2,
                data_range=255,
            )

            # Pixel diff
            orig_gray = np.mean(orig_arr, axis=2)
            gen_gray = np.mean(gen_arr, axis=2)
            diff = np.abs(orig_gray - gen_gray)
            threshold = 30  # pixel intensity threshold
            differing = np.sum(diff > threshold)
            total = diff.size
            pixel_score = 1.0 - (differing / total)

            # Combined per-page
            combined = W_STRUCTURAL * structural + W_SSIM * ssim_val + W_PIXEL * pixel_score

            diff_image_path = None
            if diff_dir:
                diff_img = self._create_diff_image(orig_arr, gen_arr)
                diff_image_path = str(diff_path / f"diff_page_{i}.png")
                Image.fromarray(diff_img).save(diff_image_path)

            page_scores.append(
                PageScore(
                    page=i,
                    structural=round(structural, 4),
                    ssim=round(ssim_val, 4),
                    pixel_diff=round(pixel_score, 4),
                    combined=round(combined, 4),
                    diff_image_path=diff_image_path,
                )
            )
            ssim_scores.append(ssim_val)
            pixel_scores.append(pixel_score)

        orig_doc.close()
        gen_doc.close()

        # Average visual scores
        avg_ssim = sum(ssim_scores) / len(ssim_scores) if ssim_scores else 0.0
        avg_pixel = sum(pixel_scores) / len(pixel_scores) if pixel_scores else 0.0

        # Page count penalty: if counts differ, scale down proportionally
        if n_orig != n_gen:
            page_penalty = n_compare / max(n_orig, n_gen)
            avg_ssim *= page_penalty
            avg_pixel *= page_penalty

        final = W_STRUCTURAL * structural + W_SSIM * avg_ssim + W_PIXEL * avg_pixel

        return ValidationResult(
            structural_score=round(structural, 4),
            ssim_score=round(avg_ssim, 4),
            pixel_diff_score=round(avg_pixel, 4),
            final_score=round(final, 4),
            page_scores=page_scores,
            details={
                "original_pages": n_orig,
                "generated_pages": n_gen,
                "compared_pages": n_compare,
            },
        )

    # ------------------------------------------------------------------
    # Structural comparison
    # ------------------------------------------------------------------

    def _structural_score(self, orig: StyleProfile, gen: StyleProfile) -> float:
        """Compare two StyleProfiles structurally."""
        # Font names
        orig_fonts = {s.family for s in orig.raw_font_specs}
        gen_fonts = {s.family for s in gen.raw_font_specs}
        font_score = _jaccard(orig_fonts, gen_fonts)

        # Font sizes (within ±0.5pt tolerance)
        orig_sizes = {round(s.size) for s in orig.raw_font_specs}
        gen_sizes = {round(s.size) for s in gen.raw_font_specs}
        size_score = _jaccard(orig_sizes, gen_sizes)

        # Colors
        orig_colors = set(orig.color_palette)
        gen_colors = set(gen.color_palette)
        color_score = _jaccard(orig_colors, gen_colors)

        # Spacing
        spacing_diffs = [
            _relative_diff(orig.spacing.line_height, gen.spacing.line_height),
            _relative_diff(orig.spacing.paragraph_spacing, gen.spacing.paragraph_spacing),
            _relative_diff(orig.spacing.section_gap, gen.spacing.section_gap),
        ]
        spacing_score = 1.0 - (sum(spacing_diffs) / len(spacing_diffs))

        # Dimensions
        dim_diffs = [
            _relative_diff(orig.page_layout.width, gen.page_layout.width),
            _relative_diff(orig.page_layout.height, gen.page_layout.height),
        ]
        dim_score = 1.0 - (sum(dim_diffs) / len(dim_diffs))

        return (
            SW_FONTS * font_score
            + SW_SIZES * size_score
            + SW_COLORS * color_score
            + SW_SPACING * max(0, spacing_score)
            + SW_DIMENSIONS * max(0, dim_score)
        )

    # ------------------------------------------------------------------
    # Visual diff
    # ------------------------------------------------------------------

    def _create_diff_image(self, orig: np.ndarray, gen: np.ndarray) -> np.ndarray:
        """Create a diff image highlighting differences in red."""
        orig_gray = np.mean(orig, axis=2)
        gen_gray = np.mean(gen, axis=2)
        diff = np.abs(orig_gray - gen_gray)

        # Create output: original with red overlay where differences exist
        result = orig.copy()
        mask = diff > 30
        result[mask] = [255, 0, 0]
        return result
