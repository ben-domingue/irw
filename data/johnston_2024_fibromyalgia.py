"""
Central sensitisation, sensory processing sensitivity and subthreshold autism
traits in people with fibromyalgia and controls.

Source: Johnston, Helen. "Autistic-like Behaviour in Fibromyalgia is
        Associated with Hypersensitisation in Sensory Processing Sensitivity
        dataset." (2024)
DOI: 10.5281/zenodo.10840244
Data: https://zenodo.org/records/10840244 (All_data_final.csv)
License: CC BY 4.0 (verified on the Zenodo record, metadata.license = cc-by-4.0)
Item text: not shipped — the CSV's only labelling is positional column headers
        (CSI1…CSI25, SPSQa_1…SPSQb_8, SAT1…SAT24) and there is no codebook in
        the deposit (the record holds this one file). Stems would have to come
        from the published CSI, SPSQ and SATQ instruments.

Item codes keep the source headers. Three instruments, three tables:
  CSI  — Central Sensitisation Inventory, 25 items, 0-4
  SPSQ — Sensory Processing Sensitivity Questionnaire, parts a and b,
         16 items, 0-10 (one instrument, so one file)
  SAT  — subthreshold autism traits, 24 items, 0-3
"""
from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

SRC = Path(sys.argv[1])
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")

COV_MAP = {
    "Group (0 = Control, 1 = Fibromyalgia)": "cov_group",
    "SEX (0 = Male, 1 = Female)": "cov_sex",
    "Age": "cov_age",
    "SES": "cov_ses",
}

SCALES = [
    ([f"CSI{i}" for i in range(1, 26)], (0, 4), "johnston_2024_csi"),
    ([f"SPSQa_{i}" for i in range(1, 9)] + [f"SPSQb_{i}" for i in range(1, 9)],
     (0, 10), "johnston_2024_spsq"),
    ([f"SAT{i}" for i in range(1, 25)], (0, 3), "johnston_2024_satq"),
]
AGG = ["CSI_total", "SAT_total", "SPS_total", "SPSa_total", "SPSb_total"]


def main() -> None:
    df = pd.read_csv(SRC)
    print("raw shape", df.shape)
    text_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: examined {len(text_cols)} string column(s) of "
          f"{len(df.columns)}: {text_cols}")
    assert len(df.columns) > 0
    assert not text_cols, f"unexpected free-text columns: {text_cols}"

    df = df.reset_index(drop=True)
    df["id"] = df.index + 1   # no respondent identifier is published
    for src, dst in COV_MAP.items():
        assert src in df.columns, src
        df[dst] = df[src]
    covs = list(COV_MAP.values())

    used = {"id"} | set(COV_MAP) | set(covs)
    written: set[str] = set()
    for cols, (lo, hi), table in SCALES:
        for c in cols:
            assert c in df.columns, c
        used.update(cols)
        long = df[["id"] + covs + cols].melt(
            id_vars=["id"] + covs, var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"])
        assert (long["resp"] % 1 == 0).all(), "fractional Likert value"
        long["resp"] = long["resp"].astype(int)
        assert long["resp"].between(lo, hi).all(), f"outside {lo}-{hi}"
        long = long[["id", "item", "resp"] + covs].sort_values(["id", "item"])
        assert table not in written
        written.add(table)
        _checks = run_qc(long)
        _fails = [(c.name, c.detail) for c in _checks if c.status == "fail"]
        assert not _fails, (table, _fails)
        for _c in _checks:
            if _c.status == "warn":
                print(f"  [qc warn] {table} {_c.name}: {_c.detail[:180]}")
        long.to_csv(OUT / f"{table}.csv", index=False)
        print(f"{table}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={sorted(long['resp'].unique())}")

    skipped = {c: "person-level composite (sum of the item columns above)"
               for c in AGG}
    used.update(skipped)
    leftover = [c for c in df.columns if c not in used]
    assert not leftover, f"unaccounted source columns: {leftover}"
    for c, why in skipped.items():
        print(f"skipped column {c}: {why}")


if __name__ == "__main__":
    main()
