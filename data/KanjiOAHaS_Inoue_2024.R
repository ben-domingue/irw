library(dplyr)

df <- read.csv("Raw_Data_20240607.csv")

df <- df %>%
  select(student_id, item, score, total_time) %>%
  rename(id = student_id, resp = score, rt = total_time)


write.csv(df, "KanjiOAHaS_Inoue_2024.csv", row.names=FALSE)
