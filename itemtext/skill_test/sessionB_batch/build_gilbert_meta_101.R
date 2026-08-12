items <- data.frame(
  table = "gilbert_meta_101",
  section_id = "gilbert_meta_101_1",
  item = c("appetite","concentration","mood","pleasure","psychomotor",
           "self_worth","sleep","suicidal_ideation","tiredness"),
  item_text = c(
    "change in appetite and/or weight",
    "concentration problems",
    "depressive mood",
    "reduced pleasure and/or interest",
    "psychomotor problems",
    "reduced self-worth",
    "sleeping problems",
    "suicidal ideation",
    "tiredness"
  ),
  correct_response = "",
  stringsAsFactors = FALSE
)

sections <- data.frame(
  table = "gilbert_meta_101",
  section_id = "gilbert_meta_101_1",
  section_prompt = "",
  stringsAsFactors = FALSE
)

instrument <- data.frame(
  table = "gilbert_meta_101",
  instrument = "Inventory of Depressive Symptomatology (IDS), 28-item self-report version, dichotomized to the 9 DSM-5 major depressive disorder symptom domains",
  instructions = "Participants were asked before every treatment session how they experienced a specific symptom on a 4-point Likert scale.",
  stringsAsFactors = FALSE
)

responses <- data.frame(
  table = "gilbert_meta_101",
  section_id = "gilbert_meta_101_1",
  item = rep(c("appetite","concentration","mood","pleasure","psychomotor",
               "self_worth","sleep","suicidal_ideation","tiredness"), each = 2),
  option_text = rep(c("symptom not present", "symptom present"), times = 9),
  resp = rep(c(0L, 1L), times = 9),
  stringsAsFactors = FALSE
)

m <- merge(items, sections, by = c("table","section_id"), all.x = TRUE)
m <- merge(m, instrument, by = "table", all.x = TRUE)
m <- merge(m, responses, by = c("table","section_id","item"), all.x = TRUE)

col_order <- c("table","section_id","item","instrument","instructions",
               "section_prompt","item_text","correct_response","option_text","resp")
m <- m[, col_order]

# order rows: by item (in ground-truth item order), then resp
item_order <- c("appetite","concentration","mood","pleasure","psychomotor",
                 "self_worth","sleep","suicidal_ideation","tiredness")
m <- m[order(match(m$item, item_order), m$resp), ]
rownames(m) <- NULL

saveRDS(m, file = "/home/ben/Dropbox/projects/irw/src/itemtext/skill_test/sessionB_batch/candidate_gilbert_meta_101.rds")

str(m)
print(m)

gt <- readRDS("/home/ben/Dropbox/projects/irw/src/itemtext/skill_test/sessionB_batch/.gt_gilbert_meta_101.rds")
cat("\n--- validation ---\n")
cat("item match:", identical(sort(unique(m$item)), sort(unique(gt$item))), "\n")
cat("resp match:", identical(sort(unique(m$resp)), sort(unique(gt$resp))), "\n")
