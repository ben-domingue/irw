#https://link.springer.com/article/10.3758/s13428-022-01834-3#Ack1
library(readxl)
library(dplyr)
library(tidyr)

data <- read_excel("Study2.xlsx",na = "NA")

data <- data %>%
  select(ID, Group, abhorrent:warranty) %>%
  rename(id = ID, group = Group)

data_1 <- data %>%
  pivot_longer(
    cols = -c(id, group), 
    names_to = "item", 
    values_to = "resp"
  )

saveRDS(data_1, "spelling assessment_study2.RData")
