"""Covariance family (irw_cov, source = "cov"): correlation tables printed in
CC BY open-access articles, read from the article's JATS XML in PubMed Central
(source "article tables", #3582; agent U batch, 2026-11-18).

Source: Europe PMC full-text XML,
https://www.ebi.ac.uk/europepmc/webservices/rest/<PMCID>/fullTextXML.
Each article's <license> is read and must be CC BY (creativecommons.org/licenses/by/
or the words "Creative Commons Attribution (CC BY)" / "Creative Commons Attribution
License") or CC0; the script stops otherwise. Every DOI was checked on Crossref
(2026-11-18).

Tables built (CONFIGS below): ten correlation tables from ten articles, chosen
from the Europe PMC caption scan of 2026-11-17 (scratchpad scripts_n/cands.tsv),
skipping candidates already built, held or vetted by agent P. Six are item-level
matrices (inter-item correlations); the others are among scale or subscale scores.
The N of each is from the caption, a table note or the article text, as noted in
matrices.csv.

Parsing: cells are read as text. Significance stars and daggers are stripped;
nothing else is changed. Unicode minus (U+2212) and an en dash used as a minus are
read as "-", and spaces inside a cell are dropped ("0.544 **" -> 0.544). Each config
names the <tr> holding each variable's row (`rows`) and the cell holding its column
(`cols`, counting <td>/<th> elements; None when the table prints no row or column
for it). `layout` says where the published cells are: "lower" (row variable later
in the published order than the column variable), "upper" (row variable earlier),
or "full" (both, checked equal). The other triangle must be empty or a dash.
Diagonal cells (1, 1.000, a dash or blank) are written as 1. Values are written in
shortest round-trip form of the published decimal (for example "0.40" -> "0.4"),
i.e. unchanged. Mean, SD and reliability cells are read from the cell a config
names, with a regular expression when the cell holds more than the number
("3.38 (1.00)", "0.954/0.943", "α = 0.97"); they become mean/sd/rel rows, values
as printed. Variable names are the source's labels without their running numbers;
where the source numbers or codes its items they are written as those codes
(item1, Q1, 1a, ...), never with item wording.

`n` is the matrix N, written on every row. A pairwise-deletion matrix whose source
prints only a sample N (and per-variable n, not per-cell n) gets the sample N, an
upper bound on each cell's n (noted in matrices.csv).

Usage: python3 data/covariance/pmc_article_tables_u.py <out dir>
(set IRW_PMC_XML_DIR=<dir of PMCxxxx.xml> to read saved copies instead of Europe PMC)
"""
import csv
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

NUM = r"(-?\d*\.?\d+)"
MSD_M = r"^(\S+) \("        # "3.38 (1.00)" -> 3.38
MSD_S = r"\((\S+)\)$"       # "3.38 (1.00)" -> 1.00
PM_M = r"^(\S+) ±"          # "9.6 ± 4.0" -> 9.6
PM_S = r"± (\S+)$"          # "9.6 ± 4.0" -> 4.0


def col_moments(stat, names, label, rows, col, rx=None, skip=()):
    """One moment per variable, read from rows[i] of column col of table label."""
    return [dict(stat=stat, var=v, label=label, row=r, col=col, rx=rx)
            for v, r in zip(names, rows) if v not in skip and r is not None]


def row_moments(stat, names, label, row, cols, rx=None):
    """One moment per variable, read from row `row`, cells cols[i] (transposed tables)."""
    return [dict(stat=stat, var=v, label=label, row=row, col=c, rx=rx)
            for v, c in zip(names, cols)]


# --- configs -----------------------------------------------------------------
MA_NAMES = ["Appearance anxiety (T1)", "FNE (T1)", "Beauty-filter use (T1)",
            "Appearance information-seeking (T1)", "Appearance feedback-seeking (T1)",
            "Media literacy (T1)", "Appearance anxiety (T2)", "Beauty-filter use (T2)",
            "Appearance information-seeking (T2)", "Appearance feedback-seeking (T2)"]
# Table 5 alpha column "T1/T2": row of each variable's scale and which half
MA_REL = [("Appearance anxiety (T1)", 1, r"^([^/]+)/"), ("FNE (T1)", 2, r"^([^/]+)/"),
          ("Beauty-filter use (T1)", 3, r"^([^/]+)/"),
          ("Appearance information-seeking (T1)", 4, r"^([^/]+)/"),
          ("Appearance feedback-seeking (T1)", 5, r"^([^/]+)/"),
          ("Media literacy (T1)", 6, r"^([^/]+)/"),
          ("Appearance anxiety (T2)", 1, r"/([^/]+)$"), ("Beauty-filter use (T2)", 3, r"/([^/]+)$"),
          ("Appearance information-seeking (T2)", 4, r"/([^/]+)$"),
          ("Appearance feedback-seeking (T2)", 5, r"/([^/]+)$")]

