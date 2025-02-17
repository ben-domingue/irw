# Ppaer: https://link.springer.com/article/10.3758/s13428-024-02496-z
# Data: https://osf.io/vf27z/?view_only=43c4db49648f428c914ebdcc4e191f27
library(haven)
library(dplyr)
library(tidyr)

# ---------- Load Study1 Data -----------
study1_df <- read_sav("Data_merged_multilevel_trimmed.sav")
study1_df <- study1_df[!duplicated(study1_df$Participant_Code), ]
study1_df <- study1_df |>
  rename(id=Participant_Code)

# ------ Process PSIQ Data ------
study1_psyq_df <- study1_df |>
  select(id, starts_with("PsiQ"), starts_with("Psy"), -starts_with("PsiQ_"))
study1_psyq_df <- pivot_longer(study1_psyq_df, cols=-id, names_to = "item", values_to = "resp")

save(study1_psyq_df, file="DMCT_Addis_2020_PSYQ.Rdata")
write.csv(study1_psyq_df, "DMCT_Addis_2020_PSYQ.csv", row.names=FALSE)

# ------ Process MCT Data ------
study1_mct_df <- study1_df |>
  select(id, starts_with("MC"), -MC_RT_indMean, -MC_RT_indSD, -MC_acc, -MC_Modality)

mct_acc_df <- study1_mct_df |>
  select(id, ends_with("acc"))
mct_acc_df <- pivot_longer(mct_acc_df, cols=-id, names_to = "item", values_to = "resp")

mct_rt_df <- study1_mct_df |>
  select(id, ends_with("rt"), -MC_rt)
mct_rt_df <- pivot_longer(mct_rt_df, cols=-id, names_to="item", values_to="rt")
mct_rt_df <- mct_rt_df |>
  select(-item, -id)

mct_df <- cbind(mct_acc_df, mct_rt_df)

save(mct_df, file="DMCT_Addis_2020_MCT.Rdata")
write.csv(mct_df, "DMCT_Addis_2020_MCT.csv", row.names=FALSE)

# ------ Process SUIS Data ------
study1_suis_df <- study1_df |>
  select(id, starts_with("SUIS"), -SUIS_total)
study1_suis_df <- pivot_longer(study1_suis_df, cols=-id, names_to="item", values_to="resp")

save(study1_suis_df, file="DMCT_Addis_2020_SUIS.Rdata")
write.csv(study1_suis_df, "DMCT_Addis_2020_SUIS.csv", row.names=FALSE)