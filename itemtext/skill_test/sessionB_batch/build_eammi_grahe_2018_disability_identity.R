## Build candidate items table for eammi_grahe_2018_disability_identity
## Source: EAMMi2 survey PDF (Q10 block) + codebook (Q10_1..Q10_15), both cached
## under itemtext/.cache/eammi_grahe_2018_moa1/ (shared cache across sibling EAMMi2 tables).

table_name <- "eammi_grahe_2018_disability_identity"

items_text <- c(
  "My disability interferes with becoming successful.",
  "I don't think of myself as a disabled person.",
  "I lack confidence because of my disability.",
  "I am proud to be a disabled person.",
  "Sometimes I am ashamed to be disabled.",
  "Being disabled has not reduced my enjoyment of life.",
  "My friendships are limited by my disability.",
  "My disability is a source of personal strength.",
  "Without my disability I could accomplish more.",
  "Having a disability has not been a problem for me.",
  "I can live a normal life with my disability.",
  "I am a better person because of my disability.",
  "My disability is an important part of who I am.",
  "I am proud of my disability.",
  "My disability enriches my life."
)
items <- paste0("Q10_", 1:15)
stopifnot(length(items_text) == 15)

instructions_text <- "If applicable, please rate your degree of agreement with each of the following statements."

options <- data.frame(
  resp = 1:5,
  option_text = c("Strongly disagree", "Disagree", "Neither agree nor disagree", "Agree", "Strongly agree"),
  stringsAsFactors = FALSE
)

instrument_name <- "EAMMi2 Disability Identity Items (Q10)"

section_id <- paste0(table_name, "_1")

rows <- do.call(rbind, lapply(seq_along(items), function(i) {
  data.frame(
    table = table_name,
    section_id = section_id,
    item = items[i],
    instrument = instrument_name,
    instructions = instructions_text,
    section_prompt = "",
    item_text = items_text[i],
    correct_response = "",
    option_text = options$option_text,
    resp = options$resp,
    stringsAsFactors = FALSE
  )
}))

rownames(rows) <- NULL

## --- Validation against cached ground truth ---
gt <- readRDS("/home/ben/Dropbox/projects/irw/src/itemtext/skill_test/sessionB_batch/.gt_eammi_grahe_2018_disability_identity.rds")
gt_items <- sort(unique(gt$item))
gt_resp  <- sort(unique(gt$resp))

cand_items <- sort(unique(rows$item))
cand_resp  <- sort(unique(rows$resp))

item_match <- setequal(gt_items, cand_items)
resp_match <- setequal(gt_resp, cand_resp)

cat("item match:", item_match, "\n")
cat("resp match:", resp_match, "\n")
if (!item_match) {
  cat("GT items not in candidate:\n"); print(setdiff(gt_items, cand_items))
  cat("Candidate items not in GT:\n"); print(setdiff(cand_items, gt_items))
}
if (!resp_match) {
  cat("GT resp not in candidate:\n"); print(setdiff(gt_resp, cand_resp))
  cat("Candidate resp not in GT:\n"); print(setdiff(cand_resp, gt_resp))
}

stopifnot(item_match, resp_match)

saveRDS(rows, "/home/ben/Dropbox/projects/irw/src/itemtext/skill_test/sessionB_batch/candidate_eammi_grahe_2018_disability_identity.rds")
cat("Saved candidate_eammi_grahe_2018_disability_identity.rds with", nrow(rows), "rows\n")
