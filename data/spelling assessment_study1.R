#https://link.springer.com/article/10.3758/s13428-022-01834-3#Ack1
library(readxl)
library(dplyr)
library(tidyr)

data <- read_excel("Study1.xlsx",na = "NA")

names(data)[names(data) == "ID"] <- "id"

data_1 <- pivot_longer(data, cols = -id, names_to = "item", values_to = "resp")

saveRDS(data_1, "spelling assessment_study1.RData")

##note: table now spelling_assessment_study1
