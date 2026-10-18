#!/usr/bin/env python3

# Source: https://zenodo.org/records/21157129
# DOI: 10.5281/zenodo.21157129
#   Septiani, Roselin Dwi (2026). Survey Dataset on Impact Live Streaming Feature
#   to Purchase Intention [Dataset]. Zenodo.
# Data: the deposit's single .csv -- 433 Indonesian respondents, 1-5 agreement.
# License: CC BY 4.0 (verified on the Zenodo record).
# Item text: NOT shipped. The .csv has one header row of bare construct codes and
#   no label level. The stems are in the paper behind the deposit title.
#
# EIGHT tables, all 1-5, three items each -- the eight constructs of a live-stream
# purchase-intention model, kept as separate tables because each is its own
# measurement scale (datastandard.md), not one 24-item instrument:
#   septiani_2026_visibility   VI1-3     septiani_2026_perceived_utility   PUV1-3
#   septiani_2026_interaction  IN1-3     septiani_2026_perceived_hedonic   PHV1-3
#   septiani_2026_attitude     AT1-3     septiani_2026_trust              PT1-3
#   septiani_2026_perceived_risk PR1-3   septiani_2026_purchase_intention PI1-3
# id: the file carries no respondent id; the 0-based row index is used.
# Covariates: none -- the deposit ships no demographics.
# Rights: none of the eight is in the instrument rights register. PR here is
#   "perceived risk", not a register instrument; checked by construct name against
#   the register's block list by hand.
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
    "IRW_RAW_DIR", REPO_ROOT / "automated_finding" / "runs" / "b5_raw" / "21157129"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
RECORD = 21157129
SCALE = set(range(1, 6))

BLOCKS = {
    "septiani_2026_visibility": "VI",
    "septiani_2026_interaction": "IN",
    "septiani_2026_attitude": "AT",
    "septiani_2026_perceived_risk": "PR",
    "septiani_2026_perceived_utility": "PUV",
    "septiani_2026_perceived_hedonic": "PHV",
    "septiani_2026_trust": "PT",
    "septiani_2026_purchase_intention": "PI",
}


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
    df = pd.read_csv(p) if p.suffix.lower() == ".csv" else pd.read_excel(p)
    df.insert(0, "id", range(len(df)))

    blocks = {n: [f"{pre}{i}" for i in range(1, 4)] for n, pre in BLOCKS.items()}
    items = {c for cols in blocks.values() for c in cols}
    for c in items:
        assert c in df.columns, f"expected item column {c} is absent"
    unaccounted = [c for c in df.columns if c not in ({"id"} | items)]
    assert not unaccounted, f"unaccounted source columns: {unaccounted}"

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    written = []
    for name, cols in blocks.items():
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
