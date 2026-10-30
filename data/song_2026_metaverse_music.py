#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0348632
# DOI: 10.1371/journal.pone.0348632
# Paper: Song, Q., Mu, D., Peng, X., & Liu, G. (2026). How metaverse music
#   platform cues shape content creation behavior: evidence from social and
#   flow pathways. PLOS ONE 21(5): e0348632.
# Data: Zenodo 10.5281/zenodo.19046244, "Data.xlsx", 435 rows x 44 columns.
#   Item wording: the article's S2 Appendix, "Measurement items".
#
# LICENCE verified on the DEPOSIT, not the article: the data is hosted
# off-site on Zenodo, which reports license {"id": "cc-by-4.0"} and
# access_right "open".
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30 (BATCH_LOG.md).
#
# ELEVEN output tables, 36 items, 15,660 responses, zero missing cells. The
# paper and the appendix agree: five points, 1 "strongly disagree" to 5
# "strongly agree". 435 Chinese users of metaverse music platforms who had
# used one in the previous 12 months (500 collected, 435 valid).
#
# TEN CONSTRUCTS SHIP WITH THEIR WORDING AND ONE DOES NOT, and the reason is
# a mismatch between the appendix and the deposit that is worth stating
# precisely. S2 Appendix publishes 33 items as eleven constructs of three:
# emotional resonance, aesthetic novelty, social presence, social experience,
# avatar customization, narrativity, multi-sensory, flow experience,
# emotional value perception, technology acceptance, and content creation
# behaviour (CCB1-3). The deposit carries ten of those blocks under the same
# prefixes -- and then a block of SIX called MRCC, where the appendix has
# CCB with three.
#   * The ten matching blocks ship with item text from the appendix.
#   * MRCC ships as all SIX administered items with NO item text. The article
#     says three items were retained per focal construct, so CCB is almost
#     certainly three of these six, but nothing says which three, and
#     shipping three of the appendix's CCB stems against six unlabelled
#     columns would be a guess with a one-in-twenty chance of being right.
#     The six ship because they are what was administered; the table is named
#     for the deposit's own prefix rather than for the article's CCB.
#
# ALL SEVEN COVARIATES SHIP AS THE DEPOSIT'S OWN LABELS, which is rare in
# this batch and removes every pinning problem: the file stores "A. 18-29
# years old", "B. Female", "C. Master's degree", "D. 11-20 times" and so on
# rather than integer codes. The leading letter is kept because it is part of
# the questionnaire's own option labelling, and the S1 Appendix reproduces
# the same options in the same order.
#
# `id` is the deposit's unnamed first column, verified unique over 435 rows.
#
# PII: screened over all 44 columns. The string columns are the seven
# covariates, each a closed vocabulary of 2-5 options; the S1 Appendix
# confirms the survey "collects no direct identifiers".

import os
import re
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("SONGMM_RAW", "zenodo_19046244_Data.xlsx")

N_ROWS = 435
LO, HI = 1, 5

CONSTRUCTS = {
    "ER": ("song_2026_mm_emotional_resonance", 3, "Emotional resonance"),
    "AN": ("song_2026_mm_aesthetic_novelty", 3, "Aesthetic novelty"),
    "SP": ("song_2026_mm_social_presence", 3, "Social presence"),
    "SE": ("song_2026_mm_social_experience", 3, "Social experience"),
    "AC": ("song_2026_mm_avatar_customization", 3, "Avatar customization"),
    "NA": ("song_2026_mm_narrativity", 3, "Narrativity"),
    "MS": ("song_2026_mm_multi_sensory", 3, "Multi-sensory appeal"),
    "FE": ("song_2026_mm_flow_experience", 3, "Flow experience"),
    "EVP": ("song_2026_mm_emotional_value", 3, "Emotional value perception"),
    "TA": ("song_2026_mm_technology_acceptance", 3, "Technology acceptance"),
    "MRCC": ("song_2026_mm_content_creation", 6,
             "Music-related content creation, all six administered items "
             "(the article's CCB is three of these, unidentifiable)"),
}
COVS = {"Age": "cov_age_band", "Gender": "cov_gender",
        "Educational Level": "cov_education",
        "Frequency of general metaverse use": "cov_metaverse_frequency",
        "Frequency of metaverse music platform use": "cov_mm_frequency",
        "Duration of metaverse music platform use": "cov_mm_duration",
        }
