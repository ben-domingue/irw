#!/usr/bin/env python3
"""Item text for prasetiyo_2022_aq / _act / _sct / _tpack (Mendeley Data 10.17632/bdzjtff5bh).

Cheap case: the deposited questionnaire (.docx, English) lists Part A-D statements in the same order as
the xlsx item columns (C1..E3, A1..Un6, Wr1..Cr4, TPACK1-5), so the k-th statement of a part is tied to
the k-th code of that part -- a positional mapping, recorded as such in mapping_verification.csv.
Anchors are the questionnaire's 5 Strongly Agree .. 1 Strongly Disagree. Administration language not
stated (Indonesian teachers); `language` left blank.
"""
import re
import zipfile

from _itemtext_writer_c import HERE, load_script, row, write

mod = load_script("prasetiyo_2022_teacher_ict")
DOCX = HERE / "runs" / "raw" / "10_17632_bdzjtff5bh" / "Questionnaire_An Investigation of TPACK among Indonesian Teachers.docx"
PARTS = {"prasetiyo_2022_aq": ("Part A. Adversity Quotient", "Adversity Quotient"),
         "prasetiyo_2022_act": ("Part B. Attitude Computer Technology", "Attitude Computer Technology"),
         "prasetiyo_2022_sct": ("Part C. Self-Efficacy with Computer Technology", "Self-Efficacy with Computer Technology"),
         "prasetiyo_2022_tpack": ("Part D. TPACK", "TPACK")}
OPTS = {5: "Strongly Agree", 4: "Agree", 3: "Neutral", 2: "Disagree", 1: "Strongly Disagree"}
INSTRUCTIONS = ("For each statement in the survey, please indicate how much you agree or disagree with the statement "
                "by putting in the box on the right side of each statement. There are no right or wrong answers.")
SKIP = {"Questions", "5", "4", "3", "2", "1", "Strongly Agree", "Agree", "Neutral", "Disagree", "Strongly Disagree"}


def paragraphs():
    x = zipfile.ZipFile(DOCX).read("word/document.xml").decode()
    ps = [re.sub("<[^>]+>", "", m) for m in re.findall(r"<w:p[ >].*?</w:p>", x, flags=re.S)]
    return [p.replace("&amp;", "&").replace("&gt;", ">").strip() for p in ps if p.strip()]


def main():
    ps = paragraphs()
    heads = [h for h, _ in PARTS.values()] + ["—  Thank You —"]
    for table, (head, instrument) in PARTS.items():
        i = ps.index(head)
        j = min(ps.index(h) for h in heads if h != head and ps.index(h) > i)
        stems = [p for p in ps[i + 1:j] if p not in SKIP]
        codes = mod.BLOCKS[table]
        assert len(stems) == len(codes), (table, len(stems), len(codes))
        rows = []
        for code, stem in zip(codes, stems):
            for r in sorted(OPTS):
                rows.append(row(table, f"{table}_1", code, instrument, "", r, stem, option_text=OPTS[r],
                                instructions=INSTRUCTIONS))
        write(table, rows)


if __name__ == "__main__":
    main()
