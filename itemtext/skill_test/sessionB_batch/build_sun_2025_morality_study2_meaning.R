library(dplyr)

table_name <- "sun_2025_morality_study2_meaning"

items_df <- data.frame(
  table = table_name,
  section_id = paste0(table_name, "_1"),
  item = paste0("tsmlq", 1:5),
  item_text = c(
    "I understand my life's meaning.",  # explicitly quoted in paper as example item; item order inferred from ts.MLQ1 variable naming
    "", "", "", ""
  ),
  correct_response = "",
  stringsAsFactors = FALSE
)

sections_df <- data.frame(
  table = table_name,
  section_id = paste0(table_name, "_1"),
  section_prompt = "",
  stringsAsFactors = FALSE
)

instrument_df <- data.frame(
  table = table_name,
  instrument = "Presence of Meaning subscale, Meaning in Life Questionnaire (MLQ; Steger, Frazier, Oishi, & Kaler, 2006)",
  instructions = "Employees reported their sense of meaning in life using the five-item Presence of Meaning subscale from the Meaning in Life Questionnaire (Steger et al., 2006), rated on a 7-point scale (1 = absolutely untrue, 7 = absolutely true).",
  stringsAsFactors = FALSE
)

# responses: one row per item x resp (1-7); only endpoints have known option_text
resp_vals <- 1:7
responses_df <- do.call(rbind, lapply(paste0("tsmlq", 1:5), function(it) {
  data.frame(
    table = table_name,
    section_id = paste0(table_name, "_1"),
    item = it,
    resp = resp_vals,
    option_text = ifelse(resp_vals == 1, "absolutely untrue",
                   ifelse(resp_vals == 7, "absolutely true", "")),
    stringsAsFactors = FALSE
  )
}))

merged <- merge(items_df, sections_df, by = c("table", "section_id"), all.x = TRUE)
merged <- merge(merged, instrument_df, by = "table", all.x = TRUE)
merged <- merge(merged, responses_df, by = c("table", "section_id", "item"), all.x = TRUE)

final_cols <- c("table", "section_id", "item", "instrument", "instructions",
                 "section_prompt", "item_text", "correct_response", "option_text", "resp")
merged <- merged[, final_cols]
merged <- merged[order(merged$item, merged$resp), ]
rownames(merged) <- NULL

str(merged)
print(merged)

saveRDS(merged, "/home/ben/Dropbox/projects/irw/src/itemtext/skill_test/sessionB_batch/candidate_sun_2025_morality_study2_meaning.rds")
