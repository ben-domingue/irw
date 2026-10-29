"""
The SOLARIS UC1 deepfake experiments: 1,124 respondents in three countries saw
a political deepfake video on climate change and one on immigration, rated each
video's perceived trustworthiness on the 22-item PDTQ, and answered the two
attitude batteries both BEFORE and AFTER the videos.

Source: Plohl, N., Mlakar, I., Smrke, U., Bisconti, P., & Aquilino, L. (2025).
        Data from the UC1 Experiments on the perception of deepfake videos and
        their impact on attitudes [Dataset]. Zenodo.
DOI: 10.5281/zenodo.17520820
Data: https://zenodo.org/records/17520820 (UC1_Zenodo.csv -- semicolon-
        delimited with comma decimal separators, which is why the triage
        reader flagged it `recoverable_format`)
License: CC BY 4.0 (verified on the Zenodo record)
Item text: NOT shipped, and the reason differs by block. The PDTQ's 22 items
        ARE published, in the authors' own validation paper (Plohl et al. 2024,
        International Journal of Human-Computer Interaction 41(11), 6786-6803,
        doi 10.1080/10447318.2024.2384821) -- one hop from this deposit, so a
        later pass starts there rather than re-deriving. The deposit itself
        carries no codebook, no variable labels and no questionnaire file, and
        nothing in it documents the wording of the climate-denial, immigration,
        media-literacy or trust items; the two 2025 preprints the record cites
        (SSRN 10.2139/ssrn.5351533, PsyArXiv 10.31234/osf.io/knvby_v1) are where
        to look for those.

Design: the attitude batteries are repeated, so T1_*/T2_* become `wave` 1 and 2
on one table per battery rather than two tables of the same items. The video
manipulation sits between the waves, but `treat` is NOT shipped: the deposit
documents neither what CC_Group/IM_Group's six codes are nor which of them is
the control, so the condition ships as a covariate (cov_cc_group, cov_im_group,
plus the deposit's own three-way collapses) and a user who learns the coding can
reconstruct the contrast. Asserting a `treat` would be a guess with a 1-in-6
chance of naming the control correctly.

The two PDTQ blocks are the SAME instrument rated about TWO DIFFERENT videos by
the same people, so they are two tables rather than one merged table: merging
them would put two rows on every (id, item) pair.

PII: none. The deposit holds no free-text column at all -- the PII screen below
prints its denominator and finds the only string-typed columns are numeric
blocks carrying a ' ' missing sentinel. No names, emails, dates of birth,
locations or identifiers; `Country` is one of three country codes, which is a
sample stratum rather than a locating geographic code.

Output: six tables, 119,032 responses.
  * plohl_2025_climate_denial        -- 12 items x 2 waves, resp 1-5
  * plohl_2025_immigration_attitudes -- 14 items x 2 waves, resp 1-5
  * plohl_2025_pdtq_climate          -- PDTQ 22 items, resp 1-7
  * plohl_2025_pdtq_immigration      -- PDTQ 22 items, resp 1-7
  * plohl_2025_media_literacy        -- 6 items, resp 1-5
  * plohl_2025_trust                 -- 4 items, resp 1-5
"""
from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("UC1_Zenodo.csv")
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

# Single-wave blocks: output table -> (source prefix, item count).
FLAT = {
    "plohl_2025_pdtq_climate": ("CC_PT", 22),
    "plohl_2025_pdtq_immigration": ("IM_PT", 22),
    "plohl_2025_media_literacy": ("ML", 6),
    "plohl_2025_trust": ("TR", 4),
}
# Repeated blocks: output table -> (source stem, item count, item prefix).
WAVED = {
    "plohl_2025_climate_denial": ("CC", 12, "cc"),
    "plohl_2025_immigration_attitudes": ("IM", 14, "im"),
}

COV_MAP = {
    "Country": "cov_country",
    "Order": "cov_topic_order",
    "CC_Group": "cov_cc_group",
    "IM_Group": "cov_im_group",
    "CC_GROUP_3": "cov_cc_group_3way",
    "IM_GROUP_3": "cov_im_group_3way",
    "CC_NEG_POS_VID": "cov_cc_video_valence",
    "IM_NEG_POS_VID": "cov_im_video_valence",
    "Gender": "cov_gender",
    "Age": "cov_age",
    "Education": "cov_education",
    "Pol1": "cov_political_left_right",
    "Pol2": "cov_political_lib_cons",
    "Smu": "cov_social_media_minutes",
    "Df_knowledge": "cov_deepfake_knowledge",
    "Number_of_ATC_fail": "cov_attention_checks_failed",
}

# A ' ' in an otherwise numeric column is this file's missing marker; it is
# what makes pandas read those columns as strings.
BLANK = " "


