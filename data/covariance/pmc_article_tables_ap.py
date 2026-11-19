"""Covariance family (irw_cov, source = "cov"): correlation tables printed in
CC BY open-access articles, read from the article's JATS XML in PubMed Central
(source "article tables", #3582; agent AP batch, 2026-11-19).

Source: Europe PMC full-text XML,
https://www.ebi.ac.uk/europepmc/webservices/rest/<PMCID>/fullTextXML.
Each article's <license> is read and must be CC BY (creativecommons.org/licenses/by/
or the words "Creative Commons Attribution (CC BY)" / "Creative Commons Attribution
License", optionally with a version) or CC0; the script stops otherwise. An article
whose own metadata (<article-meta>) carries a retraction link (<related-article
related-article-type="retraction-forward"> or "retracted-article") is refused. Links of
that kind inside the reference list mark a retracted *cited* paper, not this article,
so they are not read.

Tables built (CONFIGS below): from agent AO's screened-only row and the scale-level
pass over the AC candidate list of 2026-11-18 (resumed at AO's stopping point,
PMC9017747). The eight EUROHIS-QOL items in a German population sample, item level;
the PEZPS total and criterion variables among doctoral talent in China; top management
team boundary-spanning leadership, motivational climate and innovative behaviour;
misogyny, hypermasculinity and violent intentions in UK men and women (two groups);
work overload, trait motivation, exhaustion, job satisfaction and happiness; trait awe,
small-self, self-other inclusion and cooperative propensity of high-school students; the
NPPBQ subscales and the MBI subscales of nurses; mindfulness, self-compassion, grit and
mind wandering of UK meditators; the GIS-TW subscales, BSRI and RSES of transgender
women in China; inclusive leadership, teaching efficacy, professional identity and
thriving of young teachers; sociodemographics, pandemic effect, DASS, resilience and social
support of adults in Panama; the VASQ dimensions and the SDQ of adolescents in residential
care in Portugal. The N of each is from the caption, a table note or the
article text, as noted in matrices.csv.

Parsing: as pmc_article_tables_am.py, pmc_article_tables_an.py and pmc_article_tables_ao.py
(whose build code this file copies unchanged).
Each table is expanded into a grid (a cell with rowspan/colspan fills every position it
spans), so the `rows` and `cols` indices of a config are grid positions. Cells are read
as text. Significance stars are stripped; nothing else is changed. Unicode minus
(U+2212) and an en dash used as a minus are read as "-", and spaces inside a cell are
dropped ("0.22 **" -> "0.22"). For each pair of variables the script reads both cells
(row i/column j and row j/column i): exactly one must hold a number and the other must
be empty or a dash, or both must hold the same number. Where the two triangles hold two
samples each group reads its own triangle (`lower_only` / `upper_only`;
rottweiler_2024_misogyny8: men below, women above). A matrix with no column for its last
variable has that column given as None.

Printed row labels are checked against the expected labels of each part (`labels`,
or the variable names), after an optional `label_rx` that keeps the name of a label.
Printed column headers are checked too (`col_labels`). Variable names are the printed
scale names; where a table prints letters or abbreviations (jiang_2026_pezps9: A-I;
gao_2026_thriving9: "Gend", "Expe", "Edu") the names are spelled out from the table note
or text and the printed labels are checked. The EUROHIS-QOL items are item1-item8 (their
printed labels in TABLE 2 are item wording, which is not copied; only the leading item
number is read). Codings printed in a label ("Gender (0, 1)", "Age (years)") and footnote
marks ("†") are dropped from the name; U+2010 hyphens are written as "-". oviedo_2023_panama9
prints "___" on the diagonal (`diag_extra`); simao_2026_vasq9 prints its SDs in parentheses
in an unlabelled row under the means.

Mean and SD cells are read from the cell a config names; the row label of each moment
is checked the same way as the matrix rows, and the column header is checked too
(`hdr`). "M (SD)" cells are split by two regexes. They become mean/sd rows, values as
printed.
Cronbach's alpha printed on the diagonal (liu_2022_tmtbsl9, raines_2026_overload9 in
parentheses, hu_2020_nppbq9 as "α = x") becomes rel rows; `diag_rx` lets the diagonal
cell hold it. "M(SD)" cells in rottweiler_2024_misogyny8 have a line break between the
two numbers, which the cell text drops.

Diagonal cells (1, 1.00, a dash or blank) are written as 1. Values are written in
shortest round-trip form of the published decimal (for example "0.40" -> "0.4", ".80"
-> "0.8", "-0.00" -> "-0.0"), i.e. unchanged.

`n` is the matrix N, written on every row.

Usage: python3 data/covariance/pmc_article_tables_ap.py <out dir>
(set IRW_PMC_XML_DIR=<dir of PMCxxxx.xml> to read saved copies instead of Europe PMC)
"""
import csv
import os
import re
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path


