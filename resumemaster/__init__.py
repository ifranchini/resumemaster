"""resumemaster — PDF style cloning and resume generation tool."""

from resumemaster.extractor import StyleExtractor
from resumemaster.generator.pymupdf_gen import PyMuPDFGenerator
from resumemaster.identifier import FontIdentifier
from resumemaster.models import FontMap, ResumeData, StyleProfile, ValidationResult
from resumemaster.validator import StyleValidator


def __getattr__(name: str):
    if name == "WeasyPrintGenerator":
        from resumemaster.generator.weasyprint_gen import WeasyPrintGenerator

        return WeasyPrintGenerator
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "FontIdentifier",
    "FontMap",
    "PyMuPDFGenerator",
    "ResumeData",
    "StyleExtractor",
    "StyleProfile",
    "StyleValidator",
    "ValidationResult",
    "WeasyPrintGenerator",
]
