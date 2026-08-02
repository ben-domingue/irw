from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0327359
# DOI: 10.1371/journal.pone.0327359
# Qiang et al. (2025), "Does the perception of red tape affect the
# emotional labor of frontline retail staff in China? A post-COVID-19
# era". S1 File. CC BY 4.0. N=396. 1-5 Likert throughout.
# Column-prefix blocks RE (red tape, 10i) and NE (4i, unlabeled) shipped
# under their source codes. The remaining columns carry full item text
# (numbered 17-42 in the original questionnaire) and split cleanly by
# content into 5 more scales: job performance (17-21), value suppression/
# surface acting (22-24), job dissatisfaction (25-29), coping (30-32),
# workplace friendship (33-37, dropping item 35's Chinese-language
# duplicate of item 36), abusive supervision (38-41). Item 42 (daily
# overtime) is a single item, not shipped. The ambiguous duplicate
# CO-1..CO-4 / CO-1.1..CO block (8 columns, unclear whether a distinct
# construct or a raw-file artifact) is also not shipped.
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0327359.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_MAP = {"GENDER": "cov_gender", "AGE": "cov_age"}

JOB_PERF = {
    "17、I often perform my job duties very well.": "jp1",
    "18、I am able to meet the requirements of my job.": "jp2",
    "19、I rarely make mistakes when completing my work.": "jp3",
    "20、I never neglect the things I am supposed to do.": "jp4",
    "21、I always fulfill my job responsibilities well.": "jp5",
}
SURFACE_ACTING = {
    "22、I suppress my own values when they differ from those of the organization.": "sa1",
    "23、My behavior reflects the organization’s values, even if they are inconsistent with my personal beliefs.": "sa2",
    "24、I say things at work that I do not actually believe.": "sa3",
}
DISSATISFACTION = {
    "25、I do not enjoy my job; I just invest time to get paid.": "diss1",
    "26、Facing my daily tasks is a painful and boring experience.": "diss2",
    "27、My job feels more like a chore or a burden.": "diss3",
    "28、I often wish I were doing something else.": "diss4",
    "29、Over the years, I have become disappointed with my job.": "diss5",
}
COPING = {
    "30、If I encounter problems at work, I will solve them no matter what.": "cope1",
    "31、I usually remain calm in the face of work-related stress.": "cope2",
    "32、In my current job, I feel capable of handling many tasks simultaneously.": "cope3",
}
FRIENDSHIP = {
    "33、I have built strong friendships at work.": "fr1",
    "34、I socialize with my colleagues outside the workplace.": "fr2",
    "36、I can confide in my colleagues.": "fr3",
    "37、I feel I can truly trust many of my coworkers.": "fr4",
}
ABUSIVE_SUP = {
    "38、My supervisor does not praise me for the efforts I make at work.": "as1",
    "39、My supervisor avoids embarrassment by blaming me.": "as2",
    "40、My supervisor gives me the silent treatment.": "as3",
    "41、My supervisor takes out their anger on me when upset about other matters.": "as4",
}

RE_ITEMS = [f"RE-{i}" for i in range(1, 11)]
NE_ITEMS = [f"NE-{i}" for i in range(1, 5)]


def fetch() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
    return df.rename(columns={**COV_MAP, "序号": "id"})


def _ship(df, cov_cols, item_cols, item_map, out_name):
    sub = df[["id"] + cov_cols + item_cols].rename(columns=item_map) if item_map else df[["id"] + cov_cols + item_cols]
    long = sub.melt(id_vars=["id"] + cov_cols,
                     value_vars=[item_map[c] if item_map else c for c in item_cols],
                     var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_cols]
    long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert():
    df = fetch()
    cov_cols = [c for c in COV_MAP.values() if c in df.columns]
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    _ship(df, cov_cols, RE_ITEMS, None, "qiang_2025_red_tape")
    _ship(df, cov_cols, NE_ITEMS, None, "qiang_2025_ne_scale")
    _ship(df, cov_cols, list(JOB_PERF.keys()), JOB_PERF, "qiang_2025_job_performance")
    _ship(df, cov_cols, list(SURFACE_ACTING.keys()), SURFACE_ACTING, "qiang_2025_surface_acting")
    _ship(df, cov_cols, list(DISSATISFACTION.keys()), DISSATISFACTION, "qiang_2025_job_dissatisfaction")
    _ship(df, cov_cols, list(COPING.keys()), COPING, "qiang_2025_coping")
    _ship(df, cov_cols, list(FRIENDSHIP.keys()), FRIENDSHIP, "qiang_2025_workplace_friendship")
    _ship(df, cov_cols, list(ABUSIVE_SUP.keys()), ABUSIVE_SUP, "qiang_2025_abusive_supervision")


if __name__ == "__main__":
    convert()