def items(k, stem="item", sep=""):
    return [f"{stem}{sep}{i}" for i in range(1, k + 1)]


def seq(a, b):
    return list(range(a, b + 1))


# --- configs -----------------------------------------------------------------
def mom(stat, label, names, rows, col, hdr_row, hdr, labels=None, label_col=0, label_rx=None):
    """One moment per variable, read from rows[i] of column col of table label; the row
    label (labels[i]) and the column header (row hdr_row) are checked."""
    labels = labels or names
    return [dict(stat=stat, var=v, label=label, row=r, col=col, rx=None, lab=l,
                 label_col=label_col, label_rx=label_rx, comma=False, hdr=(hdr_row, hdr))
            for v, r, l in zip(names, rows, labels)]


def row_mom(stat, label, names, row, cols, lab, hdr_row, hdrs, label_col=0):
    """One moment per variable, read from one row (label `lab`) across columns cols; each
    column header (row hdr_row) is checked."""
    return [dict(stat=stat, var=v, label=label, row=row, col=c, rx=None, lab=lab,
                 label_col=label_col, label_rx=None, comma=False, hdr=(hdr_row, h))
            for v, c, h in zip(names, cols, hdrs)]


def msd(label, names, rows, col, hdr_row, hdr, m_rx, sd_rx, **kw):
    """Mean and SD printed in one cell ("M (SD)" or "M ± SD"), split by two regexes."""
    return [dict(m, rx=rx) for st, rx in (("mean", m_rx), ("sd", sd_rx))
            for m in mom(st, label, names, rows, col, hdr_row, hdr, **kw)]


NUMLAB = r"^(\d+)\."           # "3. <item wording>" -> 3
LEADNUM = r"^(\d+)"             # "6 (R)" -> 6
NUMS = lambda a, b: [str(i) for i in seq(a, b)]
MSD_M, MSD_SD = r"^(-?[\d.]+) \(", r"\(([\d.]+)\)$"          # "3.15 (1.55)"
MSD_PM_M, MSD_PM_SD = r"^(-?[\d.]+) ?± ?", r" ?± ?([\d.]+)$"     # "4.68 ± 2.31", "5.67±2.09"

def lower_sq(pmcid, label, table, n, k, first, hdr_row, hdrs, label_rx=NUMLAB, labels=None, **kw):
    """A lower-triangle (or diagonal-only upper) square: rows first..first+k-1, columns
    1..k, row labels numbered (label_rx) and column headers hdrs."""
    names = items(k)
    return dict(pmcid=pmcid, label=label, table=table, n=n, names=names, label_col=0,
                label_rx=label_rx,
                parts=[dict(names=names, labels=labels or NUMS(1, k), rows=seq(first, first + k - 1),
                            cols=seq(1, k), col_labels=(hdr_row, hdrs))], **kw)


def wording_sq(pmcid, label, table, n, k, full=False, **kw):
    """A square whose row labels and column headers are item content (not copied): each
    row label must equal the column header of the same position; a full square
    (`full`) must be symmetric."""
    names = items(k)
    part = dict(names=names, rows=seq(1, k), cols=seq(1, k), same_labels=(0, 0))
    if full:
        part.update(lower_only=True, asym=[])
    return dict(pmcid=pmcid, label=label, table=table, n=n, names=names, label_col=None,
                parts=[part], **kw)


def square(pmcid, label, table, n, names, rows, cols, hdr_row, hdrs, labels=None, label_col=0,
           label_rx=None, part_kw=None, **kw):
    """One square printed as a lower triangle (rows and columns in the same order); row
    labels (after label_rx) must be `labels` (default: the names) and the column headers
    of row hdr_row must be hdrs."""
    part = dict(names=names, labels=labels or names, rows=rows, cols=cols, col_labels=(hdr_row, hdrs))
    part.update(part_kw or {})
    return dict(pmcid=pmcid, label=label, table=table, n=n, names=names, label_col=label_col,
                label_rx=label_rx, parts=[part], **kw)


