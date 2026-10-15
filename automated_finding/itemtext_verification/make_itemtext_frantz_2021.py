#!/usr/bin/env python3
"""Item text for frantz_2021_env_concern / _env_commitment / _env_norms / _cns / _empathy (Zenodo 5171463).

Stems and anchors from the .sav variable/value labels: Study 1's file for concern, commitment items
1-10, norms and CNS; Study 3's file for commitment 11-13 and empathy (Study 2's Empathy value labels are
keyed 14-18, Study 3's 1-5). Study 1 labels the agreement scale Disagree / Agree where Studies 2-3 read
Slightly Disagree / Slightly Agree; Study 1 wording is shipped. Unlabeled scale points ("&nbsp;") are
left blank. English administration.
"""
import re

from _itemtext_writer_c import load_script, row, write

mod = load_script("frantz_2021_community_voices")


def clean(s):
    s = re.sub(r"&nbsp;?", "", s or "").strip()
    return re.sub(r"^How (concerned|committed)\s*-\s*", "", s)


def rows_for(table, items, labels, vlabels, instr, prompt, recode=None):
    """recode: Study 1's Commit coding {source code: shipped resp}; option labels are keyed by source code."""
    out = []
    for c in items:
        vl = vlabels[c]
        if recode:
            vl = {float(recode[int(k)]): v for k, v in vl.items() if int(k) in recode}
        for r in range(1, 6):
            out.append(row(table, f"{table}_1", c, instr, "", r, clean(labels[c]), option_text=clean(vl.get(float(r), "")), section_prompt=prompt))
    return out


def main():
    l1, v1 = mod.labels(1)
    l3, v3 = mod.labels(3)
    write("frantz_2021_env_concern", rows_for("frantz_2021_env_concern", mod.CONCERN, l1, v1, "Environmental concern, 14 items",
                                              "How concerned are you with the following environmental problems?"))
    rows = rows_for("frantz_2021_env_commitment", mod.COMMIT[:10], l1, v1, "Commitment to pro-environmental actions, 13 items",
                    "How committed are you to the following actions?", recode=mod.S1_COMMIT)
    rows += rows_for("frantz_2021_env_commitment", mod.COMMIT[10:], l3, v3, "Commitment to pro-environmental actions, 13 items",
                     "How committed are you to the following actions?")
    write("frantz_2021_env_commitment", rows)
    write("frantz_2021_env_norms", rows_for("frantz_2021_env_norms", mod.NORMS, l1, v1, "Efficacy, responsibility, optimism and youth/adult norms, 19 items",
                                            "Rate the degree to which you agree with the following statements"))
    write("frantz_2021_cns", rows_for("frantz_2021_cns", mod.CNS, l1, v1, "Connectedness to Nature Scale, 5 items",
                                      "Rate the degree to which you agree with the following statements"))
    write("frantz_2021_empathy", rows_for("frantz_2021_empathy", mod.EMP, l3, v3, "Empathy toward the people in the slides, 3 items",
                                          "Please think about how you felt when you watched the slides"))


if __name__ == "__main__":
    main()
