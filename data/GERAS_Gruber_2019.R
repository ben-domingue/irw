# Paper:https://econtent.hogrefe.com/doi/10.1027/1015-5759/a000528
# Data:https://osf.io/42jhr/
library(dplyr)
library(tidyr)
library(haven)

# ------ Process Study 1 -------
study1_cfa_df <- read_sav("./GERAS_Study1_CFA.sav")
study1_efa_df <- read_sav("./GERAS_Study1_EFA.sav")

study1_df <- rbind(study1_cfa_df, study1_efa_df) # Merge 2 datasets
study1_df <- study1_df |>
  select(-gender) |>
  rename(id=ID)
study1_df <- study1_df %>% # Replace encoded missing values with NA
  mutate_all(~replace(., . %in% c(-66, -77, -99), NA))

# ------ Process Study 2 -------
study2_df <- read_sav("./GERAS_Study2_CFA.sav")

colnames(study2_df) <- gsub("\\s*\\(.*\\)", "", colnames(study2_df))
study2_df <- lapply(study2_df, function(x) { attr(x, "label") <- NULL; x })
study2_df <- as.data.frame(study2_df)

study2_df <- study2_df %>%
  mutate(VPN = paste(VPN, gender, age, sep = "_"))
study2_df <- study2_df |>
  select(-gender) |>
  rename(id=VPN)
study2_df <- study2_df %>% # Replace encoded missing values with NA
  mutate_all(~replace(., . %in% c(-66, -77, -99), NA))

# ------ Process Merged Data ------
study1_df$id <- as.character(study1_df$id)
merged_df <- bind_rows(
  study1_df %>% mutate(group = "Study 1"), 
  study2_df %>% mutate(group = "Study 2")) # Merge datasets from the 2 studies
pivot_longer(merged_df, cols=-c(id, age, group), names_to="item", values_to = "resp")


save(merged_df, file="GERAS_Gruber_2019.Rdata")
write.csv(merged_df, "GERAS_Gruber_2019.csv", row.names=FALSE)