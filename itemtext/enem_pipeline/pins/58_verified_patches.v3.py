#!/usr/bin/env python3
"""Apply hand-verified per-item corrections, after every other pass.

WHY A SEPARATE PASS, AND WHY LAST. Each entry here was read off the printed
page and its `old` string copied from the SHIPPED cell -- i.e. from the text as
it looks after every other pass has run. Anchoring that to an earlier pass is
fragile: 43_normalize_glyphs.py runs before 46, 49 and 53, so an anchor taken
from the finished text would simply not be there yet. Running last means an
`old` string means exactly what it says.

WHAT BELONGS HERE. Corrections that geometry cannot generalise -- where the
rule-based passes have already declined and a human has read the page. What
does NOT belong here is anything a pass could learn: if a defect has a shape,
it belongs in the pass that owns that shape, with a rule.

TWO CONVENTIONS ARE ESTABLISHED BY THE ENTRIES BELOW, both ruled 2026-10-03
and both written up in EXTRACTION_RULES.md as R17 and R18:

  R17  a fraction side that is not a single token is PARENTHESISED:
       9!/(7! x 2!), not 9!/7! x 2!. Without it the text is simply wrong --
       2016 MT 39762's KEYED option ships as 6 489 600 where the printed bar
       spans the whole denominator and gives 1 622 400.

  R18  typographic emphasis lost in extraction is restored as ~~run~~.
       Plain ASCII, searchable, reversible -- the same properties 48's ^ and _
       were chosen for. The delimiter is "~~" because "~" and "`" are the only
       characters absent from all 48 tables; "*" already occurs 125 times
       (footnote marks, TiO2|S*) and "**" 20 times.

Usage:
  python3 58_verified_patches.py --items-dir DIR --year YYYY [--apply]
"""
import argparse, collections, csv, glob, os, sys

SCHEMA = ["table", "section_id", "item", "instrument", "instructions", "section_prompt",
          "item_text", "correct_response", "option_text", "resp", "item_text_translated",
          "option_text_translated", "instructions_translated", "section_prompt_translated",
          "language", "resp_raw"]

