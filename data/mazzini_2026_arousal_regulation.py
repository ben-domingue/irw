"""
Nine arousal- and behaviour-regulation items rated by owners of 1,692 dogs,
twice: for the dog now, and retrospectively for the dog as a puppy.

Source: Mazzini, A., & Riemer, S. (2026). The big dog play and motivation
        questionnaire responses, intra-rater and inter-rater responses
        [Dataset]. figshare. The deposit's own description: "anonymised
        responses to the Big Dog Play and Motivation Questionnaire, designed to
        assess variation in play motivation, toy engagement, and behavioural
        regulation in pet, sport, and working dogs ... Data were collected
        between February 2019 and April 2020 via an online survey available in
        English and German."
DOI: 10.6084/m9.figshare.30540344.v3
Data: https://doi.org/10.6084/m9.figshare.30540344.v3 (the
        "..._mazzini_riemer.csv" file; the sibling "_raw_data.xlsx" holds the
        same 25 columns)
License: CC BY 4.0 (verified on the figshare record, license.name "CC BY 4.0")
Item text: NOT shipped. The column names are short English mnemonics
        (`problems_calming`, `relaxing_after_arousal`), which identify each item
        unambiguously but are NOT the wording the owners read, and a `.csv` has
        no label level at all, so both levels were checked and neither exists.
        The deposit ships no codebook. Where to look: the validation paper the
        description cites, "Mazzini et al., 2025", on addictive-like behaviour
        towards toys in dogs -- the record carries no related identifier
        (`resource_doi` is null), so a later pass must find it. Note also that
        the survey ran in BOTH English and German, so a later pass owes the
        administered wording in both, not one.

**`id` is the dog, not the owner, and that is correct here.** `datastandard.md`
defines `id` as "the focal unit being measured -- typically a person, but
sometimes another entity", and these items rate the dog's behaviour. Non-human
subjects are not a reason to skip (SKILL.md, 2026-08-10); this was judged on
content and it is an ordinary repeated-item battery.

**TWO tables rather than one with `wave`, deliberately.** The nine items were
answered twice -- once about the dog now (`problems_calming`), once
retrospectively about the dog as a puppy (`puppy_problems_calming`) -- and both
answers were given at the SAME sitting. Putting them in one table under `wave`
1 and 2 would present a single-occasion retrospective recall as a longitudinal
measurement, which is what `wave` means to anyone fitting a model to it. Two
tables say what happened instead, and nothing is lost: both carry the same
`id`, so a user who wants the pair can join them.

The puppyhood table is smaller on purpose: about 1,180 of the 1,692 owners
answered it, presumably those who had the dog from puppyhood. That is real
structural missingness, not attrition.

**The AB-Q's own items are NOT in this deposit, only its total.** `AB_Q_score`
runs 15-75, i.e. fifteen items on 1-5, while the nine items here sum to 11-43
and correlate 0.48 with it -- so the Addictive-like Behaviour Questionnaire the
description mentions is a *different*, 15-item instrument whose per-item
responses were not deposited. Worth knowing before anyone goes looking for them
here: `AB_Q_score` is dropped as a total and the items behind it are simply
absent.

PII: none, and the deposit says so itself ("no identifying information was
collected"). The screen below prints its denominator; the string columns are
breed group, purpose and sex/neuter status, all closed categories.

Output: two tables, 25,866 responses.
  * mazzini_2026_arousal_regulation       -- 9 items, resp 1-5, 1,692 dogs
  * mazzini_2026_arousal_regulation_puppy -- 9 items, resp 1-5, ~1,192 dogs
"""
from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("mazzini_riemer.csv")
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

PERMITTED = [1, 2, 3, 4, 5]

ITEMS = ["problems_calming", "not_sleeping", "learning_quickly",
         "problems_concentrating", "over_motivated", "training_settle",
         "frustrated", "easy_motivate", "relaxing_after_arousal"]

BLOCKS = {
    "mazzini_2026_arousal_regulation": "",
    "mazzini_2026_arousal_regulation_puppy": "puppy_",
}

