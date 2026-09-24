#!/usr/bin/env python3
"""Move figure descriptions that INEP printed under the wrong item.

WHY THIS EXISTS. The accessibility ("LEDOR") editions render a figure as a
prose description. Most are set inline, where the figure would be. Some are
collected at the FOOT OF THE PAGE, after the last item's options -- and those
describe an item printed earlier on the page, or on the next one. The parser
attaches trailing text to the item it physically follows, so the description
lands on the wrong item.

This is invisible to every content gate. The stem is longer than it should be,
not shorter; no character is wrong; item_set_match stays TRUE. It surfaced
only when a model tried to ANSWER the items: 2018 CN 59858 is a question about
the energy released by oxidising glucose, and its stem ends with a description
of an electrical circuit.

A description on the wrong item is worse than no description -- it actively
misleads -- so nothing here is left in place on a hunch. Each move is
hand-verified against the printed page and recorded below with the evidence.

THE AUDIT RULE (replicable, and the reason this file also runs on new years):
flag any stem whose LAST `Descrição ...:` block starts in its final 45% AND is
preceded by a question closer ("?", "e mais proxima de", "e igual a", ...).
A well-formed item describes its figure BEFORE asking about it.

Three kinds of thing trip that rule, and only the first is a defect:

  1. MISPLACED  -- the description belongs to another item.  Listed in MOVES.
  2. OPTION SET -- "Descricao das alternativas": it describes the five OPTIONS,
                   so it correctly follows the question.  Listed in KEEP.
  3. OWN FIGURE -- printed after the options but genuinely this item's.
                   Listed in KEEP with the evidence.

--apply refuses to run if the audit finds anything in none of those lists,
rather than guessing at a new case.

Usage:
  python3 54_relocate_descriptions.py --tables DIR [--apply]
"""
import argparse, csv, glob, os, re, sys
from _rawedit import rewrite_field

MARK = re.compile(r"Descri[çc][ãa]o\s+d(?:o|a|e|os|as)\b[^:]{0,90}:")
CLOSER = re.compile(r"(\?|é mais pr[óo]xim[ao] de|corresponde a|deve ser|ser[áa] de|"
                    r"[ée] igual a|em que|classificado como|da seguinte maneira|"
                    r"respectivamente|[ée],? aproximadamente,?)\s*$", re.I)

# (year, csv basename, donor item, recipient item, evidence)
MOVES = [
    ("2018", "enem_2018_1mil_cn__items.csv", "59858", "89518",
     "acc_d2 p6 foot. 'Circuito eletrico ... dois ramos ligados em paralelo ... "
     "chave A ... chave B' describes the RESISTIVE TOUCHSCREEN item, QUESTAO 106 "
     "(= 89518), printed earlier on the same page. The donor, QUESTAO 108 "
     "(= 59858), asks about the energy from oxidising glucose and has no circuit. "
     "89518 currently carries no description."),
    ("2018", "enem_2018_1mil_cn__items.csv", "111612", "111637",
     "acc_d2 p15 foot. 'Fluxograma ciclico ... Processo 1 -> Combustiveis "
     "reduzidos e O2 -> Processo 2 -> CO2 e H2O' is the figure of QUESTAO 134 "
     "(= 111637), 'oxidacao de combustiveis, gerados no ciclo do carbono, por "
     "meio de processos capazes de interconverter ...'. The donor, QUESTAO 135 "
     "(= 111612), is about petroleum cracking. 111637 carries no description."),
    ("2020", "enem_2020_1mil_mt__items.csv", "15897", "41676",
     "CAD_11_DIA_2_LARANJA_LEDOR p18 foot. 'O recipiente com indicacao de agua a "
     "altura de 8 centimetros tem altura de 17 ... 4 ... 3' matches 41676, 'Num "
     "recipiente com a forma de paralelepipedo reto-retangulo, colocou-se agua "
     "ate a altura de 8 centimetros'. The donor, 15897, is a blood-type item. "
     "41676 carries no description."),
]

