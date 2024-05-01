#paper. https://link.springer.com/article/10.3758/s13428-022-01856-x#data-availability
#study 1
library(readxl)
library(dplyr)
library(tidyr)

data <- read_excel("Data Study 1 for R analysis.xlsx",na = "NA")
data <- data %>%
  select(id, Age, period:taxon,ND1:ND80,DanielAcheson:AynRand,D4Q1:D4Q80,D5Q1:"D6Q1[60]") %>% 
  rename(age = Age)
data_1 <- data %>%
  pivot_longer(
    cols = -c(id, age), 
    names_to = "item", 
    values_to = "resp"
  )
saveRDS(data_1, "Tests of vocabulary_study1.RData")    
