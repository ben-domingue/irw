# Paper: https://doi.org/10.1037/pas0001323
# Data: https://osf.io/p8j2v
library(dplyr)
library(tidyr)

df <- readRDS("./Depression_and_anxiety_question_framing_data_set.Rds")
df <- df |>
  select(-Framing_sequence, -Sex, -Date_of_birth, # Removal of demographic data
         -state, -skin_color, -sexual_orientation, 
         -marital_status, -religion, -kids, -family_income, 
         -cohabitants, -educational_attainment, -educational_years, 
         -working_status, -Date_of_interview, -lte_events) |>
  rename(id=ID, group=Study, date=Date_time_of_interview, age=Age)
df$date <- as.numeric(as.POSIXct(df$date, format="%d/%m/%Y %H:%M:%S", tz="UTC")) # Change date to Unix timestamp

df <- df %>% # Mutate column value types for merging purpose
  mutate(across(-c(id, age, group, date), as.double)) 
df <- pivot_longer(df, cols=c(-id, -group, -date, -age), names_to='item', values_to='resp')

df <- df %>% # Filter out unattempted items of Study Group 2
  filter(!(grepl("^promis_dep", item) & group == "Study 2 - Frame primed by symptom" & is.na(resp)))
df <- df %>%
  filter(!(grepl("^promis_anx", item) & group == "Study 2 - Frame primed by symptom" & is.na(resp)))
na_count <- which(is.na(df$resp))

save(df, file="BF_Brummer$Hoffman_2021.Rdata")
write.csv(df, "BF_Brummer$Hoffman_2021.csv", row.names=FALSE)
