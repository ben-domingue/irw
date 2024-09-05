# Paper: https://openpsychologydata.metajnl.com/articles/10.5334/jopd.af#2-methods
# Data: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/23150
library(tidyr)
library(dplyr)

load("BAFACALO_DATASET.RData")
load("codebook_BAFACALO.RData")
df <- BAFACALO_DATASET
df <- df |> # Remove demographic data columns
  select(-scholarity_father, -scholarity_mother, 
         -household_income, -previous_school_type,
         -sex, -class_number) |>
  select(-N, -P1, -P2, -P3, -FF, -FI1, -FI2, # Remove aggregate statistics
         -portuguese, -english, -math, -biology, -physics, 
         -chimestry, -geography, -history) 
