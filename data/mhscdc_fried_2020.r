# Data: https://osf.io/mvdpe/
# Paper: https://osf.io/preprints/psyarxiv/36xkp_v1
library(haven)
library(dplyr)
library(tidyr)

# ---------- EMA Data ----------
ema_df <- read.csv("clean_ema.csv")
ema_df <- ema_df |> 
  mutate(Response = as.POSIXct(Response, format="%Y-%m-%d %H:%M:%S", tz="CET")) |>
  rename(date=Response)
ema_df <- ema_df |>
  rename(id=ID) |>
  select(id, starts_with("Q"), date)
ema_df <- pivot_longer(ema_df, cols=-c(id,date), names_to="item", values_to="resp")
ema_df <- ema_df |> 
  arrange(id, date) |>  # Sort by user and response time
  group_by(id) |> 
  mutate(wave = dense_rank(date) - 1) |>  # Assign sequential wave numbers per user
  ungroup()
ema_df$date<-as.numeric(strptime(ema_df$date,format="%Y-%m-%d %H:%M:%S"))

save(ema_df, file="mhscdc_fried_2020_ema.Rdata")
write.csv(ema_df, "mhscdc_fried_2020_ema.csv", row.names=FALSE)

# ---------- Baseline Test Data ----------
cov_list <- c("Gender", "Age", "Nationality", "RelationshipStatus", 
              "StudyProgram", "StudyYear", "WorkStatus", "MentalHealth")

bt_df <- read.csv("clean_prepost.csv")
bt_df <- bt_df |>
  rename(id = ID, Pre145 = Q145) |>
  rename_with(~ paste0("cov_", .), all_of(cov_list))


process_dass_data <- function(df, prefix, start_q, end_q, output_file) {
  dass_df <- df %>%
    select(id, starts_with("cov"), num_range(prefix, start_q:end_q)) %>%
    pivot_longer(cols = -c(id, starts_with("cov")),
                 names_to = "item", 
                 values_to = "resp")
  
  #save(dass_df, file = paste0(output_file, ".Rdata"))
  write.csv(dass_df, paste0(output_file, ".csv"), row.names = FALSE)
  
  return(dass_df)
}
# ----- Conscientiousness Data -----
dass_df <- process_dass_data(bt_df, "Pre", 22, 33, "mhscdc_fried_2020_conscientiousness")
# ----- Anger Data -----
dass_df <- process_dass_data(bt_df, "Pre", 34, 40, "mhscdc_fried_2020_anger")
# ----- Self-Efficacy Data -----
dass_df <- process_dass_data(bt_df, "Pre", 46, 55, "mhscdc_fried_2020_se")
# ----- Mindfullness Data -----
dass_df <- process_dass_data(bt_df, "Pre", 56, 67, "mhscdc_fried_2020_mindfullness")
# ----- Perceived Stress Data -----
dass_df <- process_dass_data(bt_df, "Pre", 68, 77, "mhscdc_fried_2020_ps")
# ----- Motivation Data -----
dass_df <- process_dass_data(bt_df, "Pre", 86, 101, "mhscdc_fried_2020_motivation")
# ----- Smartphone Data -----
dass_df <- process_dass_data(bt_df, "Pre", 102, 115, "mhscdc_fried_2020_smartphone")


### seperate process for data that contained both pre and post 
process_dass_data2 <- function(df, prefix, start_q, end_q, wave_label, item_offset) {
  dass_df <- df %>%
    select(id, starts_with("cov"), num_range(prefix, start_q:end_q)) %>%
    pivot_longer(cols = -c(id, starts_with("cov")),
                 names_to = "item_rawname", 
                 values_to = "resp") %>%
    mutate(
      item = paste0("item_", as.integer(str_extract(item_rawname, "\\d+")) - item_offset),
      wave = wave_label,
    ) %>%
    select(id, starts_with("cov"), wave, item, resp)
  return(dass_df)
}

# ----- DASS Data -----
dass_pre <- process_dass_data2(bt_df, "Pre", 1, 21, "pre",0)
dass_post <- process_dass_data2(bt_df, "Post", 38, 58, "post",37)
dass_df <- bind_rows(dass_pre, dass_post)
write.csv(dass_df,"mhscdc_fried_2020_daas.csv", row.names = FALSE)


# ----- Loneliness Data -----
dass_pre <- process_dass_data2(bt_df, "Pre", 41, 45, "pre",40)
dass_post <- process_dass_data2(bt_df, "Post", 18, 22, "post",17)
dass_df <- bind_rows(dass_pre, dass_post)
write.csv(dass_df,"mhscdc_fried_2020_loneliness.csv", row.names = FALSE)

# ----- Procrastination Data -----
dass_pre <- process_dass_data2(bt_df, "Pre", 141, 145, "pre",140)
dass_post <- process_dass_data2(bt_df, "Post", 13, 17, "post",12)
dass_df <- bind_rows(dass_pre, dass_post)
write.csv(dass_df,"mhscdc_fried_2020_procrastination.csv", row.names = FALSE)


# ----- Tiredness Data -----  some items in post are not in pre. 
dass_pre <- process_dass_data2(bt_df, "Pre", 78, 85, "pre",77)
dass_post_1 <- process_dass_data2(bt_df, "Post", 59, 62, "post",58)
dass_post_2 <- process_dass_data2(bt_df, "Post", 64, 67, "post",59)
dass_post_3 <- process_dass_data2(bt_df, "Post", 63, 63, "post",54)
dass_post_4 <- process_dass_data2(bt_df, "Post", 68, 68, "post",58)
dass_df <- bind_rows(dass_pre, dass_post_1,dass_post_2,dass_post_3,dass_post_4)
write.csv(dass_df,"mhscdc_fried_2020_tired.csv", row.names = FALSE)
