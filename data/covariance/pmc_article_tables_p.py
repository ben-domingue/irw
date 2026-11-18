"""Covariance family (irw_cov, source = "cov"): correlation tables printed in
CC BY open-access articles, read from the article's JATS XML in PubMed Central
(source "article tables", #3582; agent P batch, 2026-11-18).

Source: Europe PMC full-text XML,
https://www.ebi.ac.uk/europepmc/webservices/rest/<PMCID>/fullTextXML.
Each article's <license> is read and must be CC BY (creativecommons.org/licenses/by/
or the words "Creative Commons Attribution (CC BY)" / "Creative Commons Attribution
License") or CC0; the script stops otherwise. Every DOI was checked on Crossref
(2026-11-18).

Tables built (CONFIGS below): ten correlation tables from ten articles, chosen
from the Europe PMC caption scan of 2026-11-17 (scratchpad scripts_n/cands.tsv).
Five are item-level matrices (inter-item Pearson, Spearman, polychoric or
tetrachoric); the others are among scale or subscale scores. The N of each is
from the caption or the article text, as noted in matrices.csv.

Parsing: cells are read as text. Significance stars are stripped; nothing else is
changed. Unicode minus (U+2212), an en dash used as a minus, and a space after a
minus sign ("- 0.015") are read as "-". Diagonal cells (1, 1.00, a dash, or blank)
are written as 1; a matrix printed without its diagonal cells (no row for the
first variable or no column for the last) gets diagonal 1 rows. For tables printed
as a full square, the script checks the upper triangle equals the lower and writes
the lower; for lower-triangle tables it checks the upper triangle is empty. Values
are written in shortest round-trip form of the published decimal (for example
"0.40" -> "0.4"), i.e. unchanged. Mean and SD columns, where used, become mean/sd
rows. Variable names are the source's labels; where the source numbers its items
("1", "2", ...) they are written "item1", "item2", ... and the item wording is in
matrices.csv `variables`.

Modification (2026-11-18): reshaped to the long lower-triangle layout in
data/covariance/README.md; stars stripped; values unchanged.

Usage: python3 data/covariance/pmc_article_tables_p.py <out dir>
(set IRW_PMC_XML_DIR=<dir of PMCxxxx.xml> to read saved copies instead of Europe PMC)
"""
import csv
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

# Each config: pmcid, label, table, n, layout ("full" or "lower"), col0 (index of the
# first matrix cell in each <tr>, counting <td>/<th> elements), names (published
# order), rows (the <tr> index holding each variable's row, or None if the table
# prints no row for it), optional mean/sd column indices, optional group
# (several configs with one table name = one table with a group column);
# optional rename maps a printed header to the name used (layout only).
CONFIGS = [
    dict(pmcid="PMC12469481", label="Table 3", table="wolfson_2025_smmconditions27", n=978,
         layout="full", col0=1, header_row=0,
         rows=list(range(1, 28)), rename={"HIV/ AIDS": "HIV/AIDS"}),
    dict(pmcid="PMC13658844", label="TABLE 3", table="tilahun_2026_trustoncologist18", n=197,
         layout="lower", col0=1,
         names=[f"item{i}" for i in range(1, 19)], rows=list(range(1, 19))),
    dict(pmcid="PMC10220345", label="Table 3", table="crescenzi_2023_deprivation11", n=2499,
         layout="full", col0=1, label_col=0,
         rows=list(range(1, 12))),
    dict(pmcid="PMC12329912", label="Table 3", table="garney_2025_totalteen22", n=481,
         layout="lower", col0=1,
         names=[f"item{i}" for i in range(1, 23)], rows=list(range(1, 23))),
    dict(pmcid="PMC13730822", label="Table 2", table="chen_2026_attachmentprosocial12", n=536,
         layout="lower", col0=1, label_col=0,
         rows=list(range(1, 13))),
    dict(pmcid="PMC12226599", label="Table 6", table="brouwer_2025_mslq15", n=509,
         layout="lower", col0=1, label_col=0,
         rows=list(range(1, 16))),
    dict(pmcid="PMC12986267", label="Table 2", table="wieteskamilek_2026_emphasis10", n=120,
         layout="lower", col0=3, mean=1, sd=2,
         names=[f"Emph-{i}" for i in range(1, 11)], rows=list(range(1, 11))),
    dict(pmcid="PMC13627343", label="Table 11", table="kilic_2026_teacherclimate12", n=424,
         layout="lower", col0=1, label_col=0,
         rows=list(range(1, 13))),
    dict(pmcid="PMC13534396", label="Table 4", table="brod_2026_acemimpact25", n=199,
         layout="lower", col0=1, label_col=0,
         rows=list(range(2, 27))),
    dict(pmcid="PMC13399294", label="Table 6", table="rosalin_2026_osce15", n=96,
         layout="lower", col0=1, group="summative",
         names=[f"Q{i}" for i in range(1, 16)], rows=[None] + list(range(2, 16))),
    dict(pmcid="PMC13399294", label="Table 6", table="rosalin_2026_osce15", n=96,
         layout="lower", col0=1, group="formative",
         names=[f"Q{i}" for i in range(1, 16)], rows=[None] + list(range(17, 31))),
]

