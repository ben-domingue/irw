## dscore_*_weber_2019: the GCDG child-development data behind the D-score.
## Weber et al. (2019), BMJ Global Health 4(6):e001724. Source files: the ten
## gcdg_*.txt files in github.com/D-score/childdevdata/tree/master/data-raw/data
## (CC BY 4.0), placed next to this script. One row per child visit (subjid x
## agedays); one table per instrument.
##
## Columns
## - agedays: the child's age in days AT THIS VISIT (#2354). Response-level, not
##   cov_, because it varies within a child across visits. Earlier versions used
##   it only to order visits and then dropped it, so no table had age at
##   measurement, which a D-score analysis is anchored on. It is empty where
##   the source has no age for the visit (5,119 Bayley rows / 127 children,
##   1,236 Dutch / 184, 29 Vineland / 1).
## - cov_gagebrth is gestational age at BIRTH (weeks), not age at assessment.
## - wave: the visit's rank within the child (1, 2, ...), empty for a child
##   with one visit. A rank carries no interval information; use agedays.
## - itemcov_difficulty: tau from the dscore package's itembank (key
##   "gsed2406"), looked up by item name. It is not the Weber 2019 estimates for
##   these data, and it is empty for items the key does not cover (all of
##   Battelle, which the itembank lacks, so that table has no such column).
##   Built with dscore 1.9.0 (CRAN archive), whose default key is gsed2406.
##   Pinning the key is not enough on its own: dscore 2.0 defaults to gsed2510,
##   which covers fewer of these items, and its gsed2406 moves the tau of 65
##   Bayley-III (by3*) items, fills 87 and drops 2. Rerunning under 2.0 would
##   silently change itemcov_difficulty, so install 1.9.0 to reproduce it.
##
## Unadministered cells are dropped (#2355). Each source file is wide over
## every instrument's items, so pivoting without dropping NA shipped every
## unadministered child x item cell as a null-resp row: 83% of denver's rows,
## 90% of bayley's. Missing values are written as empty cells, not "NA".

setwd(dirname(rstudioapi::getActiveDocumentContext()$path)) 
rm(list = ls ())

library(tidyverse)
library(haven)
library(stringr)
DSCORE_KEY <- "gsed2406"

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
    agedays,
    all_of(item_names)
  )

df_long <- df %>%
  pivot_longer(
    cols = all_of(item_names),
    names_to = "item",
    values_to = "resp",
    values_drop_na = TRUE
  )

# Bayley
cohort_bayley <- c("GCDG-CHL-1", "GCDG-CHN", "GCDG-COL-LT42M", "GCDG-COL-LT45M", "GCDG-ZAF")
df_bayley <- df_long %>%
  filter(cov_cohort %in% cohort_bayley, str_detect(item, "^by1|^by3"))
write_csv(df_bayley, "dscore_bayley_weber_2019.csv", na = "")

# ASQ (Ages & Stages Questionnaires)
df_asq <- df_long %>%
  filter(cov_cohort == "GCDG-COL-LT42M", str_starts(item, "aqi"))
df_asq <- df_asq %>%
  select(-wave)
write_csv(df_asq, "dscore_asq_weber_2019.csv", na = "")

# Battelle
df_battelle <- df_long %>%
  filter(cov_cohort == "GCDG-COL-LT42M", str_starts(item, "bat"))
df_battelle <- df_battelle %>%
  select(-wave)
write_csv(df_battelle, "dscore_battelle_weber_2019.csv", na = "")

# Denver
df_denver <- df_long %>%
  filter(cov_cohort == "GCDG-COL-LT42M", str_starts(item, "den"))
df_denver <- df_denver %>%
  select(-wave)
write_csv(df_denver, "dscore_denver_weber_2019.csv", na = "")

# WHO Motor Development Milestones
df_mds <- df_long %>%
  filter(cov_cohort == "GCDG-COL-LT42M", str_starts(item, "mds"))
df_mds <- df_mds %>%
  select(-wave)
write_csv(df_mds, "dscore_mds_weber_2019.csv", na = "")

# Barrera Moncada
df_barrera <- df_long %>%
  filter(cov_cohort == "GCDG-ECU", str_starts(item, "bar"))
df_barrera <- df_barrera %>%
  select(-wave)
write_csv(df_barrera, "dscore_barrera_weber_2019.csv", na = "")

# Griffiths
cohort_griffiths <- c("GCDG-JAM-LBW", "GCDG-JAM-STUNTED", "GCDG-ZAF")
df_griffiths <- df_long %>%
  filter(cov_cohort %in% cohort_griffiths, str_starts(item, "gri"))
write_csv(df_griffiths, "dscore_griffiths_weber_2019.csv", na = "")

# MacArthur CDI
df_macarthur <- df_long %>%
  filter(cov_cohort == "GCDG-MDG", str_starts(item, "mac"))
df_macarthur <- df_macarthur %>%
  select(-wave)
write_csv(df_macarthur, "dscore_macarthur_weber_2019.csv", na = "")

# Pegboard
df_peg <- df_long %>%
  filter(cov_cohort == "GCDG-MDG", str_starts(item, "peg"))
