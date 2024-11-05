library(haven)
library(dplyr)
library(tidyr)

df <- read_sav("database López et al (2015)_10411_20525.sav")
df$id <- seq(1, nrow(df))

df <- df %>%
  select(id, SCS1:SCS24) %>%
  pivot_longer(SCS1:SCS24,
               names_to = "item",
               values_to = "resp")

unique(df$item)

write.csv(df, "SCS_Lopez_2015.csv", row.names=FALSE)
