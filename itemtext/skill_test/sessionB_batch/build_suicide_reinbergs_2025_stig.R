library(dplyr)
library(tidyr)

table_name <- "suicide_reinbergs_2025_stig"
items <- paste0("stig0", 1:9)
resp_vals <- 1:4
option_text <- c("Disagree", "Somewhat disagree", "Somewhat agree", "Agree")

# instrument tab
instrument_df <- data.frame(
  table = table_name,
  instrument = "Suicide Stigma Scale",
  instructions = NA_character_,
  stringsAsFactors = FALSE
)

# sections tab - one trivial section for all items, no confirmed passage
sections_df <- data.frame(
  table = table_name,
  section_id = paste0(table_name, "_1"),
  section_prompt = "",
  stringsAsFactors = FALSE
)

# items tab - item_text left NA; see extraction log for why
items_df <- data.frame(
  table = table_name,
  section_id = paste0(table_name, "_1"),
  item = items,
  item_text = NA_character_,
  correct_response = "",
  stringsAsFactors = FALSE
)

# responses tab - one row per item x resp
responses_df <- expand.grid(
  table = table_name,
  section_id = paste0(table_name, "_1"),
  item = items,
  resp = resp_vals,
  stringsAsFactors = FALSE
) %>%
  mutate(option_text = option_text[resp]) %>%
  select(table, section_id, item, option_text, resp)

# merge per Step 4 / itemtext_standard.md merge logic
merged <- items_df %>%
  merge(sections_df, by = c("table", "section_id"), all.x = TRUE) %>%
  merge(instrument_df, by = "table", all.x = TRUE) %>%
  merge(responses_df, by = c("table", "section_id", "item"), all.x = TRUE)

merged <- merged %>%
  select(table, section_id, item, instrument, instructions, section_prompt,
         item_text, correct_response, option_text, resp) %>%
  arrange(item, resp)

str(merged)
print(head(merged, 12))

saveRDS(merged, file = "candidate_suicide_reinbergs_2025_stig.rds")
cat("\nRows:", nrow(merged), "\n")
