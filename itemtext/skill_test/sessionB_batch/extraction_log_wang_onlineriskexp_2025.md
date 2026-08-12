# Extraction log: wang_onlineriskexp_2025

## Source type used
Two sources, both cached under `.cache/wang_onlineriskexp_2025/`:

1. **The dictionary URL itself**, `https://doi.org/10.1371/journal.pone.0319700.s001`, resolved to
   an `.xlsx` file (`s001.xlsx`, saved with a `.pdf` extension by curl's default naming, then
   renamed) — this is PLOS's **S1 Data file**, i.e. the raw minimal response-level dataset
   (columns `XB`, `FXXL1..FXJC5`, `Na1..An7`, `RJRJ1..RJXF6`, plus computed subscale-mean
   columns), the same content as `irw::irw_fetch`, **not** a copy of the instrument/questionnaire.
   Confirmed by inspecting `Sheet1` headers directly with `openpyxl` — no item-wording text
   anywhere in the file, only item codes and numeric responses.
2. **The main PLOS ONE article** (fully open access), fetched as `main_paper.html`
   (`https://doi.org/10.1371/journal.pone.0319700`, also cross-checked against the PMC mirror,
   PMC11922264). Its Measures section 3.2.1 (Online risk exposure scale) is the only place any
   item-level text is quoted.
3. Also fetched, for the *original English precursor scale* (not the actual instrument
   administered in this Chinese-language study — see below): Wisniewski, Jia, Wang, Zheng, Xu,
   Rosson et al. (2015), *Resilience Mitigates the Negative Effects of Adolescent Internet
   Addiction and Online Risk Exposure*, CHI 2015 (cached as `wisniewski2015.pdf`, from
   `https://stirlab.org/wp-content/uploads/2018/06/2015_Wisniewski_ResilienceMitigatestheNegative.pdf`,
   text-extracted with `pdftotext -layout`). Its Appendix A / Table 2 gives full English item
   wording for a 16-item scale (3+4+4+5 items) that is structurally identical to the one used
   here.

## OCR / image-based extraction
None. All text was read from native HTML (PLOS article), a native `.xlsx` spreadsheet (S1 Data,
read via `openpyxl`, not an image scan), and a text-layer PDF (`wisniewski2015.pdf`, extracted
with `pdftotext -layout`, not OCR).

## has_bare_integer_items is FALSE — confirmed
Ground truth `item` values are semantic codes (`FXJC1..FXJC5`, `FXQF1..FXQF4`, `FXXL1..FXXL3`,
`FXXY1..FXXY4`), not bare integers, matching the dictionary row's flag. No positional
reconstruction from integer codes was needed for the item *set* — only within-subscale item
*order* (which physical item is `FXXL1` vs `FXXL2` vs `FXXL3`) remains unconfirmed (see below).

## What FXJC/FXQF/FXXL/FXXY mean (confirmed, not guessed)
The paper's Measures §3.2.1 states: "The online risk exposure scale, initially developed by
Wisniewski et al [6] and subsequently adapted for Chinese contexts by Zhang et al. [5], consists
of 16 items distributed across four sub-scales: information breaches (3 items, such as, 'I shared
my personal information or a photo of myself that I later regretted sharing.'), cyberbullying (4
items), online sexual solicitations (4 items), and exposure to explicit content (5 items)."
Cross-checked against the raw S1 spreadsheet column layout, which groups `FXXL1-3, FXQF1-4,
FXXY1-4, FXJC1-5` immediately followed by four subscale-mean columns in the same order:
`Information breaches-M, Cyberbullying-M, Online sexual solicitations-M, Exposure to explicit
content-M`. The two orderings and item counts agree exactly, giving:

