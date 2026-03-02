"""
Pablo Cartes CV Generator — Original 2021 Layout Style

Replicates the exact visual layout of CVPablo Cartes_English2021Nov.pdf:
- US Letter (612 x 792 pt) single page
- Grey sidebar (left) with Abstract, Education, Skills (dot-rated), Awards
- Right main area with Professional Experience, Diplomas, Consultancies, Activities
- Header with initials circle, name, blue subtitles, contact block
- Dark divider bar separating header from body
- Blue accent color #3d89b6 for headings/subtitles

Populated with updated content from Pablo_Cartes_CV_Pure_Industry.pdf.
"""

import os

import pymupdf

# =============================================================================
# PATHS
# =============================================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")

# System font paths (macOS)
ARIAL_REGULAR = "/System/Library/Fonts/Supplemental/Arial.ttf"
ARIAL_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

# =============================================================================
# PAGE & LAYOUT CONSTANTS (from original 2021 CV analysis)
# =============================================================================
PAGE_W = 612.0  # US Letter
PAGE_H = 792.0

# Header region
HEADER_TOP = 28
HEADER_BOTTOM = 167

# Sidebar
SIDEBAR_LEFT = 11
SIDEBAR_RIGHT = 230
SIDEBAR_BG_TOP = 185  # grey background starts below divider bar
SIDEBAR_BG_BOTTOM = 784

# Right main area
MAIN_LEFT = 243
MAIN_RIGHT = 594

# Divider bar
BAR_Y_TOP = 167
BAR_Y_BOTTOM = 172

# Page margins
MARGIN_BOTTOM = 12

# Page 2 layout (full-width, no sidebar)
P2_MARGIN_LEFT = 40
P2_MARGIN_RIGHT = 40
P2_MARGIN_TOP = 40
P2_CONTENT_W = PAGE_W - P2_MARGIN_LEFT - P2_MARGIN_RIGHT

# =============================================================================
# COLORS (RGB 0-1 tuples)
# =============================================================================
BLUE = (0.239, 0.537, 0.714)  # #3d89b6
DARK = (0.122, 0.118, 0.118)  # #1f1e1e
WHITE = (1, 1, 1)
GREY_BG = (0.945, 0.945, 0.945)  # #f1f1f1
BAR_COLOR = (0.20, 0.20, 0.20)  # dark bar
MEDIUM_GREY = (0.55, 0.55, 0.55)
CIRCLE_BLUE = (0.239, 0.537, 0.714)

# =============================================================================
# FONT SIZES
# =============================================================================
NAME_SIZE = 26
SUBTITLE_SIZE = 13
CONTACT_SIZE = 8.5
SIDEBAR_HEADING_SIZE = 12
SIDEBAR_BODY_SIZE = 10
SKILL_LABEL_SIZE = 9.5
DOT_RADIUS = 3.2
MAIN_HEADING_SIZE = 14
MAIN_SUBHEADING_SIZE = 11.5
MAIN_BODY_SIZE = 9.5
DIPLOMA_SIZE = 9
SMALL_SIZE = 8.5

