#paper. https://link.springer.com/article/10.3758/s13428-022-01856-x#data-availability
#study 5
library(readxl)
library(dplyr)
library(tidyr)

data <- read_excel("student_vocabulary_test_study5.xlsx",na = "NA")

data_BFI <- data %>%
  select(ID, age, BFI1:BFI60) %>% 
  rename(id = ID)
data_BFI <- data_BFI %>%
  pivot_longer(
    cols = -c(id, age), 
    names_to = "item", 
    values_to = "resp"
  )
data_IceageQ <- data %>%
  select(ID, age, IceageQ001:IceageQ024) %>% 
  rename(id = ID)
data_IceageQ <- data_IceageQ %>%
  pivot_longer(
    cols = -c(id, age), 
    names_to = "item", 
    values_to = "resp"
  )
data_T <- data %>%
  select(ID, age, T1Q1:T14Q3) %>% 
  rename(id = ID)
data_T <- data_T %>%
  pivot_longer(
    cols = -c(id, age), 
    names_to = "item", 
    values_to = "resp"
  )
data_AFOQT <- data %>%
  select(ID, age, AFOQT1:AFOQT20) %>% 
  rename(id = ID)
data_AFOQT <- data_AFOQT %>%
  pivot_longer(
    cols = -c(id, age), 
    names_to = "item", 
    values_to = "resp"
  )
data_TSQ <- data %>%
  select(ID, age,T1SQ001:T10SQ005) %>% 
  rename(id = ID)
data_TSQ <- data_TSQ %>%
  pivot_longer(
    cols = -c(id, age), 
    names_to = "item", 
    values_to = "resp"
  )
data_RF <- data %>%
  select(ID, age, RF1:RF24) %>% 
  rename(id = ID)
data_RF <- data_RF %>%
  pivot_longer(
    cols = -c(id, age), 
    names_to = "item", 
    values_to = "resp"
  )
data_ART <- data %>%
  select(ID, age, DanielAcheson:AynRand) %>% 
  rename(id = ID)
data_ART <- data_ART %>%
  pivot_longer(
    cols = -c(id, age), 
    names_to = "item", 
    values_to = "resp"
  )
data_Vocabulary <- data %>%
  select(ID, age, autonomy:emir) %>% 
  rename(id = ID)
data_Vocabulary <- data_Vocabulary %>%
  pivot_longer(
    cols = -c(id, age), 
    names_to = "item", 
    values_to = "resp"
  )
data_ND <- data %>%
  select(ID, age, ND1:ND80) %>% 
  rename(id = ID)
data_ND <- data_ND %>%
  pivot_longer(
    cols = -c(id, age), 
    names_to = "item", 
    values_to = "resp"
  )
data_GK <- data %>%
  select(ID, age, GK1:GK65) %>% 
  rename(id = ID)
data_GK <- data_GK %>%
  pivot_longer(
    cols = -c(id, age), 
    names_to = "item", 
    values_to = "resp"
  )

saveRDS(data_BFI, "Tests of vocabulary_BFI.RData")    
saveRDS(data_IceageQ, "Tests of vocabulary_IceageQ.RData") 
saveRDS(data_T, "Tests of vocabulary_T.RData") 
saveRDS(data_AFOQT, "Tests of vocabulary_AFOQT.RData") 
saveRDS(data_TSQ, "Tests of vocabulary_TSQ.RData") 
saveRDS(data_RF, "Tests of vocabulary_RF.RData") 
saveRDS(data_ART, "Tests of vocabulary_ART.RData") 
saveRDS(data_Vocabulary, "Tests of vocabulary_Vocabulary.RData") 
saveRDS(data_ND, "Tests of vocabulary_ND.RData") 
saveRDS(data_GK, "Tests of vocabulary_GK.RData") 
