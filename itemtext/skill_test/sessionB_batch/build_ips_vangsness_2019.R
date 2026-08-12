library(dplyr)

table_id <- "ips_vangsness_2019"

items_text <- c(
  IPS_1 = "I put things off so long that my well-being or efficiency unnecessarily suffers.",
  IPS_2 = "If there is something I should do, I get to it before attending to lesser tasks.",
  IPS_3 = "My life would be better if I did some activities or tasks earlier.",
  IPS_4 = "When I should be doing one thing, I will do another.",
  IPS_5 = "At the end of the day, I know I could have spent the time better.",
  IPS_6 = "I spend my time wisely.",
  IPS_7 = "I delay tasks beyond what is reasonable.",
  IPS_8 = "I procrastinate.",
  IPS_9 = "I do everything when I believe it needs to be done."
)

# direction of scoring per item as literally presented in the OSF survey PDF
# (procrastinationFullSurvey.pdf, "Irrational Procrastination Scale" block):
# "straight" = Strongly agree(5)...Strongly disagree(1)
# "reverse"  = Strongly agree(1)...Strongly disagree(5)
straight_items <- c("IPS_1","IPS_3","IPS_4","IPS_5","IPS_7","IPS_8")
reverse_items  <- c("IPS_2","IPS_6","IPS_9")

instructions_txt <- "This questionnaire is concerned with beliefs people have about task completion. Listed below are a number of beliefs that people have expressed. Please read each item and say how much you generally agree with it by selecting the one appropriate number. There are no right or wrong answers."

instrument_txt <- "Irrational Procrastination Scale (IPS; Steel, 2010)"

rows <- list()
for (it in names(items_text)) {
  if (it %in% straight_items) {
    opt <- c(`1` = "Strongly disagree", `2` = "Somewhat disagree", `3` = "Neither agree nor disagree",
             `4` = "Somewhat agree", `5` = "Strongly agree")
  } else {
    opt <- c(`1` = "Strongly agree", `2` = "Somewhat agree", `3` = "Neither agree nor disagree",
              `4` = "Somewhat disagree", `5` = "Strongly disagree")
  }
  for (r in 1:5) {
    rows[[length(rows) + 1]] <- data.frame(
      table = table_id,
      section_id = paste0(table_id, "_", it),
      item = it,
      instrument = instrument_txt,
      instructions = instructions_txt,
      section_prompt = "",
      item_text = items_text[[it]],
      correct_response = "",
      option_text = opt[[as.character(r)]],
      resp = r,
      stringsAsFactors = FALSE
    )
  }
}

d <- do.call(rbind, rows)
rownames(d) <- NULL
str(d)
print(head(d, 12))

saveRDS(d, file = "/home/ben/Dropbox/projects/irw/src/itemtext/skill_test/sessionB_batch/candidate_ips_vangsness_2019.rds")

# validation against ground truth
gt <- readRDS("/home/ben/Dropbox/projects/irw/src/itemtext/skill_test/sessionB_batch/.gt_ips_vangsness_2019.rds")
cat("\nitem match:", identical(sort(unique(d$item)), sort(unique(gt$item))), "\n")
cat("resp match:", identical(sort(unique(d$resp)), sort(unique(gt$resp))), "\n")
