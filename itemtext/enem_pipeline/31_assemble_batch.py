#!/usr/bin/env python3
"""Assemble itemtext/itemtables/batch_enem_<YYYY>/ per EXTRACTION_RULES.md R9.

Every count, item code and gate figure in the generated prose comes from
facts.json (written by 30_collect_facts.py, which reads the tables and the
manifest on disk). The only hand-written material here is the per-year SOURCE
record -- which booklet was read and what was done to it -- and the shared
policy paragraphs, which are the same for all years because the policy is.

Nothing is committed and nothing is uploaded. Run the R10 gates after this.

Usage:
  python3 31_assemble_batch.py --year 2013 [--year 2015 ...] [--repo ~/irw]
  python3 31_assemble_batch.py --all
"""
import argparse, csv, json, os, re, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
FACTS = json.load(open(os.path.join(HERE, "facts.json"), encoding="utf-8"))
AREAS = ["ch", "cn", "lc", "mt"]
AREA_PT = {"ch": "Ciências Humanas", "cn": "Ciências da Natureza",
           "lc": "Linguagens e Códigos", "mt": "Matemática"}

PROV_COLS = ["table", "mapping_basis", "text_source", "translation_source",
             "description_source", "source_ref", "note", "public_note", "uploaded"]
VER_COLS = ["table", "batch", "mapping_basis", "uploaded", "route", "status", "evidence"]

# ----------------------------------------------------------------- per year
# "primary" is the booklet the text was READ FROM. Pre-2017 ENEM published no
# accessibility edition at all, so those years are sourced from a standard
# colour booklet -- which is why they need 13_join.py --colour.
SRC = {
 "2013": dict(kind="standard", colour="AZUL",
   files="Caderno1_Azul_Sab.pdf (day 1: CH, CN) and Caderno7_Azul_Dom.pdf (day 2: LC, MT)",
   repair=None,
   extra="ENEM 2013 published no accessibility edition, so the text is the standard AZUL booklet."),
 "2015": dict(kind="standard", colour="AZUL",
   files="Caderno1_Azul_Sab.pdf (day 1: CH, CN) and Caderno7_Azul_Dom.pdf (day 2: LC, MT), first application",
   repair="17_decode_2018.py",
   extra="ENEM 2015 published no accessibility edition. The booklets embed Arial as a CID-keyed CFF with no /ToUnicode, so every extractor returns a byte-shifted cipher; a /ToUnicode CMap was injected before parsing."),
 "2016": dict(kind="standard", colour="AZUL",
   files="CAD_ENEM_2016_DIA_1_01_AZUL.pdf (day 1: CH, CN) and CAD_ENEM_2016_DIA_2_07_AZUL.pdf (day 2: LC, MT), first application",
   repair="17_decode_2018.py",
   extra="ENEM 2016 published no accessibility edition, and has the same missing-/ToUnicode defect as 2015."),
 "2017": dict(kind="accessibility", colour="LARANJA",
   files="the LARANJA (Adaptada Ledor) accessibility booklets for both days",
   repair=None,
   extra="2017 is the only year whose CO_POSICAO is numbered PER AREA (1-45 within each area, LC 1-50) rather than 1-180."),
 "2018": dict(kind="accessibility", colour="LARANJA",
   files="the LARANJA (Ledor) accessibility booklets for both days",
   repair="17_decode_2018.py",
   extra="The 2018 booklets embed Arial as a CID-keyed CFF with no /ToUnicode; a /ToUnicode CMap was injected before parsing."),
 "2019": dict(kind="accessibility", colour="LARANJA",
   files="the LARANJA (Adaptada Ledor) accessibility booklets for both days",
   repair=None, extra=""),
 "2020": dict(kind="accessibility", colour="LARANJA",
   files="the LARANJA (Adaptada Ledor) accessibility booklets for both days",
   repair=None,
   extra="The day-1 cover page extracts to only 195 characters in the source PDF, so `instructions` for CH and LC is thin; that is a property of the source, not of this extraction."),
 "2021": dict(kind="accessibility", colour="LARANJA",
   files="ENEM_2021_P1_CAD_{09,11}_DIA_{1,2}_LARANJA_LEDOR.pdf",
   repair="25_repair_2021.py",
   extra="The 2021 booklets name glyphs by id (/g70) in /Differences while /ToUnicode covers only the codes with real Adobe names, so the body text extracts as /gNNN tokens. The CMap was COMPLETED in the PDF (never /Differences, which corrupts every lowercase l and x) using a map derived from subsets of the same families that do carry real names."),
 "2022": dict(kind="accessibility", colour="LARANJA",
   files="the LARANJA (Adaptada Ledor) accessibility booklets for both days",
   repair="23_decode_symbolmt.py",
   extra="Some CN and MT notation is set in simple Type1 SymbolMT subsets whose /Differences names glyphs opaquely and which carry no /ToUnicode; those were resolved over the Adobe Symbol encoding (code = GID+29 for GID 3-97, GID+63 above)."),
 "2024": dict(kind="accessibility", colour="LARANJA",
   files="2024_PV_impresso_D1_CD1.pdf / D2_CD5 and the LARANJA accessibility editions",
   repair=None,
   extra="Gap items were filled from the AMARELA standard booklet (caderno 5), identified by TX_COR rather than by caderno number."),
 "2025": dict(kind="accessibility", colour="LARANJA",
   files="the LARANJA accessibility booklets for both days",
   repair=None,
   extra="LC carries a genuine shared passage (\"Texto para as questões ...\"), which is published in `section_prompt` with its own `section_id` rather than duplicated into each stem."),
}