def diag_mom(label, names, rows, cols, hdr_row, hdrs, rx, label_rx=None, labels=None, label_col=0):
    """A reliability printed on the diagonal (cell rows[i], cols[i]), split by rx."""
    labels = labels or names
    return [dict(stat="rel", var=v, label=label, row=r, col=c, rx=rx, lab=l, label_col=label_col,
                 label_rx=label_rx, comma=False, hdr=(hdr_row, h))
            for v, r, c, l, h in zip(names, rows, cols, labels, hdrs)]


DOTNUM = r"^\d+\.\s*(.+)$"      # "1. Demand" -> "Demand"
PARNUM = r"^\(\d+\)\s*(.+)$"    # "(1) Global job satisfaction" -> "Global job satisfaction"
PAREN = r"^\(([\d.]+)\)$"        # "(0.83)" -> "0.83"
PAREN_OR_DASH = r"^\((–|[\d.]+)\)$"   # "(–)" or "(0.954)"
LEADNUM_M = r"^([−-]?[\d.]+)"      # "0.54 #" -> "0.54"

EUR_RX = r"^(\d+)–"                 # "1–<item wording>" -> 1 (wording not read)
PEZ = ["PEZPS total", "Psychological safety need", "Occupational burnout", "Job insecurity", "Meaningfulness of work",
       "Boundary-control need", "Reverse mobility intention", "HEI job-search intention", "Enterprise retention intention"]
TMT = ["Gender", "Age", "Education level", "Working years", "Position level", "Organization type", "TMTBSL", "PMC", "IB"]
ROT = ["Misogyny", "Revenge motivation", "Hypermasculinity", "Collective narcissism", "Group threat",
       "Violent extremist intentions", "Willingness to use violence", "Support for violence against women"]
ROT_M, ROT_SD = r"^(-?[\d.]+)\(", r"\(([\d.]+)\)$"        # "2.63(1.17)", "1.50(.68)"
RAI = ["EE", "ACM", "AM", "OV", "HA", "JS", "Age", "Tenure (O)", "Tenure (R)"]
AWE = ["Gender", "Age", "Trait awe", "Small-self", "Self-other inclusion", "Cooperative propensity", "Inclusiveness",
       "Reciprocity", "Gregariousness"]
AWE_LAB = ["Gender (0, 1)", "Age (years)"] + AWE[2:]
NPP = ["NPPBQ total", "Positive occupational perception", "Good nurse-patient relationship",
       "Recognition from family, relatives, and friends", "Sense of belonging to a team", "Self-growth",
       "Emotional exhaustion", "Reduced personal accomplishment", "Depersonalization"]
NPP_LAB = ["Total score of the NPPBQ"] + NPP[1:]
ALPHA_EQ = r"^α = ([\d.]+)$"         # "α = 0.937" -> "0.937"
MIN = ["Age", "Gender", "Hours of meditation per week", "Income", "Education", "Mindfulness", "Self-compassion", "Grit",
       "Mind-wandering"]
MIN_LAB = ["Age", "Gender (0 = male, 1 = female)", "Hours of meditation per week†"] + MIN[3:]
GIS = ["Social Gender Role Affirmation", "Physical and Mental Incongruence", "Physical Transition",
       "Self-affirmative Gender Expression", "Sexual Attraction", "Sexual Pleasure", "Masculinity", "Femininity", "RSES"]
THR = ["Gender", "Age", "Experience", "Title", "Education", "Thriving at Work", "Inclusive Leadership",
       "Teaching Efficacy", "Professional Identity"]
THR_LAB = ["Gend", "Age", "Expe", "Title", "Edu"] + THR[5:]

PAN = ["Sex", "Age", "Education", "Income", "Effect of Pandemic", "DASS", "Resilience", "Social Support",
       "Cohabitation"]
VAS = ["Insecure-ambivalent", "Insecure-avoidant", "Proximity-seeking", "SDQ total", "Emotional problems",
       "Behavioral problems", "Hyperactivity/inattention", "Peer relationship problems", "Prosocial behaviors"]


def rot(group, part_kw):
    """Rottweiler et al. (2024), Table 2.: men below the diagonal, women above; M(SD) per
    group in columns 1 (Men) and 2 (Women); matrix in columns 6-13."""
    col, hdr = (1, "Men") if group == "men" else (2, "Women")
    return dict(pmcid="PMC11974915", label="Table 2.", table="rottweiler_2024_misogyny8",
                n=730 if group == "men" else 769, names=ROT, label_col=0, label_rx=DOTNUM, group=group,
                parts=[dict(names=ROT, rows=seq(2, 9), cols=seq(6, 13), col_labels=(1, NUMS(1, 8)), **part_kw)],
                moments=msd("Table 2.", ROT, seq(2, 9), col, 0, hdr, ROT_M, ROT_SD, label_rx=DOTNUM))


