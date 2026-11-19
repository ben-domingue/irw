"""Covariance family (irw_cov, source = "cov"): correlation tables printed in
CC BY open-access articles, read from the article's JATS XML in PubMed Central
(source "article tables", #3582; agent AH batch, 2026-11-18).

Source: Europe PMC full-text XML,
https://www.ebi.ac.uk/europepmc/webservices/rest/<PMCID>/fullTextXML.
Each article's <license> is read and must be CC BY (creativecommons.org/licenses/by/
or the words "Creative Commons Attribution (CC BY)" / "Creative Commons Attribution
License") or CC0; the script stops otherwise. An article with a retraction notice
(<related-article related-article-type="retraction-forward">) is refused.

Tables built (CONFIGS below): twelve tables (12 matrices) from ten articles, vetted
from the AC candidate list of 2026-11-18 (Europe PMC searches for "inter-item
correlation matrix", "polychoric correlation matrix" and similar, open access, CC BY /
CC0; the item-level-caption subset, continuing after the articles agent AG vetted).
Each is an item-level matrix of one scale or one questionnaire domain (inter-item
correlations), some with item means and SDs. The three almuhanna_2022 tables are the
three domains of one questionnaire, answered by one sample (`overlaps` names the
others). jacobs_2017_uewd8, lindig_2021_icansdm8 and the almuhanna_2022 tables are
printed as full squares, whose two copies of each cell are checked to agree; in
lindig_2021_icansdm8 two pairs disagree (one by 0.001, one with an upper copy printed
".-005"), and the lower triangle is taken, as the config lists (`asym`). The N of each
is from the caption, a table note or the article text, as noted in matrices.csv.

Parsing: as pmc_article_tables_ag.py. Each table is expanded into a grid (a cell with
rowspan/colspan fills every position it spans), so the `rows` and `cols` indices of a
config are grid positions. Cells are read as text. Significance stars and daggers are
stripped; nothing else is changed. Unicode minus (U+2212) and an en dash used as a
minus are read as "-", and spaces inside a cell are dropped. For each pair of variables
the script reads both cells (row i/column j and row j/column i): exactly one must hold
a number and the other must be empty or a dash, or both must hold the same number (a
full square). A full square may instead be read from its lower triangle only
(`lower_only`), with every upper copy compared to it: a pair listed in `asym` must
differ by at most 0.01 or have an upper copy that is not a number, and every other
pair must agree. A column that is not printed (the last item of fabry_2023_mcpi8,
whose triangle has no diagonal) is None in `cols`.

Printed row labels are checked against the expected labels of each part (`labels`,
or the variable names), after an optional `label_rx` that keeps the code or number of
a label (so that item wording printed as a row label is never copied here). Printed
column headers are checked too (`col_labels`). Where both the row labels and the column
headers are item wording (the almuhanna_2022 tables), `label_col` is None and each row
label is instead checked to equal the column header of the same item (`same_labels`),
so the wording is compared but never written down. Variable names are the source's
item codes or labels (E1, ESS1, ALMQ01, Eating, ...); where the source prints only a
number or item content, items are written as item1, item2, ..., never with item
wording.

Mean and SD cells are read from the cell a config names; the row label of each moment
is checked the same way as the matrix rows, and the column header is checked too
(`hdr`). A "M (SD)" cell (lindig_2021_icansdm8, Table 6) is split by a regex (`rx`).
They become mean/sd rows, values as printed.

Diagonal cells (1, 1.00, 1.0, 1.000, a dash or blank) are written as 1. Values are
written in shortest round-trip form of the published decimal (for example "0.40" ->
"0.4", ".800" -> "0.8"), i.e. unchanged.

`n` is the matrix N, written on every row.

Usage: python3 data/covariance/pmc_article_tables_ah.py <out dir>
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


NUMLAB = r"^(\d+)\."            # "3. <item wording>" -> 3
NUMS = lambda a, b: [str(i) for i in seq(a, b)]
MSD_M, MSD_SD = r"^(-?[\d.,]+) \(", r"\(([\d.,]+)\)$"   # "7.08 (1.97)"

UEWD = items(8)
COIDP = ["Eating", "Speaking", "Cleaning", "Sleeping", "EmotionalStatus", "Smiling",
         "Studying", "Social"]
COIDP_LAB = ["Eating", "Speaking", "Cleaning", "Sleeping", "Emotional Status", "Smiling",
             "Studying", "Social"]
ICAN = items(8)
OES = [f"E{i}" for i in seq(1, 8)]
ESS = [f"ESS{i}" for i in seq(1, 8)]
ESS_LAB = [f"ESS item-{i}" for i in seq(1, 8)]
EHEALS = items(8)
ALMQ = [f"ALMQ0{i}" for i in seq(1, 8)]
MCPI = items(8)
HANTA = items(8)


def square(pmcid, label, table, k, n):
    """AlMuhanna et al. (2022): a full square whose row labels and column headers are
    both item wording (row i must equal column i); items numbered in table order."""
    names = items(k)
    return dict(pmcid=pmcid, label=label, table=table, n=n, names=names, label_col=None,
                parts=[dict(names=names, rows=seq(1, k), cols=seq(1, k), same_labels=(0, 0),
                            col_labels=(0, None), lower_only=True, asym=[])])


CONFIGS = [
    # Jacobs et al. (2017), Table 5: full square (both copies checked to agree; only the
    # stars differ in some pairs); the Total score row and column are not read.
    dict(pmcid="PMC5709455", label="Table 5", table="jacobs_2017_uewd8", n=54,
         names=UEWD, label_col=0,
         parts=[dict(names=UEWD, rows=seq(1, 8), cols=seq(1, 8), col_labels=(0, UEWD),
                     lower_only=True, asym=[])]),
    # Chaudhary et al. (2022), Table 5: lower triangle; items named by the daily
    # performance each asks about, as printed.
    dict(pmcid="PMC9139254", label="Table 5", table="chaudhary_2022_coidp8", n=197,
         names=COIDP, label_col=0,
         parts=[dict(names=COIDP, labels=COIDP_LAB, rows=seq(1, 8), cols=seq(1, 8),
                     col_labels=(0, COIDP))]),
    # Lindig et al. (2021), Table 7: full square; the copies of (Item 1, Item 2) differ
    # (.166 below, .165 above) and the upper copy of (Item 3, Item 6) is printed ".-005"
    # (-.005 below): the lower triangle is taken. Means and SDs from Table 6 ("M (SD)"),
    # whose rows are numbered 1-8 (item wording in the next column is not read).
    dict(pmcid="PMC8171052", label="Table 7", table="lindig_2021_icansdm8", n=242,
         names=ICAN, label_col=0,
         parts=[dict(names=ICAN, rows=seq(1, 8), cols=seq(1, 8), col_labels=(0, ICAN),
                     lower_only=True, asym=[("item1", "item2"), ("item3", "item6")])],
         moments=[dict(m, rx=rx) for st, rx in (("mean", MSD_M), ("sd", MSD_SD))
                  for m in mom(st, "Table 6", ICAN, seq(1, 8), 2, 0, "Mean (SD)",
                               labels=NUMS(1, 8))]),
    # AlMuhanna et al. (2022), Tables 3-5: the knowledge, social and clinical setting
    # domains, each a full square (both copies checked to agree).
    square("PMC9797760", "Table 3", "almuhanna_2022_psychknow5", 5, 199),
    square("PMC9797760", "Table 4", "almuhanna_2022_psychsocial8", 8, 199),
    square("PMC9797760", "Table 5", "almuhanna_2022_psychclinic5", 5, 199),
    # Bimbashi et al. (2015), Table 3: lower triangle, 1.000 diagonal.
    dict(pmcid="PMC4548323", label="Table 3", table="bimbashi_2015_oes8", n=169,
         names=OES, label_col=0,
         parts=[dict(names=OES, rows=seq(1, 8), cols=seq(1, 8), col_labels=(0, OES))]),
    # Manzar et al. (2019), Table 4: upper triangle, blank diagonal (Spearman).
    dict(pmcid="PMC6367806", label="Table 4", table="manzar_2019_ess8", n=329,
         names=ESS, label_col=0,
         parts=[dict(names=ESS, labels=ESS_LAB, rows=seq(1, 8), cols=seq(1, 8),
                     col_labels=(0, ESS_LAB))]),
    # Chang & Schulz (2018), Table 2: lower triangle; item wording as row labels ("1. ...").
    dict(pmcid="PMC6069069", label="Table 2", table="chang_2018_eheals8", n=352,
         names=EHEALS, label_col=0, label_rx=NUMLAB,
         parts=[dict(names=EHEALS, labels=NUMS(1, 8), rows=seq(1, 8), cols=seq(1, 8),
                     col_labels=(0, NUMS(1, 8)))]),
    # Zakariya (2023), Table 3: polychoric, lower triangle; item means from Table 2 (its
    # variances are not taken).
    dict(pmcid="PMC10619651", label="Table 3", table="zakariya_2023_almq8", n=352,
         names=ALMQ, label_col=0,
         parts=[dict(names=ALMQ, rows=seq(1, 8), cols=seq(1, 8), col_labels=(0, ALMQ))],
         moments=mom("mean", "Table 2", ALMQ, seq(1, 8), 2, 0, "Mean")),
    # Fabry et al. (2023), Table 1: polychoric, lower triangle with no diagonal (columns
    # 1-7 only); item wording as row labels ("1. ..."). The M and SD columns are not
    # taken (see matrices.csv notes).
    dict(pmcid="PMC10756501", label="Table 1", table="fabry_2023_mcpi8", n=748,
         names=MCPI, label_col=0, label_rx=NUMLAB,
         parts=[dict(names=MCPI, labels=NUMS(1, 8), rows=seq(1, 8),
                     cols=seq(5, 11) + [None], col_labels=(0, NUMS(1, 7)))]),
    # Agrazal-Garcia et al. (2022), Table 3: polychoric, lower triangle under two header
    # rows; item means and SDs from Table 2 (rows numbered 1-8).
    dict(pmcid="PMC11397759", label="Table 3", table="agrazalgarcia_2022_hanta8", n=213,
         names=HANTA, label_col=0,
         parts=[dict(names=HANTA, rows=seq(2, 9), cols=seq(1, 8), col_labels=(1, HANTA))],
         moments=mom("mean", "Table 2", HANTA, seq(2, 9), 6, 1, "Mean", labels=NUMS(1, 8))
         + mom("sd", "Table 2", HANTA, seq(2, 9), 7, 1, "SD", labels=NUMS(1, 8))),
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
            or re.search(r"Creative Commons Attribution( \(CC BY\))? (L|l)icen[cs]e", ltxt)):
        raise SystemExit(f"{pmcid}: licence not CC BY / CC0: {href} {ltxt[:120]}")
    for ra in root.iter("related-article"):
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
        if d is not None and d.strip() not in DIAG:
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
            if norm(lab) != norm(m["lab"]):
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
        raise SystemExit("usage: python3 pmc_article_tables_ah.py <out dir>")
    main(sys.argv[1])
