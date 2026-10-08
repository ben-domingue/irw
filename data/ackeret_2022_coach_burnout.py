#!/usr/bin/env python3
# Source: https://doi.org/10.5061/dryad.p5hqbzkrk (Zenodo mirror: https://zenodo.org/records/6638495)
# DOI: 10.1016/j.psychsport.2022.102207
#   Ackeret, N., Rothlin, P., Allemand, M., Krieger, T., Berger, T., Znoj, H., Kentta, G.,
#   Birrer, D., & Horvath, S. (2022). "Six-month stability of individual differences in
#   sports coaches' burnout, self-compassion and social support", Psychology of Sport and
#   Exercise, 102207.
# Data: Dryad 10.5061/dryad.p5hqbzkrk, DATA_Coaches.xlsx: 422 coaches x 159 columns
#       (three waves: baseline, 3 and 6 months). README_Coaches.docx documents the
#       column naming, the 999 missing code, the reversed copies (*u), parcels and
#       scale means. Demographics are not in the file.
# License: CC0 1.0 (Dryad record).
#
# Item text: not shipped. Levels checked: xlsx headers only (t1scs1 ..), no variable or
#   value labels; the README names the instruments but gives no wording.
#
# Tables (wave = 1, 2, 3 for t1, t2, t3; ids are row order, the same coach across waves):
#   ackeret_2022_scs_sf          scs1-12  1-5  Self-Compassion Scale - Short Form (Raes et
#                                              al. 2011)
#   ackeret_2022_coach_burnout   cbq1-15  1-5  Coach Burnout Questionnaire (Harris et al.
#                                              2005)
#   ackeret_2022_social_support  ssq1-6   1-5  Brief Perceived Social Support
#                                              Questionnaire (F-SozU K-6; Kliem et al. 2015)
#   Raw (unreversed) values; the README's reversed copies (scs1/4/8/9/11/12, cbq1/14,
#   suffix "u") are skipped. 999 = missing / did not take part in that wave.
# Skipped: 24 reversed copies, 27 parcel means, 9 scale means.

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
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "ackeret_2022"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://zenodo.org/api/records/6638495/files/DATA_Coaches.xlsx/content"
TABLES = {"ackeret_2022_scs_sf": ("scs", 12), "ackeret_2022_coach_burnout": ("cbq", 15),
          "ackeret_2022_social_support": ("ssq", 6)}


def fetch() -> Path:
    p = RAW_DIR / "data.xlsx"
    if not p.exists():
        r = requests.get(URL, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def main() -> None:
    d = pd.read_excel(fetch(), sheet_name="data")
    assert d.shape == (422, 159), d.shape
    raw = [c for c in d.columns if re.fullmatch(r"t[123](scs|cbq|ssq)\d+", c)]
    rev = [c for c in d.columns if re.fullmatch(r"t[123](scs|cbq)\d+u", c)]
    parcels = [c for c in d.columns if re.fullmatch(r"(SC|BO|SU)_T[123]_P[ABC]", c)]
    means = [f"t{w}{s}" for w in (1, 2, 3) for s in ("SCStotal", "cbqtot", "socsup")]
    assert len(raw) == 99 and len(rev) == 24 and len(parcels) == 27
    assert set(d.columns) == set(raw) | set(rev) | set(parcels) | set(means)
    print("  skip 24 reversed copies (*u), 27 parcel means, 9 scale means")
    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    names = list(TABLES)
    assert len(set(names)) == len(names)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (pre, k) in TABLES.items():
        frames = []
        for w in (1, 2, 3):
            cols = {f"t{w}{pre}{i}": f"{pre}{i}" for i in range(1, k + 1)}
            m = d[["id"] + list(cols)].rename(columns=cols).melt(
                id_vars="id", var_name="item", value_name="resp")
            m.insert(2, "wave", w)
            frames.append(m)
        t = pd.concat(frames)
        t = t[t["resp"].notna() & (t["resp"] != 999)]
        assert t["resp"].isin(range(1, 6)).all(), name
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp", "wave"]].sort_values(["id", "wave", "item"]).reset_index(drop=True)
        assert not t.duplicated(["id", "item", "wave"]).any() and t["id"].nunique() >= 100
        its = [f"{pre}{i}" for i in range(1, k + 1)]
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
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} items={t['item'].nunique()} "
              f"resp={t['resp'].min()}-{t['resp'].max()} per-wave ids="
              f"{t.groupby('wave')['id'].nunique().to_dict()}")


if __name__ == "__main__":
    main()
