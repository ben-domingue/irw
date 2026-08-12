library(dplyr)

table_id <- "paampsmartsud_saba_2023_ffmq"

gt <- readRDS("/home/ben/Dropbox/projects/irw/src/itemtext/skill_test/sessionB_batch/.gt_paampsmartsud_saba_2023_ffmq.rds")
item_ids <- sort(unique(gt$item))  # FFMQ_1_POST .. FFMQ_25_POST, skipping FFMQ_23_POST (24 items)
resp_levels <- sort(unique(gt$resp))  # 1:5

items <- data.frame(
  item = item_ids,
  # Item-level wording could NOT be reliably assigned: see extraction log.
  # The FFMQ_<n>_POST numbering in the OSF raw data does not match the
  # original 39-item FFMQ (Baer et al. 2006) numbering used by secondary
  # sources to describe the Bohlmeijer et al. (2011) FFMQ-24/FFMQ-SF item
  # selection, and no supplement/codebook discloses the survey's own
  # presentation order. Left blank rather than guessed.
  item_text = NA_character_,
  stringsAsFactors = FALSE
)
items$table <- table_id
items$section_id <- paste0(table_id, "_ffmq")
items$correct_response <- ""

sections <- data.frame(
  table = table_id,
  section_id = paste0(table_id, "_ffmq"),
  section_prompt = "",
  stringsAsFactors = FALSE
)

instrument <- data.frame(
  table = table_id,
  instrument = "Five Facet Mindfulness Questionnaire - Short Form (FFMQ-24 / FFMQ-SF; Bohlmeijer et al., 2011)",
  # Directly from Saba & Black (2023/2024), describing the FFMQ-SF as used in
  # this study (not a literal on-screen instructions paragraph -- see log).
  instructions = "A self-report measure to quantify an individual's tendency to be mindful in daily life over a 30-day period. The 24-item measure asks participants to rate items on a 5-point Likert scale from 1 never or very rarely true to 5 very often or always true.",
  stringsAsFactors = FALSE
)

# Only the two scale endpoints are disclosed in the applied paper; the
# original FFMQ/FFMQ-SF sources are inconsistent on interior-point wording,
# so interior points (2,3,4) are left unlabeled rather than guessed.
option_labels <- setNames(rep("", length(resp_levels)), as.character(resp_levels))
option_labels[as.character(min(resp_levels))] <- "never or very rarely true"
option_labels[as.character(max(resp_levels))] <- "very often or always true"

responses <- do.call(rbind, lapply(items$item, function(it) {
  data.frame(
    table = table_id,
    section_id = paste0(table_id, "_ffmq"),
    item = it,
    option_text = unname(option_labels[as.character(resp_levels)]),
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

cat("item match:", identical(sort(unique(merged$item)), sort(unique(gt$item))), "\n")
cat("resp match:", identical(sort(unique(merged$resp)), sort(unique(gt$resp))), "\n")

saveRDS(merged, "/home/ben/Dropbox/projects/irw/src/itemtext/skill_test/sessionB_batch/candidate_paampsmartsud_saba_2023_ffmq.rds")
