# Paper: https://psycnet.apa.org/record/2024-52701-001
# Data: https://osf.io/tj8rh/
library(haven)
library(dplyr)
library(tidyr)
library(foreign)

# ------ Process Dataset 1 ------
df <- read_sav("PTCI_data.sav")
df <- df |>
  select(ID, starts_with("PTCI")) |>
  rename(id = ID)
df[] <- lapply(df, function(col) { # Remove column labels for each column
  attr(col, "label") <- NULL
  return(col)
})
df <- pivot_longer(df, cols=-id, names_to = "item", values_to = "resp")

# ------ Process Dataset 2 ------
df_retest <- read.spss("./PTCI_retest.sav", to.data.frame = TRUE, use.value.labels = FALSE)
df_retest <- df_retest |>
  rename(id=ID_retest) |>
  select(-YN_lec, -YN, -grade, -class, -sex, -age, -location, -fedu, -medu, 
         -TE_YN, -TE_Rest_YN, -filter_., -PCTI_Total_test, -PCTI_Total_rtest, -B_PCTI_Total_test,
         -B_PCTI_Total_rtest, -blame_test, -blame_retest, -self_retest, -word_test,
         -word_retest, -self_test, -starts_with("B_"))

# ---- Process PTCI Dataset ----
ptci_df <- df_retest |>
  select(id, starts_with("ptci"))

ptci_test_df <- ptci_df |>
  select(id, ends_with("_test"))
colnames(ptci_test_df) <- gsub('_test$', '', colnames(ptci_test_df))
ptci_test_df <- pivot_longer(ptci_test_df, cols=-id, names_to = "item", values_to = "resp")

df <- rbind(df, ptci_test_df)
save(df, file="PTCI_Chinese_Zhan_2024.Rdata")
write.csv(df, "PTCI_Chinese_Zhan_2024.csv", row.names=FALSE)
