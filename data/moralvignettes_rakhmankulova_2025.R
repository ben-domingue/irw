library(readxl)
library(tidyverse)


sample_1 <- read_excel("1_MJ_questionnaire_scores.xlsx", sheet = "Sample_1")
sample_2 <- read_excel("1_MJ_questionnaire_scores.xlsx", sheet = "Sample_2")

data_1 <- sample_1 %>%
  rename(rater = ID, date = Timestamp) %>%         # rename key columns
  pivot_longer(
    cols = matches("_[0-9]+$"),                   
    names_to = c("item", "video"),                 
    names_pattern = "(.*)_(\\d+)$",
    values_to = "resp"                             
  ) %>%
  mutate(id = as.integer(video),
         sample = 1) %>%            
  select(date, rater, id, item, resp,sample)

data_2 <- sample_2 %>%
  rename(rater = ID, date = Timestamp) %>%         # rename key columns
  pivot_longer(
    cols = matches("_[0-9]+$"),                   
    names_to = c("item", "video"),                 
    names_pattern = "(.*)_(\\d+)$",
    values_to = "resp"                             
  ) %>%
  mutate(id = as.integer(video),
         sample = 2) %>%            
  select(date, rater, id, item, resp,sample)

data <- bind_rows(data_1, data_2)

write.csv(data, "moralvignettes_rakhmankulova_2025.csv", row.names = FALSE)

