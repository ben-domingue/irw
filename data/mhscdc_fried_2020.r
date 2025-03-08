# Data: https://osf.io/mvdpe/
# Paper: https://osf.io/preprints/psyarxiv/36xkp_v1
library(haven)
library(dplyr)
library(tidyr)

# ---------- EMA Data ----------
ema_df <- read.csv("clean_ema.csv")
ema_df <- ema_df |>
  rename(id=ID) |>
  select(id, starts_with("Q"))
ema_df <- pivot_longer(ema_df, cols=-id, names_to="item", values_to="resp")

save(ema_df, file="mhscdc_fried_2020_ema.Rdata")
write.csv(ema_df, "mhscdc_fried_2020_ema.csv", row.names=FALSE)

# ---------- Baseline Test Data ----------
cov_list <- c("Gender", "Age", "Nationality", "RelationshipStatus", 
              "StudyProgram", "StudyYear", "WorkStatus", "MentalHealth")

bt_df <- read.csv("clean_prepost.csv")
bt_df <- bt_df |>
  rename(id = ID) |>
  rename_with(~ paste0("cov_", .), all_of(cov_list))


process_dass_data <- function(df, prefix, start_q, end_q, output_file) {
  dass_df <- df %>%
    select(id, starts_with("cov"), num_range(prefix, start_q:end_q)) %>%
    pivot_longer(cols = -c(id, starts_with("cov")), names_to = "item", values_to = "resp")
  
  save(dass_df, file = paste0(output_file, ".Rdata"))
  write.csv(dass_df, paste0(output_file, ".csv"), row.names = FALSE)
  
  return(dass_df)
}
# ----- DASS Data -----
dass_df <- process_dass_data(bt_df, "Pre", 17, 37, "mhscdc_fried_2020_dass")
# ----- Conscientiousness Data -----
dass_df <- process_dass_data(bt_df, "Pre", 39, 50, "mhscdc_fried_2020_conscientiousness")
# ----- Anger Data -----
dass_df <- process_dass_data(bt_df, "Pre", 52, 58, "mhscdc_fried_2020_anger")
# ----- Loneliness Data -----
dass_df <- process_dass_data(bt_df, "Pre", 41, 45, "mhscdc_fried_2020_loneliness")
# ----- Self-Efficacy Data -----
dass_df <- process_dass_data(bt_df, "Pre", 46, 55, "mhscdc_fried_2020_se")
# ----- Mindfullness Data -----
dass_df <- process_dass_data(bt_df, "Pre", 56, 67, "mhscdc_fried_2020_mindfullness")
# ----- Perceived Stress Data -----
dass_df <- process_dass_data(bt_df, "Pre", 68, 77, "mhscdc_fried_2020_ps")
# ----- Tiredness Data -----
dass_df <- process_dass_data(bt_df, "Pre", 78, 85, "mhscdc_fried_2020_tired")
# ----- Motivation Data -----
dass_df <- process_dass_data(bt_df, "Pre", 86, 101, "mhscdc_fried_2020_motivation")
# ----- Smartphone Data -----
dass_df <- process_dass_data(bt_df, "Pre", 102, 115, "mhscdc_fried_2020_smartphone")