#paper. https://link.springer.com/article/10.3758/s13428-022-01856-x#data-availability
#study 3
library(readxl)
library(dplyr)
library(tidyr)

data <- read_excel("student_vocabulary_test_study3.xlsx")

data <- data %>%
  rename(rascal1 = rascal...59,rascal2 = rascal...119)
data <- data %>%
  select("Response ID", age, mensible:wrought,ricochet:rascal2,compost:emir,GK1:GK65,ND1:ND80,T1Q1:T12Q3,"Daniel Acheson":"Ayn Rand",RF1:BFI60) %>% 
  rename(id = "Response ID")
data_1 <- data %>%
  pivot_longer(
    cols = -c(id, age), 
    names_to = "item", 
    values_to = "resp"
  )
saveRDS(data_1, "Tests of vocabulary_study3.RData")  
