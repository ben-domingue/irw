# Paper: https://osf.io/zwu26/
# Data: https://osf.io/eha26/
library(haven)
library(dplyr)
library(tidyr)
library(readxl)

set_float_NA <- function(x) {
  # Check if a value is integer-like (i.e., whole numbers, not decimals)
  ifelse(x == floor(x), x, NA)
}

study1_df <- read_excel("data_study_1.xlsx")
study2_df <- read_excel("data_study_2.xlsx")

# ------ Process Study 1 Dataset ------
study1_df <- study1_df |>
  select(-ends_with("Subscale"), -ends_with("Factor"), -Sex, -Age, -PGG_percentage)
study1_df$id <- paste0("study1_", seq_len(nrow(study1_df)))

study1_iri_df <- study1_df |>
  select(id, starts_with("Fantasy"), starts_with("Personal"), 
         starts_with("Concern"), starts_with("Perspective"))
study1_iri_df <- pivot_longer(study1_iri_df, cols=-id, names_to = "item", values_to = "resp")
study1_iri_df$resp <- set_float_NA(study1_iri_df$resp)

study1_ei_df <- study1_df |>
  select(id, starts_with("Empathy"), starts_with("Behavioral"))
study1_ei_df <- pivot_longer(study1_ei_df, cols=-id, names_to = "item", values_to = "resp")
study1_ei_df$resp <- set_float_NA(study1_ei_df$resp)

# ------ Process Study 2 Dataset ------ 
study2_df <- study2_df |>
  select(-ends_with("Subscale"), -ends_with("Factor"), -Sex, -Age)
study2_df$id <- paste0("study2_", seq_len(nrow(study2_df)))

study2_iri_df <- study2_df |>
  select(id, starts_with("Fantasy"), starts_with("Personal"), 
         starts_with("Concern"), starts_with("Perspective"))
study2_iri_df <- pivot_longer(study2_iri_df, cols=-id, names_to = "item", values_to = "resp")
study2_iri_df$resp <- set_float_NA(study2_iri_df$resp)

study2_ei_df <- study2_df |>
  select(id, starts_with("Empathy"), starts_with("Behavioral"))
study2_ei_df <- pivot_longer(study2_ei_df, cols=-id, names_to = "item", values_to = "resp")
study2_ei_df$resp <- set_float_NA(study2_ei_df$resp)

ei_df <- rbind(study1_ei_df, study2_ei_df)
iri_df <- rbind(study1_iri_df, study2_iri_df)

save(ei_df, file="VEI_Brazillian_Shiramizu_2018_EI.Rdata")
save(iri_df, file="VEI_Brazillian_Shiramizu_2018_IRI.Rdata")
write.csv(iri_df, "VEI_Brazillian_Shiramizu_2018_IRI.csv", row.names=FALSE)
write.csv(ei_df, "VEI_Brazillian_Shiramizu_2018_EI.csv", row.names=FALSE)