# =============================================================================
# CONTENT (updated from Pure Industry CV)
# =============================================================================
CONTENT = {
    "name": "PABLO E. CARTES",
    "subtitle1": "CHEMICAL ENGINEER",
    "subtitle2": "MASTER DISTILLER & CONSULTANT",
    "phone": "+1 250-986-7703",
    "email": "pabloecartes@gmail.com",
    "address": "Victoria, BC, Canada",
    "abstract": (
        "Master Distiller and Chemical Engineer with 12+ years in craft "
        "brewing and distilling, and 10+ years teaching advanced math and "
        "science. Led spirits production at Driftwood Brewing Company, "
        "producing gin, whisky, liqueurs, and specialty spirits distributed "
        "across British Columbia. Co-authored research evaluating 100+ yeast "
        "strains for novel spirit applications with UBC Wine Research Centre. "
        "Proven track record founding and operating a brewery, developing "
        "award-winning products, and consulting for 12+ craft producers "
        "across Chile, Argentina, Uruguay, and Canada."
    ),
    "education": {
        "degree": "Chemical Engineering",
        "institution": "Universidad de Santiago de Chile (USACH)",
        "dates": "2005 - 2013",
    },
    "skills": [
        ("Science", 5),
        ("Creativity", 5),
        ("Management", 4),
        ("English", 4),
        ("Business", 4),
    ],
    "awards": [
        "ADC 2025 Gold Medal Contemporary Gin: Contact Gin",
        "ADC 2025 Silver Medal Contemporary Gin: Parabola Gin",
        "BJCP Best Homebrew Mead in Latin America -- March 2020",
        "BJCP Best Homebrew Mead in Chile -- December 2018",
    ],
    "languages": [
        ("Spanish", "Native"),
        ("English", "IELTS General 7.5, CEFR C1 Advanced Proficiency"),
    ],
    "experience": [
        {
            "title": "Master Distiller",
            "company": "Driftwood Brewing Company (Driftwood Spirits)",
            "dates": "2022 - Feb 2026",
            "location": "Victoria, BC, Canada",
            "bullets": [
                "Led production of 6+ spirits including Contact Gin, "
                "Parabola Gin, Nocino, Blueberry Liqueur, and Oyster Spirit "
                "for province-wide distribution across BC",
                "Created \"Spirit Of The Deep,\" a bespoke single malt whisky "
                "anchoring the cocktail program at Fathom restaurant, "
                "Hotel Grand Pacific, Victoria BC",
                "Developed \"The Mage\" -- a 55% ABV cask-strength single malt "
                "aged in ex-bourbon and South American Malbec barrels",
                "Co-authored peer-reviewed paper in FEMS Yeast Research "
                "evaluating 100+ Canadian yeast strains for novel new-make "
                "spirit applications (Jan 2026)",
                "Collaborated with UBC Wine Research Centre on yeast-driven "
                "flavor diversification research for Canadian whisky",
            ],
        },
        {
            "title": "Fermentation & Distillation Consultant",
            "company": "Independent Practice",
            "dates": "2016 - 2021",
            "location": "Chile, Argentina, Uruguay & Canada",
            "bullets": [
                "Provided technical consulting on fermentation science, recipe "
                "development, and production optimization to 12+ craft "
                "producers between Chile, Argentina, Uruguay & Canada",
                "Advised on pot still operations, yeast management, and QC "
                "protocols for Alambiques Chile and Kayta Yeast Co.",
                "Created award-winning mead recipes, earning BJCP Best "
                "Homebrew Mead in Latin America recognition (2020)",
                "Directed the USACH HomeBrewing Lab, mentoring chemical "
                "engineering students in practical fermentation science (2017)",
            ],
        },
        {
            "title": "Founder & Head Brewer",
            "company": "Cerveza Rumba",
            "dates": "2012 - 2017",
            "location": "Chile",
            "bullets": [
                "Founded and operated craft brewery, managing all operations "
                "from recipe development and production through distribution",
                "Developed innovative fermentation processes combining chemical "
                "engineering principles with traditional brewing techniques",
            ],
        },
    ],
    "diplomas": [
        {
            "name": "Science & Cooking: Molecular Gastronomy",
            "issuer": "HarvardX",
            "date": "2020",
        },
        {
            "name": "Canvas Business Model Workshop",
            "issuer": "Pontifical Catholic U. of Chile",
            "date": "2018",
        },
    ],
    "consultancies": [
        "Boticario Bar (Argentina), 2020",
        "Quintal Distillery, 2019",
        "Punta Gruesa Brewing, 2017",
        "Alambiques Chile, 2017",
        "Kayta Yeast Co., 2016",
        "Gunnlod Mead, 2017",
    ],
    "other_activities": [
        "Technical Commercial Advisor, Alambiques Chile (2017 - 2018). "
        "Sold distillation equipment and provided technical consultancy "
        "across Chile, Argentina & Uruguay",
        "10+ years teaching Advanced Math & Science to students from "
        "High School through Chemical Engineering School",
        "HomeBrewing Lab Director, Chemical Engineering Dept, USACH (2017)",
        "Speaker: \"Entrepreneurship in the beer industry.\" National Congress "
        "of Chemical Students, Universidad de Santiago (2016)",
        "Real Estate Agent Assistant with over 1.5M USD in value of property sold "
        "(Jan 2017 - Jun 2017)",
    ],
    "technical_skills": {
        "DISTILLATION": [
            "Pot Still", "Column Still", "Gin Basket", "Whisky Production",
            "Botanical Extraction", "Spirit Maturation", "Barrel Aging", "Blending",
        ],
        "FERMENTATION & BREWING": [
            "Yeast Management", "Recipe Development", "Fermentation Kinetics",
            "Quality Control", "Sensory Evaluation", "Mashing", "All-Grain Brewing",
        ],
        "PRODUCTION & BUSINESS": [
            "Process Optimization", "Production Planning", "Inventory Management",
            "Brand Development", "Regulatory Compliance", "HACCP", "GMP",
        ],
        "SCIENCE": [
            "Chemical Engineering", "Molecular Gastronomy", "Laboratory Analysis",
            "Thermodynamics", "Research & Publication",
        ],
    },
    "publication": (
        "Marr, A., Cartes, P.E., et al. \"Evaluating Canadian yeast strains "
        "for novel new-make spirit applications.\" FEMS Yeast Research, "
        "January 2026."
    ),
}


