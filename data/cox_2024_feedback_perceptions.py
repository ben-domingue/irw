from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0300205
# DOI: 10.1371/journal.pone.0300205
# Cox & Arthur (2024), "Feedback perceptions of first year medical
# residents: An intervention-based survey study". S1 Dataset. CC BY 4.0.
# N=29. 5-item feedback-perceptions survey administered pre- and
# post-intervention (wave=1/2), 1-5 Likert; item text kept from the
# source column headers via ITEM_MAP.
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0300205.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

PRE_MAP = {
    "PreQ1: How confident are you in your ability to procure feedbackin your residency training?": "confidence",
    "PreQ2: How interested are you in receiving feedback throughoutyour residency training?": "interest",
    "PreQ3: How much effort will you put into procuring feedbackduring residency training?": "effort",
    "PreQ4: How important is feedback to your residency training?": "importance",
    "PreQ5: How often will you seek feedback from a faculty memberin your residency training?": "frequency",
}
POST_MAP = {
    "PostQ1: How confident are you in your ability to procure feedbackin your residency training?": "confidence",
    "PostQ2: How interested are you in receiving feedback throughoutyour residency training?": "interest",
    "PostQ3: How much effort will you put into procuring feedbackduring residency training?": "effort",
    "PostQ4: How important is feedback to your residency training?": "importance",
    "PostQ5: How often will you seek feedback from a faculty memberin your residency training?": "frequency",
}


def fetch() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content))


def convert():
    df = fetch().rename(columns={"Participant Code": "id"})
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    pre = df[["id"] + list(PRE_MAP.keys())].rename(columns=PRE_MAP)
    pre_long = pre.melt(id_vars=["id"], var_name="item", value_name="resp")
    pre_long["wave"] = 1

    post = df[["id"] + list(POST_MAP.keys())].rename(columns=POST_MAP)
    post_long = post.melt(id_vars=["id"], var_name="item", value_name="resp")
    post_long["wave"] = 2

    long = pd.concat([pre_long, post_long], ignore_index=True)
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp", "wave"]]
    out_path = OUT_DIR / "cox_2024_feedback_perceptions.csv"
    long.to_csv(out_path, index=False)
    print(f"cox_2024_feedback_perceptions: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