df_peg <- df_peg %>%
  select(-wave)
write_csv(df_peg, "dscore_pegboard_weber_2019.csv", na = "")

# Stanford Binet
df_sbi <- df_long %>%
  filter(cov_cohort == "GCDG-MDG", str_starts(item, "sbi"))
df_sbi <- df_sbi %>%
  select(-wave)
write_csv(df_sbi, "dscore_sbi_weber_2019.csv", na = "")

# Dutch (Van Wiechenschema)
df_dutch <- df_long %>%
  filter(cov_cohort == "GCDG-NLD-SMOCC", str_starts(item, "ddi"))
write_csv(df_dutch, "dscore_dutch_weber_2019.csv", na = "")

# Vineland
df_vineland <- df_long %>%
  filter(cov_cohort == "GCDG-ZAF", str_starts(item, "vin"))
write_csv(df_vineland, "dscore_vineland_weber_2019.csv", na = "")


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
tau_bayley <- get_tau(key = DSCORE_KEY, items = df_bayley$item)
df_bayley <- df_bayley %>%
  mutate(itemcov_difficulty = unname(tau_bayley[item]))
write_csv(df_bayley, "dscore_bayley_weber_2019.csv", na = "")

df_asq <- read_csv("dscore_asq_weber_2019.csv") #asq
tau_asq <- get_tau(key = DSCORE_KEY, items = df_asq$item)
df_asq <- df_asq %>%
  mutate(itemcov_difficulty = unname(tau_asq[item]))
write_csv(df_asq, "dscore_asq_weber_2019.csv", na = "")

df_denver <- read_csv("dscore_denver_weber_2019.csv") #denver
tau_denver <- get_tau(key = DSCORE_KEY, items = df_denver$item)
df_denver <- df_denver %>%
  mutate(itemcov_difficulty = unname(tau_denver[item]))
write_csv(df_denver, "dscore_denver_weber_2019.csv", na = "")

df_mds <- read_csv("dscore_mds_weber_2019.csv") #WHO Motor Development Milestones
tau_mds <- get_tau(key = DSCORE_KEY, items = df_mds$item)
df_mds <- df_mds %>%
  mutate(itemcov_difficulty = unname(tau_mds[item]))
write_csv(df_mds, "dscore_mds_weber_2019.csv", na = "")

df_barrera <- read_csv("dscore_barrera_weber_2019.csv") #Barrera Moncada
tau_barrera <- get_tau(key = DSCORE_KEY, items = df_barrera$item)
df_barrera <- df_barrera %>%
  mutate(itemcov_difficulty = unname(tau_barrera[item]))
write_csv(df_barrera, "dscore_barrera_weber_2019.csv", na = "")

df_griffiths <- read_csv("dscore_griffiths_weber_2019.csv") #Griffiths
tau_griffiths <- get_tau(key = DSCORE_KEY, items = df_griffiths$item)
df_griffiths <- df_griffiths %>%
  mutate(itemcov_difficulty = unname(tau_griffiths[item]))
write_csv(df_griffiths, "dscore_griffiths_weber_2019.csv", na = "")

df_macarthur <- read_csv("dscore_macarthur_weber_2019.csv") #MacArthur CDI
tau_macarthur <- get_tau(key = DSCORE_KEY, items = df_macarthur$item)
df_macarthur <- df_macarthur %>%
  mutate(itemcov_difficulty = unname(tau_macarthur[item]))
write_csv(df_macarthur, "dscore_macarthur_weber_2019.csv", na = "")

df_peg <- read_csv("dscore_pegboard_weber_2019.csv") #Pegboard
tau_peg <- get_tau(key = DSCORE_KEY, items = df_peg$item)
df_peg <- df_peg %>%
  mutate(itemcov_difficulty = unname(tau_peg[item]))
write_csv(df_peg, "dscore_pegboard_weber_2019.csv", na = "")

df_sbi <- read_csv("dscore_sbi_weber_2019.csv") #Stanford Binet
tau_sbi <- get_tau(key = DSCORE_KEY, items = df_sbi$item)
df_sbi <- df_sbi %>%
  mutate(itemcov_difficulty = unname(tau_sbi[item]))
write_csv(df_sbi, "dscore_sbi_weber_2019.csv", na = "")

df_dutch <- read_csv("dscore_dutch_weber_2019.csv") #Dutch (Van Wiechenschema)
tau_dutch <- get_tau(key = DSCORE_KEY, items = df_dutch$item)
df_dutch <- df_dutch %>%
  mutate(itemcov_difficulty = unname(tau_dutch[item]))
write_csv(df_dutch, "dscore_dutch_weber_2019.csv", na = "")

df_vineland <- read_csv("dscore_vineland_weber_2019.csv") #Vineland
tau_vineland <- get_tau(key = DSCORE_KEY, items = df_vineland$item)
df_vineland <- df_vineland %>%
  mutate(itemcov_difficulty = unname(tau_vineland[item]))
write_csv(df_vineland, "dscore_vineland_weber_2019.csv", na = "")
