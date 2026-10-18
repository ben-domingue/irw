"""GenAI use among Indonesian students: ethics, literacy, effectiveness, guidance.

Source: https://zenodo.org/records/17987225
DOI: 10.5281/zenodo.17987225
Data: GenAI Questioner (Responses).csv (319 respondents x 34 columns)
License: CC BY 4.0 (Zenodo record, licence id cc-by-4.0)
Item text: not shipped -- the deposit is a bare Google Forms response export
  whose headers are positional codes (Ethics1 .. Guidance11) with no stem
  anywhere, and no codebook or questionnaire file accompanies it. The wording
  would have to come from the paper, which the record does not link.

Four study-authored blocks by Nelvirita et al., every column a 1-5 Likert and
every one of the 34 columns an item -- the export carries no demographics at
all, so there are no covariates:

  ethics        8 items
  literacy      7 items  (the source spells the prefix "Literation")
  effectiveness 8 items  (source prefix "Effectivity")
  guidance     11 items
"""
import os

import pandas as pd

RAW = os.environ.get(
    "NELVIRITA_RAW",
    "/tmp/claude-1000/-home-ben-Dropbox-projects-irw-src-automated-finding/"
    "5eef9b18-8b21-4d62-a15f-a632f0def6f5/scratchpad/bC/raw/zenodo.17987225/"
    "GenAI Questioner (Responses).csv")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "..", "automated_finding", "irw_output")

SCALES = {
    "ethics":        [f"Ethics{i}" for i in range(1, 9)],
    "literacy":      [f"Literation{i}" for i in range(1, 8)],
    "effectiveness": [f"Effectivity{i}" for i in range(1, 9)],
    "guidance":      [f"Guidance{i}" for i in range(1, 12)],
}
SCALE = {1, 2, 3, 4, 5}


def main():
    d = pd.read_csv(RAW)
    print(f"read {d.shape[0]} rows x {d.shape[1]} cols")
    used = set()
    for cols in SCALES.values():
        used |= set(cols)
    unaccounted = [c for c in d.columns if c not in used]
    for c in unaccounted:
        print(f"  UNACCOUNTED {c!r}")
    assert not unaccounted, f"{len(unaccounted)} column(s) unaccounted for"

    d = d.reset_index(drop=True)
    d["id"] = d.index + 1
    os.makedirs(OUT, exist_ok=True)
    written = set()
    for name, cols in SCALES.items():
        assert all(c in d.columns for c in cols), name
        long = d.melt(id_vars=["id"], value_vars=cols,
                      var_name="item", value_name="resp").dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        for it, g in long.groupby("item"):
            bad = set(g["resp"].unique()) - SCALE
            assert not bad, f"{name}/{it}: {sorted(bad)}"
        assert long["id"].nunique() >= 100 and long["item"].nunique() > 1
        table = f"nelvirita_2025_{name}"
        assert table not in written
        written.add(table)
        long[["id", "item", "resp"]].to_csv(
            os.path.join(OUT, f"{table}.csv"), index=False)
        print(f"  {table}: {long['id'].nunique()} ids x "
              f"{long['item'].nunique()} items = {len(long)} responses")


if __name__ == "__main__":
    main()
