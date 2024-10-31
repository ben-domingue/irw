library(tidyr)
library(dplyr)

df <- read.table("Suppl_2_response_data_358.tab", header=TRUE, sep="\t")

df <- df %>% select(Crav1:Crav12)

df$id <- seq(1, nrow(df))

df <- df %>%
  pivot_longer(c(Crav1:Crav12),
               names_to = "item",
               values_to = "resp") %>%
  filter(!is.na(resp) & resp != 0)

write.csv(df, "K-PCQ_Huh_2022.csv", row.names=FALSE)
