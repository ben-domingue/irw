#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC10629385
# DOI: 10.7717/peerj.16295
#
# Moon & Kim (2023), "Multiple mediation effect of coping styles and
# self-esteem in the relationship between spousal support and pregnancy
# stress of married immigrant pregnant women." PeerJ. CC BY 4.0. N=206.
# (Note: the deferred-candidate CSV's title field for this DOI was wrong
# -- "sports participation" -- and doesn't match the article; verified
# via Europe PMC full-text XML that this is the correct paper/DOI.)
#
# The raw file bundles items from several distinct named instruments
# (confirmed against the paper's Measures section and each SPSS column's
# embedded value labels):
#   - Self-esteem (11 items from the Prenatal Psychosocial Profile, PPP;
#     Curry, Campbell & Christian 1994), 4-point (1=not at all,
#     4=always).
#   - Korean communication ability (4 items: speaking/hearing/reading/
#     writing), 5-point per the SPSS value labels themselves (1=naver
#     [sic, source-file label typo for "never"], 2=not good, 3=moderate,
#     4=good, 5=very good) -- overriding the paper's own text, which
#     inconsistently describes this as a "5-point scale (1='not at all'
#     to 4='very good')"; the file's own value-label metadata is the
#     authoritative definition of what was actually coded.
#   - Coping styles (Billings & Moos 1981 / Kim 1989/2003), problem-
#     focused (8 items) and emotion-focused (10 items) shipped as two
#     separate files per the paper's own two-subscale Cronbach's alpha
#     reporting, 4-point (1=strongly disagree, 4=strongly agree).
#   - Spousal support (11 of 22 PPP social-support items), 6-point
#     (1=very dissatisfied, 6=very satisfied).
#   - Pregnancy stress (11 PPP items), 4-point (1=not stressful at all,
#     4=very stressful).
#
# Two data-quality fixes applied before shipping:
#   - `9` is a shared missing/sentinel code used across several items in
#     multiple scales (self-esteem, coping, spousal support) -- out of
#     range for every 4- and 6-point scale here, dropped.
#   - `6` appears exactly once per item across all 11 pregnancystress
#     items (same respondent row each time) -- out of the confirmed 1-4
#     range for that scale (value labels only define 1 and 4), dropped
#     as a sentinel/entry error, not a real response.
#   - `socialsupportp9` has one non-integer value (1.6), a data-entry
#     artifact on an otherwise strictly-integer ordinal scale; dropped.
#   - The first item of each scale (selfesteem1, koreanspeaking,
#     stresscopingproblem1, socialsupportp1, pregnancystress1) was
#     exported by SPSS with its endpoint values as text labels
#     ("not at all"/"always" etc.) while every other item in the same
#     scale kept numeric codes -- an export quirk, not a different
#     coding scheme; mapped back to the same numeric codes.
#
# Covariates (age, spouse's age, nationality, education, job, income,
# etc.) are ordinary demographic/background variables, not PII.

import io
import tempfile
import zipfile
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SUPPL_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10629385/supplementaryFiles"
MEMBER = "peerj-11-16295-s001.sav"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {
    "mothage": "cov_age",
    "partage": "cov_partner_age",
    "nation": "cov_nationality",
    "redidura": "cov_residence_duration",
    "edu": "cov_education",
    "withpartner": "cov_lives_with_partner",
    "job": "cov_job",
    "partjob": "cov_partner_job",
    "income": "cov_income",
    "partconv": "cov_partner_conversation_time",
    "GA": "cov_gestational_age",
    "pregnancynumber": "cov_pregnancy_number",
    "pregnancyhope": "cov_pregnancy_planned",
    "pregnancycompli": "cov_pregnancy_complications",
    "presentbabynumber": "cov_children_count",
}

TEXT_MAPS = {
    "selfesteem1": {"not at all": 1, "always": 4},
    "stresscopingproblem1": {"strongly disagree": 1, "strongly agree": 4},
    "socialsupportp1": {"very dissatisfied": 1, "very satisfied": 6},
    "pregnancystress1": {"not stressful at all": 1, "very stressful": 4},
    "koreanspeaking": {"naver": 1, "not good": 2, "moderate": 3, "good": 4, "very good": 5},
}

SCALES = {
    "moon_2023_selfesteem": (
        ["selfesteem1"] + [f"se{i}" for i in range(2, 11)] + ["selfesteem11"], (1, 4)),
    "moon_2023_korean_proficiency": (
        ["koreanspeaking", "koreanhearing", "koreanreading", "koreanwriting"], (1, 5)),
    "moon_2023_coping_problem": (
        ["stresscopingproblem1"] + [f"stresscopingp{i}" for i in range(2, 9)], (1, 4)),
    "moon_2023_coping_emotion": (
        [f"stresscopinge{i}" for i in range(9, 19)], (1, 4)),
    "moon_2023_spousal_support": (
        [f"socialsupportp{i}" for i in range(1, 12)], (1, 6)),
    "moon_2023_pregnancy_stress": (
        [f"pregnancystress{i}" for i in range(1, 12)], (1, 4)),
}


def _to_numeric(series, col):
    tmap = TEXT_MAPS.get(col)
    if tmap:
        def parse(v):
            if isinstance(v, str):
                return tmap.get(v.strip().lower())
            return v
        series = series.apply(parse)
    return pd.to_numeric(series, errors="coerce")


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(SUPPL_URL, headers=UA, timeout=120)
    r.raise_for_status()
    zf = zipfile.ZipFile(io.BytesIO(r.content))
    with tempfile.NamedTemporaryFile(suffix=".sav") as tmp:
        tmp.write(zf.read(MEMBER))
        tmp.flush()
        df = pd.read_spss(tmp.name, convert_categoricals=False)
        df_labeled = pd.read_spss(tmp.name, convert_categoricals=True)

    assert df["id"].nunique() == len(df)

    # convert_categoricals=True gives us the text-labeled version for the
    # mixed text/numeric columns; use it as the source so string labels
    # come through consistently for the text-mapping step.
    for col in TEXT_MAPS:
        df[col] = df_labeled[col]

    cov_lookup = {c.lower(): c for c in df.columns}
    cov_cols = []
    for src, out in COV_RENAME.items():
        match = cov_lookup.get(src.lower())
        if match:
            df = df.rename(columns={match: out})
            cov_cols.append(out)

    for out_name, (items, (lo, hi)) in SCALES.items():
        work = df[["id"] + cov_cols + items].copy()
        for c in items:
            work[c] = _to_numeric(work[c], c)

        long = work.melt(id_vars=["id"] + cov_cols, value_vars=items,
                          var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        # drop shared missing sentinel and out-of-range/non-integer noise
        long = long[long["resp"] != 9]
        long = long[(long["resp"] >= lo) & (long["resp"] <= hi)]
        long = long[long["resp"] == long["resp"].round()]

        out_cols = ["id", "item", "resp"] + cov_cols
        long = long[out_cols]

        out_path = OUT_DIR / f"{out_name}.csv"
        long.to_csv(out_path, index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
