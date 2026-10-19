#!/usr/bin/env python3

# Source: https://figshare.com/articles/dataset/_/26788267
# DOI: 10.6084/m9.figshare.26788267
#   Jiao, W., Schulz, P. J., & Chang, A. (2024). Addressing the Role of eHealth
#   Literacy in Shaping Popular Attitudes Towards Post-COVID-19 Vaccination
#   Among Chinese Adults [Dataset]. figshare.
# Data: "Data_eHEALS_VK_Chinese_Work_N=683_Raw_CSV_05242022.sav" -- 683 adults
#   in Macao/Portugal surveyed in 2022, administered in Simplified Chinese,
#   Traditional Chinese, Portuguese or English (the UserLanguage column).
#   The deposit's "Curated" sibling file is the same N with the authors'
#   recodes; the Raw file is used here.
# License: CC BY 4.0 (verified on the figshare record).
# Item text: NOT shipped. BOTH label levels carry it -- every item has a full
#   English variable label and every scale a complete set of value labels, so
#   extraction is solved and cheap. Held because two of the three scales are
#   published third-party instruments with no row in
#   itemtext/instrument_rights_register.csv (eHEALS, Norman & Skinner 2006;
#   the Vaccine Conspiracy Beliefs Scale, Shapiro et al. 2016), and under the
#   2026-10-15 silence rule silence does not ship. The computer-skills block
#   reads as study-authored and could ship alone once a ruling exists for it.
#
# THE VACCINE-KNOWLEDGE BLOCK (Q6_1-Q6_9) IS NOT SHIPPED. Its options are
#   "Correct" / "Incorrect" / "Don't know" -- three unordered categories, so it
#   is a nominal-standard candidate rather than core (BATCH_LOG 2026-08-26:
#   option-coded columns become nominal candidates at three or more
#   categories). The deposit's own Q6_*_RE recodes are 0/1/2 with no label
#   level explaining the mapping, so they are not a scored substitute.
#   Q8 (single-item vaccination intention) is dropped: one item is not a table.
#
# THREE tables, 683 respondents:
#   jiao_2024_computer_skills       Q4_1-Q4_10, 1-5   (10 items)
#   jiao_2024_eheals                Q5_1-Q5_8,  1-5   (8 items)
#   jiao_2024_vaccine_conspiracy    Q7_1-Q7_7,  1-5   (7 items)
# id: the file carries no respondent id; the 0-based row index is used.
# Covariates: cov_language (the language the survey was taken in),
#   cov_gender, cov_age_band, cov_education, cov_self_rated_health,
#   cov_home_language, cov_residency, cov_sample (Macao / non-Macao),
#   cov_phone_hours, cov_computer_hours, cov_social_media_use -- all coded,
#   with the .sav value labels harvested into metadata/covariate_labels/.
# Not shipped: GP (the consent item, constant), Q13_4_TEXT and Q14_3_TEXT
#   (free-text "other, please specify" for home language and residency --
#   language and place names only, no personal identifiers).
import os
import sys
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = Path(os.environ.get(
    "IRW_RAW_DIR",
    REPO_ROOT / "automated_finding" / "runs" / "figshare_batch" / "26788267" / "raw"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
ARTICLE = 26788267
FNAME = "Data_eHEALS_VK_Chinese_Work_N=683_Raw_CSV_05242022.sav"
SCALE = set(range(1, 6))

BLOCKS = {
    "jiao_2024_computer_skills": [f"Q4_{i}" for i in range(1, 11)],
    "jiao_2024_eheals": [f"Q5_{i}" for i in range(1, 9)],
    "jiao_2024_vaccine_conspiracy": [f"Q7_{i}" for i in range(1, 8)],
}
COVS = {
    "UserLanguage": "cov_language",
    "Q9": "cov_gender",
    "Q10": "cov_age_band",
    "Q11": "cov_education",
    "Q12": "cov_self_rated_health",
    "Q13": "cov_home_language",
    "Q14": "cov_residency",
    "source01": "cov_sample",
    "Q1": "cov_phone_hours",
    "Q2": "cov_computer_hours",
    "Q3": "cov_social_media_use",
}
NOT_SHIPPED = (["GP", "Q8", "Q13_4_TEXT", "Q14_3_TEXT"]
               + [f"Q6_{i}" for i in range(1, 10)]
               + [f"Q6_{i}_RE" for i in (1, 3, 4, 5, 6, 7, 8)])


def fetch() -> Path:
    p = RAW_DIR / FNAME
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        j = requests.get(f"https://api.figshare.com/v2/articles/{ARTICLE}",
                         headers=UA, timeout=120).json()
        url = [f["download_url"] for f in j["files"] if f["name"] == FNAME][0]
        r = requests.get(url, headers=UA, timeout=300)
        r.raise_for_status()
        p.write_bytes(r.content)
    return p


def main():
    df, _meta = pyreadstat.read_sav(str(fetch()), apply_value_formats=False)
    df.insert(0, "id", range(len(df)))

    items = [c for cols in BLOCKS.values() for c in cols]
    for c in items + list(COVS) + NOT_SHIPPED:
        assert c in df.columns, f"expected source column {c} is absent"
    unaccounted = [c for c in df.columns
                   if c not in (["id"] + items + list(COVS) + NOT_SHIPPED)]
    assert not unaccounted, f"unaccounted source columns: {unaccounted}"
    print(f"not shipped (nominal knowledge block, consent, single item, "
          f"free text): {NOT_SHIPPED}")

    df = df.rename(columns=COVS)
    for cov in COVS.values():
        if cov != "cov_language":
            df[cov] = pd.to_numeric(df[cov]).astype("Int64")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    written = []
    for name, cols in BLOCKS.items():
        t = (df[["id", *COVS.values(), *cols]]
             .melt(id_vars=["id", *COVS.values()], value_vars=cols,
                   var_name="item", value_name="resp")
             .dropna(subset=["resp"]))
        t["resp"] = pd.to_numeric(t["resp"])
        assert (t["resp"] % 1 == 0).all(), f"{name}: fractional resp"
        t["resp"] = t["resp"].astype(int)
        bad = sorted(set(t["resp"]) - SCALE)
        assert not bad, f"{name}: resp outside the documented 1-5 scale: {bad}"
        t = t[["id", "item", "resp", *COVS.values()]]
        assert not t.duplicated(["id", "item"]).any(), name
        assert t["id"].nunique() >= 100 and t["item"].nunique() >= 2, name
        assert name not in written
        checks = run_qc(t, permitted_values=SCALE)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {name} {c.name}: {c.detail[:170]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": SCALE})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        written.append(name)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
