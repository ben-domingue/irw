# paper. https://link.springer.com/article/10.3758/s13428-023-02130-4
#data. https://osf.io/au6m5/
#study1
library(haven)
library(dplyr)
library(tidyr)

data <- read_spss("MicroPROMS_data_S1.sav")

data <- data %>% mutate(id = row_number())

data1 <- data %>% 
  filter(id <= 146) %>%
  select(id, Age, M1_cod, M2_cod, M11_cod, M12_cod, Ti10_cod, Ti13_cod, Ti14_cod, Ti15_cod, B3_cod, B5_cod, B7_cod, B12_cod, TU12_cod, TU14_cod, TU17_cod, TU18_cod, R5_cod, R6_cod, R12_cod, R13_cod)

data2 <- data %>% 
  filter(id >= 147 & id <= 280) %>%
  select(id, Age, M3_cod, M8_cod, M12_cod, Ti11_cod, Ti12_cod, Ti13_cod, Ti14_cod, Ti15_cod, B5_cod, B11_cod, B12_cod, TU12_cod, TU14_cod, TU18_cod, R12_cod, R13_cod, R18_cod, P10_cod, P12_cod, P13_cod, TE5_cod, TE10_cod, TE12_cod)

data1 <- data1 %>%
  pivot_longer(
    -c(id, Age), 
    names_to = "item", 
    values_to = "resp"
  ) %>%
  rename(age = Age)

data2 <- data2 %>%
  pivot_longer(
    -c(id, Age), 
    names_to = "item", 
    values_to = "resp"
  ) %>%
  rename(age = Age)

data_3 <- bind_rows(data1, data2)

save(data_3, file = "MicroPROMS_data_S1.Rdata")