CONFIGS = [
    # Hettich et al. (2022), TABLE 3: EUROHIS-QOL items, item level (labels are the
    # item numbers); lower triangle with a 1 diagonal in columns 5-12; item M and SD from
    # TABLE 2, whose row labels begin with the item number (wording not read).
    square("PMC9579288", "TABLE 3", "hettich_2022_eurohisqol8", 2515, items(8), seq(3, 10), seq(5, 12), 1,
           NUMS(1, 8), labels=NUMS(1, 8),
           moments=mom("mean", "TABLE 2", items(8), seq(2, 9), 3, 0, "M", labels=NUMS(1, 8), label_rx=EUR_RX)
           + mom("sd", "TABLE 2", items(8), seq(2, 9), 4, 0, "SD", labels=NUMS(1, 8), label_rx=EUR_RX)),
    # Jiang et al. (2026), Table 8: letters A-I (table note); M and SD in columns 1-2; lower
    # triangle with a dash diagonal in columns 3-11.
    square("PMC13687386", "Table 8", "jiang_2026_pezps9", 838, PEZ, seq(1, 9), seq(3, 11), 0,
           list("ABCDEFGHI"), labels=list("ABCDEFGHI"),
           moments=mom("mean", "Table 8", PEZ, seq(1, 9), 1, 0, "M", labels=list("ABCDEFGHI"))
           + mom("sd", "Table 8", PEZ, seq(1, 9), 2, 0, "SD", labels=list("ABCDEFGHI"))),
    # Liu et al. (2022), Study 2, Table 6: Mean and SD in columns 1-2; lower triangle in columns
    # 3-11, the diagonal blank for the six demographics and Cronbach's alpha for the
    # three scales (rel rows).
    square("PMC9798318", "Table 6", "liu_2022_tmtbsl9", 504, TMT, seq(1, 9), seq(3, 11), 0, NUMS(1, 9),
           label_rx=DOTNUM, diag_rx=r"0\.\d{3}",
           moments=mom("mean", "Table 6", TMT, seq(1, 9), 1, 0, "Mean", label_rx=DOTNUM)
           + mom("sd", "Table 6", TMT, seq(1, 9), 2, 0, "SD", label_rx=DOTNUM)
           + diag_mom("Table 6", TMT[6:], seq(7, 9), seq(9, 11), 0, NUMS(7, 9), r"^([\d.]+)$", label_rx=DOTNUM)),
    # Rottweiler et al. (2024), Table 2.: men (N = 730) below, women (N = 769) above.
    rot("men", dict(lower_only=True)),
    rot("women", dict(upper_only=True)),
    # Raines et al. (2026), Table 1.: lower triangle; alphas in parentheses on the
    # diagonal for the six scales (rel rows), dashes for age and tenure; Mean and SD rows.
    square("PMC13093254", "Table 1.", "raines_2026_overload9", 844, RAI, seq(1, 9), seq(1, 9), 0, NUMS(1, 9),
           label_rx=DOTNUM, diag_rx=r"\(0\.\d+\)",
           moments=row_mom("mean", "Table 1.", RAI, 10, seq(1, 9), "Mean", 0, NUMS(1, 9))
           + row_mom("sd", "Table 1.", RAI, 11, seq(1, 9), "SD", 0, NUMS(1, 9))
           + diag_mom("Table 1.", RAI[:6], seq(1, 6), seq(1, 6), 0, NUMS(1, 6), PAREN, label_rx=DOTNUM)),
    # Wu et al. (2024), TABLE 1: lower triangle, diagonal blank (1-3) or 1 (4-9);
    # M and SD rows.
    square("PMC11317189", "TABLE 1", "wu_2024_awe9", 907, AWE, seq(1, 9), seq(1, 9), 0, NUMS(1, 9),
           labels=AWE_LAB, label_rx=DOTNUM,
           moments=row_mom("mean", "TABLE 1", AWE, 10, seq(1, 9), "M", 0, NUMS(1, 9))
           + row_mom("sd", "TABLE 1", AWE, 11, seq(1, 9), "SD", 0, NUMS(1, 9))),
    # Hu et al. (2020), Study 3, Table 4: M (SD) in column 1; lower triangle in columns 2-9
    # (headers "1."-"8."), no column for the last variable; "α = x" on the diagonal for
    # the NPPBQ total and subscales (rel rows), dashes for the MBI subscales.
    square("PMC6993446", "Table 4", "hu_2020_nppbq9", 271, NPP, seq(1, 9), seq(2, 9) + [None], 0,
           [f"{i}." for i in range(1, 9)], labels=NPP_LAB, label_rx=DOTNUM, diag_rx=r"α = 0\.\d{3}",
           moments=msd("Table 4", NPP, seq(1, 9), 1, 0, "M (SD)", MSD_M, MSD_SD, labels=NPP_LAB, label_rx=DOTNUM)
           + diag_mom("Table 4", NPP[:6], seq(1, 6), seq(2, 7), 0, [f"{i}." for i in range(1, 7)], ALPHA_EQ,
                      labels=NPP_LAB[:6], label_rx=DOTNUM)),
    # Cheung & Djekou (2024), Table 2: "(j) label"; lower triangle with a
    # dash diagonal; M and SD rows (dashes for gender).
    square("PMC11032370", "Table 2", "cheung_2024_mindwandering9", 487, MIN, seq(1, 9), seq(1, 9), 0,
           [f"({i})" for i in range(1, 10)], labels=MIN_LAB, label_rx=PARNUM,
           moments=row_mom("mean", "Table 2", [v for v in MIN if v != "Gender"], 10, [1] + seq(3, 9), "M", 0,
                           [f"({i})" for i in [1] + seq(3, 9)])
           + row_mom("sd", "Table 2", [v for v in MIN if v != "Gender"], 11, [1] + seq(3, 9), "SD", 0,
                     [f"({i})" for i in [1] + seq(3, 9)])),
    # Han et al. (2022), Table 4: n in column 1, M and SD in columns 2-3; lower triangle with a
    # 1 diagonal in columns 4-12.
    square("PMC8763696", "Table 4", "han_2022_gistw9", 244, GIS, seq(1, 9), seq(4, 12), 0, NUMS(1, 9),
           label_rx=DOTNUM,
           moments=mom("mean", "Table 4", GIS, seq(1, 9), 2, 0, "M", label_rx=DOTNUM)
           + mom("sd", "Table 4", GIS, seq(1, 9), 3, 0, "SD", label_rx=DOTNUM)),
    # Gao et al. (2026), Table 3: abbreviated labels; Mean and Sd
    # in columns 1-2; lower triangle with a 1 diagonal in columns 3-11.
    square("PMC13228515", "Table 3", "gao_2026_thriving9", 755, THR, seq(1, 9), seq(3, 11), 0, NUMS(1, 9),
           labels=THR_LAB,
           moments=mom("mean", "Table 3", THR, seq(1, 9), 1, 0, "Mean", labels=THR_LAB)
           + mom("sd", "Table 3", THR, seq(1, 9), 2, 0, "Sd", labels=THR_LAB)),
    # Oviedo et al. (2023), Table 2: "j. label", lower triangle with a "___" diagonal; Mean
    # and Standard Deviation rows (N/A for sex).
    square("PMC10687484", "Table 2", "oviedo_2023_panama9", 475, PAN, seq(1, 9), seq(1, 9), 0, NUMS(1, 9),
           label_rx=DOTNUM, diag_extra=("___",),
           moments=row_mom("mean", "Table 2", PAN[1:], 10, seq(2, 9), "Mean", 0, NUMS(2, 9))
           + row_mom("sd", "Table 2", PAN[1:], 11, seq(2, 9), "Standard Deviation", 0, NUMS(2, 9))),
    # Simão et al. (2026), Table 5: "j. label", upper triangle with a dash diagonal; an
    # M(SD) row of means and an unlabelled row of SDs in parentheses.
    square("PMC13114654", "Table 5", "simao_2026_vasq9", 438, VAS, seq(1, 9), seq(1, 9), 0, NUMS(1, 9),
           label_rx=DOTNUM,
           moments=row_mom("mean", "Table 5", VAS, 10, seq(1, 9), "M(SD)", 0, NUMS(1, 9))
           + [dict(m, rx=PAREN) for m in row_mom("sd", "Table 5", VAS, 11, seq(1, 9), "", 0, NUMS(1, 9))]),
]

