"""Resume generation engines."""

from resumemaster.generator.pymupdf_gen import PyMuPDFGenerator


def __getattr__(name: str):
    if name == "WeasyPrintGenerator":
        from resumemaster.generator.weasyprint_gen import WeasyPrintGenerator

        return WeasyPrintGenerator
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["PyMuPDFGenerator", "WeasyPrintGenerator"]
