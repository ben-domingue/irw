#paper. https://link.springer.com/article/10.3758/s13428-022-01856-x#data-availability
#study 4
library(readxl)
library(dplyr)
library(tidyr)

data <- read_excel("student vocabulary test study 4.xlsx",na = "NA")
data <- data %>%
  select(ID, age, transfixed:dowel,iceage_Q1:iceage_Q18,Bacteria_Q1:Bacteria_Q19,T1Q1:T10Q4,AFOQT1:AFOQT20) %>% 
  rename(id = ID)
data_1 <- data %>%
  pivot_longer(
    cols = -c(id, age), 
    names_to = "item", 
    values_to = "resp"
  )
saveRDS(data_1, "Tests of vocabulary_study4.RData")
