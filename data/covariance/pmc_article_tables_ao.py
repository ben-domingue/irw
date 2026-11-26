"""Covariance family (irw_cov, source = "cov"): correlation tables printed in
CC BY open-access articles, read from the article's JATS XML in PubMed Central
(source "article tables", #3582; agent AO batch, 2026-11-19).

Source: Europe PMC full-text XML,
https://www.ebi.ac.uk/europepmc/webservices/rest/<PMCID>/fullTextXML.
Each article's <license> is read and must be CC BY (creativecommons.org/licenses/by/
or the words "Creative Commons Attribution (CC BY)" / "Creative Commons Attribution
License", optionally with a version) or CC0; the script stops otherwise. An article
whose own metadata (<article-meta>) carries a retraction link (<related-article
related-article-type="retraction-forward"> or "retracted-article") is refused. Links of
that kind inside the reference list mark a retracted *cited* paper, not this article,
so they are not read.

Tables built (CONFIGS below): from the screened-only rows of agents AM and AN and the
scale-level pass over the AC candidate list of 2026-11-18 (resumed at AN's stopping
point, PMC11239019). Functional classification, competitive anxiety and performance of
wheelchair basketball players; prayer, internal dialogue and well-being; Bangla PCL-5
subscales and PHQ-9; the Macquarie Anxiety Behavioural Scale and parenting stress;
fatigue, depression, symptom burden and functional status of older hospice patients;
postpartum work resumption stress and maternal well-being; the nine CORAS items (COVID-19
Own Risk Appraisal Scale), item level; the Spanish QPC-OPS factors; the AHEAD leadership
instrument and the LPI; psychological capital, subjective well-being and career
commitment of preschool teachers; digital creativity, emotional intelligence, self-esteem
and personality of adolescents; the Chronic Time Pressure Inventory and the PSS-10 in two
studies. The N of each is from the caption, a table note or the article text, as noted
in matrices.csv.

Parsing: as pmc_article_tables_am.py and pmc_article_tables_an.py (whose build code this
file copies unchanged).
Each table is expanded into a grid (a cell with rowspan/colspan fills every position it
spans), so the `rows` and `cols` indices of a config are grid positions. Cells are read
as text. Significance stars are stripped; nothing else is changed. Unicode minus
(U+2212) and an en dash used as a minus are read as "-", and spaces inside a cell are
dropped ("0.22 **" -> "0.22"). For each pair of variables the script reads both cells
(row i/column j and row j/column i): exactly one must hold a number and the other must
be empty or a dash, or both must hold the same number. Where the two triangles hold two
samples each group reads its own triangle (`lower_only` / `upper_only`); denovan_2019_ctpi8
prints its two studies as stacked upper triangles, each read with `upper_only` after its
block title ("Study 1", "Study 2") is checked. A matrix with no column for its last
variable has that column given as None.

Printed row labels are checked against the expected labels of each part (`labels`,
or the variable names), after an optional `label_rx` that keeps the name of a label.
Printed column headers are checked too (`col_labels`). Variable names are the printed
scale names or codes (QPC-OPS factors prefixed F1-F8); the CORAS items are item1-item9
(their printed labels paraphrase item content and are not copied). Where a printed
name carries a footnote marker ("Competition level1", "Anxiety a") the marker is
dropped from the name; en and em dashes inside names are written as "-". One printed
row label is cut short ("Living arrange", abduljawad_2022_hospice9) and is checked as
printed.

Mean and SD cells are read from the cell a config names; the row label of each moment
is checked the same way as the matrix rows, and the column header is checked too
(`hdr`). "M (SD)" cells are split by two regexes. They become mean/sd rows, values as
printed.
Cronbach's alpha printed in a column or row of its own (islam_2022_pcl5bangla11,
puchalskawasyl_2019_prayer11) becomes rel rows. In okorn_2024_workresume9 the means of
three subdomains carry a footnote letter ("3.99 b"), which a regex drops. Diagonal
marks other than 1 or a dash that a table uses (U+2015, U+2212) are listed per config
(`diag_extra`).

Diagonal cells (1, 1.00, a dash or blank) are written as 1. Values are written in
shortest round-trip form of the published decimal (for example "0.40" -> "0.4", ".80"
-> "0.8", "-0.00" -> "-0.0"), i.e. unchanged.

`n` is the matrix N, written on every row.

Usage: python3 data/covariance/pmc_article_tables_ao.py <out dir>
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

BOS = ["Competition level", "Sex", "Age", "Experience", "Classification", "Perceived demands", "Self-efficacy",
       "Cognitive worry", "Somatic arousal", "Points scored", "Coach evaluation", "Pre-game average"]
BOS_LAB = ["Competition level1"] + BOS[1:]
PUC = ["Inward", "Upward", "Outward", "Pure", "Identity", "Supportive", "Ruminative", "Confronting", "Simulation",
       "Perspective", "Well-being"]
ISL = ["R", "A", "NACM", "AR", "NA", "An", "DA", "AA", "EB", "Total PCL-5", "Total PHQ-9"]
ISL_RX = r"^\d+\.\s*(.+)$"
CHE = ["MABS", "GAD", "PANIC", "SAD", "SOC", "SPEC", "PSI-SF-15", "PD", "PCDI", "DC"]
ABD = ["Age", "Gender", "PPS", "CESD-10", "FSC", "MSAS severity", "MSAS distress", "MSAS occurrence",
       "Living arrangement"]
ABD_LAB = ABD[:-1] + ["Living arrange"]   # the row label is printed cut short
ABD_HDR = ["Age", "Gender", "PPS", "CESD −10", "FSC", "MSAS severity", "MSAS distress", "MSAS occurrence",
           "Living arrangement"]
OKO = ["Overall score", "Work-life imbalance", "Child-related concerns", "Lack of enrichment", "Anxiety",
       "Postpartum depression", "Perceived stress", "Work-to-family conflict", "Family-to-work conflict"]
OKO_LAB = ["Overall score", "Work–life imbalance", "Child-related concerns", "Lack of enrichment", "Anxiety a",
           "Postpartum depression", "Perceived stress a", "Work-to-family conflict", "Family-to-work conflict a"]
TOM = ["F1 Encounter", "F2 Participation-Empowerment", "F3 Participation-Information", "F4 Discharge",
       "F5 Support", "F6 Environment", "F7 Next of kin", "F8 Accessibility", "Total"]
TOM_LAB = ["F1. Encounter", "F2. Participation—Empowerment", "F3. Participation—Information", "F4. Discharge",
           "F5. Support", "F6. Environment", "F7. Next of kin", "F8. Accessibility", "Total Spanish QPC-OPS"]
OKO_HDR = [l.replace(" a", "") for l in OKO_LAB]   # column headers carry no footnote marker
ANG = ["Seniority", "AHEAD Values", "AHEAD Skills", "AHEAD Total", "LPI Model", "LPI Inspire", "LPI Challenge",
       "LPI Enable", "LPI Encourage", "LPI Total"]
ANG_RX = r"^(.+?)(?: \(\d+\))?$"    # "AHEAD Values (2)" -> "AHEAD Values"
GAN = ["Self-efficacy", "Hope", "Resilience", "Optimism", "Subjective well-being", "Affective commitment",
       "Continuance commitment", "Normative commitment"]
PER = ["Self-expressive creativity", "Emotional attention", "Emotional clarity", "Emotional repair", "Self-esteem",
       "Extraversion", "Agreeableness", "Conscientiousness", "Neuroticism", "Openness to experience"]
DEN = ["Total CTPI", "Feeling Harried", "Cognitive Awareness of Time Shortage", "Total PSS-10", "Distress",
       "Coping", "Gender", "Age"]


def den(group, n, first):
    """Denovan & Dagnall (2019), TABLE 4: one study's block (section row, then rows
    first..first+7); upper triangle in columns 4-10 with a blank diagonal (column 3 is
    empty); M and SD in columns 1-2."""
    rows = seq(first, first + 7)
    return dict(pmcid="PMC6904346", label="TABLE 4", table="denovan_2019_ctpi8", n=n, names=DEN, label_col=0,
                label_rx=PARNUM, group=group, title=(first - 1, 0, "Study 1" if group == "study1" else "Study 2"),
                parts=[dict(names=DEN, rows=rows, cols=seq(3, 10), col_labels=(0, NUMS(1, 8)), upper_only=True)],
                moments=mom("mean", "TABLE 4", DEN, rows, 1, 0, "M", label_rx=PARNUM)
                + mom("sd", "TABLE 4", DEN, rows, 2, 0, "SD", label_rx=PARNUM))


OKO_M = r"^([\d.]+)(?: b)?$"       # "3.99 b" -> "3.99" (b: a footnote on the subdomain means)

CONFIGS = [
    # Bosma & Van Yperen (2020), Table 3: number in column 0, label in column 1; M and SD
    # in columns 2-3; lower triangle in columns 4-14 with a dash diagonal (one U+2212),
    # no column for the last variable.
    square("PMC7538635", "TABLE 3", "bosma_2020_wheelchair12", 141, BOS, seq(1, 12), seq(4, 14) + [None], 0,
           NUMS(1, 11), labels=BOS_LAB, label_col=1, diag_extra=("−",),
           moments=mom("mean", "TABLE 3", BOS, seq(1, 12), 2, 0, "M", labels=BOS_LAB, label_col=1)
           + mom("sd", "TABLE 3", BOS, seq(1, 12), 3, 0, "SD", labels=BOS_LAB, label_col=1)),
    # Puchalska-Wasyl & Zarzycka (2019), Table 2: number in column 0, label in column 1;
    # lower triangle in columns 2-12 with a dash diagonal; M, SD and alpha rows below.
    square("PMC7359138", "Table 2", "puchalskawasyl_2019_prayer11", 193, PUC, seq(1, 11), seq(2, 12), 0,
           NUMS(1, 11), label_col=1,
           moments=row_mom("mean", "Table 2", PUC, 12, seq(2, 12), "M", 0, NUMS(1, 11), label_col=1)
           + row_mom("sd", "Table 2", PUC, 13, seq(2, 12), "SD", 0, NUMS(1, 11), label_col=1)
           + row_mom("rel", "Table 2", PUC, 14, seq(2, 12), "α", 0, NUMS(1, 11), label_col=1)),
    # Islam et al. (2022), Table 3: M (SD) in column 1, alpha in column 3; lower triangle in
    # columns 4-13 with a U+2015 diagonal, no column for the last variable.
    square("PMC9020159", "Table 3", "islam_2022_pcl5bangla11", 10605, ISL, seq(1, 11), seq(4, 13) + [None], 0,
           NUMS(1, 10), labels=["R", "A", "NACM", "AR", "NA", "An", "DA", "AA", "EB", "Total PCL-5", "Total PHQ-9"],
           label_rx=ISL_RX, diag_extra=("―",),
           moments=msd("Table 3", ISL, seq(1, 11), 1, 0, "Mean (SD)", MSD_M, MSD_SD, label_rx=ISL_RX)
           + mom("rel", "Table 3", ISL, seq(1, 11), 3, 0, "α", label_rx=ISL_RX)),
    # Chen et al. (2023), Table 6: lower triangle with a 1 diagonal; no moments.
    square("PMC10680268", "Table 6", "chen_2023_mabs10", 1007, CHE, seq(1, 10), seq(1, 10), 0, NUMS(1, 10),
           label_rx=DOTNUM),
    # Abduljawad et al. (2022), Table 2: lower triangle with a 1 diagonal in columns 1-9
    # (the last row label is printed "Living arrange", the column header in full);
    # Mean and SD in columns 10-11 (dashes for gender and living arrangement).
    square("PMC11022836", "Table 2.", "abduljawad_2022_hospice9", 519, ABD, seq(1, 9), seq(1, 9), 0, ABD_HDR,
           labels=ABD_LAB,
           moments=mom("mean", "Table 2.", [v for v in ABD if v not in ("Gender", "Living arrangement")],
                       [1, 3, 4, 5, 6, 7, 8], 10, 0, "Mean")
           + mom("sd", "Table 2.", [v for v in ABD if v not in ("Gender", "Living arrangement")],
                 [1, 3, 4, 5, 6, 7, 8], 11, 0, "SD")),
    # Okorn et al. (2024), Table 3 (Phase 3, N = 291): lower triangle with a dash
    # diagonal in columns 1-9; M and SD rows below (Min and Max rows not taken).
    square("PMC11915766", "Table 3", "okorn_2024_workresume9", 291, OKO, seq(1, 9), seq(1, 9), 0, OKO_HDR,
           labels=OKO_LAB,
           moments=[dict(m, rx=OKO_M) for m in row_mom("mean", "Table 3", OKO, 10, seq(1, 9), "M", 0, OKO_HDR)]
           + row_mom("sd", "Table 3", OKO, 11, seq(1, 9), "SD", 0, OKO_HDR)),
    # Jaspal et al. (2020), Table 2: CORAS items, item level (row labels are item content,
    # only the number is read); M and SD in columns 1-2; Spearman lower triangle in
    # columns 3-11 with a blank diagonal.
    square("PMC7593702", "Table 2.", "jaspal_2020_coras9", 470, items(9), seq(1, 9), seq(3, 11), 0, NUMS(1, 9),
           labels=NUMS(1, 9), label_rx=NUMLAB,
           moments=mom("mean", "Table 2.", items(9), seq(1, 9), 1, 0, "M", labels=NUMS(1, 9), label_rx=NUMLAB)
           + mom("sd", "Table 2.", items(9), seq(1, 9), 2, 0, "SD", labels=NUMS(1, 9), label_rx=NUMLAB)),
    # Tomás-Jiménez et al. (2022), Table 2: lower triangle with a 1.000 diagonal; the
    # factors and the total score.
    square("PMC8901654", "Table 2", "tomasjimenez_2022_qpcops9", 260, TOM, seq(1, 9), seq(1, 9), 0,
           ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "Total"], labels=TOM_LAB),
    # Ang et al. (2016), Table 3: Spearman lower triangle with a blank diagonal in columns
    # 1-9 (headers "(1)"-"(9)"), no column for the last variable (LPI Total).
    square("PMC4759728", "Table 3", "ang_2016_ahead10", 106, ANG, seq(1, 10), seq(1, 9) + [None], 0,
           [f"({i})" for i in range(1, 10)], label_rx=ANG_RX),
    # Gan & Cheng (2021), Table 1: number in column 0, label in column 1; lower triangle
    # with a dash diagonal in columns 2-9; Mean and SD rows below.
    square("PMC8339257", "Table 1", "gan_2021_psycap8", 759, GAN, seq(1, 8), seq(2, 9), 0, NUMS(1, 8), label_col=1,
           moments=row_mom("mean", "Table 1", GAN, 9, seq(2, 9), "Mean", 0, NUMS(1, 8), label_col=1)
           + row_mom("sd", "Table 1", GAN, 10, seq(2, 9), "SD", 0, NUMS(1, 8), label_col=1)),
    # Perez-Fuentes et al. (2019), Table 1: "j. label", lower triangle with a dash
    # diagonal in columns 1-10; Mean and SD rows below.
    square("PMC6888092", "Table 1", "perezfuentes_2019_creativity10", 742, PER, seq(1, 10), seq(1, 10), 0,
           NUMS(1, 10), label_rx=DOTNUM,
           moments=row_mom("mean", "Table 1", PER, 11, seq(1, 10), "Mean", 0, NUMS(1, 10))
           + row_mom("sd", "Table 1", PER, 12, seq(1, 10), "SD", 0, NUMS(1, 10))),
    # Denovan & Dagnall (2019), TABLE 4: Study 1 (N = 401) and Study 2 (N = 163) stacked.
    den("study1", 401, 2),
    den("study2", 163, 11),
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
        raise SystemExit("usage: python3 pmc_article_tables_ao.py <out dir>")
    main(sys.argv[1])
