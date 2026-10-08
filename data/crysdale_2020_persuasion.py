#!/usr/bin/env python3
# Source: https://doi.org/10.5683/SP2/S9D7RW
# DOI: 10.5683/SP2/S9D7RW (dataset); thesis: Crysdale, P. (2020). "The role of personality
#   in defining the boundary between persuasive technology and coercion", Master of
#   Electronic Commerce, Dalhousie University.
# Data: Borealis 10.5683/SP2/S9D7RW: "Big-5 Questionnaire Responses.xlsx" (file 126637; 407
#       participants x 61 items G2Q00001-G2Q00049, B50-B61) and "Responses to
#       Storyboards.xlsx" (file 126639; 407 x Q1-Q7). The record describes the storyboard
#       scale as "1 meaning extremely persuasive, 5 meaning extremely coercive and 3 is
#       neutral" and the personality survey as the 61-question "Big-5 V2" form at
#       outofservice.com/bigfive. "Computed Big-5 Profiles.xlsx" (scores) is not used.
# License: CC0 1.0 (Borealis record).
#
# Item text: not shipped. Levels checked: xlsx headers only (survey-platform codes), no
#   labels; the storyboards are in the thesis, the personality items on the cited website.
#
# Tables (all 1-5; no id column in either file, so id = row order within each file -- the
#   two files have the same 407 rows but nothing in the deposit ties a row of one to a row
#   of the other, so they are not linked):
#   crysdale_2020_big5         G2Q00001-G2Q00049, B50-B61 (61 items), 1-5 agreement
#   crysdale_2020_storyboards  Q1-Q7: rating of each of seven persuasive-technology
#                              storyboards, 1 extremely persuasive .. 5 extremely coercive

import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "crysdale_2020"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
FILES = {"crysdale_2020_big5": ("big5.xlsx", 126637, 61),
         "crysdale_2020_storyboards": ("story.xlsx", 126639, 7)}


def fetch(fname: str, fid: int) -> Path:
    p = RAW_DIR / fname
    if not p.exists():
        r = requests.get(f"https://borealisdata.ca/api/access/datafile/{fid}?format=original",
                         headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def main() -> None:
    names = list(FILES)
    assert len(set(names)) == len(names)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (fname, fid, k) in FILES.items():
        d = pd.read_excel(fetch(fname, fid))
        assert d.shape == (407, k), d.shape
        its = list(d.columns)
        d = d.reset_index(drop=True)
        d.insert(0, "id", d.index + 1)
        t = d.melt(id_vars="id", value_vars=its, var_name="item",
                   value_name="resp").dropna(subset=["resp"])
        assert t["resp"].isin(range(1, 6)).all(), name
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"]].sort_values(["id", "item"]).reset_index(drop=True)
        assert not t.duplicated(["id", "item"]).any() and t["id"].nunique() >= 100
        pv = {i: set(range(1, 6)) for i in its}
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {c.name}: {c.detail[:200]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": pv})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
