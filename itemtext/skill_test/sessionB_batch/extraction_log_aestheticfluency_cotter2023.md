# Extraction log: aestheticfluency_cotter2023

## Source used
Started from the dictionary row's OSF URL, `https://osf.io/d9ujk/`, and the DOI
`10.1371/journal.pone.0281547` (Cotter et al., 2023, PLOS ONE, "Updating the Aesthetic
Fluency Scale: Revised long and short forms for research in the psychology of the arts").

Three sources were fetched and cross-checked, all cached under
`.cache/aestheticfluency_cotter2023/`:

1. `plos_article.html` — full open-access PLOS ONE HTML article (curl'd directly, not
   paywalled). Gave the Methods narrative (item-pool development, response-scale
   rationale, item difficulty/discrimination prose) and the exact 0/1/2 response-label
   wording.
2. `Revised_Aesthetic_Fluency_36_Items_Sortable_Table_OSF.html` — an R `DT` htmlwidget
   file linked directly from the OSF node's file list (`osf.io/download/me238/`),
   containing "Table 1: Revised Aesthetic Fluency Scale: Items and statistics" as an
   embedded JSON payload (`<script type="application/json">`), not just a static table —
   had to parse the widget's `x.data` array. This gave item numbers 1-36 in table order,
   each paired with a lowercase slug (e.g. `richter`, `sargent`, ... `lithography`) and
   IRT item statistics (alpha, beta/difficulty, thresholds, fit).
3. `Revised_Aesthetic_Fluency_Scale.docx` — the actual "Scale Versions for Research Use"
   instrument document from the OSF node's subfolder (`osf.io/download/7xsfk/`), a real
   .docx (unzipped and parsed as OOXML, not scraped as rendered text). This gave the
   literal instructions text, the literal 3-point response-option wording, and the full
   human-readable names of all 36 items in one fixed list order.

## Structure discovered
- 36 items, verified against source (2): "As intended, the items showed a wide range of
  difficulty, from -1.82 (Vincent van Gogh, the easiest item) to 2.20 (Gerhard Richter,
  the hardest)." — item 1 in the OSF stats table (`richter`) has beta = 2.20 and item 11
  (`vangogh`) has beta = -1.82, exactly matching this sentence. That cross-check confirms
  the stats table's row order is the canonical item-number order (1-36), not an arbitrary
  sort.
- Source (3), the actual instrument docx, lists the 36 items in the identical order and
  identical content as source (2)'s slugs (Richter, Sargent, Botticelli, Basquiat, Kahlo,
  Monet, O'Keeffe, Pollock, Mondrian, Dalí, van Gogh, Duchamp, Braque, Delacroix, Greco,
  Ernst, Gauguin, Klimt, Magritte, Modigliani, Munch, Pissarro, Renoir, Rothko, Seurat,
  Fauvism, Impressionism, Abstract Expressionism, Cubism, Dada, Pointillism, Pop art,
  Surrealism, Bauhaus, Gouache, Lithography) — two independently-sourced files agree on
  both content and order, which is the basis for the item-number mapping below.
- Response scale (0/1/2), from both (1) and (3), verbatim:
  - 0 = "I don't really know anything about this artist or term"
  - 1 = "I'm familiar with this artist or term"
  - 2 = "I know a lot about this artist or term"
- Instructions, from (3) (docx paragraphs, reassembled from separate runs/paragraphs):
  "ART KNOWLEDGE SURVEY. We're interested in people's knowledge of the arts—how much they
  know about different artists, ideas, concepts, and techniques in the world of art. The
  following page has a list of 36 artists and terms in art history. For each one, please
  rate how much you know about it. There are no right or wrong answers, and we appreciate
  your time and attention. Please rate how much you know about the following artists and
  terms." (Concatenation of adjacent paragraphs/headings in the docx; no wording added.)

