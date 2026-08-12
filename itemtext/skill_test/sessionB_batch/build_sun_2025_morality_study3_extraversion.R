table <- "sun_2025_morality_study3_extraversion"

items <- data.frame(
  item = c("itbfi21", "itbfi216", "itbfi221", "itbfi226", "itbfi241", "itbfi251"),
  item_text = c(
    "is outgoing, sociable",
    "tends to be quiet",
    "is dominant, acts as a leader",
    "is less active than other people",
    "is full of energy",
    "prefers to have others take charge"
  ),
  stringsAsFactors = FALSE
)

instrument_text <- "BFI-2-S (Soto & John, 2017b) -- Extraversion domain, informant-report (Sociability, Assertiveness, and Energy Level facets)"
instructions_text <- "Informants rated six statements from the BFI-2-S (Soto & John, 2017b) using a 5-point scale anchored by strongly disagree and strongly agree."
section_id <- paste0(table, "_1")

resp_levels <- 1:5
option_map <- c(`1` = "strongly disagree", `2` = "", `3` = "", `4` = "", `5` = "strongly agree")

out <- do.call(rbind, lapply(seq_len(nrow(items)), function(i) {
  data.frame(
    table = table,
    section_id = section_id,
    item = items$item[i],
    instrument = instrument_text,
    instructions = instructions_text,
    section_prompt = "",
    item_text = items$item_text[i],
    correct_response = "",
    option_text = option_map[as.character(resp_levels)],
    resp = resp_levels,
    stringsAsFactors = FALSE
  )
}))

rownames(out) <- NULL
saveRDS(out, file.path("/home/ben/Dropbox/projects/irw/src/itemtext/skill_test/sessionB_batch",
                        "candidate_sun_2025_morality_study3_extraversion.rds"))
str(out)
print(out)
