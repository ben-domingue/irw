# Paper
# Data: https://openpsychometrics.org/_rawdata/
library(haven)
library(dplyr)
library(tidyr)

process_hexaco_data <- function(df, prefix, output_basename = "hexaco_ashton_2014") {
  # Select columns starting with the given prefix, plus cov_country and id
  df <- df |>
    select(starts_with(prefix), cov_country, id)
  
  # Reshape to long format and convert 0s to NA
  df <- pivot_longer(df, cols = -c(cov_country, id),
                     names_to = "item", values_to = "resp") |>
    mutate(resp = ifelse(resp == 0, NA, resp))
  
  # Define output filenames
  rdata_filename <- paste0(output_basename, "_", tolower(prefix), ".Rdata")
  csv_filename <- paste0(output_basename, "_", tolower(prefix), ".csv")
  
  # Save the data
  save(df, file = rdata_filename)
  write.csv(df, csv_filename, row.names = FALSE)
  print(table(df$resp))
  
  # Return the processed dataframe
  return(df)
}

df <- read.csv("data.csv", sep = "\t")
df$id <- seq_len(nrow(df))
df <- df |>
  rename(cov_country=country) |>
  select(-elapse)

# ---------- Honesty-Humility Scale ----------
process_hexaco_data(df, prefix="H")

# ---------- Emotionality (E) Facets Scale ----------
process_hexaco_data(df, prefix="E")

# ---------- Extraversion (X) Facets Scale ----------
process_hexaco_data(df, prefix="X")

# ---------- Agreeableness (A) Facets Scale ----------
process_hexaco_data(df, prefix="A")

# --------- Conscientiousness (C) Facets Scale ----------
process_hexaco_data(df, prefix="C")

# ---------- Openness to Experience (O) Facets Scale ----------
process_hexaco_data(df, prefix="O")
