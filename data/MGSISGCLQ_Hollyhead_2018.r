# Data: https://osf.io/5vhju/
#  Paper: 
library(haven)
library(dplyr)
library(tidyr)
library(openxlsx)

df <- read.xlsx("MGSIS-5 and GCLQ Data.xlsx")
df <- df[, colSums(!is.na(df)) > 0]
df$id <- seq_len(nrow(df))
df <- df |>
  select(-Start.time, -Completion.time, -Email, -`Are.you.a.resident.of.the.UK?`, -`How.old.are.you?`)
df <- df[!apply(df[, -which(names(df) == "id")], 1, function(row) all(is.na(row))), ]

mgsis_df <- df |>
  select(id, starts_with("I"), `Do.you.have.a.medical.condition.which.affects.your.lower.body.or.could.impact.how.you.feel.about.your.genitals?`) |>
  rename(cov_medical_condition=`Do.you.have.a.medical.condition.which.affects.your.lower.body.or.could.impact.how.you.feel.about.your.genitals?`)
GCLQ_df <- df |>
  select(-starts_with("I"), id) |>
  rename(cov_medical_condition=`Do.you.have.a.medical.condition.which.affects.your.lower.body.or.could.impact.how.you.feel.about.your.genitals?`)

GCLQ_df[] <- lapply(GCLQ_df, function(x) ifelse(x == "Yes", 1, ifelse(x == "No", 0, x)))
GCLQ_df <- GCLQ_df %>%
  mutate(across(everything(), ~ as.numeric(as.character(.))))
GCLQ_df <- pivot_longer(GCLQ_df, cols=-c(id, cov_medical_condition), names_to="item", values_to="resp")

likert_map <- c(
  "Strongly Disagree" = 1,
  "Disagree" = 2,
  "Agree" = 3,
  "Strongly Agree" = 4
)

mgsis_df <- pivot_longer(mgsis_df, cols=-c(id, cov_medical_condition), names_to="item", values_to="resp")
mgsis_df$resp <- likert_map[mgsis_df$resp]

final_df <- rbind(mgsis_df, GCLQ_df)
final_df$cov_medical_condition <- as.numeric(lapply(final_df$cov_medical_condition, function(x) ifelse(x == "Yes", 1, ifelse(x == "No", 0, x))))

save(final_df, file="MGSISGCLQ_Hollyhead_2018.Rdata")
write.csv(final_df, "MGSISGCLQ_Hollyhead_2018.csv", row.names=FALSE)