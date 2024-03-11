#https://osf.io/43dfq/?view_only=a97186042d6a474aad93880b183935fc

library(dplyr)
library(tidyr)
library(haven)

data <- read_sav("D:/Desktop/DataBase AAQ-II_Criteria_rev.sav")
data <- data %>% 
  mutate(across(everything(), ~`attr<-`(.x, "label", NULL)))

#Remove participants identified as potential careless responders and multivariate outliers
data <- data %>% filter(MARK15 != 1)


data_selected <- data %>% select(ResponseID, Age, AAQ_II_1, AAQ_II_2, AAQ_II_3, AAQ_II_4, AAQ_II_5, AAQ_II_6, AAQ_II_7)

#Remove participants with missing values
data_filter <- data_selected %>% filter(!if_any(starts_with("AAQ_II"), ~ .x == -999))


data_long <- data_filter %>%
  pivot_longer(
    cols = starts_with("AAQ_II"),
    names_to = "item",
    values_to = "resp"
  ) %>%
  rename(id = ResponseID,age = Age)


save(data_long, file = "D:/Desktop/AAQ-II.Rdata")
