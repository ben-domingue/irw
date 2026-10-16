#!/usr/bin/env python3
"""Item text for the four zhang_2025_* tables (Zenodo 10.5281/zenodo.17958610).

Supp_Mat_B_Codebook.docx ties each code (EU1 ...) to a sub-construct and a keyword;
Supp_Mat_A_Survey.docx lists the full stems under the same sub-construct headings, in the same order.
The builder parses both: the stems are read from the survey in document order within each
sub-construct, and each is checked against the codebook keyword for that code (printed below).
Anchors from the codebook: 1 Strongly Disagree .. 5 Strongly Agree. Administered language not
established (English instrument, Chinese record description).
"""
import re
import zipfile
from pathlib import Path

from _itemtext_writer_c import load_script, row, write

mod = load_script("zhang_2025_chatgpt_deep_learning")
RAW = mod.RAW_DIR
ANCH = {1: "Strongly Disagree", 2: "Disagree", 3: "Neutral", 4: "Agree", 5: "Strongly Agree"}
# sub-construct heading in the survey -> code prefix (codebook order)
SUB = {"Heuristic Use": "EU", "Dependent Use": "DU", "Intrinsic Cognitive Load": "IL",
       "Extraneous Cognitive Load": "EL", "Germane Cognitive Load": "GL", "C. Critical Thinking Scale": "CT",
       "Deep Motive": "DM", "Deep Strategy": "DS", "Intrinsic Goal Orientation": "IG", "Academic Self-Efficacy": "SE"}
INSTR = {"EU": "ChatGPT Learning Behavior Scale", "DU": "ChatGPT Learning Behavior Scale",
         "IL": "Cognitive Load Scale (Leppink et al. 2013)", "EL": "Cognitive Load Scale (Leppink et al. 2013)",
         "GL": "Cognitive Load Scale (Leppink et al. 2013)", "CT": "MSLQ Critical Thinking (Pintrich et al. 1993)",
         "IG": "MSLQ Intrinsic Goal Orientation (Pintrich et al. 1993)", "SE": "MSLQ Academic Self-Efficacy (Pintrich et al. 1993)",
         "DM": "R-SPQ-2F Deep Motive (Biggs et al. 2001)", "DS": "R-SPQ-2F Deep Strategy (Biggs et al. 2001)"}
TABLE = {"EU": "zhang_2025_chatgpt_use", "DU": "zhang_2025_chatgpt_use", "IL": "zhang_2025_cognitive_load",
         "EL": "zhang_2025_cognitive_load", "GL": "zhang_2025_cognitive_load", "CT": "zhang_2025_mslq",
         "IG": "zhang_2025_mslq", "SE": "zhang_2025_mslq", "DM": "zhang_2025_deep_learning", "DS": "zhang_2025_deep_learning"}
INSTRUCTIONS = ("For the main questions, please indicate your level of agreement on a 5-point Likert scale "
                "(1 = Strongly Disagree to 5 = Strongly Agree).")


def paras(fn):
    x = zipfile.ZipFile(RAW / fn).read("word/document.xml").decode("utf8")
    out = [re.sub(r"<[^>]+>", "", p) for p in re.split(r"</w:p>", x)]
    return [re.sub("&amp;", "&", p).replace("&quot;", '"').strip() for p in out if p.strip()]


def survey_stems():
    """prefix -> [stems in order], parsed from Supp_Mat_A_Survey.docx."""
    out, cur = {}, None
    for p in paras("Supp_Mat_A_Survey.docx"):
        if p.startswith("References"):
            break
        head = next((h for h in SUB if p.startswith(h)), None)
        if head:
            cur = SUB[head]
            out.setdefault(cur, [])
            p = p[len(head):]
            p = re.sub(r"^\s*\([^)]*\)", "", p)          # "(Exploratory & Deepening)"
            p = re.sub(r"^[^:]*:(?=\s*\d+\.)", "", p)   # "Please recall ...:" prompt before numbered items
        if cur is None or not p or p.startswith(("Source:", "Part ", "A. ", "B. ", "D. ", "E. ")):
            continue
        for s in re.split(r"(?:^|\s*)\d{1,2}\.\s+", p):
            s = s.strip()
            if len(s) > 15:
                out[cur].append(s)
    return out


def codebook():
    """code -> keyword from Supp_Mat_B_Codebook.docx."""
    ps = paras("Supp_Mat_B_Codebook.docx")
    out = {}
    for i, p in enumerate(ps):
        if re.fullmatch(r"(EU|DU|IL|EL|GL|CT|IG|SE|DM|DS)\d", p):
            out[p] = ps[i + 2]
    return out


def main():
    stems, cb = survey_stems(), codebook()
    assert len(cb) == 32, len(cb)
    rows = {t: [] for t in set(TABLE.values())}
    for pre, ss in stems.items():
        codes = [c for c in cb if c.startswith(pre)]
        assert len(ss) == len(codes), (pre, len(ss), codes, ss)
        for code, stem in zip(codes, ss):
            print(f"{code:<4} {cb[code]:<42} | {stem[:70]}")
            for r in ANCH:
                rows[TABLE[pre]].append(row(TABLE[pre], f"{TABLE[pre]}_1", code, INSTR[pre], "", r, stem,
                                            option_text=ANCH[r], instructions=INSTRUCTIONS))
    for t, rs in rows.items():
        write(t, rs)


if __name__ == "__main__":
    main()
