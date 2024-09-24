#paper. https://link.springer.com/article/10.3758/s13428-023-02124-2
#study 2e
library(dplyr)
library(tidyr)
library(readr)

data <- read_csv("MIST - Sample 2E (2022) - Dataset.csv")

data <- data %>%
  select(ID,MIST_1:MIST_94) %>%
  rename(id = ID)

data_1 <- data %>%
  pivot_longer(
    cols = -c(id), 
    names_to = "item", 
    values_to = "resp"
  )

saveRDS(data_1, "MIST_study2E.RData")         

write.csv(data_1, "MIST_study2E.csv", row.names = FALSE)
