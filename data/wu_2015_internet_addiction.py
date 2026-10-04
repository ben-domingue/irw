#!/usr/bin/env python3
# Source: https://doi.org/10.6084/m9.figshare.1573219 (PLOS ONE S1 Dataset)
# DOI: 10.1371/journal.pone.0137506
#   Wu, C.-Y., Lee, M.-B., Liao, S.-C., & Chang, L.-R. (2015). "Risk Factors
#   of Internet Addiction among Internet Users: An Online Questionnaire
#   Survey." PLOS ONE, 10(10), e0137506. (PMC4603790)
# Data: figshare file 6759531, S1 Dataset.SAV (1,100 rows x 105 columns;
#       Taiwanese internet users aged 15+, online survey, 2013).
# License: CC BY 4.0 (figshare API; the article is CC BY).
#
# Item text:
#   wu_2015_cias, wu_2015_bsrs5: shipped. The .sav variable labels carry the
#     full English stem of every item and the value labels the response
#     anchors (both levels populated). The survey was administered in
#     Chinese (Taiwan) and the deposit and paper carry only this English
#     rendering, so it is shipped as a translated substitute
#     (language=Chinese, _translated empty).
#   wu_2015_mpi_neuroticism, wu_2015_mpi_lie: not shipped. Variable labels
#     carry English stems, but the value labels (0 = "?", 1 = Yes, 2 = No)
#     contradict the file's own scoring (see below), so the option text
#     cannot be tied to the codes.
#
# Tables (item codes are the source column names):
#   wu_2015_cias  CIAS1-CIAS26, Chen Internet Addiction Scale-Revised, 1-4
#       (1 = does not match my experience at all .. 4 = definitely match;
#       paper Methods and the value labels). CIASTotal is their sum
#       (asserted).
#   wu_2015_bsrs5  BSRS1-BSRS6, the five-item Brief Symptom Rating Scale plus
#       the added suicide-ideation item, 0-4 (0 = not at all .. 4 =
#       extremely; paper Methods and value labels). BSRStotal = BSRS1-5
#       (asserted).
#   wu_2015_mpi_neuroticism  13 Maudsley Personality Inventory neuroticism
#       items (MPI1-17 minus the lie items), rated Yes / ? / No (paper).
#   wu_2015_mpi_lie  MPI3, MPI8, MPI10, MPI13, the 4-item social desirability
#       (lie) scale, same format.
#     The MPI value labels read 0 = "?", 1 = Yes, 2 = No, but the paper says
#     a higher NS score means more neuroticism, the deposit's Nscore equals
#     the plain sum of the stored codes over the 13 non-lie items (asserted;
#     no other lie set or recode reproduces it) and SDSscore the plain sum
#     over the 4 lie items (asserted), and the stored code rises
#     monotonically with BSRS distress on every item. So resp is the stored
#     code, read as 0 < 1 < 2 in the scored direction; the labels' mapping
#     of codes to Yes / ? / No is not trusted. Permitted set {0, 1, 2}.
#
# Dropped:
#   - Composites and recodes: CIASTotal, CUT56/58.5/62/68, BSRStotal,
#     BSRSrange, BSRS_CutOff6/10, R_BSRS1-6 (dichotomised BSRS), Nscore,
#     R_Nscore, R_Nsocre1, R_Nscore2, SDSscore, R_Liescore, R_ADD1-4
#     (0/1 recodes of ADD1-4), LifeImpair_2, lifeimpact, time7, time13,
#     ageg, R_edu, R_marr, R_job, YouthDummy, YAdultDummy, OldAdultDummy,
#     OnlineAct_2, OnlineAct_Cat.
#   - event: identical to ActGamingDummy in every row (asserted).
#   - IGD: unlabelled single 0/1 flag.
#   - 8 exact duplicate rows (all 105 columns equal; repeated submissions),
#     leaving 1,092 respondents.
# id: row index (no respondent id in the file). EmailDummy records only
#   whether an e-mail address was left; no address is in the file.
# Covariates: cov_gender (0 male, 1 female), cov_age_group (1 = 15-19 ..
#   14 = 80+), cov_education (1-6), cov_marital (1-5), cov_residence (1-22,
#   city/county), cov_occupation (1-5), cov_gaming, cov_social_networking,
#   cov_other_online (0/1 online activities), cov_internet_hours_week,
#   cov_life_impairment (1 none .. 4 severe), cov_suicide_attempt_lifetime,
#   _past_year, _past_month, _past_week (1 yes, 2 no), cov_left_email (0/1).

import os
import sys
import tempfile
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
TEXT_DIR = REPO_ROOT / "automated_finding" / "itemtext_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://ndownloader.figshare.com/files/6759531"

