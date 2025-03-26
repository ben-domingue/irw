# Paper: https://link.springer.com/article/10.3758/s13428-024-02559-1#Sec23
# Data: https://link.springer.com/article/10.3758/s13428-024-02559-1#Sec23
library(haven)
library(dplyr)
library(tidyr)

df <- read.csv("13428_2024_2559_MOESM1_ESM.csv")
df <- pivot_longer(df, cols=-ID, names_to="item", values_to="resp")
df <- df |>
  rename(id=ID, itemcov_weight=resp)
df$resp <- ifelse(df$itemcov_weight > 0, 1, 0)
df$itemcov_weight <- ifelse(df$item %in% c("X1", "X2", "X11", "X12"), 0.5,
                        ifelse(df$item %in% c("X3", "X4", "X13", "X14"), 1,
                               1.5))

save(df, file="csft_ye_2025.Rdata")
write.csv(df, "csft_ye_2025.csv", row.names=FALSE)
