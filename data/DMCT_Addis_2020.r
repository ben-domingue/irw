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
# resp is per-trial accuracy (0/1) from the long-format MC_acc, one row per
# participant x stimulus; item MCn_acc is stimulus MentalCompTask.thisIndex n-1.
# The wide MC1_acc..MC44_acc columns are NOT accuracy: each is constant across
# all 92 participants and equals the stimulus's Korrekt column (which of the two
# alternatives is correct), i.e. the answer key. The table shipped those until
# the 2026-09-27 rebuild (irw#2408), so every item then had a single value.
# rt is the participant's raw MCnrt (seconds) for the same stimulus; the wide rt
# columns are per participant and follow thisIndex (they equal MC_rt on 95% of
# trials; MC_rt itself is the deposit's trimmed copy, floored at 0.4 s).
# Source is Suggate (2024), Behav Res Methods 56:8658-8676, despite the name.
mct_long <- read_sav("Data_merged_multilevel_trimmed.sav") |>
  as.data.frame()
mct_long$n <- mct_long$MentalCompTask.thisIndex + 1
stopifnot(!anyDuplicated(mct_long[, c("Participant_Code", "n")]))
mct_rt_wide <- study1_df |>
  select(id, matches("^MC[0-9]+rt$"))
mct_rt_df <- pivot_longer(mct_rt_wide, cols=-id, names_to="n", values_to="rt")
mct_rt_df$n <- as.integer(sub("^MC([0-9]+)rt$", "\\1", mct_rt_df$n))
mct_df <- data.frame(id=mct_long$Participant_Code,
                     item=paste0("MC", mct_long$n, "_acc"),
                     resp=as.integer(mct_long$MC_acc),
                     n=mct_long$n)
mct_df <- left_join(mct_df, mct_rt_df, by=c("id", "n")) |>
  select(id, item, resp, rt)
mct_df$rt <- as.numeric(mct_df$rt)

save(mct_df, file="DMCT_Addis_2020_MCT.Rdata")
write.csv(mct_df, "DMCT_Addis_2020_MCT.csv", row.names=FALSE)

# ------ Process SUIS Data ------
study1_suis_df <- study1_df |>
  select(id, starts_with("SUIS"), -SUIS_total)
study1_suis_df <- pivot_longer(study1_suis_df, cols=-id, names_to="item", values_to="resp")

save(study1_suis_df, file="DMCT_Addis_2020_SUIS.Rdata")
write.csv(study1_suis_df, "DMCT_Addis_2020_SUIS.csv", row.names=FALSE)