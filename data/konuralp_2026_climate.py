#!/usr/bin/env python3
# Source: https://zenodo.org/records/20734378
# DOI: none recorded on the deposit (no related identifiers).
#   Konuralp, E. (2026). "igdir_survey_data." Zenodo.
# Data: Zenodo 20734378, "igdir_survey_data.csv" (532 rows x 48 columns;
#       university students in Iğdır, Türkiye) plus
#       "igdir_survey_codebook.csv" (48 rows: variable, original_label,
#       coding) -- a real codebook, which is why the drops below are
#       documented rather than inferred.
# License: CC BY 4.0 (Zenodo record metadata, API).
#
# Item text: NOT shipped. The codebook carries the administered TURKISH stem
#   in `original_label` for the demographics, the six party-evaluation items
#   and the standalone questions -- but for the 20 Likert items of the main
#   battery `original_label` is just the code again ("CB4" -> "CB4"), so
#   those stems are nowhere in the deposit. For the party block the Turkish
#   IS in hand, and itemtext_standard.md then requires the English in the
#   parallel _translated fields; the authors ship no English, so it would be
#   IRW-generated and owes a translation_source plus a public issues-page
#   callout. Same position as the Indonesian deposits in this batch -- one
#   deliberate translation round, not bolted onto a response batch.
#
# KNOWLEDGE ITEMS NOT SHIPPED (kq1-kq10), and the attempt is worth recording
#   so nobody repeats it. They are multiple-choice climate-knowledge items
#   held as RAW OPTION CODES (kq1 1-3, kq3 1-5, ...), which are unordered,
#   so they fail datastandard.md's "at least ordinal" requirement for `resp`
#   and are a nominal-standard candidate (3+ unordered categories), not core.
#   The codebook says "correct answers counted in awareness_score" but never
#   gives the key. awareness_score is a 0-10 count, so the key is in
#   principle recoverable: 10 unknowns against 532 equations. It is not.
#   A greedy fit reproduces 253 of 532 rows, and an exhaustive search over
#   all 691,200 single-correct-option combinations finds NO key that
#   reproduces every row -- so awareness_score is not a plain row-sum of ten
#   single-key items (multiple accepted answers, or a scoring step the
#   codebook does not describe). Without the key the block cannot be scored,
#   and awareness_score itself is a composite.
#
# Tables:
#   konuralp_2026_climate_attitudes  20 items, CB1-CB6 (environmental
#       consciousness), CA1-CA10 (political response), MS1-MS2 (media
#       scepticism), PD1-PD2 (administrative performance), 1-5. One table:
#       one response format, one matrix; the four prefixes are the paper's
#       constructs per the codebook, so multi_scale is expected.
#   konuralp_2026_party_environment  6 items, party_AKP/CHP/MHP/IYI/DEM/SP,
#       1-3 (1 = favourable .. 3 = unfavourable per the codebook) -- one
#       question stem asked about six parties, which is an item block.
#
# Dropped, with reasons:
#   id                     -> becomes `id`
#   kq1-kq10               see KNOWLEDGE ITEMS above
#   awareness_score        composite (count of correct answers)
#   winter_air_quality, trust_promises   single standalone 1-5 questions,
#       not a block
#   health_effects_known (1-3 yes/no/unsure), top_env_problem (1-7 choose
#       one) -- unordered single questions
#   region_origin          free text
#   gender, age, faculty, education, income -> cov_*
# id: the file's own `id` column.
# Covariates: cov_gender (1 woman, 2 man), cov_age (years), cov_faculty
#   (code), cov_education (1 associate, 2 undergraduate), cov_income_band
#   (1 lowest .. 5 highest) -- all per the codebook.

import io
import re
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
BASE = "https://zenodo.org/api/records/20734378/files/"
COVS = {"gender": "cov_gender", "age": "cov_age", "faculty": "cov_faculty",
        "education": "cov_education", "income": "cov_income_band"}
PARTIES = ["party_AKP", "party_CHP", "party_MHP", "party_IYI", "party_DEM",
           "party_SP"]
SINGLES = ["awareness_score", "winter_air_quality", "health_effects_known",
           "top_env_problem", "trust_promises", "region_origin"]


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(BASE + "igdir_survey_data.csv/content", headers=UA,
                     timeout=300)
    r.raise_for_status()
    d = pd.read_csv(io.BytesIO(r.content))
    assert d.shape == (532, 48), d.shape

    likert = [c for c in d.columns if re.fullmatch(r"(CB|CA|MS|PD)\d+", c)]
    kq = [c for c in d.columns if re.fullmatch(r"kq\d+", c)]
    assert len(likert) == 20 and len(kq) == 10, (len(likert), len(kq))

    known = set(likert) | set(kq) | set(PARTIES) | set(SINGLES) | set(COVS) | {"id"}
    assert set(d.columns) == known, set(d.columns) ^ known
    for c in kq:
        print(f"[drop] {c}  raw MC option code, no key recoverable")
    for c in SINGLES:
        print(f"[drop] {c}")
    print(f"[cols] {len(likert)} Likert + {len(PARTIES)} party items, "
          f"{len(COVS)} covariates, {len(kq) + len(SINGLES) + 1} dropped")

    assert d["id"].is_unique and d["id"].notna().all()
    d = d.rename(columns=COVS)
    cov_cols = list(COVS.values())
    for c in cov_cols:
        d[c] = pd.to_numeric(d[c], errors="coerce").astype("Int64")

    def build(table, items, allowed, order=None):
        cols = order or sorted(items)
        long = d.melt(id_vars=["id"] + cov_cols, value_vars=cols,
                      var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long["resp"] = long["resp"].astype(int)
        for it, g in long.groupby("item"):
            bad = set(g["resp"]) - allowed
            assert not bad, (table, it, bad)
        long = long[["id", "item", "resp"] + cov_cols]
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        assert not long.duplicated(["id", "item"]).any()
        assert long["item"].nunique() == len(cols)
        checks = run_qc(long, permitted_values={c: allowed for c in cols})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (table, fails)
        for c in checks:
            if c.status == "warn":
                print(f"  [warn] {table}: {c.name}: {c.detail[:120]}")
        (OUT_DIR / f"{table}.csv").write_text(long.to_csv(index=False))
        print(f"[write] {table}: {len(long)} responses, "
              f"{long['id'].nunique()} ids x {long['item'].nunique()} items")
        return len(long)

    t = 0
    t += build("konuralp_2026_climate_attitudes", likert, {1, 2, 3, 4, 5},
               order=sorted(likert, key=lambda c: (re.match(r"[A-Z]+", c).group(),
                                                   int(re.search(r"\d+", c).group()))))
    t += build("konuralp_2026_party_environment", PARTIES, {1, 2, 3},
               order=PARTIES)
    print(f"[total] {t} responses across 2 tables")


if __name__ == "__main__":
    main()
