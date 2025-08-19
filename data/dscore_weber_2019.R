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


##edit to add item difficulties:
         ############## Data Fix (Add column related to item difficulty) ################
library(dscore)
library(tidyverse)
table(builtin_itembank$instrument) # Check itembank and there're no tau values for battelle
#aqi bar by1 by2 by3 cro ddi den dmc ecd gh1 gpa gri gs1 gsd gto iyo kdi mac mds mdt 
#109  67 429  82 409 374 427 279 188  72  55 830 490 186  35 927 318 208  15   4 650 
#mul peg sbi sgr tep vin 
#138   5  34 105 169  93 

df_bayley <- read_csv("dscore_bayley_weber_2019.csv") # bayley
tau_bayley <- get_tau(items = df_bayley$item)
df_bayley <- df_bayley %>%
  mutate(itemcov_difficulty = unname(tau_bayley[item]))
write_csv(df_bayley, "dscore_bayley_weber_2019.csv")

df_asq <- read_csv("dscore_asq_weber_2019.csv") #asq
tau_asq <- get_tau(items = df_asq$item)
df_asq <- df_asq %>%
  mutate(itemcov_difficulty = unname(tau_asq[item]))
write_csv(df_asq, "dscore_asq_weber_2019.csv")

df_denver <- read_csv("dscore_denver_weber_2019.csv") #denver
tau_denver <- get_tau(items = df_denver$item)
df_denver <- df_denver %>%
  mutate(itemcov_difficulty = unname(tau_denver[item]))
write_csv(df_denver, "dscore_denver_weber_2019.csv")

df_mds <- read_csv("dscore_mds_weber_2019.csv") #WHO Motor Development Milestones
tau_mds <- get_tau(items = df_mds$item)
df_mds <- df_mds %>%
  mutate(itemcov_difficulty = unname(tau_mds[item]))
write_csv(df_mds, "dscore_mds_weber_2019.csv")

df_barrera <- read_csv("dscore_barrera_weber_2019.csv") #Barrera Moncada
tau_barrera <- get_tau(items = df_barrera$item)
df_barrera <- df_barrera %>%
  mutate(itemcov_difficulty = unname(tau_barrera[item]))
write_csv(df_barrera, "dscore_barrera_weber_2019.csv")

df_griffiths <- read_csv("dscore_griffiths_weber_2019.csv") #Griffiths
tau_griffiths <- get_tau(items = df_griffiths$item)
df_griffiths <- df_griffiths %>%
  mutate(itemcov_difficulty = unname(tau_griffiths[item]))
write_csv(df_griffiths, "dscore_griffiths_weber_2019.csv")

df_macarthur <- read_csv("dscore_macarthur_weber_2019.csv") #MacArthur CDI
tau_macarthur <- get_tau(items = df_macarthur$item)
df_macarthur <- df_macarthur %>%
  mutate(itemcov_difficulty = unname(tau_macarthur[item]))
write_csv(df_macarthur, "dscore_macarthur_weber_2019.csv")

df_peg <- read_csv("dscore_pegboard_weber_2019.csv") #Pegboard
tau_peg <- get_tau(items = df_peg$item)
df_peg <- df_peg %>%
  mutate(itemcov_difficulty = unname(tau_peg[item]))
write_csv(df_peg, "dscore_pegboard_weber_2019.csv")

df_sbi <- read_csv("dscore_sbi_weber_2019.csv") #Stanford Binet
tau_sbi <- get_tau(items = df_sbi$item)
df_sbi <- df_sbi %>%
  mutate(itemcov_difficulty = unname(tau_sbi[item]))
write_csv(df_sbi, "dscore_sbi_weber_2019.csv")

df_dutch <- read_csv("dscore_dutch_weber_2019.csv") #Dutch (Van Wiechenschema)
tau_dutch <- get_tau(items = df_dutch$item)
df_dutch <- df_dutch %>%
  mutate(itemcov_difficulty = unname(tau_dutch[item]))
write_csv(df_dutch, "dscore_dutch_weber_2019.csv")

df_vineland <- read_csv("dscore_vineland_weber_2019.csv") #Vineland
tau_vineland <- get_tau(items = df_vineland$item)
df_vineland <- df_vineland %>%
  mutate(itemcov_difficulty = unname(tau_vineland[item]))
write_csv(df_vineland, "dscore_vineland_weber_2019.csv")
