# Paper: https://osf.io/preprints/psyarxiv/s32zb
# Data: https://osf.io/yw7t2/?view_only=
library(dplyr)
library(tidyr)
library(haven)

# ------ Process Dataset 1 ------
study1_df <- read_dta("./2019_07_07_PoB_OSF.dta")
colnames(study1_df) <- gsub("\\s*\\(.*\\)", "", colnames(study1_df)) # Remove column labels
study1_df <- lapply(study1_df, function(x) { attr(x, "label") <- NULL; x })
study1_df <- as.data.frame(study1_df)

study1_df <- study1_df |>
  select(-qualtrics, -mturk, -yearsed, -p_ed, -spansurv, -female, -bornUS, 
         -yrs_us, -imm_age, -region, -KIDItotalpts, -femchild, 
         -p1spks_ch, -p2spks_ch, -parent, -L1EngNoL2, -p1spksch_imputed, 
         -L1_derived, -L2_derived, -race) |>
  rename(age=p_age)
study1_df <- pivot_longer(study1_df, cols=-c(id, age), names_to="item", values_to="resp")

# ------ Process Dataset 2 ------
study2_df <- read_dta("./PoB_TPS_2022_OSF_keyvars.dta")
colnames(study2_df) <- gsub("\\s*\\(.*\\)", "", colnames(study2_df)) # Remove column labels
study2_df <- lapply(study2_df, function(x) { attr(x, "label") <- NULL; x })
study2_df <- as.data.frame(study2_df)

study2_df <- study2_df |>
  select(-yearsed, -spansurv, -female, -bornUS, -region, -zipcode,
         -homeusage, -langback, -perclote_2016, -logplote_2016, -mturk, 
         -meanPOBp_6item, -age_cat, -tellstories, -talkchild, -sing, -read,
         -MUNE_reads_dich, -RQ2_sample, -meanPOB10) |>
  rename(id=ResponseID, age=p_age)
study2_df <- pivot_longer(study2_df, cols=-c(id, age), names_to="item", values_to="resp")

# ------ Process Merged Datasets
study1_df$id <- as.character(study1_df$id)
df <- bind_rows(
  study1_df %>% mutate(group = "Study 1"),
  study2_df %>% mutate(group = "Study 2")
)

save(df, file="PBS_Surrain_2019_PoB.Rdata")
write.csv(df, "PBS_Surrain_2019_PoB.csv", row.names=FALSE)
