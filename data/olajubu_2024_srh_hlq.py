#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/783m2r6y6m (version 1)
# DOI: 10.1177/23779608251411367
#   Olajubu, A. O., Komolafe, A. O., & Fatusi, A. O. (2026). "Sexual and
#   Reproductive Health Literacy and Service Utilization Among Young People
#   in Southwest Nigeria." SAGE Open Nursing. (PMC12847649; CC BY 4.0. Found
#   by Crossref title search; the deposit lists no article.)
#   Dataset: Olajubu, A. (2024). Dataset for sexual and reproductive health
#   literacy and service utilization among young people in southwest
#   Nigeria. Mendeley Data. https://doi.org/10.17632/783m2r6y6m.1
# Data: SRH Literacy Dataset Publish.sav (1,096 rows x 75 columns; young
#       people aged 15-24 in Osun State: 761 students at two universities and
#       335 out-of-school youths, recruited by convenience within randomly
#       selected faculties/communities). N and the in/out-of-school split
#       match the paper (asserted). Six exact repeated entries are dropped
#       (see the duplicate check below), leaving 1,090 people.
# License: CC BY 4.0 (Mendeley Data API).
#
# Table: olajubu_2024_srh_hlq  HLQ1-HLQ40. The Health Literacy
#   Questionnaire (Osborne et al. 2013) adapted to sexual and reproductive
#   health (e.g. "I feel I have good information about sexual and
#   reproductive health"). Item codes are the source column names.
#   - HLQ1-HLQ23 (Part 1, scales 1-5): 1 strongly disagree .. 4 strongly
#     agree, per the paper and the value labels -> {1..4} asserted.
#   - HLQ24-HLQ40 (Part 2): 1 "Cannot do / always difficult" .. 5 "Always
#     easy", per the paper and the value labels -> {1..5} asserted.
#   The two parts are one instrument with two response formats, so they ship
#   as one table.
#   NOT shipped: HLQ41-HLQ44. The paper describes 44 items (Part 2 = 21),
#   but in this file HLQ41-44 have no variable label and equal HLQ33, HLQ36,
#   HLQ30 and HLQ32 respectively in every row (asserted). They are copies,
#   so the last four Part-2 items' own responses are not in the deposit.
#   (Part 2 therefore has 17 items here rather than 21.)
# Dropped: Coitarche (age at first sex; 999 sentinel), sexual_activity,
#   sexual_partners, school (named university), outofschool_status,
#   type_of_family, own_smartphone and the 14 SRH-service-use flags
#   (srh_info_n_counsel .. others): background and outcome variables, not
#   items of the HLQ. No free-text or date column exists in the file.
# id: row index. ID ("Record ID", 1-1204 with gaps) is not shipped.
# Covariates (value labels): cov_age (years, 15-24), cov_gender (1 female,
#   2 male, 3 others), cov_relationship (1 not in a relationship,
#   2 cohabiting, 3 in a relationship not living together, 4 per labels),
#   cov_religion (1 Christianity, 2 Islam, 3 traditional, 4 others),
#   cov_education (highest schooling: 1 primary, 2 junior secondary,
#   3 senior secondary, 4 technical, 5 commercial/secretarial, 6 NCE,
#   7 polytechnic, 8 university, 9 others, 10 no schooling),
#   cov_in_school (1 in school, 2 out of school), cov_ethnicity (1 Yoruba,
#   2 Igbo, 3 Hausa, 4 others), cov_ever_had_sex (0 no, 1 yes),
#   cov_srh_service_use (ever visited a facility for SRH care: 0 no, 1 yes).
#
# Item text: not shipped. Both label levels are populated: every HLQ1-40
#   column carries its full adapted English stem as a variable label (HLQ41-44
#   are unlabelled), and every item has full value labels. It is cheap, but
#   the HLQ (Swinburne/Deakin, licensed) is awaiting a rights ruling (see
#   automated_finding/TODO.md, "HLQ item text is one rights call away").

import os
import sys
import tempfile
from pathlib import Path

import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = ("https://data.mendeley.com/public-files/datasets/783m2r6y6m/files/"
       "dd143495-5451-44ae-a820-dab9a83d9ff7/file_downloaded")

TABLE = "olajubu_2024_srh_hlq"
PART1 = [f"HLQ{i}" for i in range(1, 24)]
PART2 = [f"HLQ{i}" for i in range(24, 41)]
ITEMS = PART1 + PART2
COPIES = {"HLQ41": "HLQ33", "HLQ42": "HLQ36", "HLQ43": "HLQ30",
          "HLQ44": "HLQ32"}