| Prefix | N items | Subscale (paper's own English label) |
|---|---|---|
| FXXL | 3 | Information breaches |
| FXQF | 4 | Cyberbullying |
| FXXY | 4 | Online sexual solicitations |
| FXJC | 5 | Exposure to explicit content |

(`FX` = 风险 fēngxiǎn "risk"; the prompt's guess about the pinyin-initial pattern for the
subcategories was not separately verified since the paper's own English labels + the column-order
cross-check already establish the mapping with high confidence — no need to reverse-engineer
XL/QF/XY/JC from Chinese pinyin.)

## Derived vs. directly-read values
- **Directly read** from the Wang et al. (2025) paper itself: subscale names, item counts per
  subscale (3/4/4/5, matches ground truth exactly), response scale (5-point Likert, 1 = "none" to
  5 = "a lot"), and one verbatim example item quoted by the paper for the information-breaches
  subscale: "I shared my personal information or a photo of myself that I later regretted
  sharing."
- **Derived/cross-checked**, not directly stated by Wang et al.: the FXXL/FXQF/FXXY/FXJC ↔
  subscale-name correspondence, inferred by matching the S1 spreadsheet's column order to the
  paper's stated subscale order and item counts (both independently confirm the same mapping).

## Items not extracted — item_text left blank for all 16 items
Neither the PLOS article, the PMC mirror, nor the S1 Data file discloses literal wording for more
than one item, and even that one example cannot be confidently tied to a specific item code
(`FXXL1`, `FXXL2`, or `FXXL3`) — the paper gives it only as an illustrative "such as," not as
"item 1." Zhang et al. (2023), the Chinese Journal of Clinical Psychology paper that actually
adapted/translated the scale into the Chinese wording respondents saw, could not be located in
any open-access form (Chinese-language psychometrics journal, not found via web search, no PMC/DOI
resolvable from this paper's reference list).

I found the *English-language precursor scale's* full item wording (Wisniewski et al. 2015,
Appendix A / Table 2 — all 16 items across the same 4 subscales with matching counts), but did
**not** use it to fill `item_text`, for two compounding reasons: (1) the within-subscale item
order is not confirmed (which Wisniewski bullet maps to `FXXL1` vs `FXXL2` vs `FXXL3`, etc. is
unknown), and (2) even if the order were known, this is the pre-adaptation English source, not the
literal Chinese wording actually administered by Zhang et al./Wang et al. — inserting it as
`item_text` would risk being read as a verbatim transcript of the actual instrument when it is at
best an approximate, un-translated proxy. Per the "do not guess/fabricate item text" instruction,
`item_text`, `correct_response`, and per-item `option_text` (except the two Likert endpoints) are
left blank (`""`) for all 16 items rather than assigned with unconfirmed ordering. For reference,
the Wisniewski (2015) English item wording (not inserted into the output) is:

- **Information Breaches** (→ FXXL, 3 items): "Someone else shared my personal information or a
  photo of me that I didn't want him/her to post." / "I shared my personal information or a photo
  of myself that I later regretted sharing." / "I have been the victim of what I felt was an
  improper invasion of privacy or misuse of my information in some other way."
- **Online Harassment/Cyberbullying** (→ FXQF, 4 items): "I was treated in a hurtful or nasty way
  online ('Cyberbullied')." / "Someone made rude or mean comments about me or threatened me in some
  way online." / "Someone tried to spread a mean rumor about me online." / "There are other types
  of negative and unwanted interaction that hurt my feelings, and made me feel embarrassed, or
  unsafe."
- **Sexual Solicitations** (→ FXXY, 4 items): "Someone I know sent me a sexual message
  ('Sexting')." / "Someone I know asked me to send them a sexual message, revealing, or naked photo
  of myself." / "A stranger asked me to meet them offline." / "There are other types of sexually
  suggestive interactions that made me feel even a little uncomfortable."
- **Exposure to Explicit Content** (→ FXJC, 5 items): "I saw online stories, images or videos that
  were pornographic (naked or sexual in nature)." / "I saw online stories, images or videos that
  contained excessive violence." / "I saw online stories, images or videos of illegal or deviant
  (morally questionable) behavior." / "I saw online content that promoted self-harm (such as eating
  disorders, cutting, suicide, etc.)." / "I saw other online content that made me feel uncomfortable
  some way."

Note Wisniewski's original response scale ("1 = Not at all" to "5 = Almost every day", a
frequency scale) also does NOT match Wang et al.'s stated endpoints ("1 = none" to "5 = a lot"),
confirming the Chinese-adapted version used different response anchors than the 2015 English
original — another reason not to treat the 2015 wording as a safe stand-in.

`instructions` (table-wide) and `section_prompt` (per subscale) were populated from the paper's
own text: `instructions` carries the response-scale framing sentence ("Participants rate each item
on a 5-point Likert scale ranging from 1 (none) to 5 (a lot)..."); `section_prompt` carries the
paper's literal subscale label for each `section_id` (e.g. "Information breaches" for FXXL items).

## Validation
`item`/`resp` validated exactly against `irw::irw_fetch("wang_onlineriskexp_2025")`-equivalent
ground truth (`.gt_wang_onlineriskexp_2025.rds`): 16/16 items and all 5 resp values (1-5) match
with no extras and no omissions. `option_text` populated only for resp=1 ("none") and resp=5 ("a
lot"), the two anchors literally stated by the paper; resp 2/3/4 left blank (unlabeled midpoints,
consistent with how this pipeline handles other unlabeled 5-point Likert scales, e.g.
`firstborn_personality`).

## Recommended NOTES for the index sheet
"Instrument identified with high confidence (Online Risk Exposure Scale, Wisniewski et al. 2015,
adapted for Chinese college students by Zhang et al. 2023); FXXL=information breaches(3),
FXQF=cyberbullying(4), FXXY=online sexual solicitations(4), FXJC=exposure to explicit content(5)
confirmed via paper text + S1 spreadsheet column order cross-check. item/resp match ground truth
exactly. item_text left blank for all 16 items -- Zhang et al. (2023, Chin J Clin Psychol) not
open-access/not locatable; only 1 of 16 items has any verbatim wording disclosed (by the target
paper itself, for the information-breaches subscale) and it can't be tied to a specific item code.
English-language precursor scale (Wisniewski et al. 2015) has full item wording but is not the
literal Chinese-adapted text administered, uses a different response scale (frequency vs.
none-to-a lot), and item order within each subscale relative to FXXL1/2/3 etc. is unconfirmed --
not inserted into item_text to avoid mislabeling a translation-adjacent proxy as a literal
transcript. Would need the Zhang et al. (2023) Chinese-language paper's own item table to complete
item_text with confidence."