## Bare-integer validation check (has_bare_integer_items = TRUE)
Ground-truth `item` values are `"1"`-`"36"` with no semantic labels, so item identity had
to be reconstructed by position. Check performed (per SKILL.md's bare-integer guidance,
not just resp-range plausibility): matched item 1 and item 11's IRT difficulty (beta)
values in the OSF sortable-table widget against the specific numeric values quoted in the
paper's own prose ("-1.82 (Vincent van Gogh, the easiest item) to 2.20 (Gerhard Richter,
the hardest)"). Item 1 = beta 2.20 = Richter = "the hardest" ✓; item 11 = beta -1.82 =
van Gogh = "the easiest" ✓. This ties the table's row order to a specific, paper-verified
item, not just a plausible resp range — 35 of the 36 items in this instrument would have
"passed" a naive 0/1/2 resp-range check regardless of which slug was assigned to which
number, so this beta-value/prose cross-check is what actually pins the order down.
Additionally, the independently-sourced instrument docx lists the same 36 names in the
same order as the stats-table slugs, a second, independent confirmation of the mapping.
Result: mapping treated as confirmed, not merely plausible.

## Structure of output
Single section (`aestheticfluency_cotter2023_1`, blank `section_prompt`) since the
instrument has no testlet/passage grouping — all 36 items share one `instructions` block.
`item_text` is the literal artist/term name from the docx (e.g. "Gerhard Richter", "Pop
art", "Abstract Expressionism"). `correct_response` is blank throughout — this is a
subjective self-report knowledge scale with no scoring key. `resp`/`option_text` map
0/1/2 to the three literal response-option strings, identical for every item (a single
shared Likert-style scale, not per-item options).

## Ambiguities
- The docx instrument document contains a researcher note: "(Note for researchers: the
  items should be displayed in a random order.)" — i.e., in actual survey administration
  the 36 items were presented to participants in a randomized order, not the fixed
  Richter→Lithography order shown in the source documents. This doesn't affect the
  extraction: the `item` field in the live IRW data is a fixed numeric identifier (1-36)
  that reflects the underlying data column/variable order, not display order, and that
  fixed order is exactly what's reconstructed here and cross-validated via the IRT beta
  values above.
- "Pop art" in the docx (lowercase "art") maps to slug `popart` in the stats table (item
  32) — capitalization judgment call; transcribed as "Pop art" per the literal docx
  text.

## Items not extracted
None — all 36 ground-truth items were matched and extracted; validated exact item/resp
set match against `.gt_aestheticfluency_cotter2023.rds` (36/36 items, {0,1,2} resp set,
both `identical()`-equal).

## OCR / image-based extraction
Not needed. All text was extracted programmatically from real text-bearing files: the
PLOS ONE article's HTML (server-rendered text, not an image), the OSF `DT` htmlwidget's
embedded JSON payload (parsed directly from the `<script type="application/json">` block,
not rendered/screenshotted), and the instrument `.docx` (unzipped as OOXML and its
`document.xml` parsed as XML/text). No PDF-image or scanned-page reading was required at
any point.

## Derived vs. directly-read values
None — all values (`instructions`, `item_text` for all 36 items, `option_text` for all
3 response levels) were read directly from source text, not derived, paraphrased, or
computed. The only "construction" performed was (a) concatenating adjacent
paragraphs/headings in the docx into one `instructions` string (no wording changed or
added) and (b) assigning the docx's item list to `item` = "1".."36" by position, which is
the bare-integer reconstruction documented above, not a value derivation.

## Source type used
Paper appendix / companion OSF repository materials: specifically the PLOS ONE article's
open-access full-text HTML plus two files from the paper's linked OSF project — an
R-generated interactive statistics table (`Revised_Aesthetic_Fluency_36_Items_Sortable_
Table_OSF.html`) and the actual "Scale Versions for Research Use" instrument document
(`Revised_Aesthetic_Fluency_Scale.docx`). Not a PDF manual, not a website codebook, not
raw-data-file column headers.
