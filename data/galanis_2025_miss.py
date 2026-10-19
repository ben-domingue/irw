#!/usr/bin/env python3

# Source: https://figshare.com/articles/dataset/_/29432735
# DOI: 10.6084/m9.figshare.29432735
#   Galanis, P. (2025). Misinformation Susceptibility Scale [Dataset].
#   figshare.
# Data: "MISS VALIDATION data.sav" -- 522 Greek adults, the validation sample
#   for the author's own Misinformation Susceptibility Scale, administered in
#   Greek.
# License: CC BY 4.0 (verified on the figshare record).
# Item text: NOT shipped. The MISS block's variable labels hold the item
#   NUMBER, not the stem ("MISS_4"), and value labels hold the Greek response
#   anchors; the conspiracy and trust blocks have neither level populated.
#   Where stems do exist in a label they are English translations of five
#   dropped items, which is the one block not shipped here. So the wording of
#   every shipped item is in the author's paper, not in this file -- that is
#   where a later pass starts. Both label levels were checked.
#
# THE ITEM CODES COME FROM THE VARIABLE LABELS, NOT THE COLUMN NAMES. The
#   deposit renumbered the retained items: the column named MISS_1 carries the
#   label "MISS_4", and the five items dropped in validation keep their
#   original numbers with a "remove" suffix (MISS_1remove -> "MISS_1"). The
#   label level is the instrument's own numbering and is what ships, so
#   MISS_1-MISS_14 here are the 14 items of the administered pool, with the
#   nine the author retained being MISS_4-9 and MISS_11-13. Shipping the
#   column names instead would silently publish a 3-position shift.
#   Verified against the deposit's own arithmetic: MISS_total_score equals the
#   sum of the nine retained items for 522 of 522 respondents.
#
# NOT SHIPPED: the five "miss_off_*remove" items. They are a separate pool
#   (verification behaviours: "check if the post has been updated?") with full
#   English stems but NO value labels, so their response scale is undocumented
#   -- two run 1-5 and three 1-4. Rather than guess that they share the MISS
#   frequency anchors, they are dropped. Also dropped: every *_total_score and
#   *_mean column, the two single-item measures (trust in science, Cologna;
#   government conspiracy, Lantian) which cannot be a table on their own, and
#   the all-empty column "ΔΟ".
#
# FOUR tables, 522 respondents:
#   galanis_2025_miss                14 items, 1-5 (never..very often)
#   galanis_2025_trust_scientists     3 items, 1-5 (not at all..very much)
#   galanis_2025_conspiracy           5 items, 0-10 (disagree..agree);
#                                     the source numbers them 2-6
#   galanis_2025_misinfo_judgment     4 items, 0-4 (not at all..certainly
#                                     true) -- true/false headline judgments;
#                                     fake_detection_total_score equals their
#                                     sum for 522 of 522 respondents
# id: the deposit's own id column (1-522), kept so the four tables link.
# Covariates: cov_gender, cov_age, cov_education, cov_job,
#   cov_financial_status, cov_trust_tv, cov_trust_web, cov_trust_social_media,
#   cov_interest_politics, cov_internet_hours, cov_share_social_media.
#   The trust/interest/sharing single items are 0-10 self-reports kept as
#   covariates rather than as a table; .sav value labels are harvested into
#   metadata/covariate_labels/.
#
# NOTE for a later pass: TISS_mean_score_trust_scientists equals the mean of
#   the three shipped trust items for only 77% of rows, so the deposit's
#   composite may be built over items this file does not contain. The three
#   items themselves are intact; only the composite is unexplained, and no
#   composite is shipped.
import os
import re
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
    "IRW_RAW_DIR",
    REPO_ROOT / "automated_finding" / "runs" / "figshare_batch" / "29432735" / "raw"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
ARTICLE, FNAME = 29432735, "MISS VALIDATION data.sav"

MISS_COLS = ([f"MISS_{i}" for i in range(1, 10)]
             + [f"MISS_{i}remove" for i in (1, 2, 3, 10, 14)])
