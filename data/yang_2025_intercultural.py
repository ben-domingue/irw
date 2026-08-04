#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0316937
# DOI: 10.1371/journal.pone.0316937
# Supporting Information (S2 File, "Minimal data set"):
#   https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0316937.s002
#
# Yang et al. (2025), "Intercultural competence of Chinese students abroad".
# N=130 (of 145 questionnaires completed, 130 valid). Workbook has three
# sheets keyed by the same "No." respondent index:
#   - "Basic information of samples": demographics (covariates)
#   - "Intercultural Contact": raw items for the Intercultural Contact
#     scale (FSM: Foreign Social Media, 3 items; FICA: Foreign Intercultural
#     Communication Activity, 6 items), 1-5, plus derived "Final Score of..."
#     columns which are excluded (composite, not raw response)
#   - "Intercultural Competence Scores": raw items for the 28-item AIC-CCS
#     (Assessment of Intercultural Competence of Chinese College Students),
#     1-5, plus per-subscale "Final Score of..." columns which are excluded
#
# Two output tables (one scale per file per datastandard.md):
#   yang_2025_intercultural_contact  (9 items, 1-5)
#   yang_2025_aiccs                  (28 items, 1-5)

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0316937.s002")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

CONTACT_ITEMS = ["FSM1", "FSM2", "FSM3", "FICA1", "FICA2", "FICA3", "FICA4", "FICA5", "FICA6"]

# original AIC-CCS column (verbatim from the workbook) -> short item code
AICCS_ITEMS = {
    "KN1-Knowledge of self—(1) understanding native history": "KN1_1",
    "KN1(2) understanding native social norms": "KN1_2",
    "KN1(3) understanding the native sense of values": "KN1_3",
    "KN2-Knowledge of others—(1) understanding foreign knowledge of history": "KN2_1",
    "KN2-(2) understanding foreign social norms": "KN2_2",
    "KN2-(3) understanding the foreign sense of values": "KN2_3",
    "KN2-(4) understanding foreign cultural taboos": "KN2_4",
    "KN2-(5) understanding foreigners’ speech": "KN2_5",
    "KN2-(6) understanding basic concepts of intercultural communication": "KN2_6",
    "KN2-(7) understanding successful intercultural communication strategies": "KN2_7",
    "AT-Attitudes—(1) willingness to learn from those who differ from one’s self and culture": "AT_1",
    "AT-(2) willingness to respect foreigners’ lifestyles and customs": "AT_2",
    "AT-(3) willingness to learn foreign languages and cultures well": "AT_3",
    "SK1-Intercultural communicative skills—(1) the skill of consulting with foreigners when misunderstandings occur": "SK1_1",
    "SK1-(2) the skill of communicating with foreigners using body language or other nonverbal communication when it is difficult to communicate using language": "SK1_2",
    "SK1-(3) the skill of successfully communicating with foreigners": "SK1_3",
    "SK1-(4) the skill of treating foreigners politely": "SK1_4",
    "SK1-(5) the skill of avoiding offending foreigners with inappropriate words and behavior": "SK1_5",
    "SK1-(6) the skill of avoiding prejudice against foreigners": "SK1_6",
    "SK1-(7) the skill of avoiding violating foreigners’ privacy": "SK1_7",
    "SK1-(8) the skill of having intercultural sensitivity": "SK1_8",
    "SK1-(9) the skill of understanding different perspectives when encountering different cultural affairs": "SK1_9",
    "SK2-Intercultural cognitive skills—(1) the skill of acquiring knowledge of other cultures from foreigners": "SK2_1",
    "SK2-(2) the skill of learning intercultural communication strategies": "SK2_2",
    "SK2-(3) the skill of learning how to manage cultural conflicts": "SK2_3",
    "AW-Awareness—(1) realizing cultural differences and similarities when communicating with foreigners": "AW_1",
    "AW-(2) realizing the differences in cultural identity when communicating with foreigners": "AW_2",
    "AW-(3) judging cultural situations from both one’s own and the other’s cultural perspective": "AW_3",
}


def _save(long: pd.DataFrame, out_name: str, cov_cols: list[str]):
    long = long[["id", "item", "resp"] + cov_cols]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"{out_name}.csv"
    long.to_csv(out_path, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert():
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    xl = pd.ExcelFile(io.BytesIO(r.content))

    basic = pd.read_excel(xl, "Basic information of samples")
    basic.columns = [c.strip() for c in basic.columns]
    basic = basic.rename(columns={
        "No.": "id",
        "Age": "cov_age",
        "Gernder(1=Male, 2=Female)": "cov_gender",
        "English Proficiency(IELTS)": "cov_english_ielts",
        "Intercultural Training(1=yes, 2=no)": "cov_intercultural_training",
    })
    basic["id"] = pd.to_numeric(basic["id"], errors="coerce")
    basic = basic.dropna(subset=["id"]).reset_index(drop=True)
    basic["id"] = basic["id"].astype(int)
    assert basic["id"].nunique() == len(basic), "id not unique in basic-info sheet"
    cov_cols = ["cov_age", "cov_gender", "cov_english_ielts", "cov_intercultural_training"]

    # --- Intercultural Contact scale ---
    contact = pd.read_excel(xl, "Intercultural Contact")
    contact.columns = [str(c).strip() for c in contact.columns]
    contact = contact.rename(columns={"No.": "id"})
    contact["id"] = pd.to_numeric(contact["id"], errors="coerce")
    contact = contact.dropna(subset=["id"]).reset_index(drop=True)
    contact["id"] = contact["id"].astype(int)
    assert contact["id"].nunique() == len(contact), "id not unique in contact sheet"

    df = contact[["id"] + CONTACT_ITEMS].merge(basic[["id"] + cov_cols], on="id", how="inner")
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=CONTACT_ITEMS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long[(long["resp"] >= 1) & (long["resp"] <= 5)]
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    _save(long, "yang_2025_intercultural_contact", cov_cols)

    # --- AIC-CCS scale ---
    scores = pd.read_excel(xl, "Intercultural Competence Scores")
    scores.columns = [str(c).strip() if str(c).strip() != "" else c for c in scores.columns]
    id_col = [c for c in scores.columns if str(c).strip() == "No."][0]
    scores = scores.rename(columns={id_col: "id"})
    missing = [c for c in AICCS_ITEMS if c not in scores.columns]
    assert not missing, f"missing AIC-CCS columns: {missing}"
    scores = scores.rename(columns=AICCS_ITEMS)
    scores["id"] = pd.to_numeric(scores["id"], errors="coerce")
    scores = scores.dropna(subset=["id"]).reset_index(drop=True)
    scores["id"] = scores["id"].astype(int)
    assert scores["id"].nunique() == len(scores), "id not unique in scores sheet"

    aiccs_items = list(AICCS_ITEMS.values())
    df2 = scores[["id"] + aiccs_items].merge(basic[["id"] + cov_cols], on="id", how="inner")
    long2 = df2.melt(id_vars=["id"] + cov_cols, value_vars=aiccs_items,
                      var_name="item", value_name="resp")
    long2["resp"] = pd.to_numeric(long2["resp"], errors="coerce")
    long2 = long2[(long2["resp"] >= 1) & (long2["resp"] <= 5)]
    long2 = long2.dropna(subset=["resp"]).reset_index(drop=True)
    _save(long2, "yang_2025_aiccs", cov_cols)


if __name__ == "__main__":
    convert()
