# Process Chen et al. (2022) mental health dataset for IRW
# Dataset: Mental health dataset of college students during COVID-19
# Source: Science Data Bank
# DOI: 10.57760/sciencedb.000115.00089
# License: CC BY-NC 4.0
#
# This script reads the original SPSS file and creates an IRW-style
# main response table with person-level covariates merged into the table
# using the cov_ prefix.

library(haven)
library(dplyr)
library(readr)

# 1. Read raw SPSS file
raw_data <- read_sav("mental_health_covid19.sav")

# Remove SPSS value labels before reshaping to avoid conflicting labels
raw_data <- haven::zap_labels(raw_data)

# 2. Inspect raw data
print(dim(raw_data))
print(names(raw_data))

# 3. Define item-response variables
sasc_items <- paste0("SASC", sprintf("%02d", 1:22))
cesd_items <- paste0("CESD", sprintf("%02d", 1:10))
gad_items  <- paste0("GAD", sprintf("%02d", 1:7))

item_vars <- c(sasc_items, cesd_items, gad_items)

# 4. Define person-level covariates
# These are retained in the main table using the cov_ prefix.
covariate_vars <- c(
  "sex",
  "age",
  "region",
  "positive",
  "negative",
  "PSU",
  "Depression",
  "Anxiety"
)

# 5. Check that expected variables exist
expected_vars <- c("ID", covariate_vars, item_vars)
missing_vars <- setdiff(expected_vars, names(raw_data))

if (length(missing_vars) > 0) {
  stop(
    paste(
      "The following expected variables are missing from the raw data:",
      paste(missing_vars, collapse = ", ")
    )
  )
}

# 6. Create processed main table in long format
# Each row is one person-item response.
# ID is renamed to id.
# Person-level variables receive cov_ prefix.
# Item responses are converted to item / resp columns.

# 6. Create a helper function to generate one IRW-style long table per construct
# Each output table keeps person-level covariates using the cov_ prefix.
# Each row is one person-item response.

make_irw_table <- function(data, items, construct_name) {
  data %>%
    select(ID, all_of(covariate_vars), all_of(items)) %>%
    rename(id = ID) %>%
    rename_with(
      .fn = ~ paste0("cov_", .x),
      .cols = all_of(covariate_vars)
    ) %>%
    pivot_longer(
      cols = all_of(items),
      names_to = "item",
      values_to = "resp"
    ) %>%
    mutate(construct = construct_name)
}

# 7. Generate construct-specific tables

sasc_data <- make_irw_table(
  data = raw_data,
  items = sasc_items,
  construct_name = "SASC"
)

cesd_data <- make_irw_table(
  data = raw_data,
  items = cesd_items,
  construct_name = "CESD10"
)

gad_data <- make_irw_table(
  data = raw_data,
  items = gad_items,
  construct_name = "GAD7"
)

# 8. Write construct-specific processed tables

write_csv(sasc_data, "chen_2022_sasc.csv")
write_csv(cesd_data, "chen_2022_cesd.csv")
write_csv(gad_data, "chen_2022_gad.csv")


# 9. Create a simple variable codebook

variable_codebook <- tibble::tibble(
  variable = names(sasc_data),
  role = dplyr::case_when(
    variable == "id" ~ "person_id",
    grepl("^cov_", variable) ~ "person_level_covariate",
    variable == "item" ~ "item_identifier",
    variable == "resp" ~ "item_response",
    variable == "construct" ~ "construct_identifier",
    TRUE ~ "other"
  )
)

write_csv(variable_codebook, "codebook_variables.csv")

# 10. Print output summaries

print(dim(sasc_data))
print(dim(cesd_data))
print(dim(gad_data))

print(names(sasc_data))
print(names(cesd_data))
print(names(gad_data))
