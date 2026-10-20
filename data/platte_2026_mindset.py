#!/usr/bin/env python3
# Source: https://ssh.datastations.nl/dataset.xhtml?persistentId=doi:10.17026/SS/QTQ8WL
#   (DANS Data Station Social Sciences and Humanities)
# DOI: 10.17026/SS/QTQ8WL
# Data: FromBeliefstoAction_d.platte_raw_april26.sav (SPSS, served as .tab by
#   the Dataverse ingest -- the ORIGINAL is fetched with ?format=original,
#   because the .tab conversion drops the variable and value labels this
#   script reads), plus the deposit's own codebook .xlsx.
# License: CC BY-NC 4.0, as stated on the deposit record (checked 2026-10-19).
#   NC proceeds under datastandard.md "Before you start" (ruled 2026-10-01);
#   Derived_License carries the NC restriction through.
#
# Platte, D. (2026). From Beliefs to Action: Examining the Domain-Specific
#   Mediating Role of Mindset-Related Behaviours in the Relationship Between
#   Mindset Beliefs and Academic Achievement in Mathematics and Language Among
#   Primary School Students. Open Universiteit Nederland.
#
# 421 Dutch primary school students (aged 8-12, classes 6-8) answered seven
# instruments TWICE -- once about mathematics (_M) and once about language
# (_L). Each instrument is one table here, with both domains' items in it and
# itemcov_domain naming the domain, because the two administrations are the
# same scale asked about two school subjects rather than two scales:
#
#   platte_2026_mindset_beliefs   MB_*  6 items x 2 domains
#   platte_2026_challenges        CH_*  4 items x 2 domains
#   platte_2026_mistakes          MI_*  4 items x 2 domains
#   platte_2026_effort            EF_*  4 items x 2 domains
#   platte_2026_help_seeking      HS_*  4 items x 2 domains
#   platte_2026_self_monitoring   SM_*  4 items x 2 domains
#   platte_2026_motivation        MO_*  3 items x 2 domains
#
# resp = 1-5 (1 completely disagree ... 5 completely agree), as administered.
#   The codebook marks 24 items with "*" = "these items need to be reversed in
#   order to construct the scales"; they are NOT reversed here (datastandard:
#   do not recode reverse-scored items), and the codebook's own marks are
#   carried as itemcov_reverse_scored so a modeller can apply them.
#   Four items the codebook records as "removed to improve internal
#   consistency" (CH_M_1, HS_M_3, CH_L_1, HS_L_3) ARE shipped: they were
#   administered, and dropping them would hide an administered item.
# Covariates: school, age, gender, class. AA_M / AA_L (achievement scores on
#   1-5) are the study's OUTCOME, not items of any of these scales, and ship as
#   cov_achievement_math / cov_achievement_language. CAVEAT: the codebook's
#   reversal mark "*" is on those two columns as well, so a higher code is
#   likely a LOWER achievement band; the codebook gives only "1=score1 ...
#   5=score5" and does not say which end is which.
# id is the deposit's own ID column (verified unique, 1-421).
# Item text: not shipped -- neither label level carries a stem. The SPSS
#   variable labels are block names only ("MindsetBelief Math", repeated for
#   all six items) and the value labels are the 1-5 anchors; the codebook
#   .xlsx repeats the same block names. The administered Dutch wording is in
#   the thesis behind the deposit, which the record does not link.

import io
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
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
SAV = "https://ssh.datastations.nl/api/access/datafile/621740?format=original"
CODEBOOK = "https://ssh.datastations.nl/api/access/datafile/621739?format=original"

# prefix -> (n items per domain, table name)
SCALES = [
    ("MB", 6, "platte_2026_mindset_beliefs"),
    ("CH", 4, "platte_2026_challenges"),
    ("MI", 4, "platte_2026_mistakes"),
    ("EF", 4, "platte_2026_effort"),
    ("HS", 4, "platte_2026_help_seeking"),
    ("SM", 4, "platte_2026_self_monitoring"),
    ("MO", 3, "platte_2026_motivation"),
]
# Read from the deposit's codebook rather than transcribed: the last column
# marks items with "*" = "these items need to be reversed in order to construct
# the scales", and names the four items removed for internal consistency.
EXPECTED_REVERSED = {
    "AA_M", "AA_L", "MB_M_4", "MB_M_5", "MB_M_6", "CH_M_2", "CH_M_3", "CH_M_4",
    "MI_M_3", "MI_M_4", "HS_M_4", "MB_L_4", "MB_L_5", "MB_L_6", "CH_L_2",
    "CH_L_3", "CH_L_4", "MI_L_3", "MI_L_4", "HS_L_4",
}
EXPECTED_REMOVED = {"CH_M_1", "HS_M_3", "CH_L_1", "HS_L_3"}
DOMAIN = {"M": "mathematics", "L": "language"}


