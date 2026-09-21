#!/usr/bin/env python3
"""Restore table contents that INEP's accessibility edition dropped.

WHY THIS EXISTS. The accessibility ("LEDOR") editions normally transcribe a
table into prose -- "Descricao do quadro: ...". Sometimes they do not: the
stem still points at the table ("O quadro apresenta a potencia aproximada de
equipamentos eletricos") and the numbers are simply absent. The standard
edition prints them.

This matters for IRW because the item text is used for READING and LINGUISTIC
COMPLEXITY analysis. A word count over an item whose table vanished is a word
count of the wrong item. It is not primarily about answerability -- plenty of
items are legitimately unanswerable from text alone and that is fine.

No gate can see this. The stem is shorter than it should be but perfectly
well-formed, and item_set_match stays TRUE.

SCOPE, measured rather than assumed. Asking "which stems point at a table and
carry no transcription of it?" returns 51 stems, but they split by edition:

  * 2013 / 2015 / 2016 come from the STANDARD booklet, which has no
    "Descricao" convention at all -- their tables are already inline as a
    column dump (2013 MT 42907 carries 51 digits; 2016 MT 53721, 268). All
    false positives.
  * The accessibility years leave six candidates, and three of those are
    ordinary Portuguese or a described table: "Segundo quadro" is a scene in
    a Dias Gomes play (2017 LC 31891), "quadros" are comic-strip panels
    (2022 LC 140567), and 2021 CN 84331's table IS described, just as
    "Descricao da imagem: Quadro intitulado ...".

That leaves the three below, plus 2018 MT 98294, which the filter misses
because it DOES have a "Descricao do quadro" -- for the rankings. Its stem
says "nos quadros", plural, and the frequency table is the missing one.

Each entry is transcribed from the standard booklet and cites its page. The
text is laid out the way that edition extracts -- header cells then values,
in column order -- which is exactly the form the 2013/2015/2016 tables
already ship in, so the corpus stays internally consistent.

This is NOT generated content: every character is INEP's own, from INEP's own
first-application booklet, so it carries no "gerada por IA" marking. It is the
same standard-booklet gap-filling the source policy already prescribes.

Usage:
  python3 55_recover_tables.py --tables DIR [--apply]
  python3 55_recover_tables.py --items-dir DIR --year YYYY [--apply]
"""
import argparse, csv, glob, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _rawedit import rewrite_field

# (year, item, anchor sentence the table follows, table text, probe, evidence)
# The PROBE is a distinctive fragment used to detect an already-applied
# insertion. Testing the table's first and last TOKEN is not enough:
# 98294's table begins "Ranking" and ends "5", both of which already
# occur in that stem, so the pass reported it as done and skipped it.
RECOVER = [
    ("2018", "87205",
     "O quadro resume alguns dados aproximados sobre esses combustíveis.",
     "Combustível Densidade (g mL−1) Calor de combustão (kcal g−1) "
     "Etanol 0,8 −6 Gasolina 0,7 −10",
     "Calor de combustão", "std_d2 QUESTAO 92. acc_d2 keeps the sentence "
     "and drops the table."),
    ("2018", "32905",
     "Os resultados obtidos estão no quadro.",
     "Número de acidentes sofridos Número de trabalhadores "
     "0 50 1 17 2 15 3 10 4 6 5 2",
     "Número de trabalhadores",
     "std_d2 QUESTAO 145. Without it the mean cannot be read at all."),
    ("2018", "86222",
     "O quadro apresenta a potência aproximada de equipamentos elétricos.",
     "Equipamento elétrico Potência aproximada (watt) Exaustor 150 "
     "Computador 300 Aspirador de pó 600 Churrasqueira elétrica 1 200 "
     "Secadora de roupas 3 600",
     "Potência aproximada (watt)", "std_d2 QUESTAO 115."),
    ("2018", "98294",
     "Ranking IV: 1o Edu; 2o Ana; 3o Dani; 4o Bia; 5o Caio.",
     "Ranking Frequência I 4 II 9 III 7 IV 5",
     "Ranking Frequência",
     "std_d2 QUESTAO 172. acc_d2 p22 describes the RANKINGS quadro but not "
     "the FREQUENCY quadro, though the stem says 'nos quadros', plural."),
]


def files_for(tables, items_dir, year):
    if items_dir:
        return sorted(glob.glob(f"{items_dir}/*__items.csv"))
    return sorted(glob.glob(f"{tables}/batch_enem_{year}/*__items.csv"))


def loose(s):
    """Anchor regex tolerant of line breaks AND of script markers.

    The cell's line breaks are wherever the PDF wrapped, and 48_mark_scripts
    may have inserted "_" or "^" anywhere inside a word -- 98294's anchor
    reads "Ranking IV: 1^o Edu". Hard-coding the markers into the anchor
    couples this pass to that one, so a change there would silently break the
    anchor here. Allow an optional marker between any two characters instead.
    """
    return r"\s+".join("[_^]?".join(re.escape(c) for c in w) for w in s.split())


def run(tables, items_dir, only_year, apply_):
    done = missing = 0
    for year, item, anchor, table, probe, _why in RECOVER:
        if items_dir and year != only_year:
            continue
        hit = False
        for f in files_for(tables, items_dir, year):
            rows = list(csv.DictReader(open(f, encoding="utf-8")))
            tgt = [r for r in rows if r["item"] == item]
            if not tgt:
                continue
            old = tgt[0]["item_text"] or ""
            if re.search(loose(probe), old):
                print(f"  {year} {item:>7}  already present, skipped")
                hit = True
                break
            m = re.search(loose(anchor), old)
            if not m:
                print(f"  {year} {item:>7}  ANCHOR NOT FOUND -- not applied")
                hit = True; missing += 1
                break
            new = old[:m.end()] + "\n" + table + old[m.end():]
            if apply_:
                rewrite_field(f, old, new, expect=len(tgt))
            done += 1
            print(f"  {year} {item:>7}  {'inserted' if apply_ else 'would insert'} "
                  f"{len(table)} chars after {anchor[:44]!r}")
            hit = True
            break
        if not hit:
            print(f"  {year} {item:>7}  item not found")
            missing += 1
    print(f"\n{done} table(s) {'recovered' if apply_ else 'pending'}; {missing} problem(s)")
    return 1 if missing else 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tables")
    ap.add_argument("--items-dir")
    ap.add_argument("--year")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    if not (a.tables or a.items_dir):
        ap.error("give --tables or --items-dir")
    if a.items_dir and not a.year:
        ap.error("--items-dir needs --year")
    sys.exit(run(a.tables, a.items_dir, a.year, a.apply))