LIE = ["MPI3", "MPI8", "MPI10", "MPI13"]
NEURO = [f"MPI{i}" for i in range(1, 18) if f"MPI{i}" not in LIE]
TABLES = {
    "wu_2015_cias": ([f"CIAS{i}" for i in range(1, 27)], {1, 2, 3, 4}),
    "wu_2015_bsrs5": ([f"BSRS{i}" for i in range(1, 7)], {0, 1, 2, 3, 4}),
    "wu_2015_mpi_neuroticism": (NEURO, {0, 1, 2}),
    "wu_2015_mpi_lie": (LIE, {0, 1, 2}),
}
TEXT = {
    "wu_2015_cias": "Chen Internet Addiction Scale-Revised (CIAS-R)",
    "wu_2015_bsrs5": "Brief Symptom Rating Scale (BSRS-5) with added "
                     "suicide-ideation item",
}
COVS = {"Gender": "cov_gender", "Age": "cov_age_group",
        "Education": "cov_education", "Marital": "cov_marital",
        "Residence": "cov_residence", "Occupation": "cov_occupation",
        "ActGamingDummy": "cov_gaming",
        "ActSocialDummy": "cov_social_networking",
        "ActOtherDummy": "cov_other_online",
        "InternetTime": "cov_internet_hours_week",
        "LifeImpair": "cov_life_impairment",
        "ADD1": "cov_suicide_attempt_lifetime",
        "ADD2": "cov_suicide_attempt_past_year",
        "ADD3": "cov_suicide_attempt_past_month",
        "ADD4": "cov_suicide_attempt_past_week",
        "EmailDummy": "cov_left_email"}
COMPOSITES = {"CIASTotal", "CUT56", "CUT58.5", "CUT62", "CUT68",
              "BSRStotal", "BSRSrange", "BSRS_CutOff6", "BSRS_CutOff10",
              "Nscore", "R_Nscore", "R_Nsocre1", "R_Nscore2", "SDSscore",
              "R_Liescore", "LifeImpair_2", "lifeimpact", "time7", "time13",
              "ageg", "R_edu", "R_marr", "R_job", "YouthDummy",
              "YAdultDummy", "OldAdultDummy", "OnlineAct_2", "OnlineAct_Cat"}
COMPOSITES |= {f"R_BSRS{i}" for i in range(1, 7)}
COMPOSITES |= {f"R_ADD{i}" for i in range(1, 5)}
OTHER_DROPPED = {"event", "IGD"}


def load():
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".sav", delete=False) as f:
        f.write(r.content)
        path = f.name
    try:
        df, meta = pyreadstat.read_sav(path)
    finally:
        os.unlink(path)
    return df, meta


def strip_num(label):
    # "12. I choose to ..." -> "I choose to ..."
    head, _, rest = label.partition(". ")
    assert head.isdigit(), label
    return rest.strip()


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    TEXT_DIR.mkdir(parents=True, exist_ok=True)
    d, meta = load()
    assert d.shape == (1100, 105), d.shape

    # Balance the books.
    items = {c for its, _ in TABLES.values() for c in its}
    known = items | set(COVS) | COMPOSITES | OTHER_DROPPED
    assert set(d.columns) == known, set(d.columns) ^ known
    assert not d.isna().any().any()

    def ssum(cols):
        return d[cols].sum(axis=1)
    assert (ssum(TABLES["wu_2015_cias"][0]) == d["CIASTotal"]).all()
    assert (ssum([f"BSRS{i}" for i in range(1, 6)]) == d["BSRStotal"]).all()
    assert (ssum(NEURO) == d["Nscore"]).all()
    assert (ssum(LIE) == d["SDSscore"]).all()
    assert d["event"].equals(d["ActGamingDummy"])
    for c in NEURO + LIE:
        g = d.groupby(c)["BSRStotal"].mean()
        if c in NEURO:
            assert g.is_monotonic_increasing, (c, g.to_dict())

    n_dup = int(d.duplicated().sum())
    assert n_dup == 8, n_dup
    d = d.drop_duplicates().reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    d = d.rename(columns=COVS)
    cov_cols = list(COVS.values())

    names = []
    for table, (its, allowed) in TABLES.items():
        long = d.melt(id_vars=["id"] + cov_cols, value_vars=its,
                      var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        assert (long["resp"] % 1 == 0).all()
        long["resp"] = long["resp"].astype(int)
        for it, g in long.groupby("item"):
            bad = set(g["resp"]) - allowed
            assert not bad, (table, it, bad)
        long = long[["id", "item", "resp"] + cov_cols]
        for c in cov_cols:
            long[c] = long[c].astype("Int64")
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        assert not long.duplicated(["id", "item"]).any()
        assert long["id"].nunique() == 1092
        assert long["item"].nunique() == len(its) > 1
        pv = {i: allowed for i in its}
        checks = run_qc(long, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        out = OUT_DIR / f"{table}.csv"
        long.to_csv(out, index=False)
        names.append(table)
        rep = irw_validate.validate_file(str(out), profile="upload",
                                         context={"permitted_values": pv})
        assert rep.conforms and not rep.errors, \
            [(f.check, f.message) for f in rep.errors]
        for f in rep.findings:
            print(f"    [{f.severity}] {f.check}: {f.message}")
        print(f"{table}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}")

        if table in TEXT:
            text = []
            for it in its:
                vl = meta.variable_value_labels[it]
                assert set(int(k) for k in vl) == allowed, it
                for k, opt in sorted(vl.items()):
                    text.append({
                        "table": table, "section_id": f"{table}_1",
                        "item": it, "instrument": TEXT[table],
                        "language": "Chinese", "instructions": "",
                        "section_prompt": "",
                        "item_text": strip_num(
                            meta.column_names_to_labels[it]),
                        "item_text_translated": "",
                        "correct_response": "", "option_text": opt,
                        "option_text_translated": "", "resp": int(k)})
            tx = pd.DataFrame(text)
            assert set(tx["item"]) == set(long["item"])
            assert set(tx["resp"]) == allowed
            tx.to_csv(TEXT_DIR / f"{table}__items.csv", index=False)
            print(f"{table}__items.csv: rows={len(tx)}")
    assert len(names) == len(set(names))


if __name__ == "__main__":
    convert()
