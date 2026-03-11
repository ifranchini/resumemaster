# Pablo Cartes CV — Creative Layout

Dedicated generator script that produces a single-page creative CV using PyMuPDF directly, bypassing the generic pipeline. Generates two color variants (purple and red).

## Layout

Single-page, two-column layout:

- **Header:** Initials circle, name, subtitles (left), contact info (right)
- **Sidebar (left):** Abstract, Education, Skills (bulleted list), Languages, Awards
- **Main area (right):** Professional Experience, Certifications, Other Activities, Consultancies
- Dark divider bar separating header from body

## Files

| File | Purpose |
|---|---|
| `generate_cv.py` | Standalone generator script (layout geometry + content + color schemes) |
| `resume_data.json` | Resume content in the generic `ResumeData` JSON schema |
| `output/` | Generated PDFs (gitignored) |

## Usage

```bash
uv run python examples/pablo_cartes/generate_cv.py
```

This generates two files in `examples/pablo_cartes/output/`:

| Output file | Color scheme |
|---|---|
| `Pablo_Cartes_CV_Purple.pdf` | Dark purple accent (#582A6B) |
| `Pablo_Cartes_CV_Red.pdf` | Dark red accent (#8B2222) |

## Editing content

All resume content lives in the `CONTENT` dict at the top of `generate_cv.py`. To update:

1. Edit the relevant field in `CONTENT` (experience bullets, skills list, certifications, etc.)
2. Re-run the script to regenerate both PDFs

Key content sections:
- `abstract` — professional summary shown in the sidebar
- `skills` — plain list of skill keywords (sidebar)
- `languages` — list of (language, level) tuples (sidebar)
- `awards` — bulleted list (sidebar)
- `experience` — list of jobs with title, company, dates, bullets (main area)
- `diplomas` — certifications with name, issuer, date (main area)
- `other_activities` — bulleted list (main area)
- `consultancies` — pipe-separated client names (main area)

## Color schemes

The `PabloCV` class accepts `accent` and `bar` RGB tuples to control the color theme. The accent color is used for headings, the initials circle, and subtitles. The bar color is used for the header divider.

To add a new color variant, define new RGB tuples and add another `PabloCV(...).generate(...)` call in the `__main__` block.

## Fonts

Uses Arial (Regular + Bold) as a fallback for Calibri, which is not available on macOS. Font paths:

```
/System/Library/Fonts/Supplemental/Arial.ttf
/System/Library/Fonts/Supplemental/Arial Bold.ttf
```

## Why a dedicated script?

The generic resumemaster pipeline produces single-column layouts. This CV uses a sidebar, an initials circle, and precise coordinate-level placement that requires direct PyMuPDF rendering. See the main README's "Dedicated Generator Scripts" section for the general pattern.
