#!/usr/bin/env python3
"""Item text for habibi_2021_pe_tsc and habibi_2021_pe_te (Mendeley b6zh5mjd5p). Indonesian stems and the
authors' English from "1. Instrument in English and Indonesian.docx", positional by printed number within
block = column number (TSC1..5, TE1..5). Anchors: the docx's Indonesian scale (1 Sangat Tidak Setuju ...
5 Sangat Setuju), English = the usual agreement anchors. Indonesian administration."""
from _itemtext_writer_c import load_script, row, write

mod = load_script("habibi_2021_pe_teacher_burnout")
ID_ = {
    "TSC1": "Saya pikir saya memiliki keterampilan dan kemampuan mengajar yang baik selama Pandemi Covid-19",
    "TSC2": "Saya memiliki reputasi sebagai guru yang efisien dalam mengajar selama Pandemi Covid-19",
    "TSC3": "Rekan-rekan saya menganggap saya sebagai guru yang kompeten dalam mengajar selama Pandemi Covid-19",
    "TSC4": "Saya merasa saya orang yang berharga dalam mengajar selama Pandemi Covid-19",
    "TSC5": "Secara umum, saya adalah guru yang baik dalam mengajar selama Pandemi Covid-19",
    "TE1": "Saya membantu siswa saya menghargai pembelajaran selama Pandemi Covid-19",
    "TE2": "Saya memotivasi siswa yang menunjukkan minat rendah dalam pekerjaan sekolah selama Pandemi Covid-19",
    "TE3": "Saya meningkatkan pemahaman siswa yang gagal selama Pandemi Covid-19",
    "TE4": "Saya memberikan tantangan yang sesuai untuk siswa yang sangat cakap selama Pandemi Covid-19",
    "TE5": "Saya meminta siswa untuk mengikuti aturan dalam pembelajaran selama Pandemi Covid-19",
}
EN = {
    "TSC1": "I think I have good teaching skills and abilities during the Covid-19 Pandemic",
    "TSC2": "I have a reputation as an efficient teacher in teaching during the Covid-19 Pandemic",
    "TSC3": "My colleagues regard me as a competent teacher in teaching during the Covid-19 Pandemic",
    "TSC4": "I feel I am a valuable person in teaching during the Covid-19 Pandemic",
    "TSC5": "In general, I am a good teacher in teaching during the Covid-19 Pandemic",
    "TE1": "I help my students appreciate learning during the Covid-19 Pandemic",
    "TE2": "I motivate students who show low interest in school work during the Covid-19 Pandemic",
    "TE3": "I improve the understanding of students who fail during the Covid-19 Pandemic",
    "TE4": "I provide suitable challenges for highly capable students during the Covid-19 Pandemic",
    "TE5": "I ask students to follow the rules in learning during the Covid-19 Pandemic",
}
ANCH_ID = {1: "Sangat Tidak Setuju", 2: "Tidak Setuju", 3: "Netral", 4: "Setuju", 5: "Sangat Setuju"}
ANCH_EN = {1: "Strongly disagree", 2: "Disagree", 3: "Neutral", 4: "Agree", 5: "Strongly agree"}


def main():
    for k, name in (("pe_tsc", "Teacher self-concept during the Covid-19 pandemic (TSC), 5 items"),
                    ("pe_te", "Teacher efficacy during the Covid-19 pandemic (TE), 5 items")):
        table = f"habibi_2021_{k}"
        rows = [row(table, f"{table}_1", c, name, "Indonesian", r, ID_[c], option_text=ANCH_ID[r],
                    item_text_tr=EN[c], option_text_tr=ANCH_EN[r]) for c in mod.BLOCKS[k] for r in range(1, 6)]
        write(table, rows)


if __name__ == "__main__":
    main()