COV_MAP = {
    "FCI_cat": "cov_fci_breed_group",
    "purpose_all": "cov_purpose",
    "age": "cov_age_years",
    "sex_status": "cov_sex_neuter_status",
    "training_enthusiastic_ball_tug": "cov_training_enthusiasm_ball_tug",
}

DROP = {
    "AB_Q_score": "the Addictive-like Behaviour Questionnaire TOTAL. Its range "
        "15-75 is fifteen items on 1-5, and the nine items shipped here sum to "
        "11-43 and correlate 0.48 with it -- so the AB-Q is a different, "
        "15-item instrument whose per-item responses are NOT in this deposit",
}


def pii_screen(df: pd.DataFrame) -> None:
    text_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: examined {len(text_cols)} string column(s) of "
          f"{len(df.columns)}: {text_cols}")
    assert len(df.columns) > 0
    # Each is a closed category; the deposit states no identifying information
    # was collected, and this checks that rather than taking it on trust.
    for c in text_cols:
        k = df[c].nunique()
        assert k <= 20, f"{c} has {k} distinct values -- check for free text"


def main() -> None:
    df = pd.read_csv(SRC)
    print("raw shape", df.shape)
    pii_screen(df)
    assert len(df) == 1692, len(df)
    assert df["dog_id"].is_unique and df["dog_id"].min() == 1

    # The AB-Q claim in the docstring, checked rather than asserted in prose.
    ab = df["AB_Q_score"]
    complete = df[ITEMS].notna().all(axis=1)
    nine = df.loc[complete, ITEMS].sum(axis=1)
    print(f"AB_Q_score spans {int(ab.min())}-{int(ab.max())} (15 items x 1-5) "
          f"while the nine items here sum to {int(nine.min())}-"
          f"{int(nine.max())}, r={ab.corr(df[ITEMS].sum(axis=1)):.2f} -- "
          "a different instrument, items not deposited")
    assert ab.max() > nine.max()

    df = df.reset_index(drop=True)
    # `id` is the deposit's own dog_id rather than a row index: it is a bare
    # 1..1692 serial with no identifying content, it links the two tables here,
    # and it links both back to the deposit's own files.
    df["id"] = df["dog_id"].astype(int)
    for src, dst in COV_MAP.items():
        assert src in df.columns, src
        df[dst] = df[src]
    covs = list(COV_MAP.values())

    accounted = (set(COV_MAP) | set(covs) | set(DROP) | {"id", "dog_id"}
                 | {f"{p}{c}" for p in BLOCKS.values() for c in ITEMS})
    leftover = [c for c in df.columns if c not in accounted]
    assert not leftover, f"unaccounted source columns: {leftover}"
    for c, why in DROP.items():
        print(f"skipped column {c}: {why}")

    for table, prefix in BLOCKS.items():
        cols = [f"{prefix}{c}" for c in ITEMS]
        assert all(c in df.columns for c in cols), (table, cols)
        # The item code is the item's own mnemonic, identical across the two
        # tables, so the pair is joinable on (id, item).
        codes = dict(zip(cols, ITEMS))
        long = df[["id"] + covs + cols].rename(columns=codes)
        long = long.melt(id_vars=["id"] + covs, var_name="item",
                         value_name="resp")
        before = long["resp"].notna().sum()
        long = long[long["resp"].isin(PERMITTED)]
        assert before == len(long), \
            f"{table}: {before - len(long)} cell(s) outside {PERMITTED}"
        write(long, table, covs)


def write(long: pd.DataFrame, table: str, covs: list) -> None:
    long = long.copy()
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + covs].sort_values(
        ["id", "item"]).reset_index(drop=True)

    checks = run_qc(long, permitted_values=PERMITTED)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, (table, fails)
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {table} {c.name}: {c.detail[:200]}")
    long.to_csv(OUT / f"{table}.csv", index=False)
    print(f"{table}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={sorted(long['resp'].unique())}")


if __name__ == "__main__":
    main()
