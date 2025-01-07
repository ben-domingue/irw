# Paper:
# Data: https://github.com/EducationalTestingService/ies-writing-achievement-study-data
library(haven)
library(dplyr)
library(tidyr)

df <- read.csv("student_data.csv")
df <- df |>
  rename(id=Student_ID, cov_participating_course_grade=Participating_Course_Grade, cov_sat_total=FINAL_SAT_total, cov_cum_GPA=StudySemester_cumGPA)
df <- df |> 
  filter(across(starts_with("Q"), ~ !is.na(.)))

# ---------- Map Q3 strings to values ----------
Q3_df <- df |>
  select(starts_with("Q3"))
Q3_mapping <- c(
  "Strongly Disagree" = 1,
  "Disagree" = 2,
  "Neither agree nor disagree" = 3,
  "Agree" = 4,
  "Strongly Agree" = 5
)
Q3_df <- as.data.frame(lapply(Q3_df %>% select(starts_with("Q3")), function(col) Q3_mapping[col]))

# ---------- Map Q1 strings to values ----------
Q1_mapping <- c(
  "Does not describe me at all" = 1,
  "2" = 2,
  "Somewhat describes me" = 3,
  "4" = 4,
  "Describes me very well" = 5
)
Q1_df <- df |>
  select(starts_with("Q1"))
Q1_df <- as.data.frame(lapply(Q1_df, function(col) Q1_mapping[col]))

# ---------- Map Q2 strings to values ----------
Q2_df <- df |>
  select(starts_with("Q2"))
Q2_mapping <- c(
  "No Chance" = 0,
  "Completely Sure" = 100,
  "50/50 Chance" = 50
)
Q2_df <- as.data.frame(lapply(Q2_df, function(col) {
  # Use ifelse to check and replace values
  sapply(col, function(value) if (value %in% names(Q2_mapping)) Q2_mapping[value] else value)
}))
Q2_df <- as.data.frame(lapply(Q2_df, function(col) as.numeric(col)))
Q2_df <- as.data.frame(lapply(Q2_df, function(col) col / 10))

# ---------- Map Q4 strings to values ----------
Q4_df <- df |>
  select(starts_with("Q4"))
Q4_mapping <- c(
  "Strongly Disagree" = 1,
  "Disagree" = 2,
  "Neither agree nor disagree" = 3,
  "Agree" = 4,
  "Strongly Agree" = 5
)
Q4_df <- as.data.frame(lapply(Q4_df %>% select(starts_with("Q4")), function(col) Q4_mapping[col]))

final_df <- cbind(Q1_df, Q2_df, Q3_df, Q4_df)
cov_df <- df |>
  select(id, starts_with("cov"))
final_df <- cbind(cov_df, final_df)
final_df <- pivot_longer(final_df, cols=-c(id, starts_with("cov")), names_to="item", values_to="resp")

save(final_df, file="ieswriting_molloy_2022.rdata")
write.csv(final_df, "ieswriting_molloy_2022.csv", row.names=FALSE)