TRUST = [f"εμπιστοσύνη{i}" for i in (1, 2, 3)]
CONSP = [f"κυβερνηση{i}" for i in range(2, 7)]
JUDGE = ["WhatsApp", "μεσα", "NASA", "Μακρόν"]
COVS = {
    "gender": "cov_gender",
    "age": "cov_age",
    "education": "cov_education",
    "job": "cov_job",
    "financial_status": "cov_financial_status",
    "trust_TV": "cov_trust_tv",
    "trust_web_pages": "cov_trust_web",
    "trust_social_media": "cov_trust_social_media",
    "interest_politics": "cov_interest_politics",
    "use_internet": "cov_internet_hours",
    "share_social_media": "cov_share_social_media",
}
NOT_SHIPPED = [
    "MISS_total_score", "MISS_total_score_mean", "fake_detection_total_score",
    "TISS_mean_score_trust_scientists",
    "TISS_mean_score_trust_scientists_total_score",
    "κυβερνηση_συνομωσια_total_score",
    "trust_sciences_single_item_cologna",
    "κυβερνηση_συνομωσια_single_lantian", "ΔΟ",
    "miss_off_6remove", "miss_off_11remove", "miss_off_12remove",
    "miss_off_18remove", "miss_off_19remove",
]


def fetch() -> Path:
    p = RAW_DIR / FNAME
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        j = requests.get(f"https://api.figshare.com/v2/articles/{ARTICLE}",
                         headers=UA, timeout=120).json()
        url = [f["download_url"] for f in j["files"] if f["name"] == FNAME][0]
        r = requests.get(url, headers=UA, timeout=300)
        r.raise_for_status()
        p.write_bytes(r.content)
    return p


def main():
    df, meta = pyreadstat.read_sav(str(fetch()), apply_value_formats=False)
    labels = meta.column_names_to_labels

    # The MISS item code is the variable LABEL; refuse anything else.
    renames = {}
    for c in MISS_COLS:
        lab = (labels.get(c) or "").strip()
        assert re.fullmatch(r"MISS_\d{1,2}", lab), (c, lab)
        renames[c] = lab
    miss = sorted(renames.values(), key=lambda s: int(s.split("_")[1]))
    assert miss == [f"MISS_{i}" for i in range(1, 15)], miss
    nine = [f"MISS_{i}" for i in (4, 5, 6, 7, 8, 9, 11, 12, 13)]

    all_src = MISS_COLS + TRUST + CONSP + JUDGE + list(COVS) + NOT_SHIPPED
    for c in all_src:
        assert c in df.columns, f"expected source column {c} is absent"
    unaccounted = [c for c in df.columns if c not in set(all_src + ["id"])]
    assert not unaccounted, f"unaccounted source columns: {unaccounted}"
    print(f"not shipped (composites, single items, empty column, and the "
          f"undocumented-scale miss_off pool): {NOT_SHIPPED}")

    df = df.rename(columns={**renames, **COVS})
    df["id"] = pd.to_numeric(df["id"]).astype(int)
    assert df["id"].is_unique

    # The deposit's own total is the arithmetic check on the relabelling.
    raw_tot, _ = pyreadstat.read_sav(str(fetch()), usecols=["MISS_total_score"])
    assert (df[nine].sum(axis=1) == raw_tot["MISS_total_score"]).all(), \
        "MISS_total_score does not equal the sum of the nine retained items"

    cov_cols = list(COVS.values())
    for cov in cov_cols:
        v = pd.to_numeric(df[cov])
        # cov_internet_hours is reported in half hours; keep it as given.
        df[cov] = v.astype("Int64") if (v.dropna() % 1 == 0).all() else v

    tables = {
        "galanis_2025_miss": (miss, set(range(1, 6))),
        "galanis_2025_trust_scientists": (TRUST, set(range(1, 6))),
        "galanis_2025_conspiracy": (CONSP, set(range(0, 11))),
        "galanis_2025_misinfo_judgment": (JUDGE, set(range(0, 5))),
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    written = []
    for name, (cols, scale) in tables.items():
        t = (df[["id", *cov_cols, *cols]]
             .melt(id_vars=["id", *cov_cols], value_vars=cols,
                   var_name="item", value_name="resp")
             .dropna(subset=["resp"]))
        t["resp"] = pd.to_numeric(t["resp"])
        assert (t["resp"] % 1 == 0).all(), f"{name}: fractional resp"
        t["resp"] = t["resp"].astype(int)
        bad = sorted(set(t["resp"]) - scale)
        assert not bad, f"{name}: resp outside the documented scale: {bad}"
        t = t[["id", "item", "resp", *cov_cols]]
        assert not t.duplicated(["id", "item"]).any(), name
        assert t["id"].nunique() >= 100 and t["item"].nunique() >= 2, name
        assert name not in written
        checks = run_qc(t, permitted_values=scale)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {name} {c.name}: {c.detail[:170]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": scale})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        written.append(name)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