DIAG = {"1", "-", "–", "—", "‐", "", "1.00", "1.0", "1.000", "1.0000"}
EMPTY = {"", "-", "–", "—", "‐", "--"}


def txt(e):
    return re.sub(r"\s+", " ", "".join(e.itertext())).strip()


def get(pmcid):
    local = os.environ.get("IRW_PMC_XML_DIR")
    if local:
        return (Path(local) / f"{pmcid}.xml").read_bytes()
    url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML"
    req = urllib.request.Request(url, headers={"User-Agent": "irw-cov-build"})
    for attempt in range(6):  # Europe PMC sometimes answers with an HTTP 5xx or an HTML error page
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                b = r.read()
            if b.lstrip()[:1] == b"<" and b"<article" in b[:3000]:
                return b
        except (urllib.error.URLError, TimeoutError) as e:
            print(f"{pmcid}: {e}; retrying", file=sys.stderr)
        time.sleep(10 * (attempt + 1))
    raise SystemExit(f"{pmcid}: no article XML from Europe PMC")


def num(cell, where, comma=False, strip=None):
    s = cell.replace("−", "-").replace("–", "-").replace(" ", "")
    if strip:
        s = re.sub(strip, "", s)
    s = re.sub(r"[*∗†⁎]+$", "", s)
    if comma:
        s = s.replace(",", ".")
    if not re.fullmatch(r"-?(\d+)?\.\d+|-?\d+", s):
        raise SystemExit(f"{where}: cannot read {cell!r}")
    return repr(float(s))


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def label_of(lab, rx, where):
    lab = lab.strip()
    if rx:
        m = re.match(rx, lab)
        if not m:
            raise SystemExit(f"{where}: label {lab!r} does not match {rx!r}")
        lab = next(g for g in m.groups() if g)
    return lab


