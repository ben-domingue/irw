#!/usr/bin/env python3
# Item text for the xu_2026_gai_* tables (see xu_2026_gai_creativity.py for
# the response tables).
#
# Source: Appendix A, "Measurement Items and Sources", in S3 File of
# 10.1371/journal.pone.0358186 -- CC BY 4.0 Supporting Information of the
# article. All 44 questionnaire items are printed there in a table whose first
# columns are the construct and the item CODE, so the wording arrives already
# keyed to the same Q-numbers the deposit's columns carry.
#
# THE MAPPING IS CODE-LEVEL AND EXPLICIT, which is unusual for this batch and
# is the thing worth saying. Nothing is read off printed order: the appendix
# labels "I actively try to use GAI to explore new ideas and creativity." as
# Q5, and the deposit has a column named Q5. So unlike guo_2026 (block
# headings plus printed order) or robles_marinos_2023 (block membership only),
# a within-block permutation is not expressible here.
#
# Each construct's items cite their literature source in the appendix's fourth
# column -- March (1991) for exploration and exploitation, Hwang & Lee (2025)
# and McGuire et al. (2024) for co-creation, Phan (2009) for reflection, Sun &
# Rueda (2012) for cognitive stimulation, Csikszentmihalyi (1990) for flow,
# Tierney & Farmer (2002) and Beghetto (2006) for creative self-efficacy, and
# Zhou & George (2001) and Kaufman (2016) for student creativity. What the
# appendix prints is the authors' own GAI-specific adaptation, not those
# sources' wording, so nothing third-party is reproduced.
#
# THE MIDDLE OF THE RESPONSE SCALE SHIPS BLANK. The paper labels the anchors
# only -- 1 "Strongly Disagree" to 5 "Strongly Agree" -- so 2, 3 and 4 get no
# option_text rather than a guessed Disagree / Neutral / Agree. All five resp
# values still carry a row, because the validator requires the item-text resp
# set to match the response table's exactly.
#
# The survey was administered to students at Chinese universities; the
# appendix publishes the items in English only, so the English is what ships.

import csv
import os

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "automated_finding", "itemtext_output")

INSTR = ("Please indicate how strongly you agree or disagree with each of the "
         "following statements about your use of generative AI (GAI) in "
         "learning.")
INSTRUMENT = ("Xu & Zeng (2026) GAI-and-creativity questionnaire, Appendix A "
              "of S3 File")

