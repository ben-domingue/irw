library(dplyr)
library(tidyr)
library(here)

in_dir  <- here("raw_data")
out_dir <- here("processed")
dir.create(out_dir, showWarnings = FALSE, recursive = TRUE)

cov_rename <- c(
  dVersion  = "cov_version", dLang = "cov_language", age = "cov_age",
  sex = "cov_gender", lang = "cov_lang_skills", country = "cov_country",
  agreement = "cov_agreement", time = "cov_time"
)

# ---- Read files ----
raw_2a <- read.csv(file.path(out_dir, "data.beliefs.csv"), stringsAsFactors = FALSE)
raw_2b <- read.csv(file.path(out_dir, "data.dispositions.csv"), stringsAsFactors = FALSE)
raw_2c <- read.csv(file.path(out_dir, "data.behaviors.csv"), stringsAsFactors = FALSE)

# ---- Shared helper: rename covariates, add cov_study, write one table per criterion block ----
make_criterion_tables <- function(raw, criterion_blocks, study_tag, output_dir) {
  matched <- names(raw) %in% names(cov_rename)
  names(raw)[matched] <- cov_rename[names(raw)[matched]]
  raw$cov_study <- study_tag
  cov_cols <- names(raw)[startsWith(names(raw), "cov_")]
  
  for (nm in names(criterion_blocks)) {
    tbl <- raw %>%
      select(id, all_of(cov_cols), all_of(criterion_blocks[[nm]])) %>%
      pivot_longer(all_of(criterion_blocks[[nm]]), names_to = "item", values_to = "resp") %>%
      relocate(item, resp, .after = id)
    
    out_path <- file.path(output_dir, paste0("darkfactorfrench_pischel_2026_", nm, ".csv"))
    write.csv(tbl, out_path, row.names = FALSE)
    message("Wrote: ", out_path, " (", nrow(tbl), " rows)")
  }
}

# ---- Sample 2a: Beliefs ----
make_criterion_tables(
  raw_2a,
  criterion_blocks = list(
    normlessness = paste0("normless_", 1:4),
    worldview_cj = paste0("CJ_", 1:6),
    sdo7s        = paste0("SDO_", 1:8)
  ),
  study_tag = "2a", output_dir = out_dir
)

# ---- Sample 2b: Dispositions/tendencies ----
make_criterion_tables(
  raw_2b,
  criterion_blocks = list(
    interp_dysfx = paste0("PDYS_", 1:6),
    exploitative = paste0("exploit_", 1:6),
    callousness  = paste0("PID5_100_", 1:4)
  ),
  study_tag = "2b", output_dir = out_dir
)

# ---- Sample 2c: Behaviors ----
make_criterion_tables(
  raw_2c,
  criterion_blocks = list(
    civic_behavior = paste0("civicbeh_", 1:6),
    crime_analog   = paste0("CAB_", 1:10),
    dictator_game  = "DG"
  ),
  study_tag = "2c", output_dir = out_dir
)

# ---- Check the files actually got written ----
list.files(out_dir, pattern = "darkfactorfrench_pischel_2026")