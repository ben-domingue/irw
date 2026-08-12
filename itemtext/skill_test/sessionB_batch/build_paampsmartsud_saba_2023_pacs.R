library(dplyr)

table_id <- "paampsmartsud_saba_2023_pacs"
items <- c("PACS_1_POST","PACS_2_POST","PACS_3_POST","PACS_4_POST","PACS_5_POST")
resp_vals <- 0:6

instrument_name <- "Penn Alcohol Craving Scale (PACS), wording revised to also capture cravings for other drugs"

instructions_text <- "Rate each item over the past 30 days on a 7-point Likert scale from 0 (none/never) to 6 (unable to resist/all the time)."

section_id_val <- paste0(table_id, "_pacs")

item_text_map <- c(
  PACS_1_POST = NA_character_,
  PACS_2_POST = "At its most severe point how strong was your craving?",
  PACS_3_POST = "How much time have you spent thinking about doing drugs or drinking?",
  PACS_4_POST = NA_character_,
  PACS_5_POST = NA_character_
)

option_text_map <- c(
  `0` = "none/never",
  `1` = NA_character_,
  `2` = NA_character_,
  `3` = NA_character_,
  `4` = NA_character_,
  `5` = NA_character_,
  `6` = "unable to resist/all the time"
)

rows <- list()
for (it in items) {
  for (r in resp_vals) {
    rows[[length(rows) + 1]] <- data.frame(
      table = table_id,
      section_id = section_id_val,
      item = it,
      instrument = instrument_name,
      instructions = instructions_text,
      section_prompt = "",
      item_text = ifelse(is.na(item_text_map[[it]]), NA_character_, item_text_map[[it]]),
      correct_response = "",
      option_text = ifelse(is.na(option_text_map[[as.character(r)]]), "", option_text_map[[as.character(r)]]),
      resp = r,
      stringsAsFactors = FALSE
    )
  }
}

d <- do.call(rbind, rows)
d <- d[order(match(d$item, items), d$resp), ]
rownames(d) <- NULL

str(d)
print(d)

saveRDS(d, file = "candidate_paampsmartsud_saba_2023_pacs.rds")

# validation against ground truth
gt <- readRDS(".gt_paampsmartsud_saba_2023_pacs.rds")
cat("\n--- validation ---\n")
cat("item match:", identical(sort(unique(d$item)), sort(unique(gt$item))), "\n")
cat("resp match:", identical(sort(unique(d$resp)), sort(unique(gt$resp))), "\n")
