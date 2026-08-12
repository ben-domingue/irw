items_order <- c("class1","class2","class3","class4","class5","class6","class7","class8","class9","class10")

item_text <- c(
  class1  = "Have students talk about their class work",
  class2  = "Let students decide where to sit at the beginning of the school year",
  class3  = "Allow students to choose their partners for group work",
  class4  = "Ask for students' ideas",
  class5  = "Let students help make school rules",
  class6  = "Pay too much attention to grades and not enough attention to helping students learn",
  class7  = "Only care about the smart kids in the class",
  class8  = "Have given up on some of their students",
  class9  = "Encourage students to compete against each other for grades",
  class10 = "Give students credit for trying hard"
)

resp_levels <- 1:5
option_text <- c("Not at All", "A little True", "Somewhat True", "Quite True", "Very True")

instrument_name <- "Class Time (Perception of Teaching Style scale)"
instructions_text <- "This set of questions is about how things work at your school.  How true is it that your teacher does the following:"

rows <- list()
for (it in items_order) {
  for (i in seq_along(resp_levels)) {
    rows[[length(rows) + 1]] <- data.frame(
      table = "florida_twins_class",
      section_id = "florida_twins_class_1",
      item = it,
      instrument = instrument_name,
      instructions = instructions_text,
      section_prompt = "",
      item_text = item_text[[it]],
      correct_response = "",
      option_text = option_text[i],
      resp = resp_levels[i],
      stringsAsFactors = FALSE
    )
  }
}

d <- do.call(rbind, rows)
rownames(d) <- NULL
str(d)
saveRDS(d, file = "candidate_florida_twins_class.rds")
