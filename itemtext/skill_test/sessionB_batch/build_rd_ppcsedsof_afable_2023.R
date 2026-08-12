library(dplyr)

table_name <- "rd_ppcsedsof_afable_2023"

items <- sprintf("P1SD1_%02d", 1:11)

# Short item labels literally quoted from Afable, Cruz & Saito (2023), PLOS ONE
# 18(6):e0286508, Figure 3 note: "1 -poor appetite; 2 -feeling depressed;
# 3 -feeling that everything was an effort; 4 -restless sleep; 5 -feeling happy;
# 6 -feeling lonely; 7 -feeling that people are unfriendly; 8 -enjoyed life;
# 9 -feeling sad; 10 -feeling that people dislike you; 11 -could not get going"
item_text <- c(
  "Poor appetite",
  "Feeling depressed",
  "Feeling that everything was an effort",
  "Restless sleep",
  "Feeling happy",
  "Feeling lonely",
  "Feeling that people are unfriendly",
  "Enjoyed life",
  "Feeling sad",
  "Feeling that people dislike you",
  "Could not get going"
)

instrument_name <- "CES-D Scale (11-item, 3-response version)"
instructions_text <- "Respondents were asked to rate how often they felt these symptoms in the past seven days based on a three-response scale."

section_id <- paste0(table_name, "_cesd")

# resp/option_text: paper reports scoring as 0-Rarely/Not at all, 1-Sometimes,
# 2-Often, but live ground-truth resp values are 1/2/3 (not 0/1/2). Mapped here
# assuming a uniform +1 shift (raw survey coding 1-3, paper's analysis text
# describes the recoded-to-0 scoring) -- this mapping is NOT independently
# confirmed by a codebook and is logged as an assumption.
resp_map <- data.frame(
  resp = c(1L, 2L, 3L),
  option_text = c("Rarely/Not at all", "Sometimes", "Often"),
  stringsAsFactors = FALSE
)

items_tab <- data.frame(
  table = table_name,
  section_id = section_id,
  item = items,
  item_text = item_text,
  correct_response = "",
  stringsAsFactors = FALSE
)

sections_tab <- data.frame(
  table = table_name,
  section_id = section_id,
  section_prompt = "",
  stringsAsFactors = FALSE
)

instrument_tab <- data.frame(
  table = table_name,
  instrument = instrument_name,
  instructions = instructions_text,
  stringsAsFactors = FALSE
)

responses_tab <- merge(
  data.frame(table = table_name, section_id = section_id, item = items, stringsAsFactors = FALSE),
  resp_map
)
responses_tab <- responses_tab[, c("table", "section_id", "item", "option_text", "resp")]

merged <- merge(items_tab, sections_tab, by = c("table", "section_id"), all.x = TRUE)
merged <- merge(merged, instrument_tab, by = "table", all.x = TRUE)
merged <- merge(merged, responses_tab, by = c("table", "section_id", "item"), all.x = TRUE)

merged <- merged[, c("table", "section_id", "item", "instrument", "instructions",
                      "section_prompt", "item_text", "correct_response",
                      "option_text", "resp")]

# order: by item order then resp order
merged$item <- factor(merged$item, levels = items)
merged <- merged[order(merged$item, merged$resp), ]
merged$item <- as.character(merged$item)
rownames(merged) <- NULL

str(merged)
print(merged)

saveRDS(merged, file = "/home/ben/Dropbox/projects/irw/src/itemtext/skill_test/sessionB_batch/candidate_rd_ppcsedsof_afable_2023.rds")

# Validation against ground truth
gt <- readRDS("/home/ben/Dropbox/projects/irw/src/itemtext/skill_test/sessionB_batch/.gt_rd_ppcsedsof_afable_2023.rds")
cat("\n--- VALIDATION ---\n")
cat("item match:", identical(sort(unique(merged$item)), sort(unique(gt$item))), "\n")
cat("resp match:", identical(sort(unique(merged$resp)), sort(unique(as.integer(gt$resp)))), "\n")