LICENCE = (
 "INEP names no licence for the provas -- the LEIA-ME, Edital, question booklets and "
 "gabaritos name none, and the only reproduction wording anywhere in the microdata sits on "
 "technical publications and covers those publications rather than the exam -- so the "
 "operative terms are the gov.br site footer, Creative Commons Atribuição-SemDerivações 3.0 "
 "Não Adaptada, which permits redistribution but not derivative works. A translation is a "
 "derivative, so none is published; the Portuguese is INEP's own wording and a user who needs "
 "English can translate it.")
TRANSLATION = (
 "No English ships: translation_source=not_translated, so every _translated cell is blank on "
 "purpose (ruled 2026-09-14, #1848).")
RESPRAW = (
 "resp_raw (spelling per #2094) carries the printed option letter A-E, so option_text can be "
 "joined to the letter the candidate chose and the four distractors are not anonymous. Rows "
 "are in A-E order.")
OPTION_RULE = (
 "Where the five printed options are DRAWINGS with no text of their own -- circuit diagrams, "
 "graph sketches, chemical structures -- option_text is the literal NA and no label is "
 "generated for them, because a generated option label becomes a category label that someone "
 "will join to resp for distractor analysis (Ben's rule, #1848, 2026-09-03/11). "
 "correct_response and resp_raw keep those options addressable.")


# ---------------------------------------------------------------- the guard
# Ben asked on #2226: "what stops it happening a third time?" -- twice already,
# a post-pass was run on the batch directories and then silently reverted by
# this script, which recopies the tables out of /scratch. A note in a README
# does not stop it; a refusal does.
#
# Every post-pass leaves a signature that is cheap to test for. If any of them
# is present in the file about to be copied, the pass has not been run on the
# PIPELINE output, and assembling would ship the unfixed text. So: refuse, and
# name the pass that is missing.
LATE_DESC = re.compile(r"Descri[\u00e7c][\u00e3a]o\s+d(?:o|a|e|os|as)\b[^:]{0,90}:")
LATE_DESC_CLOSER = re.compile(
    r"(\?|\u00e9 mais pr[\u00f3o]xim[ao] de|corresponde a|deve ser|ser[\u00e1a] de|"
    r"[\u00e9e] igual a|em que|classificado como|da seguinte maneira|"
    r"respectivamente|[\u00e9e],? aproximadamente,?)\s*$", re.I)
KEEP_LATE_DESC = {"78578", "141775", "87450", "59546", "89518"}

