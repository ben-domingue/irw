"""Chatbot use, perceived enjoyment and repurchase intention.

Source: https://zenodo.org/records/17585865
DOI: 10.5281/zenodo.17585865
Data: PENGARUH PENGGUNAAN CHATBOTS TERHADAP REPURCHASE INTENTION.xlsx (269 respondents x 21 columns)
License: CC BY 4.0 (Zenodo record, licence id cc-by-4.0)
Item text: not shipped -- the workbook is a bare response export whose headers are positional codes (QS1 .. RI4) with no stem, and the deposit ships no codebook or questionnaire.

Six constructs, all 1-5, one table each. RIGHTS: these are named third-party marketing/TAM constructs (service quality, information quality, perceived enjoyment, perceived ease of use, customer satisfaction, repurchase intention) that no register row matches; the response tables carry positional codes and ship no item text, so no wording is exposed -- BATCH_LOG 2026-10-18i's ProQOL reasoning.
"""
import glob
import os

import pandas as pd

RAWDIR = os.environ.get(
    "RUMANGKIT_CHATBOT_RAWDIR",
    "/tmp/claude-1000/-home-ben-Dropbox-projects-irw-src-automated-finding/5eef9b18-8b21-4d62-a15f-a632f0def6f5/scratchpad/bC/raw/zenodo.17585865")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "..", "automated_finding", "irw_output")

SCALES = {'qs': ['QS1', 'QS2', 'QS3'], 'qi': ['QI1', 'QI2', 'QI3', 'QI4'], 'pe': ['PE1', 'PE2', 'PE3', 'PE4'], 'peou': ['PEOU1', 'PEOU2', 'PEOU3'], 'cs': ['CS1', 'CS2', 'CS3'], 'ri': ['RI1', 'RI2', 'RI3', 'RI4']}
SCALE = {1, 2, 3, 4, 5}
COVS = {}


def read():
    p = glob.glob(os.path.join(RAWDIR, "*.xlsx"))
    assert p, "raw file not found in " + RAWDIR
    path = sorted(p)[0]
    if path.lower().endswith((".xlsx", ".xls")):
        d = pd.read_excel(path)
    else:
        d = pd.read_csv(path)
    d.columns = [str(c).strip() for c in d.columns]
    return d, os.path.basename(path)


def main():
    d, fname = read()
    print(f"read {fname}: {d.shape[0]} rows x {d.shape[1]} cols")
    used = set(COVS)
    for cols in SCALES.values():
        used |= set(cols)
    for c in d.columns:
        if c not in used:
            print(f"  skip {c!r}: not an item of a shipped scale")
            used.add(c)
    assert not [c for c in d.columns if c not in used]

    d = d.reset_index(drop=True)
    d["id"] = d.index + 1
    os.makedirs(OUT, exist_ok=True)
    written = set()
    for name, cols in SCALES.items():
        missing = [c for c in cols if c not in d.columns]
        assert not missing, f"{name}: missing {missing}"
        long = d.melt(id_vars=["id"] + list(COVS), value_vars=cols,
                      var_name="item", value_name="resp").dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        # Per item, not pooled: an out-of-range value isolated to one item is a
        # data-entry fault even when the merged range looks fine.
        for it, g in long.groupby("item"):
            bad = set(g["resp"].unique()) - SCALE
            assert not bad, f"{name}/{it}: {sorted(bad)} outside {sorted(SCALE)}"
        assert long["id"].nunique() >= 100, (name, long["id"].nunique())
        assert long["item"].nunique() > 1, name
        long = long.rename(columns=COVS)
        table = "rumangkit_2025_chatbot_" + name
        assert table not in written, table
        written.add(table)
        cols_out = ["id", "item", "resp"] + [COVS[c] for c in COVS]
        long[cols_out].to_csv(os.path.join(OUT, table + ".csv"), index=False)
        print(f"  {table}: {long['id'].nunique()} ids x "
              f"{long['item'].nunique()} items = {len(long)} responses")


if __name__ == "__main__":
    main()
