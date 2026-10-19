#!/usr/bin/env python3

# Source: https://ssh.datastations.nl/dataset.xhtml?persistentId=doi:10.17026/SS/PVQ66Y
# DOI: 10.17026/SS/PVQ66Y
#   Hissink, E., de Laat, T., van der Schaaf, M., & Peters, M. (2025).
#   Vragenlijst meetinstrumenten Adapt at work [Dataset]. DANS Data Station
#   Social Sciences and Humanities.
# Data: "adapt at work meetinstrumenten anoniem.tab" -- 550 Dutch higher-
#   education students, measured twice (baseline and follow-up, linked by
#   student number before anonymisation), on instruments for adaptive
#   expertise in work-related contexts.
# License: CC BY 4.0 (verified on the DANS record, 2026-10-19).
# Item text: NOT shipped, extraction solved -- the deposit's
#   "Databeschrijving.pdf" prints every item's administered Dutch wording
#   against its variable name, block by block, with each block's response
#   anchors. That PDF is also what names the blocks below and what settles
#   the sentinel; the data file itself carries no labels at all.
#
# NINE tables, two waves each (wave 1 = nulmeting, wave 2 = vervolgmeting):
#   D-ADAPT, six domains, 1-5:
#     hissink_2025_problem_solving     CPS  5 items
#     hissink_2025_crisis_situations   CRS  5
#     hissink_2025_cultural_situations CUS  5
#     hissink_2025_interpersonal       IPS  5
#     hissink_2025_work_stress         STS  5
#     hissink_2025_physical_demands    ZFO  6
#   The Adaptability Scale, 1-5:
#     hissink_2025_cognitive_adapt     cognitive_   3
#     hissink_2025_behavioral_adapt    behavioral_  3
#     hissink_2025_affective_adapt     affective_   4
#
# 6 IS "NIET VAN TOEPASSING" ON THE D-ADAPT BLOCKS AND IS DROPPED. The PDF
#   lists that instrument's options as 1 Niet, 2 In geringe mate, 3 In
#   voldoende mate, 4 In hoge mate, 5 In zeer hoge mate, 6 niet van
#   toepassing -- so its scale is 1-5 and 6 is a non-response sitting inside
#   the observed range, exactly the sentinel the data standard says to filter.
#   The Adaptability Scale's own options stop at 5 (Helemaal mee eens), and no
#   6 occurs in those columns, which this script asserts.
#
# THE ADAPTIVE EXPERTISE INVENTORY IS DEFERRED, not rejected. BC1 (4 columns),
#   BC2 (4) and BC3 (3) are plainly item responses, but the PDF describes that
#   instrument as two domains of five items each -- two blocks and ten items
#   against the data's three blocks and eleven columns -- and prints its
#   response options with a duplicated "1." so the number of points is
#   ambiguous. Naming three blocks from two documented domains would be a
#   guess; recorded in the batch's leads file.
#
# NOT SHIPPED: the questionnaire's own administrative columns (q3-q12,
#   `versie`, `nulmeting`, `q3_vervolgmeting`) -- study programme, prior
#   education and year are free text or unlabelled codes here.
#
# id: the row index. The deposit is anonymised: the student number that
#   linked the two waves was removed before deposit, so a row is a student
#   and the two waves are already side by side in it.
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
    "IRW_RAW_DIR",
    REPO_ROOT / "automated_finding" / "runs" / "tail_batch" / "pvq66y" / "raw"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
FILE_ID, FNAME = None, "adapt at work meetinstrumenten anoniem.tab"
DOI = "10.17026/SS/PVQ66Y"
BASE = "https://ssh.datastations.nl"
FOLLOW_UP = "_vervolgmeting"
NOT_APPLICABLE = 6
DADAPT = {"hissink_2025_problem_solving": ("CPS", 5),
          "hissink_2025_crisis_situations": ("CRS", 5),
          "hissink_2025_cultural_situations": ("CUS", 5),
          "hissink_2025_interpersonal": ("IPS", 5),
          "hissink_2025_work_stress": ("STS", 5),
          "hissink_2025_physical_demands": ("ZFO", 6)}
