#!/usr/bin/env python3

# Source: https://zenodo.org/records/7840114
# DOI: 10.5281/zenodo.7840114
#   Cornelia Mairean (2023). Quality of life among Romanian Emergency Medicine
#   Personnel [Dataset]. Zenodo.
# Data: "database.sav" -- 372 Romanian emergency-medicine staff.
# License: CC BY 4.0 (verified on the Zenodo record).
# Item text: NOT shipped. Both label levels checked: 10 of 51 variables carry a
#   variable label and they are one-word Romanian topic tags ("siguranta",
#   "sanatate", "economic") rather than stems; 2 carry value labels, both
#   demographics. No usable item wording in the file.
# Naming: mairean_2023_childhood_trauma and mairean_2023_conspiracy_dogmatism are
#   already shipped, so this 2023 deposit takes mairean_2023c_*.
#
# THREE tables, all 1-5:
#   mairean_2023c_threat_covid       3 items (covid1-3). The variable labels tag
#                                    them siguranta / sanatate / economic -- safety,
#                                    health and economic threat from COVID-19.
#   mairean_2023c_threat_geopolitic  4 items (geopolitic1-4), the same threat frame
#                                    applied to the geopolitical situation. Kept as
#                                    its own table rather than merged with the COVID
#                                    block: they are different referents, and
#                                    geopolitic has a fourth item the COVID block
#                                    has no counterpart for.
#   mairean_2023c_proqol            30 items (pro1-pro30). This is the PROFESSIONAL
#                                    QUALITY OF LIFE SCALE (ProQOL), not a generic
#                                    prosocial measure -- identified from the three
#                                    derived scores the deposit ships alongside it
#                                    (compassion_satisfaction, STS, Burnout), which
#                                    are the ProQOL's three 10-item subscales. The
#                                    block was nearly mislabelled "prosocial" on the
#                                    strength of its pro* prefix alone.
# ProQOL RIGHTS. The ProQOL (Stamm, proqol.org) has NO row in
#   itemtext/instrument_rights_register.csv, and its own terms allow free use
#   unmodified with credit but not sale. It is flagged in this batch's TODO as a
#   register-row request. The response table ships because nothing restricted is
#   exposed by it: the item codes are the deposit's positional pro1..pro30, which
#   reveal no wording, and NO item text is shipped. If a later ruling blocks the
#   ProQOL, this table is what a withdrawal would target.
# Not shipped: razboi_neliniste / razboi_teama / razboi_financiar / razboi_siguranta
#   (four single war-related questions, not a scale with a shared format),
#   amenintare_covid (a derived threat score), and the demographics that become
#   covariates.
# id: the file carries no respondent id; the 0-based row index is used.
# Covariates: cov_gender, cov_age, cov_experience, cov_profession.
# Rights: none of the three is in the instrument rights register; the threat items
#   are the author's own and the pro* block is a prosocial-behaviour scale with no
#   register row. Checked against the register's block list by hand, since its code
#   matchers reach only a minority of its rows.
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
    "IRW_RAW_DIR", REPO_ROOT / "automated_finding" / "runs" / "b5_raw" / "7840114"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
RECORD, FNAME = 7840114, "database.sav"

COVS = {"gen": "cov_gender", "varsta": "cov_age",
        "experienta": "cov_experience", "profesie": "cov_profession"}
BLOCKS = {
    "mairean_2023c_threat_covid": [f"covid{i}" for i in range(1, 4)],
    "mairean_2023c_threat_geopolitic": [f"geopolitic{i}" for i in range(1, 5)],
    "mairean_2023c_proqol": [f"pro{i}" for i in range(1, 31)],
}
# Four standalone war-worry questions, plus every derived score: the two threat
# sums, the worry sum, and the ProQOL's three subscale sums.
SKIP = ["razboi_neliniste", "razboi_teama", "razboi_financiar",
        "razboi_siguranta", "amenintare_covid", "amenintare_razboi",
        "ingrijorari", "compassion_satisfaction", "STS", "Burnout"]
SCALE = set(range(1, 6))


def fetch() -> Path:
    p = RAW_DIR / FNAME
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        j = requests.get(f"https://zenodo.org/api/records/{RECORD}",
                         headers=UA, timeout=120).json()
        url = [f["links"]["self"] for f in j["files"] if f["key"] == FNAME][0]
        r = requests.get(url, headers=UA, timeout=300)
        r.raise_for_status()
        p.write_bytes(r.content)
    return p


def main():
    df, meta = pyreadstat.read_sav(str(fetch()), apply_value_formats=False)
    df.insert(0, "id", range(len(df)))
    items = {c for cols in BLOCKS.values() for c in cols}
    accounted = {"id"} | set(COVS) | items | set(SKIP)
    unaccounted = [c for c in df.columns if c not in accounted]
    assert not unaccounted, f"unaccounted source columns: {unaccounted}"
    for c in SKIP:
        print(f"  skipped {c}: standalone question or derived score, not part "
              f"of a shared-format block")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    written = []
    for name, cols in BLOCKS.items():
        t = (df[["id", *COVS, *cols]]
             .melt(id_vars=["id", *COVS], value_vars=cols,
                   var_name="item", value_name="resp")
             .dropna(subset=["resp"])
             .rename(columns=COVS))
        assert (t["resp"] % 1 == 0).all(), f"{name}: fractional resp"
        t["resp"] = t["resp"].astype(int)
        bad = sorted(set(t["resp"]) - SCALE)
        assert not bad, f"{name}: resp outside the observed 1-5 scale: {bad}"
        for c in COVS.values():
            v = pd.to_numeric(t[c], errors="coerce")
            # cov_experience is recorded in fractional years for some staff, so
            # only the integral covariates become Int64.
            t[c] = v.astype("Int64") if (v.dropna() % 1 == 0).all() else v
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
