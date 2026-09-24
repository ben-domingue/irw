# 100-item model-understanding check — results and disposition

`52_risk_sample.py` scored every one of the 2,210 items by *intervention* risk:
script-marker +3, fraction +3, hand-transcribed +4, AI-note +3, font-repaired
+2, letter-stripped +2, gap-filled +2, odd-char +1, short-stem +1, tiny-option
+1. 1,136 items carry at least one factor; 100 were drawn across all years and
areas, weighted toward the highest scores.

Each was presented as extracted text only — no PDF, no image — with the five
options shuffled out of key order. `?` was recorded wherever the item genuinely
cannot be answered without seeing the figure, rather than guessing.

```
answerable from text : 78 / 100
correct of those     : 72 / 78 = 92%        (chance = 20%)

by risk factor (correct / answerable):
  script-marker      52/54 =  96%     9 needed a figure
  letter-stripped     8/8  = 100%     1 needed a figure
  font-repaired      31/34 =  91%    11 needed a figure
  fraction            5/6  =  83%     4 needed a figure
  AI-note             3/5  =  60%     1 needed a figure
  hand-transcribed    2/3  =  67%     3 needed a figure
```

## The six wrong answers, each chased to the printed page

| item | key/mine | verdict |
|---|---|---|
| 2013 MT 43849 | D / B | **TEXT DEFECT**, and also not answerable. See below. |
| 2018 CN 111564 | B / C | My reasoning error. Text is complete: the geometry ("cartolina à direita, ventoinha à esquerda") is all there. |
| 2024 CN 117963 | E / B | My reasoning error. The description is complete and correct; I picked the reduction step instead of the oxidation one. |
| 2013 CN 11817 | D / C | Not answerable. The sign of the voltmeter reading depends on bridge orientation, which lives only in the figure. Should have been `?`. |
| 2021 CN 117891 | C / E | Not answerable. Requires comparing two drawn structural formulas; the extracted formula text is a glyph run. Should have been `?`. |
| 2021 CN 85781 | C / B | Not answerable. Projectile geometry is assigned by the figure, and two symbols (v0, g) are AI placeholder notes. Should have been `?`. |

Re-scored with the three unanswerable ones moved to `?`: **72 / 75 = 96%**, and
exactly **one** miss traceable to a defect in our text.

## What the one defect turned out to be

2013 MT 43849 prints `AC = 7/5 BD` as a stacked fraction at full body size.
`48_mark_scripts.py` keys on *reduced* size, so a stacked numerator is
invisible to it by construction — the only reliable signal is the fraction bar,
which is a drawing, not text. Extraction emitted `AC = 7 BD5`.

That is a class, not an instance, so it got its own pass: `53_stacked_fractions.py`.

**The fix does not make 43849 answerable, and saying so would be overclaiming.**
The stem now reads `AC = 7/5 BD ... o menor valor da razao l/BD`, which is what
the page prints. But whether AC and BD are the glass's diameters or its radii
is carried by the figure alone: as diameters the answer is 14/5 (option B, the
one I picked); the key, 24/5, follows if they are radii. So 43849 belongs with
the other three as figure-dependent. What the fix buys is that the text is no
longer *wrong* -- `AC = 7 BD5` is not a statement about anything.

Re-scored once more, with 43849 moved to `?` as well: **72 / 74 = 97%**, and
**no** remaining miss traceable to our text.