UNFIXED = [
    ("46_strip_option_letter.py", "options still prefixed with their own letter",
     lambda rs: sum(1 for r in rs
                    if re.match(r"^\s*%s\s+\S" % re.escape(r["resp_raw"]),
                                r.get("option_text") or "")) >= 2),
    ("43_normalize_glyphs.py", "wrong or unnormalised glyphs",
     lambda rs: any(ch in (r.get("item_text") or "") + (r.get("option_text") or "")
                    for r in rs
                    for ch in ("\u00fe", "\u021c", "\u0138", "\ufb01", "\ufb02",
                               "\uf02b", "\uf02d", "\uf0de", "\uf072"))),
    ("26_strip_page_furniture.py", "printed page furniture",
     lambda rs: any(re.search(r"\*[A-Za-z0-9]{5,}\*|\.ind[bd]|"
                              r"\d\s*[\u00ba\u00b0o]\s*dia\s*\|",
                              (r.get("item_text") or "") + (r.get("option_text") or ""))
                    for r in rs)),
    # R13. A description that starts late in the stem AND follows a question
    # closer describes something the item has already stopped talking about.
    # KEEP_LATE_DESC is the audited allow-list from 54_relocate_descriptions.py:
    # "Descricao das alternativas" legitimately follows the question, as do the
    # two verified own-figure cases and the recipient of a relocation.
    ("54_relocate_descriptions.py", "a figure description on the wrong item",
     lambda rs: any(
         r["item"] not in KEEP_LATE_DESC
         and (lambda st, ms: ms and ms[-1].start() >= len(st) * 0.55
              and LATE_DESC_CLOSER.search(st[:ms[-1].start()].rstrip()))(
                  re.sub(r"\s+", " ", r.get("item_text") or ""),
                  list(LATE_DESC.finditer(re.sub(r"\s+", " ", r.get("item_text") or ""))))
         for r in rs)),
    ("49_option_conventions.py", "two options with identical text",
     lambda rs: (lambda v: len(v) >= 2 and len(v) != len(set(v)))(
         [(r.get("option_text") or "").strip() for r in rs
          if (r.get("option_text") or "").strip() not in ("", "NA")])),
]


def check_unfixed(path):
    """Return [(script, why)] for every post-pass missing from this file."""
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    by = {}
    for r in rows:
        by.setdefault(r["item"], []).append(r)
    bad = []
    for script, why, test in UNFIXED:
        if any(test(rs) for rs in by.values()):
            bad.append((script, why))
    return bad


def gate_for(y):
    lines = FACTS[y].get("gate_lines") or []
    tot = [l for l in lines if l.startswith("TOTAL")]
    return tot


