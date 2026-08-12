library(dplyr)

table_name <- "mhscdc_fried_2020_ps"
instrument_name <- "Perceived Stress Scale (PSS-10)"

# Literal item text transcribed from OSF materials Measures_Baseline.pdf
# (Baseline assessment items 90(Q#206)-99(Q#216), the block headed by
# item 89(Q#151) "Questionnaire 7"), cross-checked against
# data/mhscdc_fried_2020.r's raw-column mapping:
#   dass_df <- process_dass_data(bt_df, "Pre", 68, 77, "mhscdc_fried_2020_ps")
# process_dass_data() (the NON-"2" variant, used for anger/se/mindfulness/ps/
# motivation/smartphone) keeps the raw "Pre<N>" column name AS the item value
# (no item_N renumbering/offset) -- confirmed directly from
# .gt_mhscdc_fried_2020_ps.rds: unique(item) == "Pre68".."Pre77" exactly.
# So item = raw column name = "Pre68".."Pre77", one-to-one, in ascending
# numeric order.
#
# The doc's own running item-index (89, 90, ..., 99) is a document/export
# ordinal, NOT the same numbering as "PreN" (there are non-Pre columns, e.g.
# demographics/attention checks, interspersed in the full export). The
# Pre68-77 <-> doc-index 90-99 correspondence was confirmed by (a) exact
# 10-item count match, (b) exact content match to the canonical published
# PSS-10 (Cohen, Kamarck & Mermelstein, 1983) item wording and order, and
# (c) positional bracketing: doc "Questionnaire 5" (index 65) = Self-Efficacy
# block = Pre46-55 (10 items, per script), "Questionnaire 6" (index 76) =
# Mindfulness block = Pre56-67 (12 items, per script), so the block
# immediately in between mindfulness and "Questionnaire 8" (index 100,
# confirmed elsewhere to be Tiredness = a separate table) is "Questionnaire 7"
# = doc index 90-99 = PS = Pre68-77 (10 items, per script). All three
# cross-checks agree.
item_text <- c(
  "In the last month, how often have you been upset because of something that happened unexpectedly?",
  "In the last month, how often have you felt that you were unable to control the important things in your life?",
  "In the last month, how often have you felt nervous and \"stressed\"?",
  "In the last month, how often have you felt confident about your ability to handle your personal problems?",
  "In the last month, how often have you felt that things were going your way?",
  "In the last month, how often have you found that you could not cope with all the things that you had to do?",
  "In the last month, how often have you been able to control irritations in your life?",
  "In the last month, how often have you felt that you were on top of things?",
  "In the last month, how often have you been angered because of things that were outside of your control?",
  "In the last month, how often have you felt difficulties were piling up so high that you could not overcome them?"
)
stopifnot(length(item_text) == 10)

items <- paste0("Pre", 68:77)

# Response options as printed in Measures_Baseline.pdf: each option's own
# label text embeds a "0"-"4" numeral (the PSS-10's canonical 0-4 scoring
# convention), but the actual selectable option POSITION (and the value
# recorded in the raw/clean data, confirmed against ground truth resp 1-5)
# is 1-5, i.e. a +1 shift of the canonical PSS-10 0-4 scale onto this
# platform's 1-5 radio-button coding -- same pattern noted for the sibling
# florida_twins_hwk table. option_text below is transcribed verbatim
# including the embedded "0"-"4" numerals exactly as shown to participants.
option_text <- c(
  "0 Never",
  "1 Almost never",
  "2 Sometimes",
  "3 Fairly often",
  "4 Very often"
)
resp_vals <- 1:5

# --- instrument tab ---
instrument_tab <- data.frame(
  table = table_name,
  instrument = instrument_name,
  # No standalone whole-instrument instructions/framing text was found in
  # Measures_Baseline.pdf before the first PS item: item 89(Q#151) is only a
  # bare "Questionnaire 7" section-divider label, same pattern as the sibling
  # _dass/_anger/_procrastination tables' bare "Questionnaire N" headers. Each
  # item stem instead repeats its own time-frame reminder ("In the last
  # month, how often have you ..."). Left blank rather than fabricated (the
  # well-known published PSS-10 instructions, e.g. "The questions in this
  # scale ask you about your feelings and thoughts during the last month...",
  # are not present anywhere in this dataset's source materials).
  instructions = "",
  stringsAsFactors = FALSE
)

# --- sections tab: one section_id per item (no shared passage/testlet
# grouping in the source presentation) ---
sections_tab <- data.frame(
  table = table_name,
  section_id = paste0(table_name, "_", 1:10),
  section_prompt = "",
  stringsAsFactors = FALSE
)

# --- items tab ---
items_tab <- data.frame(
  table = table_name,
  section_id = paste0(table_name, "_", 1:10),
  item = items,
  item_text = item_text,
  correct_response = "",
  stringsAsFactors = FALSE
)

# --- responses tab ---
responses_tab <- do.call(rbind, lapply(1:10, function(i) {
  data.frame(
    table = table_name,
    section_id = paste0(table_name, "_", i),
    item = items[i],
    option_text = option_text,
    resp = resp_vals,
    stringsAsFactors = FALSE
  )
}))

# --- merge per SKILL.md Step 4 ---
merged <- merge(items_tab, sections_tab, by = c("table", "section_id"), all.x = TRUE)
merged <- merge(merged, instrument_tab, by = "table", all.x = TRUE)
merged <- merge(merged, responses_tab, by = c("table", "section_id", "item"), all.x = TRUE)

merged <- merged[, c("table", "section_id", "item", "instrument", "instructions",
                      "section_prompt", "item_text", "correct_response",
                      "option_text", "resp")]

# order rows: Pre68..Pre77 (numeric), each with resp 1..5
item_num <- as.integer(sub("Pre", "", merged$item))
merged <- merged[order(item_num, merged$resp), ]
rownames(merged) <- NULL

str(merged)
print(head(merged, 10))

saveRDS(merged, file = "candidate_mhscdc_fried_2020_ps.rds")
cat("\nWrote candidate_mhscdc_fried_2020_ps.rds with", nrow(merged), "rows\n")
