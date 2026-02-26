"""CLI interface for resumemaster."""

from __future__ import annotations

from pathlib import Path

import click

from resumemaster.models import FontMap, ResumeData, StyleProfile


@click.group()
def main():
    """resumemaster — PDF style cloning and resume generation."""


@main.command()
@click.argument("input_pdf", type=click.Path(exists=True))
@click.option("-o", "--output", "output_path", default=None, help="Output style JSON path.")
@click.option("--extract-fonts", is_flag=True, help="Extract embedded font binaries.")
@click.option("--font-dir", default=None, help="Directory to save extracted fonts.")
def extract(input_pdf: str, output_path: str | None, extract_fonts: bool, font_dir: str | None):
    """Extract a style profile from a PDF."""
    from resumemaster.extractor import StyleExtractor

    if output_path is None:
        output_path = Path(input_pdf).stem + "_style.json"

    font_output = font_dir if extract_fonts else None

    with StyleExtractor(input_pdf) as ext:
        profile = ext.extract(font_output_dir=font_output)

    Path(output_path).write_text(profile.model_dump_json(indent=2))
    click.echo(f"Style profile saved to {output_path}")

    if extract_fonts and font_output:
        n = sum(1 for e in profile.embedded_fonts if e.path)
        click.echo(f"Extracted {n} font(s) to {font_output}")


@main.command()
@click.argument("style_json", type=click.Path(exists=True))
@click.option("--font-dirs", multiple=True, help="Additional font directories to scan.")
@click.option("-o", "--output", "output_path", default=None, help="Output font map JSON path.")
def identify(style_json: str, font_dirs: tuple[str, ...], output_path: str | None):
    """Identify and resolve fonts from a style profile."""
    from resumemaster.identifier import FontIdentifier

    if output_path is None:
        output_path = Path(style_json).stem.replace("_style", "") + "_fonts.json"

    style = StyleProfile.model_validate_json(Path(style_json).read_text())
    identifier = FontIdentifier(extra_font_dirs=list(font_dirs) if font_dirs else None)
    font_map = identifier.identify(style)

    Path(output_path).write_text(font_map.model_dump_json(indent=2))
    click.echo(f"Font map saved to {output_path}")

    resolved = sum(1 for m in font_map.mappings if m.local_path)
    total = len(font_map.mappings)
    click.echo(f"Resolved {resolved}/{total} fonts")

    for m in font_map.mappings:
        status = "OK" if m.local_path else "MISSING"
        suggestion = f" (try: {m.fallback_suggestion})" if m.fallback_suggestion else ""
        click.echo(f"  [{status}] {m.pdf_name} -> {m.local_path or 'unresolved'}{suggestion}")


@main.command()
@click.argument("style_json", type=click.Path(exists=True))
@click.argument("data_json", type=click.Path(exists=True))
@click.option(
    "--engine",
    type=click.Choice(["pymupdf", "weasyprint"]),
    default="pymupdf",
    help="PDF generation engine.",
)
@click.option("-o", "--output", "output_path", default=None, help="Output PDF path.")
@click.option("--fonts-json", default=None, help="Font map JSON (auto-identified if omitted).")
@click.option("--template", default=None, help="Custom Jinja2 template for WeasyPrint.")
def generate(
    style_json: str,
    data_json: str,
    engine: str,
    output_path: str | None,
    fonts_json: str | None,
    template: str | None,
):
    """Generate a resume PDF from a style profile and data."""
    from resumemaster.identifier import FontIdentifier

    if output_path is None:
        output_path = Path(data_json).stem + f"_{engine}.pdf"

    style = StyleProfile.model_validate_json(Path(style_json).read_text())
    data = ResumeData.model_validate_json(Path(data_json).read_text())

    # Resolve fonts
    if fonts_json:
        font_map = FontMap.model_validate_json(Path(fonts_json).read_text())
    else:
        identifier = FontIdentifier()
        font_map = identifier.identify(style)

    if engine == "pymupdf":
        from resumemaster.generator.pymupdf_gen import PyMuPDFGenerator

        gen = PyMuPDFGenerator(style, font_map, data)
    else:
        from resumemaster.generator.weasyprint_gen import WeasyPrintGenerator

        gen = WeasyPrintGenerator(style, font_map, data, template_path=template)

    result = gen.generate(output_path)
    click.echo(f"PDF generated: {result}")


