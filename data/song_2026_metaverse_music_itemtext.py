#!/usr/bin/env python3
# Item text for ten of the eleven song_2026_mm_* tables (see
# song_2026_metaverse_music.py for the response tables).
#
# Source: "S2 Appendix. Measurement items" of 10.1371/journal.pone.0348632 --
# CC BY 4.0 Supporting Information of the article, which lists all 33 items
# under their construct headings WITH THEIR CODES (ER1, AN2, ... CCB3), so
# the mapping to the deposit's columns is code-level for the ten blocks whose
# prefixes match.
#
# THE ELEVENTH TABLE IS NOT COVERED. The appendix publishes content creation
# behaviour as CCB1-3; the deposit's corresponding block is MRCC with SIX
# columns. The article says three items were retained per focal construct, so
# CCB is presumably three of those six, but nothing identifies which, and
# attaching three stems to six unlabelled columns would be a guess. The
# response table ships all six administered items with no text.
#
# OPTION TEXT IS FULLY PUBLISHED FOR ONCE. The S1 Appendix states the response
# format outright: "1 = Strongly disagree, 2 = Disagree, 3 = Neutral,
# 4 = Agree, 5 = Strongly agree" -- all five labels, so none has to be left
# blank as in most of this batch.
#
# The items were administered in Chinese via Sojump; the appendix is headed
# "English translation of the administered questionnaire", so what ships is
# the authors' own English rendering.

import csv
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from song_2026_metaverse_music import CONSTRUCTS, RAW  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "automated_finding", "itemtext_output")
INSTRUMENT = ("Song et al. (2026) metaverse music platform questionnaire "
              "(S2 Appendix, Measurement items)")
INSTR = ("Thinking about your metaverse music platform experience, please "
         "rate each statement on a 5-point scale.")
OPTIONS = [(1, "Strongly disagree"), (2, "Disagree"), (3, "Neutral"),
           (4, "Agree"), (5, "Strongly agree")]
SOURCES = {"ER": "[38]", "AN": "[21]", "SP": "[23]", "SE": "[39]"}

ITEMS = {
 "ER": ["I feel a strong emotional connection to the music in this metaverse music experience.",
        "The emotions conveyed by the music match how I feel during this experience.",
        "The music in this experience moves me emotionally."],
 "AN": ["This metaverse music experience is unique in its look and sound.",
        "The aesthetic design of this experience satisfies my curiosity.",
        "The visual and auditory styling makes me feel like an adventurer."],
 "SP": ["I felt like I was in the presence of another person in this metaverse music experience.",
        "I felt that the people in this metaverse music experience were aware of my presence.",
        "I had a sense that I was interacting with other people in this experience, not just with the system."],
 "SE": ["I felt connected with artists during this metaverse music experience.",
        "I felt a sense of togetherness with other audience members during this metaverse music experience.",
        "I felt that the metaverse music experience was shared with others."],
 "AC": ["I can freely customize my avatar’s appearance in this metaverse music platform.",
        "This metaverse music platform provides sufficient options to customize my avatar to my preferences.",
        "I feel I have control over many aspects of my avatar’s look (e.g., clothing, accessories) in this metaverse music platform."],
 "NA": ["During this metaverse music experience, I was impatient to find out how the story would end.",
        "During this metaverse music experience, I was eager to see how everything would play out.",
        "This experience aroused my curiosity about what would happen next."],
 "MS": ["This experience makes a strong impression on my visual and other senses.",
        "This metaverse music experience appeals to my senses.",
        "I find this metaverse music experience interesting for discovering new sensory experiences."],
 "FE": ["During this metaverse music experience, I was absorbed in what I was doing.",
        "All my attention was on this metaverse music experience.",
        "My actions flowed effortlessly during this metaverse music experience."],
 "EVP": ["I enjoyed this metaverse music experience.",
         "I felt emotionally uplifted during this metaverse music experience.",
         "This metaverse music experience gave me pleasure."],
 "TA": ["Learning to use this metaverse music platform is easy for me.",
        "My interaction with this metaverse music platform is clear and understandable.",
        "I find this platform uncomplicated and not mentally demanding to use."],
}
COLS = ["table", "section_id", "item", "instrument", "instructions",
        "section_prompt", "item_text", "correct_response", "option_text",
        "resp"]


def build():
    cols = set(str(c).strip() for c in pd.read_excel(RAW, nrows=1).columns)
    os.makedirs(OUT, exist_ok=True)
    n_items = 0
    for prefix, texts in ITEMS.items():
        name, n, label = CONSTRUCTS[prefix]
        assert len(texts) == n == 3, (prefix, len(texts), n)
        rows = []
        for i, text in enumerate(texts, 1):
            code = f"{prefix}{i}"
            assert code in cols, f"{code} is not a column in the deposit"
            prompt = label + (f" (items from {SOURCES[prefix]})"
                              if prefix in SOURCES else "")
            for resp, lab in OPTIONS:
                rows.append({"table": name, "section_id": name + "_1",
                             "item": code, "instrument": INSTRUMENT,
                             "instructions": INSTR, "section_prompt": prompt,
                             "item_text": text, "correct_response": "",
                             "option_text": lab, "resp": resp})
        with open(os.path.join(OUT, name + "__items.csv"), "w",
                  newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=COLS, quoting=csv.QUOTE_ALL)
            w.writeheader()
            w.writerows(rows)
        n_items += len(texts)
        print(f"{name}__items.csv: {len(texts)} items, {len(rows)} rows")
    assert n_items == 30, n_items
    print("10 item-text tables, 30 items. The eleventh response table "
          "(song_2026_mm_content_creation) ships 6 administered items with "
          "no text -- see the header")


if __name__ == "__main__":
    build()
