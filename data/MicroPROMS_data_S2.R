# paper. https://link.springer.com/article/10.3758/s13428-023-02130-4
#data. https://osf.io/au6m5/
#study2
library(haven)
library(dplyr)
library(tidyr)

data <- read_spss("MicroPROMS_data_S2.sav")
data <- data %>% 
  mutate(across(everything(), ~`attr<-`(.x, "label", NULL)))

data <- data %>%
  select(id, Age, MMScale_K1:MMScale_N7,M2_cod:l18_full_cod) %>%
  rename(age = Age)

data1 <- data %>%
  pivot_longer(
    -c(id, age), 
    names_to = "item", 
    values_to = "resp"
  ) 

save(data1, file = "MicroPROMS_data_S2.Rdata")
