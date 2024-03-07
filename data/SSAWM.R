# https://osf.io/hp4gs/

library(readxl)
library(dplyr)
library(tidyr)

data <- read_excel("D:/Desktop/MethodsData.toShare.xlsx")

data <- data %>%
  mutate(Total_dPrime = as.numeric(as.character(Total_dPrime))) %>%
  mutate(Total_dPrime = ifelse(is.na(Total_dPrime), NA, Total_dPrime))

long_data <- data %>%
  select(record_id, w_sum, Total_dPrime) %>% 
  pivot_longer(cols = -record_id, names_to = "item", values_to = "resp") %>%
  rename(id = record_id)


save(long_data, file = "D:/Desktop/SSAWM.RData")
