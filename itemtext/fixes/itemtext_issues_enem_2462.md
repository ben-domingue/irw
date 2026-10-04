# `itemtext_issues.qmd` entries for the ENEM tables — NOT yet applied

Prepared 2026-10-03 alongside #2462. **Not applied to the live page**
(`datapages/irw`, `itemtext_issues.qmd`), and it should go up only when the
#2462 PR merges and the affected tables are re-uploaded — the page's rule is
that a table earns an entry once it ships, and re-publishing is what makes
these descriptions public.

All eleven tables below carry `description_source=partly_generated`. **Six of
them earn that status in #2462** (2013 CH/LC, 2015 CH/LC, 2016 CH/LC); the
other five have had it since earlier batches and **have never had an entry
written** — the 2021 trio's debt has been outstanding since the 2026-09-11
ruling in #2226, and 2023 CN/MT since that batch shipped under #1848. They are included here so the
backlog is discharged rather than grown.

The eleven split into two unrelated kinds of generated text, and the page
should not blur them:

| kind | tables | what was generated |
|---|---|---|
| **figure descriptions** | 2013 CH/LC, 2015 CH/LC, 2016 CH/LC, 2023 CN/MT | prose describing a figure the booklet never puts into words |
| **notation placeholders** | 2021 CN/LC/MT | a short bracketed gloss naming a glyph the PDF's encoding does not expose |

One table, **2021 LC**, is in both: it already carried notation placeholders and
gains one figure description in #2462.

A note on how far these were checked, which belongs in the entries because it is
the thing a data user cannot see: every figure description added in #2462 was
read against the printed booklet **twice, by two independent reviewers, the
second blind to the first**. The first pass accepted 4 of 45 as drafted; the
second confirmed 10 of 45 of the corrected texts. Nine entries remain at
`medium` confidence and the reason is always the same — the embedded bitmap is
small (2016 CH 62021 is 170×242 px; 2013 LC 51365's painting 396×243; 2015 CH
28864 fits twelve miniatures into 818×717). Those are resolution ceilings of
INEP's own files, not unresolved questions.

