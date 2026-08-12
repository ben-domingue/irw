setwd("/home/ben/Dropbox/projects/irw/src/itemtext/skill_test/sessionB_batch")

table <- "eammi_grahe_2018_socmedia"
instrument_name <- "Social Media Use Motives (SocMedia)"

instructions_txt <- ""  # nothing applies unconditionally to every item incl. the derived dummy

real_items <- c(
  "SocMedia_1"  = "Avoid drifting apart from the people I know",
  "SocMedia_2"  = "Find out what my friends are planning to do tonight or this weekend",
  "SocMedia_3"  = "Keep in touch with friends",
  "SocMedia_4"  = "Let friends know what I've been up to",
  "SocMedia_5"  = "Reconnect with people I used to know",
  "SocMedia_6"  = "Find out more about someone I've just met",
  "SocMedia_7"  = "Check out someone I might want to know better",
  "SocMedia_8"  = "Make new friends",
  "SocMedia_9"  = "Get in touch with someone I met at social events",
  "SocMedia_10" = "Get different kinds of information",
  "SocMedia_11" = "Share different kinds of information"
)

section_prompt_txt <- "Think of the social media platform (e.g., Facebook, Instagram, Twitter, etc.) you use most often. How often do you use it for the following reasons?"

options_map <- c(`1` = "Never", `2` = "Rarely", `3` = "Sometimes", `4` = "Often", `5` = "A lot")

rows <- list()

for (it in names(real_items)) {
  for (r in 1:5) {
    rows[[length(rows) + 1]] <- data.frame(
      table = table,
      section_id = paste0(table, "_1"),
      item = it,
      instrument = instrument_name,
      instructions = instructions_txt,
      section_prompt = section_prompt_txt,
      item_text = real_items[[it]],
      correct_response = "",
      option_text = options_map[[as.character(r)]],
      resp = r,
      stringsAsFactors = FALSE
    )
  }
}

# Derived response-bias dummy item -- NOT an administered survey question.
# Codebook: "SocMedia_bias_dummy | response bias coded, 1 = all same answer | n/a | computed | ADDED"
# Ground truth for this table only contains resp == 1 for this item (140 rows out of ~3178
# respondents) -- consistent with a computed straight-lining flag, not a Likert item.
rows[[length(rows) + 1]] <- data.frame(
  table = table,
  section_id = paste0(table, "_bias"),
  item = "SocMedia_bias_dummy",
  instrument = instrument_name,
  instructions = instructions_txt,
  section_prompt = "",
  item_text = "Derived response-bias indicator (not an administered item): computed flag equal to 1 when a respondent gave the identical rating to all 11 SocMedia items (straight-lining detection).",
  correct_response = "",
  option_text = "Flagged as response bias (identical rating given to all SocMedia items)",
  resp = 1,
  stringsAsFactors = FALSE
)

items <- do.call(rbind, rows)
rownames(items) <- NULL

str(items)

gt <- readRDS(".gt_eammi_grahe_2018_socmedia.rds")
cat("item match:", setequal(unique(items$item), unique(gt$item)), "\n")
cat("resp match:", setequal(unique(items$resp), unique(gt$resp)), "\n")

saveRDS(items, "candidate_eammi_grahe_2018_socmedia.rds")
cat("wrote candidate_eammi_grahe_2018_socmedia.rds, nrow=", nrow(items), "\n")