@main.command()
@click.argument("original_pdf", type=click.Path(exists=True))
@click.argument("generated_pdf", type=click.Path(exists=True))
@click.option("-o", "--output", "output_path", default=None, help="Output validation report JSON.")
@click.option("--diff-dir", default=None, help="Directory to save diff images.")
def validate(
    original_pdf: str,
    generated_pdf: str,
    output_path: str | None,
    diff_dir: str | None,
):
    """Validate a generated PDF against the original."""
    from resumemaster.validator import StyleValidator

    if output_path is None:
        output_path = "validation_report.json"

    validator = StyleValidator(original_pdf, generated_pdf)
    result = validator.validate(diff_dir=diff_dir)

    Path(output_path).write_text(result.model_dump_json(indent=2))
    click.echo(f"Validation report saved to {output_path}")
    click.echo(f"Final score: {result.final_score:.4f}")
    click.echo(f"  Structural: {result.structural_score:.4f}")
    click.echo(f"  SSIM:       {result.ssim_score:.4f}")
    click.echo(f"  Pixel diff: {result.pixel_diff_score:.4f}")


@main.command()
@click.argument("input_pdf", type=click.Path(exists=True))
@click.argument("data_json", type=click.Path(exists=True))
@click.option(
    "--engine",
    type=click.Choice(["pymupdf", "weasyprint"]),
    default="pymupdf",
    help="PDF generation engine.",
)
@click.option("-o", "--output", "output_path", default=None, help="Output PDF path.")
@click.option("--diff-dir", default=None, help="Directory to save diff images.")
@click.option("--extract-fonts", is_flag=True, help="Extract embedded font binaries.")
@click.option("--font-dir", default=None, help="Directory to save extracted fonts.")
def pipeline(
    input_pdf: str,
    data_json: str,
    engine: str,
    output_path: str | None,
    diff_dir: str | None,
    extract_fonts: bool,
    font_dir: str | None,
):
    """Run the full pipeline: extract -> identify -> generate -> validate."""
    from resumemaster.extractor import StyleExtractor
    from resumemaster.identifier import FontIdentifier
    from resumemaster.validator import StyleValidator

    if output_path is None:
        output_path = Path(data_json).stem + f"_{engine}.pdf"

    # Step 1: Extract
    click.echo("Step 1/4: Extracting style profile...")
    font_output = font_dir if extract_fonts else None
    with StyleExtractor(input_pdf) as ext:
        style = ext.extract(font_output_dir=font_output)
    click.echo(f"  Found {len(style.raw_font_specs)} font specs, {len(style.color_palette)} colors")

    # Step 2: Identify fonts
    click.echo("Step 2/4: Identifying fonts...")
    identifier = FontIdentifier()
    font_map = identifier.identify(style)
    resolved = sum(1 for m in font_map.mappings if m.local_path)
    click.echo(f"  Resolved {resolved}/{len(font_map.mappings)} fonts")

    # Step 3: Generate
    click.echo(f"Step 3/4: Generating PDF with {engine}...")
    data = ResumeData.model_validate_json(Path(data_json).read_text())

    if engine == "pymupdf":
        from resumemaster.generator.pymupdf_gen import PyMuPDFGenerator

        gen = PyMuPDFGenerator(style, font_map, data)
    else:
        from resumemaster.generator.weasyprint_gen import WeasyPrintGenerator

        gen = WeasyPrintGenerator(style, font_map, data)

    result_path = gen.generate(output_path)
    click.echo(f"  Output: {result_path}")

    # Step 4: Validate
    click.echo("Step 4/4: Validating output...")
    validator = StyleValidator(input_pdf, str(result_path))
    result = validator.validate(diff_dir=diff_dir)
    click.echo(f"  Final score: {result.final_score:.4f}")
    click.echo(f"  Structural: {result.structural_score:.4f}")
    click.echo(f"  SSIM:       {result.ssim_score:.4f}")
    click.echo(f"  Pixel diff: {result.pixel_diff_score:.4f}")

    # Save validation report alongside output
    report_path = Path(output_path).with_suffix(".validation.json")
    report_path.write_text(result.model_dump_json(indent=2))
    click.echo(f"  Report: {report_path}")
