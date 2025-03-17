# Paper: https://link.springer.com/article/10.3758/s13428-025-02611-8#Sec15
# Data: https://osf.io/gc8a4/files/osfstorage
library(haven)
library(dplyr)
library(tidyr)

# ---------- Process BDI Data ----------
bdi_df <- read.csv("BDI.csv")
bdi_df <- bdi_df |>
  mutate(id=row_number())
bdi_df <- pivot_longer(bdi_df, cols=-c(id), names_to="item", values_to="resp")

save(bdi_df, file="rrca_mcneish_2025_bdi.Rdata")
write.csv(bdi_df, "rrca_mcneish_2025_bdi.csv", row.names=FALSE)

study2_df <- read.csv("MOTES_Synthetic.csv")
study2_df <- study2_df |>
  mutate(id=row_number())
# ---------- Process Use Data ----------
use_df <- study2_df |>
  select(id, starts_with("Use"))
use_df <- pivot_longer(use_df, cols=-id, names_to="item", values_to="resp")

save(use_df, file="rrca_mcneish_2025_use.Rdata")
write.csv(use_df, "rrca_mcneish_2025_use.csv", row.names=FALSE)

# ---------- Process Example Data ----------
exp_df <- study2_df |>
  select(id, starts_with("Examp"))
exp_df <- pivot_longer(exp_df, cols=-id, names_to="item", values_to="resp")

save(exp_df, file="rrca_mcneish_2025_exp.Rdata")
write.csv(exp_df, "rrca_mcneish_2025_exp.csv", row.names=FALSE)

# ---------- Process Sentence Data ----------
sen_df <- study2_df |>
  select(id, starts_with("Sen"))
sen_df <- pivot_longer(sen_df, cols=-id, names_to="item", values_to="resp")

save(sen_df, file="rrca_mcneish_2025_sen.Rdata")
write.csv(sen_df, "rrca_mcneish_2025_sen.csv", row.names=FALSE)