# table -> (construct, source cited in the appendix, [(code, text), ...])
BLOCKS = {
 "xu_2026_gai_exploration": ("Exploration", "March (1991)", [
    ("Q5", "I actively try to use GAI to explore new ideas and creativity."),
    ("Q6", "During the learning process, I use GAI tools to pose novel questions."),
    ("Q7", "I often explore different functions of GAI tools to discover new uses."),
    ("Q8", "When using GAI, I tend to try unprecedented methods to solve problems."),
    ("Q9", "I am willing to invest time to discover new areas of knowledge within GAI tools."),
 ]),
 "xu_2026_gai_exploitation": ("Exploitation", "March (1991)", [
    ("Q10", "I tend to use GAI to complete learning tasks I am already familiar with."),
    ("Q11", "I use GAI tools to improve task efficiency rather than to seek new ideas."),
    ("Q12", "I rely on GAI technologies to enhance existing solutions."),
    ("Q13", "I apply GAI to refine methods that have worked for me in the past."),
    ("Q14", "I mostly reuse familiar GAI functions to complete tasks."),
 ]),
 "xu_2026_gai_cocreation": ("Co-Creation",
  "Hwang & Lee (2025); McGuire et al. (2024)", [
    ("Q15", "I am able to co-create creative content in collaboration with GAI."),
    ("Q16", "I perceive GAI as a collaborative partner in my creative process, rather than just a tool."),
    ("Q17", "I believe that co-creating with GAI inspires me to generate new and valuable ideas."),
    ("Q18", "In creative tasks, my contributions and GAI’s input complement each other."),
    ("Q19", "GAI’s involvement helps me better solve complex creative problems."),
 ]),
 "xu_2026_gai_reflection": ("Reflection", "Phan (2009)", [
    ("Q20", "I reflect on the learning process assisted by GAI."),
    ("Q21", "I analyze how GAI influences my thinking during collaboration."),
    ("Q22", "After using GAI, I summarize the reasons behind successes and failures."),
    ("Q23", "I evaluate whether the ideas generated with GAI have practical value."),
    ("Q24", "I consider how GAI changes my learning strategies."),
 ]),
 "xu_2026_gai_cognitive_stimulation": ("Perceived Cognitive Stimulation",
  "Sun & Rueda (2012)", [
    ("Q25", "Using GAI prompts me to think more deeply."),
    ("Q26", "GAI's responses encourage me to understand problems from different perspectives."),
    ("Q27", "GAI helps me form new cognitive connections in the learning process."),
    ("Q28", "GAI encourages me to engage in critical thinking."),
    ("Q29", "Interacting with GAI promotes my re-conceptualization of problems."),
 ]),
 "xu_2026_gai_flow": ("Flow Experience", "Csikszentmihalyi (1990)", [
    ("Q30", "When using GAI, I often enter a state of “flow” or deep immersion."),
    ("Q31", "I feel highly focused when interacting with GAI."),
    ("Q32", "I often lose track of time while using GAI."),
    ("Q33", "Collaborating with GAI puts me in a state of full concentration."),
    ("Q34", "Using GAI allows me to become fully engaged in the learning task."),
 ]),
 "xu_2026_gai_creative_self_efficacy": ("Self-efficacy in Creativity",
  "Tierney & Farmer (2002); Beghetto (2006)", [
    ("Q35", "I believe I can use generative AI (GAI) to develop creative solutions."),
    ("Q36", "Even when tasks are challenging, I can come up with novel ideas with the help of GAI."),
    ("Q37", "I am able to flexibly use the knowledge provided by GAI to generate new ideas."),
    ("Q38", "I have the ability to produce unique creative outcomes using GAI."),
    ("Q39", "I am confident that I can perform well in creative tasks assisted by GAI."),
 ]),
 "xu_2026_gai_student_creativity": ("Student Creativity",
  "Zhou & George (2001); Kaufman (2016)", [
    ("Q40", "I can propose distinctive learning ideas or solutions with the assistance of GAI."),
    ("Q41", "My GAI-assisted work often demonstrates unique forms of expression."),
    ("Q42", "I am able to integrate knowledge from different domains provided by GAI into new ideas."),
    ("Q43", "I often try to complete assignments using novel approaches suggested by GAI."),
    ("Q44", "I believe that the works produced with GAI-assisted learning are creative."),
 ]),
}

# the paper labels the two anchors and nothing in between -- see the header
OPTIONS = [(1, "Strongly Disagree"), (2, ""), (3, ""), (4, ""),
           (5, "Strongly Agree")]

COLS = ["table", "section_id", "item", "instrument", "instructions",
        "section_prompt", "item_text", "correct_response", "option_text",
        "resp"]


def build():
    os.makedirs(OUT, exist_ok=True)
    n_items = 0
    for table, (construct, source, items) in BLOCKS.items():
        rows = []
        for code, text in items:
            for resp, label in OPTIONS:
                rows.append({"table": table, "section_id": table + "_1",
                             "item": code, "instrument": INSTRUMENT,
                             "instructions": INSTR,
                             "section_prompt": f"{construct} (items adapted "
                                               f"from {source})",
                             "item_text": text, "correct_response": "",
                             "option_text": label, "resp": resp})
        assert len(rows) == len(items) * len(OPTIONS)
        with open(os.path.join(OUT, table + "__items.csv"), "w",
                  newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=COLS, quoting=csv.QUOTE_ALL)
            w.writeheader()
            w.writerows(rows)
        n_items += len(items)
        print(f"{table}__items.csv: {len(items)} items, {len(rows)} rows")
    assert n_items == 40, n_items
    print(f"{len(BLOCKS)} item-text tables, {n_items} items (every one of the "
          f"response tables' items)")


if __name__ == "__main__":
    build()
