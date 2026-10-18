#!/usr/bin/env python3
# Source: https://zenodo.org/records/22240547
# DOI: 10.5281/zenodo.22240547
# Data: Data.sav
# License: cc-by-4.0 (verified on the deposit record)
# Reference: Hung (2026). Trait and State Fear of Missing Out and Adolescent Academic Burnout: A Four-Wave Study. Zenodo.
#
#  respondents. 5 table(s) ship:
#   hung_2026d_fomo                              12 items, 1-7
#   hung_2026d_learning_anxiety                   7 items, 1-7
#   hung_2026d_procrastination                    9 items, 1-7
#   hung_2026d_academic_burnout                  16 items, 1-7
#   hung_2026d_social_desirability                5 items, 1-7
#
# Five blocks, all 1-7, with full English stems in the variable labels.
# NOT the same sample as the already-staged hung_2026_fomo (zenodo
#   19784064, 582 respondents, 7 items). This deposit is 681 x 12. The
#   seven comparable items share only 16 of 541 response vectors, 3.0%,
#   which is chance for a 7-item 1-7 battery -- different samples from
#   the same programme, so the prefix is hung_2026d and the ids are not
#   comparable across deposits.
# RIGHTS, by reading the stems (the register's own matchers reach none
#   of these codes):
#   TF1-5/SF6-12 = Fear of Missing Out -> register BLOCK. Matcher is
#     ^fomo_[0-9]+$|^FOMO[0-9] with zero text patterns, so a TF/SF
#     coding is invisible to it. TF1 is Przybylski item 1 verbatim.
#   SDRS1-5 = Socially Desirable Response Set 5 (Hays) -> register
#     BLOCK with BOTH matcher columns empty.
#   EX/LC/RE = a 16-item academic burnout/engagement battery. The
#     numbering runs to 16 with three subscales (4+5+7), which fits
#     MBI-GS/MBI-SS and also OLBI-S; I could not pin which, and both
#     candidates are block-class. Shipped as responses under the
#     source's own codes, with the item text held -- see below.
#
# PII: none. All three screen surfaces were checked -- column name, values, and
#   the SPSS/Stata variable label where the file has one.
#
# Item text: held for ALL FIVE tables. FoMO and SDRS-5 are register BLOCK rows, and the burnout battery could not be pinned to a specific register row. Both label levels were checked and the English stems are present for every item, so all five are extraction-solved and ship immediately on a ruling. This follows hung_2026b_learning_engagement, which shipped the response tables and held the wording.
#
# From the #3077 blank-flag re-mine: this key was written to
# repo_triage_seen_keys.csv before irw#2222 added the flag column, so the key was
# recorded and the verdict never was. It was not a rejection -- nobody had looked.
import os
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "automated_finding"))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402
from irw_triage_updated import load_table  # noqa: E402

# --- raw input -------------------------------------------------------------
# Self-contained by design: fetches the deposit itself and caches it, so it
# re-runs in a fresh checkout (which is what metadata/covariate_labels/
# harvest.py does). Set HUNG_D_RAW to point at an already-downloaded copy.
_URL = "https://zenodo.org/api/records/22240547/files/Data.sav/content"
_NAME = "Data.sav"


def _raw():
    override = os.environ.get("HUNG_D_RAW")
    if override:
        return override if os.path.isfile(override) else os.path.join(override, _NAME)
    cache = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "..", "automated_finding", "runs", "raw_cache")
    os.makedirs(cache, exist_ok=True)
    dest = os.path.join(cache, _NAME)
    if not os.path.exists(dest):
        import urllib.request
        req = urllib.request.Request(
            _URL, headers={"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"})
        with urllib.request.urlopen(req, timeout=300) as r, open(dest, "wb") as fh:
            fh.write(r.read())
    return dest


OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")

