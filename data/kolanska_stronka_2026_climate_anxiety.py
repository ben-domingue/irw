#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/31331989
# DOI: 10.6084/m9.figshare.31331989.v1 (dataset; no paper DOI on the record)
#   Kolanska-Stronka, Magdalena (2026). "Data on Climate Anxiety, General Self-Efficacy
#   and Coping Strategies" [data set]. figshare.
# Data: date.sav: 375 Polish adults (18-90) x CA_1-13, GSES_1-10, COPE_1-28, Age, Sex,
#       Polish-labelled education / marital status / place-of-residence codes, a
#       free-text voivodeship, subscale sums and a 3-level residence recode. No variable
#       labels on the items, no value labels on the items; no codebook in the deposit.
# License: CC BY 4.0 (figshare record).
#
# Item text: not shipped. Levels checked: .sav variable labels empty on CA/GSES/COPE
#   items, value labels absent on them; the Polish wording is not in the deposit.
#
# Tables (instrument identities from the record title and the sum columns: CAS_sum with
#   cognitive / functional subscales = the 13-item Climate Anxiety Scale; GSES_sum; the
#   COPE sums Religion, Acceptance, Humor, Active_Coping, Helplessness, Support_Seeking,
#   Avoidance over 28 items = the Brief COPE / Polish Mini-COPE, scored 0-3):
#   kolanska_stronka_2026_climate_anxiety  CA_1-13    1-5
#   kolanska_stronka_2026_gses             GSES_1-10  1-4
#   kolanska_stronka_2026_mini_cope        COPE_1-28  0-3
# Dropped cells (isolated entry errors, each value occurs once or twice in the whole
#   file and on no other item): one respondent's 0s on CA_1/5/6/7/8 and on
#   GSES_1/2/5 (below the scale minimum), GSES_10 = 5, COPE_1 = 4 (x2), COPE_24 = 8.
# Not shipped: CAS_*/GSES_sum/COPE_* sums; Residence_place (recode of the 5-level
#   residence code); wojewodztwo (free-text region with mixed spellings and stray codes).
# Covariates: cov_age, cov_sex (1 woman, 2 man), cov_education (1 podstawowe, 2 srednie,
#   3 zawodowe, 4 studia, 5 wyzsze), cov_marital (1 partnerstwo, 2 malzenstwo, 3 wolny,
#   4 wdowiec), cov_residence (1 village, 2 town <50k, 3 50-150k, 4 150-500k, 5 >500k;
#   per the variable label). id = row index.

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
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "kolanska_stronka_2026"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://ndownloader.figshare.com/files/61873945"
P = "kolanska_stronka_2026_"
TABLES = {P + "climate_anxiety": ([f"CA_{i}" for i in range(1, 14)], range(1, 6)),
          P + "gses": ([f"GSES_{i}" for i in range(1, 11)], range(1, 5)),
          P + "mini_cope": ([f"COPE_{i}" for i in range(1, 29)], range(0, 4))}
COVS = {"Age": "cov_age", "Sex": "cov_sex",
        "wykształcenie1podstawowe2srednie3zawodowe4studia5wyższe": "cov_education",
        "stancywilny1partnerstwo2małżenstwo3wolny4wdowiec": "cov_marital",
        "miejscezamieszkania1wieś2miastodo50tys3miasto501504miasto150500": "cov_residence"}


def fetch() -> Path:
    p = RAW_DIR / "date.sav"
    if not p.exists():
        r = requests.get(URL, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def main() -> None:
    d, _ = pyreadstat.read_sav(str(fetch()))
    assert d.shape == (375, 69)
    items = {c for its, _ in TABLES.values() for c in its}
    skipped = [c for c in d.columns if c not in items | set(COVS)]
    print(f"  [skip] {len(skipped)} columns (sums, recode, free-text region): {skipped}")
    d.insert(0, "id", range(1, len(d) + 1))
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (its, rng) in TABLES.items():
        t = d.melt(id_vars=["id"] + covs, value_vars=its, var_name="item",
                   value_name="resp").dropna(subset=["resp"])
        bad = ~t["resp"].isin(list(rng))
        print(f"  {name}: dropped {bad.sum()} out-of-range cell(s): "
              f"{t.loc[bad, ['item', 'resp']].values.tolist()}")
        assert bad.sum() <= 9
        t = t[~bad]
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
        assert set(t["item"]) == set(its) and not t.duplicated(["id", "item"]).any()
        pv = {i: set(rng) for i in its}
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {c.name}: {c.detail[:160]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": pv})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
