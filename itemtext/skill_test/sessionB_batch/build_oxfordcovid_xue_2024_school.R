## Build candidate_oxfordcovid_xue_2024_school.rds
## Source: .cache/oxfordcovid_xue_2024_mfq/raw_data_codebook.txt (REDCap codebook export,
## "Wellbeing and Resilience during COVID-19" project), reused per instructions since it
## covers every instrument in the study, including the "covid" instrument's school_* fields
## (lines ~4071-4506 of raw_data_codebook.txt / PDF pages 27-29).

instrument_name <- "Oxford ARC COVID-19 study: school/homeschooling items (REDCap instrument 'covid', fields school_1, school_2, school_support_1-5, school_stress, school_pos_neg_1-11)"

rows <- list()

add_block <- function(items, item_text, section_id, section_prompt, resp, option_text) {
  out <- list()
  for (it in items) {
    for (i in seq_along(resp)) {
      out[[length(out) + 1]] <- data.frame(
        table = "oxfordcovid_xue_2024_school",
        section_id = section_id,
        item = it,
        instrument = instrument_name,
        instructions = "",
        section_prompt = section_prompt,
        item_text = item_text[[it]],
        correct_response = "",
        option_text = option_text[i],
        resp = resp[i],
        stringsAsFactors = FALSE
      )
    }
  }
  do.call(rbind, out)
}

## --- Block 1: school_1, school_2 (general school-status items, no shared section header) ---
gen_item_text <- list(
  school_1 = "Is your school currently:",
  school_2 = "How many days a week are you in school?"
)
b1_school1 <- add_block(
  items = "school_1", item_text = gen_item_text,
  section_id = "oxfordcovid_xue_2024_school_general", section_prompt = "",
  resp = c(1, 2, 3),
  option_text = c("open", "closed", "on a holiday break")
)
b1_school2 <- add_block(
  items = "school_2", item_text = gen_item_text,
  section_id = "oxfordcovid_xue_2024_school_general", section_prompt = "",
  resp = 0:7,
  option_text = as.character(0:7)
)

## --- Block 2: school_support_1..5 ---
support_item_text <- list(
  school_support_1 = "Support students' mental health?",
  school_support_2 = "Protect students against COVID-19?",
  school_support_3 = "Protect teachers and parents against COVID-19?",
  school_support_4 = "Enforce social distancing?",
  school_support_5 = "Wear masks?"
)
b2 <- do.call(rbind, lapply(names(support_item_text), function(it) {
  add_block(
    items = it, item_text = support_item_text,
    section_id = "oxfordcovid_xue_2024_school_support",
    section_prompt = "Do you think your school is taking enough measures to:",
    resp = c(1, 2, 3),
    option_text = c("no", "yes", "not applicable")
  )
}))

## --- Block 3: school_stress (single item, own 5-point scale) ---
b3 <- add_block(
  items = "school_stress",
  item_text = list(school_stress = "How stressful are you finding school and/or home schooling compared to this time last year?"),
  section_id = "oxfordcovid_xue_2024_school_stress", section_prompt = "",
  resp = 1:5,
  option_text = c("much more stressful", "somewhat more stressful", "equally stressful",
                   "somewhat less stressful", "much less stressful")
)

## --- Block 4: school_pos_neg_1..11 ---
posneg_item_text <- list(
  school_pos_neg_1 = "School in general",
  school_pos_neg_2 = "Homeschooling in general",
  school_pos_neg_3 = "The amount of schoolwork",
  school_pos_neg_4 = "The amount of homework",
  school_pos_neg_5 = "Relationships with teachers",
  school_pos_neg_6 = "Teacher expectations",
  school_pos_neg_7 = "Relationships with other students",
  school_pos_neg_8 = "Social distancing at school",
  school_pos_neg_9 = "Cases of COVID-19 at your school",
  school_pos_neg_10 = "Taking/Retaking exams",
  school_pos_neg_11 = "Getting grades"
)
b4 <- do.call(rbind, lapply(names(posneg_item_text), function(it) {
  add_block(
    items = it, item_text = posneg_item_text,
    section_id = "oxfordcovid_xue_2024_school_posneg",
    section_prompt = "Please rate how positive (helpful) or negative (harmful) you have found the following, relating to your school experience in the past week",
    resp = 0:7,
    option_text = c("Not applicable", "Very negative", "Quite negative", "A bit negative",
                     "Neither negative nor positive", "A bit positive", "Quite positive", "Very positive")
  )
}))

candidate <- rbind(b1_school1, b1_school2, b2, b3, b4)
rownames(candidate) <- NULL
candidate$resp <- as.integer(candidate$resp)

saveRDS(candidate, "candidate_oxfordcovid_xue_2024_school.rds")

## --- Validation against cached ground truth ---
gt <- readRDS(".gt_oxfordcovid_xue_2024_school.rds")
cat("item match:", identical(sort(unique(candidate$item)), sort(unique(gt$item))), "\n")
cat("resp match:", identical(sort(unique(candidate$resp)), sort(unique(gt$resp))), "\n")
missing_items <- setdiff(unique(gt$item), unique(candidate$item))
extra_items <- setdiff(unique(candidate$item), unique(gt$item))
cat("missing items:", paste(missing_items, collapse=","), "\n")
cat("extra items:", paste(extra_items, collapse=","), "\n")

# per-item resp subset check (candidate resp set should be superset of gt resp set per item)
for (it in unique(gt$item)) {
  gt_r <- sort(unique(gt$resp[gt$item==it]))
  cand_r <- sort(unique(candidate$resp[candidate$item==it]))
  if (!all(gt_r %in% cand_r)) cat("MISMATCH for", it, ": gt has", paste(gt_r,collapse=","), "cand has", paste(cand_r,collapse=","), "\n")
}
cat("done\n")
str(candidate)
