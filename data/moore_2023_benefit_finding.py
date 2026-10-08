#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/GNIOTF
# DOI: 10.7910/DVN/GNIOTF (dataset; the record cites no paper DOI)
#   Moore, Jessie (2023). "Benefit finding and well-being over the course of the COVID-19
#   pandemic" [data set], Harvard Dataverse. Stanford WELL for Life participants in
#   California surveyed repeatedly after the March 2020 shelter-in-place order.
# Data: silver_linings_data_feb2022.csv (file 7225267): 701 adults x 355 columns, wide,
#       survey occasions suffixed _t1 .. _t5. No codebook in the deposit.
# License: CC0 1.0 (Dataverse record).
#
# Item text: not shipped. Levels checked: CSV headers only (no labels, no codebook).
#   Headers are short descriptive slugs (who5_cheerful, cov_new_path, core_hopeless), not
#   wording; WHO-5 is blocked in the itemtext rights register.
#
# Tables (wave = the file's occasion suffix t1..t5; id = the file's id):
#   moore_2023_who5         who5_{cheerful,calm,active,fresh,interest}_tN.x, t1-t5, 0-5.
#                           The ".x" columns are the raw answers; the ".y" twins carry
#                           fractional values (0.33, 1.67, ...) at t2-t5, i.e. imputed,
#                           and are skipped.
#   moore_2023_ptgi         the ten Post-Traumatic Growth Inventory short-form items, t2-t5,
#                           1-6 (stored with a "cov_" prefix in the file: cov_change_priority,
#                           cov_appreciation, cov_better_things, cov_spiritual,
#                           cov_closeness, cov_new_path, cov_handle_difficulties,
#                           cov_religious_faith, cov_stronger, cov_wonderful_ppl). Item
#                           codes drop the "cov_" prefix. Coded 1-6 here (the PTGI's 0-5
#                           anchors shifted by one, presumably).
#   moore_2023_well         the 19 WELL for Life survey items (the CFA19 set) (core_hopeless ..
#                           core_overcome_obstacles), t1-t5; 1-5 except core_money_needs
#                           and core_fitness_level (1-6).
# Skipped: the "Unnamed: 0"/X row indices; CFA domain and WELL scores; WHO-5 totals; the
#   ".y" imputed WHO-5 copies; SLQ scores; the distress thermometer (single item);
#   household/shelter-in-place counts and free-text child ages; and the analysis dummies
#   (race_5cat_*, agegroup_*, edu_*, social_*, change_*, *_ALL, SL_prevalence_*, ...).
# Covariates: cov_age (dv_age2020_t0), cov_gender (core_gender_well0, code), cov_income
#   (core_income_well0, code), cov_marital (cov_marital_t0, code), cov_education
#   (dv_edu_5cat_well0, code), cov_race_5cat (code).

import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "moore_2023"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://dataverse.harvard.edu/api/access/datafile/7225267?format=original"

WHO5 = ["cheerful", "calm", "active", "fresh", "interest"]
PTGI = ["change_priority", "appreciation", "better_things", "spiritual", "closeness",
        "new_path", "handle_difficulties", "religious_faith", "stronger", "wonderful_ppl"]
WELL = ["hopeless", "important_energy", "important_time", "overwhelm_difficult", "content",
        "happy", "engage_oppo", "contribute_alive", "contribute_doing", "religious_beliefs",
        "money_needs", "fitness_level", "health_selfreported", "accepting_yourself",
        "satisfied_yourself", "people_rely", "people_talk", "deal_whatever",
        "overcome_obstacles"]
# table -> {item: {wave: source column}}, permitted values per item
TABLES = {
    "moore_2023_who5": ({f"who5_{i}": {w: f"who5_{i}_t{w}.x" for w in range(1, 6)}
                         for i in WHO5}, {f"who5_{i}": range(0, 6) for i in WHO5}),
    "moore_2023_ptgi": ({i: {w: f"cov_{i}_t{w}" for w in range(2, 6)} for i in PTGI},
                        {i: range(1, 7) for i in PTGI}),
    "moore_2023_well": ({f"core_{i}": {w: f"core_{i}_t{w}" for w in range(1, 6)} for i in WELL},
                        {f"core_{i}": range(1, 7 if i in ("money_needs", "fitness_level") else 6)
                         for i in WELL}),
}
COVS = {"dv_age2020_t0": "cov_age", "core_gender_well0": "cov_gender",
        "core_income_well0": "cov_income", "cov_marital_t0": "cov_marital",
        "dv_edu_5cat_well0": "cov_education", "race_5cat": "cov_race_5cat"}


def fetch() -> Path:
    p = RAW_DIR / "data.csv"
    if not p.exists():
        r = requests.get(URL, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def main() -> None:
    d = pd.read_csv(fetch())
    assert d.shape == (701, 355), d.shape
    used = {"id"} | set(COVS)
    for cmap, _ in TABLES.values():
        for waves in cmap.values():
            used |= set(waves.values())
    assert used <= set(d.columns), used - set(d.columns)
    skipped = [c for c in d.columns if c not in used]
    print(f"  skip {len(skipped)} columns: row indices, composites/scores, imputed .y WHO-5 "
          "copies, single items, household counts, analysis dummies")
    assert d["id"].is_unique
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    for c in covs:
        d[c] = d[c].astype("Int64")
    names = list(TABLES)
    assert len(set(names)) == len(names)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (cmap, rng) in TABLES.items():
        frames = []
        for item, waves in cmap.items():
            for w, src in waves.items():
                m = d[["id"] + covs].copy()
                m["item"], m["resp"], m["wave"] = item, d[src], w
                frames.append(m.dropna(subset=["resp"]))
        t = pd.concat(frames)
        assert (t["resp"] % 1 == 0).all(), name
        for it, r in rng.items():
            assert t.loc[t["item"] == it, "resp"].isin(list(r)).all(), (name, it)
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp", "wave"] + covs].sort_values(["id", "wave", "item"])
        t = t.reset_index(drop=True)
        assert not t.duplicated(["id", "item", "wave"]).any() and t["id"].nunique() >= 100
        pv = {i: set(r) for i, r in rng.items()}
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn" and c.name != "dup_id_item":
                print(f"    [qc warn] {c.name}: {c.detail[:200]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": pv})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} items={t['item'].nunique()} "
              f"resp={t['resp'].min()}-{t['resp'].max()} "
              f"ids/wave={t.groupby('wave')['id'].nunique().to_dict()}")


if __name__ == "__main__":
    main()