# (year, area, item, column, option letter or None, old, new, evidence, confidence)
PATCHES = [
    dict(year='2013', area='mt', item='31416', column='option_text', letter='C',
         old='62! 4!/10! 56!',
         new='(62! 4!)/(10! 56!)',
         conf='high', why="2013 Caderno7_Azul_Dom.pdf pageidx 18 (printed 'MT - 2º dia | Caderno 7 - AZUL - Página 19' block, QUESTÃO 136), right column. Shipped text came from 49_option_conventions.py rule (B), which joined the two printed lines '62! 4!' / '10! 56!' with '/' without parenthesising either side. One bar, so the fraction is (62! 4!)/(10! 56!) = P(62,6)/P(10,6). Arithmetic cross-check: the keyed answer is A = 62^6/10^6, and C is the per"),
    dict(year='2013', area='mt', item='31535', column='item_text', letter=None,
         old='F = G  \nm1m_2\nd^2\nonde',
         new='F = G  m1m_2/d^2\nonde',
         conf='high', why="2013 Caderno7_Azul_Dom.pdf pageidx 23 (QUESTÃO 154, right column). 53_stacked_fractions declines at step 4: the page reading order emits 'm 1 m 2 d 2', so the flattened pair '<num> <den>' is never adjacent. ADJACENT DEFECT NOT PATCHED: the leading subscript is shipped unmarked ('m1m_2'); geometry says m_1 (sz 5.66, y0 116.93 vs base y0 109.67), identical to the m_2"),
    dict(year='2013', area='mt', item='38092', column='item_text', letter=None,
         old='T(t) = − t^2\n4\n + 400',
         new='T(t) = − t^2/4 + 400',
         conf='high', why="2013 Caderno7_Azul_Dom.pdf pageidx 20 (QUESTÃO 145 region, left column). Declines at step 4: the superscript '2' of t^2 sits between numerator and denominator in reading order ('t 2 4'), so the pair 't 4' is not adjacent. Arithmetic cross-check: T=39 => t^2/4=361 => t=38, the keyed answer D = 38,0; with the /4 lost the item is unanswerable."),
    dict(year='2013', area='mt', item='41250', column='option_text', letter='A',
         old='N\n9',
         new='N/9',
         conf='high', why="2013 Caderno7_Azul_Dom.pdf pageidx 24 (QUESTÃO 158 region, left column). 53_stacked_fractions declines at STEP 2: the three option bars share an x-range, which its table-rule guard (xs[(x0,x1)] < 2, added for 2023 CN 66330) treats as a column of cell borders. 49_option_conventions also declines because its simple_fraction() only fires on all-numeric parts and 'N' has no"),
    dict(year='2013', area='mt', item='41250', column='option_text', letter='B',
         old='N\n6',
         new='N/6',
         conf='high', why='2013 Caderno7_Azul_Dom.pdf pageidx 24. Same decline cause as option A (shared x-range, step 2).'),
    dict(year='2013', area='mt', item='41250', column='option_text', letter='C',
         old='N\n3',
         new='N/3',
         conf='high', why='2013 Caderno7_Azul_Dom.pdf pageidx 24. Same decline cause as option A. Keyed answer is A = N/9 (sides tripled => area x9 => N/9 plates); the three flattened options are mutually indistinguishable as shipped.'),
    dict(year='2013', area='mt', item='9711', column='option_text', letter='B',
         old='S = k • M\n1\n3',
         new='S = k • M^(1/3)',
         conf='high', why="2013 Caderno7_Azul_Dom.pdf pageidx 23 (QUESTÃO 155 options, left column, printed page 24). A fraction INSIDE an exponent: sz 5.00 against a 9.75 body. Form '^(1/3)' follows 2015 MT 27281 D/E, which already ship '(0,5)^(t−1)' and '(1,5)^(t−1)' — the only parenthesised-exponent precedent in the corpus."),
    dict(year='2013', area='mt', item='9711', column='option_text', letter='C',
         old='S = k\n1\n• M\n1\n3 3',
         new='S = k^(1/3) • M^(1/3)',
         conf='high', why="2013 Caderno7_Azul_Dom.pdf pageidx 23. Also a step-2 decline for 53 (two bars share baseline y678.78). Exponent form taken from 2015 MT 27281's '(0,5)^(t−1)'."),
    dict(year='2013', area='mt', item='9711', column='option_text', letter='D',
         old='S = k\n1\n• M\n2\n3 3',
         new='S = k^(1/3) • M^(2/3)',
         conf='high', why="2013 Caderno7_Azul_Dom.pdf pageidx 23. KEYED OPTION. S^3 proportional to M^2 => S = k^(1/3) M^(2/3), which is what the page prints; the shipped 'S = k\\n1\\n• M\\n2\\n3 3' cannot be read as that."),
    dict(year='2013', area='mt', item='9711', column='option_text', letter='E',
         old='S = k\n1\n• M',
         new='S = k^(1/3) • M^2',
         conf='medium', why="2013 Caderno7_Azul_Dom.pdf pageidx 23. RECONSTRUCTION, not just a join: the shipped option E is TRUNCATED — it ends at '• M' and has lost both the '3' of k^(1/3) and the exponent '2' of M^2 that the page prints. Supported by the parallel structure of C and D on the same page and by 49_option_conventions' existing precedent for repairing"),
    dict(year='2015', area='cn', item='53958', column='item_text', letter=None,
         old='A razão entre os alcances D^d\nD_m\n,',
         new='A razão entre os alcances D_d/D_m,',
         conf='high', why="2015 rb_repaired/std_d1.pdf pageidx 24 (CN - 1º dia | Caderno 1 - AZUL - Página 25, QUESTÃO 70). FLAG: this patch also CORRECTS A WRONG SCRIPT ALREADY SHIPPED. The 'd' is a SUBSCRIPT (sz 5.68, y1 212.93 below the base glyph's y1 210.54) — geometrically identical to the k_d/k_m earlier in the same stem, which did ship as k_d and k_m. The shipped 'D^d' is wrong; leaving it while joining the fract"),
    dict(year='2015', area='cn', item='53958', column='option_text', letter='A',
         old='1\n4\n.',
         new='1/4.',
         conf='high', why="2015 rb_repaired/std_d1.pdf pageidx 24. 49_option_conventions declines because the trailing period lands on a THIRD line ('1\\n4\\n.') and its simple_fraction() requires exactly two parts. Mechanical and safe. Options C/D/E of the same item already ship '1.', '2.', '4.', so '1/4.' matches the item's own punctuation."),
    dict(year='2015', area='cn', item='53958', column='option_text', letter='B',
         old='1\n2\n.',
         new='1/2.',
         conf='high', why='2015 rb_repaired/std_d1.pdf pageidx 24. KEYED OPTION. Same three-part decline as option A.'),
    dict(year='2015', area='cn', item='82658', column='option_text', letter='A',
         old='λ\n4\n.',
         new='λ/4.',
         conf='high', why="2015 rb_repaired/std_d1.pdf pageidx 18 (CN - 1º dia, QUESTÃO 64 region). KEYED OPTION. Same three-part ('λ\\n4\\n.') decline in 49_option_conventions, plus its parts are not all numeric. Physics cross-check: one reflection with phase inversion => minimum thickness λ/4 = keyed answer A."),
    dict(year='2015', area='cn', item='82658', column='option_text', letter='B',
         old='λ\n2\n.',
         new='λ/2.',
         conf='high', why='2015 rb_repaired/std_d1.pdf pageidx 18. Same decline cause as option A.'),
    dict(year='2015', area='cn', item='82658', column='option_text', letter='C',
         old='3λ\n4\n.',
         new='3λ/4.',
         conf='high', why='2015 rb_repaired/std_d1.pdf pageidx 18. Same decline cause as option A.'),
    dict(year='2015', area='mt', item='40302', column='item_text', letter=None,
         old='P(x) = 8 + 5cos (\nπx − π\n)6\n,',
         new='P(x) = 8 + 5cos ((πx − π)/6),',
         conf='high', why="2015 rb_repaired/std_d2.pdf pageidx 30 (MT - 2º dia, right column). Both sides are compound, so 53's SIDE regex cannot match (limitation a). The parentheses in the NEW text around '(πx − π)' are editorial (they restore the bar's extent); the OUTER pair is printed. Arithmetic cross-check: minimum price when cos = −1 => (πx−π)/6 = π => x = 7 = julho = keyed answer D."),
    dict(year='2015', area='mt', item='54184', column='item_text', letter=None,
         old='=(\nidade da criança (em anos)\n) · dose do adulto\nidade da criança (em anos) + 12',
         new='= (idade da criança (em anos)/(idade da criança (em anos) + 12)) · dose do adulto',
         conf='medium', why="2015 rb_repaired/std_d2.pdf pageidx 24 (MT - 2º dia). Fórmula de Young. Declines at 53's SIDE regex: both sides are prose (limitation a), and the independent 'anything wordier is prose' guard would also reject it. The nested parentheses in the NEW text are unavoidable because the printed denominator itself contains '(em anos)'. Arithmetic cross-check:"),
    dict(year='2015', area='mt', item='60361', column='option_text', letter='B',
         old='9!/7! × 2!',
         new='9!/(7! × 2!)',
         conf='high', why="2015 rb_repaired/std_d2.pdf pageidx 26 (MT - 2º dia, left column). *** LIMITATION (b) CONFIRMED: THIS IS A CORRECTNESS BUG IN ALREADY-SHIPPED TEXT. *** The shipped '9!/7! × 2!' reads as (9!/7!)*2! = 144; the page prints 9!/(7!×2!) = 36 = C(9,2). 49_option_conventions.py rule (B) joined the two printed lines with '/' and did not parenthesise the product-valued denom"),
    dict(year='2015', area='mt', item='60361', column='option_text', letter='D',
         old='5!\n2!\n× 4!',
         new='5!/2! × 4!',
         conf='high', why="2015 rb_repaired/std_d2.pdf pageidx 26. The bar covers only '5!'/'2!', so '5!/2! × 4!' needs no parentheses. Declined by 53 at step 2 (its x-range matches options A and E) and by 49 because the option has three lines, which 49's docstring explicitly calls out as 'not verifiable' — the geometry now verifies it."),
    dict(year='2015', area='mt', item='60361', column='option_text', letter='E',
         old='5!\n4!\n× 4!\n3!',
         new='5!/4! × 4!/3!',
         conf='high', why='2015 rb_repaired/std_d2.pdf pageidx 26. Two fractions side by side on one line, so 53 drops both at step 2 (shared baseline) — the exact case PATCH_STEM was created for. 49 declines because the option has four lines.'),
    dict(year='2015', area='mt', item='62901', column='item_text', letter=None,
         old='7,5 4\n3 6,8\n3\n4\n3\n4Carta da mesa',
         new='7,5 4/3 6,8 3/4 3/4Carta da mesa',
         conf='medium', why="2015 rb_repaired/std_d2.pdf pageidx 19 (MT - 2º dia, the fanned-cards figure). NEW LIMITATION (c): a fraction bar on a ROTATED card is not a thin horizontal rect, so 53's bars_on() cannot see it at any tolerance. Arithmetic cross-check, which is what makes this safe: the carta da mesa is 6/8 = 0,75 and the hand holds 6/8, 75%, 3,4, 34%, 0,75, 4,3, 7,5, 4/3, 3/4 — exactly three"),
    dict(year='2015', area='mt', item='81781', column='option_text', letter='A',
         old='log (\nn + √n^2 + 4\n) − log (\nn − √n2 + 4\n)22',
         new='log ((n + √(n^2 + 4))/2) − log ((n − √(n^2 + 4))/2)',
         conf='medium', why="2015 rb_repaired/std_d2.pdf pageidx 23 (MT - 2º dia, right column). Two distinct drawn-rule kinds on one line: the fraction bar AND the radical vinculum. Both groupings are lost in the shipped text, so '√n^2 + 4' currently reads as (√n^2)+4. Declines in 53 at step 2 (the two fraction bars share baseline y514.48) and at the SIDE regex (compound sides). Arithmetic cro"),
    dict(year='2015', area='mt', item='81781', column='option_text', letter='B',
         old='log (1+\nn\n) − log (1 −\nn\n)22',
         new='log (1 + n/2) − log (1 − n/2)',
         conf='medium', why="2015 rb_repaired/std_d2.pdf pageidx 23. This settles the reading order: the two '2' glyphs that the shipped text dumps at the end ('...)22') are the two DENOMINATORS, and 'n' is the numerator — so it is 1 + n/2, not 1 + 2/n. Same conclusion applies to option A's trailing '22'."),
    dict(year='2015', area='mt', item='81781', column='option_text', letter='C',
         old='log (1+\nn\n) + log (1 −\nn\n)22',
         new='log (1 + n/2) + log (1 − n/2)',
         conf='medium', why="2015 rb_repaired/std_d2.pdf pageidx 23. Identical to option B except the connecting operator is '+'."),
    dict(year='2015', area='mt', item='81781', column='option_text', letter='D',
         old='log (\nn + √n^2 + 4\n)2',
         new='log ((n + √(n^2 + 4))/2)',
         conf='medium', why='2015 rb_repaired/std_d2.pdf pageidx 23. Same two-rule-kind structure as option A, one term instead of two.'),
    dict(year='2015', area='mt', item='81781', column='option_text', letter='E',
         old='2 log (\nn + √n^2 + 4\n)2',
         new='2 log ((n + √(n^2 + 4))/2)',
         conf='medium', why='2015 rb_repaired/std_d2.pdf pageidx 23. KEYED OPTION, and the one the derivation reproduces: h = 2 log((n + √(n^2+4))/2).'),
    dict(year='2016', area='cn', item='16901', column='item_text', letter=None,
         old='R = \nnproduto\n× 100nreagente limitante',
         new='R = nproduto/(nreagente limitante) × 100',
         conf='medium', why="2016 rb_repaired/std_d1.pdf pageidx 19 (CN - 1º dia, right column). Limitation (a): both sides are multi-word. NOTATION CHOICE FLAGGED FOR A RULING: there is no corpus precedent for either parenthesising a wordy denominator or for 'fraction × scalar'; the only existing '/(' in all 48 tables is the unit 'kJ/(kg °C)' in 2016 CN 24399. I parenthesise the denominator be"),
    dict(year='2016', area='cn', item='86572', column='item_text', letter=None,
         old='a razão \nR AB\nR BC\n,',
         new='a razão R_AB/R_BC,',
         conf='medium', why="2016 rb_repaired/std_d1.pdf pageidx 20 (CN - 1º dia, left column). I restore the subscripts because without them each side contains a space ('R AB'), which would force an unreadable '(R AB)/(R BC)'. The subscript sizes/offsets are measured and match the documented '_' convention (e.g. 'C_10H_16O'). Note the same stem elsewhere ships 'RAB e RBC' unmarked, so this le"),
    dict(year='2016', area='cn', item='87728', column='item_text', letter=None,
         old='+ 5\n2\n O2 (g)',
         new='+ 5/2 O2 (g)',
         conf='high', why="2016 rb_repaired/std_d1.pdf pageidx 16 (CN - 1º dia). Stoichiometric coefficient 5/2 for O2 in the acetylene combustion. Declines at step 4/5 for the same reason as 51275: the page reads 'C 2H2' where the stem now reads 'C 2H2'/'CO2' with scripts partly marked, so the page-derived context no longer matches the row."),
    dict(year='2016', area='cn', item='87728', column='item_text', letter=None,
         old='+ 15\n2\n O2 (g)',
         new='+ 15/2 O2 (g)',
         conf='high', why='2016 rb_repaired/std_d1.pdf pageidx 16. Coefficient 15/2 for O2 in the benzene combustion. Arithmetic cross-check: 2*(−780) ... the trimerization ΔH = 3*(−310) − (−780) = −150 = keyed answer B, which requires the half-coefficients to be present for the equations to balance.'),
    dict(year='2016', area='mt', item='24747', column='option_text', letter='C',
         old='500 . D^2\nA',
         new='500 . D^2/A',
         conf='high', why="2016 rb_repaired/std_d2.pdf pageidx 20 (MT - 2º dia, left column). 49_option_conventions declines because its simple_fraction() requires every part to contain a digit and the denominator is the bare letter 'A'. Arithmetic cross-check: the keyed answer is B = 500A/D^2 and C is its inverse-ratio distractor."),
    dict(year='2016', area='mt', item='24747', column='option_text', letter='E',
         old='500 . 3 . D^2\nA',
         new='500 . 3 . D^2/A',
         conf='high', why='2016 rb_repaired/std_d2.pdf pageidx 20. Same digit-less-denominator decline as option C.'),
    dict(year='2016', area='mt', item='39762', column='option_text', letter='D',
         old='10^2 . 26^2 . 4!/2! . 2!',
         new='10^2 . 26^2 . 4!/(2! . 2!)',
         conf='high', why="2016 rb_repaired/std_d2.pdf pageidx 26 (MT - 2º dia, left column). *** LIMITATION (b): CORRECTNESS BUG IN ALREADY-SHIPPED TEXT. *** Shipped '4!/2! . 2!' reads as (4!/2!)*2! = 24; the page prints 4!/(2!*2!) = 6 = C(4,2), the number of ways to place two digits among four slots. 49_option_conventions rule (B) again joined two printed lines without parenthesising a pro"),
    dict(year='2016', area='mt', item='39762', column='option_text', letter='E',
         old='10^2 . 52^2 . 4!/2! . 2!',
         new='10^2 . 52^2 . 4!/(2! . 2!)',
         conf='high', why='2016 rb_repaired/std_d2.pdf pageidx 26. *** LIMITATION (b), AND THIS IS THE KEYED OPTION. *** Arithmetic cross-check: 10^2 * 52^2 * 4!/(2!*2!) = 100*2704*6 = 1622400 is the correct count for the item; the shipped ungrouped form evaluates to 10^2*52^2*24 = 6489600, four times too large. This is the single most consequential cell in the tab'),
    dict(year='2016', area='mt', item='40660', column='option_text', letter='A',
         old='10!\n−\n4!\n2! × 8! 2! × 2!',
         new='10!/(2! × 8!) − 4!/(2! × 2!)',
         conf='high', why='2016 rb_repaired/std_d2.pdf pageidx 19 (MT - 2º dia, right column). KEYED OPTION. Declines on BOTH limitations at once: step 2 (the two bars share a baseline) and the SIDE regex (compound denominators). Arithmetic cross-check: C(10,2) − C(4,2) = 45 − 6 = 39 pairs with not both left-handed; 10!/(2!×8!) − 4!/(2!×2!) is exactly that, and the ungrouped reading is not.'),
    dict(year='2016', area='mt', item='40660', column='option_text', letter='B',
         old='10!\n−\n4!\n8! 2!',
         new='10!/8! − 4!/2!',
         conf='high', why='2016 rb_repaired/std_d2.pdf pageidx 19. Needs no parentheses; the bar widths are what distinguish B from A.'),
    dict(year='2016', area='mt', item='40660', column='option_text', letter='C',
         old='10!\n− 2\n2! × 8!',
         new='10!/(2! × 8!) − 2',
         conf='high', why='2016 rb_repaired/std_d2.pdf pageidx 19. Denominator is a product under one bar, so it is parenthesised.'),
    dict(year='2016', area='mt', item='40660', column='option_text', letter='D',
         old='6!\n+ 4 × 4\n4!',
         new='6!/4! + 4 × 4',
         conf='high', why='2016 rb_repaired/std_d2.pdf pageidx 19. Narrow bar => only 6!/4! is inside the fraction.'),
    dict(year='2016', area='mt', item='40660', column='option_text', letter='E',
         old='6!\n+ 6 × 4\n4!',
         new='6!/4! + 6 × 4',
         conf='high', why='2016 rb_repaired/std_d2.pdf pageidx 19. Narrow bar => only 6!/4! is inside the fraction.'),
    dict(year='2016', area='mt', item='60315', column='item_text', letter=None,
         old='M = \n2\nlog (\nE\n)3E 0\n,',
         new='M = 2/3 log (E/E_0),',
         conf='high', why="2016 rb_repaired/std_d2.pdf pageidx 30 (MT - 2º dia, right column). Step-2 decline (shared baseline) plus, for the second bar, a subscripted denominator. I write 'E_0' because the SAME stem already ships 'E_0 uma constante real positiva' two lines later, so the form is taken from the item itself. Arithmetic cross-check: M = (2/3) log(E/E_0) with M=9 and M=7 gives E_"),
    dict(year='2016', area='mt', item='60315', column='option_text', letter='D',
         old='E_1 = 10\n9\n7 . E_2',
         new='E_1 = 10^(9/7) . E_2',
         conf='high', why="2016 rb_repaired/std_d2.pdf pageidx 30. The sz-4.00 against a sz-9.75 body is what distinguishes this from option E (next row), where the same 9/7 is printed at full body size. Form '10^(9/7)' follows 2015 MT 27281's '(0,5)^(t−1)'."),
    dict(year='2016', area='mt', item='60315', column='option_text', letter='E',
         old='E_1 = 9\n7\n. E_2',
         new='E_1 = 9/7 . E_2',
         conf='high', why='2016 rb_repaired/std_d2.pdf pageidx 30. The size contrast with option D is the whole point: D is 10^(9/7), E is (9/7).'),
    dict(year='2016', area='mt', item='95265', column='item_text', letter=None,
         old='pela razão A\nA + B\n, em que A e B',
         new='pela razão A/(A + B), em que A e B',
         conf='high', why="2016 rb_repaired/std_d2.pdf pageidx 26 (MT - 2º dia, right column). Limitation (a): the denominator 'A + B' is compound, so the SIDE regex cannot match it. The parentheses are required — 'A/A + B' would read as (A/A)+B = 1+B. Arithmetic cross-check: the Gini index as A/(A+B) with the stated geometry gives the keyed answer A = 40%."),
    dict(year='2019', area='cn', item='117883', column='item_text', letter=None,
         old='A razão \nk^A\nkB\n é mais próxima de',
         new='A razão k_A/k_B é mais próxima de',
         conf='high', why="2019 ENEM_2019_P1_CAD_05_DIA_2_AMARELO.pdf pageidx 11. FLAG: this patch also CORRECTS A WRONG SCRIPT ALREADY SHIPPED. The 'A' is a SUBSCRIPT — sz 6.00 against a 10.30 body, and its y1 644.87 sits BELOW the base glyph's y1 642.53. The same stem already ships 'suas condutividades térmicas k_A e k_B' correctly, so 'k^A' contradicts the item's own text. Ari"),
    dict(year='2021', area='cn', item='117627', column='item_text', letter=None,
         old='1  __\n2  O2 + H^2O + 2 e',
         new='1/2 O2 + H_2O + 2 e',
         conf='medium', why="2021 rb_repaired/ENEM_2021_P1_CAD_07_DIA_2_AZUL.pdf pageidx 12 (the fuel-cell quadro, AFC row). NEW LIMITATION (d): INEP typed this fraction rather than drawing it, so no bar-based rule can ever see it — the signal is the literal '__' span sitting between two single-digit spans at the same x. Patch is mechanical. CAVEAT: the surrounding cell is heavily damaged and carries '[notação não extraív SECOND DEFECT IN THE SAME SPAN, corrected here rather than as a separate entry so that one patch owns one rewrite: water ships as H^2O, the WRONG KIND of script. Span geometry on this line puts the base at y0 182.61 and the 2 at y0 189.00, 6.4pt BELOW the baseline, while the charge marks on the same line (the + of H+, the - of e-) sit at y0 183.10, ABOVE it -- the page distinguishes the two directions and this one is down. Chemistry corroborates: the AFC cathode is 1/2 O2 + H2O + 2 e- -> 2 OH-. Third of three wrong-kind scripts in this batch (cf. 2015 CN 53958 D^d, 2019 CN 117883 k^A); a corpus-wide scan for a script marked between two letters of one token returns this cell and no other, so it is a one-off, not a pass-level rule. Marked rather than flattened because H_2O (154) outnumbers plain H2O (119) in the corpus."),
    dict(year='2021', area='cn', item='117627', column='item_text', letter=None,
         old='1  __\n2 \n O2 + CO_2 + 2 e',
         new='1/2 O2 + CO_2 + 2 e',
         conf='medium', why='2021 rb_repaired/ENEM_2021_P1_CAD_07_DIA_2_AZUL.pdf pageidx 12 (MSFC row). Second of three identical ½ coefficients in the same quadro.'),
    dict(year='2021', area='cn', item='117627', column='item_text', letter=None,
         old='1  __\n2 \n O2 + 2 H^+ + 2 e',
         new='1/2 O2 + 2 H^+ + 2 e',
         conf='low', why="2021 rb_repaired/ENEM_2021_P1_CAD_07_DIA_2_AZUL.pdf pageidx 12 (PEM row). Lowest confidence of the three: I measured the AFC and MSFC instances span-by-span and inferred the PEM one from the identical shipped '1 __\\n2 \\n O2 + 2 H^+ + 2 e' pattern in the same column of the same table. PEM is the KEYED row (answer C), so if only two are patched this is the one to drop, not"),
    dict(year='2022', area='mt', item='47309', column='option_text', letter='A',
         old='9 6\n62×−\n!\n!()',
         new='9 × 6!/(6 − 2)!',
         conf='high', why="2022 ENEM_2022_DIGITAL_CAD_05_DIA_2_AMARELO.pdf pageidx 67 (same item also at ENEM_2022_P1_CAD_05_DIA_2_AMARELO.pdf pageidx 19). In this booklet the ×, −, ( and ) are VECTOR GLYPHS, not text: no 2022 booklet contains a '×' character for this item, yet the shipped cell has one, so 57_drawn_glyphs.py already recovered them and appended them out of position. The recovered glyph multiset is the cross-check: shipped option A carri"),
    dict(year='2022', area='mt', item='47309', column='option_text', letter='B',
         old='9 6\n62 2×−×\n!\n!!()',
         new='9 × 6!/((6 − 2)! × 2!)',
         conf='high', why="2022 ENEM_2022_DIGITAL_CAD_05_DIA_2_AMARELO.pdf pageidx 67. KEYED OPTION. Shipped glyph multiset is two ×, one −, one ( and one ) — matching '9 × 6!/((6 − 2)! × 2!)'; the outer pair around the denominator is editorial (it restores the bar's extent). Arithmetic: 9 * C(6,2) = 135, and 6 of the 8 flats per floor (endings 1-6) get morning sun, so 135 is the item"),
    dict(year='2022', area='mt', item='47309', column='option_text', letter='C',
         old='9 4\n42 2×−×\n!\n!!()',
         new='9 × 4!/((4 − 2)! × 2!)',
         conf='high', why='2022 ENEM_2022_DIGITAL_CAD_05_DIA_2_AMARELO.pdf pageidx 67. Same shape as option B with 6 replaced by 4. Glyph multiset (two ×, one −, one paren pair) matches.'),
    dict(year='2022', area='mt', item='47309', column='option_text', letter='D',
         old='9 2\n22 2×−×\n!\n!!()',
         new='9 × 2!/((2 − 2)! × 2!)',
         conf='high', why='2022 ENEM_2022_DIGITAL_CAD_05_DIA_2_AMARELO.pdf pageidx 67. Same shape as option B with 6 replaced by 2. Glyph multiset matches.'),
    dict(year='2022', area='mt', item='47309', column='option_text', letter='E',
         old='9 8\n82 2 1× −×−!\n!!()\n⎛\n⎝\n⎜⎜\n⎞\n⎠\n⎟⎟',
         new='9 × (8!/((8 − 2)! × 2!) − 1)',
         conf='medium', why="2022 ENEM_2022_DIGITAL_CAD_05_DIA_2_AMARELO.pdf pageidx 67. Most reconstructed of the five. The shipped cell carries the sz-piecewise big-bracket glyphs ⎛⎝⎜⎜⎞⎠⎟⎟, which is independent evidence of an outer grouping around 'fraction − 1', and the second drawn minus sits at the fraction's mid-height rather than inside the denominator. Glyph multiset: two ×, two"),
    dict(year='2022', area='mt', item='89637', column='option_text', letter='A',
         old='1\n46\n1\n45+',
         new='1/46 + 1/45',
         conf='high', why="2022 ENEM_2022_DIGITAL_CAD_05_DIA_2_AMARELO.pdf pageidx 67-68 region (the bingo item). Step-2 decline (shared baseline). Both denominators are single tokens, so no parentheses. The '+' in the shipped cell was recovered by 57_drawn_glyphs and appended at the end, which is why it reads '45+'."),
    dict(year='2022', area='mt', item='89637', column='option_text', letter='B',
         old='1\n46\n2\n46 45+×',
         new='1/46 + 2/(46 × 45)',
         conf='high', why="2022 ENEM_2022_DIGITAL_CAD_05_DIA_2_AMARELO.pdf pageidx 67-68 region. The bar-width contrast is decisive: 17.58 for a single-token denominator versus 44.42 for the product. Shipped '1\\n46\\n2\\n46 45+×' carries one '+' and one '×', matching '1/46 + 2/(46 × 45)'."),
    dict(year='2022', area='mt', item='89637', column='option_text', letter='C',
         old='1\n46\n8\n46 45+×',
         new='1/46 + 8/(46 × 45)',
         conf='high', why='2022 ENEM_2022_DIGITAL_CAD_05_DIA_2_AMARELO.pdf pageidx 67-68 region. Same structure as option B with numerator 8.'),
    dict(year='2022', area='mt', item='89637', column='option_text', letter='D',
         old='1\n46\n43\n46 45+×',
         new='1/46 + 43/(46 × 45)',
         conf='high', why='2022 ENEM_2022_DIGITAL_CAD_05_DIA_2_AMARELO.pdf pageidx 67-68 region. Same structure as option B with numerator 43.'),
    dict(year='2022', area='mt', item='89637', column='option_text', letter='E',
         old='1\n46\n49\n46 45+×',
         new='1/46 + 49/(46 × 45)',
         conf='high', why="2022 ENEM_2022_DIGITAL_CAD_05_DIA_2_AMARELO.pdf pageidx 67-68 region. KEYED OPTION. Same structure as option B with numerator 49. As shipped, all five options reduce to the indistinguishable shape '1 46 <k> 46 45+×' and the keyed one cannot be identified."),
    dict(year='2013', area='lc', item='43715', column='item_text', letter=None,
         old='Novas tecnologias\nAtualmente, prevalece na mídia um discurso de \nexaltação das novas tecnologias, principalmente aquelas \nligadas às atividades de telecomunicações. Expressões \nfrequentes como “o futuro já chegou”, “maravilhas \ntecnológicas” e “conexão total com o mundo” “fetichizam” \nnovos produtos, transformando-os em objetos do desejo, \nde consumo obrigatório. Por esse motivo carregamos  \nhoje nos bolsos, bolsas e mochilas o “futuro” tão festejado.\nTodavia, não podemos reduzir-nos a meras vítimas \nde um aparelho midiático perverso, ou de um aparelho \ncapitalista controlador. Há perversão, certamente, \ne controle, sem sombra de dúvida. Entretanto, \ndesenvolvemos uma relação simbiótica de dependência \nmútua com os veículos de comunicação, que se estreita \na cada imagem compartilhada e a cada dossiê  pessoal \ntransformado em objeto público de entretenimento.\nNão mais como aqueles acorrentados na caverna de \nPlatão, somos livres para nos aprisionar, por espontânea \nvontade, a esta relação sadomasoquista com as \nestruturas midiáticas, na qual tanto controlamos quanto \nsomos controlados.\nSAMPAIO, A. S. A microfísica do espetáculo. Disponível em: http://observatoriodaimprensa.com.br.\nAcesso em: 1 mar. 2013 (adaptado).\nAo escrever um artigo de opinião, o produtor precisa criar \numa base de orientação linguística que permita alcançar \nos leitores e convencê-los com relação ao ponto de vista \ndefendido. Diante disso, nesse texto, a escolha das \nformas verbais em destaque objetiva',
         new='~~Novas tecnologias~~\nAtualmente, prevalece na mídia um discurso de \nexaltação das novas tecnologias, principalmente aquelas \nligadas às atividades de telecomunicações. Expressões \nfrequentes como “o futuro já chegou”, “maravilhas \ntecnológicas” e “conexão total com o mundo” “fetichizam” \nnovos produtos, transformando-os em objetos do desejo, \nde consumo obrigatório. Por esse motivo ~~carregamos~~  \nhoje nos bolsos, bolsas e mochilas o “futuro” tão festejado.\nTodavia, não ~~podemos~~ reduzir-nos a meras vítimas \nde um aparelho midiático perverso, ou de um aparelho \ncapitalista controlador. Há perversão, certamente, \ne controle, sem sombra de dúvida. Entretanto, \n~~desenvolvemos~~ uma relação simbiótica de dependência \nmútua com os veículos de comunicação, que se estreita \na cada imagem compartilhada e a cada ~~dossiê~~  pessoal \ntransformado em objeto público de entretenimento.\nNão mais como aqueles acorrentados na caverna de \nPlatão, ~~somos~~ livres para nos aprisionar, por espontânea \nvontade, a esta relação sadomasoquista com as \nestruturas midiáticas, na qual tanto ~~controlamos~~ quanto \nsomos controlados.\nSAMPAIO, A. S. A microfísica do espetáculo. Disponível em: http://observatoriodaimprensa.com.br.\nAcesso em: 1 mar. 2013 (adaptado).\nAo escrever um artigo de opinião, o produtor precisa criar \numa base de orientação linguística que permita alcançar \nos leitores e convencê-los com relação ao ponto de vista \ndefendido. Diante disso, nesse texto, a escolha das \nformas verbais em destaque objetiva',
         conf='high', why="Caderno7_Azul_Dom p7. Arial-BoldMT on carregamos / podemos / desenvolvemos / somos / controlamos and on the title 'Novas tecnologias'; Arial-ItalicMT on 'dossie'. The stem asks about 'a escolha das formas verbais em destaque', so without the marking the item points at an invisible highlight. The extraction left a DOUBLE SPACE at each font boundary, which is where each run was located."),
    dict(year="2015", area="mt", item="29167", column="item_text", letter=None,
         old="que ser\u00e3o  por uma",
         new="que ser\u00e3o substitu\u00eddas por uma",
         conf='high', why="2015 MT. `moved_word` pair with 29359. The stem reads 'duas antenas que seraO  por uma nova, mais potente.' with a DOUBLE SPACE where a word belongs, and the missing word is confirmed three independent ways: the gap's own grammar needs a participle; the item's NEXT sentence says 'as areas de cobertura das antenas que serao substituidas'; and the missing token is physically present in a DIFFERENT item's option (29359 option E, patched in the same batch). So this is not a guess at wording -- the word migrated across items and is being put back."),
    dict(year="2015", area="mt", item="29359", column="option_text", letter="E",
         old="5 216,68\n substitu\u00eddas ",
         new="5 216,68",
         conf='high', why="2015 MT. The other half of the 29167 pair: option E ships '5 216,68\\n substituidas ', where 'substituidas' is the word missing from item 29167's stem. E is the KEYED option, so the stray token sits in the answer. Removing it leaves the numeric option the booklet prints."),
    dict(year="2016", area="mt", item="24747", column="item_text", letter=None,
         old="fonte sonora, \u00e9\nA\n500 . 81",
         new="fonte sonora, \u00e9",
         conf='high', why="2016 MT, QUESTAO 150, std_d2 pageidx 20 ('MT - 2o dia | Caderno 7 - AZUL - Pagina 21'). `moved_word`: option A is a stacked fraction and its NUMERATOR plus its option letter were swept into the stem, so item_text ends '...fonte sonora, e\\nA\\n500 . 81'. Verified by rendering the page. The stem ends at 'e'; everything after is option A."),
    dict(year="2016", area="mt", item="24747", column="option_text", letter="A",
         old=". D^2",
         new="500 . 81/(A . D^2)",
         conf='high', why="2016 MT QUESTAO 150 option A, read off the rendered page: the printed option is 500 . 81 over A . D^2 (numerator '500 . 81', denominator 'A . D^2', one bar). Shipped as just '. D^2' because the numerator went to the stem. R17 applies and is LOAD-BEARING here: written flat as '500 . 81/A . D^2' it reads 500 . (81/A) . D^2, which puts D^2 in the NUMERATOR and inverts the physics (cost is inversely proportional to the square of the distance). Options B-E need no parentheses -- '500 . A/D^2' already reads 500 . (A/D^2) correctly -- so only A is changed."),
    dict(year="2016", area="mt", item="39198", column='option_text', letter="A",
         old="B\nC",
         new="",
         conf='high', why="2016 MT 39198 `figure_labels`: the five options ARE diagrams and the shipped option_text is label residue scraped off them, so the options cannot be told apart -- A, B, C, D and E are permutations of the bare letters A/B/C with no values at all. Ruled by Mateus 2026-10-03: set the options to NA and do NOT generate descriptions, so the column says 'these options are pictures' by being empty rather than by shipping unusable text. This follows established corpus convention, not a new one: 50 items across all twelve years already ship with every option NA for exactly this reason. No AI text and no provenance flip. Blanked cell was \"B\\nC\"."),
    dict(year="2016", area="mt", item="39198", column='option_text', letter="B",
         old="A B",
         new="",
         conf='high', why="2016 MT 39198 `figure_labels`: the five options ARE diagrams and the shipped option_text is label residue scraped off them, so the options cannot be told apart -- A, B, C, D and E are permutations of the bare letters A/B/C with no values at all. Ruled by Mateus 2026-10-03: set the options to NA and do NOT generate descriptions, so the column says 'these options are pictures' by being empty rather than by shipping unusable text. This follows established corpus convention, not a new one: 50 items across all twelve years already ship with every option NA for exactly this reason. No AI text and no provenance flip. Blanked cell was \"A B\"."),
    dict(year="2016", area="mt", item="39198", column='option_text', letter="C",
         old="C A BC",
         new="",
         conf='high', why="2016 MT 39198 `figure_labels`: the five options ARE diagrams and the shipped option_text is label residue scraped off them, so the options cannot be told apart -- A, B, C, D and E are permutations of the bare letters A/B/C with no values at all. Ruled by Mateus 2026-10-03: set the options to NA and do NOT generate descriptions, so the column says 'these options are pictures' by being empty rather than by shipping unusable text. This follows established corpus convention, not a new one: 50 items across all twelve years already ship with every option NA for exactly this reason. No AI text and no provenance flip. Blanked cell was \"C A BC\"."),
    dict(year="2016", area="mt", item="39198", column='option_text', letter="D",
         old="A BC",
         new="",
         conf='high', why="2016 MT 39198 `figure_labels`: the five options ARE diagrams and the shipped option_text is label residue scraped off them, so the options cannot be told apart -- A, B, C, D and E are permutations of the bare letters A/B/C with no values at all. Ruled by Mateus 2026-10-03: set the options to NA and do NOT generate descriptions, so the column says 'these options are pictures' by being empty rather than by shipping unusable text. This follows established corpus convention, not a new one: 50 items across all twelve years already ship with every option NA for exactly this reason. No AI text and no provenance flip. Blanked cell was \"A BC\"."),
    dict(year="2016", area="mt", item="39198", column='option_text', letter="E",
         old="A B\nC",
         new="",
         conf='high', why="2016 MT 39198 `figure_labels`: the five options ARE diagrams and the shipped option_text is label residue scraped off them, so the options cannot be told apart -- A, B, C, D and E are permutations of the bare letters A/B/C with no values at all. Ruled by Mateus 2026-10-03: set the options to NA and do NOT generate descriptions, so the column says 'these options are pictures' by being empty rather than by shipping unusable text. This follows established corpus convention, not a new one: 50 items across all twelve years already ship with every option NA for exactly this reason. No AI text and no provenance flip. Blanked cell was \"A B\\nC\"."),
    dict(year="2020", area="cn", item="62745", column='option_text', letter="A",
         old="Amper\u00edmetro\nBateria\nCircuito do ve\u00edculo\n0,5 A",
         new="",
         conf='high', why="2020 CN 62745 `figure_labels`: the five options ARE diagrams and the shipped option_text is label residue scraped off them, so the options cannot be told apart -- all five are the same four circuit labels reordered, distinguishable only by an ammeter reading. Ruled by Mateus 2026-10-03: set the options to NA and do NOT generate descriptions, so the column says 'these options are pictures' by being empty rather than by shipping unusable text. This follows established corpus convention, not a new one: 50 items across all twelve years already ship with every option NA for exactly this reason. No AI text and no provenance flip. Blanked cell was \"Amper\\u00edmetro\\nBateria\\nCircuito do ve\\u00edculo\\n0,5 A\"."),
    dict(year="2020", area="cn", item="62745", column='option_text', letter="B",
         old="Bateria\nAmper\u00edmetro\n0,5 A\nCircuito do ve\u00edculo",
         new="",
         conf='high', why="2020 CN 62745 `figure_labels`: the five options ARE diagrams and the shipped option_text is label residue scraped off them, so the options cannot be told apart -- all five are the same four circuit labels reordered, distinguishable only by an ammeter reading. Ruled by Mateus 2026-10-03: set the options to NA and do NOT generate descriptions, so the column says 'these options are pictures' by being empty rather than by shipping unusable text. This follows established corpus convention, not a new one: 50 items across all twelve years already ship with every option NA for exactly this reason. No AI text and no provenance flip. Blanked cell was \"Bateria\\nAmper\\u00edmetro\\n0,5 A\\nCircuito do ve\\u00edculo\"."),
    dict(year="2020", area="cn", item="62745", column='option_text', letter="C",
         old="Bateria\nAmper\u00edmetro2,5 A\nCircuito do ve\u00edculo",
         new="",
         conf='high', why="2020 CN 62745 `figure_labels`: the five options ARE diagrams and the shipped option_text is label residue scraped off them, so the options cannot be told apart -- all five are the same four circuit labels reordered, distinguishable only by an ammeter reading. Ruled by Mateus 2026-10-03: set the options to NA and do NOT generate descriptions, so the column says 'these options are pictures' by being empty rather than by shipping unusable text. This follows established corpus convention, not a new one: 50 items across all twelve years already ship with every option NA for exactly this reason. No AI text and no provenance flip. Blanked cell was \"Bateria\\nAmper\\u00edmetro2,5 A\\nCircuito do ve\\u00edculo\"."),
    dict(year="2020", area="cn", item="62745", column='option_text', letter="D",
         old="Bateria\nAmper\u00edmetro\n12 A\nCircuito do ve\u00edculo",
         new="",
         conf='high', why="2020 CN 62745 `figure_labels`: the five options ARE diagrams and the shipped option_text is label residue scraped off them, so the options cannot be told apart -- all five are the same four circuit labels reordered, distinguishable only by an ammeter reading. Ruled by Mateus 2026-10-03: set the options to NA and do NOT generate descriptions, so the column says 'these options are pictures' by being empty rather than by shipping unusable text. This follows established corpus convention, not a new one: 50 items across all twelve years already ship with every option NA for exactly this reason. No AI text and no provenance flip. Blanked cell was \"Bateria\\nAmper\\u00edmetro\\n12 A\\nCircuito do ve\\u00edculo\"."),
    dict(year="2020", area="cn", item="62745", column='option_text', letter="E",
         old="12 A\nBateria\nAmper\u00edmetro\nCircuito do ve\u00edculo",
         new="",
         conf='high', why="2020 CN 62745 `figure_labels`: the five options ARE diagrams and the shipped option_text is label residue scraped off them, so the options cannot be told apart -- all five are the same four circuit labels reordered, distinguishable only by an ammeter reading. Ruled by Mateus 2026-10-03: set the options to NA and do NOT generate descriptions, so the column says 'these options are pictures' by being empty rather than by shipping unusable text. This follows established corpus convention, not a new one: 50 items across all twelve years already ship with every option NA for exactly this reason. No AI text and no provenance flip. Blanked cell was \"12 A\\nBateria\\nAmper\\u00edmetro\\nCircuito do ve\\u00edculo\"."),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--items-dir", required=True)
    ap.add_argument("--year", required=True)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    mine = [p for p in PATCHES if p["year"] == a.year]
    if not mine:
        print("  no verified patches for %s" % a.year)
        return 0
    done = collections.Counter(); miss = []
    for f in sorted(glob.glob(os.path.join(a.items_dir, "*__items.csv"))):
        rows = list(csv.DictReader(open(f, encoding="utf-8")))
        touched = False
        for p in mine:
            for r in rows:
                if r["item"] != p["item"]:
                    continue
                if p["letter"] is not None and (r.get("resp_raw") or "").strip() != p["letter"]:
                    continue
                v = r.get(p["column"]) or ""
                if not v:
                    continue
                n = v.count(p["old"])
                if n == 0:
                    continue
                if n != 1:
                    miss.append((p["item"], p["column"], "%d matches, need 1" % n))
                    continue
                r[p["column"]] = v.replace(p["old"], p["new"])
                done[(p["item"], p["column"])] += 1
                touched = True
        if touched and a.apply:
            with open(f, "w", newline="", encoding="utf-8") as fh:
                w = csv.DictWriter(fh, SCHEMA); w.writeheader()
                for r in rows:
                    w.writerow({k: r.get(k, "") for k in SCHEMA})
    # an entry that matched nothing is reported: the anchor has gone stale,
    # which usually means an earlier pass changed the text under it.
    hit = {k[0] for k in done}
    stale = [p["item"] for p in mine if p["item"] not in hit]
    print("  %s %d cell-edit(s) over %d item(s)"
          % ("applied" if a.apply else "WOULD apply", sum(done.values()), len(hit)))
    for it, col, why in miss:
        print("     NOT applied: %s [%s] -- %s" % (it, col, why))
    if stale:
        print("     anchor matched nothing (stale?): %s" % sorted(set(stale)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
