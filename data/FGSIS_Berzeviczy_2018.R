library(readxl)
library(tidyr)
library(dplyr)

df <- read_xlsx("FGSIS Data.xlsx")

df <- df[-c(1, 2), c(1, 13:ncol(df))]

df <- df %>%
  rename(id = UserID)

fgsis <- pivot_longer(df, cols=-id, names_to="item", values_to="resp")

likert_map <- c(
  "Strongly disagree" = 1,
  "Disagree" = 2,
  "Agree" = 3,
  "Strongly agree" = 4,
  "Yes" = 1,
  "No" = 0
)

fgsis$resp <- likert_map[fgsis$resp]

fgsis <- fgsis %>%
  filter(!is.na(resp))

write.csv(df, "FGSIS_Berzeviczy_2018.csv", row.names=FALSE)