SERVICES = ["srh_info_n_counsel", "contraceptive", "pregnancy_test",
            "pregnancy_care", "vct", "sti_screening",
            "gynaecological_examination", "post_abortion_care",
            "mother_n_child_health_care", "cervical_cancer_screening",
            "other_cancer_screening", "sexual_dysfuntion",
            "gender_based_violence", "others"]
DROPPED = (set(COPIES) | set(SERVICES)
           | {"ID", "Coitarche", "sexual_activity", "sexual_partners",
              "school", "outofschool_status", "type_of_family",
              "own_smartphone"})
COVS = {"age": "cov_age", "gender": "cov_gender",
        "relationship_status": "cov_relationship", "religion": "cov_religion",
        "educational_status": "cov_education",
        "scholing_status": "cov_in_school", "ethnic_goup": "cov_ethnicity",
        "ever_had_sex": "cov_ever_had_sex",
        "srh_utilization": "cov_srh_service_use"}


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


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    d, meta = load()
    assert d.shape == (1096, 75), d.shape
    known = set(ITEMS) | DROPPED | set(COVS)
    assert set(d.columns) == known, set(d.columns) ^ known
    assert d["ID"].is_unique
    assert d["scholing_status"].value_counts().to_dict() == {1.0: 761,
                                                             2.0: 335}
    # Exact duplicate rows (all 74 non-ID columns equal). Two groups have a
    # varied 40-item pattern and are repeated entries -- IDs 587/590/602/
    # 604/608/762 (six copies) and 773/777 -- so only the first of each is
    # kept. The third pair (14/440) answers 3 to every Part-1 item and 4 to
    # every Part-2 item; a straight-lined pattern can recur by chance, so
    # both are kept.
    body = d.drop(columns="ID")
    groups = d[body.duplicated(keep=False)].groupby(
        list(body.columns), dropna=False)["ID"].apply(sorted).tolist()
    assert sorted(groups) == [[14.0, 440.0], [587.0, 590.0, 602.0, 604.0,
                                              608.0, 762.0], [773.0, 777.0]]
    repeat = d["ID"].isin([590, 602, 604, 608, 762, 777])
    d = d.loc[~repeat]
    assert len(d) == 1090
    for cp, src in COPIES.items():
        assert d[cp].equals(d[src]), cp
        assert not meta.column_names_to_labels.get(cp)
    lab1 = {1.0: "Strongly disagree", 2.0: "Disagree", 3.0: "Agree",
            4.0: "Strongly agree"}
    for c in PART1:
        assert meta.variable_value_labels[c] == lab1, c
    for c in PART2:
        vl = meta.variable_value_labels[c]
        assert sorted(vl) == [1.0, 2.0, 3.0, 4.0, 5.0], c
        assert vl[1.0].startswith("Cannot do"), c

    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    d = d.drop(columns="ID").rename(columns=COVS)
    cov_cols = list(COVS.values())

    long = d.melt(id_vars=["id"] + cov_cols, value_vars=ITEMS,
                  var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    assert (long["resp"] % 1 == 0).all()
    long["resp"] = long["resp"].astype(int)
    pv = {**{i: set(range(1, 5)) for i in PART1},
          **{i: set(range(1, 6)) for i in PART2}}
    for it, g in long.groupby("item"):
        bad = set(g["resp"]) - pv[it]
        assert not bad, (it, bad)
    long = long[["id", "item", "resp"] + cov_cols]
    for c in cov_cols:
        long[c] = long[c].astype("Int64")
    long = long.sort_values(["id", "item"]).reset_index(drop=True)
    assert not long.duplicated(["id", "item"]).any()
    assert long["id"].nunique() >= 100
    assert long["item"].nunique() == len(ITEMS)
    checks = run_qc(long, permitted_values=pv)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    out = OUT_DIR / f"{TABLE}.csv"
    long.to_csv(out, index=False)
    rep = irw_validate.validate_file(str(out), profile="upload",
                                     context={"permitted_values": pv})
    assert rep.conforms and not rep.errors, \
        [(f.check, f.message) for f in rep.errors]
    for f in rep.findings:
        print(f"    [{f.severity}] {f.check}: {f.message}")
    print(f"{TABLE}.csv: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