# =============================================================================
# CV GENERATOR CLASS
# =============================================================================
class PabloCV:
    def __init__(self):
        self.doc = pymupdf.open()
        self.page = None
        self._setup_fonts()

    def _setup_fonts(self):
        """Load pymupdf.Font objects for text width measurement."""
        self.font_regular = pymupdf.Font(fontfile=ARIAL_REGULAR)
        self.font_bold = pymupdf.Font(fontfile=ARIAL_BOLD)

    # -------------------------------------------------------------------------
    # Text helpers
    # -------------------------------------------------------------------------
    def _text_width(self, text, fontfile, fontsize):
        """Measure text width using cached Font object."""
        font = self.font_bold if fontfile == ARIAL_BOLD else self.font_regular
        return font.text_length(text, fontsize=fontsize)

    def _insert(self, x, y, text, fontfile, fontsize, color):
        """Register font on page and insert text at (x, y)."""
        font_name = os.path.splitext(os.path.basename(fontfile))[0]
        # PyMuPDF fontname must not contain spaces
        font_name = font_name.replace(" ", "")
        self.page.insert_font(fontname=font_name, fontfile=fontfile)
        self.page.insert_text(
            pymupdf.Point(x, y),
            text,
            fontname=font_name,
            fontsize=fontsize,
            color=color,
        )

    def _wrap(self, text, fontfile, fontsize, max_width):
        """Word-wrap text to fit max_width. Returns list of lines."""
        words = text.split()
        lines = []
        current = ""
        for word in words:
            test = f"{current} {word}".strip() if current else word
            if self._text_width(test, fontfile, fontsize) <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    # -------------------------------------------------------------------------
    # Layout drawing
    # -------------------------------------------------------------------------
    def _draw_sidebar_bg(self):
        """Draw the grey background rectangle for the sidebar."""
        rect = pymupdf.Rect(
            SIDEBAR_LEFT, SIDEBAR_BG_TOP, SIDEBAR_RIGHT, SIDEBAR_BG_BOTTOM
        )
        self.page.draw_rect(rect, color=None, fill=GREY_BG)

    def _draw_divider_bar(self):
        """Draw the dark horizontal bar separating header from body."""
        rect = pymupdf.Rect(0, BAR_Y_TOP, PAGE_W, BAR_Y_BOTTOM)
        self.page.draw_rect(rect, color=None, fill=BAR_COLOR)

    def _draw_sidebar_divider(self, y):
        """Draw a thin horizontal line in the sidebar to separate sections."""
        self.page.draw_line(
            pymupdf.Point(SIDEBAR_LEFT + 8, y),
            pymupdf.Point(SIDEBAR_RIGHT - 8, y),
            color=MEDIUM_GREY,
            width=0.5,
        )

    # -------------------------------------------------------------------------
    # Header (y: 0-167)
    # -------------------------------------------------------------------------
    def _draw_header(self):
        """Draw the header: initials circle, name, subtitles, contact info."""
        # --- Initials circle (top-left) ---
        cx, cy = 65, 80
        r = 42
        # Filled circle background
        self.page.draw_circle(
            pymupdf.Point(cx, cy), r, color=BLUE, fill=WHITE, width=2.5
        )
        # Initials "P" and "C"
        self._insert(cx - 20, cy + 10, "P", ARIAL_BOLD, 28, BLUE)
        self._insert(cx + 5, cy + 10, "C", ARIAL_BOLD, 28, BLUE)

        # --- Name ---
        name_x = 130
        self._insert(name_x, 60, CONTENT["name"], ARIAL_BOLD, NAME_SIZE, DARK)

        # --- Subtitles (blue) ---
        self._insert(
            name_x, 80, CONTENT["subtitle1"], ARIAL_BOLD, 16, BLUE
        )
        self._insert(
            name_x, 96, CONTENT["subtitle2"], ARIAL_BOLD, 10, BLUE
        )

        # --- Contact block (right side of header) ---
        contact_x = 130
        contact_y = 115

        # Phone
        self._insert(
            contact_x, contact_y, "Phone:", ARIAL_BOLD, CONTACT_SIZE, DARK
        )
        label_w = self._text_width("Phone:  ", ARIAL_BOLD, CONTACT_SIZE)
        self._insert(
            contact_x + label_w,
            contact_y,
            CONTENT["phone"],
            ARIAL_REGULAR,
            CONTACT_SIZE,
            DARK,
        )
        contact_y += 13

        # Email
        self._insert(
            contact_x, contact_y, "Email:", ARIAL_BOLD, CONTACT_SIZE, DARK
        )
        label_w = self._text_width("Email:  ", ARIAL_BOLD, CONTACT_SIZE)
        self._insert(
            contact_x + label_w,
            contact_y,
            CONTENT["email"],
            ARIAL_REGULAR,
            CONTACT_SIZE,
            DARK,
        )
        contact_y += 13

        # Address
        self._insert(
            contact_x, contact_y, "Address:", ARIAL_BOLD, CONTACT_SIZE, DARK
        )
        label_w = self._text_width("Address:  ", ARIAL_BOLD, CONTACT_SIZE)
        self._insert(
            contact_x + label_w,
            contact_y,
            CONTENT["address"],
            ARIAL_REGULAR,
            CONTACT_SIZE,
            DARK,
        )

    # -------------------------------------------------------------------------
    # Sidebar sections (x: 11-230, y: 185-784)
    # -------------------------------------------------------------------------
    def _draw_abstract(self, y_start):
        """Draw the ABSTRACT section in the sidebar. Returns next y."""
        y = y_start
        # Section heading
        self._insert(
            SIDEBAR_LEFT + 12, y, "ABSTRACT", ARIAL_BOLD, SIDEBAR_HEADING_SIZE, BLUE
        )
        y += 16

        # Wrapped body text
        max_w = SIDEBAR_RIGHT - SIDEBAR_LEFT - 24
        lines = self._wrap(CONTENT["abstract"], ARIAL_REGULAR, SIDEBAR_BODY_SIZE, max_w)
        line_h = SIDEBAR_BODY_SIZE + 3.5
        for line in lines:
            self._insert(SIDEBAR_LEFT + 12, y, line, ARIAL_REGULAR, SIDEBAR_BODY_SIZE, DARK)
            y += line_h

        return y + 6

    def _draw_education(self, y_start):
        """Draw the EDUCATION section in the sidebar. Returns next y."""
        y = y_start
        self._draw_sidebar_divider(y - 4)
        y += 6

        self._insert(
            SIDEBAR_LEFT + 12, y, "EDUCATION", ARIAL_BOLD, SIDEBAR_HEADING_SIZE, BLUE
        )
        y += 16

        edu = CONTENT["education"]
        self._insert(
            SIDEBAR_LEFT + 12, y, edu["degree"], ARIAL_BOLD, 9.5, DARK
        )
        y += 13
        self._insert(
            SIDEBAR_LEFT + 12, y, edu["institution"], ARIAL_REGULAR, 8.5, DARK
        )
        y += 12
        self._insert(
            SIDEBAR_LEFT + 12, y, edu["dates"], ARIAL_REGULAR, 8, MEDIUM_GREY
        )
        y += 14

        return y + 4

    def _draw_skills(self, y_start):
        """Draw the SKILLS section with dot ratings. Returns next y."""
        y = y_start
        self._draw_sidebar_divider(y - 4)
        y += 6

        self._insert(
            SIDEBAR_LEFT + 12, y, "SKILLS", ARIAL_BOLD, SIDEBAR_HEADING_SIZE, BLUE
        )
        y += 18

        max_dots = 5
        for skill_name, rating in CONTENT["skills"]:
            # Skill label
            self._insert(
                SIDEBAR_LEFT + 12, y, skill_name, ARIAL_REGULAR, SKILL_LABEL_SIZE, DARK
            )

            # Dots (right-aligned in sidebar)
            dots_x_start = SIDEBAR_RIGHT - 14 - (max_dots * (DOT_RADIUS * 2 + 4))
            for i in range(max_dots):
                dot_x = dots_x_start + i * (DOT_RADIUS * 2 + 4)
                dot_y = y - DOT_RADIUS + 1
                center = pymupdf.Point(dot_x, dot_y)
                if i < rating:
                    # Filled dot
                    self.page.draw_circle(
                        center, DOT_RADIUS, color=BLUE, fill=BLUE
                    )
                else:
                    # Empty dot
                    self.page.draw_circle(
                        center, DOT_RADIUS, color=MEDIUM_GREY, fill=None, width=0.8
                    )

            y += 16

        return y + 2

    def _draw_awards(self, y_start):
        """Draw the AWARDS section in the sidebar. Returns next y."""
        y = y_start
        self._draw_sidebar_divider(y - 4)
        y += 6

        self._insert(
            SIDEBAR_LEFT + 12, y, "AWARDS", ARIAL_BOLD, SIDEBAR_HEADING_SIZE, BLUE
        )
        y += 16

        max_w = SIDEBAR_RIGHT - SIDEBAR_LEFT - 32
        for award in CONTENT["awards"]:
            # Bullet
            self._insert(SIDEBAR_LEFT + 14, y, "\u2022", ARIAL_REGULAR, 9, DARK)
            lines = self._wrap(award, ARIAL_REGULAR, 8.5, max_w)
            for line in lines:
                self._insert(SIDEBAR_LEFT + 24, y, line, ARIAL_REGULAR, 8.5, DARK)
                y += 11
            y += 2

        return y

    # -------------------------------------------------------------------------
    # Right main area (x: 243-594, y: 185-784)
    # -------------------------------------------------------------------------
    def _draw_experience(self, y_start):
        """Draw Professional Experience in the right column. Returns next y."""
        y = y_start
        main_w = MAIN_RIGHT - MAIN_LEFT - 8

        # Section heading
        self._insert(
            MAIN_LEFT, y, "Professional Experience", ARIAL_BOLD, MAIN_HEADING_SIZE, BLUE
        )
        y += 20

        for i, job in enumerate(CONTENT["experience"]):
            if i > 0:
                y += 12

            # Job title (bold)
            self._insert(
                MAIN_LEFT, y, job["title"], ARIAL_BOLD, MAIN_SUBHEADING_SIZE, DARK
            )
            y += 14

            # Company + dates line
            company_dates = f"{job['company']}  |  {job['dates']}"
            self._insert(
                MAIN_LEFT, y, company_dates, ARIAL_REGULAR, SMALL_SIZE, MEDIUM_GREY
            )
            y += 12

            # Bullet points
            for bullet in job["bullets"]:
                lines = self._wrap(bullet, ARIAL_REGULAR, MAIN_BODY_SIZE, main_w - 12)
                # Bullet character
                self._insert(MAIN_LEFT + 2, y, "\u2022", ARIAL_REGULAR, MAIN_BODY_SIZE, DARK)
                for j, line in enumerate(lines):
                    if j > 0:
                        y += MAIN_BODY_SIZE + 2.5
                    self._insert(
                        MAIN_LEFT + 12, y, line, ARIAL_REGULAR, MAIN_BODY_SIZE, DARK
                    )
                y += MAIN_BODY_SIZE + 3

        return y + 4

    def _draw_certifications(self, y_start):
        """Draw CERTIFICATIONS section in the right column. Returns next y."""
        y = y_start
        main_w = MAIN_RIGHT - MAIN_LEFT - 14

        self._insert(MAIN_LEFT, y, "CERTIFICATIONS", ARIAL_BOLD, 11, BLUE)
        y += 14

        for diploma in CONTENT["diplomas"]:
            self._insert(
                MAIN_LEFT + 2, y, "\u2022", ARIAL_REGULAR, DIPLOMA_SIZE, DARK
            )
            text = f"{diploma['name']} -- {diploma['issuer']}, {diploma['date']}"
            lines = self._wrap(text, ARIAL_REGULAR, DIPLOMA_SIZE, main_w)
            for line in lines:
                self._insert(
                    MAIN_LEFT + 12, y, line, ARIAL_REGULAR, DIPLOMA_SIZE, DARK
                )
                y += 11
            y += 2

        return y + 4

    def _draw_other_activities(self, y_start):
        """Draw OTHER ACTIVITIES section. Returns next y."""
        y = y_start
        main_w = MAIN_RIGHT - MAIN_LEFT - 14

        self._insert(
            MAIN_LEFT, y, "OTHER ACTIVITIES", ARIAL_BOLD, 11, BLUE
        )
        y += 14

        for item in CONTENT["other_activities"]:
            self._insert(MAIN_LEFT + 2, y, "\u2022", ARIAL_REGULAR, MAIN_BODY_SIZE, DARK)
            lines = self._wrap(item, ARIAL_REGULAR, MAIN_BODY_SIZE, main_w)
            for j, line in enumerate(lines):
                if j > 0:
                    y += MAIN_BODY_SIZE + 2.5
                self._insert(
                    MAIN_LEFT + 12, y, line, ARIAL_REGULAR, MAIN_BODY_SIZE, DARK
                )
            y += MAIN_BODY_SIZE + 4

        return y

    # -------------------------------------------------------------------------
    # Page 2 helpers
    # -------------------------------------------------------------------------
    def _draw_p2_section_heading(self, y, title):
        """Draw a blue section heading with underline rule on page 2. Returns next y."""
        self._insert(P2_MARGIN_LEFT, y, title, ARIAL_BOLD, MAIN_HEADING_SIZE, BLUE)
        rule_y = y + 4
        self.page.draw_line(
            pymupdf.Point(P2_MARGIN_LEFT, rule_y),
            pymupdf.Point(PAGE_W - P2_MARGIN_RIGHT, rule_y),
            color=BLUE,
            width=0.8,
        )
        return y + 18

    def _draw_p2_technical_skills(self, y_start):
        """Draw the Technical Skills section with categories. Returns next y."""
        y = self._draw_p2_section_heading(y_start, "Technical Skills")
        body_size = 10
        cat_size = 10.5
        max_w = P2_CONTENT_W

        for category, skills in CONTENT["technical_skills"].items():
            # Category label (bold, uppercase)
            self._insert(P2_MARGIN_LEFT, y, category, ARIAL_BOLD, cat_size, DARK)
            y += cat_size + 5

            # Skills as pipe-separated text
            skills_text = "  |  ".join(skills)
            lines = self._wrap(skills_text, ARIAL_REGULAR, body_size, max_w)
            for line in lines:
                self._insert(P2_MARGIN_LEFT, y, line, ARIAL_REGULAR, body_size, DARK)
                y += body_size + 3.5
            y += 6

        return y + 4

    def _draw_p2_certs_consultancies(self, y_start):
        """Draw CERTIFICATIONS and CONSULTANCIES side-by-side. Returns next y."""
        mid_x = PAGE_W / 2 + 10
        item_size = 9.5

        # Headings
        y = y_start
        self._insert(
            P2_MARGIN_LEFT, y, "CERTIFICATIONS", ARIAL_BOLD, 12, BLUE
        )
        self._insert(mid_x, y, "CONSULTANCIES", ARIAL_BOLD, 12, BLUE)
        # Underlines
        rule_y = y + 4
        self.page.draw_line(
            pymupdf.Point(P2_MARGIN_LEFT, rule_y),
            pymupdf.Point(mid_x - 20, rule_y),
            color=BLUE,
            width=0.8,
        )
        self.page.draw_line(
            pymupdf.Point(mid_x, rule_y),
            pymupdf.Point(PAGE_W - P2_MARGIN_RIGHT, rule_y),
            color=BLUE,
            width=0.8,
        )
        y += 18

        # Certifications (left column)
        dy = y
        for diploma in CONTENT["diplomas"]:
            self._insert(
                P2_MARGIN_LEFT + 2, dy, "\u2022", ARIAL_REGULAR, item_size, DARK
            )
            name_line = f"{diploma['name']} --"
            issuer_line = f"{diploma['issuer']}. {diploma['date']}"
            # Name (bold)
            self._insert(
                P2_MARGIN_LEFT + 14, dy, name_line, ARIAL_BOLD, item_size, DARK
            )
            dy += item_size + 3
            # Issuer (regular, grey)
            self._insert(
                P2_MARGIN_LEFT + 14, dy, issuer_line, ARIAL_REGULAR, item_size, MEDIUM_GREY
            )
            dy += item_size + 8

        # Consultancies (right column)
        cy = y
        consult_w = PAGE_W - P2_MARGIN_RIGHT - mid_x - 14
        for client in CONTENT["consultancies"]:
            self._insert(mid_x + 2, cy, "\u2022", ARIAL_REGULAR, item_size, DARK)
            lines = self._wrap(client, ARIAL_REGULAR, item_size, consult_w)
            for line in lines:
                self._insert(
                    mid_x + 14, cy, line, ARIAL_REGULAR, item_size, DARK
                )
                cy += item_size + 3
            cy += 2

        return max(dy, cy) + 8

    def _draw_p2_publication(self, y_start):
        """Draw the PUBLICATION section. Returns next y."""
        y = self._draw_p2_section_heading(y_start, "Publication")
        body_size = 10

        lines = self._wrap(
            CONTENT["publication"], ARIAL_REGULAR, body_size, P2_CONTENT_W
        )
        for line in lines:
            self._insert(P2_MARGIN_LEFT, y, line, ARIAL_REGULAR, body_size, DARK)
            y += body_size + 3.5

        return y + 8

    def _draw_p2_other_activities(self, y_start):
        """Draw OTHER ACTIVITIES section on page 2. Returns next y."""
        y = self._draw_p2_section_heading(y_start, "Other Activities")
        body_size = 10

        for item in CONTENT["other_activities"]:
            self._insert(
                P2_MARGIN_LEFT + 2, y, "\u2022", ARIAL_REGULAR, body_size, DARK
            )
            lines = self._wrap(item, ARIAL_REGULAR, body_size, P2_CONTENT_W - 16)
            for j, line in enumerate(lines):
                if j > 0:
                    y += body_size + 3
                self._insert(
                    P2_MARGIN_LEFT + 14, y, line, ARIAL_REGULAR, body_size, DARK
                )
            y += body_size + 6

        return y + 4

    def _draw_p2_languages(self, y_start):
        """Draw LANGUAGES section on page 2. Returns next y."""
        y = self._draw_p2_section_heading(y_start, "Languages")
        body_size = 10.5

        parts = [
            f"{lang} ({level})" for lang, level in CONTENT["languages"]
        ]
        text = "    \u00b7    ".join(parts)
        self._insert(P2_MARGIN_LEFT, y, text, ARIAL_REGULAR, body_size, DARK)

        return y + body_size + 8

    # -------------------------------------------------------------------------
    # Generate
    # -------------------------------------------------------------------------
    def generate(self, output_path):
        """Generate the complete 2-page CV PDF."""
        # ==== PAGE 1: Creative 2-column layout ====
        self.page = self.doc.new_page(width=PAGE_W, height=PAGE_H)

        # Background elements (drawn first so text overlays)
        self._draw_sidebar_bg()
        self._draw_divider_bar()

        # Header
        self._draw_header()

        # Sidebar sections
        sidebar_y = 200
        sidebar_y = self._draw_abstract(sidebar_y)
        sidebar_y = self._draw_education(sidebar_y)
        sidebar_y = self._draw_skills(sidebar_y)
        self._draw_awards(sidebar_y)

        # Right main area: Work Experience (takes full right column on page 1)
        main_y = 190
        main_y = self._draw_experience(main_y)

        # If space remains on page 1 after experience, add certifications
        # Push certifications toward the bottom of the page
        if main_y < 720:
            cert_y = max(main_y + 16, 665)
            self._draw_certifications(cert_y)

        # ==== PAGE 2: Full-width continuation ====
        self.page = self.doc.new_page(width=PAGE_W, height=PAGE_H)

        # Thin blue accent bar at top of page 2
        self.page.draw_rect(
            pymupdf.Rect(0, 0, PAGE_W, 4), color=None, fill=BLUE
        )

        p2_y = P2_MARGIN_TOP
        p2_gap = 14
        p2_y = self._draw_p2_technical_skills(p2_y) + p2_gap
        p2_y = self._draw_p2_certs_consultancies(p2_y) + p2_gap
        p2_y = self._draw_p2_publication(p2_y) + p2_gap
        p2_y = self._draw_p2_other_activities(p2_y) + p2_gap
        self._draw_p2_languages(p2_y)

        # Subset fonts and save
        self.doc.subset_fonts()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        self.doc.save(output_path, garbage=4, deflate=True)
        self.doc.close()
        print(f"CV generated: {output_path} (2 pages)")


# =============================================================================
# MAIN
# =============================================================================
if __name__ == "__main__":
    out = os.path.join(OUTPUT_DIR, "Pablo_Cartes_CV_Original_Style.pdf")
    cv = PabloCV()
    cv.generate(out)