def codebook_marks() -> set:
    """The set of item codes the codebook marks '*' (reverse-scored)."""
    cb = pd.read_excel(io.BytesIO(fetch(CODEBOOK)), header=None)
    starred, removed = set(), set()
    for _, row in cb.iterrows():
        code, note = str(row[1]).strip(), str(row[5]).strip()
        if note == "*":
            starred.add(code)
        elif "removed" in note:
            removed.add(code)
    assert starred == EXPECTED_REVERSED, starred ^ EXPECTED_REVERSED
    assert removed == EXPECTED_REMOVED, removed ^ EXPECTED_REMOVED
    return starred


def fetch(url: str) -> bytes:
    r = requests.get(url, headers=UA, timeout=180)
    r.raise_for_status()
    return r.content


def convert() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    reversed_items = codebook_marks()
    raw = fetch(SAV)
    tmp = OUT_DIR / "_platte_raw.sav"
    tmp.write_bytes(raw)
    try:
        d, meta = pyreadstat.read_sav(str(tmp))
    finally:
        tmp.unlink()

    assert d.shape == (421, 65), d.shape
    assert d["ID"].is_unique and d["ID"].notna().all()
    # Every item carries the same 1-5 anchor set; confirm from the file's own
    # value labels rather than from the observed range.
    anchors = {1.0: "completely disagree", 5.0: "completely agree"}
    for c, lab in meta.variable_value_labels.items():
        if c.split("_")[0] in {p for p, _, _ in SCALES}:
            got = {k: v.lower() for k, v in lab.items()}
            assert got.get(1.0) == anchors[1.0] and got.get(5.0) == anchors[5.0], (c, lab)

    covs = pd.DataFrame({
        "id": d["ID"].astype(int),
        "cov_school": d["School"],
        "cov_age": d["Age"],
        "cov_gender": d["Gender"],
        "cov_class": d["Class"],
        "cov_achievement_math": d["AA_M"],
        "cov_achievement_language": d["AA_L"],
    })

    accounted = {"ID", "School", "Age", "Gender", "Class", "AA_M", "AA_L"}
    written = 0
    for prefix, n, name in SCALES:
        cols = [f"{prefix}_{dom}_{i}" for dom in ("M", "L") for i in range(1, n + 1)]
        missing = [c for c in cols if c not in d.columns]
        assert not missing, missing
        accounted.update(cols)

        long = d[["ID"] + cols].melt(id_vars="ID", var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"])
        t = pd.DataFrame({
            "id": long["ID"].astype(int),
            "item": long["item"],
            "resp": long["resp"].astype(int),
        })
        t["itemcov_domain"] = t["item"].str.split("_").str[1].map(DOMAIN)
        t["itemcov_reverse_scored"] = t["item"].isin(reversed_items).astype(int)
        t = t.merge(covs, on="id", how="left", validate="many_to_one")
        t = t[["id", "item", "resp"] + [c for c in t.columns if c.startswith("cov_")]
              + ["itemcov_domain", "itemcov_reverse_scored"]]
        t = t.sort_values(["id", "item"]).reset_index(drop=True)

        assert not t.duplicated(["id", "item"]).any()
        assert t["id"].nunique() >= 100, t["id"].nunique()
        assert t["item"].nunique() == 2 * n
        assert t["resp"].between(1, 5).all()
        assert t.groupby("itemcov_domain")["item"].nunique().eq(n).all()

        pv = {i: {1, 2, 3, 4, 5} for i in t["item"].unique()}
        cl = {i: name.replace("platte_2026_", "") for i in t["item"].unique()}
        fails = [(c.name, c.detail) for c in
                 run_qc(t, permitted_values=pv, item_constructs=cl) if c.status == "fail"]
        assert not fails, (name, fails)
        report = irw_validate.validate_frame(
            t, label=name, profile="upload",
            context={"permitted_values": pv, "item_constructs": cl})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        for f in report.findings:
            print(f"    [{f.severity}] {f.check}: {f.message}")

        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        written += 1
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")

    # Balance the books: every source column is either an item, a covariate, or
    # named here as deliberately dropped.
    unaccounted = set(d.columns) - accounted
    assert not unaccounted, unaccounted
    assert written == len(SCALES)


if __name__ == "__main__":
    convert()