PLATFORM = ("Which of the following metaverse music platforms have you used "
            "for music-related activities in the past 12 months?")


def convert():
    df = pd.read_excel(RAW)
    assert len(df) == N_ROWS, len(df)
    cov_src = dict(COVS)
    cov_src[[c for c in df.columns if str(c).startswith(PLATFORM[:40])][0]] = \
        "cov_platform"

    strings = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    assert set(strings) == set(cov_src), sorted(set(strings) ^ set(cov_src))
    for c in strings:
        assert df[c].nunique() <= 6, (c, df[c].nunique())
    print(f"PII screen: {len(strings)} string columns, all of them covariates "
          f"stored as the questionnaire's own option labels (2-5 levels "
          f"each). The S1 Appendix confirms the survey collects no direct "
          f"identifiers")

    blocks = {}
    for c in df.columns:
        m = re.fullmatch(r"([A-Z]+)(\d+)", str(c).strip())
        if m:
            blocks.setdefault(m.group(1), []).append(str(c))
    got = {k: len(v) for k, v in blocks.items()}
    want = {k: v[1] for k, v in CONSTRUCTS.items()}
    assert got == want, f"block counts are {got}, expected {want}"
    assert "CCB" not in blocks, (
        "a CCB block now exists in the deposit -- the article's three "
        "content-creation items may now be identifiable, so revisit the "
        "decision to ship all six MRCC items without text")
    print("10 blocks of 3 match the appendix prefix for prefix; the eleventh "
          "is MRCC with SIX items where the appendix publishes CCB with "
          "three, so MRCC ships whole and without item text")

    id_col = [c for c in df.columns if str(c).startswith("Unnamed")]
    assert len(id_col) == 1, id_col
    accounted = set(id_col) | set(cov_src) | {c for v in blocks.values()
                                              for c in v}
    left_out = [c for c in df.columns if c not in accounted]
    assert not left_out, f"unaccounted source columns: {left_out}"
    assert df[id_col[0]].nunique() == len(df), "the id is not unique"
    df = df.rename(columns={id_col[0]: "id", **cov_src})
    cov_cols = sorted(cov_src.values())

    os.makedirs(OUT_DIR, exist_ok=True)
    total = 0
    for prefix, (name, n, label) in CONSTRUCTS.items():
        cols = sorted(blocks[prefix], key=lambda c: int(re.sub(r"\D", "", c)))
        assert int(df[cols].isna().sum().sum()) == 0, (name, "missing cells")
        vals = pd.to_numeric(df[cols].stack(), errors="coerce")
        assert vals.notna().all() and vals.between(LO, HI).all(), \
            (name, sorted(vals.unique()))

        long = df.melt(id_vars=["id"] + cov_cols, value_vars=cols,
                       var_name="item", value_name="resp")
        long["resp"] = long["resp"].astype(int)
        assert long["id"].nunique() == N_ROWS
        assert long["item"].nunique() == n
        assert not long.duplicated(["id", "item"]).any()
        assert len(name) <= 40, name
        long = long[["id", "item", "resp"] + cov_cols]

        checks = run_qc(long, permitted_values={i: list(range(LO, HI + 1))
                                                for i in cols})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {name} {c.name}: {c.detail[:135]}")

        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        total += len(long)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={n} resp={long['resp'].min()}-{long['resp'].max()}  "
              f"[{label[:46]}]")

    assert total == 36 * N_ROWS, total
    print(f"11 tables, {total} responses (36 items x {N_ROWS} respondents)")


if __name__ == "__main__":
    convert()