# audit hits that are correct as printed -- item -> why
KEEP = {
    "78578": "2023: 'Descricao das alternativas' -- describes the five OPTIONS.",
    "141775": "2024: 'Descricao das alternativas' -- describes the five OPTIONS.",
    "87450": "2025: 'Descricao das alternativas' -- describes the five OPTIONS.",
    # recipients of a MOVE: the relocated block is appended, so it lands after
    # the question. That is the move working, not a new defect.
    "89518": "2018: receives the circuit description relocated from 59858.",
    "59546": "2020: the column-graph description IS this item's own data "
             "('Dia 1: 800 pecas ... Dia 1: 4 horas'), merely printed after the "
             "options. Verified on CAD_11_DIA_2_LARANJA_LEDOR p20.",
}


def _files(tables, items_dir):
    return (sorted(glob.glob(f"{items_dir}/*__items.csv")) if items_dir
            else sorted(glob.glob(f"{tables}/batch_enem_*/*__items.csv")))


def audit(tables, items_dir=None):
    out = []
    for f in _files(tables, items_dir):
        seen = set()
        for r in csv.DictReader(open(f)):
            if r["item"] in seen:
                continue
            seen.add(r["item"])
            st = re.sub(r"\s+", " ", r.get("item_text") or "")
            ms = list(MARK.finditer(st))
            if not ms or ms[-1].start() < len(st) * 0.55:
                continue
            if CLOSER.search(st[:ms[-1].start()].rstrip()):
                out.append((f, r["item"], st[ms[-1].start():ms[-1].start() + 60]))
    return out


def apply_moves(tables, items_dir=None, only_year=None):
    known = {m[2] for m in MOVES} | set(KEEP)
    unknown = [(f, it, s) for f, it, s in audit(tables, items_dir) if it not in known]
    if unknown:
        print("REFUSING TO APPLY -- audit found cases not in MOVES or KEEP:")
        for f, it, s in unknown:
            print(f"   {os.path.basename(f)} item {it}: {s}")
        print("\nVerify each against the printed page and add it to one of the "
              "two lists. Do not let this pass run on an unclassified case.")
        return 1
    n = 0
    for year, base, donor, recip, _why in MOVES:
        if items_dir and year != only_year:
            continue
        f = f"{items_dir}/{base}" if items_dir else f"{tables}/batch_enem_{year}/{base}"
        if not os.path.exists(f):
            continue
        rows = list(csv.DictReader(open(f)))
        dtxt = next((r["item_text"] for r in rows if r["item"] == donor), None)
        if dtxt is None:
            print(f"   {year} {donor}: not found, skipped"); continue
        ms = list(MARK.finditer(dtxt))
        if not ms:
            print(f"   {year} {donor}: description already moved, skipped"); continue
        cut, keep = dtxt[ms[-1].start():].strip(), dtxt[:ms[-1].start()].rstrip()
        rec = [r for r in rows if r["item"] == recip]
        if not rec:
            print(f"   {year} {recip}: recipient not found -- NOT applied"); continue
        don = [r for r in rows if r["item"] == donor]
        rbefore = rec[0]["item_text"] or ""
        rewrite_field(f, rbefore, rbefore.rstrip() + " " + cut, expect=len(rec))
        rewrite_field(f, dtxt, keep, expect=len(don))
        n += 1
        print(f"   {year} {donor} -> {recip}: moved {len(cut)} chars")
    print(f"\n{n} descriptions relocated")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tables")
    ap.add_argument("--items-dir", help="one year's out dir, as used by 42_rebuild.py")
    ap.add_argument("--year")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    if not (a.items_dir or a.tables):
        ap.error("give --tables or --items-dir")
    if a.items_dir and not a.year:
        ap.error("--items-dir needs --year")
    if a.apply:
        sys.exit(apply_moves(a.tables, a.items_dir, a.year))
    known = {m[2] for m in MOVES} | set(KEEP)
    for f, it, s in audit(a.tables, a.items_dir):
        tag = "MOVE" if it in {m[2] for m in MOVES} else ("keep" if it in KEEP else "UNCLASSIFIED")
        print(f"  {os.path.basename(f):32} {it:>7} [{tag}] {s}")
