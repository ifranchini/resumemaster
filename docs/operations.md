# Operations Guide — Pablo Cartes CV

Step-by-step instructions for generating, validating, and exporting Pablo's resume.

## Generate the latest resume

```bash
cd /path/to/resumemaster
uv run python examples/pablo_cartes/generate_cv.py
```

Output (in `examples/pablo_cartes/output/`):
- `Pablo_Cartes_CV_Purple.pdf` — dark purple color scheme
- `Pablo_Cartes_CV_Red.pdf` — dark red color scheme

The script is self-contained — all content data, layout constants, and color schemes are defined inline. To update resume content, edit the `CONTENT` dict at the top of `generate_cv.py` and re-run.

## Current layout

Single-page US Letter (612 x 792 pt):

- **Header (top):** Initials circle + name/subtitles on the left, phone/email/address on the right
- **Sidebar (left, grey background):** Abstract, Education, Skills, Languages, Awards
- **Main area (right):** Professional Experience (3 roles), Certifications (4), Other Activities (4), Consultancies (10 clients)

## Editing content

All content is in the `CONTENT` dict at the top of `generate_cv.py`:

```python
CONTENT = {
    "name": "...",
    "subtitle1": "...",
    "subtitle2": "...",
    "phone": "...",
    "email": "...",
    "address": "...",
    "abstract": "...",
    "education": { "degree": "...", "institution": "...", "dates": "..." },
    "skills": ["...", "..."],
    "languages": [("English", "CEFR Level C1"), ...],
    "awards": ["...", "..."],
    "experience": [{ "title": "...", "company": "...", "dates": "...", "bullets": [...] }, ...],
    "diplomas": [{ "name": "...", "issuer": "...", "date": "..." }, ...],
    "consultancies": ["pipe | separated | client names"],
    "other_activities": ["...", "..."],
}
```

After editing, re-run the script to regenerate both PDFs.

## Adding or changing color variants

Color schemes are defined at the bottom of `generate_cv.py`:

```python
PURPLE_ACCENT = (0.345, 0.161, 0.420)  # #582A6B
PURPLE_BAR = (0.220, 0.110, 0.275)     # #381C46
RED_ACCENT = (0.545, 0.133, 0.133)     # #8B2222
RED_BAR = (0.361, 0.082, 0.082)        # #5C1515
```

Each variant calls `PabloCV(accent=..., bar=...).generate(output_path)`. To add a new variant (e.g., teal), define new tuples and add a call in the `__main__` block.

## Source PDFs

Original reference PDFs live in `output/original/` (gitignored). Used for visual comparison during validation:

- `CVPablo Cartes_English2021Nov.pdf` — the 2021 creative layout that inspired the design
- `Pablo_Cartes_CV_Pure_Industry.pdf` — industry-focused version (source of latest content)

## Validate output against the original

```bash
uv run resumemaster validate \
  output/original/Pablo_Cartes_CV_2021_Original.pdf \
  examples/pablo_cartes/output/Pablo_Cartes_CV_Purple.pdf \
  -o output/pablo_validation.json \
  --diff-dir output/pablo_diffs
```

This produces:
- `pablo_validation.json` — structural, SSIM, and pixel-diff scores
- `pablo_diffs/diff_page_0.png` — visual overlay showing differences

A score above 0.6 indicates reasonable layout match; above 0.8 is a close visual clone.

## Font fallbacks

The original CV uses **Calibri**, which is not available on macOS without Microsoft Office. The generator uses **Arial** (Regular + Bold) as a substitute:

```
/System/Library/Fonts/Supplemental/Arial.ttf
/System/Library/Fonts/Supplemental/Arial Bold.ttf
```

To use Calibri instead, update the `ARIAL_REGULAR` and `ARIAL_BOLD` constants in `generate_cv.py`.

## Google Docs export workflow

1. Generate the PDF as above
2. Upload to Google Drive
3. Right-click in Drive and select **Open with > Google Docs**
4. Review formatting — sidebar layout and multi-column sections may not convert cleanly
5. For best results, use `resume_data.json` to manually populate a Google Docs template instead of converting from PDF

## Content decisions (latest)

- Single-page layout (consolidated from earlier 2-page version)
- Title: "Distillery Manager" at Driftwood (previously "Master Distiller")
- Abstract focuses on Chemical Engineering applied to fermentation & distillation
- Skills as plain bulleted list (no dot ratings)
- Languages section added (English CEFR C1, Spanish Native)
- Publication citation embedded in Driftwood experience bullets
- Certifications include First Aid (2024) and Serving It Right (2022)
- Consultancies contracted to pipe-separated single line (10 clients)
- Contact info in header beside name (not below) to save vertical space
