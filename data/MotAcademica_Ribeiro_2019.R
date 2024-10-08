library(tidyr)
library(dplyr)

df <- read.table("MotAcademica_AmostraA.tab", header=TRUE)
df <- df %>% select(contains("Item"))

df2 <- read.table("MotAcademica_AmostraB.tab", header=TRUE)
df2 <- df2 %>% select(contains("Item"))

dfc <- union_all(df, df2)

dfc$id <- seq(1, nrow(dfc))

print(length(unique(dfc$id)))

dfc <- dfc %>%
  pivot_longer(c(contains("Item")),
               names_to = "item",
               values_to = "resp") %>%
  filter(!is.na(resp))

write.csv(dfc, "MotAcademica_Ribeiro_2019.csv", row.names=FALSE)
