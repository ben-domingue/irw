setwd(dirname(rstudioapi::getActiveDocumentContext()$path)) 
rm(list = ls ())
library(tidyverse)
library(haven)
library(stringr)

file_list <- list.files(pattern = "\\.txt$")
data_list <- lapply(file_list, function(file) {
  df_temp <- read.delim(file, header = TRUE, sep = "\t", stringsAsFactors = FALSE)
  df_temp$cohort_file <- file
  return(df_temp)
})
df <- bind_rows(data_list)
# Add 'wave' column
df <- df %>%
  group_by(subjid) %>%
  arrange(agedays, .by_group = TRUE) %>%
  mutate(wave = if(n() > 1) row_number() else NA_integer_) %>%
  ungroup()

item_prefixes <- c("by1", "by3", "aqi", "bat", "den", "mds", 
                   "bar", "gri", "mac", "peg", "sbi", "ddi", 
                   "sgr", "vin")
item_names <- names(df)[str_detect(names(df), paste0("^(", paste(item_prefixes, collapse = "|"), ")"))]

df <- df %>%
  select(
    id = subjid,
    cov_country = ctrycd,
    cov_cohort = cohort,
    cov_gender = sex,
    cov_gagebrth = gagebrth,
    wave,
    all_of(item_names)
  )

df_long <- df %>%
  pivot_longer(
    cols = all_of(item_names),
    names_to = "item",
    values_to = "resp"
  )

# Bayley
cohort_bayley <- c("GCDG-CHL-1", "GCDG-CHN", "GCDG-COL-LT42M", "GCDG-COL-LT45M", "GCDG-ZAF")
df_bayley <- df_long %>%
  filter(cov_cohort %in% cohort_bayley, str_detect(item, "^by1|^by3"))
write_csv(df_bayley, "dscore_bayley_weber_2019.csv")

# ASQ (Ages & Stages Questionnaires)
df_asq <- df_long %>%
  filter(cov_cohort == "GCDG-COL-LT42M", str_starts(item, "aqi"))
df_asq <- df_asq %>%
  select(-wave)
write_csv(df_asq, "dscore_asq_weber_2019.csv")

# Battelle
df_battelle <- df_long %>%
  filter(cov_cohort == "GCDG-COL-LT42M", str_starts(item, "bat"))
df_battelle <- df_battelle %>%
  select(-wave)
write_csv(df_battelle, "dscore_battelle_weber_2019.csv")

# Denver
df_denver <- df_long %>%
  filter(cov_cohort == "GCDG-COL-LT42M", str_starts(item, "den"))
df_denver <- df_denver %>%
  select(-wave)
write_csv(df_denver, "dscore_denver_weber_2019.csv")

# WHO Motor Development Milestones
df_mds <- df_long %>%
  filter(cov_cohort == "GCDG-COL-LT42M", str_starts(item, "mds"))
df_mds <- df_mds %>%
  select(-wave)
write_csv(df_mds, "dscore_mds_weber_2019.csv")

# Barrera Moncada
df_barrera <- df_long %>%
  filter(cov_cohort == "GCDG-ECU", str_starts(item, "bar"))
df_barrera <- df_barrera %>%
  select(-wave)
write_csv(df_barrera, "dscore_barrera_weber_2019.csv")

# Griffiths
cohort_griffiths <- c("GCDG-JAM-LBW", "GCDG-JAM-STUNTED", "GCDG-ZAF")
df_griffiths <- df_long %>%
  filter(cov_cohort %in% cohort_griffiths, str_starts(item, "gri"))
write_csv(df_griffiths, "dscore_griffiths_weber_2019.csv")

# MacArthur CDI
df_macarthur <- df_long %>%
  filter(cov_cohort == "GCDG-MDG", str_starts(item, "mac"))
df_macarthur <- df_macarthur %>%
  select(-wave)
write_csv(df_macarthur, "dscore_macarthur_weber_2019.csv")

# Pegboard
df_peg <- df_long %>%
  filter(cov_cohort == "GCDG-MDG", str_starts(item, "peg"))
df_peg <- df_peg %>%
  select(-wave)
write_csv(df_peg, "dscore_pegboard_weber_2019.csv")

# Stanford Binet
df_sbi <- df_long %>%
  filter(cov_cohort == "GCDG-MDG", str_starts(item, "sbi"))
df_sbi <- df_sbi %>%
  select(-wave)
write_csv(df_sbi, "dscore_sbi_weber_2019.csv")

# Dutch (Van Wiechenschema)
df_dutch <- df_long %>%
  filter(cov_cohort == "GCDG-NLD-SMOCC", str_starts(item, "ddi"))
write_csv(df_dutch, "dscore_dutch_weber_2019.csv")

# Vineland
df_vineland <- df_long %>%
  filter(cov_cohort == "GCDG-ZAF", str_starts(item, "vin"))
write_csv(df_vineland, "dscore_vineland_weber_2019.csv")