STEM = "hung_2026d"
BLOCKS = {'fomo': (['TF1', 'TF2', 'TF3', 'TF4', 'TF5', 'SF6', 'SF7', 'SF8', 'SF9', 'SF10', 'SF11', 'SF12'], {1, 2, 3, 4, 5, 6, 7}), 'learning_anxiety': (['LA1', 'LA2', 'LA3', 'LA4', 'LA5', 'LA6', 'LA7'], {1, 2, 3, 4, 5, 6, 7}), 'procrastination': (['GPS1P', 'GPS2P', 'GPS3P', 'GPS4P', 'GPS5R', 'GPS6P', 'GPS7R', 'GPS8P', 'GPS9R'], {1, 2, 3, 4, 5, 6, 7}), 'academic_burnout': (['EX2', 'EX5', 'EX8', 'EX12', 'LC3', 'LC6', 'LC9', 'LC10', 'LC13', 'RE1R', 'RE4R', 'RE7R', 'RE11R', 'RE14R', 'RE15R', 'RE16R'], {1, 2, 3, 4, 5, 6, 7}), 'social_desirability': (['SDRS1', 'SDRS2R', 'SDRS3R', 'SDRS4R', 'SDRS5'], {1, 2, 3, 4, 5, 6, 7})}
COVS = {'Gender': 'cov_gender', 'Age': 'cov_age', 'Grade': 'cov_grade'}
IDCOL = 'Number'
SKIP = {'ME': 'a single item, not a scale', 'FE': 'a single item, not a scale'}


def convert():
    df = load_table(open(_raw(), "rb").read(), filename="Data.sav")
    print(f"raw: {df.shape}")

    if IDCOL:
        assert df[IDCOL].nunique() == len(df), (
            f"{IDCOL} is not unique ({df[IDCOL].nunique()} of {len(df)}) -- "
            "it cannot be the person id")
        ids = df[IDCOL].astype(str).values
    else:
        # No person identifier is deposited, so the row index IS the person.
        ids = [str(i + 1) for i in range(len(df))]

    # Balance the books: every source column is shipped, a covariate, the id,
    # or skipped for a printed reason.
    shipped = {c for cols, _ in BLOCKS.values() for c in cols}
    accounted = shipped | set(COVS) | set(SKIP) | ({IDCOL} if IDCOL else set())
    for c, why in SKIP.items():
        if c in df.columns:
            print(f"  skip {c!r}: {why}")
    unaccounted = [c for c in df.columns if c not in accounted]
    assert not unaccounted, f"unaccounted source columns: {unaccounted}"
    missing = [c for c in shipped if c not in df.columns]
    assert not missing, f"expected item columns absent: {missing}"

    cov = {v: df[k] for k, v in COVS.items() if k in df.columns}
    written = []
    for suffix, (cols, permitted) in BLOCKS.items():
        long = df[cols].copy()
        long.insert(0, "id", ids)
        for name, series in cov.items():
            long[name] = series.values
        out = long.melt(id_vars=["id"] + list(cov),
                        value_vars=cols, var_name="item", value_name="resp")
        out = out.dropna(subset=["resp"])
        out["resp"] = out["resp"].astype(int)
        # The permitted set is asserted PER TABLE, never inherited from a
        # sibling block -- that is what catches a 1-6 block in a 1-5 family.
        extra = set(out["resp"].unique()) - permitted
        assert not extra, f"{suffix}: resp values outside {sorted(permitted)}: {extra}"
        assert out["item"].nunique() > 1, f"{suffix}: only one distinct item"
        assert out["id"].nunique() >= 100, (
            f"{suffix}: {out['id'].nunique()} unique ids, below the floor of 100")
        out = out[["id", "item", "resp"] + list(cov)]

        pv = {i: set(permitted) for i in cols}
        checks = run_qc(out, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (suffix, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {c.name}: {c.detail[:200]}")
        report = irw_validate.validate_frame(out, label=f"{STEM}_{suffix}",
                                             profile="upload",
                                             context={"permitted_values": pv})
        assert report.conforms and not report.errors,             (suffix, [(f.check, f.message) for f in report.errors])

        name = f"{STEM}_{suffix}"
        assert name not in written, f"duplicate output name {name}"
        written.append(name)
        path = os.path.join(OUT_DIR, name + ".csv")
        out.to_csv(path, index=False, na_rep="NA")
        print(f"  {name}: {out['id'].nunique()} ids x {out['item'].nunique()} "
              f"items = {len(out)} responses -> {path}")
    return written


if __name__ == "__main__":
    convert()
