#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC10588714
# DOI: 10.7717/peerj.16246
#
# Arza-Moncunill, Medina-Mirapeix & Martin-San Agustin (2023), "Development
# and validity of the expectations of physiotherapists questionnaire on
# practice management software." PeerJ. CC BY 4.0. N=272.
# Supplementary file peerj-11-16246-s004.sav has the 43 retained items of
# the Expectations of Physiotherapists Questionnaire (EPQ), each a 7-point
# Likert item ("very much disagree" to "very much agree", per the paper's
# Methods). The instrument covers two distinct areas -- clinical care (22
# items) and administrative activities (21 items) -- so it's split into two
# files per datastandard.md's "one file per scale" rule. The item-to-area
# mapping comes from supplementary file peerj-11-16246-s005.docx, which
# lists each item number's subtheme/area; cross-checked against the .sav
# columns present (E1-E48 minus E4/E10/E21/E40/E41, which were dropped from
# the original 43-item pool and are absent from both area lists and the
# data file). No PII (Response_Identity is a survey-platform response ID,
# not a personal identifier).

import io
import zipfile
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SUPPL_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10588714/supplementaryFiles"
MEMBER = "peerj-11-16246-s004.sav"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

CLINICAL_ITEMS = [f"E{i}" for i in
                  [16, 14, 15, 20, 11, 19, 18, 12, 17, 13, 23, 22, 24,
                   1, 2, 3, 25, 26, 27, 31, 32, 33]]
ADMIN_ITEMS = [f"E{i}" for i in
               [8, 6, 7, 9, 5, 28, 30, 29, 42, 43, 44, 45, 46,
                47, 48, 37, 38, 34, 36, 35, 39]]


def fetch_raw() -> pd.DataFrame:
    r = requests.get(SUPPL_URL, headers=UA, timeout=120)
    r.raise_for_status()
    zf = zipfile.ZipFile(io.BytesIO(r.content))
    with zf.open(MEMBER) as f:
        return pd.read_spss(io.BytesIO(f.read()), convert_categoricals=False)


def build_long(raw: pd.DataFrame, items: list[str]) -> pd.DataFrame:
    long = raw[["id"] + items].melt(id_vars=["id"], value_vars=items,
                                     var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    return long[["id", "item", "resp"]]


def write_scale(long: pd.DataFrame, fname: str):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / fname, index=False)
    print(f"{fname}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert():
    raw = fetch_raw()
    raw = raw.rename(columns={"Response_Identity": "id"})
    raw["id"] = raw["id"].astype(int)
    assert raw["id"].nunique() == len(raw)

    clinical = build_long(raw, CLINICAL_ITEMS)
    admin = build_long(raw, ADMIN_ITEMS)

    write_scale(clinical, "arzamoncunill_2023_epq_clinical.csv")
    write_scale(admin, "arzamoncunill_2023_epq_admin.csv")


if __name__ == "__main__":
    convert()
