"""Build the batch-A item text tables from the SPSS label levels.

Two deposits carry stems, so only these ship:

  zenodo.22035722 (Hartmann) -- English. Four of its five scales. The fifth,
    ClimateAnxiety, is the Climate Change Anxiety Scale (Clayton & Karazsia
    2020): a NAMED third-party instrument with no quotable rights clause, and
    the 2026-10-15 ruling is that silence on a named third-party instrument no
    longer ships. The four that do ship are authored by the depositor for this
    study, so the CC BY deposit is the originator's own grant.

  zenodo.5708255 (Lischer) -- German as administered, plus the canonical
    English. The PHQ family is an express GRANT in the rights register.

Rules applied: one row per item x response option; `section_id` never blank;
an UNLABELLED scale point gets a BLANK option_text rather than being padded
with its own number (audit_batch.R warns when you pad it); nothing is invented
-- the PHQ instruction line is left NA because the variable labels do not carry
it and the questionnaire PDF was not transcribed.
"""
import csv, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pyreadstat  # noqa: E402

HERE = os.environ.get("IRW_BATCHA_RAW", os.path.dirname(os.path.abspath(__file__)))
OUT = ("/home/ben/Dropbox/projects/irw/src/.claude/worktrees/"
       "remine-3077-zenodo-leads/automated_finding/itemtext_output")
COLS = ["table", "section_id", "item", "instrument", "language", "instructions",
        "section_prompt", "item_text", "correct_response", "option_text", "resp",
        "instructions_translated", "section_prompt_translated",
        "item_text_translated", "option_text_translated"]

# ---------------------------------------------------------------- Hartmann
HART = {
    "hartmann_2026_ai_use_intensity": dict(
        prefix="AIUseIntensity",
        n=4,
        instrument="AI use intensity items (author-developed)",
        instructions=("Think about your use of artificial intelligence (AI) "
                      "technologies. Please answer the following questions."),
    ),
    "hartmann_2026_ai_env_awareness": dict(
        prefix="AIEnvironmentalImpactAwareness",
        n=8,
        code=lambda i: f"AIEnvAware{i}",
        instrument="Awareness of AI's environmental impact items (author-developed)",
        instructions=("Please indicate your level of agreement with the following "
                      "statements about the environmental impact of AI."),
    ),
    "hartmann_2026_climate_commitment": dict(
        prefix="ClimateCommitment",
        n=4,
        instrument="Climate commitment items (author-developed)",
        instructions="How do you feel about tackling climate change?",
    ),
    "hartmann_2026_pro_climate_intention": dict(
        prefix="ProClimateIntention",
        n=5,
        instrument="Pro-climate behavioural intention items (author-developed)",
        instructions=("How likely is it that you will take the following actions "
                      "against climate change in the next few months?"),
    ),
}

# ---------------------------------------------------------------- Lischer PHQ-4
# The official English PHQ-4 wording, which the phqscreeners.com grant covers
# ("no permission is required to reproduce, translate, display or distribute").
PHQ_EN = {
    "PHQ4_01": "Little interest or pleasure in doing things",
    "PHQ4_02": "Feeling down, depressed, or hopeless",
    "PHQ4_03": "Feeling nervous, anxious or on edge",
    "PHQ4_04": "Not being able to stop or control worrying",
}
PHQ_OPT_EN = {1: "Not at all", 2: "Several days",
              3: "More than half the days", 4: "Nearly every day"}


def rows_hartmann():
    d, meta = pyreadstat.read_sav(
        os.path.join(HERE, "raw/22035722/26 IJCS AI climate.sav"),
        apply_value_formats=False)
    labs, vals = meta.column_names_to_labels, meta.variable_value_labels
    out = []
    for table, spec in HART.items():
        for i in range(1, spec["n"] + 1):
            src = f"{spec['prefix']}{i}"
            code = spec.get("code", lambda k: f"{spec['prefix']}{k}")(i)
            full = labs[src]
            instr = spec["instructions"]
            assert full.startswith(instr), (src, full[:80])
            stem = full[len(instr):].strip()
            assert stem, src
            vl = vals[src]
            for resp in sorted(vl):
                label = str(vl[resp]).strip()
                # An unlabelled midpoint is deposited as its own number; that is
                # not a label, so it ships blank rather than padded.
                opt = "" if label == str(int(resp)) else label
                out.append({
                    "table": table, "section_id": f"{table}_1", "item": code,
                    "instrument": spec["instrument"], "language": "English",
                    "instructions": instr, "section_prompt": "",
                    "item_text": stem, "correct_response": "",
                    "option_text": opt, "resp": int(resp),
                    "instructions_translated": "", "section_prompt_translated": "",
                    "item_text_translated": "", "option_text_translated": "",
                })
    return out


def rows_lischer():
    d, meta = pyreadstat.read_sav(
        os.path.join(HERE, "raw/5708255/Datensatz_Publikation_Lischer.sav"),
        apply_value_formats=False)
    labs, vals = meta.column_names_to_labels, meta.variable_value_labels
    out = []
    for item, en in PHQ_EN.items():
        # The deposited label is "PHQ01: <stem>"; the code prefix is bookkeeping,
        # not part of what was asked, so it is stripped reversibly.
        de = labs[item].split(":", 1)[1].strip()
        vl = vals[item]
        for resp in sorted(vl):
            if int(resp) == 5:        # "Keine Angabe" -- the missing code, not an option
                continue
            out.append({
                "table": "lischer_2021_phq4",
                "section_id": "lischer_2021_phq4_1", "item": item,
                "instrument": "Patient Health Questionnaire-4 (PHQ-4)",
                "language": "German",
                "instructions": "", "section_prompt": "",
                "item_text": de, "correct_response": "",
                "option_text": str(vl[resp]).strip(), "resp": int(resp),
                "instructions_translated": "", "section_prompt_translated": "",
                "item_text_translated": en,
                "option_text_translated": PHQ_OPT_EN[int(resp)],
            })
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    allrows = rows_hartmann() + rows_lischer()
    by = {}
    for r in allrows:
        by.setdefault(r["table"], []).append(r)
    for table, rows in by.items():
        p = os.path.join(OUT, f"{table}__items.csv")
        with open(p, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=COLS, quoting=csv.QUOTE_ALL,
                               lineterminator="\n")
            w.writeheader()
            for r in rows:
                w.writerow({k: (r[k] if r[k] != "" else "NA") for k in COLS})
        print(f"{table}__items.csv: {len(rows)} rows, "
              f"{len({r['item'] for r in rows})} items")


if __name__ == "__main__":
    main()