def check_article(pmcid, root):
    lic = root.find(".//license")
    href = (lic.get("{http://www.w3.org/1999/xlink}href") or "") if lic is not None else ""
    links = " ".join(e.get("{http://www.w3.org/1999/xlink}href") or "" for e in lic.iter()) if lic is not None else ""
    ltxt = txt(lic) if lic is not None else ""
    if re.search(r"NonCommercial|NoDeriv|by-nc|by-nd|by-sa|ShareAlike", href + links + ltxt):
        raise SystemExit(f"{pmcid}: restricted licence {href} {ltxt[:120]}")
    if not (re.search(r"creativecommons\.org/(licenses/by/|publicdomain/zero)", href + links + ltxt)
            or re.search(r"Creative Commons Attribution( \(CC BY\))?( \d\.\d)? (L|l)icen[cs]e", ltxt)):
        raise SystemExit(f"{pmcid}: licence not CC BY / CC0: {href} {ltxt[:120]}")
    meta = root.find(".//article-meta")
    for ra in (meta.iter("related-article") if meta is not None else []):
        if ra.get("related-article-type") in ("retraction-forward", "retracted-article"):
            raise SystemExit(f"{pmcid}: retracted")


def table_rows(root, label, span_fill=True):
    tws = [t for t in root.iter("table-wrap")
           if t.find("label") is not None and txt(t.find("label")) == label]
    if len(tws) != 1:
        raise SystemExit(f"{label}: found {len(tws)} tables")
    grid = {}
    for i, tr in enumerate(tws[0].iter("tr")):
        j = 0
        for c in (c for c in tr if c.tag in ("td", "th")):
            while (i, j) in grid:
                j += 1
            rs, cs = int(c.get("rowspan") or 1), int(c.get("colspan") or 1)
            for a in range(rs):
                for b in range(cs):  # without span_fill only the first spanned cell holds the text
                    grid[(i + a, j + b)] = txt(c) if span_fill or (a, b) == (0, 0) else ""
            j += cs
    nr = max(k[0] for k in grid) + 1
    return [[grid.get((i, j), "") for j in range(max([k[1] for k in grid if k[0] == i] + [-1]) + 1)]
            for i in range(nr)]


