"""
Generative-AI use, crisis leadership, job crafting and innovative work
behaviour among Saudi healthcare employees.

Source: Mashat, Reem. "The impact of generative artificial intelligence on
        healthcare innovation: the mediation effect of job crafting and
        moderation effect of crisis leadership." (2026)
DOI: 10.5281/zenodo.21311625
Data: https://zenodo.org/records/21311625 (Saudi Healthcare Data.xlsx, Sheet1)
License: CC BY 4.0 (verified on the Zenodo record, metadata.license = cc-by-4.0)
Item text: not shipped — the .xlsx has one header row of positional codes
        (GAI1…GAI19, CL1…CL24, JC1…JC21, IWB1…IWB9) and no codebook,
        second header row or label sheet anywhere in the deposit (Sheet2 is
        empty). Stems would have to come from the paper.

No respondent identifier and no demographic columns are published, so `id` is
the spreadsheet row index (1-based) and the tables carry no covariates.
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

SCALES = [
    ([f"GAI{i}" for i in range(1, 20)], "mashat_2026_genai_use"),
    ([f"CL{i}" for i in range(1, 25)],  "mashat_2026_crisis_leadership"),
    ([f"JC{i}" for i in range(1, 22)],  "mashat_2026_job_crafting"),
    ([f"IWB{i}" for i in range(1, 10)], "mashat_2026_innov_work_behaviour"),
]
FACTOR_SCORES = ["De.HJC", "In.Challenging", "In.SocialJR", "In.StJR"]


def main() -> None:
    df = pd.read_excel(SRC, sheet_name="Sheet1")
    print("raw shape", df.shape)
    text_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: examined {len(text_cols)} string column(s) of "
          f"{len(df.columns)}: {text_cols}")
    assert len(df.columns) > 0
    assert not text_cols, f"unexpected free-text columns: {text_cols}"

    df = df.reset_index(drop=True)
    df["id"] = df.index + 1

    used = {"id"}
    written: set[str] = set()
    for cols, table in SCALES:
        for c in cols:
            assert c in df.columns, c
        used.update(cols)
        long = df[["id"] + cols].melt(id_vars=["id"], var_name="item",
                                      value_name="resp")
        long = long.dropna(subset=["resp"])
        assert (long["resp"] % 1 == 0).all(), "fractional Likert value"
        long["resp"] = long["resp"].astype(int)
        assert long["resp"].between(1, 5).all(), "outside the 1-5 scale"
        long = long[["id", "item", "resp"]].sort_values(["id", "item"])
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

    skipped = {c: "standardised factor/composite score, not an item response"
               for c in FACTOR_SCORES}
    used.update(skipped)
    leftover = [c for c in df.columns if c not in used]
    assert not leftover, f"unaccounted source columns: {leftover}"
    for c, why in skipped.items():
        print(f"skipped column {c}: {why}")


if __name__ == "__main__":
    main()
