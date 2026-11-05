"""Add the code-3 option row to the item text of six spain_* tables rebuilt in irw#2864.

    python3 spain_cis_code3_itemtext_2864.py LIVE_ITEMS_DIR CIS_RAW_DIR OUT_DIR

As spain_cis_code3_itemtext_2843.py did for #2843: the rebuilt tables keep code 3, the
volunteered middle answer (NO LEER), and their live item text listed only options 1, 2, 4, 5.
For each <table>__items.csv this adds, per item, one row copied from the item's resp-1 row with
resp = 3, option_text = the CIS value label for code 3 (verbatim from the study's SPSS syntax
file CIS_RAW_DIR/ES<study>, whitespace trimmed, as the live option rows are), and
option_text_translated from ENGLISH below. The row goes right after the item's resp-2 row.
Nothing else changes. spain_2016_pain_personality has no item text, so it is not here.
"""
import glob
import os
import re
import sys

import pandas as pd

STUDY = {"spain_2012_reality": "ES2973", "spain_2014_debate": "Es3016", "spain_2016_pain": "ES3137",
         "spain_2017_politics": "ES3184", "spain_2023_identity": "ES3409", "spain_2023_science": "ES3406"}
ENGLISH = {
    "Ni sí ni no (NO LEER)": "Neither yes nor no (not read out)",
    "(No leer) Regular": "(not read out) So-so",
    "(NO LEER) Algo": "(not read out) Somewhat",
    "(NO LEER) Ni de acuerdo, ni en desacuerdo": "(not read out) Neither agree nor disagree",
    "(NO LEER) Ni poco ni bastante": "(not read out) Neither a little nor a lot",
    "(NO LEER) Regular": "(not read out) So-so",
}


def code3_labels(path):
    raw = open(path, "rb").read()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("latin-1")
    out = {}
    for var, body in re.findall(r"^\s*/(\w+)\s*\n(.*?)(?=^\s*/\w+\s*$|\Z)", text.replace("\r", ""), re.S | re.M):
        m = re.search(r"(?:^|\s)3\s+'([^']*)'", body)
        if m:
            out[var.lower()] = m[1].strip()
    return out


def main(live_dir, raw_dir, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    for f in sorted(glob.glob(os.path.join(live_dir, "*__items.csv"))):
        table = os.path.basename(f)[: -len("__items.csv")]
        study = next(v for k, v in STUDY.items() if table.startswith(k + "_"))
        labels = code3_labels(os.path.join(raw_dir, study))
        d = pd.read_csv(f, dtype=str, keep_default_na=False)
        assert "3" not in set(d.resp), table
        rows = []
        for item, g in d.groupby("item", sort=False):
            new = g[g.resp == "1"].iloc[0].copy()
            new["resp"] = "3"
            new["option_text"] = labels[item.lower()]
            new["option_text_translated"] = ENGLISH[new["option_text"]]
            for _, r in g.iterrows():
                rows.append(r)
                if r.resp == "2":
                    rows.append(new)
        out = pd.DataFrame(rows)[d.columns]
        assert len(out) == len(d) + d.item.nunique(), table
        out.to_csv(os.path.join(out_dir, table + "__items.csv"), index=False)
        print(f"{table}: {len(d)} -> {len(out)} rows; code 3 = {sorted(set(out[out.resp == '3'].option_text))}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
