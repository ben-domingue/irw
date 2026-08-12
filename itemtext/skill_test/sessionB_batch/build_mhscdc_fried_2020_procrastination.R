library(dplyr)

table_name <- "mhscdc_fried_2020_procrastination"
instrument_name <- "Procrastination Scale"

# Literal item text transcribed from OSF materials Measures_Baseline.pdf
# (Baseline assessment items 171(Q#223)-175(Q#227), "Questionnaire 15" block),
# cross-checked against Codebook_Baseline.xlsx (cleandata_pre Q141-Q145,
# Label/Scale = "Procrastination" on the first row of the block) and
# Codebook_Post.xlsx (clean_post Q13-Q17, same 5 items, same order,
# "Specifc questions 1" label). item_N (N=1..5) = column PreN (pre) /
# Post(N+12) (post) per data/mhscdc_fried_2020.r's process_dass_data2() calls:
#   dass_pre  <- process_dass_data2(bt_df, "Pre",  141, 145, "pre", 140)
#   dass_post <- process_dass_data2(bt_df, "Post", 13, 17, "post", 12)
# i.e. item = paste0("item_", as.integer(str_extract(item_rawname, "\\d+")) - item_offset)
# Pre141..Pre145 -> item_1..item_5 (offset 140, 141-140=1 ... 145-140=5).
# Post13..Post17 -> item_1..item_5 (offset 12, 13-12=1 ... 17-12=5).
# Confirmed against Codebook_Baseline.xlsx cleandata_pre column: Q141-Q145 rows
# map 1:1, in order, to the 5 procrastination items below; Codebook_Post.xlsx
# clean_post column: Q13-Q17 rows give the identical 5 item texts in the same
# order, corroborating the mapping across both waves.
item_text <- c(
  "I usually buy even essential item at the last minute.",
  "In preparing for some deadline, I often waste time by doing other things.",
  "I usually have to rush to complete a task on time.",
  "I generally delay before starting on work I have to do.",
  "I do not do assignments until just before they are to be handed in."
)
stopifnot(length(item_text) == 5)

items <- paste0("item_", 1:5)

option_text <- c(
  "Extremely uncharacteristic",
  "Moderately uncharacteristic",
  "Neutral",
  "Moderately characteristic",
  "Extremely characteristic"
)
resp_vals <- 1:5

# --- instrument tab ---
instrument_tab <- data.frame(
  table = table_name,
  instrument = instrument_name,
  # No standalone whole-instrument instructions text was found in the source
  # materials (Measures_Baseline.pdf / Measures_Post.pdf): item 170/Q#222 is
  # only a bare "Questionnaire 15" section heading with no participant-facing
  # framing text captured before the first item (same pattern as the sibling
  # _dass table's "Questionnaire 1" heading). Left blank rather than
  # fabricated; see extraction log.
  instructions = "",
  stringsAsFactors = FALSE
)

# --- sections tab: one section_id per item (no shared passage/testlet
# grouping in the source presentation) ---
sections_tab <- data.frame(
  table = table_name,
  section_id = paste0(table_name, "_", 1:5),
  section_prompt = "",
  stringsAsFactors = FALSE
)

# --- items tab ---
items_tab <- data.frame(
  table = table_name,
  section_id = paste0(table_name, "_", 1:5),
  item = items,
  item_text = item_text,
  correct_response = "",
  stringsAsFactors = FALSE
)

# --- responses tab ---
responses_tab <- do.call(rbind, lapply(1:5, function(i) {
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

# order rows: item_1..item_5 (numeric), each with resp 1..5
item_num <- as.integer(sub("item_", "", merged$item))
merged <- merged[order(item_num, merged$resp), ]
rownames(merged) <- NULL

str(merged)
print(head(merged, 8))

saveRDS(merged, file = "candidate_mhscdc_fried_2020_procrastination.rds")
cat("\nWrote candidate_mhscdc_fried_2020_procrastination.rds with", nrow(merged), "rows\n")
