# Paper: https://www.researchgate.net/publication/318014800_Re-evaluating_the_psychometric_properties_of_MicroFIN_A_multidimensional_measurement_of_complex_problem_solving_or_a_unidimensional_reasoning_test
# Data: https://osf.io/wp3z4/
library(haven)
library(dplyr)
library(tidyr)

# Remove participants whose responses are all NAs
remove_na <- function(df) {
  df <- df[!(rowSums(is.na(df[, -which(names(df) == "id")])) == (ncol(df) - 1)), ]
  return(df)
}

df <- read.csv("data_microfin_final.csv")
df <- df |>
  select(-age, -gender, -fin, -fin_re, -reas.fig, -reas.verb, 
         -reas.num, -starts_with("reas.tot"))

# ------ Process MicroFIN Dataset ------
microfin_df <- df |>
  select(id, starts_with("zi"), starts_with("iz"), 
         starts_with("know"), starts_with("c"))
microfin_df <- microfin_df %>%
  filter(id != 222)
microfin_df <- remove_na(microfin_df)

microfin_test_df <- microfin_df |>
  select(-ends_with("re"))
microfin_test_df <- remove_na(microfin_test_df)

microfin_test_df <- pivot_longer(microfin_test_df, cols=-id, names_to="item", values_to="resp")
microfin_test_df$wave <- 0

microfin_retest_df <- microfin_df |>
  select(id, ends_with("re"))
microfin_retest_df <- remove_na(microfin_retest_df)
colnames(microfin_retest_df) <- gsub('_re', '', colnames(microfin_retest_df))
microfin_retest_df <- pivot_longer(microfin_retest_df, cols=-id, names_to="item", values_to="resp")
microfin_retest_df$wave <- 1

microfin_df <- rbind(microfin_retest_df, microfin_test_df)
save(microfin_df, file="PTAM_Kretzschmar_2017_MicroFIN.Rdata")
write.csv(microfin_df, "PTAM_Kretzschmar_2017_MicroFIN.csv", row.names=FALSE)
# ------ Process Raven's Matrix Task Dataset ------
raven_df <- df |>
  select(id, starts_with("rav"))
raven_df <- remove_na(raven_df)
raven_df <- pivot_longer(raven_df, cols=-id, names_to="item", values_to = "resp")

save(raven_df, file="PTAM_Kretzschmar_2017_Raven.Rdata")
write.csv(raven_df, "PTAM_Kretzschmar_2017_Raven.csv", row.names=FALSE)
# ------ Process Reasoning Dataset ------
res_df <- df |>
  select(id, starts_with("qr"), starts_with("verb"))
res_df <- remove_na(res_df)
res_df <- pivot_longer(res_df, cols=-id, names_to="item", values_to = "resp")

save(res_df, file="PTAM_Kretzschmar_2017_Reasoning.Rdata")
write.csv(res_df, "PTAM_Kretzschmar_2017_Reasoning.csv", row.names=FALSE)
