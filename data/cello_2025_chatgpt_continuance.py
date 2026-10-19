#!/usr/bin/env python3

# Source: https://zenodo.org/records/15332365
# DOI: 10.5281/zenodo.15332365
#   Cello, A., Rauf, M. A., Jamil, M., et al. (2025). Questionnaire Dataset for the
#   Study on Continuance Usage Intention of ChatGPT [Dataset]. Zenodo.
# Data: the deposit's single file -- 421 Indonesian students, 1-5 agreement.
# License: CC BY 4.0 (verified on the Zenodo record).
#
# ITEM CODES COME FROM THE HEADER, NOT THE POSITION. Each item column's header is
#   the author's code AND the stem in one cell -- "CF 1. Layanan yang dibutuhkan
#   ...". The code is parsed off the front ("CF 1." -> "CF1"), so the mapping is the
#   source's own labelling rather than column order; a one-position slip would
#   otherwise be invisible to every set-comparing gate. The parse is asserted to
#   produce exactly the expected count per block.
# Item text: NOT shipped, though it is RIGHT THERE in those headers. The stems are
#   the administered INDONESIAN with no author-supplied English, so shipping needs
#   an IRW-generated translation owing a translation_source and an issues-page
#   callout. Queued with the batch's translation round in TODO -- and this deposit
#   is one of the cheapest cases for it, since code and stem are already in the
#   same cell.
#
# A SIX-POINT SCALE. All six categories are used across every item block, so
#   6 is a response and not a sentinel; checked over the whole item range
#   before shipping. (This deposit is one of two in the batch whose scale the
#   automated profiling could not read -- stem-bearing / banner-offset headers
#   defeat a prefix grouping -- and both turned out to be 1-6 rather than the
#   1-5 the rest of the family uses. The range assertion is what caught it.)
#
# NINE tables, all 1-6:
#   cello_2025_confirmation          3 (CF)   cello_2025_information_quality  5 (IQ)
#   cello_2025_perceived_usefulness  4 (PU)   cello_2025_social_influence     3 (SI)
#   cello_2025_satisfaction          4 (ST)   cello_2025_perceived_ease       5 (PEU)
#   cello_2025_continuance_intention 4 (CUI)  cello_2025_effort_expectancy    3 (EE)
#   cello_2025_habit                 3 (HB)
# id: the file carries no respondent id; the 0-based row index is used.
# Covariates: cov_gender, cov_semester, cov_university, cov_major.
# Rights: none of the nine is in the instrument rights register; these are
#   ECM/UTAUT items. Checked against the register's block list by construct name.
import os
import re
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = Path(os.environ.get(
    "IRW_RAW_DIR", REPO_ROOT / "automated_finding" / "runs" / "b5_raw" / "15332365"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
RECORD = 15332365
SCALE = set(range(1, 7))

COVS = {"Gender": "cov_gender", "Semester": "cov_semester",
        "Asal Universitas": "cov_university", "Jurusan": "cov_major"}
# prefix -> (table, expected item count)
BLOCKS = {
    "CF": ("cello_2025_confirmation", 3),
    "PU": ("cello_2025_perceived_usefulness", 4),
    "ST": ("cello_2025_satisfaction", 4),
    "CUI": ("cello_2025_continuance_intention", 4),
    "IQ": ("cello_2025_information_quality", 5),
    "SI": ("cello_2025_social_influence", 3),
    "PEU": ("cello_2025_perceived_ease", 5),
    "EE": ("cello_2025_effort_expectancy", 3),
    "HB": ("cello_2025_habit", 3),
}
CODE = re.compile(r"^([A-Z]{2,3})\s*(\d+)\s*\.")


def fetch() -> Path:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    hits = [p for p in RAW_DIR.iterdir() if p.name != "_record.json"]
    if hits:
        return hits[0]
    j = requests.get(f"https://zenodo.org/api/records/{RECORD}",
                     headers=UA, timeout=120).json()
    f = j["files"][0]
    p = RAW_DIR / f["key"]
    r = requests.get(f["links"]["self"], headers=UA, timeout=300)
    r.raise_for_status()
    p.write_bytes(r.content)
    return p


def main():
    p = fetch()
    df = (pd.read_csv(p) if p.suffix.lower() == ".csv" else pd.read_excel(p))
    rename, by_prefix = {}, {}
    for c in df.columns:
        m = CODE.match(str(c).strip())
        if m:
            code = f"{m.group(1)}{int(m.group(2))}"
            rename[c] = code
            by_prefix.setdefault(m.group(1), []).append(code)
    df = df.rename(columns=rename)

    for pre, (name, n) in BLOCKS.items():
        got = sorted(by_prefix.get(pre, []), key=lambda s: int(s[len(pre):]))
        assert len(got) == n, f"{pre}: parsed {len(got)} items, expected {n}: {got}"
        by_prefix[pre] = got
    unknown = set(by_prefix) - set(BLOCKS)
    assert not unknown, f"unexpected code prefixes in the header: {unknown}"

    df.insert(0, "id", range(len(df)))
    items = {c for cols in by_prefix.values() for c in cols}
    unaccounted = [c for c in df.columns
                   if c not in ({"id"} | items | set(COVS))]
    assert not unaccounted, f"unaccounted source columns: {unaccounted}"

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    written = []
    for pre, (name, _) in BLOCKS.items():
        cols = by_prefix[pre]
        t = (df[["id", *COVS, *cols]]
             .melt(id_vars=["id", *COVS], value_vars=cols,
                   var_name="item", value_name="resp")
             .dropna(subset=["resp"])
             .rename(columns=COVS))
        t["resp"] = pd.to_numeric(t["resp"])
        assert (t["resp"] % 1 == 0).all(), f"{name}: fractional resp"
        t["resp"] = t["resp"].astype(int)
        bad = sorted(set(t["resp"]) - SCALE)
        assert not bad, f"{name}: resp outside the observed 1-6 scale: {bad}"
        t = t[["id", "item", "resp", *COVS.values()]]
        assert not t.duplicated(["id", "item"]).any(), name
        assert t["id"].nunique() >= 100 and t["item"].nunique() >= 2, name
        assert name not in written
        checks = run_qc(t, permitted_values=SCALE)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {name} {c.name}: {c.detail[:170]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": SCALE})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        written.append(name)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