ADAPTABILITY = {"hissink_2025_cognitive_adapt": ("cognitive_", 3),
                "hissink_2025_behavioral_adapt": ("behavioral_", 3),
                "hissink_2025_affective_adapt": ("affective_", 4)}
SCALE = set(range(1, 6))
DEFERRED = ["BC1", "BC2", "BC3"]


def fetch() -> Path:
    p = RAW_DIR / FNAME
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        j = requests.get(f"{BASE}/api/datasets/:persistentId/",
                         params={"persistentId": f"doi:{DOI}"},
                         headers=UA, timeout=120).json()
        fid = [f["dataFile"]["id"] for f in j["data"]["latestVersion"]["files"]
               if f["dataFile"]["filename"] == FNAME][0]
        r = requests.get(f"{BASE}/api/access/datafile/{fid}",
                         headers=UA, timeout=600)
        r.raise_for_status()
        p.write_bytes(r.content)
    return p


def main():
    df = pd.read_csv(fetch(), sep="\t")
    assert len(df) == 550, len(df)
    deferred_cols = [c for c in df.columns
                     if any(c.startswith(p) for p in DEFERRED)]
    assert len(deferred_cols) == 22, len(deferred_cols)   # 11 items x 2 waves
    print(f"deferred (see the header note): {len(deferred_cols)} Adaptive "
          f"Expertise Inventory columns across BC1/BC2/BC3")

    df["id"] = range(1, len(df) + 1)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for group, drops_six in ((DADAPT, True), (ADAPTABILITY, False)):
        for name, (prefix, n) in group.items():
            frames = []
            for wave, suffix in ((1, ""), (2, FOLLOW_UP)):
                cols = [f"{prefix}_{i}{suffix}" for i in range(1, n + 1)]
                missing = [c for c in cols if c not in df.columns]
                assert not missing, (name, wave, missing)
                part = (df[["id", *cols]]
                        .melt(id_vars=["id"], value_vars=cols,
                              var_name="item", value_name="resp")
                        .dropna(subset=["resp"]))
                part["item"] = part["item"].str.replace(suffix, "", regex=False) \
                    if suffix else part["item"]
                part["wave"] = wave
                frames.append(part)
            t = pd.concat(frames, ignore_index=True)
            t["resp"] = pd.to_numeric(t["resp"])
            assert (t["resp"] % 1 == 0).all(), name
            t["resp"] = t["resp"].astype(int)
            if drops_six:
                n_na = int((t["resp"] == NOT_APPLICABLE).sum())
                t = t[t["resp"] != NOT_APPLICABLE]
                print(f"{name}: dropped {n_na} 'niet van toepassing' "
                      f"(code {NOT_APPLICABLE})")
            else:
                assert NOT_APPLICABLE not in set(t["resp"]), \
                    f"{name}: a 6 in a block the PDF says stops at 5"
            bad = sorted(set(t["resp"]) - SCALE)
            assert not bad, f"{name}: resp outside the documented 1-5: {bad}"
            t = t[["id", "item", "resp", "wave"]]
            assert not t.duplicated(["id", "item", "wave"]).any(), name
            assert t["item"].nunique() == n, name
            assert t["id"].nunique() >= 100, (name, t["id"].nunique())
            checks = run_qc(t, permitted_values=SCALE)
            fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
            assert not fails, (name, fails)
            for c in checks:
                if c.status == "warn":
                    print(f"    [qc warn] {name} {c.name}: {c.detail[:130]}")
            report = irw_validate.validate_frame(
                t, label=name, profile="upload",
                context={"permitted_values": SCALE})
            assert report.conforms and not report.errors, \
                (name, [(f.check, f.message) for f in report.errors])
            t.to_csv(OUT_DIR / f"{name}.csv", index=False)
            print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
                  f"items={t['item'].nunique()} waves={t['wave'].nunique()} "
                  f"resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
