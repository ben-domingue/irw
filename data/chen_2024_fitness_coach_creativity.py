"""Chen (2024), Zenodo -- curiosity, sport commitment, knowledge sharing, flow
and creativity among Chinese fitness coaches.

Source: https://zenodo.org/records/13855427
DOI: 10.5281/zenodo.13855427
Data: 2024929健身教练数据(Peerj).sav
License: CC BY 4.0
Item text: not shipped -- the .sav has no value labels and only one stray
    variable label (`TS1` = "thrillseeking 需求刺激"). The wording is in the
    PeerJ article this deposit backs, which is open access; a later pass with
    the paper in hand could recover all 74 stems.

732 fitness coaches, every item on a 1-7 agreement format.

Tables written (one per source column prefix, 16 in all)
--------------------------------------------------------
chen_2024_je 5, chen_2024_ds 5, chen_2024_sc 5, chen_2024_ts 5,
chen_2024_ec 6, chen_2024_cc 5, chen_2024_spe 5, chen_2024_kc 4,
chen_2024_kd 4, chen_2024_uf 4, chen_2024_cg 4, chen_2024_cotah 4,
chen_2024_tot 4, chen_2024_ae 4, chen_2024_cr 9, chen_2024_smu 5

Coding notes
------------
* The tables are split on the source column prefixes, which are the only
  grouping the deposit supplies. The abbreviations are not expanded here:
  `TS` is confirmed as thrill seeking by its one variable label, and JE/DS/SC/
  TS read as four of the Five-Dimensional Curiosity Scale's subscales, but the
  fifth (stress tolerance) is absent and the remaining eleven prefixes have
  nothing in the deposit to decode them. Naming them on a guess would put an
  invented construct in the dictionary; the prefix is what the source says.
* **The scale is 1-7, not the 1-6 most items reach.** Only `AE2` is observed at
  7, but every one of the sixteen aggregate columns the deposit also ships
  (`JE`, `DS`, ... `SMU` -- block means) has a maximum of exactly 7.0, which is
  only reachable if the item scale runs to 7. The blocks are one left-skewed
  1-7 format, so no table is split on observed maxima.
* Dropped as derived: the sixteen block-mean columns named exactly like their
  prefixes (`JE`, `DS`, `SC`, `TS`, `EC`, `CC`, `SPE`, `KC`, `KD`, `UF`, `CG`,
  `COTAH`, `TOT`, `AE`, `CR`, `SMU`).
* Covariates: `cov_gender`, `cov_age_band` (1-6), `cov_seniority` (1-5),
  `cov_monthly_income` (1-5). All four are the questionnaire's own banded
  codes; the deposit does not publish the band boundaries.
* `id` is the deposit's own `ord`, 1-732, one row per coach.
"""

import os
import re
import sys

import pandas as pd
import pyreadstat
import requests

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "automated_finding"))
from irw_triage_updated import run_qc          # noqa: E402

AF = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                  "automated_finding")
OUTDIR = os.path.join(AF, "irw_output")
REC = "13855427"
FILENAME = "2024929健身教练数据(Peerj).sav"
PREFIXES = ["JE", "DS", "SC", "TS", "EC", "CC", "SPE", "KC", "KD", "UF",
            "CG", "COTAH", "TOT", "AE", "CR", "SMU"]
COVS = {"Gender": "cov_gender", "Age": "cov_age_band",
        "Seniority": "cov_seniority", "Monthly": "cov_monthly_income"}


def load():
    path = os.path.join("/tmp", f"zenodo_{REC}.sav")
    if not os.path.exists(path):
        api = requests.get(f"https://zenodo.org/api/records/{REC}",
                           timeout=60).json()
        url = next(f["links"]["self"] for f in api["files"]
                   if f["key"] == FILENAME)
        with requests.get(url, stream=True, timeout=600) as r:
            r.raise_for_status()
            with open(path, "wb") as fh:
                for chunk in r.iter_content(1 << 20):
                    fh.write(chunk)
    df, _ = pyreadstat.read_sav(path)
    return df


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    d = load()
    assert len(d) == 732, len(d)
    d = d.rename(columns={"ord": "id"})

    # the aggregate columns are exactly the prefixes; they are what establishes
    # the 1-7 ceiling, so assert that before dropping them
    for p in PREFIXES:
        assert d[p].max() == 7.0, (p, d[p].max())

    blocks = {}
    for c in d.columns:
        m = re.match(r"^([A-Z]+)(\d+)$", c)
        if m and m.group(1) in PREFIXES:
            blocks.setdefault(m.group(1), []).append(c)
    assert sorted(blocks) == sorted(PREFIXES), sorted(blocks)

    shipped, total, names = set(), 0, []
    for p in PREFIXES:
        cols = sorted(blocks[p], key=lambda c: int(re.sub(r"\D", "", c)))
        shipped.update(cols)
        long = d[["id"] + cols + list(COVS)].melt(
            id_vars=["id"] + list(COVS), value_vars=cols,
            var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"]).rename(columns=COVS)
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + list(COVS.values())]

        assert long["resp"].between(1, 7).all()
        assert not long.duplicated(["id", "item"]).any()
        assert long["id"].nunique() >= 100
        assert long["item"].nunique() >= 2
        checks = run_qc(long)
        bad = [c for c in checks if c.status == "fail"]
        assert not bad, (p, [(c.name, c.detail) for c in bad])

        name = f"chen_2024_{p.lower()}"
        assert name not in names, name
        names.append(name)
        path = os.path.join(OUTDIR, f"{name}.csv")
        assert not os.path.exists(path), name
        long.to_csv(path, index=False)
        total += len(long)
        print(f"{name}: {long['id'].nunique()} coaches x "
              f"{long['item'].nunique()} items = {len(long)} responses")

    for c in d.columns:
        assert (c == "id" or c in shipped or c in COVS or c in PREFIXES), (
            f"unaccounted source column: {c}")
    print(f"\n{len(names)} tables, {total:,} responses "
          f"({len(shipped)} items); dropped {len(PREFIXES)} block-mean columns")


if __name__ == "__main__":
    main()
