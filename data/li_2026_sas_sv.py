#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0349016
# DOI: 10.1371/journal.pone.0349016
# Data: figshare 10.6084/m9.figshare.32109184, "Original data.xlsx"
# License: CC BY 4.0 -- verified on the figshare record itself
#          (api.figshare.com/v2/articles/32109184 -> license "CC BY 4.0"),
#          not inherited from the PLOS article.
#
# Li & Mao (2026), "Network analysis of smartphone addiction and sleep
# disorder symptoms in Chinese college students." PLOS ONE. N=1,842.
#
# The deposit is one sheet with two blocks. Only one of them is item
# response data:
#   SA1..SA10   -- Smartphone Addiction Scale, Short Version (SAS-SV),
#                  10 items on 1-6. Shipped.
#   PSQI1..PSQI7 -- the seven PSQI *component scores*, each 0-3. NOT
#                  shipped: a PSQI component is computed from one or more
#                  of the instrument's 19 underlying questions (component
#                  2 combines sleep latency minutes with a Likert item,
#                  component 5 sums nine disturbance items), so these are
#                  composites, not responses, which datastandard.md keeps
#                  out of `resp`. The underlying 19 questions are not in
#                  the deposit. If they ever surface this becomes a
#                  second table; the component scores alone do not.
#
# Item text: not shipped. The sheet has bare column codes and no
# codebook, and the administration was in Chinese to Chinese college
# students, so the English SAS-SV of Kwon et al. (2013) would be a
# translated substitute rather than the wording respondents read.
import os
import pandas as pd
from irw_validate.compat import run_qc

RAW = os.environ.get("LI_XLSX", "Original data.xlsx")
OUTDIR = os.path.join(os.path.dirname(__file__), "..", "automated_finding", "irw_output")

ITEMS = [f"SA{n}" for n in range(1, 11)]
COMPONENTS = [f"PSQI{n}" for n in range(1, 8)]


def main():
    df = pd.read_excel(RAW)

    accounted = set(ITEMS) | set(COMPONENTS)
    unaccounted = [c for c in df.columns if c not in accounted]
    assert not unaccounted, f"unaccounted source columns: {unaccounted}"
    print(f"columns: {len(ITEMS)} SAS-SV items shipped, "
          f"{len(COMPONENTS)} PSQI component scores dropped as composites")

    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)
    assert df["id"].nunique() == len(df)

    long = df.melt(id_vars=["id"], value_vars=ITEMS,
                   var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"])
    long["resp"] = pd.to_numeric(long["resp"])

    bad = long.loc[~long["resp"].isin([1, 2, 3, 4, 5, 6]), "resp"].unique()
    assert len(bad) == 0, f"off-scale resp values: {bad}"
    assert (long["resp"] % 1 == 0).all(), "fractional resp -- check for imputation"

    long = long[["id", "item", "resp"]]
    n = long["id"].nunique()
    assert n >= 100, f"below the 100-id floor: {n}"
    print(f"{len(long):,} responses | {n:,} ids | {long['item'].nunique()} items")

    bad = [c for c in run_qc(long, permitted_values=[1, 2, 3, 4, 5, 6],
                             item_constructs={i: "li_2026_sas_sv" for i in long["item"].unique()})
           if c.status == "fail"]
    assert not bad, f"run_qc failures: {[(c.name, c.detail) for c in bad]}"

    os.makedirs(OUTDIR, exist_ok=True)
    out = os.path.join(OUTDIR, "li_2026_sas_sv.csv")
    long.to_csv(out, index=False)
    print("wrote", out)


if __name__ == "__main__":
    main()