def pii_screen(df: pd.DataFrame) -> None:
    text_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: examined {len(text_cols)} string column(s) of "
          f"{len(df.columns)}: {text_cols}")
    assert len(df.columns) > 0
    for banned in ("name", "email", "mail", "phone", "birth", "dob",
                   "address", "postcode", "zip", "city"):
        bad = [c for c in text_cols if banned in c.lower()]
        assert not bad, f"possible identifier column: {bad}"
    # Nothing here is free text: every string column must be numeric once the
    # ' ' sentinel is removed, which is also what makes the PII question moot.
    for c in text_cols:
        vals = _clean(df[c]).dropna()
        assert pd.to_numeric(vals, errors="coerce").notna().all(), \
            f"{c} holds non-numeric text: {sorted(set(vals))[:5]}"


def _clean(s: pd.Series) -> pd.Series:
    """Drop the ' ' missing marker, and the comma decimal separator that
    survives on any column the marker forced pandas to read as text."""
    out = s.replace(BLANK, pd.NA)
    if pd.api.types.is_string_dtype(out):
        out = out.str.replace(",", ".", regex=False)
    return out


def numeric(df: pd.DataFrame, cols: list) -> pd.DataFrame:
    return df[cols].apply(lambda s: pd.to_numeric(_clean(s), errors="raise"))


def main() -> None:
    df = pd.read_csv(SRC, sep=";", decimal=",", encoding="utf-8-sig")
    print("raw shape", df.shape)
    assert len(df) == 1124, len(df)
    pii_screen(df)

    df = df.reset_index(drop=True)
    df["id"] = range(1, len(df) + 1)
    for src, dst in COV_MAP.items():
        assert src in df.columns, src
    covs = list(COV_MAP.values())
    df = pd.concat([df, numeric(df, list(COV_MAP)).set_axis(covs, axis=1)],
                   axis=1)

    used = {"id"} | set(COV_MAP) | set(covs)
    for prefix, n in FLAT.values():
        used |= {f"{prefix}{i}" for i in range(1, n + 1)}
    for stem, n, _p in WAVED.values():
        used |= {f"T{w}_{stem}{i}" for w in (1, 2) for i in range(1, n + 1)}
    leftover = [c for c in df.columns if c not in used]
    # Everything left is a scale/subscale total, a per-topic single question,
    # an attention-check response or a deposit-computed change score. Named
    # here so the books balance rather than scrolling past.
    print(f"skipped {len(leftover)} non-item column(s), each either a "
          f"deposit-computed total/change score or a single question outside "
          f"the six batteries: {leftover}")
    assert len(leftover) == 40, len(leftover)

    for table, (prefix, n) in FLAT.items():
        cols = [f"{prefix}{i}" for i in range(1, n + 1)]
        assert all(c in df.columns for c in cols), cols
        codes = {c: c.lower() for c in cols}
        long = pd.concat([df[["id"] + covs], numeric(df, cols)], axis=1)
        long = long.rename(columns=codes).melt(
            id_vars=["id"] + covs, var_name="item", value_name="resp")
        write(long, table, covs)

    for table, (stem, n, code_prefix) in WAVED.items():
        waves = []
        for w in (1, 2):
            cols = [f"T{w}_{stem}{i}" for i in range(1, n + 1)]
            assert all(c in df.columns for c in cols), cols
            codes = {c: f"{code_prefix}{i}" for i, c in enumerate(cols, 1)}
            part = pd.concat([df[["id"] + covs], numeric(df, cols)], axis=1)
            part = part.rename(columns=codes).melt(
                id_vars=["id"] + covs, var_name="item", value_name="resp")
            part["wave"] = w
            waves.append(part)
        write(pd.concat(waves, ignore_index=True), table, covs)


def write(long: pd.DataFrame, table: str, covs: list) -> None:
    long = long.dropna(subset=["resp"]).copy()
    assert not (long["resp"] % 1 != 0).any(), "fractional resp values"
    long["resp"] = long["resp"].astype(int)
    order = (["id", "item", "resp"]
             + [c for c in ("wave",) if c in long.columns] + covs)
    long = long[order].sort_values(
        ["id", "item"] + (["wave"] if "wave" in long.columns else [])
    ).reset_index(drop=True)

    checks = run_qc(long)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, (table, fails)
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {table} {c.name}: {c.detail[:200]}")
    long.to_csv(OUT / f"{table}.csv", index=False)
    print(f"{table}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={sorted(long['resp'].unique())}"
          + (f" waves={sorted(long['wave'].unique())}"
             if "wave" in long.columns else ""))


if __name__ == "__main__":
    main()
