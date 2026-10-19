#!/usr/bin/env python3

# Source: https://zenodo.org/records/20453710
# DOI: 10.5281/zenodo.20453710
#   Nita, Natalia; Alex, M. Muqarabbin (2026). Questionnaire & Raw Research Data
#   "From Marketplace to Website: Determinants of Customer Loyalty" [Dataset].
#   Zenodo.
# Data: "[Raw Research Data] From Marketplace to Website_ Determinants ..." --
#       409 Indonesian online shoppers, 1-5 agreement, bare construct codes.
# License: CC BY 4.0 (verified on the Zenodo record).
# Item text: NOT shipped. The deposit's companion "[Questionnaire] ..." file holds
#   the full stems and they line up with these codes (PE1., PS1., ET1., ...), so the
#   mapping is cheap -- but they are the administered INDONESIAN with no author
#   English, so shipping needs an IRW translation with a translation_source and an
#   issues-page callout. Queued with the batch's translation round in TODO; the text
#   is in that questionnaire file.
# TWO FILES, ONE SAMPLE. The questionnaire file also carries the 409 responses, with
#   the stems as column headers and six extra demographic/screening columns. The raw
#   file is the same 409 respondents under clean codes, so only it is used -- taking
#   both would duplicate every respondent.
#
# SEVEN tables, all 1-5:
#   nita_2026_perceived_enjoyment   4 (PE1-4)    nita_2026_perceived_value   5 (PV1-5)
#   nita_2026_perceived_security    4 (PS1-4)    nita_2026_satisfaction      4 (CS1-4)
#   nita_2026_trust                 5 (ET1-5)    nita_2026_loyalty          13 (CL1-13)
#   nita_2026_perceived_risk        5 (PR1-5)
# id: the file carries no respondent id; the 0-based row index is used.
# Covariates: none in the raw file (the demographics live only in the questionnaire
#   export, under free-text Indonesian headers, and are not carried here).
# Rights: none of the seven is in the register; checked against its block list by
#   construct rather than by code prefix.
import os
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
    "IRW_RAW_DIR", REPO_ROOT / "automated_finding" / "runs" / "b5_raw" / "20453710"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
RECORD = 20453710
SCALE = set(range(1, 6))

BLOCKS = {
    "nita_2026_perceived_enjoyment": [f"PE{i}" for i in range(1, 5)],
    "nita_2026_perceived_security": [f"PS{i}" for i in range(1, 5)],
    "nita_2026_trust": [f"ET{i}" for i in range(1, 6)],
    "nita_2026_perceived_risk": [f"PR{i}" for i in range(1, 6)],
    "nita_2026_perceived_value": [f"PV{i}" for i in range(1, 6)],
    "nita_2026_satisfaction": [f"CS{i}" for i in range(1, 5)],
    "nita_2026_loyalty": [f"CL{i}" for i in range(1, 14)],
}


def fetch() -> Path:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    hits = [p for p in RAW_DIR.iterdir()
            if p.name.startswith("[Raw Research Data]")]
    if hits:
        return hits[0]
    j = requests.get(f"https://zenodo.org/api/records/{RECORD}",
                     headers=UA, timeout=120).json()
    f = [x for x in j["files"] if x["key"].startswith("[Raw Research Data]")][0]
    p = RAW_DIR / f["key"]
    r = requests.get(f["links"]["self"], headers=UA, timeout=300)
    r.raise_for_status()
    p.write_bytes(r.content)
    return p


def main():
    p = fetch()
    df = pd.read_csv(p) if p.suffix.lower() in ("", ".csv") else pd.read_excel(p)
    df.insert(0, "id", range(len(df)))
    items = {c for cols in BLOCKS.values() for c in cols}
    for c in items:
        assert c in df.columns, f"expected item column {c} is absent"
    unaccounted = [c for c in df.columns if c not in ({"id"} | items)]
    assert not unaccounted, f"unaccounted source columns: {unaccounted}"

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    written = []
    for name, cols in BLOCKS.items():
        t = (df[["id", *cols]]
             .melt(id_vars="id", value_vars=cols, var_name="item",
                   value_name="resp")
             .dropna(subset=["resp"]))
        t["resp"] = pd.to_numeric(t["resp"])
        assert (t["resp"] % 1 == 0).all(), f"{name}: fractional resp"
        t["resp"] = t["resp"].astype(int)
        bad = sorted(set(t["resp"]) - SCALE)
        assert not bad, f"{name}: resp outside the observed 1-5 scale: {bad}"
        t = t[["id", "item", "resp"]]
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
