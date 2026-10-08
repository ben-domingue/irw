#!/usr/bin/env python3
# Source: https://zenodo.org/records/22829237
# DOI: 10.5281/zenodo.22829237 (dataset; no paper DOI on the record)
#   Belyakova, Alina, Shonbay, Kuanysh & Karibayeva, Indira (2026). "Dataset for
#   Big Five Personality, Dispositional Mindfulness and Meaning in Life in
#   Russian-Speaking Adults" [data set]. Zenodo.
# Data: mindfulness_meaning_kz_items.csv: 147 Russian-speaking adults (18-60) in
#       Kazakhstan, online 2025 x pid, five recoded demographics, bfi1-30 (BFI-2-S,
#       Russian), pil1-20 (Russian Purpose-in-Life / Life-Meaning Orientations
#       test), maas1-15 (MAAS), duplicate_flag, duplicate_of. codebook.csv documents
#       every column (instrument, domain/subscale, range, keying).
# License: CC BY 4.0 (Zenodo record).
#
# Item text: not shipped. Levels checked: CSV headers are codes; codebook.csv labels
#   are positional ("BFI-2-S item 1 -- Extraversion", "PIL item 2 -- subscale(s):
#   Process", "MAAS item 4 -- ... Attention distribution") with ranges and keying
#   only. The Russian wording is not in the deposit (BFI-2 forms are blocked in the
#   rights register in any case).
#
# Tables (raw responses as recorded; reverse-keyed items NOT reversed -- the codebook
# lists keying per item):
#   belyakova_2026_bfi2s  bfi1-30   1 = disagree strongly ... 5 = agree strongly
#   belyakova_2026_pil    pil1-20   1-7 bipolar scale as recorded in the survey
#   belyakova_2026_maas   maas1-15  1 = almost always ... 6 = almost never
# Duplicates: the 4 rows with duplicate_flag = 1 (codebook: "same contact e-mail and
#   identical responses to all 65 items but different age group") are dropped, so
#   N = 143; the paper's analyses retained them (N = 147).
# Covariates (strings, as released): cov_age_group, cov_sex, cov_education,
#   cov_family_status, cov_occupation. id = the numeric part of pid (P001-P147).

import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "belyakova_2026"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
BASE = "https://zenodo.org/api/records/22829237/files/"
FILES = ["mindfulness_meaning_kz_items.csv", "codebook.csv"]
TABLES = {"belyakova_2026_bfi2s": ([f"bfi{i}" for i in range(1, 31)], range(1, 6)),
          "belyakova_2026_pil": ([f"pil{i}" for i in range(1, 21)], range(1, 8)),
          "belyakova_2026_maas": ([f"maas{i}" for i in range(1, 16)], range(1, 7))}
COVS = {"age_group": "cov_age_group", "sex": "cov_sex", "education": "cov_education",
        "family_status": "cov_family_status", "occupation": "cov_occupation"}


def fetch() -> Path:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for f in FILES:
        p = RAW_DIR / f
        if not p.exists():
            r = requests.get(BASE + f + "/content", headers=UA, timeout=300)
            r.raise_for_status()
            p.write_bytes(r.content)
    return RAW_DIR / FILES[0]


def main() -> None:
    d = pd.read_csv(fetch())
    cb = pd.read_csv(RAW_DIR / FILES[1])
    assert d.shape == (147, 73) and cb["variable"].tolist() == d.columns.tolist()
    items = [c for its, _ in TABLES.values() for c in its]
    assert set(d.columns) == {"pid", "duplicate_flag", "duplicate_of"} | set(items) | set(COVS)
    dup = d["duplicate_flag"] == 1
    print(f"  dropped {dup.sum()} flagged duplicate submission(s): {d.loc[dup, 'pid'].tolist()}")
    assert dup.sum() == 4
    d = d[~dup].copy()
    d["id"] = d["pid"].str.extract(r"^P(\d{3})$")[0].astype(int)
    assert d["id"].is_unique
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (its, rng) in TABLES.items():
        t = d.melt(id_vars=["id"] + covs, value_vars=its, var_name="item",
                   value_name="resp").dropna(subset=["resp"])
        assert t["resp"].isin(list(rng)).all(), name
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
        assert set(t["item"]) == set(its) and not t.duplicated(["id", "item"]).any()
        assert t["id"].nunique() >= 100
        pv = {i: set(rng) for i in its}
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
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
