#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/_/32964434
# DOI: 10.6084/m9.figshare.32964434
# Data: Data_F.xlsx
# License: CC BY 4.0 (verified on the deposit record)
# Reference: Schaap, P., & Reynell van der Ross, M. (2025). The Dimensionality of the 19-item Copenhagen Burnout Inventory Adapted for Students.
#
#  respondents. 1 table(s) ship:
#   schaap_2025_cbi_s                             19 items, 1-5
#
# B1-B19 is the 19-item Copenhagen Burnout Inventory adapted for
#   students (CBI-S), named in the deposit's own title. The CBI has NO
#   register row -- logged as a register-row request in
#   itemtext/register_gaps_2026-10-18.csv rather than assumed open.
# Two further blocks are deposited and NOT shipped: R1-R18 (1-4) and
#   V1-V5 (1-4). The .xlsx carries no variable labels and the title
#   names only the CBI, so naming them would be a guess.
#
# PII: none. All three screen surfaces were checked -- column name, values, and
#   the SPSS/Stata variable label where the file has one.
#
# Item text: not shipped -- the .xlsx has no label level at all (no variable and no value labels; it is a bare export). Where the text is: the CBI-S items in the paper behind figshare 32964434.
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
# harvest.py does). Set SCHAAP_RAW to point at an already-downloaded copy.
_URL = "https://ndownloader.figshare.com/files/67015763"
_NAME = "Data_F.xlsx"


def _raw():
    override = os.environ.get("SCHAAP_RAW")
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

STEM = "schaap_2025"
BLOCKS = {'cbi_s': (['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9', 'B10', 'B11', 'B12', 'B13', 'B14', 'B15', 'B16', 'B17', 'B18', 'B19'], {1, 2, 3, 4, 5})}
COVS = {}
IDCOL = None
SKIP = {'R1': 'unlabelled block R (18 items, 1-4): neither the deposit nor the paper title names the instrument -- deferred, not rejected', 'R2': 'unlabelled block R (18 items, 1-4): neither the deposit nor the paper title names the instrument -- deferred, not rejected', 'R3': 'unlabelled block R (18 items, 1-4): neither the deposit nor the paper title names the instrument -- deferred, not rejected', 'R4': 'unlabelled block R (18 items, 1-4): neither the deposit nor the paper title names the instrument -- deferred, not rejected', 'R5': 'unlabelled block R (18 items, 1-4): neither the deposit nor the paper title names the instrument -- deferred, not rejected', 'R6': 'unlabelled block R (18 items, 1-4): neither the deposit nor the paper title names the instrument -- deferred, not rejected', 'R7': 'unlabelled block R (18 items, 1-4): neither the deposit nor the paper title names the instrument -- deferred, not rejected', 'R8': 'unlabelled block R (18 items, 1-4): neither the deposit nor the paper title names the instrument -- deferred, not rejected', 'R9': 'unlabelled block R (18 items, 1-4): neither the deposit nor the paper title names the instrument -- deferred, not rejected', 'R10': 'unlabelled block R (18 items, 1-4): neither the deposit nor the paper title names the instrument -- deferred, not rejected', 'R11': 'unlabelled block R (18 items, 1-4): neither the deposit nor the paper title names the instrument -- deferred, not rejected', 'R12': 'unlabelled block R (18 items, 1-4): neither the deposit nor the paper title names the instrument -- deferred, not rejected', 'R13': 'unlabelled block R (18 items, 1-4): neither the deposit nor the paper title names the instrument -- deferred, not rejected', 'R14': 'unlabelled block R (18 items, 1-4): neither the deposit nor the paper title names the instrument -- deferred, not rejected', 'R15': 'unlabelled block R (18 items, 1-4): neither the deposit nor the paper title names the instrument -- deferred, not rejected', 'R16': 'unlabelled block R (18 items, 1-4): neither the deposit nor the paper title names the instrument -- deferred, not rejected', 'R17': 'unlabelled block R (18 items, 1-4): neither the deposit nor the paper title names the instrument -- deferred, not rejected', 'R18': 'unlabelled block R (18 items, 1-4): neither the deposit nor the paper title names the instrument -- deferred, not rejected', 'V1': 'unlabelled block V (5 items, 1-4): same reason as block R', 'V2': 'unlabelled block V (5 items, 1-4): same reason as block R', 'V3': 'unlabelled block V (5 items, 1-4): same reason as block R', 'V4': 'unlabelled block V (5 items, 1-4): same reason as block R', 'V5': 'unlabelled block V (5 items, 1-4): same reason as block R'}


def convert():
    df = load_table(open(_raw(), "rb").read(), filename="Data_F.xlsx")
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
