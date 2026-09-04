# Paper: https://www.sciencedirect.com/science/article/pii/S002209652400153X?casa_token=frUv3Kl3eTIAAAAA:YYuVvzzbk5DFpvFlUAO2XvfWd3qnt6ToOT46ExDaabGezuZsA4-MWgt_stLyebZaZ6EUrsIq
# Data: https://osf.io/sa87b/
library(haven)
library(dplyr)
library(tidyr)

df <- read_sav("data-3.sav")
df <- df |>
  rename(id = number)
df <- df[!is.na(df$child_age_in_months) & !is.na(df$c_PSIAT), ]
df[] <- lapply(df, function(col) { # Remove column labels for each column
  attr(col, "label") <- NULL
  return(col)
})

# `number` is labelled "Child's & parent's number" in the .sav: it identifies a
# child-caregiver dyad, not a respondent. One dyad that survives the filter
# (id 1) carries two caregiver rows -- different p_sex and different p_age, so
# two different people rather than a duplicated record -- and its child columns
# are byte-identical across the two, the same child copied onto both rows.
#
# So the id means different things in the two families of tables below, and the
# repeats need opposite treatment (irw#1842): the parent-report scales are two
# respondents and must be told apart, the child measures are one measurement
# recorded twice. Deduping the parent scales would delete a real caregiver;
# namespacing the child measures would invent a second child.
parent_df <- df |>
  group_by(id) |>
  mutate(id = if (n() > 1) paste0(id, "_", row_number()) else as.character(id)) |>
  ungroup()
# The child frames are deduped at the point of use, after the item columns are
# selected -- distinct() there only collapses rows that agree on every item, so
# a dyad whose two rows ever disagreed would survive rather than be silently
# halved.

# ------ Process PRD Dataset ------
prd_df <- parent_df |>
  select(id, starts_with("p_personal_rel_dep"), -ends_with("R"))
prd_df <- pivot_longer(prd_df, cols=-id, names_to="item", values_to="resp")

save(prd_df, file="FEDSP_Trzcinska_2023_PRD.Rdata")
write.csv(prd_df, "FEDSP_Trzcinska_2023_PRD.csv", row.names=FALSE)

# ------ Process PSPCSA Dataset ------
pspcsa_df <- df |>
  select(id, starts_with("c_PSPCSA"), -c_PSPCSA) |>
  distinct()
pspcsa_test_df <- pspcsa_df |>
  select(-ends_with("r"))
pspcsa_retest_df <- pspcsa_df |>
  select(id, ends_with("r"))
colnames(pspcsa_retest_df) <- gsub("r", "", colnames(pspcsa_retest_df))

pspcsa_test_df <- pivot_longer(pspcsa_test_df, cols=-id, names_to="item", values_to="resp")
pspcsa_retest_df <- pivot_longer(pspcsa_retest_df, cols=-id, names_to="item", values_to="resp")
pspcsa_test_df$wave <- 0
pspcsa_retest_df$wave <- 1

pspcsa_df <- rbind(pspcsa_test_df, pspcsa_retest_df)

save(pspcsa_df, file="FEDSP_Trzcinska_2023_PSPCSA.Rdata")
write.csv(pspcsa_df, "FEDSP_Trzcinska_2023_PSPCSA.csv", row.names=FALSE)

# ------ Process SMSD Dataset ------
smsd_df <- parent_df |>
  select(id, starts_with("p_SMSD"), -ends_with("R"), -ends_with("total"))
smsd_df <- pivot_longer(smsd_df, cols=-id, names_to="item", values_to="resp")

save(smsd_df, file="FEDSP_Trzcinska_2023_SMSD.Rdata")
write.csv(smsd_df, "FEDSP_Trzcinska_2023_SMSD.csv", row.names=FALSE)

# ------ Process MonKnow Dataset ------
monknow_df <- df |>
  select(id, starts_with("c_MonKnow_")) |>
  distinct()
monknow_df <- pivot_longer(monknow_df, cols=-id, names_to="item", values_to="resp")

save(monknow_df, file="FEDSP_Trzcinska_2023_MonKonw.Rdata")
write.csv(monknow_df, "FEDSP_Trzcinska_2023_MonKnow.csv", row.names=FALSE)
