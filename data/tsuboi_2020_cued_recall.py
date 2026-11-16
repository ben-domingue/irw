#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/jcwyb2knb6/1
# DOI: 10.17632/jcwyb2knb6.1 (data); paper 10.1016/j.jml.2020.104155
#   Tsuboi N, Francis WS (2020). Rethinking bilingual enhancement effects in associative learning
#   of foreign language vocabulary: The role of proficiency in the mediating language. Journal of
#   Memory and Language 115: 104155.
# License: CC BY-NC 3.0 (Mendeley Data record) -> Derived License CC BY-NC 3.0
# Data: one PsyScope/Excel workbook per participant ("ED 01.xlsx" ...) plus
#   Experiment_1_06-08-20.sav (144 participants: English monolinguals EM, English-dominant ED and
#   Spanish-dominant SD bilinguals, 48 each, with variable and value labels).
#   Task: paired-associate learning of 40 Japanese words, then cued recall of each word's English
#   translation. In each workbook the experimenter's scoring block, under the first "Correct Info"
#   header, lists the correct English word, the typed response and a 0/1 accuracy for each of the
#   40 pairs.
#
# Table: tsuboi_2020_cued_recall -- item = "recall_<English target word>_en" (40 items, the same
#   40 for all participants; the affixes keep targets like "place" and "response" from reading as
#   covariate names in irw_lint_covariates), resp = cued recall correct (1) / incorrect (0), as scored by the experimenters.
#   Check: for every participant the 40 item scores sum to 10 x (RecallVC + RecallVA + RecallAC +
#   RecallAA) in the .sav, whose four scores are per-block proportions correct out of 10.
#   Workbooks EM 43 and SD 12 are the .sav's "EM43R" and "SD12R" (re-run sessions).
#   EM 22 is dropped: its workbook's AC block repeats the AA word list, so its 10 concrete-
#   auditory words cannot be identified (143 participants ship; all 143 pass the check above).
#   Not shipped: the recognition test (a second scoring block of 2-alternative decisions) and
#   Experiment 2 (40 Japanese-dominant bilinguals, different target words; N < 100).
# id: the participant code (EM01 ...), which encodes the language group.
# Covariates: cov_group (English monolingual / English dominant / Spanish dominant), cov_sex, cov_age.
# Item text: not shipped -- the items are word pairs; the Japanese-English pairs are in each
#   workbook's trial log, not in a stimulus file.
import io
import re
import sys
from pathlib import Path

import pandas as pd
import pyreadstat
import requests
import tempfile
import time

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402


def gate(t):
    fails = [c for c in run_qc(t) if c.status == "fail"]
    assert not fails, fails


OUT = REPO_ROOT / "automated_finding" / "irw_output"
API = "https://data.mendeley.com/public-api/datasets/jcwyb2knb6"
WORDS = """place response south war dream legend finish fault move lift deed shame sadness bribe youth aid stubborn freedom advice heritage song movie blanket mail fence nose bee money throat water hair balloon rice furniture needle street hat gift eagle fire""".split()  # the 40 English targets
GROUP = {"EM": "English monolingual", "ED": "English dominant", "SD": "Spanish dominant"}


def get(url):
    for attempt in range(5):
        try:
            r = requests.get(url, timeout=120)
            r.raise_for_status()
            return r
        except requests.exceptions.RequestException:
            if attempt == 4:
                raise
            time.sleep(5 * (attempt + 1))


def parse(content):
    d = pd.read_excel(io.BytesIO(content), header=None)
    hits = [(r, c) for r in range(min(40, len(d))) for c in range(d.shape[1])
            if str(d.iat[r, c]).strip() == "Correct Info"]
    r0, ci = min(hits)  # the first block is cued recall; the second is recognition
    out = {}
    for r in range(r0 + 1, len(d)):
        word, acc = d.iat[r, ci], str(d.iat[r, ci + 2]).strip()
        if isinstance(word, str) and word.strip() and acc in ("0", "1", "0.0", "1.0"):
            out.setdefault(word.strip().lower(), int(float(acc)))
    return out


def main():
    meta = get(API).json()
    files = {f["filename"]: f["content_details"]["download_url"] for f in meta["files"]}
    with tempfile.NamedTemporaryFile(suffix=".sav") as f:
        f.write(get(files["Experiment_1_06-08-20.sav"]).content)
        f.flush()
        sav, _ = pyreadstat.read_sav(f.name)
    assert len(sav) == 144
    sav["code"] = sav["ID"].str.replace(" ", "").str.upper().str.replace(r"R$", "", regex=True)
    rows, dropped = [], []
    for name, url in sorted(files.items()):
        m = re.match(r"^(EM|ED|SD) ?(\d+)\.xlsx$", name)
        if not m:
            continue
        code = m.group(1) + m.group(2)
        rec = parse(get(url).content)
        s = sav[sav["code"] == code]
        assert len(s) == 1, code
        s = s.iloc[0]
        if not set(WORDS) <= set(rec):
            print("dropped", code, "-- scoring block lacks", sorted(set(WORDS) - set(rec)))
            dropped.append(code)
            continue
        scores = {w: rec[w] for w in WORDS}  # other matches in the block are its labels ("ac", "aa")
        total = round(10 * (s.RecallVC + s.RecallVA + s.RecallAC + s.RecallAA))
        assert sum(scores.values()) == total, (code, sum(scores.values()), total)
        for w, a in scores.items():
            rows.append({"id": code, "item": f"recall_{w}_en", "resp": a, "cov_group": GROUP[m.group(1)],
                         "cov_sex": {"F": "female", "M": "male"}[s.Gender], "cov_age": s.Age})
    t = pd.DataFrame(rows)
    assert len(dropped) <= 3 and t["id"].nunique() == 144 - len(dropped)
    assert t["item"].nunique() == 40 and len(t) == t["id"].nunique() * 40
    assert not t.duplicated(["id", "item"]).any()
    t = t.sort_values(["id", "item"])
    gate(t)
    t.to_csv(OUT / "tsuboi_2020_cued_recall.csv", index=False)
    print(len(t), t.id.nunique(), t.item.nunique(), round(t.resp.mean(), 3))


if __name__ == "__main__":
    main()
