"""Python port of the five CIS .do files fixed in irw#2843.

    python3 spain_cis_likert_blocks.py DO_FILE NUM_CSV OUT_DIR [TABLE ...]

No Stata on the build machine. The five scripts (spain_2024_values,
spain_2024_ideology, spain_2025_tourism, spain_2026_love,
spain_2026_prostitution) share one shape, which this reads from the .do
itself rather than restating: a master step (id = row number, SEXO ->
cov_sex labelled Hombre/Mujer, EDAD -> cov_age with an optional
`replace cov_age = . if cov_age == K`), then one block per table, from
`local survey_cols ...` to `export delimited using "<table>.csv"`, whose
`replace V = . if inlist(V, ...)` sentinel lines and optional
`replace resp = . if resp == 3` line are applied before going long.

Checked: run on origin/main's scripts (which drop code 3), every one of the
15 affected tables reproduces its live table exactly (rows, ids, items and
every response). Run on the fixed scripts, each table differs from live only
by the added code-3 rows.

Source: CIS microdata MD<study>.zip (<study>_num.csv), https://www.cis.es/
"""
import os
import re
import sys

import pandas as pd


def read_num(path):
    raw = pd.read_csv(path, sep=";", dtype=str, encoding="utf-8-sig")
    # 3508 headers are "NAME: label"; the others are plain names
    raw.columns = [c.split(":")[0].strip().strip('"').lower() for c in raw.columns]
    return raw.apply(pd.to_numeric, errors="coerce")   # Stata: destring, force


def parse(do_text):
    age = re.search(r"replace cov_age = \. if cov_age == (\d+)", do_text)
    blocks = []
    for m in re.finditer(r"local survey_cols ([^\n]+)\n(.*?)export delimited using \"([^\"]+)\.csv\"",
                         do_text, re.S):
        cols, body, table = m[1].split(), m[2], m[3]
        sent = {v: [int(x) for x in codes.split(",")]
                for v, codes in re.findall(r"replace (\w+) = \. if inlist\(\1, ([\d, ]+)\)", body)}
        drop3 = bool(re.search(r"^\s*replace resp = \. if resp == 3\s*$", body, re.M))
        blocks.append((table, cols, sent, drop3))
    return (int(age[1]) if age else None), blocks


def build(do_path, num_path, out_dir, only=()):
    age_sentinel, blocks = parse(open(do_path, encoding="utf-8").read())
    d = read_num(num_path)
    d["id"] = range(1, len(d) + 1)
    d["cov_sex"] = d["sexo"].map({1: "Hombre", 2: "Mujer"})
    d["cov_age"] = d["edad"].where(d["edad"] != age_sentinel) if age_sentinel else d["edad"]
    os.makedirs(out_dir, exist_ok=True)
    for table, cols, sent, drop3 in blocks:
        if only and table not in only:
            continue
        w = d[["id", "cov_sex", "cov_age"] + cols].copy()
        for v, codes in sent.items():
            w.loc[w[v].isin(codes), v] = pd.NA
        long = w.melt(id_vars=["id", "cov_sex", "cov_age"], value_vars=cols,
                      var_name="item", value_name="resp")
        if drop3:
            long = long[long.resp != 3]
        long = long.dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        long["cov_age"] = long["cov_age"].astype("Int64")
        long = long.sort_values(["id", "item"])[["id", "item", "resp", "cov_sex", "cov_age"]]
        long.to_csv(os.path.join(out_dir, table + ".csv"), index=False)
        print(f"{table}: rows={len(long)} ids={long.id.nunique()} items={long.item.nunique()} "
              f"resp={long.resp.value_counts().sort_index().to_dict()} drop3={drop3}")


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2], sys.argv[3], tuple(sys.argv[4:]))
