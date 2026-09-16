"""Martinez et al. (2024), "The Joint Simon task is not joint for capuchin
monkeys" -- Scientific Reports 14:5937, CC BY 4.0.

Two trial-level tables, one per experiment:

  * `martinez_2024_joint_simon` -- the Joint Simon task, 4 conditions
  * `martinez_2024_gonogo`      -- a go/no-go control, 2 conditions

`id` is the monkey; there are ten of them, below the 100-id floor in
datastandard.md. Taken on ben-domingue's ruling of 2026-09-16 (irw#2220): the
floor is a proxy for "enough data to fit a model" that was written for survey
designs, where each person answers each item once. A trials-based design
inverts that shape -- ten monkeys times ~290 trials is 2,802 observations.

`item` is the stimulus probe, `condition` crossed with `trial_type`, because
that is what varies between measurements; the repeats are carried in `trial`,
which is also what makes duplicate id+item pairs valid here. `trial_type`
determines `compatibility` exactly (1 and 2 compatible, 3 and 4 incompatible),
so compatibility travels as an item covariate rather than a second item axis.

Two things about `resp`. It comes from the experiment program's own scoring
column (`correct_fromprogram` / `correct_program`), not from comparing
`monkey_response` to `side_correct` -- those agree on all but one row of 2,802,
and the program's column is the authoritative one. And that column has a THIRD
value, 2, on 49 exp1 and 88 exp2 trials: those are trials where the monkey did
not respond at all (`monkey_response` is blank and latency is missing or at the
5s ceiling). A non-response is not a wrong answer, so they are dropped rather
than scored 0. The deposit's `correct_rv` string column labels them
inconsistently -- 9 of 49 as "correct" -- which is why it is not used.

`date` carries the session date as Unix seconds. It is also, incidentally, what
keeps `dup_id_item` from failing: that check accepts only wave/timepoint/date as
the column explaining a repeat, even though `trial` is the semantically right
one here and `_checks.py` says in a comment that trial columns belong in the
set. Filed as irw#2224; `trial` is emitted regardless.

Monkey names are case-inconsistent between the two sheets (`Gambit` in exp1,
`gambit` in exp2); they are lowercased so `id` means the same animal in both.
"""
from __future__ import annotations

import io
import zipfile
from pathlib import Path

import pandas as pd
import requests

from irw_validate.compat import run_qc

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

DOI = "10.1038/s41598-024-55885-x"
PMCID = "PMC10928181"
MEMBER = "41598_2024_55885_MOESM1_ESM.xlsx"
SUPPL = ("https://www.ebi.ac.uk/europepmc/webservices/rest/"
         "{pmcid}/supplementaryFiles?includeInlineImage=false")
UA = {"User-Agent": "irw-batch/1.0 (research)"}

NO_RESPONSE = 2

EXPERIMENTS = {
    "martinez_2024_joint_simon": ("exp1", "correct_fromprogram"),
    "martinez_2024_gonogo":      ("exp2", "correct_program"),
}


def fetch() -> bytes:
    raw = requests.get(SUPPL.format(pmcid=PMCID), headers=UA, timeout=120)
    raw.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(raw.content)) as z:
        return z.read(MEMBER)


def convert() -> None:
    blob = fetch()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for table, (sheet, score_col) in EXPERIMENTS.items():
        raw = pd.read_excel(io.BytesIO(blob), sheet_name=sheet)

        long = pd.DataFrame({
            "id": raw["monkey"].astype(str).str.strip().str.lower(),
            "item": (raw["condition"].astype(str).str.strip()
                     + "_t" + raw["trial_type"].astype(int).astype(str)),
            "resp": pd.to_numeric(raw[score_col], errors="coerce"),
            "trial": pd.to_numeric(raw["trial_number"], errors="coerce").astype("Int64"),
            "rt": pd.to_numeric(raw["latency"], errors="coerce"),
            # Unix seconds. Built by subtracting the epoch rather than by
            # dividing the int64 view, whose unit is ns on some pandas builds
            # and us on others.
            "date": (pd.to_datetime(raw["date"], errors="coerce")
                     - pd.Timestamp("1970-01-01")).dt.total_seconds(),
            "itemcov_compatibility": raw["compatibility"].astype(str).str.strip(),
        })
        # trial_type determines compatibility; assert it before relying on it.
        assert long.groupby("item")["itemcov_compatibility"].nunique().eq(1).all(), table

        n_omitted = int((long["resp"] == NO_RESPONSE).sum())
        long = long[long["resp"] != NO_RESPONSE].dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        long = long.sort_values(["id", "item", "trial"]).reset_index(drop=True)

        assert long["resp"].isin([0, 1]).all(), table
        bad = [c for c in run_qc(long) if c.status == "fail"]
        assert not bad, [(c.name, c.detail) for c in bad]

        long.to_csv(OUT_DIR / f"{table}.csv", index=False)
        print(f"{table}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} pct_correct={long['resp'].mean():.3f} "
              f"(dropped {n_omitted} no-response trials)")


if __name__ == "__main__":
    convert()
