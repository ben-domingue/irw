#!/usr/bin/env python3
"""Item text for six zhang_2026 (10.1037/pspp0000608, OSF ztxcd) tables.

The cheap case in Step 3.5: the deposit's own Qualtrics files carry the
administered English wording.

- zhang_2026_ipip_{fairness,forgiveness,gratitude,patience}: the stems are the
  choices of the IPIP1/IPIP2 matrix questions in
  S1/materials/Virtue_Affordances_Baseline.qsf. Each is tied to its item code
  by matching the stem text against the codebook's "Item" column
  (S1/data/Codebook Virtue Dilemma - S1.xlsx), which is keyed by the column
  name that data/zhang_2026_virtue_tradeoffs.py keeps as `item`. The
  instructions are the IPIP1 question text, and the options are the matrix
  answers (1 Does not apply at all .. 5 Applies completely). IPIP is `ship`
  in itemtext/instrument_rights_register.csv.
- zhang_2026_virtue_states / zhang_2026_episode_affect: the stems and anchors
  of the per-episode questions in S1/materials/Virtue_Affordances_DRM.qsf,
  taken from the episode-10 copies ("10-fairness" .. "10-meaning"). Every
  episode block repeats them verbatim; the Trash block's bipolar drafts are
  not used. Only 1, 4 and 7 are labelled for the virtues, and 1 and 7 for the
  affect items. The unlabelled points are left blank, not padded. These are
  the authors' own items in a CC BY 4.0 deposit.
Administered in English (US Prolific sample), so there are no language or
_translated columns.
"""
import csv
import io
import json
import re
from pathlib import Path

import pandas as pd
import requests

HERE = Path(__file__).resolve().parent.parent
OUT_DIR = HERE / "itemtext_output"
RESP_DIR = HERE / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
BASELINE = "https://osf.io/download/7tw3s/"
DRM = "https://osf.io/download/vwxjz/"
CODEBOOK = "https://osf.io/download/68e08b1ed3525ab7b56d33d9/"

COLS = ["table", "section_id", "item", "instrument", "instructions",
        "section_prompt", "item_text", "correct_response", "option_text",
        "resp"]


def get(url):
    r = requests.get(url, headers=UA, timeout=300)
    r.raise_for_status()
    return r.content


def text(html):
    s = re.sub(r"<br\s*/?>", " ", html)
    s = re.sub(r"<[^>]+>", "", s).replace("&nbsp;", " ")
    return re.sub(r"\s+", " ", s).strip()


def questions(qsf_bytes):
    q = json.loads(qsf_bytes)
    return {e["Payload"]["DataExportTag"]: e["Payload"]
            for e in q["SurveyElements"] if e.get("Element") == "SQ"}


def norm(s):
    return re.sub(r"[^a-z]", "", s.lower())


def write(table, rows):
    resp = pd.read_csv(RESP_DIR / f"{table}.csv")
    got_items = {r["item"] for r in rows}
    want_items = set(resp["item"].astype(str))
    assert got_items == want_items, (table, got_items ^ want_items)
    got_resp = {float(r["resp"]) for r in rows}
    want_resp = set(resp["resp"].astype(float))
    assert got_resp == want_resp, (table, got_resp ^ want_resp)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / f"{table}__items.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS, quoting=csv.QUOTE_ALL)
        w.writeheader()
        w.writerows(rows)
    print(f"{path.name}: {len(rows)} rows, {len(got_items)} items, "
          f"{len(got_resp)} response options")


def ipip(base, cb):
    stems = {}  # normalized stem -> administered stem
    for tag in ("IPIP1", "IPIP2"):
        p = base[tag]
        for c in p["Choices"].values():
            s = text(c["Display"])
            stems[norm(s)] = s
        answers = [(int(k), text(v["Display"])) for k, v in p["Answers"].items()]
    assert [a for a, _ in answers] == [1, 2, 3, 4, 5]
    instructions = text(base["IPIP1"]["QuestionText"])
    for scale in ("Fairness", "Forgiveness", "Gratitude", "Patience"):
        table = f"zhang_2026_ipip_{scale.lower()}"
        rows = []
        for k in range(1, 5):
            code = f"IPIP_{scale}{k}"
            cb_text = cb.loc[code, "Item"].lstrip(".").strip()
            stem = stems[norm(cb_text)]  # KeyError = no unique tie
            for resp, opt in answers:
                rows.append({"table": table, "section_id": f"{table}_1",
                             "item": code,
                             "instrument": f"IPIP {scale} scale "
                                           "(International Personality "
                                           "Item Pool)",
                             "instructions": instructions,
                             "section_prompt": "", "item_text": stem,
                             "correct_response": "", "option_text": opt,
                             "resp": resp})
        write(table, rows)


def episode(drm):
    virtues = {"fairness": "10-fairness", "patience": "10-patience",
               "courage": "10-courage", "humility": "10-humility",
               "honesty": "10-honesty", "gratitude": "10-gratitude",
               "wisdom": "10-wisdom", "responsibility": "10-responsibility",
               "compassion": "10-compassion", "forgiveness": "10-forgiveness",
               "loyalty": "10-loyalty", "respect": "10-respectful"}
    affect = {"happiness": "10-happiness",
              "socialconnection": "10-socialconnection",
              "meaning": "10-meaning"}
    for table, tags, instrument in [
            ("zhang_2026_virtue_states", virtues,
             "Episode-level virtue state ratings (Day Reconstruction Method "
             "diary)"),
            ("zhang_2026_episode_affect", affect,
             "Episode-level happiness, social connection and meaning "
             "(Day Reconstruction Method diary)")]:
        rows = []
        for code, tag in tags.items():
            p = drm[tag]
            stem = text(p["QuestionText"])
            # "10-respectful" etc. carry the episode header before the stem.
            stem = re.sub(r"^Please answer these questions.*?(?=How )", "",
                          stem)
            assert stem.startswith("How ") and stem.endswith("?"), stem
            for i, c in enumerate(p["Choices"].values(), start=1):
                # Choice labels read "Not at all fair\n1" or just "2": keep
                # the words, drop the printed scale number.
                label = re.sub(r"\s*\d+$", "", text(c["Display"])).strip()
                rows.append({"table": table, "section_id": f"{table}_1",
                             "item": code, "instrument": instrument,
                             "instructions": "", "section_prompt": "",
                             "item_text": stem, "correct_response": "",
                             "option_text": label, "resp": i})
            assert i == 7, (tag, i)
        write(table, rows)


def main():
    base = questions(get(BASELINE))
    drm = questions(get(DRM))
    cb = pd.read_excel(io.BytesIO(get(CODEBOOK))).set_index("Variable Name")
    ipip(base, cb)
    episode(drm)


if __name__ == "__main__":
    main()