def read_part(cfg, part, rows, where):
    """{frozenset(pair): (value, raw)} for the pairs printed in one panel."""
    names, ridx, cidx = part["names"], part["rows"], part["cols"]
    labels = part.get("labels", names)
    comma, strip = cfg.get("comma", False), cfg.get("strip")
    k = len(names)
    if len(ridx) != k or len(cidx) != k or len(labels) != k:
        raise SystemExit(f"{where}: bad part config")
    for nm, r in zip(labels, ridx):  # printed row labels must be the expected ones
        if r is not None and cfg["label_col"] is not None:
            lab = label_of(rows[r][cfg["label_col"]], cfg.get("label_rx"), where)
            if norm(lab) != norm(nm):
                raise SystemExit(f"{where}: row label {lab!r} is not {nm!r}")
    if part.get("same_labels"):         # row label i must equal column header i (item wording)
        lc, hr = part["same_labels"]
        for a, (r, c) in enumerate(zip(ridx, cidx)):
            if not norm(rows[r][lc]) or norm(rows[r][lc]) != norm(rows[hr][c]):
                raise SystemExit(f"{where}: row {r} label is not column {c} header")
        if len({norm(rows[r][lc]) for r in ridx}) != k:
            raise SystemExit(f"{where}: repeated row labels")
    if part.get("col_labels") and part["col_labels"][1] is not None:  # printed column headers
        hr, hl = part["col_labels"]
        got_cols = [c for c in cidx if c is not None]
        if len(got_cols) != len(hl):
            raise SystemExit(f"{where}: bad col_labels config")
        for c, h in zip(got_cols, hl):
            if norm(rows[hr][c]) != norm(h):
                raise SystemExit(f"{where}: column {c} header {rows[hr][c]!r} is not {h!r}")

    def cell(a, b):
        r, c = ridx[a], cidx[b]
        if r is None or c is None or c >= len(rows[r]):
            return None
        return rows[r][c]

    def absent(a, b):                   # no printed position for this cell in this part
        return ridx[a] is None or cidx[b] is None

    asym = {frozenset(p) for p in part.get("asym", [])}
    seen_asym = set()
    got = {}
    for i in range(k):
        d = cell(i, i)
        if (d is not None and d.strip() not in DIAG | set(cfg.get("diag_extra", ()))
                and not (cfg.get("diag_rx") and re.fullmatch(cfg["diag_rx"], d.strip()))):
            raise SystemExit(f"{where}: diagonal {names[i]} is {d!r}")
        for j in range(i):
            a, b = cell(i, j), cell(j, i)       # a: below the diagonal, b: above it
            a = None if a is None or a.strip() in EMPTY else a
            b = None if b is None or b.strip() in EMPTY else b
            key = frozenset((names[i], names[j]))
            if part.get("upper_only"):          # the lower triangle holds another sample
                if b is None:
                    raise SystemExit(f"{where}: missing upper cell ({names[j]}, {names[i]})")
                a = None
            if part.get("lower_only"):
                if a is None:
                    raise SystemExit(f"{where}: missing lower cell ({names[i]}, {names[j]})")
                if part.get("asym") is not None:   # a full square: the copies must agree
                    if b is None:
                        raise SystemExit(f"{where}: missing upper cell ({names[j]}, {names[i]})")
                    va = num(a, where, comma, strip)
                    if key in asym:             # a listed disagreement: the upper copy differs
                        try:                    # by at most 0.01, or cannot be read as a number
                            vb = num(b, where, comma, strip)
                        except SystemExit:
                            vb = None
                        if vb == va or (vb is not None and abs(float(va) - float(vb)) > 0.01 + 1e-9):
                            raise SystemExit(f"{where}: listed pair ({names[i]}, {names[j]}): {a!r} / {b!r}")
                        seen_asym.add(key)
                    elif va != num(b, where, comma, strip):
                        raise SystemExit(f"{where}: asymmetric ({names[i]}, {names[j]}): {a!r} / {b!r}")
                b = None
            if a is None and b is None:
                if absent(i, j) or absent(j, i):   # the pair is printed in another panel
                    continue
                raise SystemExit(f"{where}: missing cell ({names[i]}, {names[j]})")
            if a is not None and b is not None and num(a, where, comma, strip) != num(b, where, comma, strip):
                raise SystemExit(f"{where}: asymmetric ({names[i]}, {names[j]}): {a!r} / {b!r}")
            raw = a if a is not None else b
            v = num(raw, f"{where} ({names[i]},{names[j]})", comma, strip)
            if abs(float(v)) >= 1:
                raise SystemExit(f"{where}: |r| >= 1 at ({names[i]},{names[j]})")
            got[key] = (v, raw)
    if seen_asym != asym:
        raise SystemExit(f"{where}: asymmetric pairs {seen_asym} are not the listed {asym}")
    return got


