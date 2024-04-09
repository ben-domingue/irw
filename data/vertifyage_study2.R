#paper https://link.springer.com/article/10.3758/s13428-022-01944-y#Sec34
#study_2
library(dplyr)
library(tidyr)
library(haven)

data <- read_sav("Study 2_Imposters_Data.sav")
data <- data %>% 
  mutate(across(everything(), ~`attr<-`(.x, "label", NULL)))

data <- data[!is.na(data$Q57), ]
questions <- c("Q4", "Q6","Q8", "Q11", "Q13", "Q23", "Q33", "Q40", "Q41", "Q45", "Q47", "Q49", "Q59", "Q61", "Q63", "Q65", "Q67", "Q69", "Q75")
for(q in questions) {
  correct_col <- paste0(q, "correct")
  data[[correct_col]][is.na(data[[q]])] <- NA
}

data <- data %>%
  select(ResponseId, Q4correct:Q59correct, Q57) %>%
  rename(id = ResponseId, age = Q57)
names(data) <- gsub("correct", "", names(data))

data_1 <- data %>% 
  pivot_longer(
    cols = -c(id, age), 
    names_to = "item", 
    values_to = "resp"
  )

saveRDS(data_1, "vertifyage_study2.RData") 
