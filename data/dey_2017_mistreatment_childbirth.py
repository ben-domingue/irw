#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/MTBJ98
# DOI: 10.1186/s12978-017-0409-z
#   Dey, A., Shakya, H. B., Chandurkar, D., Kumar, S., Das, A. K., Anthony, J., Shetye, M.,
#   Krishnan, S., Silverman, J. G., & Raj, A. (2017). Discordance in self-report and
#   observation data on mistreatment of women by providers during childbirth in Uttar
#   Pradesh, India. Reproductive Health, 14, 149.
# Data: Harvard Dataverse 10.7910/DVN/MTBJ98 (Dey, Arnab; 2017-07-20). Mistreatment_data-UP.dta
#       (file 3037220, format=original) -- 875 deliveries observed in 81 public facilities
#       in Uttar Pradesh (April-August 2016), followed up in the community: ten mistreatment
#       items recorded by a trained observer during the delivery (obs_*) and 28 self-reported
#       by the woman afterwards (sr_*), each 0 No / 1 Yes, with the .dta variable labels
#       naming each item; plus woman, delivery and provider characteristics.
#       The identical deposit DVN/GLXDPR (Dehingia, Nabamallika; same file, same size) is a
#       duplicate and is not processed separately.
# License: CC0 1.0 (Dataverse record).
#
# Item text: not shipped. The .dta variable labels give a short English description of each
#   item at the variable-label level ("Beaten/slapped by health care provider - Observed")
#   and value labels No/Yes on most items; these are coder descriptions rather than the
#   questionnaire wording, and the questions were asked in Hindi. The instrument is not
#   deposited.
#
# Tables (0/1, 1 = the mistreatment/event occurred):
#   dey_2017_mistreatment_observed   obs_beat .. obs_deniedcompany (9)
#   dey_2017_mistreatment_selfreport sr_beat .. sr_anyonepresent (28)
# Skipped: obs_anymistreat, sr_anymistreat_common, sr_anymistreat_halpha (any-item
#   indicators), ureport (derived concordance flag).
# cluster_id: facilityid (the delivery facility, 81).
# Covariates: cov_nurse_mentored (facility), cov_age, cov_age_at_marriage, cov_literate,
#   cov_religion (0/1 as stored), cov_sli_quintile (standard-of-living index quintile),
#   cov_delivery_problem, cov_postdelivery_problem, cov_newborn_problem, cov_caste
#   (1 SC/ST/OBC, 2 general), cov_parity (1 single, 2 multiparous), cov_stay_48h,
#   cov_nurse_age, cov_nurse_experience, cov_nurse_sba_trained.
# id: row index (one delivery per woman; no identifier in the file).

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
RAW_DIR = Path(os.environ.get("IRW_RAW_DIR",
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "mtbj98"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://dataverse.harvard.edu/api/access/datafile/3037220?format=original"
P = "dey_2017_"
RANGE = range(0, 2)
COVS = {"nm_facility": "cov_nurse_mentored", "womanage": "cov_age",
        "age_at_marriage": "cov_age_at_marriage", "momlit": "cov_literate",
        "religion": "cov_religion", "sli_q": "cov_sli_quintile",
        "del_problem": "cov_delivery_problem", "postdel_problem": "cov_postdelivery_problem",
        "nb_prob": "cov_newborn_problem", "caste2": "cov_caste", "parity2": "cov_parity",
        "stay_48": "cov_stay_48h", "sn_age": "cov_nurse_age",
        "sn_years_exp": "cov_nurse_experience", "sn_sba_trained": "cov_nurse_sba_trained"}
SKIP = {"obs_anymistreat", "sr_anymistreat_common", "sr_anymistreat_halpha", "ureport"}


def fetch() -> Path:
    p = RAW_DIR / "data.dta"
    if not p.exists():
        r = requests.get(URL, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def main() -> None:
    d, _ = pyreadstat.read_dta(str(fetch()))
    assert d.shape == (875, 57)
    obs = [c for c in d.columns if c.startswith("obs_") and c not in SKIP]
    sr = [c for c in d.columns if c.startswith("sr_") and c not in SKIP]
    assert len(obs) == 9 and len(sr) == 28
    TABLES = {"mistreatment_observed": obs, "mistreatment_selfreport": sr}
    items = obs + sr
    accounted = set(items) | set(COVS) | SKIP | {"facilityid"}
    assert accounted == set(d.columns), set(d.columns) ^ accounted
    print(f"  [skip] {sorted(SKIP)}: any-item indicators / derived")
    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    d = d.rename(columns={"facilityid": "cluster_id", **COVS})
    d["cluster_id"] = d["cluster_id"].astype(int)
    covs = ["cluster_id"] + list(COVS.values())
    for c in COVS.values():
        if (d[c].dropna() % 1 == 0).all():
            d[c] = d[c].astype("Int64")
    names = [P + k for k in TABLES]
    assert len(set(names)) == len(names) and max(map(len, names)) <= 40
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    total = 0
    for k, its in TABLES.items():
        name = P + k
        t = d.melt(id_vars=["id"] + covs, value_vars=its, var_name="item",
                   value_name="resp").dropna(subset=["resp"])
        assert t["resp"].isin(RANGE).all(), name
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
        assert set(t["item"]) == set(its) and not t.duplicated(["id", "item"]).any()
        assert t["id"].nunique() >= 100
        pv = {i: set(RANGE) for i in its}
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {c.name}: {c.detail[:200]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": pv})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        for f in report.warnings:
            print(f"    [validate warn] {f.check}: {f.message[:160]}")
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        total += len(t)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")
    assert total == int(d[items].notna().sum().sum()), "books do not balance"


if __name__ == "__main__":
    main()