```yaml
- table: enem_2013_1mil_ch
  issue: |-
    Five items in this table carry a description of their stimulus that was generated for this project rather than published by INEP, and each is marked inline `(gerada por IA)` so it can be separated from INEP's own words. These are items whose stimulus is a photograph, painting or map that the printed booklet never describes, so the shipped cell previously held only the credit line and the question and the item could not be answered from text at all. Three of the five are mixed: where the picture contains printed words — a legend, a caption, a panel's wording — those words are transcribed and sit outside the marked paragraph, because reading words off the page is recovery rather than generation. Every description was checked against the booklet twice by independent reviewers; 51365 is flagged medium confidence because its two embedded images are only 396x243 and 237x263 pixels, which is the limit of what INEP's file contains.
- table: enem_2013_1mil_lc
  issue: |-
    Thirteen items here carry a stimulus description generated for this project, each marked inline `(gerada por IA)`; nine of them are mixed, with the picture's own printed wording transcribed outside the marked paragraph. The stimuli are comic strips, cartoons, advertisements and a museum panel, none described in the printed booklet, so these items previously shipped with only a credit and a question. Four are flagged medium confidence (9614, 28727, 49507, 51091) and in every case the reason is the size of the embedded image rather than disagreement about what it shows — the Calvin and Hobbes strip, for instance, is 812x299 pixels for four panels. For 49507, a photographed 1911 school exercise, the two pencil annotations on the sheet are transcribed as the document's own words and only their position is described.
- table: enem_2015_1mil_ch
  issue: |-
    Seven items carry a generated stimulus description, marked inline `(gerada por IA)`, four of them mixed with transcribed legend or caption text outside the marked paragraph. One is worth singling out: 83810's weathering map has a four-class greyscale legend, and the item asks which climate corresponds to the weakest class, so the description names the printed class labels and assigns regions to classes. Those assignments were derived by sampling the legend's own grey values and classifying the map against them, not judged by eye. 28864 is medium confidence: it is a twelve-panel calendar in an 818x717 pixel reproduction, and at that size the sex of some figures and exact animal counts are at the limit of the source.
- table: enem_2015_1mil_lc
  issue: |-
    Seven items carry a generated stimulus description marked inline `(gerada por IA)`, four of them mixed. A further two items in this table gained text that is **not** generated and carries no marker: 33156 and 83482 reproduce wording printed inside the image itself — a poem rendered as a picture and a notice board — which is transcription of INEP's own source rather than new prose, on the same basis as text recovered from the standard booklet. For 49341, a Magritte painting, the description deliberately stops short of naming the relation between the figure and its reflection, because that relation is what the item asks the candidate to notice.
- table: enem_2016_1mil_ch
  issue: |-
    Four items carry a generated stimulus description marked inline `(gerada por IA)`, two of them mixed with transcribed caption text outside the marked paragraph. One of the four, 38717, reproduces the lettering of a Persepolis page; that lettering is transcribed, not generated, and it is transcribed as the booklet prints it. The booklet prints the name `MARIN`, although the Brazilian edition of the book is usually cited with `Narine`. This was settled on the native pixel grid of a 247x246 pixel bitmap whose caption glyphs are about five pixels tall, by per-column ink profile, so the transcription follows INEP's page rather than the published book. 62021 is medium confidence at 170x242 pixels.
- table: enem_2016_1mil_lc
  issue: |-
    Six items carry a generated stimulus description marked inline `(gerada por IA)`, three of them mixed with the image's printed wording transcribed outside the marked paragraph. 45089 and 61388 are medium confidence: both are photographs of installations reproduced small enough that some background detail is indistinct, and the descriptions say only what is distinguishable at the source's own resolution.
- table: enem_2021_1mil_cn
  issue: |-
    Seven items in this table contain short bracketed glosses, marked `(gerada por IA)`, standing in for glyphs that the booklet prints but its PDF encoding does not expose — most often a minus sign serving as an ionic charge or an exponent, and in a few places a physics symbol such as the one for gravitational acceleration or for speed. The gloss names what the symbol is; it is not a transcription, because the character itself could not be recovered from the file. Nothing else in these cells is generated: the surrounding text is INEP's own.
- table: enem_2021_1mil_lc
  issue: |-
    Two items contain short bracketed glosses marked `(gerada por IA)` standing in for glyphs the PDF's encoding does not expose — a typographic ff ligature and one unidentified symbol. Separately, item 118258 carries a generated description of its comic strip, also marked inline; the strip's own dialogue was already present in the cell from the PDF's text layer and is left as INEP wrote it, so the generated paragraph refers to the speeches by position rather than restating them.
- table: enem_2021_1mil_mt
  issue: |-
    One item contains bracketed glosses marked `(gerada por IA)` standing in for a Greek letter phi that the booklet prints but its PDF encoding does not expose. The gloss names the letter rather than reproducing it. Nothing else in the table is generated.
- table: enem_2023_1mil_cn
  issue: |-
    Three items carry a description of a figure that was generated for this project rather than published by INEP, each marked inline `(gerada por IA)`: two structural formulae and one chemical equation, none of which the booklet renders as text. The descriptions name atoms, substituents and reaction participants, so for these three items the chemistry a reader sees is a reading of INEP's diagram rather than INEP's own words.
- table: enem_2023_1mil_mt
  issue: |-
    Two items carry a generated figure description, marked inline `(gerada por IA)`: a geometric dot-pattern sequence and a distance-against-time graph. In both the figure is the item's data, so the numbers and the shape a reader sees are a reading of INEP's diagram rather than text INEP published.
```

## What still needs a human decision

Two points are deliberately left as they are, and a reviewer may want to rule
differently:

1. **2013 CH 25217 and 2013 LC 51365 each have two images but one insertion
   point.** Both descriptions are self-labelled (`Descrição da primeira
   imagem`, `Descrição do Mapa 2`) and both are correct, but the second one
   lands before the first image's credit line, which reads oddly. Splitting
   each into two insertions would be tidier and is a small change.
2. **2013 CH 44785's caption is 1930s typography in which accents are printed
   as displaced apostrophes** — `Havera' ainda quem resista a' poderosa
   influencia`. The transcription normalises those two to `Haverá` and `à`
   while leaving `influencia` unaccented as printed, which is internally
   inconsistent: it follows the typesetter's evident intent on the apostrophes
   and the page's literal glyphs on the missing circumflex. Either rule is
   defensible; the mixture is what should be settled.
