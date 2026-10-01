#!/usr/bin/env python3
# Source: https://osf.io/baues/  (RAW data/responses.csv
#   https://osf.io/download/9c68k/, RAW data/participants.csv
#   https://osf.io/download/jcuqb/, codebook RAW data/codes.txt)
# Paper DOI: 10.3758/s13428-026-02976-4
#   Martínez-Tomás, C., Guasch, M., Ferré, P., Lázaro, M., & Hinojosa, J. A.
#   (2026). When the meaningless make sense: Wordlikeness and affective norms
#   for 4,800 pseudowords and 1,200 Spanish words. Behavior Research Methods,
#   58(4), 103.
# Data DOI: none (OSF node baues)
# License: CC0 1.0 (OSF node baues, "CC0 1.0 Universal", checked on the OSF API
#   2026-09-27).
#
# Table: martineztomas_2026_pseudowords -- a stimulus-rating (norming) study.
#   Encoded the settled IRW way for rating studies with more than one rating
#   dimension (KalimahNorms_alzahrani_2025, emoji_scheffler_2024): the
#   STIMULUS is on `id`, the rating dimension is the `item`, and the human who
#   rated is in `rater`.
#     id    = the 6,000 stimuli (source id_item, e.g. "985c"), as integers
#     item  = valence (1-9), arousal (1-9), wordlikeness (1-7)
#     rater = the participant's unique_participant_code, as integers (the code
#             itself is not carried). A code links the questionnaires one
#             person completed (1,210 raters, 2,348 questionnaires); each
#             questionnaire is one dimension x one 240-stimulus list.
#   Each stimulus x dimension has 25-47 ratings (mean 31).
#   cov_stimulus is the rated letter string; cov_stimulus_type is the codebook's
#   condition letter (a base word; b root + suffix; c root + pseudo-suffix;
#   d pseudo-root + suffix; e pseudo-root + pseudo-suffix); cov_set is the
#   numeric part of id_item, which ties a base word to its four pseudowords;
#   cov_list is the rated list (1-25).
#   RAW data are used ("No cleaning or preprocessing has been applied"). The
#   authors' trimming (script 1: raters with >= 95% identical responses or a
#   low correlation with the group are dropped) is NOT applied; it is a quality
#   screen a user can reproduce from the rater column. One questionnaire's
#   list number differs between participants.csv and responses.csv; the
#   response file's value is kept.
# Rater age and sex are rater-level and not carried.
#
# One table although the dimensions use different scales (Ben 2026-10-01,
# irw#1443): irw-validate's `resp_scale_constructs` refusal is waived for this
# table only, recorded in processing_notes/validator_overrides.csv. Every other
# check must still pass, and the asserts below enforce that.

import sys
import time
from io import BytesIO
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RESP_URL = "https://osf.io/download/9c68k/"
PART_URL = "https://osf.io/download/jcuqb/"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
NAME = "martineztomas_2026_pseudowords"
DIMS = {1: "valence", 2: "arousal", 3: "wordlikeness"}


def fetch(url: str) -> bytes:
    for attempt in range(5):
        r = requests.get(url, headers=UA, timeout=300)
        if r.status_code == 200 and len(r.content) > 1000:
            return r.content
        time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"{url} failed after 5 attempts")


def convert() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = pd.read_csv(BytesIO(fetch(RESP_URL)), sep=";")
    p = pd.read_csv(BytesIO(fetch(PART_URL)), sep=";")
    assert r.shape == (563520, 8) and p.shape == (2348, 6), (r.shape, p.shape)
    assert p["id_participant"].is_unique
    assert (r.groupby("id_participant").size() == 240).all()
    assert r["id_item"].nunique() == 6000
    assert (r.groupby("id_item")["item"].nunique() == 1).all()

    x = r.merge(p[["id_participant", "unique_participant_code"]],
                on="id_participant", how="left", validate="many_to_one")
    assert x["unique_participant_code"].notna().all()
    stim = sorted(x["id_item"].unique(), key=lambda s: (int(s[:-1]), s[-1]))
    x["id"] = x["id_item"].map({s: i + 1 for i, s in enumerate(stim)})
    x["rater"] = pd.factorize(x["unique_participant_code"], sort=True)[0] + 1
    x["item"] = x["variable"].map(DIMS)
    x["resp"] = x["response"].astype(int)
    x["cov_stimulus"] = r["item"]
    x["cov_stimulus_type"] = x["id_item"].str[-1]
    x["cov_set"] = x["id_item"].str[:-1].astype(int)
    x["cov_list"] = x["list"]
    assert set(x["cov_stimulus_type"]) == set("abcde")
    t = x[["id", "item", "resp", "rater", "cov_stimulus", "cov_stimulus_type",
           "cov_set", "cov_list"]].sort_values(["id", "item", "rater"]).reset_index(drop=True)
    assert not t.duplicated(["id", "item", "rater"]).any()

    pv = {"valence": set(range(1, 10)), "arousal": set(range(1, 10)),
          "wordlikeness": set(range(1, 8))}
    for i, s in pv.items():
        bad = set(t.loc[t["item"] == i, "resp"]) - s
        assert not bad, (i, bad)
    cl = {"valence": "valence", "arousal": "arousal", "wordlikeness": "wordlikeness"}
    # The one waived check (validator_overrides.csv, Ben 2026-10-01, #1443).
    waived = {"resp_scale_constructs"}
    checks = run_qc(t, permitted_values=pv, item_constructs=cl)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert {n for n, _ in fails} <= waived, fails
    report = irw_validate.validate_frame(
        t, label=NAME, profile="upload",
        context={"permitted_values": pv, "item_constructs": cl})
    errors = [(f.check, f.message) for f in report.errors if f.check not in waived]
    assert not errors, errors
    print(f"    waived: {sorted({f.check for f in report.errors} & waived)}")
    for f in report.findings:
        print(f"    [{f.severity}] {f.check}: {f.message}")

    t.to_csv(OUT_DIR / f"{NAME}.csv", index=False)
    print(f"{NAME}.csv: rows={len(t)} ids={t['id'].nunique()} "
          f"items={t['item'].nunique()} raters={t['rater'].nunique()}")


if __name__ == "__main__":
    convert()
