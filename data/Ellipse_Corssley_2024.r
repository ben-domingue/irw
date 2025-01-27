# Data: https://github.com/scrosseye/ELLIPSE-Corpus
library(haven)
library(dplyr)
library(tidyr)

df <- read.csv("ellipsis_raw_rater_scores_anon_all_essay.csv")
df <- df |>
  rename(id=Filename) |>
  select(-Text)
df1 <- df |>
  select(id, ends_with("1")) |>
  df2 <- df |>
  select(id, ends_with("2"))

colnames(df1) <- ifelse(
  colnames(df1) == "id", 
  colnames(df1), 
  gsub("_1$", "", colnames(df1))
)
colnames(df2) <- ifelse(
  colnames(df2) == "id", 
  colnames(df2), 
  gsub("_2$", "", colnames(df2))
)

df1 <- df1 |>
  rename(rater=Rater)
df2 <- df2 |>
  rename(rater=Rater)

df1 <- pivot_longer(df1, cols=-c(id, rater), names_to="item", values_to="resp")
df2 <- pivot_longer(df2, cols=-c(id, rater), names_to="item", values_to="resp")

final_df <- rbind(df1, df2)

save(final_df, file="Ellipse_Corssley_2024.Rdata")
write.csv(final_df, "Ellipse_Corssley_2024.csv", row.names=FALSE)