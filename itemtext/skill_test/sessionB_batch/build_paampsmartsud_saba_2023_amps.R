library(dplyr)

table_id <- "paampsmartsud_saba_2023_amps"

items <- data.frame(
  item = sprintf("AMPS_%02d", 1:15),
  item_text = c(
    "I used mindfulness practice to… observe my thoughts in a non-attached manner.",
    "I used mindfulness practice to… relax my body when I was tense.",
    "I used mindfulness practice to… see that my thoughts were not necessarily true.",
    "I used mindfulness practice to… enjoy the little things in life more fully.",
    "I used mindfulness practice to… calm my emotions when I was upset.",
    "I used mindfulness practice to… stop reacting to my negative impulses.",
    "I used mindfulness practice to… see the positive side of difficult circumstances.",
    "I used mindfulness practice to… reduce tension when I was stressed.",
    "I used mindfulness practice to… realize that I can grow stronger from difficult circumstances.",
    "I used mindfulness practice to… stop my unhelpful reactions to situations.",
    "I used mindfulness practice to… be aware of and appreciating pleasant events.",
    "I used mindfulness practice to… let go of unpleasant thoughts and feelings.",
    "I used mindfulness practice to… realize that my thoughts were not facts.",
    "I used mindfulness practice to… notice pleasant things in the face of difficult circumstances.",
    "I used mindfulness practice to… see alternate views of a situation."
  ),
  stringsAsFactors = FALSE
)
items$table <- table_id
items$section_id <- paste0(table_id, "_amps")
items$correct_response <- ""

sections <- data.frame(
  table = table_id,
  section_id = paste0(table_id, "_amps"),
  section_prompt = "",
  stringsAsFactors = FALSE
)

instrument <- data.frame(
  table = table_id,
  instrument = "Applied Mindfulness Process Scale (AMPS)",
  instructions = "Everyone gets confronted with negative or stressful events in daily life, and people who practice mindfulness cope with these events in different ways. Please indicate how often you have used mindfulness to cope in each of these ways (if at all) for the period of the last week (past 7 days).",
  stringsAsFactors = FALSE
)

resp_levels <- 0:4
option_labels <- c("Never", "", "", "", "Almost always")

responses <- do.call(rbind, lapply(items$item, function(it) {
  data.frame(
    table = table_id,
    section_id = paste0(table_id, "_amps"),
    item = it,
    option_text = option_labels,
    resp = resp_levels,
    stringsAsFactors = FALSE
  )
}))

merged <- merge(items, sections, by = c("table", "section_id"), all.x = TRUE)
merged <- merge(merged, instrument, by = "table", all.x = TRUE)
merged <- merge(merged, responses, by = c("table", "section_id", "item"), all.x = TRUE)

merged <- merged[, c("table","section_id","item","instrument","instructions",
                      "section_prompt","item_text","correct_response",
                      "option_text","resp")]

merged <- merged[order(match(merged$item, items$item), merged$resp), ]
rownames(merged) <- NULL

str(merged)
cat("n rows:", nrow(merged), "\n")

# Validate against ground truth
gt <- readRDS(".gt_paampsmartsud_saba_2023_amps.rds")
gt <- readRDS("/home/ben/Dropbox/projects/irw/src/itemtext/skill_test/sessionB_batch/.gt_paampsmartsud_saba_2023_amps.rds")
cat("item match:", identical(sort(unique(merged$item)), sort(unique(gt$item))), "\n")
cat("resp match:", identical(sort(unique(merged$resp)), sort(unique(gt$resp))), "\n")

saveRDS(merged, "/home/ben/Dropbox/projects/irw/src/itemtext/skill_test/sessionB_batch/candidate_paampsmartsud_saba_2023_amps.rds")