def build(cfg, root):
    where = f"{cfg['pmcid']} {cfg['label']} {cfg.get('group', '')}".strip()
    rows = table_rows(root, cfg["label"], cfg.get("span_fill", True))
    if cfg.get("title"):                # a block title printed in the table (group, n)
        tr, tc, tt = cfg["title"]
        if rows[tr][tc].strip() != tt:
            raise SystemExit(f"{where}: block title {rows[tr][tc]!r} is not {tt!r}")
    names = cfg["names"]
    k = len(names)
    if len(set(names)) != k:
        raise SystemExit(f"{where}: duplicate names")
    cells = {}
    for part in cfg["parts"]:
        if not set(part["names"]) <= set(names):
            raise SystemExit(f"{where}: part names")
        for key, (v, raw) in read_part(cfg, part, rows, where).items():
            if key in cells and cells[key][0] != v:
                raise SystemExit(f"{where}: panels disagree on {sorted(key)}")
            cells[key] = (v, raw)

    g = {"group": cfg["group"]} if cfg.get("group") else {}
    out, check = [], []
    for i in range(k):
        for j in range(i):
            key = frozenset((names[i], names[j]))
            if key not in cells:
                if cfg.get("blank_across_parts") and not any(key <= set(p["names"]) for p in cfg["parts"]):
                    cells[key] = ("", "")       # measured, not reported (different blocks)
                else:
                    raise SystemExit(f"{where}: pair {sorted(key)} not printed")
            v, raw = cells[key]
            out.append({"stat": "cor", "var1": names[i], "var2": names[j], "value": v,
                        "n": cfg["n"], **g})
            check.append((cfg.get("group", ""), names[i], names[j], raw))
        out.append({"stat": "cor", "var1": names[i], "var2": names[i], "value": "1",
                    "n": cfg["n"], **g})

    seen = set()
    for m in cfg.get("moments", []):
        if m["var"] not in names or (m["stat"], m["var"]) in seen:
            raise SystemExit(f"{where}: bad moment {m}")
        seen.add((m["stat"], m["var"]))
        t = table_rows(root, m["label"])
        if isinstance(m["lab"], tuple):     # the label must equal the text of a named cell
            _, rl, rr, rc, pre = m["lab"]   # pre: compare only the first `pre` letters/digits
            want = norm(table_rows(root, rl)[rr][rc])[:pre]
            if not want or norm(t[m["row"]][m["label_col"]])[:pre] != want:
                raise SystemExit(f"{where}: {m['label']} row {m['row']} is not {rl} row {rr}")
        elif m["lab"] is not None:          # None: the row label is item wording (not checked)
            lab = label_of(t[m["row"]][m["label_col"]], m["label_rx"], where)
            if norm(lab) != norm(m["lab"]) or (not norm(m["lab"]) and lab != m["lab"]):
                raise SystemExit(f"{where}: {m['label']} row {m['row']} is {lab!r}, not {m['lab']!r}")
        if m.get("hdr"):
            hr, h = m["hdr"]
            if norm(t[hr][m["col"]]) != norm(h):
                raise SystemExit(f"{where}: {m['label']} column {m['col']} is {t[hr][m['col']]!r}, not {h!r}")
        c = t[m["row"]][m["col"]].strip()
        if m.get("rx"):
            hit = re.search(m["rx"], c)
            if not hit:
                raise SystemExit(f"{where}: {m['stat']} cell {c!r} for {m['var']!r}")
            raw = hit.group(1)
        else:
            raw = c
        v = num(raw, f"{where} {m['stat']} {m['var']}", m.get("comma", False))
        if m["stat"] == "sd" and float(v) <= 0:
            raise SystemExit(f"{where}: sd {v} for {m['var']}")
        out.append({"stat": m["stat"], "var1": m["var"], "var2": "", "value": v, "n": cfg["n"], **g})
        check.append((cfg.get("group", ""), m["stat"] + ":" + m["var"], "", raw))
    return out, check


def main(outdir):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    cache, tables = {}, {}
    for cfg in CONFIGS:
        if cfg["pmcid"] not in cache:
            cache[cfg["pmcid"]] = ET.fromstring(get(cfg["pmcid"]))
            check_article(cfg["pmcid"], cache[cfg["pmcid"]])
        rows, check = build(cfg, cache[cfg["pmcid"]])
        t = tables.setdefault(cfg["table"], {"rows": [], "check": [], "grouped": bool(cfg.get("group"))})
        if t["grouped"] != bool(cfg.get("group")):
            raise SystemExit(f"{cfg['table']}: grouped and ungrouped configs")
        t["rows"] += rows
        t["check"] += check
    for name, t in tables.items():
        cols = ["stat", "var1", "var2", "value", "n"] + (["group"] if t["grouped"] else [])
        with open(outdir / f"{name}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            w.writerows(t["rows"])
        with open(outdir / f"{name}.check.tsv", "w", encoding="utf-8") as f:
            for row in t["check"]:
                f.write("\t".join(row) + "\n")
        print(f"{name}: {len(t['rows'])} rows")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 pmc_article_tables_ap.py <out dir>")
    main(sys.argv[1])
