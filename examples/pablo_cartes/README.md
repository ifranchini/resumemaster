# Pablo Cartes CV — 2021 Creative Layout

Dedicated generator script that replicates a 2-page creative CV layout using PyMuPDF directly, bypassing the generic pipeline.

## Layout

- **Page 1:** Two-column layout with grey sidebar (abstract, education, dot-rated skills, awards) and right main area (professional experience, certifications)
- **Page 2:** Full-width continuation (technical skills, consultancies, publication, other activities, languages)
- Header with initials circle, blue accent subtitles, contact block
- Dark divider bar separating header from body

## Files

| File | Purpose |
|---|---|
| `generate_cv.py` | Standalone generator script (hard-coded layout geometry + content) |
| `resume_data.json` | Resume content in the generic `ResumeData` JSON schema |
| `output/` | Generated PDFs (gitignored) |

## Usage

```bash
uv run python examples/pablo_cartes/generate_cv.py
```

Output: `examples/pablo_cartes/output/Pablo_Cartes_CV_Original_Style.pdf`

## Why a dedicated script?

The generic resumemaster pipeline produces single-column layouts. This CV uses a sidebar with dot-rated skills, an initials circle, and precise coordinate-level placement that requires direct PyMuPDF rendering. See the main README's "Dedicated Generator Scripts" section for the general pattern.

## Fonts

Uses Arial (Regular + Bold) as a fallback for Calibri, which is not available on macOS. The font paths point to `/System/Library/Fonts/Supplemental/Arial.ttf`.
