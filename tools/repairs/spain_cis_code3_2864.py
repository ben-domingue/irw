"""irw#2864: keep CIS code 3, the volunteered (NO LEER) middle answer, in seven spain_* tables.

    python3 spain_cis_code3_2864.py SOURCE_DIR OUT_DIR [--as-live]

Follow-on to #2843 (PR #2862), which ruled that code 3 on a 5-point CIS scale is the
volunteered middle answer and is kept. These seven blocks dropped it through
`inlist(x, 3, 8, 9)`. Each was checked against its study's SPSS value labels (ES<study>):

  spain_2012_reality_personality  P3701-P3710  3 'Ni si ni no (NO LEER)'              ES2973
  spain_2014_debate_leaders       P13_1-P13_17 3 '(No leer) Regular'                  Es3016
  spain_2016_pain_difficulty      P16, P17     3 '(NO LEER) Algo'                     ES3137
  spain_2016_pain_personality     P27_1-P27_10 3 '(NO LEER) Ni si, ni no'             ES3137
  spain_2017_politics_attitudes   P2501-P2503  3 '(NO LEER) Ni de acuerdo, ni en desacuerdo' ES3184
  spain_2023_identity_identification P5_1-P5_9 3 '(NO LEER) Ni poco ni bastante'      ES3409
  spain_2023_science_future       P12, P13     3 '(NO LEER) Regular'                  ES3406

Not changed: spain_2013_services p27c, where 3 is 'Todavia esta tramitandose' (the complaint
is still being processed), a status rather than an answer.

No Stata on the build machine, so this reads each .do: the master step (fixed-width `infix`
positions or the _num.csv, id = row number, cov_sex labelled Hombre/Mujer, cov_age with 99
missing) and, per table, its `replace V = . if inlist(V, ...)` lines. `--as-live` keeps code
3 dropped; run that way every table reproduces its live table exactly, which is the check
that the port is faithful. Without it, each table gains only its code-3 rows.

SOURCE_DIR holds the CIS microdata (DA<study> fixed-width files, <study>_num.csv), from
https://www.cis.es/ (MD<study>.zip).
"""
import os
import re
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "..", "data")

TABLES = {
    "spain_2012_reality": ("DA2973", ["spain_2012_reality_personality"]),
    "spain_2014_debate": ("Da3016", ["spain_2014_debate_leaders"]),
    "spain_2016_pain": ("DA3137", ["spain_2016_pain_difficulty", "spain_2016_pain_personality"]),
    "spain_2017_politics": ("DA3184", ["spain_2017_politics_attitudes"]),
    "spain_2023_identity": ("3409_num.csv", ["spain_2023_identity_identification"]),
    "spain_2023_science": ("3406_num.csv", ["spain_2023_science_future"]),
}


def infix_spec(do):
    m = re.search(r"infix\s+(.*?)\s+using\s+\"", do, re.S)
    toks = m[1].replace("///", " ").split()
    spec, i = [], 0
    while i < len(toks):
        t = toks[i]
        if re.fullmatch(r"str\d+", t):
            i += 1
            t = toks[i]
        a, _, b = toks[i + 1].partition("-")
        spec.append((t.lower(), int(a) - 1, int(b or a)))
        i += 2
    return spec


def read_source(do, path):
    if path.endswith(".csv"):
        d = pd.read_csv(path, sep=";", dtype=str, encoding="utf-8-sig")
        d.columns = [c.split(":")[0].strip().strip('"').lower() for c in d.columns]
    else:
        spec = infix_spec(do)
        d = pd.read_fwf(path, colspecs=[(a, b) for _, a, b in spec],
                        names=[n for n, _, _ in spec], dtype=str, header=None)
    return d.apply(pd.to_numeric, errors="coerce")       # Stata: destring, force


def master(do, d):
    sex = re.search(r"rename (\w+) cov_sex", do, re.I)[1].lower()
    age = re.search(r"rename (\w+) cov_age", do, re.I)[1].lower()
    out = pd.DataFrame({"id": range(1, len(d) + 1)})
    out["cov_sex"] = d[sex].map({1: "Hombre", 2: "Mujer"}).astype(object)
    out.loc[out.cov_sex.isna() & d[sex].notna(), "cov_sex"] = d[sex].astype("Int64").astype(str)
    out["cov_age"] = d[age].where(d[age] != 99).astype("Int64")
    return out


def block(do, table):
    m = re.search(r"((?:(?!export delimited).)*?)export delimited using \"" + re.escape(table) + r"\.csv\"",
                  do, re.S)
    body = m[1][m[1].rfind("**#"):] if "**#" in m[1] else m[1]
    return [(v.lower(), [int(x) for x in codes.split(",")])
            for v, codes in re.findall(r"replace (\w+) = \. if inlist\(\1, ([\d, ]+)\)", body)]


def build(script, src_dir, out_dir, as_live):
    src, tables = TABLES[script]
    do = open(os.path.join(DATA, script + ".do"), encoding="utf-8", errors="replace").read()
    d = read_source(do, os.path.join(src_dir, src))
    base = master(do, d)
    for table in tables:
        sent = block(do, table)
        w = base.copy()
        for v, codes in sent:
            drop = [c for c in codes if as_live or c != 3]
            w[v] = d[v].where(~d[v].isin(drop))
        long = w.melt(id_vars=["id", "cov_sex", "cov_age"], value_vars=[v for v, _ in sent],
                      var_name="item", value_name="resp").dropna(subset=["resp"])
        long["resp"] = long.resp.astype(int)
        long = long.sort_values(["id", "item"])[["id", "item", "resp", "cov_sex", "cov_age"]]
        long.to_csv(os.path.join(out_dir, table + ".csv"), index=False, na_rep="")
        print(f"{table}: rows={len(long)} ids={long.id.nunique()} items={long.item.nunique()} "
              f"resp={long.resp.value_counts().sort_index().to_dict()}")


if __name__ == "__main__":
    src_dir, out_dir = sys.argv[1], sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)
    for s in TABLES:
        build(s, src_dir, out_dir, "--as-live" in sys.argv)
