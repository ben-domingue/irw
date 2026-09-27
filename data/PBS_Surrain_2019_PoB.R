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

# ------ Dataset 2 is NOT included (irw#2409) ------
# PoB_TPS_2022_OSF_keyvars.dta (n=319) was pooled here as group "Study 2" until
# the 2026-09-27 rebuild. It is not a second sample: aligned by item content,
# every one of its 319 rows matches exactly one Study 1 respondent on age, the
# ten PoB items and the six shared POBplus items, so those people appeared twice
# under unlinked ids. It also numbers the final 10-item PoB form 1..10, while
# Study 1 keeps the dropped reverse items (PoB3R/5R/11R) in its numbering, so
# PoB3-PoB10 meant different questions in the two groups (Study 2 PoB3..PoB10 =
# Study 1 PoB4, 6, 7, 8, 9, 10, 12, 13). The table is Study 1 only, and `group`
# (now constant) is dropped.
# PoB3R, PoB5R, PoB11R, POBplus_5R and POBplus_7R are stored reverse-scored, as
# deposited.
df <- study1_df
df$id <- as.character(df$id)

save(df, file="PBS_Surrain_2019_PoB.Rdata")
write.csv(df, "PBS_Surrain_2019_PoB.csv", row.names=FALSE, na="")  # empty, not literal NA (#2029)
