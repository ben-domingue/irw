"""
Seven construct blocks answered by 123 Indonesian Gen-Z beauty shoppers after
watching a simulated TikTok Shop Live session hosted by an AI streamer.

Source: Earja, D. F., & Nursanti, T. D. (2026). Dataset and Questionnaire:
        Algorithmic Transparency and Anthropomorphism of AI Streamers in
        TikTok Shop Live (n = 123) [Data set]. Zenodo.
DOI: 10.5281/zenodo.23763732
Data: https://zenodo.org/records/23763732 (files
        "Dataset_AI_Streamer_TikTokShop_n123.csv" and
        "Questionnaire_AI_Streamer_TikTokShop (1).pdf")
License: CC BY 4.0 (verified on the Zenodo record, metadata.license.id
        "cc-by-4.0")
Item text: shipped, from the deposit's own questionnaire PDF, which is a full
        codebook -- every one of the 34 item codes with its administered
        Indonesian stem and the authors' own English translation, plus the
        five shared anchors (1 = sangat tidak setuju .. 5 = sangat setuju).
        The English is the authors' gloss, not a machine translation, so it
        ships in the `_translated` columns with `language = ind`.

**Seven tables, because the questionnaire is seven labelled construct blocks**
("Section C. Construct items" names each one) and `datastandard.md`'s
"Multiple scales in one file" asks for one file per scale. The blocks share a
single five-point agreement anchor set, so the split is taken from the
questionnaire's own section headings and code prefixes, not inferred from
anchors.

The item codes keep the deposit's own column headers (`AT1`..`AT5`, lowercased),
which the questionnaire PDF also uses as its `Code` column -- so each item is
tied to its stem by the source's own label, not by position.

Dropped: `MV1` and `MV2`, the two common-method-bias marker items ("I prefer
rainy weather to sunny weather", "I prefer warm drinks to cold drinks"). They
measure nothing the study reports, they belong to no construct, and two items
is below the three-item floor ruled 2026-10-19 -- so they cannot ship as a
table of their own either.

`AL1`-`AL3` (AI literacy) DO ship: the questionnaire marks them "collected, not
used in the reported model", which is a fact about the authors' analysis, not
about the responses.

PII: none, and the deposit says so explicitly ("No names, contact details or
timestamps are included"). `ID` is a sequential 1-123 respondent number; every
other column is a coded response or a coded demographic. The screen below
prints its denominator.

Output: seven tables, 3,936 responses -- 123 respondents, 32 of the
questionnaire's 34 items (MV1/MV2 dropped, see above), all 1-5.
  * earja_2026_algorithmic_transparency -- 5 items
  * earja_2026_anthropomorphism         -- 5 items
  * earja_2026_perceived_risk           -- 5 items
  * earja_2026_trust                    -- 5 items
  * earja_2026_fomo                     -- 5 items
  * earja_2026_purchase_intention       -- 4 items
  * earja_2026_ai_literacy              -- 3 items
"""
from __future__ import annotations

from pathlib import Path
import re
import sys

import pandas as pd

SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
    "Dataset_AI_Streamer_TikTokShop_n123.csv")
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

PERMITTED = [1, 2, 3, 4, 5]

# table -> (code prefix, item count). The prefix and the count both come from
# the questionnaire PDF's "Section C" tables, which list every code.
BLOCKS = {
    "earja_2026_algorithmic_transparency": ("AT", 5),
    "earja_2026_anthropomorphism": ("AN", 5),
    "earja_2026_perceived_risk": ("PR", 5),
    "earja_2026_trust": ("TR", 5),
    "earja_2026_fomo": ("FO", 5),
    "earja_2026_purchase_intention": ("PI", 4),
    "earja_2026_ai_literacy": ("AL", 3),
}

COV_MAP = {
    "BirthCohort": "cov_birth_cohort",
    "Gender": "cov_gender",
    "Education": "cov_education",
    "Domicile": "cov_domicile",
    "Occupation": "cov_occupation",
    "Income": "cov_income",
    "PurchaseFreq": "cov_beauty_purchase_freq",
    "LiveViewingFreq": "cov_live_viewing_freq",
    "PriorAILive": "cov_prior_ai_live",
    "ManipulationCheck": "cov_manipulation_check",
}

DROP = {
    "MV1": "common-method-bias marker item, belongs to no construct",
    "MV2": "common-method-bias marker item, belongs to no construct",
}


def pii_screen(df: pd.DataFrame) -> None:
    """Print the denominator, so a screen that selected nothing is visible.

    A screen that examines zero columns reports clean, which is the worst
    shape a safety check can take -- see the 2026-10-19 Parkins incident in
    the pipeline SKILL.md.
    """
    text_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: examined {len(text_cols)} string column(s) of "
          f"{len(df.columns)}; dtypes present: "
          f"{sorted({str(t) for t in df.dtypes})}")
    assert len(df.columns) > 0
    assert not text_cols, f"unexpected text column(s): {text_cols}"


def main() -> None:
    df = pd.read_csv(SRC)
    print("raw shape", df.shape)
    pii_screen(df)
    assert len(df) == 123, len(df)
    assert df["ID"].is_unique and df["ID"].min() == 1, "ID is not 1..n"
    assert int(df.isna().sum().sum()) == 0, "unexpected missing cells"

    item_cols = {}
    for table, (prefix, n) in BLOCKS.items():
        cols = sorted((c for c in df.columns
                       if re.fullmatch(rf"{prefix}\d+", c)),
                      key=lambda c: int(re.sub(r"\D", "", c)))
        assert len(cols) == n, (table, len(cols), n, cols)
        observed = sorted(set(df[cols].to_numpy().ravel().tolist()))
        assert set(observed) <= set(PERMITTED), (table, observed)
        print(f"{table}: {n} items {cols}, observed {observed}")
        item_cols[table] = cols

    df = df.rename(columns={"ID": "id"})
    for src, dst in COV_MAP.items():
        assert src in df.columns, src
        df[dst] = df[src]
    covs = list(COV_MAP.values())

    # Balance the books: every source column is an item, a covariate, the id,
    # or a documented drop.
    accounted = set(COV_MAP) | set(covs) | {"id"}
    accounted |= {c for cs in item_cols.values() for c in cs}
    leftover = [c for c in df.columns
                if c not in accounted and c not in DROP]
    assert not leftover, f"unaccounted source columns: {leftover}"
    for col, why in DROP.items():
        assert col in df.columns, col
        print(f"skipped {col} -- {why}")

    total = 0
    for table, cols in item_cols.items():
        total += write(df, table, cols, covs)
    print(f"total responses across {len(item_cols)} tables: {total}")
    # 34 item columns in the file, less the two dropped marker items.
    assert total == 123 * 32, total


def write(df: pd.DataFrame, table: str, cols: list, covs: list) -> int:
    codes = {c: c.lower() for c in cols}
    assert len(set(codes.values())) == len(cols), codes
    long = df[["id"] + covs + cols].rename(columns=codes)
    long = long.melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    before = long["resp"].notna().sum()
    long = long[long["resp"].isin(PERMITTED)]
    assert before == len(long), \
        f"{table}: {before - len(long)} cell(s) outside {PERMITTED}"

    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + covs].sort_values(
        ["id", "item"]).reset_index(drop=True)

    checks = run_qc(long, permitted_values=PERMITTED)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, (table, fails)
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {table} {c.name}: {c.detail[:180]}")
    long.to_csv(OUT / f"{table}.csv", index=False)
    print(f"  -> {table}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={sorted(long['resp'].unique())}")
    return len(long)


if __name__ == "__main__":
    main()
