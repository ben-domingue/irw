#!/usr/bin/env python3

# Source: https://borealisdata.ca/dataset.xhtml?persistentId=doi:10.5683/SP3/GQ8DUY
# DOI: 10.5683/SP3/GQ8DUY
#   Sirovica, L., Ritter, C., Hendricks, J., Weary, D., & Gulati, S. (2022).
#   Replication Data and Supplementary Material for: Public attitude towards
#   and perceptions of dairy cattle welfare in cow-calf management systems
#   differing in type of social and maternal contact [Dataset]. Borealis.
# Data: "CAUSdataset with AnonymousIDs and Constructs_Perceptions of cow-calf
#   management.tab" -- 1,794 Canadian and US respondents, each shown ONE of
#   four cow-calf management systems and then asked about it.
# License: CC0 1.0 (verified on the Borealis record, 2026-10-19).
# Item text: NOT shipped, and it needs no derivation: the deposit ships
#   "Survey_PerceptionsCowCalf.pdf", its own questionnaire. The items are the
#   study's own, so there is no rights question either. Left for a text pass.
#
# THREE tables, 1,794 respondents:
#   sirovica_2022_system_attitude     3 items, 1-7  (agree / appropriate /
#                                     acceptable, about the system shown)
#   sirovica_2022_welfare_relevance   3 items, 1-6  (how relevant welfare is
#                                     for the cow, the calf, the foster cow)
#   sirovica_2022_welfare_perception 15 items, 1-7  (five welfare dimensions
#                                     x three animals)
#
# THE FOSTER ITEMS ARE NOT MISSING DATA, THEY ARE THE DESIGN. Only the 469
#   respondents shown the foster-cow system (`FC`) were asked anything about a
#   foster cow; for the other three systems those columns are blank by
#   construction, which this script asserts rather than assumes. So the
#   relevance and perception tables are sparse on purpose: 1,794 respondents
#   answered the cow and calf items, 469 also the foster ones.
#
# The 15 perception items are one battery, not five: the same five welfare
#   dimensions (quality of life, care, health, feelings, natural life) were
#   asked about each animal on the same 1-7 scale, so the item name carries
#   the dimension and the animal (`Care_Calf`) and one table holds them.
#
# NOT SHIPPED: the deposit's own construct scores (`attitude`,
#   `aw_quallife_construct`, `WelfareRelevance`), the `text*` string copies of
#   the single-choice questions, `Qual` (a free-text comment), and the
#   willingness-to-pay / reality-belief single items and their recodes -- each
#   is one global question of its own content.
#
# id: the deposit's own anonymous ID (CA1..., unique for all 1,794 rows).
# cov_system: which of the four systems the respondent was shown -- the
#   experimental assignment, as a covariate because `treat` is one 0/1 column
#   and this has four arms (NS 477, FC 469, SG 429, SI 419).
# Covariates: cov_system, cov_age, cov_sex, cov_country, cov_children,
#   cov_pets, cov_education, cov_income, cov_location,
#   cov_dairy_consumption, cov_industry_familiarity,
#   cov_industry_involvement -- the deposit's own numeric recodes.
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
    REPO_ROOT / "automated_finding" / "runs" / "tail_batch" / "gq8duy" / "raw"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
FILE_ID = 270642
FNAME = ("CAUSdataset with AnonymousIDs and Constructs_Perceptions of "
         "cow-calf management.tab")
ATTITUDE = ["Agree", "Appropriate", "Acceptable"]
RELEVANCE = ["Relevant_Cow", "Relevant_Calf", "Relevant_Foster"]
PERCEPTION = [f"{d}_{a}" for d in ("QualLife", "Care", "Health", "Feelings",
                                   "NatlLife") for a in ("Cow", "Calf", "Foster")]
FOSTER_SYSTEM = "FC"
COVS = {"System": "cov_system", "Age": "cov_age", "textSex": "cov_sex",
        "Country": "cov_country", "textChildren": "cov_children",
        "textPets": "cov_pets", "textEducationLevel": "cov_education",
        "textIncome": "cov_income", "textLocation": "cov_location",
        "DairyConsumption": "cov_dairy_consumption",
        "InducstryFamiliarity": "cov_industry_familiarity",
        "IndustryInvolvement": "cov_industry_involvement"}
STRING_COVS = {"cov_sex", "cov_country", "cov_children", "cov_pets",
               "cov_education", "cov_income", "cov_location", "cov_system"}
TABLES = {"sirovica_2022_system_attitude": (ATTITUDE, set(range(1, 8))),
          "sirovica_2022_welfare_relevance": (RELEVANCE, set(range(1, 7))),
          "sirovica_2022_welfare_perception": (PERCEPTION, set(range(1, 8)))}


def fetch() -> Path:
    p = RAW_DIR / FNAME
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        url = ("https://borealisdata.ca/api/access/datafile/"
               f"{FILE_ID}?format=original")
        r = requests.get(url, headers=UA, timeout=600)
        r.raise_for_status()
        p.write_bytes(r.content)
    return p


def main():
    # The original file is COMMA-separated although Dataverse serves it
    # as a .tab: reading it with a tab separator yields one column.
    df = pd.read_csv(fetch(), sep=",")
    assert len(df) == 1794, len(df)
    assert df["ID"].is_unique
    assert not df[ATTITUDE].isna().any().any(), "the attitude block is complete"

    # The foster columns exist only for the foster-system respondents.
    foster = [c for c in RELEVANCE + PERCEPTION if c.endswith("_Foster")]
    is_fc = df["System"] == FOSTER_SYSTEM
    assert df.loc[is_fc, foster].notna().all().all(), "an FC respondent is blank"
    assert df.loc[~is_fc, foster].isna().all().all(), \
        "a non-FC respondent answered a foster item"
    print(f"foster items answered by {int(is_fc.sum())} of 1,794 respondents "
          f"(system {FOSTER_SYSTEM} only), blank by design for the rest")

    df = df.rename(columns=COVS)
    df["id"] = df["ID"].astype(str)
    cov_cols = list(COVS.values())
    for cov in cov_cols:
        if cov in STRING_COVS:
            df[cov] = df[cov].astype(str)
        else:
            v = pd.to_numeric(df[cov], errors="coerce")
            df[cov] = v.astype("Int64") if (v.dropna() % 1 == 0).all() else v

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (cols, scale) in TABLES.items():
        t = (df[["id", *cov_cols, *cols]]
             .melt(id_vars=["id", *cov_cols], value_vars=cols,
                   var_name="item", value_name="resp")
             .dropna(subset=["resp"]))
        t["resp"] = pd.to_numeric(t["resp"])
        assert (t["resp"] % 1 == 0).all(), name
        t["resp"] = t["resp"].astype(int)
        bad = sorted(set(t["resp"]) - scale)
        assert not bad, f"{name}: resp outside the documented scale: {bad}"
        t = t[["id", "item", "resp", *cov_cols]]
        assert not t.duplicated(["id", "item"]).any(), name
        assert t["id"].nunique() == 1794 and t["item"].nunique() == len(cols)
        checks = run_qc(t, permitted_values=scale)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {name} {c.name}: {c.detail[:140]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": scale})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
