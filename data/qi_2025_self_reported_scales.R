# IRW processing script: Qi et al. (2025) self-reported scales
#
# Source data:
#   https://osf.io/3h95f/
#   https://doi.org/10.17605/OSF.IO/3H95F
# Source file:
#   Self_bias_dataset/0.Self_reported_scales/Scales.xlsx
#   SHA-256: 895fbd26e261c6439b291b6339c87d2dc346eedf84525b2573efe31f2c7ec05a
# Reference:
#   Qi, Y., Zou, F., Chau, X. Y., Zhou, M., Wang, F., & Sui, J. (2025).
#   A Comprehensive Dataset for Investigating the Structure of Self-Bias.
#   Scientific Data, 12, 1755.
#   https://doi.org/10.1038/s41597-025-06035-z
# Original data license:
#   CC BY 4.0, as stated in the article's Data Records section.
#
# Scope:
#   This script processes only the self-reported scales in Scales.xlsx.
#   It does not process the ten experimental-task folders.
#
# Processing decisions:
#   - Preserve original item identifiers and response values.
#   - Do not reverse-score any items.
#   - Exclude all computed dimension/scale mean columns at the far right.
#   - Rename ID, sex, and age to id, cov_gender, and cov_age.
#   - Drop only missing item responses (the source workbook currently has none).
#
# Usage:
#   Rscript qi_2025_self_reported_scales.R [input_xlsx] [output_dir] [qa_dir]
#
# With no arguments, paths are resolved relative to this script:
#   input:  ../raw/Scales.xlsx
#   output: ../output
#   QA:     ../qa

suppressPackageStartupMessages({
  library(dplyr)
  library(purrr)
  library(readr)
  library(readxl)
  library(tidyr)
})

script_arg <- grep("^--file=", commandArgs(), value = TRUE)
script_dir <- if (length(script_arg) == 1L) {
  dirname(normalizePath(sub("^--file=", "", script_arg), mustWork = TRUE))
} else {
  normalizePath(getwd(), mustWork = TRUE)
}

args <- commandArgs(trailingOnly = TRUE)
input_path <- if (length(args) >= 1L) {
  args[[1]]
} else {
  file.path(script_dir, "..", "raw", "Scales.xlsx")
}
output_dir <- if (length(args) >= 2L) {
  args[[2]]
} else {
  file.path(script_dir, "..", "output")
}
qa_dir <- if (length(args) >= 3L) {
  args[[3]]
} else {
  file.path(script_dir, "..", "qa")
}

if (!file.exists(input_path)) {
  stop("Input workbook not found: ", input_path)
}

dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)
dir.create(qa_dir, recursive = TRUE, showWarnings = FALSE)

numbered_items <- function(prefix, n) {
  paste0(prefix, seq_len(n))
}

# One IRW table per source instrument. PANAS retains its positive- and
# negative-affect items together because they belong to the same instrument;
# SWLS is kept separate.
scale_specs <- list(
  qi_2025_big_five = list(
    label = "Big Five Inventory-2",
    items = numbered_items("BFP_", 60),
    valid_min = 1,
    valid_max = 5
  ),
  qi_2025_self_construal = list(
    label = "Self-Construal Scale",
    items = numbered_items("SC_", 30),
    valid_min = 1,
    valid_max = 7
  ),
  qi_2025_individualism_collectivism = list(
    label = "Individualism-Collectivism Scale",
    items = numbered_items("IC_", 32),
    valid_min = 1,
    valid_max = 7
  ),
  qi_2025_self_esteem = list(
    label = "Rosenberg Self-Esteem Scale",
    items = numbered_items("Esteem_", 10),
    valid_min = 1,
    valid_max = 4
  ),
  qi_2025_panas = list(
    label = "Positive and Negative Affect Schedule",
    items = c(numbered_items("PA_", 9), numbered_items("NA_", 9)),
    valid_min = 1,
    valid_max = 5
  ),
  qi_2025_swls = list(
    label = "Satisfaction With Life Scale",
    items = numbered_items("SWLS_", 5),
    valid_min = 1,
    valid_max = 7
  ),
  qi_2025_dark_triad = list(
    label = "Short Dark Triad",
    items = numbered_items("DT_", 27),
    valid_min = 1,
    valid_max = 5
  ),
  qi_2025_modesty = list(
    label = "Modest Responding Scale",
    items = numbered_items("Modesty_", 21),
    valid_min = 1,
    valid_max = 7
  ),
  qi_2025_self_concept_clarity = list(
    label = "Self-Concept Clarity Scale",
    items = numbered_items("SCC_", 12),
    valid_min = 1,
    valid_max = 5
  )
)

raw <- read_excel(
  input_path,
  sheet = "Summary_of_data",
  # The source workbook has one intentionally blank separator column before
  # the computed score columns. Unique name repair makes that column harmless
  # while preserving every meaningful source item name.
  .name_repair = "unique_quiet"
)

