#!/usr/bin/env python3
"""Cut the Redacao (essay) section out of the last LC item that absorbed it.

THE SHAPE. In the day-1 booklet the Redacao section is printed immediately
after the final Linguagens question, with no question number of its own and no
QUESTAO header to stop at. The item parser closes an item when it meets the
next question header, so for the LAST question of the area there is nothing to
close against and the whole essay apparatus -- motivating texts, the infographic
residue, PROPOSTA DE REDACAO, sometimes a stray page number -- lands inside that
one item's `item_text`.

Exactly FOUR items in the corpus are affected (2017 LC 60715, 2019 LC 76167,
2021 LC 120165, 2022 LC 86703) and no others; a scan for `PROPOSTA DE REDA`,
`motivador`, `dissertativo-argumentativo` and `proposta de intervencao` over
every item_text of every year returns these four and nothing else. The years
without the defect are the ones whose extraction never reached the essay pages.

Note `instructions` legitimately mentions the Redacao -- the booklet COVER says
the day-1 caderno contains the essay proposal. Do not strip that; this pass
touches `item_text` only.

WHY A KEEP-ANCHOR AND NOT A CUT-ANCHOR. The essay material does not begin with
a reliable marker. In 2021 and 2022 it opens with `Descricao da imagem:`, which
is the accessibility edition's own description of an essay TEXTO; in 2017 it
opens with `Descricao do grafico:`; and in 2017 the ITEM's own stimulus already
carries `TEXTO I`/`TEXTO II` labels, so anchoring on `TEXTO` would cut the item
in half. What IS stable is the end of the item's own question, so each entry
names the text to KEEP THROUGH and everything after it goes.

Every anchor below was confirmed by checking that the item's keyed option
completes the question grammatically:
  2017 60715 "...caracterizava pela"   + A "dissolucao das tonalidades..."
  2019 76167 "...construido por uma"   + A "segmentacao de enunciados..."
  2021 120165 "...concepcao de lingua que" + A "contrapoe caracteristicas..."
  2022 86703 "...como inventario e a"  + A "enumeracao de objetos e fatos."

In 2022 the PROPOSTA paragraph appears in the MIDDLE of the removed span rather
than at its end, because the essay pages are two-column and the content stream
emits the columns out of order. That is cosmetic to this pass: everything after
the question closer is essay material either way.

Usage:
  python3 59_strip_essay_section.py --items-dir DIR --year YYYY [--apply]
"""
import argparse, csv, glob, os, sys

SCHEMA = ["table", "section_id", "item", "instrument", "instructions", "section_prompt",
          "item_text", "correct_response", "option_text", "resp", "item_text_translated",
          "option_text_translated", "instructions_translated", "section_prompt_translated",
          "language", "resp_raw"]

# The removed span must look like essay material. If none of these occurs in
# what we are about to delete, the anchor has drifted into the item and the cut
# is refused -- this pass deletes text, so it fails closed.
ESSAY_SIGNALS = ("PROPOSTA DE REDA", "motivador", "dissertativo-argumentativo",
                 "proposta de interven")

CUTS = [
    dict(year="2017", area="lc", item="60715", expect_removed=2596,
         keep_through="artístico que se caracterizava pela",
         why="Rauschenberg 'Cama' item. Essay section (theme 'Desafios para a "
             "formação educacional de surdos no Brasil') begins at 'Descrição do "
             "gráfico:' describing the deaf-enrolment line chart, which is essay "
             "TEXTO material, not part of this item."),
    dict(year="2019", area="lc", item="76167", expect_removed=2235,
         keep_through="construído por uma",
         why="Ed Mort cronica item. Essay section (theme 'Democratização do acesso "
             "ao cinema no Brasil') follows the question closer."),
    dict(year="2021", area="lc", item="120165", expect_removed=1815,
         keep_through="uma concepção de língua que",
         why="Manoel de Barros 'A draga' item. Essay section (theme 'Invisibilidade "
             "e registro civil') begins at the 'Mapa da invisibilidade' poster "
             "description and runs through TEXTO 3, TEXTO 4 and the PROPOSTA."),
    dict(year="2022", area="lc", item="86703", expect_removed=3426,
         keep_through="como inventário é a",
         why="Machado de Assis 'Notas' item. Essay section (theme 'Desafios para a "
             "valorização de comunidades e povos tradicionais no Brasil') begins at "
             "the 'Povos tradicionais do Brasil' infographic description."),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--items-dir", required=True)
    ap.add_argument("--year", required=True)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    mine = [c for c in CUTS if c["year"] == a.year]
    if not mine:
        print("  no essay-section cut for %s" % a.year)
        return 0

    applied = 0
    problems = []
    for f in sorted(glob.glob(os.path.join(a.items_dir, "*__items.csv"))):
        rows = list(csv.DictReader(open(f, encoding="utf-8")))
        touched = False
        for c in mine:
            # an item occupies one row per option; item_text is duplicated
            # across them, so every matching row gets the same cut.
            targets = [r for r in rows if r["item"] == c["item"]]
            if not targets:
                continue
            for r in targets:
                v = r.get("item_text") or ""
                if not v:
                    continue
                n = v.count(c["keep_through"])
                if n != 1:
                    problems.append((c["item"], "anchor occurs %d times, need 1" % n))
                    continue
                end = v.index(c["keep_through"]) + len(c["keep_through"])
                removed = v[end:]
                if not removed.strip():
                    continue                      # already cut
                if not any(s in removed for s in ESSAY_SIGNALS):
                    problems.append((c["item"],
                                     "removed span carries no essay signal -- "
                                     "refusing to delete %d chars" % len(removed)))
                    continue
                # The essay-signal test above only catches an anchor that has
                # drifted PAST the essay. It cannot catch one that drifted
                # EARLIER, because the essay material is still inside the
                # removed span and the signal still matches -- a deliberately
                # mis-aimed anchor sailed through it in testing. The exact
                # removed length is the invariant that catches drift in BOTH
                # directions, so it is measured per item and enforced.
                if len(removed) != c["expect_removed"]:
                    problems.append((c["item"],
                                     "would remove %d chars, expected %d -- "
                                     "anchor or upstream text has changed"
                                     % (len(removed), c["expect_removed"])))
                    continue
                r["item_text"] = v[:end]
                applied += 1
                touched = True
        if touched and a.apply:
            with open(f, "w", newline="", encoding="utf-8") as fh:
                w = csv.DictWriter(fh, SCHEMA); w.writeheader()
                for r in rows:
                    w.writerow({k: r.get(k, "") for k in SCHEMA})

    print("  %s essay-section cut on %d row(s)"
          % ("applied" if a.apply else "WOULD apply", applied))
    for it, why in problems:
        print("     NOT cut: %s -- %s" % (it, why))
    return 0


if __name__ == "__main__":
    sys.exit(main())
