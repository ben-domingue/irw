library(dplyr)
library(tidyr)
library(here)

in_dir  <- here("raw_data")
out_dir <- here("processed")
dir.create(out_dir, showWarnings = FALSE, recursive = TRUE)

d70_items <- paste0("d", 1:70)

cov_rename <- c(
  dVersion  = "cov_version",
  dLang     = "cov_language",
  age       = "cov_age",
  sex       = "cov_gender",
  byear     = "cov_birth_year",
  lang      = "cov_lang_skills",
  country   = "cov_country",
  agreement = "cov_agreement",
  group     = "cov_group"
)

# Shared helper: rename covariates, pivot just the D70 items, tag with study
make_d70_table <- function(raw, study_tag) {
  matched <- names(raw) %in% names(cov_rename)
  names(raw)[matched] <- cov_rename[names(raw)[matched]]
  cov_cols <- names(raw)[startsWith(names(raw), "cov_")]
  
  raw %>%
    select(id, all_of(cov_cols), all_of(d70_items)) %>%
    pivot_longer(all_of(d70_items), names_to = "item", values_to = "resp") %>%
    mutate(cov_study = study_tag) %>%
    relocate(item, resp, .after = id)
}

# ---- Sample 1a (semicolon-delimited, id column is "X") ----
raw_1a <- read.csv2(file.path(in_dir, "d-fr-en-matched-MI-analysis.csv"), stringsAsFactors = FALSE) %>%
  rename(id = X) %>%
  mutate(id = paste0("1a_", id))
d70_1a <- make_d70_table(raw_1a, "1a")

# ---- Sample 1b (semicolon-delimited, id column unnamed -> read in as "X") ----
raw_1b <- read.csv2(file.path(in_dir, "data.cct.csv"), stringsAsFactors = FALSE) %>%
  rename(id = X) %>%
  mutate(id = paste0("1b_", id))
d70_1b <- make_d70_table(raw_1b, "1b")

# ---- Sample 2a (comma-delimited, id column already named "id") ----
raw_2a <- read.csv(file.path(in_dir, "data.beliefs.csv"), stringsAsFactors = FALSE) %>%
  mutate(id = paste0("2a_", id))
d70_2a <- make_d70_table(raw_2a, "2a")

# ---- Sample 2b ----
raw_2b <- read.csv(file.path(in_dir, "data.dispositions.csv"), stringsAsFactors = FALSE) %>%
  mutate(id = paste0("2b_", id))
d70_2b <- make_d70_table(raw_2b, "2b")

# ---- Sample 2c ----
raw_2c <- read.csv(file.path(in_dir, "data.behaviors.csv"), stringsAsFactors = FALSE) %>%
  mutate(id = paste0("2c_", id))
d70_2c <- make_d70_table(raw_2c, "2c")

# ---- Merge all five D70 blocks ----
d70_all <- bind_rows(d70_1a, d70_1b, d70_2a, d70_2b, d70_2c) %>%
  mutate(id = as.numeric(factor(id, levels = unique(id))))

write.csv(d70_all, file.path(out_dir, "darkfactorfrench_pischel_2026_d70.csv"), row.names = FALSE)