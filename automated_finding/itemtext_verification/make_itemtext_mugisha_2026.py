#!/usr/bin/env python3
"""Item text for mugisha_2026_ehr_status / _ehr_use / _ehr_competence (Zenodo 19387267). Stems = the .sav
variable labels, anchors = the value labels ("Strongly Disagree (SD)" ... with the abbreviation kept as
printed). English administration (Ugandan hospital staff; the file is in English)."""
from _itemtext_writer_c import load_script, row, write

mod = load_script("mugisha_2026_ehr_competence")
INSTR = {"ehr_status": "Status of the electronic health record (EHR) system, 16 items",
         "ehr_use": "Effective use of the EHR system, 16 items",
         "ehr_competence": "Evaluation of users' EHR competence, 16 items"}


def main():
    labels, vlabels = mod.labels()
    for k, pre in mod.PREFIX.items():
        table = f"mugisha_2026_{k}"
        rows = []
        for c in [x for x in labels if x.startswith(pre)]:
            for r, opt in sorted(vlabels[c].items()):
                rows.append(row(table, f"{table}_1", c, INSTR[k], "", int(r), labels[c].strip(), option_text=opt))
        write(table, rows)


if __name__ == "__main__":
    main()
