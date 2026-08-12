library(dplyr)

table_name <- "mhscdc_fried_2020_dass"
instrument_name <- "Depression Anxiety Stress Scales - 21 Item (DASS-21)"

# Literal item text transcribed from OSF materials Measures_Baseline.pdf
# (Baseline assessment items 17(Q#25)-37(Q#45), "Questionnaire 1" block),
# cross-checked against Codebook_Baseline.xlsx (Label/Scale = "DASS", Item Q1-Q21)
# and Codebook_Post.xlsx (Item Q38-Q58, same 21 items same order, "Questionnaire 1"
# heading at item 38). item_N (N=1..21) = column PreN (pre) / Post(N+37) (post) per
# data/mhscdc_fried_2020.r's process_dass_data2() calls:
#   dass_pre  <- process_dass_data2(bt_df, "Pre", 1, 21, "pre", 0)
#   dass_post <- process_dass_data2(bt_df, "Post", 38, 58, "post", 37)
# confirming item_1..item_21 map 1:1, in order, onto Q1..Q21 of each codebook block.
item_text <- c(
  "In the past week, I found it hard to wind down.",
  "In the past week, I was aware of dryness of my mouth",
  "In the past week, I couldn't seem to experience any positive feeling at all",
  "In the past week, I experienced breathing difficulty (eg, excessively rapid breathing, breathlessness in the absence of physical exertion).",
  "In the past week, I found it difficult to work up the initiative to do things.",
  "In the past week, I tended to over-react to situations.",
  "In the past week, I experienced trembling (eg, in the hands).",
  "In the past week, I felt that I was using a lot of nervous energy.",
  "In the past week, I was worried about situations in which I might panic and make a fool of myself",
  "In the past week, I felt that I had nothing to look forward to",
  "In the past week, I found myself getting agitated",
  "In the past week, I found it difficult to relax",
  "In the past week, I felt down-hearted and blue",
  "In the past week, I was intolerant of anything that kept me from getting on with what I was doing",
  "In the past week, I felt I was close to panic",
  "In the past week, I was unable to become enthusiastic about anything",
  "In the past week, I felt I wasn't worth much as a person",
  "In the past week, I felt that I was rather touchy",
  "In the past week, I was aware of the action of my heart in the absence of physical exertion (eg, sense of heart rate increase, heart missing a beat)",
  "In the past week, I felt scared without any good reason",
  "In the past week, I felt that life was meaningless"
)
stopifnot(length(item_text) == 21)

items <- paste0("item_", 1:21)

option_text <- c(
  "Did not apply to me at all",
  "Applied to me to some degree, or some of the time",
  "Applied to me to a considerable degree, or a good part of time",
  "Applied to me very much, or most of the time"
)
resp_vals <- 1:4

# --- instrument tab ---
instrument_tab <- data.frame(
  table = table_name,
  instrument = instrument_name,
  # No standalone whole-instrument instructions text was found in the source
  # materials (Measures_Baseline.pdf / Measures_Post.pdf): item 16/38 is only a
  # bare "Questionnaire 1" section heading with no participant-facing framing
  # text captured before the first item. Each item stem repeats "In the past
  # week, I ..." itself. Left blank rather than fabricated; see extraction log.
  instructions = "",
  stringsAsFactors = FALSE
)

# --- sections tab: one section_id per item (interleaved D/A/S subscale items,
# no shared passage/testlet grouping in the source presentation) ---
sections_tab <- data.frame(
  table = table_name,
  section_id = paste0(table_name, "_", 1:21),
  section_prompt = "",
  stringsAsFactors = FALSE
)

# --- items tab ---
items_tab <- data.frame(
  table = table_name,
  section_id = paste0(table_name, "_", 1:21),
  item = items,
  item_text = item_text,
  correct_response = "",
  stringsAsFactors = FALSE
)

# --- responses tab ---
responses_tab <- do.call(rbind, lapply(1:21, function(i) {
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

# order rows: item_1..item_21 (numeric), each with resp 1..4
item_num <- as.integer(sub("item_", "", merged$item))
merged <- merged[order(item_num, merged$resp), ]
rownames(merged) <- NULL

str(merged)
print(head(merged, 8))

saveRDS(merged, file = "candidate_mhscdc_fried_2020_dass.rds")
cat("\nWrote candidate_mhscdc_fried_2020_dass.rds with", nrow(merged), "rows\n")