required_person_columns <- c("ID", "sex", "age")
missing_person_columns <- setdiff(required_person_columns, names(raw))
if (length(missing_person_columns) > 0L) {
  stop(
    "Missing required participant column(s): ",
    paste(missing_person_columns, collapse = ", ")
  )
}

if (anyNA(raw$ID)) {
  stop("ID contains missing values.")
}
if (n_distinct(raw$ID) != nrow(raw)) {
  stop("ID is not unique across participant rows.")
}

expected_item_columns <- unlist(
  map(scale_specs, "items"),
  use.names = FALSE
)
missing_item_columns <- setdiff(expected_item_columns, names(raw))
if (length(missing_item_columns) > 0L) {
  stop(
    "Missing expected item column(s): ",
    paste(missing_item_columns, collapse = ", ")
  )
}
if (anyDuplicated(expected_item_columns)) {
  stop("An item column is assigned to more than one output table.")
}

column_map <- imap_dfr(scale_specs, function(spec, table_name) {
  tibble(
    table = table_name,
    instrument = spec$label,
    source_column = spec$items,
    item = spec$items,
    item_order = seq_along(spec$items),
    valid_min = spec$valid_min,
    valid_max = spec$valid_max
  )
})

write_csv(
  column_map,
  file.path(qa_dir, "qi_2025_self_reported_scales_column_map.csv")
)

process_scale <- function(spec, table_name) {
  item_cols <- spec$items

  source_slice <- raw |>
    transmute(
      id = ID,
      cov_gender = sex,
      cov_age = age,
      across(all_of(item_cols))
    )

  expected_nonmissing <- sum(!is.na(source_slice[item_cols]))

  long <- source_slice |>
    pivot_longer(
      cols = all_of(item_cols),
      names_to = "item",
      values_to = "resp"
    )

  original_nonmissing <- !is.na(long$resp)
  numeric_resp <- suppressWarnings(as.numeric(long$resp))
  newly_missing <- original_nonmissing & is.na(numeric_resp)
  if (any(newly_missing)) {
    bad_values <- unique(long$resp[newly_missing])
    stop(
      table_name,
      " contains non-numeric response value(s): ",
      paste(head(bad_values, 10L), collapse = ", ")
    )
  }

  long <- long |>
    mutate(resp = numeric_resp) |>
    filter(!is.na(resp)) |>
    select(id, item, resp, cov_gender, cov_age)

  if (nrow(long) != expected_nonmissing) {
    stop(table_name, ": row count changed unexpectedly during conversion.")
  }
  if (anyDuplicated(long[c("id", "item")])) {
    stop(table_name, ": duplicate id-item pairs detected.")
  }
  if (!identical(names(long), c("id", "item", "resp", "cov_gender", "cov_age"))) {
    stop(table_name, ": output schema or column order is incorrect.")
  }
  if (n_distinct(long$id) != n_distinct(raw$ID)) {
    stop(table_name, ": participant count differs from the source workbook.")
  }
  if (n_distinct(long$item) != length(item_cols)) {
    stop(table_name, ": item count differs from the explicit scale mapping.")
  }

  invalid_range <- long |>
    filter(resp < spec$valid_min | resp > spec$valid_max)
  if (nrow(invalid_range) > 0L) {
    stop(
      table_name,
      ": responses found outside the documented ",
      spec$valid_min,
      "-",
      spec$valid_max,
      " scale."
    )
  }
  if (any(abs(long$resp - round(long$resp)) > .Machine$double.eps^0.5)) {
    stop(table_name, ": non-integer responses found on an ordinal item scale.")
  }

  output_path <- file.path(output_dir, paste0(table_name, ".csv"))
  write_csv(long, output_path, na = "")

  tibble(
    table = table_name,
    instrument = spec$label,
    output_file = basename(output_path),
    rows = nrow(long),
    ids = n_distinct(long$id),
    items = n_distinct(long$item),
    missing_responses_dropped = length(item_cols) * nrow(raw) - nrow(long),
    resp_min = min(long$resp),
    resp_max = max(long$resp),
    response_values = paste(sort(unique(long$resp)), collapse = "|"),
    duplicate_id_item_pairs = sum(duplicated(long[c("id", "item")])),
    schema = paste(names(long), collapse = "|"),
    qa_status = "PASS"
  )
}

qa_summary <- imap_dfr(scale_specs, process_scale)

write_csv(
  qa_summary,
  file.path(qa_dir, "qi_2025_self_reported_scales_qa.csv")
)

cat(
  "\nQi et al. (2025) self-reported scales processed successfully.\n",
  "Input: ", normalizePath(input_path, mustWork = TRUE), "\n",
  "Participants: ", n_distinct(raw$ID), "\n",
  "Gender codes: 1 = male; 2 = female (preserved from source).\n",
  "Age range: ", min(raw$age, na.rm = TRUE), "-", max(raw$age, na.rm = TRUE), "\n",
  "Output directory: ", normalizePath(output_dir, mustWork = TRUE), "\n\n",
  sep = ""
)

print(
  qa_summary |>
    select(table, rows, ids, items, resp_min, resp_max, qa_status),
  n = Inf
)