QUP_NAMES = [f"item{i}" for i in range(1, 10)]

RYD_NAMES = ["CD-RISC-10", "Age", "Teaching experience", "Extraversion", "Agreeableness",
             "Conscientiousness", "Emotional stability", "Openness"]

ALG_NAMES = ["PHQ-4 total", "GAD-2 anxiety", "PHQ-2 depression", "MSPSS total",
             "MSPSS significant other", "MSPSS family", "MSPSS friends", "SSOSH total",
             "SSOSH positively worded", "SSOSH reverse worded", "BACE-30 total"]

IOI_NAMES = ["Use", "Ben", "RAL", "Sat", "RPR", "Ioth", "QoL"]

MIN_NAMES = ["MAAS Total Score", "MAIA Noticing", "MAIA Not Distracting", "MAIA Not Worrying",
             "MAIA Attention Regulation", "MAIA Emotional Awareness", "MAIA Self-Regulation",
             "MAIA Body Listening", "MAIA Trusting", "MAIA Total Score"]

ISI_NAMES = [f"item{i}" for i in range(1, 8)]

BED_NAMES = ["1a", "1b", "2a", "2b", "2c", "2d", "2e"]

BBQ_NAMES = ["Leisure", "View on life", "Creativity", "Learning", "Friends and friendship",
             "View of self"]

MAT_NAMES = ["Q1", "Q3", "Q4", "Q5", "Q6", "Q8", "Q9", "Q10", "Q11"]

CONFIGS = [
    dict(pmcid="PMC13582449", label="Table 2", table="ma_2026_appearanceanxiety10", n=339,
         layout="lower", names=MA_NAMES, label_col=0, rows=list(range(1, 11)),
         cols=list(range(2, 12)),
         moments=col_moments("mean", MA_NAMES, "Table 2", list(range(1, 11)), 1, MSD_M)
         + col_moments("sd", MA_NAMES, "Table 2", list(range(1, 11)), 1, MSD_S)
         + [dict(stat="rel", var=v, label="Table 5", row=r, col=2, rx=rx) for v, r, rx in MA_REL]),
    dict(pmcid="PMC13183525", label="Table 2", table="banoschaparro_2026_quptw9", n=507,
         layout="lower", names=QUP_NAMES, rows=list(range(1, 10)), cols=list(range(6, 15)),
         moments=col_moments("mean", QUP_NAMES, "Table 2", list(range(1, 10)), 1)
         + col_moments("sd", QUP_NAMES, "Table 2", list(range(1, 10)), 2)),
    dict(pmcid="PMC13603468", label="Table 3", table="ryder_2026_resilience8", n=234,
         layout="lower", names=RYD_NAMES, label_col=0, rows=list(range(1, 9)),
         cols=list(range(1, 9)),
         moments=[dict(stat="mean", var="Age", label="Table 1", row=1, col=1, rx=MSD_M),
                  dict(stat="mean", var="Teaching experience", label="Table 1", row=2, col=1, rx=MSD_M),
                  dict(stat="sd", var="Age", label="Table 1", row=1, col=1, rx=MSD_S),
                  dict(stat="sd", var="Teaching experience", label="Table 1", row=2, col=1, rx=MSD_S)]
         + col_moments("mean", [RYD_NAMES[0]] + RYD_NAMES[3:], "Table 2", range(1, 7), 1)
         + col_moments("sd", [RYD_NAMES[0]] + RYD_NAMES[3:], "Table 2", range(1, 7), 2)
         + col_moments("rel", [RYD_NAMES[0]] + RYD_NAMES[3:], "Table 2", range(1, 7), 5,
                       rx=r"^(?:α|SB) = (\S+)$")),
    dict(pmcid="PMC13605599", label="Table 3", table="alghadban_2026_selfstigma11", n=507,
         layout="lower", names=ALG_NAMES, rows=list(range(1, 12)), cols=list(range(1, 12)),
         moments=col_moments("mean", ALG_NAMES, "Table 2", list(range(1, 12)), 2, MSD_M)
         + col_moments("sd", ALG_NAMES, "Table 2", list(range(1, 12)), 2, MSD_S)
         + col_moments("rel", ALG_NAMES, "Table 2", list(range(1, 12)), 4,
                       skip=("GAD-2 anxiety", "PHQ-2 depression"))),
    dict(pmcid="PMC12921933", label="Table 2", table="dallari_2026_ioiha7", n=98,
         layout="upper", names=IOI_NAMES, label_col=1, rows=list(range(2, 9)),
         cols=list(range(2, 9))),
    dict(pmcid="PMC13064690", label="Table 6.", table="miniati_2025_maasmaia10", n=141,
         layout="upper", names=MIN_NAMES, rows=list(range(1, 10)) + [None],
         cols=[None] + list(range(1, 10)),
         moments=col_moments("mean", MIN_NAMES, "Table 2.", [12] + list(range(3, 12)), 1, PM_M)
         + col_moments("sd", MIN_NAMES, "Table 2.", [12] + list(range(3, 12)), 1, PM_S)
         + [dict(stat="rel", var="MAAS Total Score", text=r"MAAS showed good internal consistency in our study \(Cronbach’s α = (\d?\.\d+)\)"),
            dict(stat="rel", var="MAIA Total Score", text=r"MAIA allows researchers.{0,400}? In our study, the scale showed a very good internal consistency \(Cronbach’s α = (\d?\.\d+)\)")]),
    dict(pmcid="PMC12713979", label="Table 1", table="pretorius_2025_isi7", n=429,
         layout="lower", names=ISI_NAMES, rows=list(range(2, 9)), cols=list(range(1, 8)),
         moments=row_moments("mean", ISI_NAMES, "Table 1", 10, list(range(1, 8)))
         + row_moments("sd", ISI_NAMES, "Table 1", 11, list(range(1, 8)))),
    dict(pmcid="PMC13495186", label="Table 2", table="linnet_2026_bedq7", n=364,
         layout="lower", names=BED_NAMES, rows=list(range(1, 8)), cols=list(range(1, 8))),
    dict(pmcid="PMC11114274", label="Table 3", table="hamatani_2024_bbqj6", n=637,
         layout="upper", names=BBQ_NAMES, label_col=0, rows=list(range(1, 7)),
         cols=list(range(1, 7))),
    dict(pmcid="PMC13113691", label="Table 3", table="mattingsdal_2026_decisionclaims9", n=225,
         layout="lower", names=MAT_NAMES, label_col=0, rows=list(range(1, 10)),
         cols=list(range(1, 10))),
]

