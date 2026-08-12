library(dplyr)

table_id <- "aip_vangsness_2019"

items_text <- c(
  AIP_1  = "I often think that “I don’t get things done on time.”",
  AIP_2  = "If someone were teaching a course on how to get things done on time I would want to attend.",
  AIP_3  = "My friends and family think I often wait until the last minute.",
  AIP_4  = "I get important things done with time to spare.",
  AIP_5  = "I am not very good at meeting deadlines.",
  AIP_6  = "I find myself frequently running out of time.",
  AIP_7  = "I am as on time as most people I know.",
  AIP_8  = "I have problems with procrastination (or putting things off).",
  AIP_9  = "When I must be somewhere at a certain time my friends can count on me being there.",
  AIP_10 = "I usually meet major deadlines.",
  AIP_11 = "I often think that “I don’t get things done on time.”"
)

# direction of scoring per item as literally presented in the OSF survey PDF
# (procrastinationFullSurvey.pdf, "Adult Inventory of Procrastination" block):
# "straight" = Strongly agree(5)...Strongly disagree(1)
# "reverse"  = Strongly agree(1)...Strongly disagree(5)
straight_items <- c("AIP_1","AIP_2","AIP_3","AIP_5","AIP_6","AIP_8","AIP_11")
reverse_items  <- c("AIP_4","AIP_7","AIP_9","AIP_10")

instructions_txt <- "This questionnaire is concerned with beliefs people have about task completion. Listed below are a number of beliefs that people have expressed. Please read each item and say how much you generally agree with it by selecting the one appropriate number. There are no right or wrong answers."

instrument_txt <- "Adult Inventory of Procrastination (AIP; McCown & Johnson, 1989)"

rows <- list()
for (idx in seq_along(items_text)) {
  it <- names(items_text)[idx]
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
      resp = as.numeric(r),
      stringsAsFactors = FALSE
    )
  }
}

d <- do.call(rbind, rows)
rownames(d) <- NULL
str(d)
print(head(d, 12))

saveRDS(d, file = "/home/ben/Dropbox/projects/irw/src/itemtext/skill_test/sessionB_batch/candidate_aip_vangsness_2019.rds")

# validation against ground truth
gt <- readRDS("/home/ben/Dropbox/projects/irw/src/itemtext/skill_test/sessionB_batch/.gt_aip_vangsness_2019.rds")
cat("\nitem match:", identical(sort(unique(d$item)), sort(unique(gt$item))), "\n")
cat("resp match:", identical(sort(unique(as.numeric(d$resp))), sort(unique(as.numeric(gt$resp)))), "\n")
