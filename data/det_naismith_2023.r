# Paper: https://www.sciencedirect.com/science/article/pii/S1075293524000886
# Data: https://osf.io/zy8fb/
library(haven)
library(dplyr)
library(tidyr)
library(readxl)

df <- read_excel("DET-duration.xlsm", sheet="data")
df <- df |>
  rename(id=user_id, item=prompt_id, 
         cov_gender=gender, cov_test_taker_intent=test_taker_intent, cov_first_langugage=first_language, 
         itemcov_condition=condition, itemcov_length_characters=length_characters, cov_ielts_writing=ielts_writing) |>
  select(id, item, machine_grade, starts_with("cov"), starts_with("rater"), starts_with("itemcov"), -rater3)
df <- pivot_longer(df, cols=-c(id, item, starts_with("cov"), starts_with("itemcov")), names_to="rater", values_to="resp")

save(df, file="det_naismith_2023.rdata")
write.csv(df, "det_naismith_2023.csv", row.names=FALSE)