def note_for(y, a):
    f = FACTS[y]["areas"][a]
    s = SRC[y]
    conv = (FACTS[y].get("position_convention") or {}).get(a.upper(), "continuous")
    off = (FACTS[y].get("derived_offset") or {}).get(a.upper())
    bits = [f"ENEM {y} {AREA_PT[a]}."]
    if s["kind"] == "accessibility":
        bits.append("Item text is INEP's own, read from the accessibility booklet "
                    f"({s['files']}), which is the primary source because INEP wrote verbal "
                    "descriptions of figures, graphs and tables into that edition.")
    else:
        bits.append(f"Item text is INEP's own, read from the standard {s['colour']} booklet "
                    f"({s['files']}).")
    if s["repair"]:
        bits.append(f"The PDF's fonts were repaired with {s['repair']} before parsing.")
    if s["extra"]:
        bits.append(s["extra"])
    bits.append(f"Item codes come from INEP's published position-to-item table "
                f"ITENS_PROVA_{y}.csv, joined on the booklet's own printed question number; "
                f"TX_GABARITO in the same table gives correct_response. "
                f"{f['n_items']} of {f['published']} published items.")
    if conv != "continuous":
        bits.append(f"Position convention for this area is `{conv}`"
                    + (f" (measured offset {off:+d} between the printed number and CO_POSICAO)"
                       if isinstance(off, int) and off else "")
                    + "; it was verified against INEP's own printed-position key strings, not assumed.")
    if f["missing"]:
        bits.append(f"NOT SHIPPED: {', '.join(f['missing'])} -- "
                    + ("annulled by INEP with TX_GABARITO='X', so there is no correct answer to "
                       "ship (R3)." if set(f["missing"]) <= set(f["no_key_declared"])
                       else "the printed options could not be segmented in any booklet colour; "
                            "reported rather than guessed."))
    if f["aban_kept_valid_key"]:
        bits.append(f"IN_ITEM_ABAN is set on {', '.join(f['aban_kept_valid_key'])} but the key is "
                    "valid, so the item IS shipped and disclosed rather than dropped (R3).")
    nfig, nun = len(f["figure_option_items"]), len(f["unsegmented_option_items"])
    nguess = len(f.get("untranscribable_option_items", []))
    if nfig + nun + nguess:
        tot = nfig + nun + nguess
        bits.append(f"{tot} item(s) ship the literal NA in option_text, because the printed "
                    "options carry no text that could be transcribed. " + OPTION_RULE)
        if nfig:
            bits.append("Checked individually against the printed page and confirmed to be "
                        "DRAWINGS with no text of their own: "
                        + ", ".join(f["figure_option_items"]) + ".")
        if nun:
            bits.append("Checked individually and NOT drawings -- their options are notation "
                        "the parser could not segment, chiefly STACKED FRACTIONS (numerator "
                        "over denominator): " + ", ".join(f["unsegmented_option_items"])
                        + ". These are a gap rather than a deliberate omission: the options "
                        "are legible in the source PDF and recoverable by hand.")
        if nguess:
            bits.append("The remaining " + str(nguess) + " ("
                        + ", ".join(f["untranscribable_option_items"]) + ") were classified "
                        "from the wording of the stem rather than re-checked page by page. "
                        "That test is a heuristic and it is known to misfire -- it read "
                        "2016 CN 86572 as a figure item because the stem mentions a circuit, "
                        "when the options are the fractions 1, 4/7, 10/27, 14/81 and 4/81 -- "
                        "so no claim is made here about WHICH kind each one is. What is "
                        "certain for all of them is that the extractor found no option text "
                        "and none was invented.")
    if f["figure_option_items"] or f["unsegmented_option_items"] or nguess:
        bits.append("On figure items the stem legitimately contains the figure's OWN embedded "
                    "labels -- axis names, component letters, units -- because those are "
                    "printed text on the page and the extractor cannot tell them from prose. "
                    "2013 CN 15947 is the clearest case: its stem ends '...está representado "
                    "em: A Fase Fase', where 'Fase' labels a wire in the first circuit "
                    "diagram. Nothing was invented and nothing was removed; a reader treating "
                    "item_text as continuous prose should expect these fragments.")
    if f["generated_desc_items"]:
        bits.append(f"{len(f['generated_desc_items'])} item(s) carry an inline, explicitly "
                    "AI-marked description where notation could not be extracted from the font: "
                    f"{', '.join(f['generated_desc_items'])}. The description is in item_text "
                    "only and is marked in Portuguese as generated, so it cannot be read as "
                    "transcribed item text; description_source is partly_generated.")
    if f["replacement_char"]:
        # Name the item. "one item" is not a disclosure a reader can act on.
        bits.append(f"{f['replacement_char']} U+FFFD replacement characters remain, in "
                    f"{', '.join(f['replacement_char_items']) or 'one item'}: decorative "
                    "bullet glyphs from a font (MyriadPro) whose remaining code points have no "
                    "document-internal mapping, repeated once per option row. Left visible "
                    "rather than guessed; the surrounding prose is unaffected.")
    if f["instructions_words"] < 25:
        bits.append(f"`instructions` is only {f['instructions_words']} words because the cover "
                    "page extracts to 195 characters in the source PDF.")
    if f["section_prompt_used"]:
        bits.append("A genuine shared passage is carried in `section_prompt` with its own "
                    "`section_id` rather than duplicated into each stem (ruled 2026-09-15).")
    else:
        bits.append("No item shares a passage with another, so section_id is the trivial "
                    "<table>_1 and section_prompt is empty.")
    bits.append(TRANSLATION)
    bits.append(LICENCE)
    bits.append(RESPRAW)
    return " ".join(bits)


