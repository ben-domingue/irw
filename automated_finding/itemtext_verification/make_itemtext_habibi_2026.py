#!/usr/bin/env python3
"""Item text for habibi_2026_teacher_self_concept / _teacher_self_efficacy / _teaching_anxiety / _workload /
_performance (figshare 10.6084/m9.figshare.31672783). Indonesian administration.

Cheap case: data/habibi_2026_teacher_burnout.py stems() reads the Raw sheet's column headers (Indonesian
stems, leading number stripped) in column order, and the deposit's own Coded sheet names those same
columns TSC1..PE4 in the same order, so the code-to-stem tie is the deposit's (column position in two
sheets of one workbook). No anchor text is deposited, so option_text is blank on every point. The
burnout table ships no item text (MBI adaptation; rights register). WOL1 and PE1 are the questionnaire's
block descriptions rather than statements and are kept verbatim. English in *_translated is an IRW
translation.
"""
from _itemtext_writer_c import load_script, row, write

mod = load_script("habibi_2026_teacher_burnout")
TABLES = {"habibi_2026_teacher_self_concept": "Teacher self-concept",
          "habibi_2026_teacher_self_efficacy": "Teacher self-efficacy",
          "habibi_2026_teaching_anxiety": "Teaching anxiety",
          "habibi_2026_workload": "Workload",
          "habibi_2026_performance": "Teacher performance"}
EN = {
    "TSC1": "I think I have good teaching skills and abilities.",
    "TSC2": "I have a reputation as an efficient teacher.",
    "TSC3": "My colleagues regard me as a competent teacher.",
    "TSC4": "I feel I am a worthwhile person.",
    "TSC5": "In general, I am a good teacher.",
    "TSE1": "I help my students value learning.",
    "TSE2": "I motivate students who show low interest in schoolwork.",
    "TSE3": "I improve the understanding of students who are failing.",
    "TSE4": "I provide appropriate challenges for very capable students.",
    "TSE5": "I get students to follow classroom rules.",
    "ANX1": "I feel anxious when preparing lessons or organising my teaching schedule.",
    "ANX2": "I worry about meeting the academic expectations of my students or institution.",
    "ANX3": "I feel nervous when facing unexpected challenges during my teaching sessions.",
    "WOL1": "Workload assesses the effort and time required for teaching tasks.",
    "WOL2": "I feel my teaching responsibilities take up a lot of time.",
    "WOL3": "The effort required to prepare lessons and grade assignments feels very heavy.",
    "WOL4": "I feel my teaching load is too heavy to manage effectively.",
    "PE1": "Performance evaluates teachers' perceived effectiveness in their teaching role.",
    "PE2": "I am confident my teaching methods have a positive impact on my students' learning outcomes.",
    "PE3": "I feel that I perform well in delivering quality education to my students.",
    "PE4": "My teaching approach effectively supports my students' academic progress.",
}


def main():
    stems = dict(mod.stems())
    for table, instrument in TABLES.items():
        rows = []
        for code in mod.BLOCKS[table]:
            for r in range(1, 6):
                rows.append(row(table, f"{table}_1", code, instrument, "Indonesian", r, stems[code], item_text_tr=EN[code]))
        write(table, rows)


if __name__ == "__main__":
    main()
