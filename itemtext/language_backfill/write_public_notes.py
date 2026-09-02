"""Give every machine-translated table the public note it owes (#1777).

Ben's ruling, 2026-09-02: a table shipping English this project generated
carries per-table provenance AND a line on the public issues page. 64 tables
qualify; 4 had a line. This writes the note for all of them into
`backfill_provenance.csv`'s `public_note` column -- the same column every
`itemtables/batch_*/provenance.csv` already has, which is what
`check_issues_page.R` reads.

The note is composed rather than hand-written 64 times: one disclosure sentence
built from the table's `language`, plus a caveat where the internal `note`
records something a reader of the published table should know. The caveats are
curated here rather than derived, because the internal notes are written in an
internal voice ("SEE THE ANOMALY", "DEFECT recorded, not repaired") and several
say only "As administration." -- a cross-reference that means nothing on a
public page.

Rerunnable: it rewrites the column from scratch every time.
"""
from __future__ import annotations

import csv
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
PROV = HERE / "backfill_provenance.csv"

#: Deliberately does NOT say "no published English exists". For several of these
#: tables one does, and was rejected for a stated reason -- the BDI-II's is
#: Pearson-licensed, the FAD-Plus's does not map onto the administered item set.
#: Saying otherwise on the public page would be false for those.
BASE = ("The item text here is the administered {lang}, which is what respondents "
        "read. The English in the `_translated` columns was produced by IRW rather "
        "than by the study's authors.")

#: Where the published table has something a reader should know beyond the
#: disclosure itself. Keyed by table; appended to BASE.
CAVEATS: dict[str, str] = {
    # --- defects in the published data, recorded and deliberately not repaired
    "heekerens2025_sdq":
        "This table is labelled the Somatoform Dissociation Questionnaire (SDQ-20), but its "
        "20 German item texts are identical to `heekerens2025_dss`'s, differing only in one "
        "typo. The SDQ-20 is a different instrument, so one of the two tables is almost "
        "certainly carrying the other's item text. The published text is translated as it "
        "stands and is not repaired here; the discrepancy needs resolving at source.",
    "namprb_siwiak_2024_kop20":
        "The instructions and all four option labels have had their Polish diacritics stripped "
        "by an encoding fault in the source (`W naszym spolecze stwie`, `Zgadzam si`). The "
        "damage is left exactly as published, because it is what the table currently serves; "
        "the translation renders the intended sense.",
    "idas_machado2024":
        "Two `item_text` values are not items at all but English scoring notes -- `reversed "
        "scoring of item 27` and `reversed scoring of item 64` -- which have leaked into the "
        "item text column and should be removed at source. Source typos are left verbatim.",
    "sv-maia2_randelovic_2021_maia":
        "`option_text` mixes languages within one field, carrying Serbian `nikad` and English "
        "`Always` as the two endpoint anchors of the same scale. `Always` is mapped to itself "
        "so the translated column is whole rather than half-filled.",
    "bakumenko_2023_adyghe_values":
        "Only one option label exists in the published table for a 1-5 scale, so the other "
        "four points carry no option text.",
    "aguirre_camacho_2021_champion":
        "`option_text` is already English in the published table, so its translated column is "
        "empty.",

    # --- source text kept verbatim where it looks wrong but is what was administered
    "namprb_siwiak_2024_aot":
        "The source carries PDF line-break hyphens inside words (`naszy-mi`, `przeko-nan`, "
        "`na-wet`). These are kept verbatim in the administered text and rendered whole in "
        "the translation.",
    "gilbert_meta_64":
        "Item texts embed the template variable `${fc_name}`, kept verbatim in both columns -- "
        "it is a placeholder the instrument fills with the child's name, not text to translate. "
        "Levantine Arabic forms appear alongside standard Arabic.",
    "pedroso_2021_ifsq_pressuring":
        "Items embed the placeholder `(nome da crianca)`, kept verbatim in both columns.",
    "rd_ppcvdos_padconacns_jinbo_2019_dos":
        "Item codes carry the source numbering inside the text (`4. ...`) and are left verbatim.",
    "chile_2023_social-welfare-survey_ee":
        "Item texts are the survey's own abbreviated field labels, truncated in the source and "
        "left verbatim.",
    "chile_2023_social-welfare-survey_f":
        "Item texts are the survey's own abbreviated field labels. The source abbreviates to fit "
        "a column width (`Ult. 12 meses`, `org.`, `RRSS`) and contains stray zero-width "
        "characters; both are kept as published.",
    "chile_2023_social-welfare-survey_g":
        "Item texts are the survey's own abbreviated field labels, truncated in the source and "
        "left verbatim.",
    "chile_2023_social-welfare-survey_h":
        "Item texts are the survey's own abbreviated field labels. `NNA` (ninos, ninas y "
        "adolescentes) is expanded in the translation.",
    "chile_2023_social-welfare-survey_oo":
        "Item texts are the survey's own abbreviated field labels. Parenthetical population "
        "markers (Ocupados, Cuenta Propia, Desoc, FFT) are expanded in the translation.",
    "mexico_2023_quality_drainage":
        "Item texts carry the source numbering and trailing punctuation verbatim.",
    "mexico_2023_quality_lightning":
        "The table name misspells `lighting`, and is left as the published table spells it.",
    "mexico_2023_quality_corruptionperception":
        "Mexican institution names are kept in Spanish with an English gloss where the acronym "
        "would otherwise be opaque (CONAPRED, INE, CNDH, INEGI).",
    "mexico_2023_quality_problems":
        "Item texts are response categories of a `three most important problems` question, so "
        "each is a noun phrase rather than a sentence.",

    # --- where a published English exists but was deliberately not used
    "ccapsvtskhpacr_mercedes_2023_beck":
        "The official English BDI-II wording is Pearson-licensed, so the translated column is "
        "IRW's own rendering of the Spanish statements the study published, not Beck's English. "
        "Compound options where the source joins two statements with `;` are kept as one string "
        "in both columns so the two stay row-aligned.",
    "lys_2020_rape_3_asi":
        "Glick & Fiske's published English for the Ambivalent Sexism Inventory exists and the "
        "item count matches, but the correspondence is not clean enough to rely on -- the Polish "
        "carries a short form where the original pairs a reverse-scored item with a long one, so "
        "using the original's numbering could invert an item's polarity.",
    "namprb_siwiak_2024_bsr10":
        "Pennycook's English originals exist, but these are Polish renderings of randomly "
        "generated pseudo-profound statements, and the construct is the surface plausibility of "
        "the wording itself -- so substituting the original would change what the item measures.",
    "fad_dataset1":
        "Published English exists for the FAD-Plus, but the Chinese item set here does not map "
        "one-to-one onto it, so the administered Chinese is translated instead.",
    "fad_dataset2":
        "As `fad_dataset1`: the published FAD-Plus English does not map one-to-one onto this "
        "item set. The ten items this table has beyond `fad_dataset1` are translated on the "
        "same basis.",
    "isi_insomnia_wang2025":
        "This is an adapted Chinese Insomnia Severity Index: its interference item names study "
        "efficiency rather than the ISI original's work and chores, so the administered wording "
        "is translated rather than replaced with the published English.",
    "lshs-e_quidaja_2022":
        "Published English exists for the LSHS-E, but this administration is a Spanish "
        "adaptation with its own item set, so the administered Spanish is what is translated.",

    # --- partial translations, by design
    "rosenberg_fadplus_goto2021":
        "Only `option_text` is translated: `item_text` is already English in the published "
        "table, for a Japanese administration.",
    "aslec_insomnia_wang2025":
        "`instructions` and `option_text` are already English in the published table, so only "
        "the Chinese item text carries a translation.",
    "shu_2025_translation_mcpis":
        "`option_text` is already English, so only `item_text` carries a translation.",
    "heekerens2025_dss":
        "`option_text` is already English, so its translated column stays empty.",
    "sun_2025_morality_study2_self-moral-character":
        "The section prompt is already English in the published table, so its translated column "
        "stays empty.",
}