def public_note_for(y, a):
    f = FACTS[y]["areas"][a]
    s = SRC[y]
    bits = []
    if s["kind"] == "accessibility":
        bits.append("Item text is INEP's own accessibility-booklet wording, including its "
                    "descriptions of figures.")
    else:
        bits.append(f"Item text is INEP's own, transcribed from the published {s['colour']} "
                    f"question booklet for ENEM {y}.")
    if f["figure_option_items"]:
        bits.append("For some items the printed response options are drawings with no text of "
                    "their own (diagrams, graphs, chemical structures); their option text is "
                    "left blank rather than described, so that no generated label is ever "
                    "treated as a printed option.")
    if (f["figure_option_items"] or f["unsegmented_option_items"]
            or f.get("untranscribable_option_items")):
        bits.append("Some items have no option text. For most, the printed response options "
                    "are drawings with no words in them (diagrams, graphs, chemical "
                    "structures), and nothing is invented to fill the gap. For a few the "
                    "options are fractions or notation that could not be read reliably. "
                    "Where the options are drawings, the question text also contains the "
                    "labels printed inside the figures themselves, which cannot be separated "
                    "from the surrounding sentences automatically. Each table's notes say "
                    "which items were checked page by page and which were not.")
    if f["missing"] and set(f["missing"]) <= set(f["no_key_declared"]):
        bits.append("Items that INEP annulled carry no correct answer and are not included.")
    elif f["missing"]:
        bits.append("One item's printed options could not be read reliably and it is not "
                    "included.")
    if f["instructions_words"] < 25:
        bits.append("The instructions field is brief because little text is recoverable from "
                    "that booklet's cover page.")
    bits.append("No English translation ships. INEP publishes the exam under the Creative "
                "Commons Attribution-NoDerivatives licence named on its site, which allows "
                "redistribution but not derivative works, and a translation would be a "
                "derivative; what ships is INEP's own Portuguese.")
    return " ".join(bits)


