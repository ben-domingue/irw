"""Personality, academic motivation and distance-education attitudes --
two Turkish samples deposited together.

DOI: 10.17632/hwp4wsb549
Source: https://data.mendeley.com/datasets/hwp4wsb549
License: CC BY 4.0
Contributor (deposit record): CELIK

The deposit holds two files covering two different samples with different
instruments, so they are NOT merged:

  TEZ_412VERI.xlsx  (412 respondents)
    ams   28 items, 1-7  -- Academic Motivation Scale ("NEDEN OKULA ...")
    dist  26 items, 1-5  -- distance/face-to-face education attitudes
    tipi  10 items, 1-7  -- Ten-Item Personality Inventory ("Kendimi ...")

  TEZ_VERI_UNI.csv  (653 respondents, semicolon-delimited)
    bfi   44 items, 1-5  -- Big Five Inventory
    dist  16 items, 1-5  -- distance-education attitudes (a DIFFERENT and
                            shorter form than the 26-item one above, hence a
                            separate table, not a merge)
    bpns  24 items, 1-5  -- Basic Psychological Need Satisfaction

TODO.md recorded this deposit as returning an empty file listing at every
attempt; the Mendeley public API returns both files without trouble, so that
item is resolved. The CSV is semicolon-delimited, which is why a default read
produced a 653x12 mess.

Items ship under short positional codes (ams01, bfi01, ...) rather than their
full Turkish sentences: `item` is the join key against any future itemtext
table and must be a short stable identifier.

The `Rumuz` column is dropped. It is a self-constructed linkage pseudonym
("first letter of your name, first letter of your surname, and the last two
digits of your phone number") -- initials plus two digits, not a name and not
a phone number, so this is not treated as a PII block on the deposit; it is
simply useless as a covariate and is replaced by a sequential id.
"""
from __future__ import annotations

import io
import re
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
sys.path.insert(0, str(REPO_ROOT / "automated_finding"))
from irw_triage_updated import run_qc  # noqa: E402

DOI = "10.17632/hwp4wsb549"
KEY = "hwp4wsb549"
UA = {"User-Agent": "irw-batch/1.0 (research)"}

XLSX = "TEZ_412VERI.xlsx"
CSV = "TEZ_VERI_UNI.csv"


def _download(filename: str) -> bytes:
    r = requests.get(f"https://data.mendeley.com/public-api/datasets/{KEY}",
                     headers=UA, timeout=60)
    r.raise_for_status()
    match = [f for f in r.json()["files"] if f["filename"] == filename]
    assert len(match) == 1, (filename, [f["filename"] for f in r.json()["files"]])
    rr = requests.get(match[0]["content_details"]["download_url"],
                      headers=UA, timeout=180)
    rr.raise_for_status()
    return rr.content


def emit(df: pd.DataFrame, cols: list, code: str, name: str,
         scale: tuple, covs: dict, written: dict) -> None:
    codes = [f"{code}{i:02d}" for i in range(1, len(cols) + 1)]
    block = df[cols].copy()
    block.columns = codes
    block["id"] = df["id"].values
    cov = df[["id"] + list(covs)].rename(columns=covs)

    long = (block.melt(id_vars="id", var_name="item", value_name="resp")
            .dropna(subset=["resp"])
            .merge(cov, on="id"))
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(int)

    oor = ~long["resp"].between(*scale)
    if oor.any():
        per = long.loc[oor].groupby("item").size().to_dict()
        print(f"    [{name}] dropped {int(oor.sum())} out-of-range cells {per}")
        long = long[~oor]

    long = long[["id", "item", "resp"] + [c for c in long.columns
                                          if c.startswith("cov_")]]
    checks = run_qc(long)
    fails = [c for c in checks if c.status == "fail"]
    assert not fails, f"{name}: {[(c.name, c.detail) for c in fails]}"

    assert long["id"].nunique() >= 100, name
    assert long["item"].nunique() > 1, name
    assert name not in written, f"duplicate table name {name}"

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / f"{name}.csv", index=False)
    written[name] = len(long)
    print(f"  {name}: {long['id'].nunique()} ids x {long['item'].nunique()} "
          f"items = {len(long)} responses")


def build() -> None:
    written: dict = {}

    # ---- sample 1: the 412-respondent workbook --------------------------
    d = pd.read_excel(io.BytesIO(_download(XLSX)))
    d.columns = [str(c).strip() for c in d.columns]
    d["id"] = range(1, len(d) + 1)
    covs1 = {"Cinsiyet": "cov_gender", "Yaş": "cov_age",
             "Okul": "cov_school", "Sınıf": "cov_class"}

    ams = [c for c in d.columns if c.startswith("NEDEN OKULA")]
    dist26 = [c for c in d.columns if c.startswith("Yüz yüze")]
    tipi = [c for c in d.columns if c.startswith("Kendimi")]
    assert (len(ams), len(dist26), len(tipi)) == (28, 26, 10), \
        (len(ams), len(dist26), len(tipi))

    emit(d, ams, "ams", "celik_2026_academic_motivation", (1, 7), covs1, written)
    emit(d, dist26, "dist", "celik_2026_distance_ed_attitudes_26", (1, 5), covs1, written)
    emit(d, tipi, "tipi", "celik_2026_tipi", (1, 7), covs1, written)

    accounted = set(covs1) | set(ams) | set(dist26) | set(tipi) | {"id"}
    leftover = [c for c in d.columns if c not in accounted]
    assert leftover == [c for c in leftover
                        if c.startswith(("Rumuz", "Doldurduğunuz"))], leftover
    for c in leftover:
        print(f"    dropped '{c[:48]}...': linkage pseudonym / manipulation check")

    # ---- sample 2: the 653-respondent semicolon CSV ---------------------
    e = pd.read_csv(io.BytesIO(_download(CSV)), sep=";")
    e.columns = [str(c).strip() for c in e.columns]
    e["id"] = range(1, len(e) + 1)
    covs2 = {"Cinsiyetiniz": "cov_gender", "Yaş": "cov_age",
             "Okul": "cov_school", "Sınıf": "cov_class"}

    # the three instruments each restart their own 1..N numbering
    numbered = [c for c in e.columns if re.match(r"^\d+\.", c)]
    groups, current, last = [], [], 0
    for c in numbered:
        n = int(re.match(r"^(\d+)\.", c).group(1))
        if n <= last and current:
            groups.append(current); current = []
        current.append(c); last = n
    groups.append(current)
    assert [len(g) for g in groups] == [44, 16, 24], [len(g) for g in groups]

    emit(e, groups[0], "bfi", "celik_2026_bfi", (1, 5), covs2, written)
    emit(e, groups[1], "dist", "celik_2026_distance_ed_attitudes_16", (1, 5), covs2, written)
    emit(e, groups[2], "bpns", "celik_2026_bpns", (1, 5), covs2, written)

    print(f"  total: {sum(written.values())} responses across {len(written)} tables")


if __name__ == "__main__":
    build()
