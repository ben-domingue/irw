"""
spotcheck_worth_retrying.py
===========================
Downloads and examines the 12 worth_retrying cases identified in
irw_retriage_ha.csv (4) and irw_retriage_personality.csv (8, 2 skipped).

For each file: shows columns, head, dup structure, and any wave/timepoint cols.
"""

from __future__ import annotations

import io
import re
import sys
import time
from collections import defaultdict
from urllib.parse import urlparse

import requests
import pandas as pd

UA = {"User-Agent": "irw-spotcheck/1.0 (research)"}
TABULAR_EXT = (".csv", ".tsv", ".xlsx", ".xls")
_last_hit: dict = defaultdict(float)


def polite_get(url: str, delay: float = 1.5) -> requests.Response:
    dom = urlparse(url).netloc
    wait = delay - (time.time() - _last_hit[dom])
    if wait > 0:
        time.sleep(wait)
    resp = requests.get(url, headers=UA, timeout=120)
    _last_hit[dom] = time.time()
    resp.raise_for_status()
    return resp


def _dataverse_files(doi: str) -> list[tuple[str, str]]:
    pid = f"doi:{doi}"
    r = polite_get(
        f"https://dataverse.harvard.edu/api/datasets/:persistentId/?persistentId={pid}"
    )
    r.raise_for_status()
    latest = r.json().get("data", {}).get("latestVersion", {})
    out = []
    for f in latest.get("files", []):
        df = f.get("dataFile", {})
        name = df.get("filename", "")
        fid = df.get("id")
        if name.lower().endswith(TABULAR_EXT) and fid:
            out.append((f"https://dataverse.harvard.edu/api/access/datafile/{fid}", name))
    return out


def _figshare_files(url: str) -> list[tuple[str, str]]:
    m = re.search(r"articles/(?:[^/]+/)?(?:[^/]+/)?(\d+)", url)
    if not m:
        return []
    r = polite_get(f"https://api.figshare.com/v2/articles/{m.group(1)}")
    data = r.json()
    out = []
    for f in data.get("files", []):
        name = f.get("name", "")
        dl = f.get("download_url", "")
        if name.lower().endswith(TABULAR_EXT) and dl:
            out.append((dl, name))
    return out


def _osf_files(url: str) -> list[tuple[str, str]]:
    node_id = [s for s in url.rstrip("/").split("/") if s][-1]
    r = polite_get(f"https://api.osf.io/v2/nodes/{node_id}/files/osfstorage/")
    out = []
    for f in r.json().get("data", []):
        name = f.get("attributes", {}).get("name", "")
        dl = f.get("links", {}).get("download", "")
        if name.lower().endswith(TABULAR_EXT) and dl:
            out.append((dl, name))
    return out


def load_file(url: str, name: str) -> pd.DataFrame | None:
    r = polite_get(url)
    src = io.BytesIO(r.content)
    name_l = name.lower()
    try:
        if name_l.endswith((".xlsx", ".xls")):
            return pd.read_excel(src)
        if name_l.endswith(".tsv"):
            return pd.read_csv(src, sep="\t")
        return pd.read_csv(src)
    except Exception as e:
        print(f"  [load error: {e}]")
        return None


WAVE_PATTERNS = re.compile(
    r"\b(wave|time|timepoint|visit|session|phase|occasion|t\d+|pre|post|follow"
    r"|baseline|year|month|week|day|date|survey_date|timestamp)\b",
    re.IGNORECASE,
)


def check_df(df: pd.DataFrame, target_file: str) -> None:
    """Print diagnostic info about a dataframe."""
    print(f"  Shape: {df.shape[0]} rows × {df.shape[1]} cols")
    print(f"  Columns: {list(df.columns)}")

    # Look for wave/time columns
    wave_cols = [c for c in df.columns if WAVE_PATTERNS.search(c)]
    if wave_cols:
        print(f"  *** WAVE/TIME COLS FOUND: {wave_cols} ***")
        for wc in wave_cols[:3]:
            print(f"      {wc} unique values: {sorted(df[wc].dropna().unique()[:15].tolist())}")
    else:
        print("  No obvious wave/time columns")

    # Check for duplicate id×item
    id_candidates = [c for c in df.columns
                     if re.search(r"\bid\b|subject|participant|person|respondent|code", c, re.I)
                     and df[c].nunique() >= max(5, 0.3 * len(df))]
    item_candidates = [c for c in df.columns
                       if re.search(r"\bitem\b|q\d+|question", c, re.I)]

    if id_candidates and item_candidates:
        id_c = id_candidates[0]
        item_c = item_candidates[0]
        n_dup = df.duplicated(subset=[id_c, item_c]).sum()
        print(f"  id candidate='{id_c}' ({df[id_c].nunique()} unique), "
              f"item candidate='{item_c}' ({df[item_c].nunique()} unique), "
              f"dup id×item={n_dup}")

    # Sample
    print("  Head (3 rows):")
    print(df.head(3).to_string(max_cols=10, max_colwidth=20))
    print()


