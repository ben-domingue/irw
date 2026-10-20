#!/usr/bin/env python3

# Source: https://zenodo.org/records/23318225
# DOI: 10.5281/zenodo.23318225
#   Byrne, P., Saia Pope, J., O'Leary, N., Bakshi, N., & Devane, D. (2026).
#   Health literacy and trust in health information sources in Ireland:
#   anonymised survey data [Dataset]. Zenodo.
# Data: "iHF_health_literacy_survey_anonymised_v2.csv" -- 448 adults living in
#   Ireland, recruited through Prolific, surveyed on QuestionPro 18-24 March
#   2025. Ships with a real codebook (iHF_codebook_v2.xlsx), which is the
#   source for every scale range and covariate coding below.
# License: CC BY 4.0 (verified on the Zenodo record, 2026-10-20).
# Item text: NOT shipped for the 44 HLQ items, and it is not a gap this
#   pipeline can close. The codebook states it outright: "the HLQ is used
#   under licence from Swinburne University of Technology. Under that licence
#   the individual item wording cannot be reproduced ... Researchers wishing
#   to see the items should contact Swinburne." So the text exists, is
#   deliberately withheld at source, and a later pass should not re-derive
#   this -- it should go to Swinburne or not at all. Both label levels were
#   checked: the CSV has bare codes (hlq01..hlq44) and the codebook's own
#   "Survey question" column says "item wording not reproduced (licensed
#   instrument)" for all 44.
#   The eight information-source items ARE fully worded in the codebook's
#   Variables sheet (study-authored, under the deposit's CC BY), so
#   byrne_2026_health_info_sources is item-text-ready for a follow-up pass.
#
# THREE tables. The split is the codebook's own structure, not an inference
#   from observed value ranges:
#     byrne_2026_hlq_part1         hlq01-hlq23, "HLQ Part 1 (agreement
#                                  scale)", 1-4 strongly disagree..strongly
#                                  agree
#     byrne_2026_hlq_part2         hlq24-hlq44, "HLQ Part 2 (difficulty
#                                  scale)", 1-5 cannot do or always
#                                  difficult..very easy
#     byrne_2026_health_info_sources  the 8 Section 4 items, 1-5 never..very
#                                  often
#   Parts 1 and 2 are two response instruments the HLQ administers in
#   sequence, each named and ranged separately by the codebook -- not one
#   scale split on a format difference.
#
# id: respondent_id (HL0001-HL0448), kept as the string the deposit assigns.
#   The codebook says it is "random, non-sequential; assigned after the rows
#   were shuffled" and cannot be linked back -- a study-assigned anonymous id,
#   so there is nothing to replace.
# PII: none. Every demographic is banded, and the deposit applied disclosure
#   control until each respondent shared their 3-way demographic combination
#   with at least two others. No postal code, no free text, no dates.
# Covariates: the 17 banded demographics and access variables, carried with
#   the deposit's own codes and categories. Blanks are suppressed values
#   (codebook, Recodes sheet) and stay missing.
# NOT shipped: internet_home -- constant (1 = Yes for all 448 respondents),
#   so it distinguishes nobody.
import os
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = Path(os.environ.get(
    "IRW_RAW_DIR",
    REPO_ROOT / "automated_finding" / "runs" / "zenodo" / "23318225"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
RECORD, FNAME = 23318225, "iHF_health_literacy_survey_anonymised_v2.csv"

COVS = ["age_band", "sex", "education_band", "employment_status",
        "long_standing_condition", "private_insurance", "medical_card",
        "ed_attend_12m", "settlement_type", "ethnicity_grp", "residence_band",
        "home_language", "internet_health_freq", "device_smartphone",
        "device_tablet", "device_laptop", "device_desktop"]
NOT_SHIPPED = ["internet_home"]
SOURCE_ITEMS = ["source_clinician", "source_health_org", "source_government",
                "source_news", "source_independent_web", "source_social_media",
                "source_family_friends", "source_other"]
SCALES = [
    ("byrne_2026_hlq_part1", [f"hlq{i:02d}" for i in range(1, 24)],
     set(range(1, 5))),
    ("byrne_2026_hlq_part2", [f"hlq{i:02d}" for i in range(24, 45)],
     set(range(1, 6))),
    ("byrne_2026_health_info_sources", SOURCE_ITEMS, set(range(1, 6))),
]


def fetch() -> Path:
    p = RAW_DIR / FNAME
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        url = (f"https://zenodo.org/api/records/{RECORD}/files/"
               f"{FNAME}/content")
        r = requests.get(url, headers=UA, timeout=600)
        r.raise_for_status()
        p.write_bytes(r.content)
    return p


def main():
    df = pd.read_csv(fetch())
    items_all = [c for _, cols, _ in SCALES for c in cols]
    expected = {"respondent_id", *COVS, *NOT_SHIPPED, *items_all}
    assert set(df.columns) == expected, set(df.columns) ^ expected
    assert len(df) == 448, len(df)
    assert df["respondent_id"].nunique() == len(df)
    assert df["internet_home"].nunique() == 1, "internet_home is not constant"
    print(f"not shipped: {NOT_SHIPPED} (constant)")

    df = df.rename(columns={"respondent_id": "id"})
    cov_cols = [f"cov_{c}" for c in COVS]
    df = df.rename(columns=dict(zip(COVS, cov_cols)))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for table, items, scale in SCALES:
        t = (df[["id", *cov_cols, *items]]
             .melt(id_vars=["id", *cov_cols], value_vars=items,
                   var_name="item", value_name="resp")
             .dropna(subset=["resp"]))
        t["resp"] = pd.to_numeric(t["resp"])
        assert (t["resp"] % 1 == 0).all(), f"{table}: fractional resp"
        t["resp"] = t["resp"].astype(int)
        bad = sorted(set(t["resp"]) - scale)
        assert not bad, f"{table}: resp outside the codebook range: {bad}"
        t = t[["id", "item", "resp", *cov_cols]]
        assert not t.duplicated(["id", "item"]).any()
        assert t["id"].nunique() == 448
        assert t["item"].nunique() == len(items) >= 2

        checks = run_qc(t, permitted_values=scale)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (table, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {table}: {c.name}: {c.detail[:150]}")
        report = irw_validate.validate_frame(
            t, label=table, profile="upload", context={"permitted_values": scale})
        assert report.conforms and not report.errors, \
            [(f.check, f.message) for f in report.errors]

        t.to_csv(OUT_DIR / f"{table}.csv", index=False)
        print(f"{table}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} "
              f"resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