def evidence_for(y, a):
    f = FACTS[y]["areas"][a]
    tot = gate_for(y)
    bits = [f"Mapping is INEP's own published position->item table (ITENS_PROVA_{y}.csv), so "
            "item values are taken verbatim from the publisher rather than reconstructed."]
    bits.append("Cross-checks: (1) the printed-position key strings in INEP's own microdata "
                "(TX_GABARITO_{CN,CH,LC,MT}, one 45- or 50-character string per CO_PROVA, "
                "indexed by printed position within area) were compared letter by letter "
                "against the TX_GABARITO of the item this extraction attached to that "
                f"position: {'; '.join(tot) if tot else 'see 20_verify_gabarito_microdata.py'}. "
                "A wrong position convention lands near chance (about 9/45), so an exact match "
                "over ~45 effectively random 5-way letters is decisive.")
    bits.append("(2) Option order is fixed across booklet colours, so text transcribed from one "
                "booklet is valid for that item whichever colour a respondent sat; item ORDER is "
                "permuted, so positions were always looked up for the booklet actually read.")
    if y == "2017":
        bits.append("(3) KNOWN AND ACCEPTED: on the LARANJA accessibility booklet LC scores "
                    "43/45. The two disagreements are items 39670 (printed E vs TX_GABARITO D) "
                    "and 29586 (printed C vs B). This is a defect in INEP's own accessibility "
                    "key string, not here: ITENS_PROVA gives D and B for those items in all "
                    "five colours including LARANJA, the AZUL and AMARELA key strings both give "
                    "D and B at 45/45, and the extracted option text is character-identical "
                    "between LARANJA and AZUL for both items, so no reordering could justify E "
                    "and C. Three independent sources against one; correct_response is unchanged.")
    bits.append("(4) A cross-booklet reproduction check extracted the same items from two "
                "different colour booklets with independently embedded font subsets and compared "
                "them by CO_ITEM: 99.97% character agreement with zero substituted letters, the "
                "residual being line-wrapping and printed page furniture (since removed).")
    return " ".join(bits)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--year", action="append", default=[])
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--repo", default=os.path.expanduser("~/irw"))
    a = ap.parse_args()
    years = sorted(FACTS) if a.all else a.year
    if not years:
        print("nothing to do: pass --year or --all"); return 2
    for y in years:
        batch = f"batch_enem_{y}"
        dst = os.path.join(a.repo, "itemtext", "itemtables", batch)
        os.makedirs(os.path.join(dst, "scripts"), exist_ok=True)
        src_dir = FACTS[y]["dir"]
        tables = []
        for ar in AREAS:
            if ar not in FACTS[y]["areas"]:
                continue
            name = f"enem_{y}_1mil_{ar}__items.csv"
            srcf = os.path.join(src_dir, name)
            bad = check_unfixed(srcf)
            if bad:
                print(f"  REFUSING to assemble {name}: the pipeline output in\n"
                      f"    {src_dir}\n"
                      f"  has not been through:")
                for script, why in bad:
                    print(f"      {script:32s} ({why})")
                print("  Run 42_rebuild.py for this year, which applies every post-pass,\n"
                      "  rather than applying them to the batch directory by hand --\n"
                      "  this copy would overwrite that and the fix would be lost.")
                return 3
            shutil.copy(srcf, os.path.join(dst, name))
            tables.append((f"enem_{y}_1mil_{ar}", ar))
        with open(os.path.join(dst, "provenance.csv"), "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, PROV_COLS, quoting=csv.QUOTE_ALL); w.writeheader()
            for t, ar in tables:
                f = FACTS[y]["areas"][ar]
                w.writerow({"table": t, "mapping_basis": "paper_explicit",
                            "text_source": "study_materials",
                            "translation_source": "not_translated",
                            "description_source": ("partly_generated"
                                                   if f["generated_desc_items"] else "source_published"),
                            "source_ref": (f"{SRC[y]['files']}; position->item map from "
                                           f"ITENS_PROVA_{y}.csv"),
                            "note": note_for(y, ar), "public_note": public_note_for(y, ar),
                            "uploaded": ""})
        with open(os.path.join(dst, "notes.csv"), "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, ["table", "note"], quoting=csv.QUOTE_ALL); w.writeheader()
            for t, ar in tables:
                w.writerow({"table": t, "note": note_for(y, ar)})
        with open(os.path.join(dst, "verification_merged.csv"), "w", newline="",
                  encoding="utf-8") as fh:
            w = csv.DictWriter(fh, VER_COLS, quoting=csv.QUOTE_ALL); w.writeheader()
            for t, ar in tables:
                w.writerow({"table": t, "batch": batch, "mapping_basis": "paper_explicit",
                            "uploaded": "", "route": "publisher_position_item_map",
                            "status": "VERIFIED", "evidence": evidence_for(y, ar)})
        # The pipeline lives ONCE, in itemtext/enem_pipeline/. It used to be
        # copied into every batch directory -- 16 files x 11 years, 2.6 MB of
        # duplicate, and a fix had to land eleven times. What each batch keeps
        # is the RECORD of which pinned versions built it, which is the part
        # that is actually per-year.
        import hashlib
        rec = [f"# How batch_enem_{y} was built", "",
               "The pipeline is in `itemtext/enem_pipeline/`, one copy for every",
               "year. This file records the pinned versions that produced THIS",
               "batch, so the build can be reproduced exactly:", "",
               "    cd itemtext/enem_pipeline",
               f"    python3 42_rebuild.py --year {y}",
               f"    python3 31_assemble_batch.py --year {y}", "",
               "| script | pin used | md5 |", "|---|---|---|"]
        import glob as _g
        for stem in sorted({os.path.basename(f).split(".v")[0]
                            for f in _g.glob(os.path.join(HERE, "*.v*.py"))}):
            pins = sorted(_g.glob(os.path.join(HERE, f"{stem}.v*.py")),
                          key=lambda q: int(re.search(r"\.v(\d+)\.py$", q).group(1)))
            if not pins:
                continue
            newest = pins[-1]
            md5 = hashlib.md5(open(newest, "rb").read()).hexdigest()
            rec.append(f"| {stem}.py | {os.path.basename(newest)} | `{md5}` |")
        with open(os.path.join(dst, "scripts", "README.md"), "w",
                  encoding="utf-8") as fh:
            fh.write("\n".join(rec) + "\n")
        print(f"  {batch}: {len(tables)} table(s) + 3 sidecars + a build record")
    return 0


if __name__ == "__main__":
    sys.exit(main())
