# paper. https://link.springer.com/article/10.3758/s13428-023-02130-4
#data. https://osf.io/au6m5/
#study3
library(haven)
library(dplyr)
library(tidyr)

data <- read_spss("MicroPROMS_data_S3.sav")
data <- data %>% 
  mutate(across(everything(), ~`attr<-`(.x, "label", NULL)))

data <- data %>%
  select(id, Age, MMQ_K1:MMQ_N7, GMSI1_AE01:GMSI3_EM06, M2_cod:B12_t2_cod) %>%
  rename(age = Age)

data1 <- data %>%
  pivot_longer(
    -c(id, age), 
    names_to = "item", 
    values_to = "resp"
  ) 

save(data1, file = "MicroPROMS_data_S3.Rdata")