DIAG = {"1", "-", "–", "—", "", "1.00", "1.0", "1.000"}
EMPTY = {"", "-", "–", "—", "--"}


def txt(e):
    return re.sub(r"\s+", " ", "".join(e.itertext())).strip()


def get(pmcid):
    local = os.environ.get("IRW_PMC_XML_DIR")
    if local:
        return (Path(local) / f"{pmcid}.xml").read_bytes()
    url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML"
    req = urllib.request.Request(url, headers={"User-Agent": "irw-cov-build"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def num(cell, where):
    s = cell.replace("−", "-").replace("–", "-").replace(" ", "")
    s = re.sub(r"[*†]+$", "", s)
    if not re.fullmatch(r"-?(\d+)?\.\d+|-?\d+", s):
        raise SystemExit(f"{where}: cannot read {cell!r}")
    return repr(float(s))


def varname(lab):
    return re.sub(r"^(\(\d+\)|\[\d+\]|\d+\.)\s*", "", lab).strip()


def check_licence(pmcid, root):
    lic = root.find(".//license")
    href = (lic.get("{http://www.w3.org/1999/xlink}href") or "") if lic is not None else ""
    links = " ".join(e.get("{http://www.w3.org/1999/xlink}href") or "" for e in lic.iter()) if lic is not None else ""
    ltxt = txt(lic) if lic is not None else ""
    if re.search(r"NonCommercial|NoDeriv|by-nc|by-nd|by-sa|ShareAlike", href + links + ltxt):
        raise SystemExit(f"{pmcid}: restricted licence {href} {ltxt[:120]}")
    if not (re.search(r"creativecommons\.org/(licenses/by/|publicdomain/zero)", href + links + ltxt)
            or re.search(r"Creative Commons Attribution( \(CC BY\))? (L|l)icen[cs]e", ltxt)):
        raise SystemExit(f"{pmcid}: licence not CC BY / CC0: {href} {ltxt[:120]}")


def table_rows(root, label):
    tws = [t for t in root.iter("table-wrap")
           if t.find("label") is not None and txt(t.find("label")) == label]
    if len(tws) != 1:
        raise SystemExit(f"{label}: found {len(tws)} tables")
    return [[txt(c) for c in tr if c.tag in ("td", "th")] for tr in tws[0].iter("tr")]


def build(cfg, root):
    where = f"{cfg['pmcid']} {cfg['label']}"
    rows = table_rows(root, cfg["label"])
    names, ridx, cidx = cfg["names"], cfg["rows"], cfg["cols"]
    k = len(names)
    if len(ridx) != k or len(cidx) != k or len(set(names)) != k:
        raise SystemExit(f"{where}: bad config")
    if "label_col" in cfg:  # printed row labels must match the names used
        for nm, r in zip(names, ridx):
            if r is not None:
                lab = varname(rows[r][cfg["label_col"]])
                if lab.replace(" ", "").lower() != nm.replace(" ", "").lower():
                    raise SystemExit(f"{where}: row label {lab!r} is not {nm!r}")

    def cell(a, b):  # cell in the row of variable a, column of variable b
        r, c = ridx[a], cidx[b]
        if r is None or c is None or c >= len(rows[r]):
            return None
        return rows[r][c]

    out, check = [], []
    for i in range(k):
        d = cell(i, i)
        if d is not None and d.strip() not in DIAG:
            raise SystemExit(f"{where}: diagonal {i} is {d!r}")
        for j in range(i):
            if cfg["layout"] == "lower":
                raw, other = cell(i, j), cell(j, i)
            else:
                raw, other = cell(j, i), cell(i, j)
            if raw is None or raw in EMPTY:
                raise SystemExit(f"{where}: missing cell ({names[i]}, {names[j]})")
            v = num(raw, f"{where} ({names[i]},{names[j]})")
            if cfg["layout"] == "full":
                if num(other, where) != v:
                    raise SystemExit(f"{where}: asymmetric ({i},{j})")
            elif other not in EMPTY and other is not None:
                raise SystemExit(f"{where}: other triangle not empty at ({i},{j}): {other!r}")
            if abs(float(v)) >= 1:
                raise SystemExit(f"{where}: |r| >= 1 at ({i},{j})")
            out.append({"stat": "cor", "var1": names[i], "var2": names[j], "value": v,
                        "n": cfg["n"]})
            check.append((names[i], names[j], raw))
        out.append({"stat": "cor", "var1": names[i], "var2": names[i], "value": "1",
                    "n": cfg["n"]})
    body = None
    seen = set()
    for m in cfg.get("moments", []):
        if m["var"] not in names or (m["stat"], m["var"]) in seen:
            raise SystemExit(f"{where}: bad moment {m}")
        seen.add((m["stat"], m["var"]))
        if "text" in m:
            if body is None:
                body = txt(root.find(".//body"))
            hits = set(re.findall(m["text"], body))
            if len(hits) != 1:
                raise SystemExit(f"{where}: {m['stat']} for {m['var']!r} matched {hits}")
            raw = hits.pop()
        else:
            c = table_rows(root, m["label"])[m["row"]][m["col"]]
            if m.get("rx"):
                hit = re.search(m["rx"], c)
                if not hit:
                    raise SystemExit(f"{where}: {m['stat']} cell {c!r} for {m['var']!r}")
                raw = hit.group(1)
            else:
                raw = c
        v = num(raw, f"{where} {m['stat']} {m['var']}")
        if m["stat"] == "rel" and not 0 < float(v) <= 1:
            raise SystemExit(f"{where}: reliability {v} for {m['var']}")
        if m["stat"] == "sd" and float(v) <= 0:
            raise SystemExit(f"{where}: sd {v} for {m['var']}")
        out.append({"stat": m["stat"], "var1": m["var"], "var2": "", "value": v, "n": cfg["n"]})
        check.append((m["stat"] + ":" + m["var"], "", raw))
    return out, check


def main(outdir):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    cache = {}
    for cfg in CONFIGS:
        if cfg["pmcid"] not in cache:
            cache[cfg["pmcid"]] = ET.fromstring(get(cfg["pmcid"]))
            check_licence(cfg["pmcid"], cache[cfg["pmcid"]])
        rows, check = build(cfg, cache[cfg["pmcid"]])
        with open(outdir / f"{cfg['table']}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["stat", "var1", "var2", "value", "n"])
            w.writeheader()
            w.writerows(rows)
        with open(outdir / f"{cfg['table']}.check.tsv", "w", encoding="utf-8") as f:
            for a, b, raw in check:
                f.write(f"{a}\t{b}\t{raw}\n")
        print(f"{cfg['table']}: {len(cfg['names'])} variables, {len(rows)} rows")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 pmc_article_tables_u.py <out dir>")
    main(sys.argv[1])