CASES = [
    # --- From irw_retriage_ha.csv (original retriage) ---
    {
        "label": "1. AI Literacy (1146p/54i) — figshare 29488523",
        "source": "figshare",
        "url": "https://figshare.com/articles/dataset/AI_Literacy_Questionnaire_data/29488523",
        "target_file": "AI_Literacy_questionnaire_data_.csv",
    },
    {
        "label": "2. Cognitive Dissonance (1201p/39i) — DVN/XPURU1",
        "source": "dataverse",
        "doi": "10.7910/dvn/xpuru1",
        "target_file": "FullSample.xlsx",
    },
    {
        "label": "3. Body Checking (216p/180i) — osf.io/58xb9",
        "source": "osf",
        "url": "https://osf.io/58xb9/",
        "target_file": "Data – Rawdata.xlsx",
    },
    {
        "label": "4. Conspiracy Belief (373p/109i) — figshare 30903575",
        "source": "figshare",
        "url": "https://figshare.com/articles/dataset/Conspiracy_Belief_and_the_association_with_autistic_traits_schizotypy_cognitive_processes_and_demographics/30903575",
        "target_file": "Questionnaire 1 (Conspiracy Beliefs)_July 16, 2024_08.34.xlsx",
    },
    # --- From irw_retriage_personality.csv ---
    {
        "label": "5. Smoking Cessation (317p/21i) — DVN/8LBLYS",
        "source": "dataverse",
        "doi": "10.7910/dvn/8lblys",
        "target_file": "Unassisted Smoking Cessation MINIMAL ANONYMIZED DATASET.xlsx",
    },
    {
        "label": "6. Language Learning (54p/15i) — DVN/CRSBHT",
        "source": "dataverse",
        "doi": "10.7910/dvn/crsbht",
        "target_file": "Research Raw Data.xlsx",
    },
    {
        "label": "7. Self-esteem/Loneliness Chinese adolescents (181p/50i) — figshare 21515877",
        "source": "figshare",
        "url": "https://frontiersin.figshare.com/articles/dataset/Data_Sheet_1_Self-esteem_mediated_relations_between_loneliness_and_social_anxiety_in_Chinese_adolescents_with_left-behind_experience_CSV/21515877",
        "target_file": "Data_Sheet_1_Self-esteem mediated relations between loneliness and social anxiety in Chinese adolescents with left-behind experience.CSV",
    },
    {
        "label": "8. Aging Male Symptom (620p/17i) — DVN/9V2I0P",
        "source": "dataverse",
        "doi": "10.7910/dvn/9v2i0p",
        "target_file": "ams2012renew.xls",
    },
    {
        "label": "9. Empathy Medical Students (244p/132i) — figshare 16683931",
        "source": "figshare",
        "url": "https://frontiersin.figshare.com/articles/dataset/Data_Sheet_1_Relationship_Between_Medical_Students_Empathy_and_Occupation_Expectation_Mediating_Roles_of_Resilience_and_Subjective_Well-Being_CSV/16683931",
        "target_file": "Data_Sheet_1_Relationship Between Medical Students' Empathy and Occupation Expectation: Mediating Roles of Resilience and Subjective Well-Being.CSV",
    },
]


def process_case(case: dict) -> None:
    print("=" * 70)
    print(case["label"])
    print("=" * 70)

    target = case.get("target_file", "")
    src = case["source"]

    try:
        if src == "figshare":
            files = _figshare_files(case["url"])
        elif src == "dataverse":
            files = _dataverse_files(case["doi"])
        elif src == "osf":
            files = _osf_files(case["url"])
        else:
            print(f"  Unknown source: {src}")
            return
    except Exception as e:
        print(f"  [resolve error: {e}]")
        return

    if not files:
        print("  No tabular files found on landing page!")
        return

    print(f"  Files found: {[name for _, name in files]}")

    # Find the target file (fuzzy match)
    match = None
    for url, name in files:
        if name.lower() == target.lower() or target.lower() in name.lower():
            match = (url, name)
            break
    if match is None:
        # Fall back to first file
        match = files[0]
        print(f"  [target not found exactly — using first file: {match[1]}]")

    url, name = match
    print(f"  Downloading: {name}")
    df = load_file(url, name)
    if df is not None:
        check_df(df, name)


def main():
    for case in CASES:
        try:
            process_case(case)
        except Exception as e:
            print(f"  [ERROR: {e}]")
        print()
    print("Done.")


if __name__ == "__main__":
    main()
