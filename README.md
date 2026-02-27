# resumemaster

PDF style cloning and resume generation tool. Extracts style profiles from existing PDFs, resolves fonts, generates new PDFs matching the original style, and validates output fidelity.

## Requirements

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) for dependency management
- macOS: `brew install pango` (required for the WeasyPrint engine only)

## Setup

```bash
uv venv
uv sync
```

## Architecture

Four-module pipeline:

1. **Extractor** — reads a PDF via PyMuPDF span-level analysis and produces a `StyleProfile` (fonts, sizes, colors, layout)
2. **Identifier** — resolves PDF font names to local font files on the system
3. **Generator** — produces a new PDF from `StyleProfile` + `FontMap` + `ResumeData`
4. **Validator** — scores the generated PDF against the original using structural, SSIM, and pixel-diff metrics

Two generation engines are available:

| Engine | Pros | Cons |
|---|---|---|
| `pymupdf` (default) | Fast, no system deps | Single-column layout only |
| `weasyprint` | HTML/CSS via Jinja2 templates, flexible layouts | Requires pango/gobject |

For complex layouts (2-column, sidebars, dot-rated skills), use a **dedicated generator script** instead of the generic pipeline. See [Dedicated Generator Scripts](#dedicated-generator-scripts) below.

## CLI Usage

### Full pipeline (extract + identify + generate + validate)

```bash
resumemaster pipeline original.pdf resume_data.json \
  --engine pymupdf \
  -o output/generated.pdf \
  --diff-dir output/diffs
```

### Individual commands

```bash
# 1. Extract style profile from a PDF
resumemaster extract original.pdf -o style.json

# 2. Resolve fonts from the style profile
resumemaster identify style.json -o fonts.json

# 3. Generate a new PDF
resumemaster generate style.json data.json --engine pymupdf -o output.pdf

# 4. Validate output against the original
resumemaster validate original.pdf output.pdf -o report.json --diff-dir diffs/
```

### Options

- `--engine pymupdf|weasyprint` — choose the PDF generation engine (default: `pymupdf`)
- `--extract-fonts` — extract embedded font binaries during extraction
- `--font-dirs` — additional directories to scan for font files
- `--fonts-json` — pre-built font map JSON (skips auto-identification)
- `--template` — custom Jinja2 template for the WeasyPrint engine
- `--diff-dir` — directory to save visual diff images during validation

## Data Format

Resume content is provided as a JSON file matching the `ResumeData` schema:

```json
{
  "contact": {
    "name": "Name",
    "address": "City, Country",
    "phone": "+1 555-0100",
    "email": "name@example.com"
  },
  "profile": "Professional summary text...",
  "experience": [
    {
      "title": "Job Title",
      "company": "Company Name",
      "dates": "2020 - Present",
      "location": "City, Country",
      "bullets": ["Achievement one", "Achievement two"]
    }
  ],
  "skills": {
    "Category": ["Skill 1", "Skill 2"]
  },
  "education": [
    {
      "institution": "University",
      "degree": "Degree Name",
      "dates": "2015 - 2019",
      "location": "City, Country"
    }
  ],
  "languages": [
    {"language": "English", "level": "Native"}
  ],
  "publications": [
    {"text": "Publication citation..."}
  ],
  "certifications": [
    {"name": "Cert Name", "issuer": "Issuer", "date": "2023"}
  ]
}
```

## Dedicated Generator Scripts

The generic pipeline produces a flat single-column layout. For CVs with complex visual layouts (sidebars, photo placeholders, dot-rated skills, multi-column sections), use a standalone PyMuPDF script that hard-codes the target layout geometry.

### Pablo Cartes CV (2021 layout)

```bash
uv run python output/generate_pablo_cv.py
```

Produces `output/Pablo_Cartes_CV_Original_Style.pdf` — a single-page US Letter PDF replicating the 2021 creative layout:

- Grey sidebar with abstract, education, dot-rated skills, awards
- Right main area with professional experience, diplomas, consultancies
- Header with initials circle, blue accent subtitles, contact block
- Dark divider bar separating header from body

To create a new dedicated script for a different CV, use `output/generate_pablo_cv.py` as a template. The pattern is:

1. Analyze the original PDF layout (coordinates, fonts, colors, spacing)
2. Define layout constants matching the original geometry
3. Hard-code content data at the top of the script
4. Build a generator class with methods for each visual section
5. Validate with `resumemaster validate original.pdf generated.pdf`

## Validation Scores

The validator produces three metrics (0-1 scale, higher is better):

| Metric | What it measures |
|---|---|
| Structural | Font roles, section count, page dimensions match |
| SSIM | Structural similarity of rendered page images |
| Pixel diff | Pixel-level overlap between original and generated |

The final score is a weighted average. A score above 0.6 indicates a reasonable layout match; above 0.8 is a close visual clone.

## Development

```bash
# Lint and format
ruff check
ruff format --check

# Type check
ty check

# Run tests
pytest -q
```

## WeasyPrint on macOS with uv

uv's standalone Python may not find Homebrew's native libs. For `--engine weasyprint`, either:

```bash
# Option A: set library path
DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib resumemaster generate ...

# Option B: invoke via system python module
python3 -c "from resumemaster.cli import main; main()" generate ...
```

The PyMuPDF engine works without any extra setup.
