library(tidyr)
library(dplyr)

# Data: https://osf.io/vds7a/ ("Smoking Perseverance Data.csv"), CC BY 4.0
df <- read.csv("Smoking Perseverance Data.csv")

# #2401: ID 43 at Time 184 is in the file twice, identical in every column (one
# record written twice); keep one copy. ID 38 at Time 230 also repeats, but its
# two rows differ on i47, so both stay, for #1856.
df <- distinct(df)

df <- df %>%
  select(-c("Day", "Hour")) %>%
  pivot_longer(c("i44":"i47"),
               names_to = "item",
               values_to = "resp")

colnames(df) <- tolower(colnames(df))

df$date <- df$time * 3600

df <- df %>%
  select(id, item, resp, date)

write.csv(df, "smoking_perseverance_mcneish_2025.csv", row.names = FALSE)
