# Project: resumemaster

PDF style cloning and resume generation tool. Extracts style profiles from existing PDFs, resolves fonts, generates new PDFs using the extracted style, and validates output fidelity.

## Python

- Runtime: 3.13 with `uv venv`

| Purpose         | Tool                             |
|-----------------|----------------------------------|
| deps & venv     | `uv`                             |
| lint & format   | `ruff check` · `ruff format`     |
| static types    | `ty check`                       |
| tests           | `pytest -q`                      |

## System dependencies

WeasyPrint requires pango: `brew install pango`

## Architecture

4-module pipeline:

1. **Extractor** (`extractor.py`) — extracts StyleProfile from a PDF via PyMuPDF span-level analysis
2. **Identifier** (`identifier.py`) — resolves PDF font names to local font files
3. **Generator** (`generator/`) — produces new PDFs from StyleProfile + FontMap + ResumeData
   - `pymupdf_gen.py` — direct PyMuPDF rendering (faster, no system deps)
   - `weasyprint_gen.py` — HTML/CSS via Jinja2 template (better for complex layouts)
4. **Validator** (`validator.py`) — scores generated PDF against original (structural + SSIM + pixel diff)

Data models in `models.py`, CLI in `cli.py`.

## Workflow

### Before committing

- Run `ruff check && ruff format --check`
- Run `pytest -q`
- Verify CLI commands work end-to-end

### Commits

- Imperative mood, ≤72 char subject line, one logical change per commit
- Never push directly to main — use feature branches and PRs

## Style

Use plain, factual language. Avoid: critical, crucial, essential, significant, comprehensive, robust, elegant.