DIAG = {"1", "-", "–", "—", "", "1.00", "1.0", "1.000"}


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
    s = re.sub(r"\*+$", "", s)
    if not re.fullmatch(r"-?(\d+)?\.\d+|-?\d+", s):
        raise SystemExit(f"{where}: cannot read {cell!r}")
    return repr(float(s))


def varname(lab):
    return re.sub(r"^(\[\d+\]|\d+\.)\s+", "", lab).strip()


def check_licence(pmcid, root):
    lic = root.find(".//license")
    href = (lic.get("{http://www.w3.org/1999/xlink}href") or "") if lic is not None else ""
    ltxt = txt(lic) if lic is not None else ""
    if re.search(r"NonCommercial|NoDeriv|by-nc|by-nd|by-sa|ShareAlike", href + ltxt):
        raise SystemExit(f"{pmcid}: restricted licence {href} {ltxt[:120]}")
    if not (re.search(r"creativecommons\.org/(licenses/by/|publicdomain/zero)", href + ltxt)
            or re.search(r"Creative Commons Attribution( \(CC BY\))? (L|l)icen[cs]e", ltxt)
            or re.search(r"Creative Commons Attribution \(CC BY\) license", ltxt)):
        raise SystemExit(f"{pmcid}: licence not CC BY / CC0: {href} {ltxt[:120]}")


def build(cfg, root):
    where = f"{cfg['pmcid']} {cfg['label']}"
    tw = next(t for t in root.iter("table-wrap")
              if t.find("label") is not None and txt(t.find("label")) == cfg["label"])
    rows = [[txt(c) for c in tr if c.tag in ("td", "th")] for tr in tw.iter("tr")]
    ridx = cfg["rows"]
    k = len(ridx)
    if "names" in cfg:
        names = cfg["names"]
    elif "header_row" in cfg:
        names = rows[cfg["header_row"]][cfg["col0"]:cfg["col0"] + k]
    else:
        names = [varname(rows[r][cfg["label_col"]]) for r in ridx]
    names = [cfg.get("rename", {}).get(x, x) for x in names]
    if len(names) != k or len(set(names)) != k:
        raise SystemExit(f"{where}: bad names {names}")

    def cell(i, j):
        r = ridx[i]
        if r is None:
            return None
        row = rows[r]
        c = cfg["col0"] + j
        return row[c] if c < len(row) else None

    out, check = [], []
    for i in range(k):
        d = cell(i, i)
        if d is not None and d.strip() not in DIAG:
            raise SystemExit(f"{where}: diagonal {i} is {d!r}")
        for j in range(i + 1, k):
            up = cell(i, j)
            if cfg["layout"] == "lower" and up not in (None, ""):
                raise SystemExit(f"{where}: upper cell ({i},{j}) {up!r}")
            if cfg["layout"] == "full":
                if num(up, where) != num(cell(j, i), where):
                    raise SystemExit(f"{where}: asymmetric ({i},{j}) {up!r} vs {cell(j, i)!r}")
        for j in range(i):
            raw = cell(i, j)
            if raw is None:
                raise SystemExit(f"{where}: missing cell ({i},{j})")
            v = num(raw, f"{where} ({i},{j})")
            if abs(float(v)) >= 1:
                raise SystemExit(f"{where}: |r| >= 1 at ({i},{j})")
            out.append({"stat": "cor", "var1": names[i], "var2": names[j], "value": v, "n": cfg["n"]})
            check.append((names[i], names[j], raw))
        out.append({"stat": "cor", "var1": names[i], "var2": names[i], "value": "1", "n": cfg["n"]})
    for stat in ("mean", "sd"):
        if cfg.get(stat) is not None:
            for i in range(k):
                out.append({"stat": stat, "var1": names[i], "var2": "",
                            "value": num(rows[ridx[i]][cfg[stat]], where), "n": cfg["n"]})
    if cfg.get("group"):
        for r in out:
            r["group"] = cfg["group"]
    return out, check, names


def main(outdir):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    tables, cache = {}, {}
    for cfg in CONFIGS:
        if cfg["pmcid"] not in cache:
            cache[cfg["pmcid"]] = ET.fromstring(get(cfg["pmcid"]))
            check_licence(cfg["pmcid"], cache[cfg["pmcid"]])
        rows, check, names = build(cfg, cache[cfg["pmcid"]])
        t = tables.setdefault(cfg["table"], {"rows": [], "check": [], "grouped": bool(cfg.get("group"))})
        t["rows"] += rows
        t["check"] += [(cfg.get("group", ""),) + c for c in check]
        print(f"{cfg['table']} {cfg.get('group', '')}: {len(names)} variables, N = {cfg['n']}")
    for name, t in tables.items():
        fields = ["stat", "var1", "var2", "value", "n"] + (["group"] if t["grouped"] else [])
        with open(outdir / f"{name}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(t["rows"])
        with open(outdir / f"{name}.check.tsv", "w", encoding="utf-8") as f:
            for g, a, b, raw in t["check"]:
                f.write(f"{g}\t{a}\t{b}\t{raw}\n")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 pmc_article_tables_p.py <out dir>")
    main(sys.argv[1])
