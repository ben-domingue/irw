library(readr)
library(dplyr)
library(lubridate)
library(here)

# ---- 0. Resolve input/output paths ----------------------------------------
# here() anchors to the project folder (where this script + Interactions.csv
# live), so paths work the same whether you run this via Rscript, source()
# it in RStudio, or run it in VS Code.
input_path  <- here("Interactions.csv")
output_path <- here("foundationalassist_worden_2026.csv")

# ---- 1. Read raw data -------------------------------------------------------
df <- read_csv(input_path, show_col_types = FALSE)

# ---- 2. Drop exact-duplicate interaction rows -------------------------------
# Compare every column except any unnamed leading index column (readr names
# it "...1" if present); if there isn't one, this just compares all columns.
index_col    <- intersect(names(df), "...1")
compare_cols <- setdiff(names(df), index_col)

n_before <- nrow(df)
df <- df %>% distinct(across(all_of(compare_cols)), .keep_all = TRUE)
cat("Removed", n_before - nrow(df), "exact-duplicate rows\n")

# ---- 3. Drop rows with no scoreable response ---------------------------------
n_before <- nrow(df)
df <- df %>% filter(!is.na(discrete_score))
cat("Removed", n_before - nrow(df), "rows with missing discrete_score\n")

# ---- 4. Map columns to the IRW standard --------------------------------------
# id   <- user_id      (the actual person identifier)
# item <- problem_id
# resp <- discrete_score (0/1)
# date <- end_time, converted to Unix seconds (UTC); left NA if unparseable
irw <- df %>%
  mutate(
    parsed_time = ymd_hms(end_time, tz = "UTC")   # handles both
    # "...+00" and
    # "....ddd+00" formats
  ) %>%
  transmute(
    id   = user_id,
    item = problem_id,
    resp = as.integer(discrete_score),
    date = as.numeric(parsed_time)   # kept numeric (not integer) to avoid
    # 32-bit overflow on later timestamps
  )

cat("Rows with missing date:", sum(is.na(irw$date)), "\n")
cat("Final table:", nrow(irw), "rows x", ncol(irw), "columns\n")

# ---- 5. Write cleaned table ---------------------------------------------------
write_csv(irw, output_path)
cat("Wrote:", output_path, "\n")