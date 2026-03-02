# Operations Guide — Pablo Cartes CV

Step-by-step instructions for generating, validating, and exporting Pablo's resume.

## Generate the latest resume

```bash
cd /path/to/resumemaster
uv run python examples/pablo_cartes/generate_cv.py
```

Output: `examples/pablo_cartes/output/Pablo_Cartes_CV_Original_Style.pdf`

The script is self-contained — all content data and layout constants are defined inline. To update resume content, edit the `CONTENT` dict at the top of `generate_cv.py`.

## Source PDFs

Original reference PDFs should be placed in the `output/original/` directory (gitignored). These are used for visual comparison during validation:

- `CVPablo Cartes_English2021Nov.pdf` — the 2021 creative layout being replicated
- `Pablo_Cartes_CV_2021_Original.pdf` — alternate copy of the original
- `Pablo_Cartes_CV_Pure_Industry.pdf` — industry-focused version (source of latest content updates)

## Validate output against the original

```bash
uv run resumemaster validate \
  output/original/Pablo_Cartes_CV_2021_Original.pdf \
  examples/pablo_cartes/output/Pablo_Cartes_CV_Original_Style.pdf \
  -o output/pablo_validation.json \
  --diff-dir output/pablo_diffs
```

This produces:
- `pablo_validation.json` — structural, SSIM, and pixel-diff scores
- `pablo_diffs/diff_page_0.png` — visual overlay showing differences

A score above 0.6 indicates reasonable layout match; above 0.8 is a close visual clone.

## Font fallbacks

The original CV uses **Calibri**, which is not available on macOS without a Microsoft Office installation. The generator uses **Arial** (Regular + Bold) as a substitute:

```
/System/Library/Fonts/Supplemental/Arial.ttf
/System/Library/Fonts/Supplemental/Arial Bold.ttf
```

Arial has similar metrics to Calibri but slightly wider letterforms. If Calibri is available (e.g., on a Windows machine or with Office installed), update the `ARIAL_REGULAR` and `ARIAL_BOLD` constants in `generate_cv.py` to point to the Calibri font files.

## Google Docs export workflow

To produce a Google Docs-editable version:

1. Generate the PDF as above
2. Upload the PDF to Google Drive
3. Right-click the PDF in Drive and select **Open with > Google Docs**
4. Google Docs will OCR/convert the PDF into an editable document
5. Review formatting — sidebar layout, dot-rated skills, and multi-column sections may not convert cleanly
6. For best results, use the `resume_data.json` file to manually populate a Google Docs template instead of converting from PDF

Alternatively, the generic pipeline can produce DOCX output via WeasyPrint, but this does not preserve the 2-column creative layout.

## Content and layout decisions

### Two-page layout
The CV was expanded from a single-page design to two pages to accommodate additional content (technical skills breakdown, consultancies, publication, other activities). Page 1 retains the original 2021 creative layout; page 2 uses a full-width format with blue accent headings.

### Content source
The `CONTENT` dict in `generate_cv.py` combines:
- Layout structure from `CVPablo Cartes_English2021Nov.pdf` (2021 creative design)
- Updated content from `Pablo_Cartes_CV_Pure_Industry.pdf` (latest experience, awards, publication)

The `resume_data.json` file follows the generic `ResumeData` schema and can be used with the resumemaster pipeline for simpler single-column output.

### Key content updates (latest)
- Experience dates updated (Driftwood: "2022 - Feb 2026")
- ADC 2025 gold and silver medals added to awards
- FEMS Yeast Research publication added (January 2026)
- UBC Wine Research Centre collaboration noted
- Consultancy list expanded (6 clients)
- "The Mage" cask-strength whisky added to experience bullets
