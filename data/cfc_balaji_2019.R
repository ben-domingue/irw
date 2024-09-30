library(openxlsx)
library(dplyr)
library(tidyr)

df <- read.xlsx("CFC Dataset without AP - Vaidhyanatha Balaji.xlsx")
df$id <- seq(1, nrow(df))
df <- df %>%
  select(-c(Age,	Education.Level,	Nationality)) %>%
  pivot_longer(c(CFC1,	CFC2,	CFC3,	CFC4,	CFC5,	CFC6,	CFC7,	CFC8,	CFC9,	CFC10,	CFC11,	CFC12),
               names_to = "item",
               values_to = "resp") %>%
  filter(!is.na(resp))

write.csv(df, "CFC_Balaji_2019.csv", row.names=FALSE)
