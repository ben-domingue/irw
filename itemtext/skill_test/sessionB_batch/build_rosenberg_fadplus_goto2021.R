## Build candidate_rosenberg_fadplus_goto2021.rds
## Table's live item/resp ground truth: Rosenberg_1..Rosenberg_10, resp 1-4.
## Confirmed via Goto (2021) Frontiers in Psychology paper text + OSF raw data/analysis
## script (https://osf.io/2xbe5/) that despite the table name referencing "FAD-Plus",
## the live items are the 10-item Rosenberg Self-Esteem Scale (RSES), Japanese
## translation by Mimura & Griffiths (2007), administered as a convergent-validity
## measure alongside the two FAD-Plus translations in this study.

table_name <- "Rosenberg_fadplus_goto2021"  # exact-case value for `table` column

items <- paste0("Rosenberg_", 1:10)
section_id <- "rosenberg_fadplus_goto2021_1"

instrument_name <- "Rosenberg Self-Esteem Scale (RSES; Japanese translation by Mimura & Griffiths, 2007)"

## Literal sentence from Goto (2021) describing the instrument/response format
## (paper.txt lines ~198-210 of the cached PDF text) -- no participant-facing
## instructions are quoted verbatim anywhere in the paper, so this Methods-section
## description is used in the `instructions` field instead (paper does not give a
## separate literal instruction stem).
instructions_txt <- paste0(
  "This scale consisted of 10 items in a four-point Likert format with anchors of ",
  "1 = 強くそう思わない (“Strongly disagree”) to ",
  "4 = 強くそう思う (“Strongly agree”)."
)

## Standard published RSES item wording (Rosenberg, 1965; public-domain, canonical
## English original), in the instrument's fixed/conventional 10-item presentation
## order. Order (and reverse-scoring direction) was cross-checked -- not just assumed --
## against the OSF-hosted analysis script (FAD_compare_analysis.Rmd, lines 85-88), which
## reverse-scores exactly items 2, 5, 6, 8, and 9 (via `5 - Rosenberg_k`), which is the
## standard RSES reverse-keyed item set/order. The literal Mimura & Griffiths (2007)
## Japanese translation wording itself is NOT reproduced in the Goto (2021) paper, its
## OSF materials, or any open-access source located; Journal of Psychosomatic Research
## (Mimura & Griffiths 2007) is paywalled and was not accessible. English item text below
## is the canonical original the Japanese version was translated from, used for
## corroboration/documentation, not claimed to be the literal Japanese text respondents saw.
item_text_en <- c(
  "On the whole, I am satisfied with myself.",
  "At times I think I am no good at all.",
  "I feel that I have a number of good qualities.",
  "I am able to do things as well as most other people.",
  "I feel I do not have much to be proud of.",
  "I certainly feel useless at times.",
  "I feel that I'm a person of worth, at least on an equal plane with others.",
  "I wish I could have more respect for myself.",
  "All in all, I am inclined to feel that I am a failure.",
  "I take a positive attitude toward myself."
)

reverse_scored <- c(2, 5, 6, 8, 9)

items_df <- data.frame(
  table = table_name,
  section_id = section_id,
  item = items,
  item_text = item_text_en,
  correct_response = "",
  stringsAsFactors = FALSE
)

sections_df <- data.frame(
  table = table_name,
  section_id = section_id,
  section_prompt = "",
  stringsAsFactors = FALSE
)

instrument_df <- data.frame(
  table = table_name,
  instrument = instrument_name,
  instructions = instructions_txt,
  stringsAsFactors = FALSE
)

## resp/option_text: only the two verbal anchors the paper actually discloses
## (1 = Strongly disagree, 4 = Strongly agree) are populated; 2 and 3 are left blank
## since the paper does not give literal labels for the interior scale points
## (same convention as firstborn_personality's unlabeled midpoints).
resp_levels <- 1:4
option_labels <- c("Strongly disagree", "", "", "Strongly agree")

responses_list <- list()
for (it in items) {
  responses_list[[it]] <- data.frame(
    table = table_name,
    section_id = section_id,
    item = it,
    option_text = option_labels,
    resp = resp_levels,
    stringsAsFactors = FALSE
  )
}
responses_df <- do.call(rbind, responses_list)

merged <- merge(items_df, sections_df, by = c("table", "section_id"), all.x = TRUE)
merged <- merge(merged, instrument_df, by = "table", all.x = TRUE)
merged <- merge(merged, responses_df, by = c("table", "section_id", "item"), all.x = TRUE)

## Reorder columns to match the model schema exactly
final_cols <- c("table", "section_id", "item", "instrument", "instructions",
                 "section_prompt", "item_text", "correct_response", "option_text", "resp")
merged <- merged[, final_cols]

## Sort by item (Rosenberg_1..Rosenberg_10 in natural numeric order) then resp
item_order <- match(merged$item, items)
merged <- merged[order(item_order, merged$resp), ]
rownames(merged) <- NULL

saveRDS(merged, file = "candidate_rosenberg_fadplus_goto2021.rds")
cat("Rows:", nrow(merged), "\n")
cat("Unique items:", length(unique(merged$item)), "\n")
cat("Unique resp:", paste(sort(unique(merged$resp)), collapse=","), "\n")
str(merged)
