"""Item text for rollcall_house and rollcall_senate (irw#2445).

Each item is one roll-call vote, and its wording is the question as the chamber
recorded it, read from the same XML file that supplies that vote's yeas and
nays (data/rollcall_congress.py). The item code is built from the file's own
congress / session / roll-number fields, so code and text cannot be mismatched
-- no positional inference.

  House (Clerk EVS XML, vote-metadata): "<vote-question>: <legis-num>", then
    the amendment's sponsor line ("amendment-author") or the short description
    ("vote-desc") when the Clerk gives one. The Clerk's XML carries no bill
    titles, so a House item names the measure by number (e.g. "H R 21").
  Senate (LIS XML): vote_question_text, then vote_document_text (the
    nomination, bill title or amendment purpose) when it adds anything.

option_text is the chamber's own vote wording: House "Yea"/"Aye" and "Nay"/"No"
(recorded votes say Aye/No, yea-and-nay votes Yea/Nay; both are listed), Senate
"Yea"/"Nay", and "Guilty"/"Not Guilty" on impeachment-trial articles. resp
matches the response table: 1 for, 0 against.

section_id groups a Congress-session. instructions and section_prompt are
blank: a roll call has none. Public-domain US Government records (17 U.S.C.
105), as the response tables.

Reads the XML cache written by data/rollcall_congress.py (run that first; the
default cache is ~/.cache/irw_rollcall) and never fetches.
"""
import argparse
import gzip
import os
import re
import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent.parent
OUT_DIR = HERE / "itemtext_output"
RESP_DIR = HERE / "irw_output"
COLS = ["table", "section_id", "item", "instrument", "instructions",
        "section_prompt", "item_text", "correct_response", "option_text", "resp"]
INSTRUMENT = {
    "house": "U.S. House of Representatives recorded votes (Office of the Clerk)",
    "senate": "U.S. Senate roll-call votes (Secretary of the Senate)",
}
SESSION = {"1st": 1, "2nd": 2, "3rd": 3}


def clean(s):
    return re.sub(r"\s+", " ", (s or "")).strip()


def house_items(cache):
    out = []
    for f in sorted((cache / "house").glob("*/roll*.xml.gz")):
        md = ET.fromstring(gzip.open(f).read()).find("vote-metadata")
        c = int(md.findtext("congress"))
        sess = SESSION[md.findtext("session").strip()]
        item = f"{c}_{sess}_{int(md.findtext('rollcall-num')):04d}"
        text = clean(md.findtext("vote-question"))
        legis = clean(md.findtext("legis-num"))
        if legis and legis != "0":
            text += f": {legis}"
        extra = clean(md.findtext("amendment-author")) or clean(md.findtext("vote-desc"))
        if extra:
            text += f" ({extra})"
        opts = [("Yea / Aye", 1), ("Nay / No", 0)]
        out.append((c, sess, item, text, opts))
    return out


def senate_items(cache):
    out = []
    for f in sorted((cache / "senate").glob("*_*/vote_*.xml.gz")):
        r = ET.fromstring(gzip.open(f).read())
        c, sess = int(r.findtext("congress")), int(r.findtext("session"))
        item = f"{c}_{sess}_{int(r.findtext('vote_number')):05d}"
        text = clean(r.findtext("vote_question_text"))
        doc = clean(r.findtext("vote_document_text"))
        if doc and doc not in text:
            text += f" -- {doc}"
        casts = {clean(m.findtext("vote_cast")) for m in r.iter("member")}
        if casts & {"Guilty", "Not Guilty"}:
            opts = [("Guilty", 1), ("Not Guilty", 0)]
        else:
            opts = [("Yea", 1), ("Nay", 0)]
        out.append((c, sess, item, text, opts))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default=os.path.expanduser("~/.cache/irw_rollcall"))
    ap.add_argument("--resp-dir", default=str(RESP_DIR))
    ap.add_argument("--out", default=str(OUT_DIR))
    a = ap.parse_args()
    cache = Path(a.cache)
    os.makedirs(a.out, exist_ok=True)
    for ch, fn in (("house", house_items), ("senate", senate_items)):
        table = f"rollcall_{ch}"
        resp = pd.read_csv(Path(a.resp_dir) / f"{table}.csv", usecols=["item", "resp"],
                           dtype={"item": str})
        keep = set(resp["item"])
        rows = []
        for c, sess, item, text, opts in fn(cache):
            if item not in keep:   # quorum calls, Speaker elections, other Congresses
                continue
            for opt, k in opts:
                rows.append({"table": table, "section_id": f"{table}_{c}_{sess}",
                             "item": item, "instrument": INSTRUMENT[ch],
                             "instructions": "", "section_prompt": "",
                             "item_text": text, "correct_response": "",
                             "option_text": opt, "resp": k})
        out = pd.DataFrame(rows, columns=COLS)
        assert not out.duplicated(["item", "resp"]).any(), f"{table}: duplicate item/resp"
        assert set(out["item"]) == keep, f"{table}: item sets differ"
        live = set(map(tuple, resp.drop_duplicates().itertuples(index=False)))
        assert live <= set(zip(out["item"], out["resp"])), f"{table}: resp values not covered"
        assert (out["item_text"] != "").all(), f"{table}: blank item_text"
        path = Path(a.out) / f"{table}__items.csv"
        out.to_csv(path, index=False)
        print(f"{path.name}: {out['item'].nunique():,} items, {len(out):,} rows")


if __name__ == "__main__":
    main()