#: Twelve tables from one Hungarian media-use survey share a note.
for _t in ("torok_2025_ai_acceptance", "torok_2025_data_disclosure",
           "torok_2025_data_security", "torok_2025_discourse_responsibility",
           "torok_2025_facebook_uses", "torok_2025_internet_use_frequency",
           "torok_2025_legality_beliefs", "torok_2025_manipulation_fear",
           "torok_2025_news_consumption", "torok_2025_news_source_frequency",
           "torok_2025_news_source_trust", "torok_2025_social_media_effects"):
    CAVEATS[_t] = ("These are author-written survey items with no canonical instrument behind "
                   "them, so no published English exists to use instead. Typos in the source "
                   "are left verbatim in the administered text.")


def compose(row: dict) -> str:
    if row["translation_source"] != "machine_translation":
        return ""
    note = BASE.format(lang=row["language"])
    caveat = CAVEATS.get(row["table"])
    return f"{note} {caveat}" if caveat else note


def main() -> int:
    rows = list(csv.DictReader(open(PROV)))
    cols = list(rows[0].keys())
    if "public_note" not in cols:
        cols.insert(cols.index("note") + 1, "public_note")
    n = 0
    for row in rows:
        row["public_note"] = compose(row)
        n += bool(row["public_note"])
    with open(PROV, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, quoting=csv.QUOTE_ALL)
        w.writeheader()
        w.writerows(rows)
    print(f"wrote public_note for {n} of {len(rows)} rows "
          f"({len(CAVEATS)} carry a table-specific caveat)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
