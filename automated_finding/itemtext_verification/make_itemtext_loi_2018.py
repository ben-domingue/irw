#!/usr/bin/env python3
"""Item text for loi_2018_workload_increase / _teacher_self_efficacy / _pos / _exchange_ideology
(figshare 6114659). Qualtrics .sav: each variable label is "<block prompt>-<stem>"; the prompt goes to
section_prompt and the stem (printed "k. " number stripped) to item_text. Value labels are the anchors;
"." marks an unlabeled scale point (left blank). English administration (NSW, Australia).
"""
import re

from _itemtext_writer_c import load_script, row, write

mod = load_script("loi_2018_teacher_work_intensification")
INSTR = {"workload_increase": "Workload increase over the 24 NTSES task statements, 24 items",
         "teacher_self_efficacy": "Norwegian Teacher Self-Efficacy Scale (NTSES), 24 items",
         "pos": "Perceived organisational support ('the organisation' = the school), 16 items",
         "exchange_ideology": "Exchange ideology, 5 items"}


def split(label):
    m = re.search(r"-(?=\d+\. )", label) or re.search(r"\.\.\.-", label) or re.search(r":-", label)
    assert m, label
    prompt, stem = label[:m.start()], label[m.end():]
    if m.group(0) == ":-":
        prompt += ":"
    prompt = prompt.rstrip(".") if prompt.endswith("...") else prompt
    return " ".join(prompt.split()), re.sub(r"^\d+\.\s*", "", " ".join(stem.split()))


def main():
    labels, vlabels = mod.labels()
    for k, instr in INSTR.items():
        cols, valid = mod.BLOCKS[k]
        table = f"loi_2018_{k}"
        rows = []
        for c in cols:
            prompt, stem = split(labels[c])
            vl = vlabels[c]
            for r in valid:
                opt = vl.get(float(r), "")
                rows.append(row(table, f"{table}_1", c, instr, "", r, stem, option_text="" if opt.strip() == "." else opt, section_prompt=prompt))
        write(table, rows)


if __name__ == "__main__":
    main()
